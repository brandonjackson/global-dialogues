#!/usr/bin/env python3
"""
Create SQLite database for Global Dialogues data analysis.

This script creates a comprehensive SQLite database combining:
- ALL data from aggregate_standardized.csv (both poll questions and open-ended responses)
- PRI scores per participant
- Divergence and consensus scores per response
- Tag labels for responses

All column names are normalized to lowercase_underscored format for consistency.
"""

import argparse
import sqlite3
import pandas as pd
from pathlib import Path
import sys
import re

# Constants for file paths
DIVERGENCE_FILE = "divergence/divergence_by_question.csv"
CONSENSUS_FILE = "consensus/consensus_profiles.csv"

def normalize_column_name(name):
    """Convert column names to lowercase_underscored format."""
    import re
    original_name = name
    
    # Special handling for "Branches" columns - keep the question part as identifier
    if name.startswith('Branches (') and name.endswith(')'):
        # Extract the question part and create a unique identifier
        match = re.search(r'Branches \((.*?)\)', name)
        if match:
            question_part = match.group(1)
            # Create a short identifier from the question
            question_id = re.sub(r'[^a-zA-Z0-9]+', '_', question_part[:50]).strip('_').lower()
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

def create_database(gd_number: int, force: bool = False):
    """Create SQLite database for a specific Global Dialogue."""
    
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / f"Data/GD{gd_number}"
    output_dir = base_dir / f"analysis_output/GD{gd_number}"
    db_path = base_dir / f"Data/GD{gd_number}/GD{gd_number}.db"
    
    # Check if database exists
    if db_path.exists():
        if not force:
            print(f"Database {db_path} already exists. Use --force to recreate.")
            return
        else:
            print(f"Removing existing database {db_path}")
            db_path.unlink()
    
    # Check required files exist
    aggregate_file = data_dir / f"GD{gd_number}_aggregate_standardized.csv"
    if not aggregate_file.exists():
        print(f"Error: {aggregate_file} not found. Run preprocessing first.")
        sys.exit(1)
    
    print(f"Creating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load aggregate data
    print(f"Loading aggregate data from {aggregate_file}")
    df_aggregate = pd.read_csv(aggregate_file, low_memory=False)
    
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
    
    # Create indexes on key columns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_qid ON responses(question_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_pid ON responses(participant_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_lang ON responses(language)')
    
    # Load and add PRI scores if available
    pri_file = output_dir / f"pri/GD{gd_number}_pri_scores.csv"
    if pri_file.exists():
        print(f"Loading PRI scores from {pri_file}")
        df_pri = pd.read_csv(pri_file)
        
        # Normalize PRI column names
        pri_column_mapping = {col: normalize_column_name(col) for col in df_pri.columns}
        df_pri.rename(columns=pri_column_mapping, inplace=True)
        
        # Create participants table
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
    else:
        print(f"PRI scores not found at {pri_file}, skipping...")
    
    # Load and add divergence scores if available
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
    else:
        print(f"Divergence scores not found at {divergence_file}, skipping...")
    
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
    else:
        print(f"Consensus scores not found at {consensus_file}, skipping...")
    
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
            print("Updating sentiment values from tags file...")
            for _, row in df_tags.iterrows():
                if pd.notna(row.get('sentiment')):
                    cursor.execute("""
                        UPDATE responses 
                        SET sentiment = ?
                        WHERE question_id = ? AND participant_id = ?
                    """, (row['sentiment'], row['question_id'], row['participant_id']))
        
        # Create tags tables
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
                FOREIGN KEY (response_id) REFERENCES responses(response_id),
                FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
                PRIMARY KEY (response_id, tag_id)
            )
        """)
        
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
    else:
        print(f"Tags file not found at {tags_file}, skipping...")
    
    # Create additional indexes for better query performance
    print("Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_response_tags_response ON response_tags(response_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_response_tags_tag ON response_tags(tag_id)")
    
    # Load and process participant-level responses if available
    participants_file = data_dir / f"GD{gd_number}_participants.csv"
    question_id_mapping_file = data_dir / f"GD{gd_number}_question_id_mapping.csv"
    
    if participants_file.exists() and question_id_mapping_file.exists():
        print(f"Loading participant responses from {participants_file}")
        
        # Load question ID mapping from CSV
        import csv
        import re
        import json
        
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
                
                # Create mapping - add Q prefix only if not already present
                if q_num.startswith('Q'):
                    q_id = q_num  # Already has Q prefix (like Q114_branch_a)
                else:
                    q_id = f"Q{q_num}"  # Add Q prefix for regular numbers
                
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
        
        # Drop unnamed columns (empty columns from CSV)
        unnamed_cols = [col for col in df_participants.columns if col.startswith('Unnamed:')]
        if unnamed_cols:
            df_participants = df_participants.drop(columns=unnamed_cols)
            print(f"  Dropped {len(unnamed_cols)} unnamed columns")
        
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
            
            # Also skip columns that are entirely empty (no actual header text)
            if len(str(col).strip()) == 0:
                continue
            
            # Check if this is an agreement rate column
            if '(%agree)' in col.lower():
                # This is an agreement column
                # Check if it's for a branch question
                agreement_col_name = None
                
                if 'branch a' in col.lower():
                    # This is for a branch A question - find Q114 or Q145
                    if col_idx > 0:
                        # Look for the associated branch question
                        for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                            prev_col = df_participants.columns[prev_idx]
                            if 'Branch A' in prev_col and prev_col in regular_columns:
                                base_q_id = regular_columns[prev_col]
                                if base_q_id.endswith('_original'):
                                    base_q_id = base_q_id[:-9]  # Remove '_original' suffix
                                agreement_col_name = f"{base_q_id}_agree_pct"
                                break
                elif 'branch b' in col.lower():
                    # This is for a branch B question
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if 'Branch B' in prev_col and prev_col in regular_columns:
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]  # Remove '_original' suffix
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                elif 'branch c' in col.lower():
                    # This is for a branch C question
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if 'Branch C' in prev_col and prev_col in regular_columns:
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]  # Remove '_original' suffix
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                else:
                    # Regular "All (%agree)" column - find the previous Ask Opinion question
                    for prev_idx in range(col_idx - 1, max(0, col_idx - 10), -1):
                        prev_col = df_participants.columns[prev_idx]
                        if prev_col in regular_columns:
                            # Get the base question ID without _original suffix
                            base_q_id = regular_columns[prev_col]
                            if base_q_id.endswith('_original'):
                                base_q_id = base_q_id[:-9]  # Remove '_original' suffix
                            agreement_col_name = f"{base_q_id}_agree_pct"
                            break
                
                if agreement_col_name:
                    agreement_columns[col] = agreement_col_name
                    print(f"  Found agreement column: {agreement_col_name} for {col[:50]}...")
                else:
                    # Couldn't find the associated question
                    print(f"  WARNING: Agreement column without clear question: {col[:50]}...")
                    regular_columns[col] = f"unmapped_{len(regular_columns) + len(multi_select_groups) + 1}"
                continue
                
            if col in ['Participant Id', 'Sample Provider Id']:
                regular_columns[col] = normalize_column_name(col)
                continue
            
            # Check if this is a "Categories" column (follows an Ask Experience question)
            if col == 'Categories' or col.startswith('Categories.'):
                # Skip categories columns - they'll be merged with their parent question
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
                # Split on last ' - ' to get question and option
                parts = base_col.rsplit(' - ', 1)
                if len(parts) == 2:
                    question_part = parts[0].strip()
                    option_part = parts[1].strip()
                    normalized_question = normalize_text_for_matching(question_part)
                    
                    # Find matching question
                    found_match = False
                    
                    # First try normalized exact/partial matches
                    for normalized_q, q_id in normalized_mapping.items():
                        if (normalized_question == normalized_q or
                            (len(normalized_question) > 30 and normalized_question[:30] in normalized_q) or
                            (len(normalized_q) > 30 and normalized_q[:30] in normalized_question)):
                            
                            # Check if this is a multi-select question
                            if q_id in multi_select_questions:
                                if not is_original:  # Only process English versions for multi-select
                                    if q_id not in multi_select_groups:
                                        multi_select_groups[q_id] = []
                                    multi_select_groups[q_id].append((col, option_part))
                            else:
                                # Not a multi-select, treat as regular column
                                regular_columns[col] = f"{q_id}_{re.sub(r'[^a-zA-Z0-9]+', '_', option_part[:30]).lower()}"
                            found_match = True
                            break
                    
                    if not found_match:
                        # No match found
                        regular_columns[col] = f"unmapped_{len(regular_columns) + len(multi_select_groups) + 1}"
            else:
                # Regular question column
                found_match = False
                clean_col = base_col.replace('\n', ' ').replace('  ', ' ').strip()
                normalized_col = normalize_text_for_matching(base_col)
                
                # First try exact match on normalized text
                if normalized_col in normalized_mapping:
                    q_id = normalized_mapping[normalized_col]
                    if is_original:
                        regular_columns[col] = f"{q_id}_original"
                    else:
                        regular_columns[col] = q_id
                        # Debug for specific questions
                        if q_id in ['Q39', 'Q40', 'Q43']:
                            print(f"  Mapped column to {q_id}: {col[:60]}...")
                        # Handle Ask Experience questions
                        if q_id in ask_experience_questions:
                            col_idx = df_participants.columns.get_loc(col)
                            categories_cols = []
                            for next_idx in range(col_idx + 1, min(col_idx + 10, len(df_participants.columns))):
                                next_col = df_participants.columns[next_idx]
                                if next_col == 'Categories' or next_col.startswith('Categories.'):
                                    categories_cols.append(next_col)
                                elif next_col and not next_col.startswith('Categories'):
                                    break
                            if categories_cols:
                                categories_groups[q_id] = categories_cols
                    found_match = True
                else:
                    # Try partial matches on normalized text
                    for normalized_q, q_id in normalized_mapping.items():
                        # Try various matching strategies
                        if (len(normalized_col) > 40 and len(normalized_q) > 40 and 
                            normalized_col[:40] == normalized_q[:40]):
                            # First 40 chars match
                            found_match = True
                        elif (len(normalized_col) > 60 and len(normalized_q) > 60 and 
                              normalized_col[:60] == normalized_q[:60]):
                            # First 60 chars match
                            found_match = True
                        elif (len(normalized_col) > 80 and len(normalized_q) > 80 and 
                              normalized_col[:80] == normalized_q[:80]):
                            # First 80 chars match  
                            found_match = True
                        elif (len(normalized_col) > 90 and len(normalized_q) > 90 and 
                              normalized_col[:90] == normalized_q[:90]):
                            # First 90 chars match  
                            found_match = True
                        elif len(normalized_col) > 30 and normalized_col[:30] in normalized_q:
                            # Start of column matches part of question
                            found_match = True
                        elif len(normalized_q) > 30 and normalized_q[:30] in normalized_col:
                            # Start of question matches part of column
                            found_match = True
                        elif len(normalized_col) > 50 and normalized_col in normalized_q:
                            # Entire column text is subset of question
                            found_match = True
                        elif len(normalized_q) > 50 and normalized_q in normalized_col:
                            # Entire question text is subset of column
                            found_match = True
                        
                        if found_match:
                            if is_original:
                                regular_columns[col] = f"{q_id}_original"
                            else:
                                regular_columns[col] = q_id
                                # Handle Ask Experience questions
                                if q_id in ask_experience_questions:
                                    col_idx = df_participants.columns.get_loc(col)
                                    categories_cols = []
                                    for next_idx in range(col_idx + 1, min(col_idx + 10, len(df_participants.columns))):
                                        next_col = df_participants.columns[next_idx]
                                        if next_col == 'Categories' or next_col.startswith('Categories.'):
                                            categories_cols.append(next_col)
                                        elif next_col and not next_col.startswith('Categories'):
                                            break
                                    if categories_cols:
                                        categories_groups[q_id] = categories_cols
                            break
                
                if not found_match:
                    if col != 'Categories' and not col.startswith('Categories.'):
                        regular_columns[col] = f"unmapped_{len(regular_columns) + len(multi_select_groups) + 1}"
        
        # Now create the final dataframe with merged columns
        print(f"  Processing {len(multi_select_groups)} multi-select questions and {len(categories_groups)} questions with categories")
        
        # Debug: Check if Q39, Q40, Q43 are in regular_columns
        for q in ['Q39', 'Q40', 'Q43']:
            if q in regular_columns.values():
                print(f"  {q} found in regular_columns")
            else:
                print(f"  ERROR: {q} NOT found in regular_columns!")
        
        # Create new dataframe with processed columns
        processed_data = {}
        
        # Add regular columns first
        for orig_col, new_col in regular_columns.items():
            if orig_col in df_participants.columns:
                processed_data[new_col] = df_participants[orig_col]
        
        # Add agreement columns with percentage conversion
        for orig_col, new_col in agreement_columns.items():
            if orig_col in df_participants.columns:
                # Convert percentage strings to floats
                agree_data = []
                for val in df_participants[orig_col]:
                    if pd.isna(val) or str(val).strip() in ['--', '', 'N/A']:
                        agree_data.append(None)
                    elif '%' in str(val):
                        try:
                            # Remove % and convert to decimal (52% -> 0.52)
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
                        # Check if this option was selected (cell contains the option text)
                        if pd.notna(cell_value) and str(cell_value).strip() == option_text:
                            row_options.append(option_text)
                selected_options.append(json.dumps(row_options) if row_options else None)
            processed_data[q_id] = selected_options
        
        # Process Ask Experience questions with categories
        for q_id, cat_cols in categories_groups.items():
            # The main question response is already in regular_columns
            # Create a categories JSON column
            categories_data = []
            for idx, row in df_participants.iterrows():
                row_categories = []
                for cat_col in cat_cols:
                    if cat_col in df_participants.columns:
                        cat_value = df_participants.at[idx, cat_col]
                        if pd.notna(cat_value) and str(cat_value).strip():
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
        
        # Create question_columns table to document the mapping
        print("Creating question_columns mapping table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_columns (
                column_name TEXT PRIMARY KEY,
                question_id TEXT,
                question_text TEXT,
                column_type TEXT  -- 'question', 'question_original', 'multi_select_option'
            )
        """)
        
        # Populate question_columns table with new structure
        for col_name in df_participants_processed.columns:
            if col_name in ['participant_id', 'sample_provider_id']:
                continue
            
            col_type = 'question'
            question_id = None
            question_text = None
            
            if col_name.endswith('_original'):
                col_type = 'question_original'
                question_id = col_name.replace('_original', '')
            elif col_name.endswith('_categories'):
                col_type = 'categories_json'
                question_id = col_name.replace('_categories', '')
            elif col_name in multi_select_groups:
                col_type = 'multi_select_json'
                question_id = col_name
                # Get the original question text from mapping
                if col_name in question_uuids:
                    uuid = question_uuids[col_name]
                    for q_text, q_id in question_mapping.items():
                        if q_id == col_name:
                            question_text = q_text
                            break
            elif col_name.startswith('Q'):
                question_id = col_name.split('_')[0]
                if '_' in col_name:
                    col_type = 'question_subfield'
            elif col_name.startswith('unmapped'):
                col_type = 'unmapped'
            
            cursor.execute("""
                INSERT OR IGNORE INTO question_columns (column_name, question_id, question_text, column_type)
                VALUES (?, ?, ?, ?)
            """, (col_name, question_id, question_text, col_type))
        
        print(f"  Loaded {len(df_participants_processed)} participant response records")
    else:
        if not participants_file.exists():
            print(f"Participant responses file not found at {participants_file}, skipping...")
        if not question_id_mapping_file.exists():
            print(f"Question ID mapping file not found at {question_id_mapping_file}, skipping...")
    
    # Create branch mapping table
    print("Creating branch mapping table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branch_mappings (
            response_id INTEGER PRIMARY KEY,
            source_poll_question_id TEXT,
            source_poll_question TEXT,
            branch_id TEXT,  -- 'A', 'B', or 'C'
            branch_condition TEXT,  -- The poll option(s) that led to this branch
            FOREIGN KEY (response_id) REFERENCES responses(response_id)
        )
    """)
    
    # Populate branch mappings from the Branches columns
    print("Populating branch mappings...")
    branches_columns = [col for col in df_responses.columns if col.startswith('branches_') and col not in ['branches', 'branches_1']]
    
    for branches_col in branches_columns:
        # Extract the poll question from the column name
        branch_data = df_responses[df_responses[branches_col].notna()]
        
        if not branch_data.empty:
            # Get the source poll question from the column name (in parentheses in original CSV)
            original_col_name = None
            for orig_col in df_aggregate.columns:
                if 'Branches' in orig_col and normalize_column_name(orig_col) == branches_col:
                    # Extract question from parentheses
                    import re
                    match = re.search(r'\((.*?)\)$', orig_col)
                    if match:
                        original_col_name = match.group(1)
                    break
            
            for idx, row in branch_data.iterrows():
                # Parse the branch value (e.g., "Branch A - Yes")
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
    
    # Create index for branch lookups
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
    
    print(f"\nDatabase created successfully!")
    print(f"  Total responses: {response_count}")
    print(f"  Participants: {participant_count}")
    print(f"  Total questions: {question_count}")
    print(f"\n  Breakdown by question type:")
    for qt_type, qt_count, qt_responses in question_type_stats:
        print(f"    {qt_type}: {qt_count} questions, {qt_responses} responses")
    
    # Check what additional tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"  Tables created: {', '.join([t[0] for t in tables])}")
    
    # Check branch mappings
    cursor.execute("SELECT COUNT(*) FROM branch_mappings")
    branch_count = cursor.fetchone()[0]
    if branch_count > 0:
        print(f"  Branch mappings: {branch_count}")
    
    # Show sample of normalized column names
    cursor.execute("PRAGMA table_info(responses)")
    columns = cursor.fetchall()
    print(f"\nSample normalized column names in responses table:")
    for col in columns[:10]:
        print(f"  - {col[1]}")
    
    conn.close()
    print(f"\nDatabase saved to: {db_path}")

def main():
    parser = argparse.ArgumentParser(description="Create SQLite database for Global Dialogues data")
    parser.add_argument("gd_number", type=int, help="Global Dialogue number (e.g., 1, 2, 3, 4, 5)")
    parser.add_argument("--force", action="store_true", help="Force recreation of database if it exists")
    
    args = parser.parse_args()
    
    create_database(args.gd_number, args.force)

if __name__ == "__main__":
    main()