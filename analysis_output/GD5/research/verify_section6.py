#!/usr/bin/env python3
"""
Section 6 Review: Verify all statistical claims
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== SECTION 6 REVIEW: VERIFYING STATISTICAL CLAIMS ===\n")

# Question 6.1: Animal protection preferences by country
print("6.1: Animal protection preferences by country/region")
print("=" * 50)

query_q70_q7 = """
SELECT 
    pr."What country or region do you most identify with?" as country,
    pr."Which approach feels most appropriate to you for protecting animals?" as approach,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr."What country or region do you most identify with?" IS NOT NULL 
    AND pr."Which approach feels most appropriate to you for protecting animals?" IS NOT NULL
    AND pr."What country or region do you most identify with?" != ''
    AND pr."Which approach feels most appropriate to you for protecting animals?" != ''
GROUP BY pr."What country or region do you most identify with?", 
         pr."Which approach feels most appropriate to you for protecting animals?"
ORDER BY country, approach
"""

df_q70_q7 = pd.read_sql_query(query_q70_q7, conn)
print("Raw data:")
print(df_q70_q7.head(20))

# Create contingency table
pivot_q70_q7 = df_q70_q7.pivot_table(index='country', columns='approach', values='count', fill_value=0)
print("\nContingency table:")
print(pivot_q70_q7)

# Chi-square test
chi2, p_val, dof, expected = chi2_contingency(pivot_q70_q7)
print(f"\nChi-square test results:")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"p-value: {p_val:.3f}")
print(f"Degrees of freedom: {dof}")

# Calculate percentages by country
pivot_pct = pivot_q70_q7.div(pivot_q70_q7.sum(axis=1), axis=0) * 100
print("\nPercentages by country:")
print(pivot_pct.round(1))

print("\n" + "="*70 + "\n")

# Question 6.2: Human-animal equality by religion
print("6.2: Human-animal equality by religion")
print("=" * 40)

query_q94_q6 = """
SELECT 
    pr."What religious group or faith do you most identify with?" as religion,
    pr.Q94 as human_animal_relation,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr."What religious group or faith do you most identify with?" IS NOT NULL 
    AND pr.Q94 IS NOT NULL
    AND pr."What religious group or faith do you most identify with?" != ''
    AND pr.Q94 != ''
GROUP BY pr."What religious group or faith do you most identify with?", pr.Q94
ORDER BY religion, human_animal_relation
"""

df_q94_q6 = pd.read_sql_query(query_q94_q6, conn)
print("Raw data:")
print(df_q94_q6.head(15))

# Create contingency table
pivot_q94_q6 = df_q94_q6.pivot_table(index='religion', columns='human_animal_relation', values='count', fill_value=0)
print("\nContingency table:")
print(pivot_q94_q6)

# Chi-square test
chi2, p_val, dof, expected = chi2_contingency(pivot_q94_q6)
print(f"\nChi-square test results:")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"p-value: {p_val:.6f}")
print(f"Degrees of freedom: {dof}")

# Calculate percentages by religion
pivot_pct_religion = pivot_q94_q6.div(pivot_q94_q6.sum(axis=1), axis=0) * 100
print("\nPercentages by religion:")
print(pivot_pct_religion.round(1))

print("\n" + "="*70 + "\n")

# Question 6.3: AI trust by location type
print("6.3: AI trust by location type")
print("=" * 35)

query_q61_q4 = """
SELECT 
    pr."What best describes where you live?" as location,
    pr."Would you trust AI more or less than humans to interpret animal communication to resolve a human-wildlife conflict? Why?" as ai_trust_response,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr."What best describes where you live?" IS NOT NULL 
    AND pr."Would you trust AI more or less than humans to interpret animal communication to resolve a human-wildlife conflict? Why?" IS NOT NULL
    AND pr."What best describes where you live?" != ''
    AND pr."Would you trust AI more or less than humans to interpret animal communication to resolve a human-wildlife conflict? Why?" != ''
GROUP BY pr."What best describes where you live?", 
         pr."Would you trust AI more or less than humans to interpret animal communication to resolve a human-wildlife conflict? Why?"
ORDER BY location
"""

df_q61_q4 = pd.read_sql_query(query_q61_q4, conn)
print(f"Total responses for Q61 x Q4: {len(df_q61_q4)}")
print("Sample responses:")
for i, row in df_q61_q4.head(10).iterrows():
    print(f"{row['location']}: {row['ai_trust_response'][:60]}...")

# Need to categorize the open-text responses - this would require manual coding
# Let's check what location types exist
location_counts = df_q61_q4.groupby('location')['count'].sum().sort_values(ascending=False)
print("\nLocation distribution:")
print(location_counts)

print("\n" + "="*70 + "\n")

# Question 6.4: Recording ownership by country
print("6.4: Recording ownership by country")
print("=" * 40)

query_q90_q7 = """
SELECT 
    pr."What country or region do you most identify with?" as country,
    pr."If we record an elephant's conversation or a whale's song, who should own that recording?" as ownership,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr."What country or region do you most identify with?" IS NOT NULL 
    AND pr."If we record an elephant's conversation or a whale's song, who should own that recording?" IS NOT NULL
    AND pr."What country or region do you most identify with?" != ''
    AND pr."If we record an elephant's conversation or a whale's song, who should own that recording?" != ''
GROUP BY pr."What country or region do you most identify with?", 
         pr."If we record an elephant's conversation or a whale's song, who should own that recording?"
ORDER BY country, ownership
"""

df_q90_q7 = pd.read_sql_query(query_q90_q7, conn)
print("Raw data (first 20 rows):")
print(df_q90_q7.head(20))

# Create contingency table
pivot_q90_q7 = df_q90_q7.pivot_table(index='country', columns='ownership', values='count', fill_value=0)
print("\nContingency table:")
print(pivot_q90_q7)

# Chi-square test
chi2, p_val, dof, expected = chi2_contingency(pivot_q90_q7)
print(f"\nChi-square test results:")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"p-value: {p_val:.3f}")
print(f"Degrees of freedom: {dof}")

# Calculate percentages
pivot_pct_ownership = pivot_q90_q7.div(pivot_q90_q7.sum(axis=1), axis=0) * 100
print("\nPercentages by country:")
print(pivot_pct_ownership.round(1))

conn.close()
print("\n=== REVIEW COMPLETE ===")