#!/usr/bin/env python3
"""
Section 17: Surprising Cross-Trust Dynamics
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
print("SECTION 17: SURPRISING CROSS-TRUST DYNAMICS")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get reliable participants
query = """
SELECT pr.*, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
df = pd.read_sql_query(query, conn)
print(f"\nTotal reliable participants: {len(df)}")

# Helper function to convert trust levels to numeric
def trust_to_numeric(val):
    """Convert trust levels to numeric scale 1-5"""
    if pd.isna(val):
        return np.nan
    val_str = str(val).lower()
    if 'strongly distrust' in val_str:
        return 1
    elif 'somewhat distrust' in val_str:
        return 2
    elif 'neither' in val_str:
        return 3
    elif 'somewhat trust' in val_str:
        return 4
    elif 'strongly trust' in val_str:
        return 5
    else:
        return np.nan

print("\n" + "=" * 80)
print("Question 17.1: Global Trust Rankings")
print("=" * 80)

# Q12: Family doctor, Q13: Social media, Q15: Faith leader, Q17: AI chatbot, Q57: AI translator
trust_questions = {
    'Q12': 'Family doctor',
    'Q13': 'Social media',
    'Q15': 'Faith/community leader',
    'Q17': 'AI chatbot',
    'Q57': 'AI animal translator'
}

# Convert trust columns to numeric
for col in trust_questions.keys():
    if col in df.columns:
        df[f'{col}_numeric'] = df[col].apply(trust_to_numeric)

# Calculate mean trust scores
trust_scores = {}
for col, label in trust_questions.items():
    if col in df.columns:
        numeric_col = f'{col}_numeric'
        mean_score = df[numeric_col].mean()
        std_score = df[numeric_col].std()
        count = df[numeric_col].notna().sum()
        trust_scores[label] = {
            'mean': mean_score,
            'std': std_score,
            'count': count
        }

# Sort by mean trust
sorted_trust = sorted(trust_scores.items(), key=lambda x: x[1]['mean'] if not np.isnan(x[1]['mean']) else 0, reverse=True)

print("\n**Global Trust Rankings (1=Strongly Distrust, 5=Strongly Trust):**")
for rank, (entity, scores) in enumerate(sorted_trust, 1):
    print(f"{rank}. {entity}: {scores['mean']:.2f} (SD: {scores['std']:.2f}, N={scores['count']})")

# Focus on the three mentioned in the question
key_entities = ['AI chatbot', 'AI animal translator', 'Faith/community leader']
print("\n**Comparison of Key Entities:**")
for entity in key_entities:
    if entity in trust_scores:
        print(f"- {entity}: {trust_scores[entity]['mean']:.2f}")

# Statistical comparison
if 'Q17_numeric' in df.columns and 'Q57_numeric' in df.columns and 'Q15_numeric' in df.columns:
    # Paired t-tests
    ai_chatbot_vs_translator = stats.ttest_rel(
        df['Q17_numeric'].dropna(),
        df['Q57_numeric'].dropna()
    )
    print(f"\nAI chatbot vs AI translator: t={ai_chatbot_vs_translator.statistic:.2f}, p={ai_chatbot_vs_translator.pvalue:.4f}")

print("\n" + "=" * 80)
print("Question 17.2: AI vs. Doctors Trust")
print("=" * 80)

