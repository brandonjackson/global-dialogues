#!/usr/bin/env python3
"""
Create SQLite database for Global Dialogues data analysis.

This script creates a comprehensive SQLite database combining:
- Core response data from aggregate_standardized.csv
- PRI scores per participant
- Divergence and consensus scores per response
- Tag labels for responses
"""

import argparse
import sqlite3
import pandas as pd
from pathlib import Path
import sys
import json

# Constants for file paths
DIVERGENCE_FILE = "divergence/divergence_by_question.csv"
CONSENSUS_FILE = "consensus/consensus_profiles.csv"

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
    
    # Filter to only include rows with Participant ID (skip aggregate rows)
    df_responses = df_aggregate[df_aggregate['Participant ID'].notna()].copy()
    
    # Add columns for scores that will be populated later
    df_responses['divergence_score'] = None
    df_responses['consensus_minagree_50pct'] = None
    
    # Create main responses table by directly importing the dataframe
    print("Creating responses table...")
    df_responses.to_sql('responses', conn, if_exists='replace', index=True, index_label='response_id')
    
    # Create indexes on key columns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_qid ON responses("Question ID")')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resp_pid ON responses("Participant ID")')
    
    # Load and add PRI scores if available
    pri_file = output_dir / f"pri/GD{gd_number}_pri_scores.csv"
    if pri_file.exists():
        print(f"Loading PRI scores from {pri_file}")
        df_pri = pd.read_csv(pri_file)
        
        # Check actual column names in PRI file
        print(f"  PRI columns: {df_pri.columns.tolist()}")
        
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
                INSERT INTO participants (participant_id, pri_score, pri_scale_1_5, duration_seconds, 
                                        lowqualitytag_perc, universaldisagreement_perc, asc_score_raw)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row['Participant ID'], 
                  row.get('PRI_Score'), 
                  row.get('PRI_Scale_1_5'),
                  row.get('Duration_seconds'),
                  row.get('LowQualityTag_Perc'),
                  row.get('UniversalDisagreement_Perc'),
                  row.get('ASC_Score_Raw')))
    else:
        print(f"PRI scores not found at {pri_file}, skipping...")
    
    # Load and add divergence scores if available
    divergence_file = output_dir / DIVERGENCE_FILE
    if divergence_file.exists():
        print(f"Loading divergence scores from {divergence_file}")
        df_divergence = pd.read_csv(divergence_file)
        
        # Check actual column names in divergence file
        print(f"  Divergence columns: {df_divergence.columns.tolist()}")
        
        # Update responses with divergence scores
        for _, row in df_divergence.iterrows():
            cursor.execute("""
                UPDATE responses 
                SET divergence_score = ?
                WHERE "Question ID" = ? AND "Response" = ?
            """, (row.get('Divergence Score'), row['Question ID'], row['Response Text']))
    else:
        print(f"Divergence scores not found at {divergence_file}, skipping...")
    
    # Load and add consensus scores if available
    consensus_file = output_dir / CONSENSUS_FILE
    if consensus_file.exists():
        print(f"Loading consensus scores from {consensus_file}")
        df_consensus = pd.read_csv(consensus_file)
        
        # Check actual column names in consensus file
        print(f"  Consensus columns: {df_consensus.columns.tolist()}")
        
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
                row['Question ID'],
                row['Response Text'],
                row.get('Num Valid Segments'),
                row.get('MinAgree_100pct'),
                row.get('MinAgree_95pct'),
                row.get('MinAgree_90pct'),
                row.get('MinAgree_80pct'),
                row.get('MinAgree_70pct'),
                row.get('MinAgree_60pct'),
                row.get('MinAgree_50pct'),
                row.get('MinAgree_40pct'),
                row.get('MinAgree_30pct'),
                row.get('MinAgree_20pct'),
                row.get('MinAgree_10pct')
            ))
            
            # Also update the responses table with the 50% consensus score as default
            cursor.execute("""
                UPDATE responses 
                SET consensus_minagree_50pct = ?
                WHERE "Question ID" = ? AND "Response" = ?
            """, (row.get('MinAgree_50pct'), row['Question ID'], row['Response Text']))
    else:
        print(f"Consensus scores not found at {consensus_file}, skipping...")
    
    # Load and add tags if available
    tags_file = data_dir / "tags/all_thought_labels.csv"
    if tags_file.exists():
        print(f"Loading tags from {tags_file}")
        df_tags = pd.read_csv(tags_file)
        
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
        
        # Process tags (assuming format: Question_ID, Participant_ID, Tag1, Tag2, ...)
        tag_columns = [col for col in df_tags.columns if col not in ['Question_ID', 'Participant_ID']]
        
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
                WHERE "Question ID" = ? AND "Participant ID" = ?
            """, (row.get('Question_ID', row.get('Question ID')), row.get('Participant_ID', row.get('Participant ID'))))
            
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
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_language ON responses("Language")')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_response_tags_response ON response_tags(response_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_response_tags_tag ON response_tags(tag_id)")
    
    # Create useful views
    print("Creating views...")
    
    # View combining responses with PRI scores
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS responses_with_pri AS
        SELECT r.*, p.pri_score, p.pri_scale_1_5
        FROM responses r
        LEFT JOIN participants p ON r."Participant ID" = p.participant_id
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
    
    cursor.execute('SELECT COUNT(DISTINCT "Participant ID") FROM responses')
    participant_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT "Question ID") FROM responses')
    question_count = cursor.fetchone()[0]
    
    print(f"\nDatabase created successfully!")
    print(f"  Responses: {response_count}")
    print(f"  Participants: {participant_count}")
    print(f"  Questions: {question_count}")
    
    # Check what additional tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"  Tables created: {', '.join([t[0] for t in tables])}")
    
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