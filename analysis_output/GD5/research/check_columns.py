#!/usr/bin/env python3
"""
Check available columns in participant_responses table
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Get participant responses
query = "SELECT * FROM participant_responses LIMIT 1"
df = pd.read_sql_query(query, conn)

print("Columns in participant_responses table:")
for col in sorted(df.columns):
    print(f"  {col}")

# Check for Q32, Q41, Q55, Q57, Q77, Q83, Q84, Q91
print("\nChecking for needed questions:")
needed = ['Q32', 'Q41', 'Q55', 'Q57', 'Q77', 'Q83', 'Q84', 'Q91']
for q in needed:
    if q in df.columns:
        print(f"  {q}: FOUND")
    else:
        print(f"  {q}: NOT FOUND")

# Check unmapped columns
print("\nUnmapped columns:")
unmapped_cols = [col for col in df.columns if 'unmapped' in col]
for col in unmapped_cols:
    val = df[col].iloc[0] if len(df) > 0 else None
    print(f"  {col}: {val}")

conn.close()