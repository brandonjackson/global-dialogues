#!/usr/bin/env python3
"""
Check what columns exist for worldview questions
"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get all columns
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()

# Look for Q93, Q94 and any columns around Q31-32 range
print("Searching for worldview columns...")
for col in columns:
    col_name = col[1]
    if any(x in col_name for x in ['Q93', 'Q94', 'Q31', 'Q32', 'nature', 'superior', 'equal', 'separate']):
        print(f"  {col_name}")

# Check what Q93 and Q94 contain
print("\nQ93 values:")
cursor.execute("SELECT DISTINCT Q93 FROM participant_responses LIMIT 5")
for val in cursor.fetchall():
    print(f"  {val[0]}")

print("\nQ94 values:")
cursor.execute("SELECT DISTINCT Q94 FROM participant_responses LIMIT 5")
for val in cursor.fetchall():
    print(f"  {val[0]}")

# Look for the initial questions - they might be in unmapped columns
print("\nUnmapped columns that might be initial worldview:")
for col in columns:
    col_name = col[1]
    if 'unmapped' in col_name:
        # Sample the content
        try:
            cursor.execute(f"SELECT DISTINCT {col_name} FROM participant_responses WHERE {col_name} IS NOT NULL LIMIT 3")
            vals = cursor.fetchall()
            if vals:
                for val in vals:
                    if val[0] and any(word in str(val[0]).lower() for word in ['superior', 'equal', 'nature', 'separate']):
                        print(f"\n{col_name} contains worldview data:")
                        for v in vals:
                            print(f"  {v[0]}")
                        break
        except:
            pass

conn.close()