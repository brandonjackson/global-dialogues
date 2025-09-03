#!/usr/bin/env python3
"""
Section 21: Risk vs. Benefit Balances
Analyzing Q63 (benefits) and Q64 (risks) - these are open-ended questions
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import re

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("=" * 80)
print("SECTION 21: RISK VS. BENEFIT BALANCES")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get participant responses with reliable PRI scores
query = """
SELECT pr.*, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
df_participants = pd.read_sql_query(query, conn)
print(f"\nTotal reliable participants: {len(df_participants)}")

# Get open-ended responses for Q63 and Q64
responses_query = """
SELECT r.participant_id, r.question, r.response
FROM responses r
JOIN participants p ON r.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
AND (r.question LIKE '%biggest benefit%' OR r.question LIKE '%biggest risk%')
"""
df_responses = pd.read_sql_query(responses_query, conn)

print(f"Open-ended responses collected: {len(df_responses)}")

# Separate benefits and risks
benefits_df = df_responses[df_responses['question'].str.contains('benefit', case=False, na=False)]
risks_df = df_responses[df_responses['question'].str.contains('risk', case=False, na=False)]

print(f"  Benefits responses: {len(benefits_df)}")
print(f"  Risks responses: {len(risks_df)}")

# Helper function to categorize responses
def categorize_response(response, categories):
    """Categorize a response based on keyword matching"""
    if pd.isna(response):
        return 'Unknown'
    response_lower = str(response).lower()
    for category, keywords in categories.items():
        if any(keyword in response_lower for keyword in keywords):
            return category
    return 'Other'

# Define benefit categories
benefit_categories = {
    'Bond/Relationship': ['bond', 'relationship', 'connection', 'connect', 'understanding', 'empathy', 'compassion', 'love', 'closer'],
    'Conservation': ['conservation', 'protect', 'preserve', 'save', 'extinct', 'environment', 'ecosystem', 'habitat'],
    'Communication': ['communication', 'communicate', 'talk', 'speak', 'listen', 'language', 'understand what'],
    'Welfare': ['welfare', 'wellbeing', 'well-being', 'suffering', 'pain', 'help', 'care', 'needs'],
    'Coexistence': ['coexist', 'harmony', 'peaceful', 'together', 'share', 'respect'],
    'Knowledge': ['learn', 'knowledge', 'discover', 'research', 'science', 'study']
}

# Define risk categories
risk_categories = {
    'Manipulation/Exploitation': ['manipulat', 'exploit', 'abuse', 'control', 'use', 'commercial', 'profit'],
    'Emotional': ['emotional', 'attach', 'anthropomorph', 'project', 'feeling', 'distress'],
    'Poaching/Harm': ['poach', 'hunt', 'kill', 'harm', 'capture', 'illegal'],
    'Disruption': ['disrupt', 'chaos', 'conflict', 'society', 'order', 'change', 'radical'],
    'Misunderstanding': ['misunderstand', 'misinterpret', 'wrong', 'mistake', 'error', 'inaccurate'],
    'Privacy': ['privacy', 'intrusion', 'invasive', 'surveillance', 'monitor'],
    'Technology': ['technology', 'AI', 'artificial', 'hack', 'misuse', 'malfunction']
}

# Categorize responses
benefits_df['category'] = benefits_df['response'].apply(lambda x: categorize_response(x, benefit_categories))
risks_df['category'] = risks_df['response'].apply(lambda x: categorize_response(x, risk_categories))

print("\n" + "=" * 80)
print("Question 21.1: Bond Deepening vs. Manipulation")
print("=" * 80)

# Merge benefits and risks by participant
merged_df = pd.merge(
    benefits_df[['participant_id', 'category']].rename(columns={'category': 'benefit_category'}),
    risks_df[['participant_id', 'category']].rename(columns={'category': 'risk_category'}),
    on='participant_id',
    how='inner'
)

