#!/usr/bin/env python3
"""
Section 6.2: Religious Perspectives on Human Superiority
Analyzing Q94 (human superiority) by Q6 (religion)
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Analyze human superiority views (Q94) by religion (Q6)
query = """
SELECT 
    Q6 as religion,
    Q94 as human_animal_relationship,
    COUNT(*) as count
FROM participant_responses
WHERE Q6 IS NOT NULL AND Q6 != '--' AND Q6 != ''
    AND Q94 IS NOT NULL AND Q94 != '--' AND Q94 != ''
GROUP BY Q6, Q94
"""

df = pd.read_sql_query(query, conn)

# Get major religions (top 8 by response count)
religion_counts = df.groupby('religion')['count'].sum().sort_values(ascending=False)
major_religions = religion_counts.head(8).index.tolist()

print("=== MAJOR RELIGIOUS GROUPS (by response count) ===")
for rel in major_religions:
    print(f"  {rel}: {religion_counts[rel]} responses")

# Calculate percentages within each religion
df['pct_within_religion'] = df.groupby('religion')['count'].transform(lambda x: (x / x.sum() * 100).round(2))

# Filter to major religions and create pivot table
df_major = df[df['religion'].isin(major_religions)]
pivot = df_major.pivot(index='religion', columns='human_animal_relationship', values='pct_within_religion').fillna(0)

print("\n=== HUMAN-ANIMAL RELATIONSHIP VIEWS BY RELIGION (%) ===")
print(pivot.round(1))

# Statistical test for all religions
contingency_table = df.pivot(index='religion', columns='human_animal_relationship', values='count').fillna(0)
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print(f"\n=== STATISTICAL TEST (All Religions) ===")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"P-value: {p_value:.6f}")
print(f"Degrees of freedom: {dof}")
print(f"Significant religious differences: {'YES (p < 0.05)' if p_value < 0.05 else 'NO'}")

# Find dominant view per religion
print("\n=== DOMINANT VIEW BY MAJOR RELIGION ===")
for religion in pivot.index:
    if pivot.loc[religion].sum() > 0:  # Ensure there's data
        max_view = pivot.loc[religion].idxmax()
        max_val = pivot.loc[religion].max()
        # Simplify the view names for readability
        view_short = max_view.replace('Humans are fundamentally ', '').replace(' to other animals', '')
        print(f"{religion:30} -> {view_short:10} ({max_val:.1f}%)")

# Overall distribution
overall_query = """
SELECT 
    Q94 as view,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q94 IS NOT NULL AND Q94 != '--'), 2) as percentage
FROM participant_responses
WHERE Q94 IS NOT NULL AND Q94 != '--' AND Q94 != ''
GROUP BY Q94
ORDER BY percentage DESC
"""
overall = pd.read_sql_query(overall_query, conn)

print("\n=== OVERALL DISTRIBUTION (All Respondents) ===")
for _, row in overall.iterrows():
    view_short = row['view'].replace('Humans are fundamentally ', '').replace(' to other animals', '')
    print(f"  {view_short:10} : {row['count']:4} ({row['percentage']:.1f}%)")

# Specific interesting comparisons
print("\n=== NOTABLE PATTERNS ===")
if 'Humans are fundamentally equal to other animals' in pivot.columns:
    equal_col = 'Humans are fundamentally equal to other animals'
    religions_equal = pivot[equal_col].sort_values(ascending=False)
    print(f"Religions most likely to view humans as EQUAL to animals:")
    for rel in religions_equal.head(3).index:
        print(f"  {rel}: {religions_equal[rel]:.1f}%")

conn.close()