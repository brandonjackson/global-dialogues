#!/usr/bin/env python3
"""
Section 6.1: Regional Views on Animal Rights
Analyzing differences in preferred future for animal protection across regions
"""
import sqlite3
import pandas as pd
from datetime import datetime

# Connect to the database in read-only mode
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# First check what columns exist for Q70 and Q32
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()
q70_cols = [col[1] for col in columns if 'Q70' in col[1] or 'protect' in col[1].lower() or 'animal' in col[1].lower()]
q32_cols = [col[1] for col in columns if 'Q32' in col[1] or 'superior' in col[1].lower() or 'equal' in col[1].lower()]

print("Q70-related columns:", q70_cols)
print("\nQ32-related columns:", q32_cols)

# Check all columns with question marks
all_cols = [col[1] for col in columns]
question_cols = [c for c in all_cols if '?' in c]
print("\nColumns with questions (first 10):")
for col in question_cols[:10]:
    print(f"  {col}")

# Look for Q70 by searching for key words
cursor.execute("""
    SELECT column_name 
    FROM participant_responses_column_mappings 
    WHERE column_name LIKE '%protect%' OR column_name LIKE '%animal%' OR question_id LIKE '%70%'
""")
results = cursor.fetchall()
print("\nQ70 search results:")
for r in results:
    print(f"  {r[0]}")

# Get sample responses to understand the data
cursor.execute("""
    SELECT Q7, COUNT(*) as count
    FROM participant_responses
    WHERE Q7 IS NOT NULL
    GROUP BY Q7
    ORDER BY count DESC
    LIMIT 10
""")
regions = cursor.fetchall()
print("\nTop 10 regions by response count:")
for r in regions:
    print(f"  {r[0]}: {r[1]} responses")