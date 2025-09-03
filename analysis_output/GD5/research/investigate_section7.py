#!/usr/bin/env python3
"""
Deep investigation of Section 7 discrepancies
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect('../../../Data/GD5/GD5.db')

print("Deep Investigation of Section 7 Issues")
print("=" * 50)

# Issue 1: Economic rights calculation
print("\nIssue 1: Economic Rights Support")
print("-" * 30)

# Check Q91 structure
q91_sample = """
SELECT Q91 FROM participant_responses 
WHERE participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
LIMIT 10
"""
sample = pd.read_sql_query(q91_sample, conn)
print("Sample Q91 responses:")
for i, val in enumerate(sample['Q91'].values[:5]):
    print(f"  {i}: {val}")

# Get proper economic rights support calculation
equality_econ_query = """
SELECT 
    pr.participant_id,
    pr.Q94 as human_nature,
    pr.Q91 as economic_rights
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q94 = 'Humans are fundamentally equal to other animals'
"""
equality_df = pd.read_sql_query(equality_econ_query, conn)

print(f"\nTotal equality believers: {len(equality_df)}")

# Count those with "None of the above"
none_count = equality_df[equality_df['economic_rights'] == 'None of the above']['participant_id'].count()
print(f"Selecting 'None of the above': {none_count} ({none_count/len(equality_df)*100:.1f}%)")

# Count those with actual economic rights
with_rights = equality_df[~equality_df['economic_rights'].isin(['None of the above', '--', None])]['participant_id'].count()
print(f"Supporting at least one economic right: {with_rights} ({with_rights/len(equality_df)*100:.1f}%)")

print("\nDistribution of Q91 responses among equality believers:")
print(equality_df['economic_rights'].value_counts().head(10))

# Issue 2: Culture beliefs and democratic participation
print("\n\nIssue 2: Culture Beliefs and Political Views")
print("-" * 30)

# Check Q41 structure (culture beliefs)
q41_sample = """
SELECT Q41 FROM participant_responses 
WHERE participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
    AND Q41 IS NOT NULL
LIMIT 10
"""
sample41 = pd.read_sql_query(q41_sample, conn)
print("Sample Q41 responses (culture beliefs):")
for val in sample41['Q41'].unique()[:5]:
    print(f"  - {val}")

# Check Q77 structure (democratic participation)
q77_sample = """
SELECT Q77 FROM participant_responses 
WHERE participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
    AND Q77 IS NOT NULL
LIMIT 10
"""
sample77 = pd.read_sql_query(q77_sample, conn)
print("\nSample Q77 responses (democratic participation):")
for val in sample77['Q77'].unique()[:5]:
    print(f"  - {val}")

# Get actual culture belief counts
culture_query = """
SELECT 
    pr.Q41 as culture_belief,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q41 IS NOT NULL
GROUP BY pr.Q41
ORDER BY count DESC
"""
culture_dist = pd.read_sql_query(culture_query, conn)
print("\nDistribution of Q41 (culture beliefs):")
for _, row in culture_dist.iterrows():
    print(f"  {row['culture_belief']}: {row['count']}")

# Now check democratic participation among strong culture believers
culture_demo_query = """
SELECT 
    pr.Q41 as culture,
    pr.Q77 as democratic
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q41 = 'Strongly believe'
"""
culture_demo_df = pd.read_sql_query(culture_demo_query, conn)

print(f"\nStrong culture believers: {len(culture_demo_df)}")
print("\nTheir democratic participation views:")
print(culture_demo_df['democratic'].value_counts())

# Check for "radical" positions
radical_keywords = ['constituencies', 'proxy', 'voting rights', 'formal political']
radical_count = 0
for val in culture_demo_df['democratic'].values:
    if pd.notna(val) and any(keyword in val.lower() for keyword in radical_keywords):
        radical_count += 1
        print(f"\nRadical position found: {val}")

if len(culture_demo_df) > 0:
    print(f"\nTotal with radical positions: {radical_count} ({radical_count/len(culture_demo_df)*100:.1f}%)")
else:
    print(f"\nTotal with radical positions: {radical_count} (no strong culture believers found)")

conn.close()