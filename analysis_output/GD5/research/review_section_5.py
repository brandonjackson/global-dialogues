#!/usr/bin/env python3
"""
Review Section 5: Ethics, Rights, and Governance
Verifying the analysis claims and calculations
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== REVIEWING SECTION 5 ANALYSIS ===\n")

# === Question 5.1: Q70 Preferred Future ===
print("=== Q5.1: PREFERRED FUTURE FOR ANIMAL PROTECTION ===")

q70_query = """
SELECT Q70, COUNT(*) as count, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q70 IS NOT NULL AND Q70 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q70 IS NOT NULL AND Q70 != '--'
GROUP BY Q70
ORDER BY count DESC
"""
q70_results = pd.read_sql_query(q70_query, conn)
print("Q70 Distribution:")
print(q70_results)

# Check the correlation with Q94 (superiority/equality beliefs)
q70_q94_query = """
SELECT Q94, Q70, COUNT(*) as count
FROM participant_responses
WHERE Q70 IS NOT NULL AND Q70 != '--' AND Q94 IS NOT NULL AND Q94 != '--'
GROUP BY Q94, Q70
"""
q70_q94 = pd.read_sql_query(q70_q94_query, conn)

# Create crosstab for statistical test
if len(q70_q94) > 0:
    pivot = q70_q94.pivot(index='Q94', columns='Q70', values='count').fillna(0)
    chi2, p_value, dof, expected = chi2_contingency(pivot)
    print(f"\nQ70 x Q94 correlation:")
    print(f"Chi-square: {chi2:.4f}, p-value: {p_value:.6f}")
    
    # Calculate percentages within each belief group
    percentages = pivot.div(pivot.sum(axis=1), axis=0) * 100
    print("\nPercentages by belief:")
    print(percentages.round(1))

# === Question 5.2: Q73 Animal Representation ===
print("\n\n=== Q5.2: ANIMAL REPRESENTATION (Q73) ===")

q73_query = """
SELECT Q73, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q73 IS NOT NULL AND Q73 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q73 IS NOT NULL AND Q73 != '--'
GROUP BY Q73
ORDER BY count DESC
"""
q73_results = pd.read_sql_query(q73_query, conn)
print("Q73 Distribution:")
print(q73_results)

# === Question 5.4: Q77 Democratic Participation ===  
print("\n\n=== Q5.4: DEMOCRATIC PARTICIPATION (Q77) ===")

q77_query = """
SELECT Q77, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q77 IS NOT NULL AND Q77 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q77 IS NOT NULL AND Q77 != '--'
GROUP BY Q77
ORDER BY count DESC
"""
q77_results = pd.read_sql_query(q77_query, conn)
print("Q77 Distribution:")
print(q77_results)

# Check correlation with Q41 (animal culture)
q77_q41_query = """
SELECT Q41, Q77, COUNT(*) as count
FROM participant_responses
WHERE Q77 IS NOT NULL AND Q77 != '--' AND Q41 IS NOT NULL AND Q41 != '--'
GROUP BY Q41, Q77
"""
q77_q41 = pd.read_sql_query(q77_q41_query, conn)
if len(q77_q41) > 0:
    pivot_41 = q77_q41.pivot(index='Q41', columns='Q77', values='count').fillna(0)
    chi2_41, p_value_41, dof_41, expected_41 = chi2_contingency(pivot_41)
    print(f"\nQ77 x Q41 correlation:")
    print(f"Chi-square: {chi2_41:.4f}, p-value: {p_value_41:.6f}")

# === Question 5.5: Regulation Questions ===
print("\n\n=== Q5.5: REGULATION (Q82, Q83, Q85) ===")

# Q82 and Q83
for q, label in [('Q82', 'Restrict to professionals'), ('Q83', 'Everyone can listen')]:
    query = f"""
    SELECT {q}, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE {q} IS NOT NULL AND {q} != '--'), 2) as percentage
    FROM participant_responses 
    WHERE {q} IS NOT NULL AND {q} != '--'
    GROUP BY {q}
    ORDER BY count DESC
    """
    results = pd.read_sql_query(query, conn)
    print(f"\n{label} ({q}):")
    print(results)
    
    # Calculate agreement percentage
    agree_pct = results[results[q].str.contains('agree', case=False, na=False)]['percentage'].sum()
    print(f"Total agreement: {agree_pct:.1f}%")

# === Question 5.7: Age and Economic Rights ===
print("\n\n=== Q5.7: AGE AND ECONOMIC RIGHTS (Q91) ===")

# Check age groups and Q91
q91_age_query = """
SELECT Q2 as age, Q91, COUNT(*) as count
FROM participant_responses
WHERE Q2 IS NOT NULL AND Q91 IS NOT NULL AND Q91 != '--'
GROUP BY Q2, Q91
"""
q91_age = pd.read_sql_query(q91_age_query, conn)

# Focus on 18-25 vs 56+ comparison as claimed
young_support = q91_age[q91_age['age'] == '18-25']
old_support = q91_age[q91_age['age'] == '56-65'] # Assuming this is the 56+ group

if len(young_support) > 0 and len(old_support) > 0:
    print("\nAge group Q91 responses:")
    print("18-25 group:")
    print(young_support[['Q91', 'count']].head())
    print("\n56-65 group:")  
    print(old_support[['Q91', 'count']].head())

conn.close()

print("\n=== REVIEW SUMMARY ===")
print("Key numbers to verify against the analysis:")
print("- Q70 percentages")
print("- Q70 x Q94 correlation p-value") 
print("- Q73 percentages")
print("- Q77 percentages and Q41 correlation")
print("- Q82/Q83 agreement rates")
print("- Q91 age differences")