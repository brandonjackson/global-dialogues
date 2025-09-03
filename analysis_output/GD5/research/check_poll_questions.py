#!/usr/bin/env python3
"""
Check poll vs open-ended questions
"""

import sqlite3
import pandas as pd

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

# Check question types
query = """
SELECT question_type, COUNT(DISTINCT question) as unique_questions, COUNT(*) as total_responses
FROM responses
GROUP BY question_type
"""
result = pd.read_sql_query(query, conn)
print("Question Types in Database:")
print(result)

# Get poll questions
print("\n" + "=" * 80)
print("Poll Questions:")
poll_query = """
SELECT DISTINCT question, COUNT(DISTINCT participant_id) as participants
FROM responses
WHERE question_type = 'poll'
GROUP BY question
ORDER BY question
"""
polls = pd.read_sql_query(poll_query, conn)
for idx, row in polls.iterrows():
    print(f"\n{idx+1}. {row['question'][:100]}...")
    print(f"   Participants: {row['participants']}")

# Check for Section 5 related poll questions
print("\n" + "=" * 80)
print("Section 5 Related Poll Questions:")
section_5_poll_query = """
SELECT DISTINCT question, COUNT(DISTINCT participant_id) as participants,
       COUNT(DISTINCT response) as unique_responses
FROM responses
WHERE question_type = 'poll'
AND (question LIKE '%approach%' 
     OR question LIKE '%representative%'
     OR question LIKE '%decision-making%'
     OR question LIKE '%democratic%'
     OR question LIKE '%recording%'
     OR question LIKE '%earn%'
     OR question LIKE '%own%')
GROUP BY question
"""
section_5_polls = pd.read_sql_query(section_5_poll_query, conn)
for idx, row in section_5_polls.iterrows():
    print(f"\n{row['question'][:100]}...")
    print(f"   Participants: {row['participants']}, Unique responses: {row['unique_responses']}")

# Check participant_responses table
print("\n" + "=" * 80)
print("Checking participant_responses table:")
pr_query = """
SELECT * FROM participant_responses LIMIT 5
"""
try:
    pr_data = pd.read_sql_query(pr_query, conn)
    print(f"participant_responses columns: {pr_data.columns.tolist()}")
    print(f"Sample data shape: {pr_data.shape}")
except Exception as e:
    print(f"Error accessing participant_responses: {e}")

conn.close()