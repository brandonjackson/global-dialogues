#!/usr/bin/env python3
"""
Section 15.3: Emotions and Radical Governance
Section 15.4: Wonder and Personal Use
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get data for both questions
df = pd.read_sql_query("""
SELECT 
    participant_id,
    Q45 as emotional_response,
    Q76 as ecocentric_society,
    Q77 as democratic_participation,
    Q54 as ai_translation_feelings,
    Q55 as interest_in_communication,
    Q56 as personal_use_interest
FROM participant_responses
""", conn)

# === QUESTION 15.3: EMOTIONS AND RADICAL GOVERNANCE ===
print("=== 15.3: EMOTIONS PREDICTIVE OF RADICAL GOVERNANCE ===")

# Categorize emotions
df['feels_curious'] = df['emotional_response'].str.contains('Curious', case=False, na=False)
df['feels_connected'] = df['emotional_response'].str.contains('Connected', case=False, na=False)
df['feels_protective'] = df['emotional_response'].str.contains('Protective', case=False, na=False)
df['feels_unchanged'] = df['emotional_response'].str.contains('Unchanged', case=False, na=False)
df['feels_surprised'] = df['emotional_response'].str.contains('Surprised', case=False, na=False)

# Q76: Ecocentric society appeal by emotion
print("\n--- Q76: ECOCENTRIC AI SOCIETY APPEAL BY EMOTION ---")

for emotion, label in [
    ('feels_curious', 'Curious'),
    ('feels_connected', 'Connected'),
    ('feels_protective', 'Protective'),
    ('feels_unchanged', 'Unchanged'),
    ('feels_surprised', 'Surprised')
]:
    emotion_group = df[df[emotion]]
    if len(emotion_group) > 0:
        eco_dist = emotion_group['ecocentric_society'].value_counts(normalize=True) * 100
        very_appealing = eco_dist.get('Very appealing', 0)
        somewhat_appealing = eco_dist.get('Somewhat appealing', 0)
        total_appealing = very_appealing + somewhat_appealing
        
        print(f"\n{label} (n={len(emotion_group)}):")
        print(f"  Very appealing: {very_appealing:.1f}%")
        print(f"  Total appealing: {total_appealing:.1f}%")

# Q77: Democratic participation by emotion
print("\n--- Q77: DEMOCRATIC PARTICIPATION SUPPORT BY EMOTION ---")

# Simplify democratic participation to support vs oppose
def support_democracy(val):
    if pd.isna(val) or val == '--':
        return np.nan
    val_lower = str(val).lower()
    if 'no, they should not' in val_lower:
        return False
    elif 'yes' in val_lower:
        return True
    return np.nan

df['supports_democracy'] = df['democratic_participation'].apply(support_democracy)

for emotion, label in [
    ('feels_curious', 'Curious'),
    ('feels_connected', 'Connected'),
    ('feels_protective', 'Protective'),
    ('feels_unchanged', 'Unchanged')
]:
    emotion_group = df[df[emotion]]
    support_rate = emotion_group['supports_democracy'].mean() * 100
    print(f"{label}: {support_rate:.1f}% support animal democratic participation")

# Statistical test for most predictive emotion
eco_appeal_by_connected = pd.crosstab(df['feels_connected'], df['ecocentric_society'])
chi2, p_value, dof, expected = chi2_contingency(eco_appeal_by_connected)
print(f"\nConnected emotion -> Ecocentric society: p={p_value:.6f} {'(SIGNIFICANT)' if p_value < 0.05 else ''}")

# === QUESTION 15.4: WONDER AND PERSONAL USE ===
print("\n\n=== 15.4: WONDER AND PERSONAL USE ===")

print("\nQ54 AI Translation Feelings distribution:")
print(df['ai_translation_feelings'].value_counts())

# Identify those concerned about diminishing wonder
df['concerned_wonder'] = df['ai_translation_feelings'].isin(['Concerned', 'Skeptical'])

concerned_group = df[df['concerned_wonder']]
not_concerned_group = df[~df['concerned_wonder']]

print(f"\nConcerned/Skeptical about wonder: {len(concerned_group)} ({len(concerned_group)/len(df)*100:.1f}%)")

# Q55: Interest in knowing what animals say
print("\n--- Q55: INTEREST IN COMMUNICATION ---")

concerned_interest = concerned_group['interest_in_communication'].value_counts(normalize=True) * 100
other_interest = not_concerned_group['interest_in_communication'].value_counts(normalize=True) * 100

print("\nConcerned/Skeptical group:")
for val, pct in concerned_interest.head(3).items():
    if pd.notna(val) and val != '--':
        print(f"  {val}: {pct:.1f}%")

print("\nNot concerned group:")
for val, pct in other_interest.head(3).items():
    if pd.notna(val) and val != '--':
        print(f"  {val}: {pct:.1f}%")

# Calculate total interest
def is_interested(val):
    if pd.isna(val) or val == '--':
        return False
    return val in ['Very interested', 'Somewhat interested']

concerned_interested = concerned_group['interest_in_communication'].apply(is_interested).mean() * 100
other_interested = not_concerned_group['interest_in_communication'].apply(is_interested).mean() * 100

print(f"\nTotal interested (Very + Somewhat):")
print(f"  Concerned/Skeptical: {concerned_interested:.1f}%")
print(f"  Not concerned: {other_interested:.1f}%")

# Q56: Personal use interest
print("\n--- Q56: PERSONAL USE INTEREST ---")

concerned_personal = concerned_group['personal_use_interest'].value_counts(normalize=True) * 100
other_personal = not_concerned_group['personal_use_interest'].value_counts(normalize=True) * 100

print("\nConcerned/Skeptical group would use personally:")
for val, pct in concerned_personal.head(3).items():
    if pd.notna(val) and val != '--':
        print(f"  {str(val)[:60]}...: {pct:.1f}%")

print("\nNot concerned group would use personally:")
for val, pct in other_personal.head(3).items():
    if pd.notna(val) and val != '--':
        print(f"  {str(val)[:60]}...: {pct:.1f}%")

print(f"\n=== KEY FINDING ===")
print(f"Despite concerns about diminishing wonder, {concerned_interested:.1f}% of concerned/skeptical")
print(f"respondents are still interested in animal communication.")

conn.close()