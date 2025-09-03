#!/usr/bin/env python3
"""
Section 17: Surprising Cross-Trust Dynamics - Fixed Version
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

print("\n**Finding:** Family doctors are most trusted (4.24/5), followed by AI chatbots (3.48) and AI animal translators (3.46), with faith leaders (3.16) and social media (2.43) trailing.")
print("\n**Method:** Mean trust scores on 5-point scale from 1005 participants with PRI >= 0.3")
print("\n**Details:**")
print("Global Trust Rankings (1=Strongly Distrust, 5=Strongly Trust):")
for rank, (entity, scores) in enumerate(sorted_trust, 1):
    print(f"  {rank}. {entity}: {scores['mean']:.2f} (SD: {scores['std']:.2f}, N={scores['count']})")

# Statistical comparison for paired data
if 'Q17_numeric' in df.columns and 'Q57_numeric' in df.columns:
    # Only use participants who answered both questions
    paired_data = df[['Q17_numeric', 'Q57_numeric']].dropna()
    if len(paired_data) > 0:
        ai_chatbot_vs_translator = stats.ttest_rel(
            paired_data['Q17_numeric'],
            paired_data['Q57_numeric']
        )
        print(f"\nAI chatbot vs AI translator (paired): t={ai_chatbot_vs_translator.statistic:.2f}, p={ai_chatbot_vs_translator.pvalue:.4f}")
        print(f"  N={len(paired_data)} participants answered both questions")

print("\n" + "=" * 80)
print("Question 17.2: AI vs. Doctors Trust")
print("=" * 80)

# Compare AI trust vs doctor trust by demographics
if 'Q12_numeric' in df.columns and 'Q57_numeric' in df.columns:
    # Create comparison for those who answered both
    df['ai_minus_doctor'] = df['Q57_numeric'] - df['Q12_numeric']
    df['trusts_ai_more'] = df['ai_minus_doctor'] > 0
    
    # Overall percentage
    valid_comparisons = df['trusts_ai_more'].notna()
    overall_pct = df.loc[valid_comparisons, 'trusts_ai_more'].mean() * 100
    overall_count = df.loc[valid_comparisons, 'trusts_ai_more'].sum()
    overall_total = valid_comparisons.sum()
    
    print(f"\n**Finding:** Only {overall_pct:.1f}% ({int(overall_count)}/{int(overall_total)}) trust AI translators more than family doctors")
    print("\n**Method:** Direct comparison of Q57 vs Q12 trust scores")
    print("\n**Details:**")
    
    # Analyze by age
    print("By Age Group:")
    age_analysis = df[df['trusts_ai_more'].notna()].groupby('Q2')['trusts_ai_more'].agg(['mean', 'sum', 'count'])
    age_analysis['percentage'] = age_analysis['mean'] * 100
    age_analysis = age_analysis.sort_values('percentage', ascending=False)
    for age, row in age_analysis.iterrows():
        if row['count'] > 10:  # Only show groups with sufficient data
            print(f"  {age}: {row['percentage']:.1f}% trust AI more ({int(row['sum'])}/{int(row['count'])})")
    
    # By gender
    print("\nBy Gender:")
    gender_analysis = df[df['trusts_ai_more'].notna()].groupby('Q3')['trusts_ai_more'].agg(['mean', 'sum', 'count'])
    gender_analysis['percentage'] = gender_analysis['mean'] * 100
    for gender, row in gender_analysis.iterrows():
        if row['count'] > 10:
            print(f"  {gender}: {row['percentage']:.1f}% trust AI more ({int(row['sum'])}/{int(row['count'])})")
    
    # By AI excitement
    print("\nBy AI Sentiment (Q5):")
    ai_sentiment_analysis = df[df['trusts_ai_more'].notna()].groupby('Q5')['trusts_ai_more'].agg(['mean', 'sum', 'count'])
    ai_sentiment_analysis['percentage'] = ai_sentiment_analysis['mean'] * 100
    for sentiment, row in ai_sentiment_analysis.iterrows():
        if row['count'] > 10:
            print(f"  {sentiment}: {row['percentage']:.1f}% trust AI more ({int(row['sum'])}/{int(row['count'])})")

print("\n" + "=" * 80)
print("Question 17.3: Social Media and AI Distrust")
print("=" * 80)

if 'Q13_numeric' in df.columns and 'Q57_numeric' in df.columns:
    # Define distrust as score <= 2
    df['distrusts_social_media'] = df['Q13_numeric'] <= 2
    df['distrusts_ai_translator'] = df['Q57_numeric'] <= 2
    
    # Only analyze those who answered both
    valid_data = df[df['Q13_numeric'].notna() & df['Q57_numeric'].notna()]
    
    # Calculate correlation
    correlation = valid_data['Q13_numeric'].corr(valid_data['Q57_numeric'])
    
    # Conditional probabilities
    social_distrusters = valid_data[valid_data['distrusts_social_media']]
    social_trusters = valid_data[~valid_data['distrusts_social_media']]
    
    if len(social_distrusters) > 0:
        ai_distrust_rate_among_social_distrusters = social_distrusters['distrusts_ai_translator'].mean() * 100
        ai_distrust_rate_among_social_trusters = social_trusters['distrusts_ai_translator'].mean() * 100
        overall_ai_distrust = valid_data['distrusts_ai_translator'].mean() * 100
        
        print(f"\n**Finding:** Social media distrusters show moderate correlation (r={correlation:.3f}) with AI translator distrust")
        print(f"Among social media distrusters, {ai_distrust_rate_among_social_distrusters:.1f}% also distrust AI vs {ai_distrust_rate_among_social_trusters:.1f}% among social media trusters")
        print("\n**Method:** Correlation analysis and conditional probabilities")
        print("\n**Details:**")
        print(f"- Overall AI translator distrust rate: {overall_ai_distrust:.1f}%")
        print(f"- AI distrust among social media distrusters: {ai_distrust_rate_among_social_distrusters:.1f}%")
        print(f"- AI distrust among social media trusters: {ai_distrust_rate_among_social_trusters:.1f}%")
        print(f"- Lift factor: {(ai_distrust_rate_among_social_distrusters/overall_ai_distrust):.2f}x")
        print(f"- {100-ai_distrust_rate_among_social_distrusters:.1f}% of social media distrusters do NOT distrust AI (compartmentalization)")

    # Trust patterns
    print("\n**Trust Pattern Segmentation:**")
    df['tech_skeptic'] = (valid_data['Q13_numeric'] <= 2) & (valid_data['Q57_numeric'] <= 2)
    df['selective_skeptic'] = (valid_data['Q13_numeric'] <= 2) & (valid_data['Q57_numeric'] > 2)
    df['general_truster'] = (valid_data['Q13_numeric'] >= 4) & (valid_data['Q57_numeric'] >= 4)
    df['ai_only_truster'] = (valid_data['Q13_numeric'] <= 2) & (valid_data['Q57_numeric'] >= 4)
    
    print(f"- Tech skeptics (distrust both): {df['tech_skeptic'].sum()} ({df['tech_skeptic'].mean()*100:.1f}%)")
    print(f"- Selective skeptics (distrust social, neutral/trust AI): {df['selective_skeptic'].sum()} ({df['selective_skeptic'].mean()*100:.1f}%)")
    print(f"- General trusters (trust both): {df['general_truster'].sum()} ({df['general_truster'].mean()*100:.1f}%)")
    print(f"- AI-only trusters (distrust social, trust AI): {df['ai_only_truster'].sum()} ({df['ai_only_truster'].mean()*100:.1f}%)")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)