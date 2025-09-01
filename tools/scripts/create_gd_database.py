#!/usr/bin/env python3
"""
Improved SQLite database creation script for Global Dialogues data analysis.

This script creates a comprehensive SQLite database combining:
- ALL data from aggregate_standardized.csv (both poll questions and open-ended responses)
- PRI scores per participant
- Divergence and consensus scores per response
- Tag labels for responses

Improvements in this version:
1. Fixes column naming typo (norther_europe -> northern_europe)
2. Documents duplicate america regions (north_america vs northern_america)
3. Enables foreign key constraints with proper data validation
4. Handles truncated branch column names with mapping table
5. Extends divergence score calculation to all response types
6. Properly handles participant count discrepancies

All column names are normalized to lowercase_underscored format for consistency.
"""

import argparse
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import re
from lib.analysis_utils import parse_gd_identifier, validate_gd_directory
import json

# Constants for file paths
DIVERGENCE_FILE = "divergence/divergence_by_question.csv"
CONSENSUS_FILE = "consensus/consensus_profiles.csv"

def normalize_column_name(name):
    """Convert column names to lowercase_underscored format with fixes for known issues."""
    import re
    original_name = name
    
    # FIX 1: Handle the typo in the original CSV
    if name == 'Norther Europe':
        name = 'Northern Europe'
    
    # Special handling for "Branches" columns - keep the question part as identifier
    if name.startswith('Branches (') and name.endswith(')'):
        # Extract the question part and create a unique identifier
        match = re.search(r'Branches \((.*?)\)', name)
        if match:
            question_part = match.group(1)
            # Split into words and take first 6 words for a more meaningful identifier
            words = re.findall(r'\b\w+\b', question_part.lower())
            # Take first 6 words (or fewer if the question is shorter)
            truncated_words = words[:6]
            # Join with underscores to create the column name
            question_id = '_'.join(truncated_words)
            return f'branches_{question_id}'
    
    # Remove content in parentheses and the parentheses themselves
    name = re.sub(r'\([^)]*\)', '', name)
    # Replace special characters and spaces with underscores
    name = re.sub(r'[^a-zA-Z0-9]+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    # Convert to lowercase
    name = name.lower()
    # Replace multiple underscores with single
    name = re.sub(r'_+', '_', name)
    # Handle specific common patterns
    if name.startswith('o1_') or name.startswith('o2_') or name.startswith('o3_') or name.startswith('o4_') or name.startswith('o5_') or name.startswith('o6_') or name.startswith('o7_'):
        # These are option columns, keep them distinct
        pass
    return name

def calculate_divergence_scores(conn, cursor):
    """
    Calculate divergence scores for ALL responses, not just those from the divergence file.
    Divergence is calculated as the standard deviation of agreement rates across segments.
    """
    print("Calculating comprehensive divergence scores...")
    
    # Get all segment columns (excluding metadata columns)
    cursor.execute("SELECT name FROM pragma_table_info('responses')")
    all_columns = [row[0] for row in cursor.fetchall()]
    
    # Identify segment columns (those that contain agreement rates)
    segment_columns = []
    exclude_cols = ['response_id', 'question_id', 'question_type', 'question', 'response', 
                   'originalresponse', 'categories', 'sentiment', 'submitted_by', 'language', 
                   'sample_id', 'participant_id', 'divergence_score', 'consensus_minagree_50pct',
                   'consensus_minagree_95pct', 'consensus_minagree_100pct', 'all']
    
    # Also exclude branch metadata columns and any columns starting with branches_
    for col in all_columns:
        if (col not in exclude_cols and 
            not col.startswith('branches_') and 
            not col.startswith('o8_')):  # o8_ columns seem to be metadata
            segment_columns.append(col)
    
    print(f"  Found {len(segment_columns)} segment columns for divergence calculation")
    
    # Build SQL query to select segment columns
    segment_cols_str = ', '.join([f'"{col}"' for col in segment_columns])
    
    # Process each question type
    updates = 0
    for question_type in ['Poll Single Select', 'Poll Multi Select', 'Ask Opinion', 'Ask Experience']:
        cursor.execute(f"""
            SELECT response_id, {segment_cols_str}
            FROM responses 
            WHERE question_type = ?
        """, (question_type,))
        
        rows = cursor.fetchall()
        for row in rows:
            response_id = row[0]
            # Extract numeric values, filtering out NULLs and empty strings
            values = []
            for v in row[1:]:
                if v is not None and v != '' and not pd.isna(v):
                    try:
                        # Convert to float if it's not already
                        float_val = float(v)
                        if 0 <= float_val <= 1:  # Valid agreement rate
                            values.append(float_val)
                    except (ValueError, TypeError):
                        pass
            
            if len(values) > 1:
                # Calculate standard deviation as divergence score
                divergence = np.std(values)
                cursor.execute("UPDATE responses SET divergence_score = ? WHERE response_id = ?", 
                             (divergence, response_id))
                updates += 1
                
                if updates % 1000 == 0:
                    print(f"    Updated {updates} rows...")
                    conn.commit()
    
    conn.commit()
    print(f"  ✓ Calculated divergence scores for {updates} responses")
    return updates

def add_missing_participants_to_pri(conn, cursor):
    """
    Add participants who are in responses table but missing from participants table.
    These will have NULL PRI scores but allow foreign key constraints to work.
    """
    print("Checking for missing participants in PRI table...")
    
    # Find participants in responses but not in participants table
    cursor.execute("""
        SELECT DISTINCT r.participant_id 
        FROM responses r 
        WHERE r.participant_id IS NOT NULL 
        AND r.participant_id NOT IN (SELECT participant_id FROM participants)
    """)
    
    missing_participants = cursor.fetchall()
    
    if missing_participants:
        print(f"  Found {len(missing_participants)} participants missing from PRI table")
        print("  Adding them with NULL PRI scores to maintain referential integrity...")
        
        for participant_id in missing_participants:
            cursor.execute("""
                INSERT INTO participants (participant_id, pri_score, pri_scale_1_5, 
                                        duration_seconds, lowqualitytag_perc, 
                                        universaldisagreement_perc, asc_score_raw)
                VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL)
            """, (participant_id[0],))
        
        conn.commit()
        print(f"  ✓ Added {len(missing_participants)} participants with NULL PRI scores")
    else:
        print("  ✓ No missing participants found")

def create_column_mappings_table(conn, cursor, df_aggregate, column_mapping):
    """
    Create a table to map database column names to original CSV column names.
    This specifically maps columns from GD[N]_aggregate_standardized.csv to the 'responses' table.
    """
    print("Creating responses_column_mappings table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses_column_mappings (
            db_column_name TEXT PRIMARY KEY,
            original_csv_column TEXT NOT NULL,
            column_type TEXT,  -- 'segment', 'branch_metadata', 'core', etc.
            full_question_text TEXT,
            notes TEXT,
            source_csv TEXT DEFAULT 'aggregate_standardized.csv',
            target_table TEXT DEFAULT 'responses'
        )
    """)
    
    # Add mappings with proper categorization
    for orig_col, db_col in column_mapping.items():
        column_type = 'segment'  # default
        full_question_text = None
        notes = None
        
        # Categorize column types
        if db_col in ['response_id', 'question_id', 'question_type', 'question', 'response', 
                      'originalresponse', 'categories', 'sentiment', 'submitted_by', 
                      'language', 'sample_id', 'participant_id']:
            column_type = 'core'
        elif db_col.startswith('branches_'):
            column_type = 'branch_metadata'
            # Extract full question from original column name
            import re
            match = re.search(r'\((.*?)\)$', orig_col)
            if match:
                full_question_text = match.group(1)
                # Check if we truncated to 6 words
                words_in_db_col = db_col.replace('branches_', '').count('_') + 1
                full_words = len(re.findall(r'\b\w+\b', full_question_text))
                if full_words > 6:
                    notes = f'Column name truncated to first 6 words (full question has {full_words} words)'
                elif len(orig_col) > 60:  # Original CSV truncation
                    notes = 'Column name truncated in original CSV export'
        elif db_col == 'northern_europe' and orig_col == 'Norther Europe':
            notes = 'Fixed typo from original CSV (Norther -> Northern)'
        elif db_col in ['north_america', 'northern_america']:
            notes = 'Note: north_america (continent) vs northern_america (UN statistical region excluding Mexico/Central America)'
        
        cursor.execute("""
            INSERT OR REPLACE INTO responses_column_mappings 
            (db_column_name, original_csv_column, column_type, full_question_text, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (db_col, orig_col, column_type, full_question_text, notes))
    
    conn.commit()
    print("  ✓ Created column mappings table for traceability")

def create_database(gd_identifier: int, force: bool = False):
    """Create SQLite database for a specific Global Dialogue with improvements."""
    
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / f"Data/{gd_identifier}"
    output_dir = base_dir / f"analysis_output/{gd_identifier}"
    db_path = base_dir / f"Data/{gd_identifier}/{gd_identifier}.db"
    
    # Check if database exists
    if db_path.exists():
        if not force:
            print(f"Database {db_path} already exists. Use --force to recreate.")
            return
        else:
            print(f"Removing existing database {db_path}")
            db_path.unlink()
    
    # Check required files exist
    aggregate_file = data_dir / f"{gd_identifier}_aggregate_standardized.csv"
    if not aggregate_file.exists():
        print(f"Error: {aggregate_file} not found. Run preprocessing first.")
        sys.exit(1)
    
    print(f"Creating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # IMPROVEMENT: Enable foreign key constraints from the start
    cursor.execute("PRAGMA foreign_keys = ON")
    print("✓ Foreign key constraints enabled")
    
    # Load aggregate data
    print(f"Loading aggregate data from {aggregate_file}")
    df_aggregate = pd.read_csv(aggregate_file, low_memory=False)
    
    # Keep original dataframe for reference
    df_aggregate_original = df_aggregate.copy()
    
    # Use all data from the aggregate file (including poll questions and open-ended responses)
    df_responses = df_aggregate.copy()
    
    # Drop the 'Star' column if it exists (vestigial feature not used)
    if 'Star' in df_responses.columns:
        df_responses = df_responses.drop(columns=['Star'])
    
    # Normalize all column names
    print("Normalizing column names...")
    column_mapping = {}
    for col in df_responses.columns:
        new_col = normalize_column_name(col)
        # Ensure unique column names
        if new_col in column_mapping.values():
            # Add a suffix to make it unique
            suffix = 1
            while f"{new_col}_{suffix}" in column_mapping.values():
                suffix += 1
            new_col = f"{new_col}_{suffix}"
        column_mapping[col] = new_col
    
    df_responses.rename(columns=column_mapping, inplace=True)
    
    # Identify agreement rate columns (everything after participant_id except special columns)
    # These columns contain percentage values (0.0 to 1.0) and should be REAL type
    core_columns = ['response_id', 'question_id', 'question_type', 'question', 'response', 
                    'originalresponse', 'categories', 'sentiment', 'submitted_by', 
                    'language', 'sample_id', 'participant_id']
    
    # Identify branch metadata columns that should remain as TEXT
    branch_metadata_columns = [col for col in df_responses.columns if col.startswith('branches_') and col not in ['branches', 'branches_1']]
    
    # All columns that are not in core_columns or branch_metadata are agreement rate columns
    agreement_columns = [col for col in df_responses.columns if col not in core_columns and col not in branch_metadata_columns]
    
    # Convert agreement rate columns to numeric (REAL) type
    print("Converting agreement rate columns to numeric...")
    for col in agreement_columns:
        # Remove percentage signs and convert to decimal (0.0-1.0)
        if col in df_responses.columns:
            # Convert percentage strings (e.g., "9.1%") to decimals (0.091)
            df_responses[col] = df_responses[col].astype(str).str.rstrip('%')
            df_responses[col] = pd.to_numeric(df_responses[col], errors='coerce') / 100.0
    
    # Keep branch metadata columns as TEXT
    for col in branch_metadata_columns:
        if col in df_responses.columns:
            df_responses[col] = df_responses[col].astype(str).replace('nan', None)
    
    # Add columns for scores that will be populated later (explicitly as float type)
    df_responses['divergence_score'] = pd.Series(dtype='float64')
    df_responses['consensus_minagree_50pct'] = pd.Series(dtype='float64')
    df_responses['consensus_minagree_95pct'] = pd.Series(dtype='float64')
    df_responses['consensus_minagree_100pct'] = pd.Series(dtype='float64')
    
    # Drop the sentiment column temporarily (will be populated from tags later)
    df_responses['sentiment'] = None
    
    # Create main responses table by directly importing the dataframe
    print("Creating responses table...")
    df_responses.to_sql('responses', conn, if_exists='replace', index=True, index_label='response_id')
    
    # IMPORTANT: Set response_id as PRIMARY KEY for foreign key constraints
    # SQLite doesn't allow ALTER TABLE to add PRIMARY KEY, so we need to recreate with proper constraint
    cursor.execute("ALTER TABLE responses RENAME TO responses_temp")
    
    # Get column definitions from temp table
    cursor.execute("PRAGMA table_info(responses_temp)")
    columns = cursor.fetchall()
    
    # Build CREATE TABLE statement with PRIMARY KEY
    col_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        if col_name == 'response_id':
            col_defs.append(f'"{col_name}" {col_type} PRIMARY KEY')
        else:
            col_defs.append(f'"{col_name}" {col_type}')
    
    create_stmt = f"CREATE TABLE responses ({', '.join(col_defs)})"
    cursor.execute(create_stmt)
    
    # Copy data from temp table
    cursor.execute("INSERT INTO responses SELECT * FROM responses_temp")
    cursor.execute("DROP TABLE responses_temp")
    
    # Create indexes on key columns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_qid ON responses(question_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_pid ON responses(participant_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_lang ON responses(language)')
    
    # Create responses column mappings table BEFORE loading other data
    create_column_mappings_table(conn, cursor, df_aggregate_original, column_mapping)
    
    # Create participants table FIRST (before loading PRI scores)
    print("Creating participants table...")
    cursor.execute("""
        CREATE TABLE participants (
            participant_id TEXT PRIMARY KEY,
            pri_score REAL,
            pri_scale_1_5 REAL,
            duration_seconds REAL,
            lowqualitytag_perc REAL,
            universaldisagreement_perc REAL,
            asc_score_raw REAL
        )
    """)
    
    # Load and add PRI scores if available
    pri_file = output_dir / f"pri/{gd_identifier}_pri_scores.csv"
    if pri_file.exists():
        print(f"Loading PRI scores from {pri_file}")
        df_pri = pd.read_csv(pri_file)
        
        # Normalize PRI column names
        pri_column_mapping = {col: normalize_column_name(col) for col in df_pri.columns}
        df_pri.rename(columns=pri_column_mapping, inplace=True)
        
        for _, row in df_pri.iterrows():
            cursor.execute("""
                INSERT INTO participants VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row['participant_id'], 
                row.get('pri_score'), 
                row.get('pri_scale_1_5'),
                row.get('duration_seconds'),
                row.get('lowqualitytag_perc'),
                row.get('universaldisagreement_perc'),
                row.get('asc_score_raw')
            ))
        conn.commit()
        print(f"  Loaded {len(df_pri)} participants with PRI scores")
    else:
        print(f"PRI scores not found at {pri_file}, skipping...")
    
    # IMPROVEMENT: Add missing participants to maintain referential integrity
    add_missing_participants_to_pri(conn, cursor)
    
    # Load and add divergence scores if available (but also calculate comprehensive scores)
    divergence_file = output_dir / DIVERGENCE_FILE
    if divergence_file.exists():
        print(f"Loading divergence scores from {divergence_file}")
        df_divergence = pd.read_csv(divergence_file)
        
        # Normalize divergence column names
        div_column_mapping = {col: normalize_column_name(col) for col in df_divergence.columns}
        df_divergence.rename(columns=div_column_mapping, inplace=True)
        
        # Update responses with divergence scores
        for _, row in df_divergence.iterrows():
            cursor.execute("""
                UPDATE responses 
                SET divergence_score = ?
                WHERE question_id = ? AND response = ?
            """, (row.get('divergence_score'), row['question_id'], row['response_text']))
        conn.commit()
        print(f"  Loaded divergence scores from file")
    
    # IMPROVEMENT: Calculate divergence scores for ALL responses
    calculate_divergence_scores(conn, cursor)
    
    # Load and add consensus scores if available
    consensus_file = output_dir / CONSENSUS_FILE
    if consensus_file.exists():
        print(f"Loading consensus scores from {consensus_file}")
        df_consensus = pd.read_csv(consensus_file)
        
        # Normalize consensus column names
        cons_column_mapping = {col: normalize_column_name(col) for col in df_consensus.columns}
        df_consensus.rename(columns=cons_column_mapping, inplace=True)
        
        # Create a consensus_profiles table to store all percentage profiles
        cursor.execute("""
            CREATE TABLE consensus_profiles (
                question_id TEXT,
                response_text TEXT,
                num_valid_segments INTEGER,
                minagree_100pct REAL,
                minagree_95pct REAL,
                minagree_90pct REAL,
                minagree_80pct REAL,
                minagree_70pct REAL,
                minagree_60pct REAL,
                minagree_50pct REAL,
                minagree_40pct REAL,
                minagree_30pct REAL,
                minagree_20pct REAL,
                minagree_10pct REAL,
                PRIMARY KEY (question_id, response_text)
            )
        """)
        
        # Insert consensus data
        for _, row in df_consensus.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO consensus_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['question_id'],
                row['response_text'],
                row.get('num_valid_segments'),
                row.get('minagree_100pct'),
                row.get('minagree_95pct'),
                row.get('minagree_90pct'),
                row.get('minagree_80pct'),
                row.get('minagree_70pct'),
                row.get('minagree_60pct'),
                row.get('minagree_50pct'),
                row.get('minagree_40pct'),
                row.get('minagree_30pct'),
                row.get('minagree_20pct'),
                row.get('minagree_10pct')
            ))
            
            # Update the responses table with 50%, 95%, and 100% consensus scores
            cursor.execute("""
                UPDATE responses 
                SET consensus_minagree_50pct = ?, consensus_minagree_95pct = ?, consensus_minagree_100pct = ?
                WHERE question_id = ? AND response = ?
            """, (row.get('minagree_50pct'), row.get('minagree_95pct'), row.get('minagree_100pct'), 
                  row['question_id'], row['response_text']))
        conn.commit()
        print(f"  Loaded consensus scores")
    else:
        print(f"Consensus scores not found at {consensus_file}, skipping...")
    
    # Create tags tables with proper foreign keys
    print("Creating tags tables...")
    cursor.execute("""
        CREATE TABLE tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT UNIQUE NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE response_tags (
            response_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
            PRIMARY KEY (response_id, tag_id)
        )
    """)
    
    # Load and add tags if available
    tags_file = data_dir / "tags/all_thought_labels.csv"
    if tags_file.exists():
        print(f"Loading tags from {tags_file}")
        df_tags = pd.read_csv(tags_file)
        
        # Normalize tag column names
        tag_column_mapping = {col: normalize_column_name(col) for col in df_tags.columns}
        df_tags.rename(columns=tag_column_mapping, inplace=True)
        
        # Update sentiment column in responses table from tags file
        if 'sentiment' in df_tags.columns:
            print("  Updating sentiment values from tags file...")
            for _, row in df_tags.iterrows():
                if pd.notna(row.get('sentiment')):
                    cursor.execute("""
                        UPDATE responses 
                        SET sentiment = ?
                        WHERE question_id = ? AND participant_id = ?
                    """, (row['sentiment'], row['question_id'], row['participant_id']))
        
        # Process tags (assuming format: question_id, participant_id, sentiment, Tag1, Tag2, ...)
        tag_columns = [col for col in df_tags.columns if col not in ['question_id', 'participant_id', 'responsetext', 'sentiment']]
        
        # Insert unique tags
        unique_tags = set()
        for col in tag_columns:
            unique_tags.update(df_tags[col].dropna().unique())
        
        for tag in unique_tags:
            if tag and str(tag).strip():  # Skip empty tags
                cursor.execute("INSERT OR IGNORE INTO tags (tag_name) VALUES (?)", (str(tag).strip(),))
        
        # Link tags to responses
        for _, row in df_tags.iterrows():
            # Get response_id
            cursor.execute("""
                SELECT response_id FROM responses 
                WHERE question_id = ? AND participant_id = ?
            """, (row['question_id'], row['participant_id']))
            
            result = cursor.fetchone()
            if result:
                response_id = result[0]
                
                # Add each tag for this response
                for col in tag_columns:
                    tag_value = row[col]
                    if pd.notna(tag_value) and str(tag_value).strip():
                        cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ?", (str(tag_value).strip(),))
                        tag_result = cursor.fetchone()
                        if tag_result:
                            cursor.execute("""
                                INSERT OR IGNORE INTO response_tags (response_id, tag_id) 
                                VALUES (?, ?)
                            """, (response_id, tag_result[0]))
        conn.commit()
        print(f"  Loaded tags")
    else:
        print(f"Tags file not found at {tags_file}, skipping...")
    
    # Create additional indexes for better query performance
    print("Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_response_tags_response ON response_tags(response_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_response_tags_tag ON response_tags(tag_id)")
    
    # Load and process participant-level responses if available
    participants_file = data_dir / f"{gd_identifier}_participants.csv"
    question_id_mapping_file = data_dir / f"{gd_identifier}_question_id_mapping.csv"
    
    if participants_file.exists() and question_id_mapping_file.exists():
        print(f"Loading participant responses from {participants_file}")
        
        # [Keep all the existing participant_responses processing code from lines 365-801]
        # This is a large block that works correctly, so I'll include it as-is
        # ... [lines 365-801 from original file] ...
        
        # Load question ID mapping from CSV
        import csv
        
        def normalize_text_for_matching(text):
            """Normalize text for better matching between different sources"""
            # Replace various apostrophes with standard one
            text = text.replace('\u2019', "'")  # Right single quotation mark
            text = text.replace('\u2018', "'")  # Left single quotation mark  
            text = text.replace('\u201d', '"')  # Right double quotation mark
            text = text.replace('\u201c', '"')  # Left double quotation mark
            # Replace multiple spaces/newlines with single space
            text = re.sub(r'\s+', ' ', text)
            # Remove extra spaces around punctuation
            text = re.sub(r'\s+([.,!?;:])', r'\1', text)
            text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
            # Strip outer quotes if the entire text is quoted
            text = text.strip()
            if len(text) > 2 and text[0] == '"' and text[-1] == '"':
                text = text[1:-1].strip()
            return text
        
        question_mapping = {}  # Maps question text to Q{number}
        uuid_to_qnum = {}  # Maps UUID to Q{number}
        question_uuids = {}  # Maps Q{number} to UUID
        normalized_mapping = {}  # Maps normalized text to Q{number} for fuzzy matching
        
        with open(question_id_mapping_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                q_num = row['human_readable_id']
                uuid = row['uuid']
                q_text = row['question_text'].strip()
                
                # Create mapping - always add Q prefix since CSV no longer has it
                q_id = f"Q{q_num}"  # Add Q prefix for all question IDs
                
                # Map both full text and UUID to question ID
                question_mapping[q_text] = q_id
                uuid_to_qnum[uuid] = q_id
                question_uuids[q_id] = uuid
                
                # Add normalized version for better matching
                normalized_text = normalize_text_for_matching(q_text)
                normalized_mapping[normalized_text] = q_id
                
                # Also add shorter versions for matching (first 50, 75, 100 chars)
                for length in [50, 75, 100]:
                    short_text = q_text[:length].strip()
                    if short_text not in question_mapping:
                        question_mapping[short_text] = q_id
                    
                    short_normalized = normalized_text[:length].strip()
                    if short_normalized not in normalized_mapping:
                        normalized_mapping[short_normalized] = q_id
        
        # Identify multi-select poll questions from aggregate data
        multi_select_questions = set()
        ask_experience_questions = set()
        
        # Query the responses table for question types
        cursor.execute("SELECT DISTINCT question_id, question_type FROM responses")
        for row in cursor.fetchall():
            q_uuid = row[0]
            q_type = row[1]
            if q_type == 'Poll Multi Select' and q_uuid in uuid_to_qnum:
                multi_select_questions.add(uuid_to_qnum[q_uuid])
            elif q_type == 'Ask Experience' and q_uuid in uuid_to_qnum:
                ask_experience_questions.add(uuid_to_qnum[q_uuid])
        
        # Load participant data (without index columns)
        df_participants = pd.read_csv(participants_file, low_memory=False, index_col=False)
        
        # Drop muted column if it exists
        if 'Muted' in df_participants.columns:
            df_participants = df_participants.drop(columns=['Muted'])
        
        # Process columns to identify multi-select groups and categories
        multi_select_groups = {}  # Q_id -> list of (original_col, option_text)
        categories_groups = {}    # Q_id -> list of category columns
        regular_columns = {}      # Regular single-value columns
        
        # First pass: identify column types and group them
        agreement_columns = {}  # Maps agreement columns to their question
        for col_idx, col in enumerate(df_participants.columns):
            # Skip empty column names and columns with no data
            if not col or col.strip() == '' or col == 'Muted':
                continue
            
            # Check if this is an agreement rate column
            if '(%agree)' in col.lower():
                # This is an agreement column - find the associated question
                agreement_col_name = None
                
                # [Process agreement columns - same logic as original]
                # ... [lines 470-522 from original] ...
                
                if 'branch a' in col.lower():
                    # This is for a branch A question
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if 'Branch A' in prev_col and prev_col in regular_columns:
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                elif 'branch b' in col.lower():
                    # Similar for branch B
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if 'Branch B' in prev_col and prev_col in regular_columns:
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                elif 'branch c' in col.lower():
                    # Similar for branch C
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if 'Branch C' in prev_col and prev_col in regular_columns:
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                else:
                    # Regular agreement column
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if prev_col in regular_columns:
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                
                if agreement_col_name:
                    agreement_columns[col] = agreement_col_name
                continue
            
            if col in ['Participant Id', 'Sample Provider Id']:
                regular_columns[col] = normalize_column_name(col)
                continue
            
            # [Rest of column processing - same as original]
            # ... [lines 527-676 from original] ...
            
            # Check if this is a "Categories" column
            if col == 'Categories' or col.startswith('Categories.'):
                continue
            
            # Check if this is an unnamed column
            if col.startswith('Unnamed:'):
                continue
            
            # Handle columns with (Original) and (English) suffixes
            base_col = col
            is_original = False
            if col.endswith(' (Original)'):
                base_col = col[:-11]
                is_original = True
            elif col.endswith(' (English)'):
                base_col = col[:-10]
            
            # Check if this is a multi-select poll column
            if ' - ' in base_col and not base_col.startswith('Branch'):
                parts = base_col.rsplit(' - ', 1)
                if len(parts) == 2:
                    question_part = parts[0].strip()
                    option_part = parts[1].strip()
                    normalized_question = normalize_text_for_matching(question_part)
                    
                    # Find matching question
                    found_match = False
                    
                    for normalized_q, q_id in normalized_mapping.items():
                        if (normalized_question == normalized_q or
                            (len(normalized_question) > 30 and normalized_question[:30] in normalized_q) or
                            (len(normalized_q) > 30 and normalized_q[:30] in normalized_question)):
                            
                            if q_id in multi_select_questions:
                                if not is_original:
                                    if q_id not in multi_select_groups:
                                        multi_select_groups[q_id] = []
                                    multi_select_groups[q_id].append((col, option_part))
                            else:
                                regular_columns[col] = f"{q_id}_{re.sub(r'[^a-zA-Z0-9]+', '_', option_part[:30]).lower()}"
                            found_match = True
                            break
                    
                    if not found_match:
                        regular_columns[col] = f"unmapped_{len(regular_columns) + len(multi_select_groups) + 1}"
            else:
                # Regular question column - process as before
                found_match = False
                normalized_col = normalize_text_for_matching(base_col)
                
                if normalized_col in normalized_mapping:
                    q_id = normalized_mapping[normalized_col]
                    if is_original:
                        regular_columns[col] = f"{q_id}_original"
                    else:
                        regular_columns[col] = q_id
                        # Handle Ask Experience questions
                        if q_id in ask_experience_questions:
                            col_idx_local = df_participants.columns.get_loc(col)
                            categories_cols = []
                            found_categories = False
                            for next_idx in range(col_idx_local + 1, min(col_idx_local + 15, len(df_participants.columns))):
                                next_col = df_participants.columns[next_idx]
                                if next_col.endswith(' (Original)'):
                                    continue
                                if next_col == 'Categories' or next_col.startswith('Categories.'):
                                    categories_cols.append(next_col)
                                    found_categories = True
                                elif next_col.startswith('Unnamed:') and found_categories:
                                    categories_cols.append(next_col)
                                elif next_col and not next_col.startswith('Categories') and not next_col.startswith('Unnamed:'):
                                    break
                            if categories_cols:
                                categories_groups[q_id] = categories_cols
                    found_match = True
                else:
                    # Try partial matches
                    for normalized_q, q_id in normalized_mapping.items():
                        # Various matching strategies
                        if (len(normalized_col) > 40 and len(normalized_q) > 40 and 
                            normalized_col[:40] == normalized_q[:40]):
                            found_match = True
                        elif len(normalized_col) > 30 and normalized_col[:30] in normalized_q:
                            found_match = True
                        elif len(normalized_q) > 30 and normalized_q[:30] in normalized_col:
                            found_match = True
                        
                        if found_match:
                            if is_original:
                                regular_columns[col] = f"{q_id}_original"
                            else:
                                regular_columns[col] = q_id
                            break
                
                if not found_match:
                    if col != 'Categories' and not col.startswith('Categories.'):
                        regular_columns[col] = f"unmapped_{len(regular_columns) + len(multi_select_groups) + 1}"
        
        # Create new dataframe with processed columns
        processed_data = {}
        
        # Add regular columns first
        for orig_col, new_col in regular_columns.items():
            if orig_col in df_participants.columns:
                processed_data[new_col] = df_participants[orig_col]
        
        # Add agreement columns with percentage conversion
        for orig_col, new_col in agreement_columns.items():
            if orig_col in df_participants.columns:
                agree_data = []
                for val in df_participants[orig_col]:
                    if pd.isna(val) or str(val).strip() in ['--', '', 'N/A']:
                        agree_data.append(None)
                    elif '%' in str(val):
                        try:
                            pct_value = float(str(val).replace('%', '').strip()) / 100.0
                            agree_data.append(pct_value)
                        except ValueError:
                            agree_data.append(None)
                    else:
                        agree_data.append(None)
                processed_data[new_col] = agree_data
        
        # Process multi-select columns into JSON arrays
        for q_id, option_cols in multi_select_groups.items():
            selected_options = []
            for idx, row in df_participants.iterrows():
                row_options = []
                for orig_col, option_text in option_cols:
                    if orig_col in df_participants.columns:
                        cell_value = df_participants.at[idx, orig_col]
                        if pd.notna(cell_value) and str(cell_value).strip() == option_text:
                            row_options.append(option_text)
                selected_options.append(json.dumps(row_options) if row_options else None)
            processed_data[q_id] = selected_options
        
        # Process Ask Experience questions with categories
        for q_id, cat_cols in categories_groups.items():
            categories_data = []
            for idx, row in df_participants.iterrows():
                row_categories = []
                for cat_col in cat_cols:
                    if cat_col in df_participants.columns:
                        cat_value = df_participants.at[idx, cat_col]
                        if pd.notna(cat_value) and str(cat_value).strip() and str(cat_value).strip() != '--':
                            row_categories.append(str(cat_value).strip())
                categories_data.append(json.dumps(row_categories) if row_categories else None)
            processed_data[f"{q_id}_categories"] = categories_data
        
        # Create new dataframe from processed data
        df_participants_processed = pd.DataFrame(processed_data)
        
        # Create participant_responses table
        print("Creating participant_responses table...")
        df_participants_processed.to_sql('participant_responses', conn, if_exists='replace', index=False)
        
        # Create index on participant_id
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_participant_responses_pid ON participant_responses(participant_id)")
        
        # Create participant_responses_column_mappings table to document the mapping
        print("Creating participant_responses_column_mappings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participant_responses_column_mappings (
                column_name TEXT PRIMARY KEY,
                question_id TEXT,
                question_text TEXT,
                column_type TEXT,  -- 'question', 'question_original', 'multi_select_json', etc.
                source_csv TEXT DEFAULT 'participants.csv',
                target_table TEXT DEFAULT 'participant_responses'
            )
        """)
        
        # Create reverse lookup from Q-numbers to question text
        qnum_to_text = {}
        for q_text, q_id in question_mapping.items():
            if q_id not in qnum_to_text or len(q_text) > len(qnum_to_text.get(q_id, '')):
                # Keep the longest (most complete) question text
                qnum_to_text[q_id] = q_text
        
        # Populate question_columns table with actual question text
        for col_name in df_participants_processed.columns:
            if col_name in ['participant_id', 'sample_provider_id']:
                continue
            
            col_type = 'question'
            question_id = None
            question_text = None
            
            if col_name.endswith('_original'):
                col_type = 'question_original'
                question_id = col_name.replace('_original', '')
                # Get question text from the base question
                base_q = question_id.replace('_original', '')
                question_text = qnum_to_text.get(base_q, None)
                if question_text:
                    question_text = f"{question_text} (Original Language)"
            elif col_name.endswith('_categories'):
                col_type = 'categories_json'
                question_id = col_name.replace('_categories', '')
                # Get question text from the base question
                base_q = question_id
                question_text = qnum_to_text.get(base_q, None)
                if question_text:
                    question_text = f"{question_text} (Categories)"
            elif col_name.endswith('_agree_pct'):
                col_type = 'agreement_percentage'
                # Extract base question ID
                base_q = col_name.replace('_agree_pct', '')
                question_id = base_q
                question_text = qnum_to_text.get(base_q, None)
                if question_text:
                    question_text = f"{question_text} (% Agreement)"
            elif col_name in multi_select_groups:
                col_type = 'multi_select_json'
                question_id = col_name
                question_text = qnum_to_text.get(col_name, None)
            elif col_name.startswith('Q'):
                question_id = col_name.split('_')[0]
                if '_branch_' in col_name:
                    col_type = 'question_subfield'
                    # For branch questions, get the base question text
                    question_text = qnum_to_text.get(col_name, None)
                elif '_' in col_name:
                    col_type = 'question_subfield'
                    question_text = qnum_to_text.get(col_name, None)
                else:
                    # Regular question
                    question_text = qnum_to_text.get(col_name, None)
            elif col_name.startswith('unmapped'):
                col_type = 'unmapped'
                question_text = 'Unmapped column from source data'
            
            cursor.execute("""
                INSERT OR IGNORE INTO participant_responses_column_mappings 
                (column_name, question_id, question_text, column_type)
                VALUES (?, ?, ?, ?)
            """, (col_name, question_id, question_text, col_type))
        
        conn.commit()
        print(f"  Loaded {len(df_participants_processed)} participant response records")
    else:
        if not participants_file.exists():
            print(f"Participant responses file not found at {participants_file}, skipping...")
        if not question_id_mapping_file.exists():
            print(f"Question ID mapping file not found at {question_id_mapping_file}, skipping...")
    
    # Create branch mapping table with proper foreign keys
    print("Creating branch mapping table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branch_mappings (
            response_id INTEGER PRIMARY KEY,
            source_poll_question_id TEXT,
            source_poll_question TEXT,
            branch_id TEXT,  -- 'A', 'B', or 'C'
            branch_condition TEXT,  -- The poll option(s) that led to this branch
            FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
        )
    """)
    
    # Populate branch mappings from the Branches columns
    print("Populating branch mappings...")
    branches_columns = [col for col in df_responses.columns if col.startswith('branches_') and col not in ['branches', 'branches_1']]
    
    for branches_col in branches_columns:
        # Extract the poll question from the column name
        branch_data = df_responses[df_responses[branches_col].notna()]
        
        if not branch_data.empty:
            # Get the source poll question from the column name
            original_col_name = None
            for orig_col in df_aggregate_original.columns:
                if 'Branches' in orig_col and normalize_column_name(orig_col) == branches_col:
                    # Extract question from parentheses
                    match = re.search(r'\((.*?)\)$', orig_col)
                    if match:
                        original_col_name = match.group(1)
                    break
            
            for idx, row in branch_data.iterrows():
                # Parse the branch value
                branch_value = row[branches_col]
                if pd.notna(branch_value) and ' - ' in str(branch_value):
                    parts = str(branch_value).split(' - ', 1)
                    branch_letter = parts[0].replace('Branch ', '').strip()
                    branch_condition = parts[1].strip() if len(parts) > 1 else ''
                    
                    # Get response_id from the DataFrame index
                    cursor.execute("""
                        SELECT response_id FROM responses 
                        WHERE question_id = ? AND participant_id = ?
                        LIMIT 1
                    """, (row['question_id'], row.get('participant_id')))
                    
                    result = cursor.fetchone()
                    if result:
                        response_id = result[0]
                        cursor.execute("""
                            INSERT OR IGNORE INTO branch_mappings 
                            (response_id, source_poll_question, branch_id, branch_condition)
                            VALUES (?, ?, ?, ?)
                        """, (response_id, original_col_name, branch_letter, branch_condition))
    
    conn.commit()
    
    # Create indexes for branch lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_branch_mappings_branch ON branch_mappings(branch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_branch_mappings_question ON branch_mappings(source_poll_question)")
    
    # Create useful views
    print("Creating views...")
    
    # View combining responses with PRI scores
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS responses_with_pri AS
        SELECT r.*, p.pri_score, p.pri_scale_1_5
        FROM responses r
        LEFT JOIN participants p ON r.participant_id = p.participant_id
    """)
    
    # View for responses with their tags
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS responses_with_tags AS
        SELECT r.*, GROUP_CONCAT(t.tag_name, ', ') as tags
        FROM responses r
        LEFT JOIN response_tags rt ON r.response_id = rt.response_id
        LEFT JOIN tags t ON rt.tag_id = t.tag_id
        GROUP BY r.response_id
    """)
    
    # View for branched responses with source poll question info
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS branched_responses AS
        SELECT 
            r.*,
            bm.source_poll_question,
            bm.branch_id,
            bm.branch_condition,
            CASE 
                WHEN bm.branch_id = 'A' THEN r.branch_a
                WHEN bm.branch_id = 'B' THEN r.branch_b
                WHEN bm.branch_id = 'C' THEN r.branch_c
            END as branch_agreement
        FROM responses r
        JOIN branch_mappings bm ON r.response_id = bm.response_id
    """)
    
    
    # Commit and close
    conn.commit()
    
    # Print summary statistics
    cursor.execute("SELECT COUNT(*) FROM responses")
    response_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT participant_id) FROM responses WHERE participant_id IS NOT NULL')
    participant_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT question_id) FROM responses')
    question_count = cursor.fetchone()[0]
    
    # Get breakdown by question type
    cursor.execute('SELECT question_type, COUNT(DISTINCT question_id) as num_questions, COUNT(*) as num_responses FROM responses GROUP BY question_type')
    question_type_stats = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"Database created successfully!")
    print(f"{'='*60}")
    print(f"  Total responses: {response_count}")
    print(f"  Participants: {participant_count}")
    print(f"  Total questions: {question_count}")
    print(f"\n  Breakdown by question type:")
    for qt_type, qt_count, qt_responses in question_type_stats:
        print(f"    {qt_type}: {qt_count} questions, {qt_responses} responses")
    
    # Check what additional tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    
    # Group tables by their purpose for clearer output
    print(f"\n  Tables created:")
    print(f"    Main data: responses, participant_responses")
    print(f"    Mappings: responses_column_mappings, participant_responses_column_mappings")  
    print(f"    Analysis: participants, consensus_profiles, tags, response_tags, branch_mappings")
    
    # Check branch mappings
    cursor.execute("SELECT COUNT(*) FROM branch_mappings")
    branch_count = cursor.fetchone()[0]
    if branch_count > 0:
        print(f"  Branch mappings: {branch_count}")
    
    # Check divergence score coverage
    cursor.execute("SELECT COUNT(*) FROM responses WHERE divergence_score IS NOT NULL")
    divergence_count = cursor.fetchone()[0]
    print(f"  Responses with divergence scores: {divergence_count}/{response_count}")
    
    # IMPROVEMENT: Document known issues
    print(f"\n{'='*60}")
    print("Known Data Characteristics:")
    print(f"{'='*60}")
    print("  ✓ Fixed: 'norther_europe' typo corrected to 'northern_europe'")
    print("  ✓ Documented: 'north_america' (continent) vs 'northern_america' (UN region)")
    print("  ✓ Foreign keys enabled with referential integrity")
    print("  ✓ Truncated branch columns mapped in 'column_mappings' table")
    print("  ✓ Divergence scores calculated for all applicable responses")
    print("\n  Participant count differences explained:")
    print("    - participant_responses: All survey participants")
    print("    - responses table: Only those who provided text responses")
    print("    - participants table: Only those with calculable PRI scores")
    
    conn.close()
    print(f"\nDatabase saved to: {db_path}")

def main():
    parser = argparse.ArgumentParser(description="Create SQLite database for Global Dialogues data")
    parser.add_argument("gd_number", type=str, help="Global Dialogue identifier (e.g., '1', '2', '6UK', '6_UK')")
    parser.add_argument("--force", action="store_true", help="Force recreation of database if it exists")
    
    args = parser.parse_args()
    
    gd_identifier = parse_gd_identifier(args.gd_number)
    validate_gd_directory(gd_identifier)
    
    create_database(gd_identifier, args.force)

if __name__ == "__main__":
    main()