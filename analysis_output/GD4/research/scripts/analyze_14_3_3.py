import sqlite3
import pandas as pd
import numpy as np
import json
from scipy.stats import f_oneway, kruskal

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Section 14.3.3: Human Exceptionalism Scores by Religious Affiliation
# Is there a significant difference in "Human Exceptionalism" scores 
# (the belief that certain traits are uniquely human) between respondents of different religious affiliations?

print("\n" + "="*80)
print("14.3.3 Human Exceptionalism Scores by Religious Affiliation")
print("="*80)

# Get participant data
query = """
SELECT 
    pr.participant_id,
    pr.Q6 as religion,  -- Religious affiliation
    pr.Q96 as uniquely_human_traits,  -- JSON array of traits only humans can fulfill
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q7 as country,
    pr.Q67 as ai_companionship,
    pr.Q97 as romantic_ai_openness,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# Parse the uniquely human traits JSON
def parse_traits(traits_str):
    if pd.isna(traits_str) or traits_str == '' or traits_str == 'null':
        return []
    try:
        traits = json.loads(traits_str)
        if isinstance(traits, list):
            return traits
        return []
    except:
        # Sometimes it's a simple string
        if isinstance(traits_str, str) and traits_str != '':
            return [traits_str]
        return []

df['traits_list'] = df['uniquely_human_traits'].apply(parse_traits)

# Calculate Human Exceptionalism Score (number of traits selected)
df['exceptionalism_score'] = df['traits_list'].apply(len)

# 1. Overall distribution of scores
print("\n1. Human Exceptionalism Score Distribution:")
score_counts = df['exceptionalism_score'].value_counts().sort_index()
for score, count in score_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {score} traits: {count} participants ({pct:.1f}%)")

print(f"\n   Mean score: {df['exceptionalism_score'].mean():.2f} traits")
print(f"   Median score: {df['exceptionalism_score'].median():.0f} traits")
print(f"   Std deviation: {df['exceptionalism_score'].std():.2f}")

# 2. Religious affiliation distribution
print("\n2. Religious Affiliation Distribution:")
religion_counts = df['religion'].value_counts()
for religion, count in religion_counts.items():
    if pd.notna(religion):
        pct = (count / len(df)) * 100
        print(f"   {religion}: {count} ({pct:.1f}%)")

# 3. Exceptionalism scores by religion
print("\n3. Human Exceptionalism Scores by Religious Affiliation:")
religions = df['religion'].dropna().unique()
religion_scores = {}

for religion in religions:
    religion_df = df[df['religion'] == religion]
    if len(religion_df) >= 10:  # Only analyze religions with at least 10 respondents
        mean_score = religion_df['exceptionalism_score'].mean()
        median_score = religion_df['exceptionalism_score'].median()
        std_score = religion_df['exceptionalism_score'].std()
        religion_scores[religion] = {
            'mean': mean_score,
            'median': median_score,
            'std': std_score,
            'n': len(religion_df)
        }
        print(f"\n   {religion} (n={len(religion_df)}):")
        print(f"   - Mean: {mean_score:.2f} traits")
        print(f"   - Median: {median_score:.0f} traits")
        print(f"   - Std Dev: {std_score:.2f}")

# 4. Statistical test (ANOVA or Kruskal-Wallis)
print("\n4. Statistical Test for Differences Between Religions:")

# Prepare data for test (only religions with n>=10)
religion_groups = []
religion_names = []
for religion in religions:
    religion_df = df[df['religion'] == religion]
    if len(religion_df) >= 10:
        religion_groups.append(religion_df['exceptionalism_score'].values)
        religion_names.append(religion)

if len(religion_groups) >= 3:
    # Kruskal-Wallis test (non-parametric, doesn't assume normal distribution)
    h_stat, p_value = kruskal(*religion_groups)
    print(f"   Kruskal-Wallis H-test:")
    print(f"   H = {h_stat:.3f}, p = {p_value:.4f}")
    
    if p_value < 0.001:
        print("   Highly significant differences between religious groups")
    elif p_value < 0.05:
        print("   Significant differences between religious groups")
    else:
        print("   No significant differences between religious groups")
    
    # Also run ANOVA for comparison
    f_stat, p_value_anova = f_oneway(*religion_groups)
    print(f"\n   One-way ANOVA (for comparison):")
    print(f"   F = {f_stat:.3f}, p = {p_value_anova:.4f}")

# 5. Ranking religions by exceptionalism
print("\n5. Religions Ranked by Human Exceptionalism (highest to lowest):")
sorted_religions = sorted(religion_scores.items(), key=lambda x: x[1]['mean'], reverse=True)
for i, (religion, scores) in enumerate(sorted_religions, 1):
    print(f"   {i}. {religion}: {scores['mean']:.2f} traits (n={scores['n']})")

# 6. Most common uniquely human traits by religion
print("\n6. Most Common 'Uniquely Human' Traits by Top Religions:")
top_religions = [r[0] for r in sorted_religions[:3]]  # Top 3 religions by exceptionalism

for religion in top_religions:
    religion_df = df[df['religion'] == religion]
    all_traits = {}
    for traits in religion_df['traits_list']:
        for trait in traits:
            if trait and trait != 'None of the above':
                all_traits[trait] = all_traits.get(trait, 0) + 1
    
    print(f"\n   {religion} - Top 3 traits:")
    sorted_traits = sorted(all_traits.items(), key=lambda x: x[1], reverse=True)
    for trait, count in sorted_traits[:3]:
        pct = (count / len(religion_df)) * 100
        print(f"   - {trait}: {pct:.1f}%")

# 7. Believers vs Non-believers
print("\n7. Believers vs Non-Believers Comparison:")
# Group into believers (any religion) vs non-believers
believers = df[~df['religion'].isin(['Atheist', 'Agnostic', 'None', 'No religious affiliation'])]
non_believers = df[df['religion'].isin(['Atheist', 'Agnostic', 'None', 'No religious affiliation'])]

if len(believers) > 0 and len(non_believers) > 0:
    believers_mean = believers['exceptionalism_score'].mean()
    non_believers_mean = non_believers['exceptionalism_score'].mean()
    
    print(f"   Believers (n={len(believers)}): {believers_mean:.2f} traits")
    print(f"   Non-believers (n={len(non_believers)}): {non_believers_mean:.2f} traits")
    print(f"   Difference: {believers_mean - non_believers_mean:+.2f} traits")
    
    # T-test
    from scipy.stats import ttest_ind
    t_stat, p_value_t = ttest_ind(believers['exceptionalism_score'], non_believers['exceptionalism_score'])
    print(f"   T-test: t = {t_stat:.3f}, p = {p_value_t:.4f}")
    
    if p_value_t < 0.05:
        print("   Significant difference between believers and non-believers")

# 8. Correlation with AI acceptance
print("\n8. Exceptionalism vs AI Acceptance (by religion):")
for religion in sorted_religions[:3]:
    religion_name = religion[0]
    religion_df = df[df['religion'] == religion_name]
    
    # Check correlation with AI companionship use
    companions = religion_df[religion_df['ai_companionship'] == 'Yes']
    non_companions = religion_df[religion_df['ai_companionship'] == 'No']
    
    if len(companions) > 0 and len(non_companions) > 0:
        comp_mean = companions['exceptionalism_score'].mean()
        non_comp_mean = non_companions['exceptionalism_score'].mean()
        print(f"\n   {religion_name}:")
        print(f"   - AI users: {comp_mean:.2f} traits")
        print(f"   - Non-users: {non_comp_mean:.2f} traits")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: ")
if len(religion_scores) > 0:
    highest = sorted_religions[0]
    lowest = sorted_religions[-1]
    print(f"{highest[0]} shows highest human exceptionalism ({highest[1]['mean']:.2f} traits)")
    print(f"while {lowest[0]} shows lowest ({lowest[1]['mean']:.2f} traits).")
    if 'p_value' in locals() and p_value < 0.05:
        print(f"These differences are statistically significant (p = {p_value:.4f}).")
print("="*80)