#!/usr/bin/env python3
"""
Section 9.1: Complete Tech-First Futurist Persona Analysis
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get all relevant data
query = """
SELECT 
    participant_id,
    Q5 as ai_excitement,
    Q17 as ai_chatbot_trust,
    Q23 as ai_workplace,
    Q24 as ai_mental_health,
    Q25 as ai_education,
    Q26 as ai_environment,
    Q27 as ai_justice,
    Q82 as restrict_to_professionals,
    Q83 as everyone_should_listen,
    Q84 as regulate_companies,
    Q85 as prohibit_harmful_uses,
    Q76 as ecocentric_ai_society
FROM participant_responses
"""

df = pd.read_sql_query(query, conn)

# Define Tech-First Futurist segment more precisely
def is_tech_futurist(row):
    # Q5: More excited than concerned
    excited = False
    if pd.notna(row['ai_excitement']):
        excited = 'more excited' in str(row['ai_excitement']).lower()
    
    # Q17: Trust AI chatbots (4-5 on scale)
    trust_ai = False
    if pd.notna(row['ai_chatbot_trust']):
        try:
            trust_ai = int(row['ai_chatbot_trust']) >= 4
        except:
            pass
    
    # Q23-27: Believe AI will improve at least 3 areas
    improve_count = 0
    for col in ['ai_workplace', 'ai_mental_health', 'ai_education', 'ai_environment', 'ai_justice']:
        if pd.notna(row[col]) and 'better' in str(row[col]).lower():
            improve_count += 1
    
    return excited and trust_ai and improve_count >= 3

df['is_tech_futurist'] = df.apply(is_tech_futurist, axis=1)

tech_futurists = df[df['is_tech_futurist']]
general_pop = df[~df['is_tech_futurist']]

print(f"=== SEGMENT SIZES ===")
print(f"Tech-First Futurists: {len(tech_futurists)} ({len(tech_futurists)/len(df)*100:.1f}%)")
print(f"General Population: {len(general_pop)} ({len(general_pop)/len(df)*100:.1f}%)")

# Analyze Q76: Ecocentric AI Society Appeal
print(f"\n=== Q76: APPEAL OF ECOCENTRIC AI-GOVERNED SOCIETY ===")

def analyze_categorical(column_name, label):
    tech_dist = tech_futurists[column_name].value_counts(normalize=True) * 100
    gen_dist = general_pop[column_name].value_counts(normalize=True) * 100
    
    print(f"\n{label}:")
    print("\nTech-First Futurists:")
    for val, pct in tech_dist.items():
        if pd.notna(val) and val != '--':
            print(f"  {val}: {pct:.1f}%")
    
    print("\nGeneral Population:")
    for val, pct in gen_dist.items():
        if pd.notna(val) and val != '--':
            print(f"  {val}: {pct:.1f}%")
    
    # Chi-square test
    contingency = pd.crosstab(df['is_tech_futurist'], df[column_name])
    if contingency.shape[0] > 1 and contingency.shape[1] > 1:
        chi2, p_value, dof, expected = chi2_contingency(contingency)
        print(f"\nStatistical difference: p={p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else '(not significant)'}")

analyze_categorical('ecocentric_ai_society', 'Q76: Ecocentric AI Society Appeal')

# Analyze governance attitudes
print(f"\n=== GOVERNANCE ATTITUDES (Q82-Q85) ===")

# Convert Likert scales to numeric for comparison
def likert_to_numeric(val):
    if pd.isna(val):
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

for col, label in [
    ('restrict_to_professionals', 'Q82: Restrict to Professionals'),
    ('everyone_should_listen', 'Q83: Everyone Should Listen'),
    ('regulate_companies', 'Q84: Regulate Companies')
]:
    df[f'{col}_numeric'] = df[col].apply(likert_to_numeric)
    
    tech_mean = tech_futurists[f'{col}_numeric'].mean()
    gen_mean = general_pop[f'{col}_numeric'].mean()
    
    # Mann-Whitney U test for ordinal data
    tech_vals = tech_futurists[f'{col}_numeric'].dropna()
    gen_vals = general_pop[f'{col}_numeric'].dropna()
    
    if len(tech_vals) > 0 and len(gen_vals) > 0:
        statistic, p_value = mannwhitneyu(tech_vals, gen_vals, alternative='two-sided')
        
        print(f"\n{label}:")
        print(f"  Tech-First Futurists mean: {tech_mean:.2f}")
        print(f"  General Population mean: {gen_mean:.2f}")
        print(f"  Difference: {tech_mean - gen_mean:+.2f}")
        print(f"  P-value: {p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else ''}")

# Q85: Prohibited uses (multiple choice)
print(f"\n=== Q85: PROHIBITED HARMFUL USES ===")
print("(This is a multiple-choice question - analyzing response patterns)")

# Count unique response patterns
tech_q85 = tech_futurists['prohibit_harmful_uses'].value_counts().head(3)
gen_q85 = general_pop['prohibit_harmful_uses'].value_counts().head(3)

print("\nTop 3 response patterns - Tech-First Futurists:")
for i, (pattern, count) in enumerate(tech_q85.items(), 1):
    if pd.notna(pattern):
        print(f"  {i}. {str(pattern)[:100]}... ({count/len(tech_futurists)*100:.1f}%)")

print("\nTop 3 response patterns - General Population:")
for i, (pattern, count) in enumerate(gen_q85.items(), 1):
    if pd.notna(pattern):
        print(f"  {i}. {str(pattern)[:100]}... ({count/len(general_pop)*100:.1f}%)")

# Summary
print(f"\n=== KEY FINDINGS ===")
print("1. Tech-First Futurists show distinct patterns in AI governance preferences")
print("2. Compare their openness to AI-led decision-making vs general population")
print("3. Examine if they're less concerned about risks")

conn.close()