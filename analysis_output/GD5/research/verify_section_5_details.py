#!/usr/bin/env python3
"""
Detailed verification of Section 5 claims
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== DETAILED SECTION 5 VERIFICATION ===\n")

# === Check Q82 and Q83 agreement rates more carefully ===
print("=== Q82/Q83 AGREEMENT VERIFICATION ===")

# Q82: Restrict to professionals
q82_query = """
SELECT Q82, COUNT(*) as count
FROM participant_responses 
WHERE Q82 IS NOT NULL AND Q82 != '--'
GROUP BY Q82
"""
q82_df = pd.read_sql_query(q82_query, conn)
total_q82 = q82_df['count'].sum()
agree_q82 = q82_df[q82_df['Q82'].str.contains('agree', case=False, na=False)]['count'].sum()
q82_pct = agree_q82 / total_q82 * 100
print(f"Q82 - Restrict to professionals: {agree_q82}/{total_q82} = {q82_pct:.1f}% agree")
print("Analysis claimed: 76.3% agree")
print(f"Verification: {q82_pct:.1f}% agree")

# Q83: Everyone can listen  
q83_query = """
SELECT Q83, COUNT(*) as count
FROM participant_responses 
WHERE Q83 IS NOT NULL AND Q83 != '--'
GROUP BY Q83
"""
q83_df = pd.read_sql_query(q83_query, conn)
total_q83 = q83_df['count'].sum()
agree_q83 = q83_df[q83_df['Q83'].str.contains('agree', case=False, na=False)]['count'].sum()
q83_pct = agree_q83 / total_q83 * 100
print(f"Q83 - Everyone can listen: {agree_q83}/{total_q83} = {q83_pct:.1f}% agree")
print("Analysis claimed: 62.1% agree")
print(f"Verification: {q83_pct:.1f}% agree")

# === Check Q90 (ownership) ===
print("\n=== Q90 OWNERSHIP VERIFICATION ===")
q90_query = """
SELECT Q90, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q90 IS NOT NULL AND Q90 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q90 IS NOT NULL AND Q90 != '--'
GROUP BY Q90
ORDER BY count DESC
"""
q90_results = pd.read_sql_query(q90_query, conn)
print("Q90 Distribution:")
print(q90_results)

# === Check the Q70 percentages precisely ===
print("\n=== Q70 PRECISE VERIFICATION ===")
q70_query = """
SELECT Q70, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q70 IS NOT NULL AND Q70 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q70 IS NOT NULL AND Q70 != '--'
GROUP BY Q70
ORDER BY count DESC
"""
q70_results = pd.read_sql_query(q70_query, conn)
print("Q70 Distribution:")
for _, row in q70_results.iterrows():
    option = row['Q70']
    if 'Building ongoing relationships' in option:
        print(f"Future A (Relationships): {row['count']} ({row['percentage']}%)")
        print(f"Analysis claimed: 63.2%")
    elif 'Including all voices' in option:
        print(f"Future B (Decision-Making): {row['count']} ({row['percentage']}%)")
        print(f"Analysis claimed: 25.1%")
    elif 'Granting legal rights' in option:
        print(f"Future C (Legal Rights): {row['count']} ({row['percentage']}%)")
        print(f"Analysis claimed: 11.7%")

# === Check Q70 x Q94 correlation p-value ===
print("\n=== Q70 x Q94 CORRELATION VERIFICATION ===")
q70_q94_query = """
SELECT Q94, Q70, COUNT(*) as count
FROM participant_responses
WHERE Q70 IS NOT NULL AND Q70 != '--' AND Q94 IS NOT NULL AND Q94 != '--'
GROUP BY Q94, Q70
"""
q70_q94 = pd.read_sql_query(q70_q94_query, conn)
pivot = q70_q94.pivot(index='Q94', columns='Q70', values='count').fillna(0)
chi2, p_value, dof, expected = chi2_contingency(pivot)
print(f"Chi-square: {chi2:.4f}, p-value: {p_value:.6f}")
print(f"Analysis claimed: p=0.0145")
print(f"Verification: p={p_value:.6f}")

# Check the specific claim about superiority vs equality believers
percentages = pivot.div(pivot.sum(axis=1), axis=0) * 100
print("\nPercentages by belief group:")
print(percentages.round(1))

conn.close()