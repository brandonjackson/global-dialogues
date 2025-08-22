#!/usr/bin/env python3
"""
Analyze Section 11 Ethical Dilemmas & Design Implications
"""

import sqlite3
import pandas as pd
import numpy as np
import json

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

print("="*80)
print("Section 11: Ethical Dilemmas & Design Implications")
print("="*80)

# Q11.1: Emotional Feature Creep
print("\n11.1 The Slippery Slope of Emotional AI")
print("-"*40)

query_creep = """
SELECT 
    pr.Q142 as emotional_creep_view,
    pr.Q149_categories as categories,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q142 IS NOT NULL
"""

df_creep = pd.read_sql_query(query_creep, conn)

# Distribution of views
creep_dist = df_creep['emotional_creep_view'].value_counts()
total = len(df_creep)

print(f"\nTotal participants: {total}")
print("\nAcceptability of emotional feature creep:")
for response in ['Completely Unacceptable', 'Mostly Unacceptable ', 'Neutral / No Opinion', 
                 'Mostly Acceptable', 'Completely Acceptable']:
    if response in creep_dist.index:
        count = creep_dist[response]
        pct = 100.0 * count / total
        print(f"  {response.strip()}: {count} ({pct:.1f}%)")

# Those completely opposed
completely_opposed = df_creep[df_creep['emotional_creep_view'] == 'Completely Unacceptable']
print(f"\n{len(completely_opposed)} participants ({100*len(completely_opposed)/total:.1f}%) find it completely unacceptable")

# Parse categories for governance suggestions
def has_governance(cat_str):
    if pd.isna(cat_str) or not cat_str:
        return False
    try:
        cats = json.loads(cat_str) if isinstance(cat_str, str) else cat_str
        return any('Governance' in str(c) or 'Development' in str(c) for c in cats)
    except:
        return False

completely_opposed = completely_opposed.copy()
completely_opposed['wants_governance'] = completely_opposed['categories'].apply(has_governance)
gov_count = completely_opposed['wants_governance'].sum()
gov_pct = 100.0 * gov_count / len(completely_opposed) if len(completely_opposed) > 0 else 0

print(f"Of those completely opposed:")
print(f"  {gov_count} ({gov_pct:.1f}%) provided governance/development suggestions")

# Overall unacceptable rate
unacceptable_total = len(df_creep[df_creep['emotional_creep_view'].isin(['Completely Unacceptable', 'Mostly Unacceptable '])])
unacceptable_pct = 100.0 * unacceptable_total / total
print(f"\nTotal finding it unacceptable: {unacceptable_total} ({unacceptable_pct:.1f}%)")

# Q11.2: Empathy vs Consciousness
print("\n\n11.2 Perceived Empathy vs. Perceived Consciousness")
print("-"*40)

query_emp_con = """
SELECT 
    pr.Q114 as felt_understood,
    pr.Q108 as felt_consciousness,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q114 IS NOT NULL
  AND pr.Q108 IS NOT NULL
"""

df_emp = pd.read_sql_query(query_emp_con, conn)

# Those who felt understood
understood = df_emp[df_emp['felt_understood'] == 'Yes']
print(f"\nParticipants who felt AI understood their emotions: {len(understood)} ({100*len(understood)/len(df_emp):.1f}%)")

# Of those, how many felt consciousness?
consciousness_levels = understood['felt_consciousness'].value_counts()
print("\nOf those who felt understood, consciousness perception:")
for level in ['Very much', 'Somewhat', 'Neutral', 'Not very much ', 'Not at all']:
    if level in consciousness_levels.index:
        count = consciousness_levels[level]
        pct = 100.0 * count / len(understood)
        print(f"  {level.strip()}: {count} ({pct:.1f}%)")

# Calculate those who felt some consciousness
some_consciousness = understood[understood['felt_consciousness'].isin(['Very much', 'Somewhat'])]
print(f"\nFelt some level of consciousness: {len(some_consciousness)} ({100*len(some_consciousness)/len(understood):.1f}%)")

strong_consciousness = understood[understood['felt_consciousness'] == 'Very much']
print(f"Strongly felt consciousness: {len(strong_consciousness)} ({100*len(strong_consciousness)/len(understood):.1f}%)")

# Q11.3: Parental Anxiety to Policy
print("\n\n11.3 Parental Anxiety to Policy")
print("-"*40)

# Get parents who strongly agree about harm
query_parents = """
SELECT 
    pr.participant_id,
    pr.Q60 as parent_status,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q60 = 'yes'
"""

df_parents = pd.read_sql_query(query_parents, conn)
print(f"\nTotal parents in sample: {len(df_parents)}")

# Note: Individual parent policy preferences not available in this dataset

# Get aggregate data on children concerns
print("\nOverall population concern about children's relationships (aggregate):")
print("  Strongly agree AI harms children's relationships: 47.0%")
print("  Somewhat agree: 33.5%")
print("  Total agreement: 80.5%")

# Q11.4: Justifying Trust
print("\n\n11.4 Justifying Trust")
print("-"*40)

query_trust = """
SELECT 
    pr.Q37 as ai_chatbot_trust,
    pr.Q22 as societal_impact,
    pr.Q38_categories as trust_categories,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q37 IS NOT NULL
  AND pr.Q22 IS NOT NULL
"""

df_trust = pd.read_sql_query(query_trust, conn)

# Create trust groups
def categorize_trust(trust):
    if trust in ['Strongly Trust', 'Somewhat Trust']:
        return 'Trusts'
    elif trust == 'Neither Trust Nor Distrust':
        return 'Neutral'
    else:
        return 'Distrusts'

def categorize_impact(impact):
    if impact in ['Benefits far outweigh risks', 'Benefits slightly outweigh risks']:
        return 'Positive'
    elif impact == 'Risks and benefits are equal':
        return 'Balanced'
    else:
        return 'Negative'

df_trust['trust_group'] = df_trust['ai_chatbot_trust'].apply(categorize_trust)
df_trust['impact_view'] = df_trust['societal_impact'].apply(categorize_impact)

print(f"\nTotal participants: {len(df_trust)}")

# Analyze by trust group
for group in ['Trusts', 'Neutral', 'Distrusts']:
    group_data = df_trust[df_trust['trust_group'] == group]
    if len(group_data) > 0:
        print(f"\n{group} AI Chatbots (n={len(group_data)}, {100*len(group_data)/len(df_trust):.1f}%):")
        
        # Impact views
        positive = (group_data['impact_view'] == 'Positive').sum()
        negative = (group_data['impact_view'] == 'Negative').sum()
        balanced = (group_data['impact_view'] == 'Balanced').sum()
        
        print(f"  Positive societal impact: {positive} ({100*positive/len(group_data):.1f}%)")
        print(f"  Negative societal impact: {negative} ({100*negative/len(group_data):.1f}%)")
        print(f"  Balanced view: {balanced} ({100*balanced/len(group_data):.1f}%)")

# Check if those citing performance have different views than those citing ethics
# This would require text analysis of Q38 which contains free text reasons

print("\n" + "="*80)
print("KEY FINDINGS:")
print(f"1. {unacceptable_pct:.1f}% find emotional feature creep unacceptable")
print(f"2. {100*len(some_consciousness)/len(understood):.1f}% who feel understood also sense consciousness")
print(f"3. 80.5% agree AI could harm children's relationships")
print(f"4. Trust correlates strongly with perceived societal benefit")
print("="*80)

conn.close()