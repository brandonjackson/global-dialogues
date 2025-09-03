#!/usr/bin/env python3
"""
Section 9.1: Tech-First Futurist Persona Analysis (Final)
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get all relevant data
df = pd.read_sql_query("""
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
""", conn)

# Define Tech-First Futurist segment
def is_tech_futurist(row):
    # Q5: More excited than concerned
    excited = str(row['ai_excitement']) == 'More excited than concerned' if pd.notna(row['ai_excitement']) else False
    
    # Q17: Trust AI chatbots (Strongly Trust or Somewhat Trust)
    trust_ai = False
    if pd.notna(row['ai_chatbot_trust']):
        trust_val = str(row['ai_chatbot_trust']).strip()
        trust_ai = trust_val in ['Strongly Trust', 'Somewhat Trust']
    
    # Q23-27: Believe AI will improve at least 3 areas
    improve_count = 0
    for col in ['ai_workplace', 'ai_mental_health', 'ai_education', 'ai_environment', 'ai_justice']:
        if pd.notna(row[col]) and 'Better' in str(row[col]):
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

tech_q76 = tech_futurists['ecocentric_ai_society'].value_counts(normalize=True) * 100
gen_q76 = general_pop['ecocentric_ai_society'].value_counts(normalize=True) * 100

print("\nTech-First Futurists:")
for val, pct in tech_q76.items():
    if pd.notna(val) and val != '--':
        print(f"  {val}: {pct:.1f}%")

print("\nGeneral Population:")
for val, pct in gen_q76.items():
    if pd.notna(val) and val != '--':
        print(f"  {val}: {pct:.1f}%")

# Statistical test
contingency = pd.crosstab(df['is_tech_futurist'], df['ecocentric_ai_society'])
chi2, p_value, dof, expected = chi2_contingency(contingency)
print(f"\nStatistical difference: p={p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else '(not significant)'}")

# Analyze governance attitudes
print(f"\n=== GOVERNANCE ATTITUDES (Q82-Q84) ===")

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

for col, label in [
    ('restrict_to_professionals', 'Q82: Restrict communication to professionals'),
    ('everyone_should_listen', 'Q83: Everyone should be allowed to listen'),
    ('regulate_companies', 'Q84: Strictly regulate companies')
]:
    tech_vals = tech_futurists[col].apply(likert_to_numeric).dropna()
    gen_vals = general_pop[col].apply(likert_to_numeric).dropna()
    
    if len(tech_vals) > 0:
        tech_mean = tech_vals.mean()
        gen_mean = gen_vals.mean()
        
        # Distribution comparison
        tech_agree = ((tech_vals >= 4).sum() / len(tech_vals) * 100)
        gen_agree = ((gen_vals >= 4).sum() / len(gen_vals) * 100)
        
        statistic, p_value = mannwhitneyu(tech_vals, gen_vals, alternative='two-sided')
        
        print(f"\n{label}:")
        print(f"  Tech-First Futurists: {tech_agree:.1f}% agree (mean={tech_mean:.2f})")
        print(f"  General Population: {gen_agree:.1f}% agree (mean={gen_mean:.2f})")
        print(f"  Difference: {tech_agree - gen_agree:+.1f} percentage points")
        print(f"  P-value: {p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else ''}")

# Q85: Concerns about prohibited uses
print(f"\n=== Q85: PROHIBITED HARMFUL USES ===")
print("(Analyzing if Tech-First Futurists are less concerned about risks)")

# Count how many prohibitions each group supports
def count_prohibitions(val):
    if pd.isna(val) or val == '--':
        return 0
    return str(val).count(',') + 1 if ',' in str(val) else 1

tech_prohibit_count = tech_futurists['prohibit_harmful_uses'].apply(count_prohibitions)
gen_prohibit_count = general_pop['prohibit_harmful_uses'].apply(count_prohibitions)

print(f"\nAverage number of prohibited uses supported:")
print(f"  Tech-First Futurists: {tech_prohibit_count.mean():.2f}")
print(f"  General Population: {gen_prohibit_count.mean():.2f}")

if len(tech_prohibit_count) > 0:
    statistic, p_value = mannwhitneyu(tech_prohibit_count, gen_prohibit_count, alternative='two-sided')
    print(f"  P-value: {p_value:.4f} {'(SIGNIFICANT - less concerned)' if p_value < 0.05 and tech_prohibit_count.mean() < gen_prohibit_count.mean() else ''}")

conn.close()