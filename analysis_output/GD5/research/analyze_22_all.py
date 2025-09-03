#!/usr/bin/env python3
"""
Section 22: Emotion, Imagination, and Wonder - All Questions
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get all relevant data
df = pd.read_sql_query("""
SELECT 
    participant_id,
    Q2 as age,
    Q6 as religion,
    Q48 as imagine_umwelt,
    Q54 as ai_translation_feelings,
    Q45 as emotional_response,
    Q82 as restrict_to_professionals,
    Q83 as everyone_should_listen,
    Q77 as democratic_participation
FROM participant_responses
""", conn)

print("=== SECTION 22: EMOTION, IMAGINATION, AND WONDER ===\n")

# === QUESTION 22.1: UMWELT IMAGINATION AND HOPE ===
print("=== 22.1: UMWELT IMAGINATION AND HOPE ===")

# Categorize imagination frequency
df['often_imagines'] = df['imagine_umwelt'].isin(['Yes, Often', 'Yes, sometimes'])

# Check if Q54 contains "Hopeful"
df['feels_hopeful'] = df['ai_translation_feelings'].str.contains('Hopeful', case=False, na=False)

# Compare hopefulness by imagination frequency
often_hope = df[df['often_imagines']]['feels_hopeful'].mean() * 100
rarely_hope = df[~df['often_imagines']]['feels_hopeful'].mean() * 100

print(f"Often imagine umwelt: {df['often_imagines'].sum()} respondents")
print(f"  Hopeful about AI translation: {often_hope:.1f}%")
print(f"Rarely/Never imagine: {(~df['often_imagines']).sum()} respondents")
print(f"  Hopeful about AI translation: {rarely_hope:.1f}%")

# Statistical test
contingency = pd.crosstab(df['often_imagines'], df['feels_hopeful'])
chi2, p_value, dof, expected = chi2_contingency(contingency)
print(f"Chi-square test: p={p_value:.6f} {'(SIGNIFICANT)' if p_value < 0.05 else '(not significant)'}")

# === QUESTION 22.2: UNSETTLED FEELINGS AND RESTRICTIONS ===
print("\n=== 22.2: UNSETTLED FEELINGS AND RESTRICTIONS ===")

df['feels_unsettled'] = df['emotional_response'].str.contains('Unsettled', case=False, na=False)

print(f"Feels unsettled: {df['feels_unsettled'].sum()} respondents")

# Convert restriction questions to support/oppose
def supports_restriction(val):
    if pd.isna(val) or val == '--':
        return np.nan
    return 'agree' in str(val).lower()

df['supports_restrict_prof'] = df['restrict_to_professionals'].apply(supports_restriction)
df['supports_open_access'] = df['everyone_should_listen'].apply(supports_restriction)

# Compare restriction support
if df['feels_unsettled'].sum() > 0:
    unsettled_restrict = df[df['feels_unsettled']]['supports_restrict_prof'].mean() * 100
    other_restrict = df[~df['feels_unsettled']]['supports_restrict_prof'].mean() * 100
    
    unsettled_open = df[df['feels_unsettled']]['supports_open_access'].mean() * 100
    other_open = df[~df['feels_unsettled']]['supports_open_access'].mean() * 100
    
    print(f"\nQ82 - Restrict to professionals:")
    print(f"  Unsettled: {unsettled_restrict:.1f}% support")
    print(f"  Others: {other_restrict:.1f}% support")
    
    print(f"\nQ83 - Everyone should listen:")
    print(f"  Unsettled: {unsettled_open:.1f}% support")
    print(f"  Others: {other_open:.1f}% support")
else:
    print("No unsettled respondents found")

# === QUESTION 22.3: CURIOSITY AND POLITICAL RADICALISM ===
print("\n=== 22.3: CURIOSITY AND POLITICAL RADICALISM ===")

df['feels_curious'] = df['emotional_response'].str.contains('Curious', case=False, na=False)

# Check support for animal voting (Q77)
df['supports_voting'] = df['democratic_participation'].str.contains('Yes', case=False, na=False)

curious_count = df['feels_curious'].sum()
curious_voting = df[df['feels_curious']]['supports_voting'].mean() * 100
other_voting = df[~df['feels_curious']]['supports_voting'].mean() * 100

print(f"Curious respondents: {curious_count}")
print(f"  Support animal voting: {curious_voting:.1f}%")
print(f"Others: {(~df['feels_curious']).sum()}")
print(f"  Support animal voting: {other_voting:.1f}%")

# Detailed voting breakdown for curious group
if curious_count > 0:
    curious_q77 = df[df['feels_curious']]['democratic_participation'].value_counts(normalize=True).head(3) * 100
    print("\nTop Q77 responses among curious:")
    for response, pct in curious_q77.items():
        if pd.notna(response) and response != '--':
            print(f"  {str(response)[:60]}...: {pct:.1f}%")

# === QUESTION 22.4: WONDER DIMINISHMENT DEMOGRAPHICS ===
print("\n=== 22.4: WONDER DIMINISHMENT DEMOGRAPHICS ===")

# Identify skeptical/concerned about AI translation
df['skeptical_concerned'] = (
    df['ai_translation_feelings'].str.contains('Skeptical', case=False, na=False) |
    df['ai_translation_feelings'].str.contains('Concerned', case=False, na=False)
)

print(f"Skeptical/Concerned about AI translation: {df['skeptical_concerned'].sum()} total")

# By religion
print("\nBy Religion (top groups):")
religion_groups = df.groupby('religion')['skeptical_concerned'].agg(['mean', 'count'])
religion_groups['percentage'] = religion_groups['mean'] * 100
religion_groups = religion_groups[religion_groups['count'] >= 10]  # Filter small groups
religion_groups = religion_groups.sort_values('percentage', ascending=False).head(5)

for religion, row in religion_groups.iterrows():
    if pd.notna(religion) and religion != '--':
        print(f"  {religion}: {row['percentage']:.1f}% (n={row['count']:.0f})")

# By age
print("\nBy Age Group:")
age_mapping = {
    '18-25': '18-25',
    '26-35': '26-35', 
    '36-45': '36-45',
    '46-55': '46-55',
    '56-65': '56+',
    '66+': '56+'
}

df['age_group'] = df['age'].map(age_mapping)
age_groups = df.groupby('age_group')['skeptical_concerned'].agg(['mean', 'count'])
age_groups['percentage'] = age_groups['mean'] * 100

for age, row in age_groups.iterrows():
    if pd.notna(age):
        print(f"  {age}: {row['percentage']:.1f}% (n={row['count']:.0f})")

# Check if there's a pattern
print("\nOverall skeptical/concerned rate: {:.1f}%".format(df['skeptical_concerned'].mean() * 100))

conn.close()