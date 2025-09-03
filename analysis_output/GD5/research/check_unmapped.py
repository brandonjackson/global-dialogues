#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)
cursor = conn.cursor()

# Check early unmapped columns which might contain Q32
unmapped_cols = ['unmapped_31', 'unmapped_32', 'Q31', 'Q30', 'Q29', 'Q28']

for col in unmapped_cols:
    try:
        cursor.execute(f"SELECT DISTINCT {col} FROM participant_responses WHERE {col} IS NOT NULL LIMIT 3")
        values = cursor.fetchall()
        if values:
            print(f"\n{col}:")
            for v in values:
                print(f"  {v[0][:100] if len(str(v[0])) > 100 else v[0]}")
    except:
        pass

# Let me check the columns that come after Q27
cursor.execute("""
    SELECT DISTINCT Q28 FROM participant_responses 
    WHERE Q28 IS NOT NULL 
    LIMIT 5
""")
q28_vals = cursor.fetchall()
print("\nQ28 values:")
for v in q28_vals:
    print(f"  {v[0]}")

# Check Q29, Q30, Q31
for q in ['Q29', 'Q30', 'Q31']:
    try:
        cursor.execute(f"SELECT DISTINCT {q} FROM participant_responses WHERE {q} IS NOT NULL LIMIT 3")
        values = cursor.fetchall()
        print(f"\n{q} values:")
        for v in values:
            print(f"  {v[0]}")
    except:
        print(f"\n{q}: column not found")

conn.close()