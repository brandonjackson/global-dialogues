#!/usr/bin/env python3
"""
Verification script for Section 7 findings
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

print("Verifying Section 7 findings...")
print("=" * 50)

# 1. Verify equality believers and economic rights (Question 7.1)
print("Question 7.1: Equality to Economics")
print("-" * 30)

# Get equality believers
equality_query = """
SELECT 
    pr.participant_id,
    pr.Q94 as human_nature_view,
    pr.Q91 as economic_rights
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
equality_df = pd.read_sql_query(equality_query, conn)

# Count equality believers
equality_believers = equality_df[equality_df['human_nature_view'] == 'Humans are fundamentally equal to other animals']
print(f"Equality believers: {len(equality_believers)} out of {len(equality_df)}")
print(f"Percentage: {len(equality_believers)/len(equality_df)*100:.1f}%")

# Check economic rights support
equality_with_rights = equality_believers[~equality_believers['economic_rights'].isin(['None of the above', '--', None])].dropna()
print(f"Equality believers supporting economic rights: {len(equality_with_rights)} ({len(equality_with_rights)/len(equality_believers)*100:.1f}%)")

# Non-equality believers
non_equality = equality_df[equality_df['human_nature_view'] != 'Humans are fundamentally equal to other animals']
non_equality_with_rights = non_equality[~non_equality['economic_rights'].isin(['None of the above', '--', None])].dropna()
print(f"Non-equality believers supporting economic rights: {len(non_equality_with_rights)} ({len(non_equality_with_rights)/len(non_equality)*100:.1f}%)")

print()

# 2. Verify skeptics' interest (Question 7.2)
print("Question 7.2: The Skeptic's Interest")
print("-" * 30)

skeptics_query = """
SELECT 
    pr.participant_id,
    pr.Q5 as ai_sentiment,
    pr.Q57 as ai_translation_trust,
    pr.Q55 as interest_level
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q5 = 'More concerned than excited'
    AND pr.Q57 LIKE '%Strongly Distrust%'
"""
skeptics_df = pd.read_sql_query(skeptics_query, conn)

print(f"Total skeptics (concerned + strongly distrust): {len(skeptics_df)}")
if len(skeptics_df) > 0:
    interest_counts = skeptics_df['interest_level'].value_counts()
    print("Interest levels:")
    for level, count in interest_counts.items():
        print(f"  - {level}: {count} ({count/len(skeptics_df)*100:.1f}%)")
    
    # Check if Q57 is about AI translation trust
    check_q57 = """
    SELECT DISTINCT Q57 FROM participant_responses 
    WHERE participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
    LIMIT 5
    """
    q57_sample = pd.read_sql_query(check_q57, conn)
    print("\nQ57 sample responses (to verify it's about AI translation):")
    print(q57_sample)

print()

# 3. Verify regulation paradox (Question 7.3)
print("Question 7.3: The Regulation Paradox")
print("-" * 30)

regulation_query = """
SELECT 
    pr.Q83 as public_access,
    pr.Q84 as company_regulation
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q83 IS NOT NULL
    AND pr.Q84 IS NOT NULL
"""
regulation_df = pd.read_sql_query(regulation_query, conn)

# Convert to numeric for correlation
agree_mapping = {
    'Strongly agree': 5,
    'Somewhat agree': 4,
    'Neutral': 3,
    'Somewhat disagree': 2,
    'Strongly disagree': 1
}

regulation_df['access_score'] = regulation_df['public_access'].map(agree_mapping)
regulation_df['regulation_score'] = regulation_df['company_regulation'].map(agree_mapping)

# Calculate correlation
if len(regulation_df.dropna()) > 1:
    correlation = regulation_df[['access_score', 'regulation_score']].corr().iloc[0, 1]
    print(f"Correlation between public access and company regulation: {correlation:.3f}")

# Count those who want both
both = regulation_df[
    (regulation_df['public_access'].isin(['Strongly agree', 'Somewhat agree'])) &
    (regulation_df['company_regulation'].isin(['Strongly agree', 'Somewhat agree']))
]
print(f"Want both regulation and access: {len(both)} ({len(both)/len(regulation_df)*100:.1f}%)")

print()

# 4. Verify animal culture and political views (Question 7.4)
print("Question 7.4: Animal Culture and Political Radicalism")
print("-" * 30)

culture_query = """
SELECT 
    pr.Q41 as culture_belief,
    pr.Q77 as democratic_participation
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q41 IS NOT NULL
    AND pr.Q77 IS NOT NULL
"""
culture_df = pd.read_sql_query(culture_query, conn)

# Strong culture believers
strong_believers = culture_df[culture_df['culture_belief'].str.contains('strongly', case=False, na=False)]
print(f"Strong culture believers: {len(strong_believers)}")

# Check radical positions (constituencies or proxy voting)
if len(strong_believers) > 0:
    radical_believers = strong_believers[
        strong_believers['democratic_participation'].str.contains('constituencies|proxy', case=False, na=False)
    ]
    print(f"Strong believers supporting radical positions: {len(radical_believers)} ({len(radical_believers)/len(strong_believers)*100:.1f}%)")

# Culture skeptics
skeptics = culture_df[culture_df['culture_belief'].str.contains('disagree|do not', case=False, na=False)]
print(f"Culture skeptics: {len(skeptics)}")
if len(skeptics) > 0:
    radical_skeptics = skeptics[
        skeptics['democratic_participation'].str.contains('constituencies|proxy', case=False, na=False)
    ]
    print(f"Skeptics supporting radical positions: {len(radical_skeptics)} ({len(radical_skeptics)/len(skeptics)*100:.1f}%)")

# Chi-square test
if len(strong_believers) > 0 and len(skeptics) > 0:
    contingency = pd.crosstab(
        culture_df['culture_belief'].str.contains('strongly', case=False, na=False),
        culture_df['democratic_participation'].str.contains('constituencies|proxy', case=False, na=False)
    )
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square test:")
    print(f"  χ² = {chi2:.2f}, p = {p_value:.3f}")

conn.close()

print("\n" + "=" * 50)
print("Verification complete!")