# Compare AI trust vs doctor trust by demographics
if 'Q12_numeric' in df.columns and 'Q57_numeric' in df.columns:
    # Create comparison column
    df['trusts_ai_more'] = df['Q57_numeric'] > df['Q12_numeric']
    
    # Analyze by age
    print("\n**Demographics where AI is trusted more than doctors:**")
    print("\nBy Age Group:")
    age_analysis = df.groupby('Q2')['trusts_ai_more'].agg(['mean', 'sum', 'count'])
    age_analysis['percentage'] = age_analysis['mean'] * 100
    for age, row in age_analysis.iterrows():
        if row['count'] > 10:  # Only show groups with sufficient data
            print(f"  {age}: {row['percentage']:.1f}% trust AI more ({int(row['sum'])}/{int(row['count'])})")
    
    # By gender
    print("\nBy Gender:")
    gender_analysis = df.groupby('Q3')['trusts_ai_more'].agg(['mean', 'sum', 'count'])
    gender_analysis['percentage'] = gender_analysis['mean'] * 100
    for gender, row in gender_analysis.iterrows():
        if row['count'] > 10:
            print(f"  {gender}: {row['percentage']:.1f}% trust AI more ({int(row['sum'])}/{int(row['count'])})")
    
    # By location
    print("\nBy Location Type:")
    location_analysis = df.groupby('Q4')['trusts_ai_more'].agg(['mean', 'sum', 'count'])
    location_analysis['percentage'] = location_analysis['mean'] * 100
    for location, row in location_analysis.iterrows():
        if row['count'] > 10:
            print(f"  {location}: {row['percentage']:.1f}% trust AI more ({int(row['sum'])}/{int(row['count'])})")
    
    # Overall percentage
    overall_pct = df['trusts_ai_more'].mean() * 100
    print(f"\n**Overall: {overall_pct:.1f}% trust AI translators more than family doctors**")

print("\n" + "=" * 80)
print("Question 17.3: Social Media and AI Distrust")
print("=" * 80)

if 'Q13_numeric' in df.columns and 'Q57_numeric' in df.columns:
    # Define distrust as score <= 2
    df['distrusts_social_media'] = df['Q13_numeric'] <= 2
    df['distrusts_ai_translator'] = df['Q57_numeric'] <= 2
    
    # Create crosstab
    cross_trust = pd.crosstab(
        df['distrusts_social_media'],
        df['distrusts_ai_translator'],
        normalize='index'
    ) * 100
    
    print("\n**Relationship between Social Media and AI Translator Distrust:**")
    print(cross_trust.round(1))
    
    # Calculate correlation
    correlation = df['Q13_numeric'].corr(df['Q57_numeric'])
    print(f"\nCorrelation coefficient: {correlation:.3f}")
    
    # Conditional probabilities
    social_distrusters = df[df['distrusts_social_media']]
    if len(social_distrusters) > 0:
        ai_distrust_rate = social_distrusters['distrusts_ai_translator'].mean() * 100
        print(f"\nAmong social media distrusters:")
        print(f"  - {ai_distrust_rate:.1f}% also distrust AI translators")
        print(f"  - {100-ai_distrust_rate:.1f}% do NOT distrust AI translators (compartmentalization)")
    
    # Compare to overall population
    overall_ai_distrust = df['distrusts_ai_translator'].mean() * 100
    print(f"\nOverall AI translator distrust rate: {overall_ai_distrust:.1f}%")
    
    if len(social_distrusters) > 0:
        lift = (ai_distrust_rate / overall_ai_distrust) if overall_ai_distrust > 0 else 0
        print(f"Lift factor: {lift:.2f}x (social media distrusters are {lift:.2f}x more likely to distrust AI)")

# Additional analysis: Trust patterns
print("\n**Trust Pattern Analysis:**")
if 'Q13_numeric' in df.columns and 'Q57_numeric' in df.columns and 'Q17_numeric' in df.columns:
    # Create trust categories
    df['general_ai_trust'] = (df['Q17_numeric'] + df['Q57_numeric']) / 2
    df['tech_skeptic'] = (df['Q13_numeric'] <= 2) & (df['general_ai_trust'] <= 2.5)
    df['selective_skeptic'] = (df['Q13_numeric'] <= 2) & (df['general_ai_trust'] > 2.5)
    df['general_truster'] = (df['Q13_numeric'] > 3) & (df['general_ai_trust'] > 3)
    
    print(f"Tech skeptics (distrust both): {df['tech_skeptic'].sum()} ({df['tech_skeptic'].mean()*100:.1f}%)")
    print(f"Selective skeptics (distrust social media, not AI): {df['selective_skeptic'].sum()} ({df['selective_skeptic'].mean()*100:.1f}%)")
    print(f"General trusters (trust both): {df['general_truster'].sum()} ({df['general_truster'].mean()*100:.1f}%)")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)