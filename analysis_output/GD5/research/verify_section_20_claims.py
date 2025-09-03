#!/usr/bin/env python3
"""
Verify key claims in Section 20: Moral/Ethical Contradictions
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== VERIFYING SECTION 20 CLAIMS ===\n")

# === Claim 1: Selective Democratic Acceptance ===
print("=== CLAIM 1: SELECTIVE DEMOCRATIC ACCEPTANCE ===")

# First verify Q77 distribution
q77_query = """
SELECT Q77, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q77 IS NOT NULL AND Q77 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q77 IS NOT NULL AND Q77 != '--'
GROUP BY Q77
ORDER BY count DESC
"""
q77_results = pd.read_sql_query(q77_query, conn)
print("Q77 Democratic participation distribution:")
for _, row in q77_results.iterrows():
    print(f"  {row['Q77']}: {row['count']} ({row['percentage']}%)")

# Find those who oppose democratic participation
no_participation = q77_results[q77_results['Q77'].str.contains('No', na=False)]['count'].iloc[0]
no_participation_pct = q77_results[q77_results['Q77'].str.contains('No', na=False)]['percentage'].iloc[0]

print(f"\nThose opposing democratic participation: {no_participation} ({no_participation_pct}%)")
print(f"Claimed: 37.1% oppose participation")

# Check Q73 support among those who oppose Q77
q77_q73_query = """
SELECT Q77, Q73, COUNT(*) as count
FROM participant_responses
WHERE Q77 IS NOT NULL AND Q77 != '--' AND Q73 IS NOT NULL AND Q73 != '--'
GROUP BY Q77, Q73
"""
q77_q73_df = pd.read_sql_query(q77_q73_query, conn)

# Filter for those who oppose democratic participation
oppose_demo = q77_q73_df[q77_q73_df['Q77'].str.contains('No', na=False)]
print("\nQ73 responses among those opposing democratic participation:")
print(oppose_demo)

# Calculate percentages among opposition group
if len(oppose_demo) > 0:
    total_oppose = oppose_demo['count'].sum()
    oppose_support_rep = oppose_demo[oppose_demo['Q73'] == 'Yes']['count'].sum() if 'Yes' in oppose_demo['Q73'].values else 0
    oppose_support_rep_pct = (oppose_support_rep / total_oppose * 100) if total_oppose > 0 else 0
    
    print(f"\nAmong those opposing democratic participation:")
    print(f"Support legal representation: {oppose_support_rep}/{total_oppose} ({oppose_support_rep_pct:.1f}%)")
    print(f"Claimed: 20.6% support representation")

# === Claim 2: Professional Restrictions vs Democratic Rights ===
print("\n\n=== CLAIM 2: PROFESSIONAL RESTRICTIONS vs DEMOCRATIC RIGHTS ===")

# Q82 distribution
q82_query = """
SELECT Q82, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q82 IS NOT NULL AND Q82 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q82 IS NOT NULL AND Q82 != '--'
GROUP BY Q82
ORDER BY count DESC
"""
q82_results = pd.read_sql_query(q82_query, conn)
print("Q82 Professional restrictions distribution:")
for _, row in q82_results.iterrows():
    print(f"  {row['Q82']}: {row['count']} ({row['percentage']}%)")

# Calculate agreement rate
agree_count = q82_results[q82_results['Q82'].str.contains('agree', case=False, na=False)]['count'].sum()
total_q82 = q82_results['count'].sum()
agree_pct = (agree_count / total_q82 * 100) if total_q82 > 0 else 0
print(f"\nTotal agreement with professional restrictions: {agree_pct:.1f}%")
print(f"Claimed: 76.3% agreement")

# Check correlation between Q82 and formal political constituencies
political_const_query = """
SELECT Q82, Q77, COUNT(*) as count
FROM participant_responses
WHERE Q82 IS NOT NULL AND Q82 != '--' AND Q77 IS NOT NULL AND Q77 != '--'
  AND Q77 LIKE '%formal political constituency%'
GROUP BY Q82, Q77
"""
political_const_df = pd.read_sql_query(political_const_query, conn)
print(f"\nFormal political constituency supporters by Q82 stance:")
if len(political_const_df) > 0:
    print(political_const_df)

# === Claim 3: Property vs Economic Participation ===
print("\n\n=== CLAIM 3: PROPERTY vs ECONOMIC PARTICIPATION ===")

# Q91 distribution sample
q91_query = """
SELECT Q91, COUNT(*) as count
FROM participant_responses 
WHERE Q91 IS NOT NULL AND Q91 != '--'
GROUP BY Q91
ORDER BY count DESC
LIMIT 10
"""
q91_results = pd.read_sql_query(q91_query, conn)
print("Q91 Economic rights - top responses:")
for _, row in q91_results.iterrows():
    print(f"  {row['Q91']}: {row['count']}")

# Count property ownership supporters
property_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q91 IS NOT NULL AND Q91 != '--' AND Q91 LIKE '%property%'
"""
property_count = pd.read_sql_query(property_query, conn)['count'].iloc[0]
print(f"\nProperty ownership supporters: {property_count}")
print(f"Claimed: n=130 property supporters")

# Look for correlation patterns in the data
print("\n=== GENERAL DATA QUALITY CHECK ===")
total_responses_query = """
SELECT COUNT(*) as total_responses
FROM participant_responses
"""
total_responses = pd.read_sql_query(total_responses_query, conn)['count'].iloc[0]
print(f"Total responses in database: {total_responses}")

conn.close()

print("\n=== SUMMARY ===")
print("Key claims to verify:")
print("1. 37.1% oppose democratic participation - among them, 20.6% support legal representation")
print("2. 76.3% support professional restrictions, no correlation with democratic rights")
print("3. Property ownership supporters (n=130) show 70% support for economic participation")