#!/usr/bin/env python3
"""
Analysis for Section 5: Ethics, Rights, and Governance
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# Connect to database in read-only mode
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("Connected to GD5 database")
print("=" * 80)

# First, let's get the question mapping
question_mapping_query = """
SELECT DISTINCT question_id, question 
FROM responses 
WHERE question LIKE '%future%' 
   OR question LIKE '%legal%'
   OR question LIKE '%represent%'
   OR question LIKE '%democra%'
   OR question LIKE '%animal%'
   OR question LIKE '%regulat%'
   OR question LIKE '%restrict%'
   OR question LIKE '%own%'
   OR question LIKE '%money%'
   OR question LIKE '%property%'
   OR question LIKE '%earn%'
ORDER BY question;
"""

df_questions = pd.read_sql_query(question_mapping_query, conn)
print("Relevant questions found:")
for idx, row in df_questions.iterrows():
    print(f"\nQ{idx+1}: {row['question'][:100]}...")
    print(f"ID: {row['question_id']}")

print("\n" + "=" * 80)
print("Starting Section 5 Analysis")
print("=" * 80)

# Get participant data with PRI scores
participants_query = """
SELECT participant_id, pri_score
FROM participants
WHERE pri_score >= 0.3
"""
df_participants = pd.read_sql_query(participants_query, conn)
print(f"\nTotal reliable participants (PRI >= 0.3): {len(df_participants)}")

conn.close()