# Analyze bond-deepening respondents
bond_deepeners = merged_df[merged_df['benefit_category'] == 'Bond/Relationship']
if len(bond_deepeners) > 0:
    risk_distribution = bond_deepeners['risk_category'].value_counts()
    total_bond = len(bond_deepeners)
    
    print(f"\n**Finding:** Among {total_bond} respondents citing bond-deepening as the biggest benefit:")
    manipulation_count = risk_distribution.get('Manipulation/Exploitation', 0) + risk_distribution.get('Emotional', 0)
    manipulation_pct = (manipulation_count / total_bond) * 100
    print(f"  {manipulation_pct:.1f}% cite manipulation/emotional risks as biggest concern")
    
    print("\n**Method:** Categorization of open-ended responses using keyword matching")
    print("\n**Details:**")
    print("Risk concerns among bond-deepening advocates:")
    for risk, count in risk_distribution.items():
        pct = (count / total_bond) * 100
        print(f"  - {risk}: {count} ({pct:.1f}%)")

print("\n" + "=" * 80)
print("Question 21.2: Age-Based Risk Perceptions")
print("=" * 80)

# Merge with participant data for demographics
risks_with_demo = pd.merge(
    risks_df,
    df_participants[['participant_id', 'Q2']],  # Q2 is age
    on='participant_id',
    how='inner'
)

# Group ages into younger vs older
def age_group(age):
    if age in ['18-25', '26-35']:
        return 'Younger (18-35)'
    elif age in ['46-55', '56-65', '65+']:
        return 'Older (46+)'
    else:
        return 'Middle (36-45)'

risks_with_demo['age_group'] = risks_with_demo['Q2'].apply(age_group)

# Analyze risk perceptions by age group
print("\n**Finding:** Age-based risk perception differences")
print("\n**Method:** Chi-square test of risk categories by age groups")
print("\n**Details:**")

for age_grp in ['Younger (18-35)', 'Older (46+)']:
    age_risks = risks_with_demo[risks_with_demo['age_group'] == age_grp]
    if len(age_risks) > 0:
        risk_dist = age_risks['category'].value_counts()
        total = len(age_risks)
        print(f"\n{age_grp} (N={total}):")
        for risk, count in risk_dist.head(5).items():
            pct = (count / total) * 100
            print(f"  - {risk}: {pct:.1f}%")

# Statistical test for differences
from scipy import stats
if len(risks_with_demo) > 0:
    contingency_table = pd.crosstab(risks_with_demo['age_group'], risks_with_demo['category'])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    print(f"\nChi-square test: χ²={chi2:.2f}, p={p_value:.4f}")
    if p_value < 0.05:
        print("Significant age differences in risk perceptions detected")

print("\n" + "=" * 80)
print("Question 21.3: Conservation Benefits vs. Poaching Risks")
print("=" * 80)

# Analyze conservation advocates
conservationists = merged_df[merged_df['benefit_category'] == 'Conservation']
if len(conservationists) > 0:
    conservation_risks = conservationists['risk_category'].value_counts()
    total_conservation = len(conservationists)
    
    poaching_concerned = conservation_risks.get('Poaching/Harm', 0)
    poaching_pct = (poaching_concerned / total_conservation) * 100
    
    print(f"\n**Finding:** Among {total_conservation} conservation-focused respondents:")
    print(f"  {poaching_pct:.1f}% cite poaching/harm as their biggest risk")
    
    print("\n**Method:** Cross-tabulation of benefit and risk categories")
    print("\n**Details:**")
    print("Risk priorities among conservation advocates:")
    for risk, count in conservation_risks.items():
        pct = (count / total_conservation) * 100
        print(f"  - {risk}: {count} ({pct:.1f}%)")

# Overall benefit-risk patterns
print("\n" + "=" * 80)
print("OVERALL BENEFIT-RISK PATTERNS")
print("=" * 80)

# Most common benefit-risk pairs
benefit_risk_pairs = merged_df.groupby(['benefit_category', 'risk_category']).size().reset_index(name='count')
benefit_risk_pairs = benefit_risk_pairs.sort_values('count', ascending=False)

print("\nMost common benefit-risk pairings:")
for idx, row in benefit_risk_pairs.head(10).iterrows():
    pct = (row['count'] / len(merged_df)) * 100
    print(f"  {row['benefit_category']} → {row['risk_category']}: {row['count']} ({pct:.1f}%)")

# Calculate correlation between benefit and risk types
if len(merged_df) > 30:
    # Create contingency table
    contingency = pd.crosstab(merged_df['benefit_category'], merged_df['risk_category'])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nBenefit-Risk Association: χ²={chi2:.2f}, p={p_value:.4f}")
    if p_value < 0.05:
        print("Significant association between perceived benefits and risks")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)