#!/usr/bin/env python3
"""
Analyze correlation between loneliness scores and AI emotional support usage
for GD4 Investigation Question 5.2
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import json

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Get participant data with loneliness questions and AI usage
query = """
SELECT 
    pr.participant_id,
    pr.Q51, pr.Q52, pr.Q53, pr.Q54, pr.Q55, pr.Q56, pr.Q57, pr.Q58,
    pr.Q17 as emotional_support_freq,
    pr.Q67 as ai_companionship,
    pr.Q70 as ai_made_less_lonely,
    pr.Q65 as ai_activities,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)

# Function to convert loneliness responses to numeric scores
def score_loneliness_item(response, reverse=False):
    """Convert loneliness item response to numeric score (1-4)
    Higher score = more lonely
    """
    if pd.isna(response):
        return np.nan
    
    mapping = {
        'Never': 1,
        'Rarely': 2, 
        'Sometimes': 3,
        'Often': 4,
        'Often/Always': 4,
        'Often / Always': 4
    }
    
    score = mapping.get(response, np.nan)
    
    # Reverse score for positive items
    if reverse and not pd.isna(score):
        score = 5 - score
    
    return score

# Calculate loneliness scores
# Positive items to reverse: Q51, Q55, Q56, Q58
df['Q51_score'] = df['Q51'].apply(lambda x: score_loneliness_item(x, reverse=True))
df['Q52_score'] = df['Q52'].apply(lambda x: score_loneliness_item(x, reverse=False))
df['Q53_score'] = df['Q53'].apply(lambda x: score_loneliness_item(x, reverse=False))
df['Q54_score'] = df['Q54'].apply(lambda x: score_loneliness_item(x, reverse=False))
df['Q55_score'] = df['Q55'].apply(lambda x: score_loneliness_item(x, reverse=True))
df['Q56_score'] = df['Q56'].apply(lambda x: score_loneliness_item(x, reverse=True))
df['Q57_score'] = df['Q57'].apply(lambda x: score_loneliness_item(x, reverse=False))
df['Q58_score'] = df['Q58'].apply(lambda x: score_loneliness_item(x, reverse=True))

# Calculate composite loneliness score (sum of all 8 items)
loneliness_cols = ['Q51_score', 'Q52_score', 'Q53_score', 'Q54_score', 
                   'Q55_score', 'Q56_score', 'Q57_score', 'Q58_score']
df['loneliness_score'] = df[loneliness_cols].sum(axis=1)

# Only keep participants who answered all loneliness questions
df = df[df['loneliness_score'].notna()]

print(f"Total participants with complete loneliness data: {len(df)}")
print(f"Loneliness score range: {df['loneliness_score'].min():.1f} - {df['loneliness_score'].max():.1f}")
print(f"Mean loneliness score: {df['loneliness_score'].mean():.2f} (SD: {df['loneliness_score'].std():.2f})")

# Categorize loneliness levels
df['loneliness_category'] = pd.cut(df['loneliness_score'], 
                                   bins=[0, 16, 24, 32],
                                   labels=['Low (8-16)', 'Moderate (17-24)', 'High (25-32)'])

# Analyze emotional support frequency by loneliness level
print("\n=== Emotional Support Frequency by Loneliness Level ===")
support_freq_order = ['never', 'annually', 'monthly', 'weekly', 'daily']

for category in ['Low (8-16)', 'Moderate (17-24)', 'High (25-32)']:
    cat_data = df[df['loneliness_category'] == category]
    total = len(cat_data)
    print(f"\n{category} Loneliness (n={total}):")
    
    # Calculate percentages for each frequency
    freq_counts = cat_data['emotional_support_freq'].value_counts()
    
    # Daily/Weekly combined
    daily_weekly = 0
    if 'daily' in freq_counts:
        daily_weekly += freq_counts['daily']
    if 'weekly' in freq_counts:
        daily_weekly += freq_counts['weekly']
    
    print(f"  Daily/Weekly emotional support: {daily_weekly}/{total} ({100*daily_weekly/total:.1f}%)")
    
    # Never
    never_count = freq_counts.get('never', 0)
    print(f"  Never used emotional support: {never_count}/{total} ({100*never_count/total:.1f}%)")

