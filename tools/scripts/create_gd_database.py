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
    
    # All columns that are not in core_columns are agreement rate columns
    agreement_columns = [col for col in df_responses.columns if col not in core_columns]
    
    # Convert agreement rate columns to numeric (REAL) type
    print("Converting agreement rate columns to numeric...")
    for col in agreement_columns:
        # Remove percentage signs and convert to decimal (0.0-1.0)
        if col in df_responses.columns:
            # Convert percentage strings (e.g., "9.1%") to decimals (0.091)
            df_responses[col] = df_responses[col].astype(str).str.rstrip('%')
            df_responses[col] = pd.to_numeric(df_responses[col], errors='coerce') / 100.0
    
    # Add columns for scores that will be populated later
    df_responses['divergence_score'] = None
    df_responses['consensus_minagree_50pct'] = None
    
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
            
            # Also update the responses table with the 50% consensus score as default
            cursor.execute("""
                UPDATE responses 
                SET consensus_minagree_50pct = ?
                WHERE question_id = ? AND response = ?
            """, (row.get('minagree_50pct'), row['question_id'], row['response_text']))
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