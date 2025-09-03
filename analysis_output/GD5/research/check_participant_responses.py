#!/usr/bin/env python3
"""
Check which questions have responses from reliable participants
"""

import sqlite3
import pandas as pd

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

# Get reliable participants
participants_query = """
SELECT participant_id
FROM participants
WHERE pri_score >= 0.3
"""
df_participants = pd.read_sql_query(participants_query, conn)
reliable_participants = df_participants['participant_id'].tolist()
print(f"Total reliable participants: {len(reliable_participants)}")

# Check what questions these participants answered
sample_participant = reliable_participants[0] if reliable_participants else None
if sample_participant:
    query = f"""
    SELECT DISTINCT question, COUNT(*) as response_count
    FROM responses
    WHERE participant_id = '{sample_participant}'
    GROUP BY question
    ORDER BY question
    """
    questions = pd.read_sql_query(query, conn)
    print(f"\nQuestions answered by first participant ({sample_participant}):")
    for idx, row in questions.iterrows():
        print(f"{idx+1}. {row['question'][:100]}... (count: {row['response_count']})")

# Check specifically for Section 5 related questions in responses
print("\n" + "=" * 80)
print("Checking for Section 5 questions with reliable participant responses:")

section_5_keywords = [
    'approach',
    'protecting animals',
    'representative',
    'decision-making',
    'democratic',
    'restricted',
    'recording',
    'elephant',
    'whale',
    'earn money',
    'non-humans'
]

for keyword in section_5_keywords:
    query = f"""
    SELECT DISTINCT question, COUNT(DISTINCT participant_id) as participant_count
    FROM responses
    WHERE question LIKE '%{keyword}%'
    AND participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
    GROUP BY question
    """
    result = pd.read_sql_query(query, conn)
    if not result.empty:
        print(f"\nKeyword '{keyword}':")
        for idx, row in result.iterrows():
            print(f"  - {row['question'][:80]}... ({row['participant_count']} participants)")

conn.close()