# Correlation between loneliness score and emotional support frequency
# Convert frequency to numeric scale
freq_to_numeric = {'never': 0, 'annually': 1, 'monthly': 2, 'weekly': 3, 'daily': 4}
df['support_freq_numeric'] = df['emotional_support_freq'].map(freq_to_numeric)

# Calculate correlation
valid_data = df[df['support_freq_numeric'].notna()]
correlation, p_value = stats.spearmanr(valid_data['loneliness_score'], 
                                       valid_data['support_freq_numeric'])

print(f"\n=== Correlation Analysis ===")
print(f"Spearman correlation between loneliness and emotional support frequency:")
print(f"  r = {correlation:.3f}, p = {p_value:.4f}")

# AI companionship usage by loneliness level
print("\n=== AI Companionship Usage by Loneliness Level ===")
for category in ['Low (8-16)', 'Moderate (17-24)', 'High (25-32)']:
    cat_data = df[df['loneliness_category'] == category]
    total = len(cat_data)
    yes_count = (cat_data['ai_companionship'] == 'Yes').sum()
    print(f"{category}: {yes_count}/{total} ({100*yes_count/total:.1f}%) have used AI companionship")

# Among AI users, does loneliness correlate with feeling less lonely after use?
ai_users = df[df['ai_companionship'] == 'Yes']
print(f"\n=== AI Impact on Loneliness (among {len(ai_users)} AI users) ===")

for category in ['Low (8-16)', 'Moderate (17-24)', 'High (25-32)']:
    cat_users = ai_users[ai_users['loneliness_category'] == category]
    if len(cat_users) > 0:
        print(f"\n{category} Loneliness (n={len(cat_users)} AI users):")
        
        # Count positive responses
        definitely = (cat_users['ai_made_less_lonely'] == 'Yes, definitely').sum()
        somewhat = (cat_users['ai_made_less_lonely'] == 'Yes, somewhat').sum()
        no = (cat_users['ai_made_less_lonely'] == 'No').sum()
        
        total = len(cat_users)
        print(f"  Yes, definitely: {definitely} ({100*definitely/total:.1f}%)")
        print(f"  Yes, somewhat: {somewhat} ({100*somewhat/total:.1f}%)")
        print(f"  No: {no} ({100*no/total:.1f}%)")
        print(f"  Total positive impact: {definitely+somewhat} ({100*(definitely+somewhat)/total:.1f}%)")

# Parse AI activities to see which activities correlate with loneliness
print("\n=== Specific AI Activities by Loneliness Level ===")

def parse_activities(activities_str):
    """Parse the JSON string of activities"""
    if pd.isna(activities_str):
        return []
    try:
        return json.loads(activities_str)
    except:
        return []

df['activities_list'] = df['ai_activities'].apply(parse_activities)

# Key emotional activities to analyze
emotional_activities = [
    'Used AI when feeling lonely',
    'Vented to AI when frustrated',
    'Shared something with AI you wouldn\'t tell others',
    'Asked AI about relationships/dating'
]

for activity in emotional_activities:
    print(f"\n'{activity}':")
    for category in ['Low (8-16)', 'Moderate (17-24)', 'High (25-32)']:
        cat_data = df[df['loneliness_category'] == category]
        total = len(cat_data)
        
        # Count how many have this activity
        has_activity = cat_data['activities_list'].apply(lambda x: activity in x).sum()
        print(f"  {category}: {has_activity}/{total} ({100*has_activity/total:.1f}%)")

# Statistical test: Is there a significant difference in loneliness scores between
# those who use AI for emotional support vs those who don't?
print("\n=== T-Test: Loneliness Scores by AI Companionship Usage ===")
users = df[df['ai_companionship'] == 'Yes']['loneliness_score']
non_users = df[df['ai_companionship'] == 'No']['loneliness_score']

t_stat, p_value = stats.ttest_ind(users, non_users)
print(f"AI Users (n={len(users)}): Mean loneliness = {users.mean():.2f} (SD: {users.std():.2f})")
print(f"Non-Users (n={len(non_users)}): Mean loneliness = {non_users.mean():.2f} (SD: {non_users.std():.2f})")
print(f"t-statistic: {t_stat:.3f}, p-value: {p_value:.4f}")

if p_value < 0.05:
    print("Result: Statistically significant difference in loneliness scores")
else:
    print("Result: No statistically significant difference in loneliness scores")

conn.close()