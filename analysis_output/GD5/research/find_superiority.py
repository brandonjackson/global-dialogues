#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)
cursor = conn.cursor()

# Check unmapped columns (often contain the actual questions)
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()

print("Unmapped columns:")
for col in columns:
    if 'unmapped' in col[1]:
        print(f"  {col[1]}")

# Check a few unmapped columns for content
for i in range(28, 34):
    col_name = f'unmapped_{i}'
    try:
        cursor.execute(f"SELECT DISTINCT {col_name} FROM participant_responses WHERE {col_name} IS NOT NULL LIMIT 5")
        values = cursor.fetchall()
        if values and any('superior' in str(v[0]).lower() or 'equal' in str(v[0]).lower() or 'inferior' in str(v[0]).lower() for v in values if v[0]):
            print(f"\n{col_name} might be Q32:")
            for v in values:
                print(f"  {v[0]}")
    except:
        pass

# Check columns after Q27
print("\nColumns after Q27:")
for col in columns[50:80]:  # Check columns in this range
    print(f"  {col[0]}: {col[1]}")

conn.close()