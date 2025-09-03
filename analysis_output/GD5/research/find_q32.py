#!/usr/bin/env python3
import sqlite3
import pandas as pd

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)
cursor = conn.cursor()

# Get all columns
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()

# Look for columns between Q31 and Q33
print("Columns between Q30 and Q35:")
for col in columns:
    col_name = col[1]
    if any(x in col_name for x in ['Q30', 'Q31', 'Q32', 'Q33', 'Q34', 'Q35']):
        print(f"  {col_name}")

# Check column mappings
cursor.execute("""
    SELECT * FROM participant_responses_column_mappings 
    WHERE question_id BETWEEN 'Q30' AND 'Q35'
    ORDER BY question_id
""")
mappings = cursor.fetchall()
print("\nColumn mappings Q30-Q35:")
for m in mappings:
    print(f"  {m[1]}: {m[2]}")

# Search for keywords related to superiority/equality
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()
all_cols = [col[1] for col in columns]

print("\nColumns with 'superior', 'equal', 'inferior' keywords:")
for c in all_cols:
    if any(word in c.lower() for word in ['superior', 'equal', 'inferior', 'nature', 'relation']):
        print(f"  {c}")

conn.close()