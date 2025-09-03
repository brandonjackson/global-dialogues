#!/usr/bin/env python3
"""
Section 6.3: Urban vs. Rural Divide on Wildlife Management
Analyzing Q61 (trust in AI for wildlife conflicts) by Q4 (urban/suburban/rural)
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# First, let's see what Q61 contains
sample_query = """
SELECT DISTINCT Q61 
FROM participant_responses 
WHERE Q61 IS NOT NULL AND Q61 != '' AND Q61 != '--'
LIMIT 10
"""
samples = pd.read_sql_query(sample_query, conn)
print("Sample Q61 responses (AI trust for wildlife conflicts):")
for val in samples['Q61'].values[:5]:
    print(f"  {str(val)[:100]}...")

# Check Q4 values (urban/rural/suburban)
location_query = """
SELECT DISTINCT Q4, COUNT(*) as count
FROM participant_responses
WHERE Q4 IS NOT NULL AND Q4 != ''
GROUP BY Q4
ORDER BY count DESC
"""
locations = pd.read_sql_query(location_query, conn)
print("\n=== LOCATION DISTRIBUTION ===")
print(locations)

# Since Q61 appears to be open text, let's analyze sentiment/trust levels
# We'll need to categorize responses
analysis_query = """
SELECT 
    Q4 as location,
    Q61 as ai_trust_response,
    participant_id
FROM participant_responses
WHERE Q4 IS NOT NULL AND Q4 != '' AND Q4 != '--'
    AND Q61 IS NOT NULL AND Q61 != '' AND Q61 != '--'
"""
df = pd.read_sql_query(analysis_query, conn)

print(f"\nTotal responses with both Q4 and Q61: {len(df)}")

# Categorize trust levels based on keywords in responses
def categorize_trust(response):
    if pd.isna(response):
        return 'No response'
    
    response_lower = str(response).lower()
    
    # Trust indicators
    if any(word in response_lower for word in ['more than', 'trust ai', 'prefer ai', 'better than human', 'ai more', 'definitely ai']):
        return 'Trust AI more'
    elif any(word in response_lower for word in ['less than', 'distrust', 'prefer human', 'not trust ai', 'human better', 'ai less']):
        return 'Trust humans more'
    elif any(word in response_lower for word in ['same', 'equal', 'both', 'depends', 'neither']):
        return 'Equal/Depends'
    else:
        # Try to infer from sentiment
        if 'trust' in response_lower and 'not' not in response_lower:
            return 'Trust AI more'
        elif 'not' in response_lower or 'no' in response_lower:
            return 'Trust humans more'
        else:
            return 'Unclear'

df['trust_category'] = df['ai_trust_response'].apply(categorize_trust)

# Analyze by location
trust_by_location = df.groupby(['location', 'trust_category']).size().unstack(fill_value=0)
trust_pct = trust_by_location.div(trust_by_location.sum(axis=1), axis=0) * 100

print("\n=== TRUST IN AI VS HUMANS BY LOCATION (%) ===")
print(trust_pct.round(1))

# Statistical test
if trust_by_location.shape[0] > 1 and trust_by_location.shape[1] > 1:
    chi2, p_value, dof, expected = chi2_contingency(trust_by_location)
    print(f"\n=== STATISTICAL TEST ===")
    print(f"Chi-square statistic: {chi2:.2f}")
    print(f"P-value: {p_value:.6f}")
    print(f"Significant urban/rural differences: {'YES (p < 0.05)' if p_value < 0.05 else 'NO'}")

# Summary statistics
print("\n=== KEY FINDINGS ===")
for location in trust_pct.index:
    if 'Trust AI more' in trust_pct.columns:
        ai_trust = trust_pct.loc[location, 'Trust AI more']
        print(f"{location:20} -> {ai_trust:.1f}% trust AI more than humans")

# Look at actual response examples
print("\n=== EXAMPLE RESPONSES BY LOCATION ===")
for location in ['Urban', 'Rural', 'Suburban']:
    if location in df['location'].values:
        print(f"\n{location} examples:")
        location_responses = df[df['location'] == location]['ai_trust_response'].sample(min(3, len(df[df['location'] == location])))
        for resp in location_responses:
            print(f"  - {str(resp)[:150]}...")

conn.close()