#!/usr/bin/env python3
"""
Section 6: Cross-Demographic and Cultural Insights Analysis
Analyzing GD5 survey data for cross-demographic patterns
"""
import sqlite3
import pandas as pd
from datetime import datetime

# Connect to the database in read-only mode
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get the table structure first
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Available tables:", tables)

# Check participants table structure
cursor.execute("PRAGMA table_info(participants)")
columns = cursor.fetchall()
print("\nColumns in participants:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Check participant_responses table
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()
print("\nColumns in participant_responses:")
for col in columns[:30]:
    print(f"  {col[1]}: {col[2]}")

# Get sample data to understand structure
cursor.execute("SELECT COUNT(*) FROM participants")
print(f"\nTotal participants: {cursor.fetchone()[0]}")

# Check Q7 (region/country) and Q70 (animal protection) column names
cursor.execute("SELECT * FROM participant_responses_column_mappings WHERE question_id IN ('Q7', 'Q70', 'Q32', 'Q6', 'Q4', 'Q61', 'Q90', 'Q91') ORDER BY question_id")
mappings = cursor.fetchall()
print("\nColumn mappings for key questions:")
for m in mappings:
    print(f"  Q{m[1]}: column '{m[2]}'")