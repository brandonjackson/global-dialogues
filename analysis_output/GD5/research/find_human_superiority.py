#!/usr/bin/env python3
import sqlite3
import pandas as pd

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get all columns from participant_responses
query = "PRAGMA table_info(participant_responses)"
df_cols = pd.read_sql_query(query, conn)

# Get first row to see actual values
sample_query = "SELECT * FROM participant_responses LIMIT 1"
sample = pd.read_sql_query(sample_query, conn)

# Look for human superiority question by checking values
for col in df_cols['name']:
    try:
        val = sample[col].iloc[0]
        if val and isinstance(val, str):
            if any(word in val.lower() for word in ['superior', 'inferior', 'equal', 'fundamentally']):
                print(f"Found potential Q32 in column '{col}': {val}")
    except:
        pass

# Check between Q27 and Q35 range more carefully
print("\nChecking specific columns for superiority question:")
test_cols = ['Q94', 'unmapped_10', 'unmapped_11'] + [f'unmapped_{i}' for i in range(28, 36)]

for col in test_cols:
    if col in df_cols['name'].values:
        try:
            query = f"SELECT DISTINCT {col} FROM participant_responses WHERE {col} IS NOT NULL AND {col} != '' LIMIT 5"
            result = pd.read_sql_query(query, conn)
            if not result.empty:
                values = result[col].unique()
                # Check if these look like the superiority options
                if any('superior' in str(v).lower() or 'equal' in str(v).lower() for v in values):
                    print(f"\n{col} contains:")
                    for v in values[:3]:
                        print(f"  {v}")
        except Exception as e:
            pass

conn.close()