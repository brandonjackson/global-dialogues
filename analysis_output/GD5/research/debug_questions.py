#!/usr/bin/env python3
"""
Debug - Find actual questions in database
"""

import sqlite3
import pandas as pd

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

# Get all unique questions
query = """
SELECT DISTINCT question, COUNT(*) as count
FROM responses
GROUP BY question
ORDER BY question
"""
df = pd.read_sql_query(query, conn)

print(f"Total unique questions: {len(df)}")
print("\n" + "=" * 80)

# Filter for Section 5 related keywords
keywords = [
    'approach', 'appropriate', 'protecting',
    'representative', 'lawyer', 'rights',
    'decision-making', 'democratic',
    'restricted', 'authorized', 'professional',
    'recording', 'own', 'whale',
    'earn money', 'non-humans', 'future'
]

print("Questions containing Section 5 keywords:")
print("=" * 80)

for idx, row in df.iterrows():
    question = row['question']
    if any(keyword.lower() in question.lower() for keyword in keywords):
        print(f"\nQ{idx}: {question[:200]}")
        print(f"Count: {row['count']}")

# Also check for questions by number pattern
print("\n" + "=" * 80)
print("Questions numbered 70-91:")
print("=" * 80)

for i in range(70, 92):
    pattern = f"{i}."
    matching = df[df['question'].str.startswith(pattern)]
    if not matching.empty:
        for idx, row in matching.iterrows():
            print(f"\n{row['question'][:200]}")
            print(f"Count: {row['count']}")

conn.close()