#!/usr/bin/env python3
"""
Check for belief-related questions in the database
"""

import sqlite3
import pandas as pd

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

# Get all columns from participant_responses
query = """
SELECT * FROM participant_responses LIMIT 1
"""
df = pd.read_sql_query(query, conn)

print("Checking columns that might contain human-nature relationship questions:")
print("=" * 80)

# Look for columns that might contain the initial and final belief questions
for col in df.columns:
    if col.startswith('Q'):
        # Get a sample value
        sample_query = f"""
        SELECT {col}, COUNT(*) as count
        FROM participant_responses
        WHERE {col} IS NOT NULL
        GROUP BY {col}
        LIMIT 3
        """
        try:
            sample = pd.read_sql_query(sample_query, conn)
            if len(sample) > 0:
                # Check if it looks like a belief question
                first_val = str(sample.iloc[0][col])
                if any(keyword in first_val.lower() for keyword in ['human', 'animal', 'nature', 'superior', 'equal', 'different']):
                    print(f"\n{col}:")
                    for idx, row in sample.iterrows():
                        print(f"  - {row[col][:100]}")
        except:
            pass

# Also check the responses table for belief questions
print("\n" + "=" * 80)
print("Checking responses table for belief questions:")
print("=" * 80)

responses_query = """
SELECT DISTINCT question
FROM responses
WHERE question LIKE '%human%' 
   OR question LIKE '%superior%' 
   OR question LIKE '%equal%'
   OR question LIKE '%nature%'
ORDER BY question
"""
responses = pd.read_sql_query(responses_query, conn)
for idx, row in responses.iterrows():
    print(f"\n{idx+1}. {row['question'][:150]}")

conn.close()