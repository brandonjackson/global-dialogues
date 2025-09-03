#!/usr/bin/env python3
"""
Section 6.1: Regional Views on Animal Rights
"""
import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get the Q70 responses with region data
query = """
SELECT 
    Q7 as region,
    Q70 as animal_protection_preference,
    COUNT(*) as count
FROM participant_responses
WHERE Q7 IS NOT NULL AND Q70 IS NOT NULL
GROUP BY Q7, Q70
"""

df = pd.read_sql_query(query, conn)
print("Unique Q70 responses (animal protection preferences):")
print(df['animal_protection_preference'].unique())

# Get overall distribution
overall_query = """
SELECT 
    Q70 as preference,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q70 IS NOT NULL), 2) as percentage
FROM participant_responses
WHERE Q70 IS NOT NULL
GROUP BY Q70
ORDER BY count DESC
"""
overall = pd.read_sql_query(overall_query, conn)
print("\n=== OVERALL DISTRIBUTION OF ANIMAL PROTECTION PREFERENCES ===")
print(overall)

# Analyze by major regions
major_regions_query = """
SELECT 
    Q7 as region,
    Q70 as preference,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY Q7), 2) as pct_within_region
FROM participant_responses
WHERE Q7 IN ('India', 'United States', 'China', 'Kenya', 'Canada', 'United Kingdom', 'Indonesia', 'Brazil')
    AND Q70 IS NOT NULL
GROUP BY Q7, Q70
ORDER BY Q7, count DESC
"""
regional = pd.read_sql_query(major_regions_query, conn)
print("\n=== REGIONAL BREAKDOWN (Top 8 Countries) ===")
pivot = regional.pivot(index='region', columns='preference', values='pct_within_region').fillna(0)
print(pivot)

# Statistical test for significance
from scipy.stats import chi2_contingency

# Create contingency table for chi-square test
contingency_query = """
SELECT Q7, Q70, COUNT(*) as count
FROM participant_responses
WHERE Q7 IN ('India', 'United States', 'China', 'Kenya', 'Canada', 'United Kingdom', 'Indonesia', 'Brazil')
    AND Q70 IS NOT NULL
GROUP BY Q7, Q70
"""
cont_df = pd.read_sql_query(contingency_query, conn)
cont_table = cont_df.pivot(index='Q7', columns='Q70', values='count').fillna(0)

chi2, p_value, dof, expected = chi2_contingency(cont_table)
print(f"\n=== STATISTICAL TEST ===")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"P-value: {p_value:.6f}")
print(f"Degrees of freedom: {dof}")
print(f"Significant regional differences: {'YES' if p_value < 0.05 else 'NO'}")

# Find most distinctive preferences by region
print("\n=== MOST DISTINCTIVE REGIONAL PREFERENCES ===")
for region in pivot.index:
    max_pref = pivot.loc[region].idxmax()
    max_val = pivot.loc[region].max()
    print(f"{region:20} -> {max_pref:10} ({max_val:.1f}%)")

conn.close()