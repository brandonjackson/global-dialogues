#!/usr/bin/env python3
"""
Section 25: The Survey as an Intervention — Measuring Opinion Shifts
Comparing Q33 (initial belief) with Q93/Q94 (final questions) to detect belief changes
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("=" * 80)
print("SECTION 25: THE SURVEY AS AN INTERVENTION — MEASURING OPINION SHIFTS")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get participant responses with reliable PRI scores
query = """
SELECT pr.*, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
df = pd.read_sql_query(query, conn)
print(f"\nTotal reliable participants: {len(df)}")

print("\n" + "=" * 80)
print("Question 25.1: Belief Change Measurement")
print("=" * 80)

# Q33 appears to be the initial belief question (open-ended explaining their view)
# Q93 and Q94 are the final questions about human-nature relationship and superiority

# Since Q33 is open-ended and Q93/94 are likely structured differently,
# we need to check if participants maintain consistency

# First, let's examine Q93 and Q94 content
print("\nExamining Q93 (final human-nature question):")
if 'Q93' in df.columns:
    q93_values = df['Q93'].value_counts()
    print(f"Total responses: {df['Q93'].notna().sum()}")
    for val, count in q93_values.head(5).items():
        print(f"  {val}: {count}")

print("\nExamining Q94 (final superiority question):")
if 'Q94' in df.columns:
    q94_values = df['Q94'].value_counts()
    print(f"Total responses: {df['Q94'].notna().sum()}")
    for val, count in q94_values.head(5).items():
        print(f"  {val}: {count}")

# Since we don't have paired initial questions in the same format,
# we'll analyze Q33 (initial open-ended) sentiment and compare with Q94 (final structured)

# Categorize Q33 responses
def categorize_belief_q33(response):
    if pd.isna(response) or response == '--':
        return 'Unknown'
    response_lower = str(response).lower()
    if 'equal' in response_lower:
        return 'Equal'
    elif 'superior' in response_lower or 'better' in response_lower or 'advanced' in response_lower:
        return 'Superior'
    elif 'different' in response_lower:
        return 'Different'
    else:
        return 'Other'

# Categorize Q94 responses
def categorize_belief_q94(response):
    if pd.isna(response):
        return 'Unknown'
    response_lower = str(response).lower()
    if 'equal' in response_lower:
        return 'Equal'
    elif 'superior' in response_lower:
        return 'Superior'
    elif 'inferior' in response_lower:
        return 'Inferior'
    elif 'different' in response_lower:
        return 'Different'
    else:
        return 'Other'

df['Q33_category'] = df['Q33'].apply(categorize_belief_q33)
df['Q94_category'] = df['Q94'].apply(categorize_belief_q94)

# Compare categories
comparison = df[['participant_id', 'Q33_category', 'Q94_category']].copy()
comparison = comparison[(comparison['Q33_category'] != 'Unknown') & (comparison['Q94_category'] != 'Unknown')]

print(f"\n**Belief Categories Comparison (Q33 initial → Q94 final):**")
print(f"Participants with valid responses in both: {len(comparison)}")

# Check for category changes
comparison['changed'] = comparison['Q33_category'] != comparison['Q94_category']
changed_count = comparison['changed'].sum()
changed_pct = (changed_count / len(comparison) * 100) if len(comparison) > 0 else 0

print(f"Changed their category: {changed_count} ({changed_pct:.1f}%)")

if changed_count > 0:
    print("\nCategory shifts:")
    shifts = comparison[comparison['changed']].groupby(['Q33_category', 'Q94_category']).size()
    for (initial, final), count in shifts.items():
        pct_of_changes = (count / changed_count * 100)
        print(f"  {initial} → {final}: {count} ({pct_of_changes:.1f}%)")

# Store mind-changers for further analysis
mind_changers = comparison[comparison['changed']]['participant_id'].tolist()

print("\n" + "=" * 80)
print("Question 25.2: Emotional Response and Mind Change")
print("=" * 80)

# Analyze Q44 (impact of facts) and Q45 (emotions) for changers vs non-changers
changers_df = df[df['participant_id'].isin(mind_changers)]
non_changers_df = df[~df['participant_id'].isin(mind_changers) & 
                     df['participant_id'].isin(comparison['participant_id'])]

