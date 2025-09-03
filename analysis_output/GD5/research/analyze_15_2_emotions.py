#!/usr/bin/env python3
"""
Section 15.2: Emotional Response and Restrictions
Does feeling "unsettled" (Q45) predict stronger support for restrictions (Q82-85)?
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

df = pd.read_sql_query("""
SELECT 
    participant_id,
    Q45 as emotional_response,
    Q82 as restrict_to_professionals,
    Q83 as everyone_should_listen,
    Q84 as regulate_companies,
    Q85 as prohibit_harmful_uses
FROM participant_responses
""", conn)

print("=== Q45: EMOTIONAL RESPONSES ===")
print(df['emotional_response'].value_counts().head(15))

# Categorize emotional responses
def categorize_emotion(val):
    if pd.isna(val) or val == '--':
        return 'No response'
    val_lower = str(val).lower()
    
    if 'unsettled' in val_lower:
        return 'Unsettled'
    elif 'curious' in val_lower:
        return 'Curious'
    elif 'connected' in val_lower:
        return 'Connected'
    elif 'protective' in val_lower:
        return 'Protective'
    elif 'unchanged' in val_lower:
        return 'Unchanged'
    elif 'surprised' in val_lower:
        return 'Surprised'
    else:
        return 'Other'

df['emotion_category'] = df['emotional_response'].apply(categorize_emotion)

# Create groups for comparison
df['feels_unsettled'] = df['emotional_response'].str.contains('Unsettled', case=False, na=False)
df['feels_curious'] = df['emotional_response'].str.contains('Curious', case=False, na=False)
df['feels_connected'] = df['emotional_response'].str.contains('Connected', case=False, na=False)

print("\n=== EMOTION GROUPS ===")
print(f"Feels unsettled: {df['feels_unsettled'].sum()} ({df['feels_unsettled'].mean()*100:.1f}%)")
print(f"Feels curious: {df['feels_curious'].sum()} ({df['feels_curious'].mean()*100:.1f}%)")
print(f"Feels connected: {df['feels_connected'].sum()} ({df['feels_connected'].mean()*100:.1f}%)")

# Convert Likert to numeric
def likert_to_numeric(val):
    if pd.isna(val) or val == '--':
        return np.nan
    val_lower = str(val).lower()
    if 'strongly agree' in val_lower:
        return 5
    elif 'somewhat agree' in val_lower:
        return 4
    elif 'neutral' in val_lower:
        return 3
    elif 'somewhat disagree' in val_lower:
        return 2
    elif 'strongly disagree' in val_lower:
        return 1
    return np.nan

# Analyze Q82-84 for each emotion group
for col, label in [
    ('restrict_to_professionals', 'Q82: Restrict to professionals'),
    ('everyone_should_listen', 'Q83: Everyone should listen (reverse)'),
    ('regulate_companies', 'Q84: Regulate companies')
]:
    df[f'{col}_numeric'] = df[col].apply(likert_to_numeric)
    
    print(f"\n=== {label} ===")
    
    # Compare unsettled vs curious vs connected
    unsettled_vals = df[df['feels_unsettled']][f'{col}_numeric'].dropna()
    curious_vals = df[df['feels_curious']][f'{col}_numeric'].dropna()
    connected_vals = df[df['feels_connected']][f'{col}_numeric'].dropna()
    
    if len(unsettled_vals) > 0:
        print(f"Unsettled group (n={len(unsettled_vals)}):")
        print(f"  Mean agreement: {unsettled_vals.mean():.2f}")
        print(f"  % Agree (4-5): {(unsettled_vals >= 4).mean()*100:.1f}%")
    
    if len(curious_vals) > 0:
        print(f"Curious group (n={len(curious_vals)}):")
        print(f"  Mean agreement: {curious_vals.mean():.2f}")
        print(f"  % Agree (4-5): {(curious_vals >= 4).mean()*100:.1f}%")
    
    if len(connected_vals) > 0:
        print(f"Connected group (n={len(connected_vals)}):")
        print(f"  Mean agreement: {connected_vals.mean():.2f}")
        print(f"  % Agree (4-5): {(connected_vals >= 4).mean()*100:.1f}%")
    
    # Statistical test: Unsettled vs Curious
    if len(unsettled_vals) > 0 and len(curious_vals) > 0:
        stat, p_value = mannwhitneyu(unsettled_vals, curious_vals, alternative='two-sided')
        print(f"\nUnsettled vs Curious: p={p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else ''}")

# Q85: Count prohibited uses
def count_prohibitions(val):
    if pd.isna(val) or val == '--':
        return 0
    return str(val).count(',') + 1 if ',' in str(val) else 1

df['prohibition_count'] = df['prohibit_harmful_uses'].apply(count_prohibitions)

print(f"\n=== Q85: NUMBER OF PROHIBITED USES ===")
unsettled_prohibit = df[df['feels_unsettled']]['prohibition_count']
curious_prohibit = df[df['feels_curious']]['prohibition_count']
connected_prohibit = df[df['feels_connected']]['prohibition_count']

print(f"Unsettled group: {unsettled_prohibit.mean():.2f} prohibitions")
print(f"Curious group: {curious_prohibit.mean():.2f} prohibitions")
print(f"Connected group: {connected_prohibit.mean():.2f} prohibitions")

if len(unsettled_prohibit) > 0 and len(curious_prohibit) > 0:
    stat, p_value = mannwhitneyu(unsettled_prohibit, curious_prohibit, alternative='two-sided')
    print(f"\nUnsettled vs Curious prohibition count: p={p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else ''}")

conn.close()