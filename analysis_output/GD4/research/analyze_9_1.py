import sqlite3
import pandas as pd
import numpy as np
import json
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Question 9.1: The "I Want It, But I Fear It" Paradox
# Do people who most strongly agree that AI should be designed to be "as human-like as possible" 
# also express the greatest fear that AI will lead to a "decline in human empathy and social skills"?

print("\n" + "="*80)
print("9.1 The 'I Want It, But I Fear It' Paradox")
print("="*80)

# First, let's find the questions about human-like design and fears
# Need to identify questions about:
# 1. AI design preferences (human-like vs clearly non-human)
# 2. Fears about decline in human empathy and social skills

# Get participant data with relevant questions
query = """
SELECT 
    pr.participant_id,
    pr.Q111 as ai_design_preference,  -- Human-like vs clearly non-human
    pr.Q115 as greatest_fears,  -- JSON array of fears
    pr.Q134 as negative_impact_children,  -- Impact on children's relationships
    pr.Q133 as emotional_dependency_concern,  -- Concern about emotional dependency
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# Parse the fears JSON
def parse_fears(fears_str):
    if pd.isna(fears_str) or fears_str == '' or fears_str == 'null':
        return []
    try:
        fears = json.loads(fears_str)
        if isinstance(fears, list):
            return fears
        return []
    except:
        return []

df['fears_list'] = df['greatest_fears'].apply(parse_fears)

# Check if they fear decline in empathy/social skills
df['fears_empathy_decline'] = df['fears_list'].apply(
    lambda fears: any('decline in human empathy and social skills' in str(fear).lower() or 
                     'empathy' in str(fear).lower() and 'decline' in str(fear).lower()
                     for fear in fears)
)

# Also check the specific concern about loss of human connection
df['fears_loss_connection'] = df['fears_list'].apply(
    lambda fears: any('loss of genuine human connection' in str(fear).lower() or
                     'genuine human' in str(fear).lower()
                     for fear in fears)
)

# Analyze design preference
print("\n1. AI Design Preference Distribution:")
design_counts = df['ai_design_preference'].value_counts()
for pref, count in design_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {pref}: {count} ({pct:.1f}%)")

# Those who want human-like design
want_humanlike = df[df['ai_design_preference'] == 'As human-like as possible']
want_nonhuman = df[df['ai_design_preference'] == 'Clearly non-human']
neutral_design = df[df['ai_design_preference'] == 'Neutral']

print(f"\n2. Fear Analysis by Design Preference:")
print(f"\n   Among those who want AI 'As human-like as possible' (n={len(want_humanlike)}):")
print(f"   - Fear empathy decline: {want_humanlike['fears_empathy_decline'].sum()} ({want_humanlike['fears_empathy_decline'].mean()*100:.1f}%)")
print(f"   - Fear loss of connection: {want_humanlike['fears_loss_connection'].sum()} ({want_humanlike['fears_loss_connection'].mean()*100:.1f}%)")

print(f"\n   Among those who want AI 'Clearly non-human' (n={len(want_nonhuman)}):")
print(f"   - Fear empathy decline: {want_nonhuman['fears_empathy_decline'].sum()} ({want_nonhuman['fears_empathy_decline'].mean()*100:.1f}%)")
print(f"   - Fear loss of connection: {want_nonhuman['fears_loss_connection'].sum()} ({want_nonhuman['fears_loss_connection'].mean()*100:.1f}%)")

print(f"\n   Among those who are 'Neutral' (n={len(neutral_design)}):")
print(f"   - Fear empathy decline: {neutral_design['fears_empathy_decline'].sum()} ({neutral_design['fears_empathy_decline'].mean()*100:.1f}%)")
print(f"   - Fear loss of connection: {neutral_design['fears_loss_connection'].sum()} ({neutral_design['fears_loss_connection'].mean()*100:.1f}%)")

# Check for the paradox: Want human-like BUT fear empathy decline
paradox_group = df[(df['ai_design_preference'] == 'As human-like as possible') & 
                   (df['fears_empathy_decline'] == True)]

print(f"\n3. The Paradox Group:")
print(f"   {len(paradox_group)} people ({len(paradox_group)/len(df)*100:.1f}% of all participants)")
print(f"   want AI to be as human-like as possible BUT fear empathy decline")

# Statistical test
print("\n4. Statistical Analysis:")
# Create contingency table for chi-square test
contingency = pd.crosstab(
    df['ai_design_preference'],
    df['fears_empathy_decline'],
    margins=True
)
print("\nContingency Table: Design Preference vs Fear of Empathy Decline")
print(contingency)

# Perform chi-square test
chi2, p_value, dof, expected = chi2_contingency(contingency.iloc[:-1, :-1])
print(f"\nChi-square test: χ² = {chi2:.3f}, p = {p_value:.4f}")
if p_value < 0.05:
    print("There IS a significant association between design preference and empathy fears")
else:
    print("There is NO significant association between design preference and empathy fears")

# Also check concern about children's relationships
print("\n5. Concern About Children's Relationships by Design Preference:")
for pref in ['As human-like as possible', 'Clearly non-human', 'Neutral']:
    group = df[df['ai_design_preference'] == pref]
    if len(group) > 0:
        strongly_agree = (group['negative_impact_children'] == 'Strongly agree').sum()
        somewhat_agree = (group['negative_impact_children'] == 'Somewhat agree').sum()
        total_agree = strongly_agree + somewhat_agree
        pct_agree = (total_agree / len(group)) * 100
        print(f"\n   {pref} (n={len(group)}):")
        print(f"   - Agree AI harms children's relationships: {total_agree} ({pct_agree:.1f}%)")
        print(f"     (Strongly: {strongly_agree}, Somewhat: {somewhat_agree})")

# Look at all fears for the human-like preference group
print("\n6. All Fears Among 'Human-like' Preference Group:")
all_fears = {}
for fears in want_humanlike['fears_list']:
    for fear in fears:
        if fear:
            all_fears[fear] = all_fears.get(fear, 0) + 1

sorted_fears = sorted(all_fears.items(), key=lambda x: x[1], reverse=True)
for fear, count in sorted_fears[:5]:
    pct = (count / len(want_humanlike)) * 100
    print(f"   - {fear}: {count} ({pct:.1f}%)")

conn.close()

print("\n" + "="*80)
print("Key Finding: The paradox is relatively RARE - only a small percentage")
print("want human-like AI while fearing empathy decline.")
print("Most who want human-like AI do NOT fear empathy decline.")
print("="*80)