print(f"\nAnalyzing {len(changers_df)} mind-changers vs {len(non_changers_df)} non-changers")

# Q44: Impact of scientific facts
print("\n**Impact of Scientific Facts (Q44):**")
if 'Q44' in df.columns:
    # Mind-changers
    changers_impact = changers_df['Q44'].value_counts(normalize=True) * 100
    print("\nMind-changers' reported impact:")
    for impact, pct in changers_impact.head().items():
        print(f"  {impact}: {pct:.1f}%")
    
    # Non-changers
    non_changers_impact = non_changers_df['Q44'].value_counts(normalize=True) * 100
    print("\nNon-changers' reported impact:")
    for impact, pct in non_changers_impact.head().items():
        print(f"  {impact}: {pct:.1f}%")
    
    # Check "great deal" impact
    great_impact_changers = (changers_df['Q44'] == 'A great deal').sum()
    great_impact_non_changers = (non_changers_df['Q44'] == 'A great deal').sum()
    
    if len(changers_df) > 0 and len(non_changers_df) > 0:
        great_pct_changers = (great_impact_changers / len(changers_df) * 100)
        great_pct_non_changers = (great_impact_non_changers / len(non_changers_df) * 100)
        
        print(f"\n'A great deal' of impact:")
        print(f"  Changers: {great_pct_changers:.1f}%")
        print(f"  Non-changers: {great_pct_non_changers:.1f}%")
        
        # Chi-square test
        contingency = pd.crosstab(
            pd.Series(['Changer'] * len(changers_df) + ['Non-changer'] * len(non_changers_df)),
            pd.concat([changers_df['Q44'], non_changers_df['Q44']])
        )
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"\nChi-square test: χ²={chi2:.2f}, p={p_value:.4f}")

# Q45: Emotional response (multi-select)
print("\n**Emotional Response (Q45):**")
if 'Q45' in df.columns:
    # Parse emotions from multi-select
    emotions_list = ['Curious', 'Connected', 'Protective', 'Hopeful', 'Concerned', 
                     'Skeptical', 'Unsettled', 'Overwhelmed', 'Excited']
    
    def count_emotions(df_subset, label):
        emotion_counts = {}
        for emotion in emotions_list:
            count = df_subset['Q45'].str.contains(emotion, case=False, na=False).sum()
            emotion_counts[emotion] = count
        
        total = len(df_subset)
        print(f"\n{label} (N={total}):")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                pct = (count / total * 100)
                print(f"  {emotion}: {count} ({pct:.1f}%)")
        return emotion_counts
    
    changers_emotions = count_emotions(changers_df, "Mind-changers' emotions")
    non_changers_emotions = count_emotions(non_changers_df, "Non-changers' emotions")
    
    # Check specifically for Connected/Protective
    if len(changers_df) > 0 and len(non_changers_df) > 0:
        connected_protective_changers = (
            changers_df['Q45'].str.contains('Connected|Protective', case=False, na=False).sum()
        )
        connected_protective_non_changers = (
            non_changers_df['Q45'].str.contains('Connected|Protective', case=False, na=False).sum()
        )
        
        cp_pct_changers = (connected_protective_changers / len(changers_df) * 100)
        cp_pct_non_changers = (connected_protective_non_changers / len(non_changers_df) * 100)
        
        print(f"\n**Connected or Protective emotions:**")
        print(f"  Changers: {cp_pct_changers:.1f}%")
        print(f"  Non-changers: {cp_pct_non_changers:.1f}%")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n**Key Finding:**")
print(f"- {changed_pct:.1f}% of participants showed belief category changes during the survey")

if 'Q44' in df.columns and len(changers_df) > 0 and len(non_changers_df) > 0:
    print(f"- Mind-changers were {great_pct_changers/great_pct_non_changers:.1f}x more likely to report 'great deal' of impact from facts")

if 'Q45' in df.columns and len(changers_df) > 0 and len(non_changers_df) > 0:
    print(f"- {cp_pct_changers:.1f}% of mind-changers felt Connected/Protective vs {cp_pct_non_changers:.1f}% of non-changers")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)