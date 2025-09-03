#!/usr/bin/env python3
"""
Section 6.4: Cultural Influence on Ownership
Analyzing Q90 (animal recording ownership) and Q91 (economic agency) by Q7 (region)
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# First check Q90 (ownership of recordings)
q90_query = """
SELECT DISTINCT Q90, COUNT(*) as count
FROM participant_responses
WHERE Q90 IS NOT NULL AND Q90 != '' AND Q90 != '--'
GROUP BY Q90
ORDER BY count DESC
"""
q90_values = pd.read_sql_query(q90_query, conn)
print("=== Q90: WHO SHOULD OWN ANIMAL RECORDINGS? ===")
print(q90_values)

# Check Q91 (economic agency)
q91_query = """
SELECT DISTINCT Q91, COUNT(*) as count
FROM participant_responses
WHERE Q91 IS NOT NULL AND Q91 != '' AND Q91 != '--'
GROUP BY Q91
ORDER BY count DESC
LIMIT 10
"""
q91_values = pd.read_sql_query(q91_query, conn)
print("\n=== Q91: ANIMAL ECONOMIC AGENCY OPTIONS ===")
for val in q91_values['Q91'].values[:5]:
    print(f"  {str(val)[:100]}")

# Analyze Q90 by region
ownership_by_region = """
SELECT 
    Q7 as region,
    Q90 as ownership_preference,
    COUNT(*) as count
FROM participant_responses
WHERE Q7 IN ('India', 'United States', 'China', 'Kenya', 'Canada', 'United Kingdom', 'Indonesia', 'Brazil', 'Chile', 'Italy')
    AND Q90 IS NOT NULL AND Q90 != '' AND Q90 != '--'
GROUP BY Q7, Q90
"""
df_ownership = pd.read_sql_query(ownership_by_region, conn)

# Calculate percentages
df_ownership['pct'] = df_ownership.groupby('region')['count'].transform(lambda x: (x / x.sum() * 100).round(1))

# Pivot for better visualization
pivot_ownership = df_ownership.pivot(index='region', columns='ownership_preference', values='pct').fillna(0)
print("\n=== OWNERSHIP PREFERENCES BY REGION (%) ===")
print(pivot_ownership)

# Statistical test for Q90
contingency_ownership = df_ownership.pivot(index='region', columns='ownership_preference', values='count').fillna(0)
if contingency_ownership.shape[0] > 1 and contingency_ownership.shape[1] > 1:
    chi2, p_value, dof, expected = chi2_contingency(contingency_ownership)
    print(f"\n=== STATISTICAL TEST FOR OWNERSHIP (Q90) ===")
    print(f"Chi-square statistic: {chi2:.2f}")
    print(f"P-value: {p_value:.6f}")
    print(f"Significant regional differences: {'YES (p < 0.05)' if p_value < 0.05 else 'NO'}")

# Analyze Q91 by region
# Since Q91 might be multiple choice, let's check its structure
q91_by_region = """
SELECT 
    Q7 as region,
    Q91 as economic_rights,
    COUNT(*) as count
FROM participant_responses
WHERE Q7 IN ('India', 'United States', 'China', 'Kenya', 'Canada', 'United Kingdom')
    AND Q91 IS NOT NULL AND Q91 != '' AND Q91 != '--'
GROUP BY Q7, Q91
"""
df_economic = pd.read_sql_query(q91_by_region, conn)

print("\n=== ANIMAL ECONOMIC RIGHTS BY REGION ===")
print(f"Unique Q91 responses found: {df_economic['economic_rights'].nunique()}")

# Categorize Q91 responses
def categorize_economic_rights(response):
    if pd.isna(response) or response == '--':
        return 'No response'
    
    response_lower = str(response).lower()
    
    if 'earn money' in response_lower or 'earn income' in response_lower:
        return 'Support earning money'
    elif 'own property' in response_lower or 'own things' in response_lower:
        return 'Support ownership'
    elif 'both' in response_lower or 'all' in response_lower:
        return 'Support both'
    elif 'none' in response_lower or 'neither' in response_lower:
        return 'Support neither'
    else:
        return 'Other'

df_economic['category'] = df_economic['economic_rights'].apply(categorize_economic_rights)

# Summarize by region
economic_summary = df_economic.groupby(['region', 'category'])['count'].sum().unstack(fill_value=0)
economic_pct = economic_summary.div(economic_summary.sum(axis=1), axis=0) * 100

print("\n=== ECONOMIC RIGHTS SUPPORT BY REGION (%) ===")
print(economic_pct.round(1))

# Key findings
print("\n=== KEY FINDINGS ===")
print("\n1. Most preferred ownership model globally:")
if not pivot_ownership.empty:
    global_pref = pivot_ownership.mean().idxmax()
    global_pct = pivot_ownership.mean().max()
    print(f"   {global_pref}: {global_pct:.1f}% average across regions")

print("\n2. Regional variations in ownership preferences:")
for region in pivot_ownership.index[:5]:  # Top 5 regions
    top_pref = pivot_ownership.loc[region].idxmax()
    top_pct = pivot_ownership.loc[region].max()
    print(f"   {region:20} -> {top_pref[:40]}... ({top_pct:.1f}%)")

conn.close()