#!/usr/bin/env python3
"""
Section 6.2: Religious Perspectives on Human Superiority
"""
import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# First find Q32 column
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()
all_cols = [col[1] for col in columns]

# Look for Q32 
print("Searching for Q32 (human superiority question)...")
q32_cols = [c for c in all_cols if 'Q32' in c or 'superior' in c.lower() or 'inferior' in c.lower()]
print("Q32-related columns:", q32_cols)

# Check columns around Q32 position
for i, col in enumerate(columns):
    if col[1] == 'Q32':
        print(f"\nColumns around Q32:")
        for j in range(max(0, i-2), min(len(columns), i+3)):
            print(f"  {columns[j][1]}")
        break

# Get sample Q32 values
cursor.execute("SELECT DISTINCT Q32 FROM participant_responses WHERE Q32 IS NOT NULL LIMIT 10")
q32_values = cursor.fetchall()
print("\nSample Q32 values:")
for val in q32_values:
    print(f"  {val[0]}")

# Now analyze by religion
query = """
SELECT 
    Q6 as religion,
    Q32 as human_animal_relationship,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY Q6), 2) as pct_within_religion
FROM participant_responses
WHERE Q6 IS NOT NULL AND Q32 IS NOT NULL AND Q32 != '--'
GROUP BY Q6, Q32
ORDER BY Q6, count DESC
"""

df = pd.read_sql_query(query, conn)

# Get major religions
major_religions = df.groupby('religion')['count'].sum().nlargest(8).index.tolist()
df_major = df[df['religion'].isin(major_religions)]

print("\n=== HUMAN-ANIMAL RELATIONSHIP VIEWS BY RELIGION ===")
pivot = df_major.pivot(index='religion', columns='human_animal_relationship', values='pct_within_religion').fillna(0)
print(pivot)

# Statistical test
from scipy.stats import chi2_contingency

contingency_query = """
SELECT Q6, Q32, COUNT(*) as count
FROM participant_responses
WHERE Q6 IN %s
    AND Q32 IS NOT NULL AND Q32 != '--'
GROUP BY Q6, Q32
""" % str(tuple(major_religions))

cont_df = pd.read_sql_query(contingency_query, conn)
cont_table = cont_df.pivot(index='Q6', columns='Q32', values='count').fillna(0)

chi2, p_value, dof, expected = chi2_contingency(cont_table)
print(f"\n=== STATISTICAL TEST ===")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"P-value: {p_value:.6f}")
print(f"Significant religious differences: {'YES' if p_value < 0.05 else 'NO'}")

# Find most common view per religion
print("\n=== DOMINANT VIEW BY RELIGION ===")
for religion in pivot.index:
    if pivot.columns.size > 0:
        max_view = pivot.loc[religion].idxmax()
        max_val = pivot.loc[religion].max()
        print(f"{religion:30} -> {max_view} ({max_val:.1f}%)")

# Overall distribution
overall_query = """
SELECT 
    Q32 as view,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q32 IS NOT NULL AND Q32 != '--'), 2) as percentage
FROM participant_responses
WHERE Q32 IS NOT NULL AND Q32 != '--'
GROUP BY Q32
ORDER BY count DESC
"""
overall = pd.read_sql_query(overall_query, conn)
print("\n=== OVERALL DISTRIBUTION ===")
print(overall)

conn.close()