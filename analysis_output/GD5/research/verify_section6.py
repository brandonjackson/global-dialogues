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
    pr.Q7 as country,
    pr.Q70 as approach,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr.Q7 IS NOT NULL 
    AND pr.Q70 IS NOT NULL
    AND pr.Q7 != ''
    AND pr.Q70 != ''
GROUP BY pr.Q7, pr.Q70
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
    pr.Q6 as religion,
    pr.Q94 as human_animal_relation,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr.Q6 IS NOT NULL 
    AND pr.Q94 IS NOT NULL
    AND pr.Q6 != ''
    AND pr.Q94 != ''
GROUP BY pr.Q6, pr.Q94
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
    pr.Q4 as location,
    pr.Q61 as ai_trust_response,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr.Q4 IS NOT NULL 
    AND pr.Q61 IS NOT NULL
    AND pr.Q4 != ''
    AND pr.Q61 != ''
GROUP BY pr.Q4, pr.Q61
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
    pr.Q7 as country,
    pr.Q90 as ownership,
    COUNT(*) as count
FROM participant_responses pr
WHERE pr.Q7 IS NOT NULL 
    AND pr.Q90 IS NOT NULL
    AND pr.Q7 != ''
    AND pr.Q90 != ''
GROUP BY pr.Q7, pr.Q90
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