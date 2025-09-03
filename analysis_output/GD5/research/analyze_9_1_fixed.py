#!/usr/bin/env python3
"""
Section 9.1: Tech-First Futurist Persona Analysis (Fixed)
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

# Check actual values in Q5 and Q17
print("Q5 (AI excitement) distribution:")
print(df['ai_excitement'].value_counts())
print("\nQ17 (AI chatbot trust) distribution:")
print(df['ai_chatbot_trust'].value_counts())

# Adjusted Tech-First Futurist definition
def is_tech_futurist(row):
    # Q5: More excited than concerned (or equally excited)
    excited = False
    if pd.notna(row['ai_excitement']):
        val = str(row['ai_excitement']).lower()
        excited = ('more excited' in val) or ('equally' in val)
    
    # Q17: Trust AI chatbots (4-5 on scale)
    trust_ai = False
    if pd.notna(row['ai_chatbot_trust']):
        try:
            trust_val = float(str(row['ai_chatbot_trust']).strip())
            trust_ai = trust_val >= 4
        except:
            pass
    
    # Q23-27: Believe AI will improve at least 2 areas (lowered threshold)
    improve_count = 0
    for col in ['ai_workplace', 'ai_mental_health', 'ai_education', 'ai_environment', 'ai_justice']:
        if pd.notna(row[col]) and 'better' in str(row[col]).lower():
            improve_count += 1
    
    return excited and trust_ai and improve_count >= 2

df['is_tech_futurist'] = df.apply(is_tech_futurist, axis=1)

tech_futurists = df[df['is_tech_futurist']]
general_pop = df[~df['is_tech_futurist']]

print(f"\n=== SEGMENT SIZES ===")
print(f"Tech-First Futurists: {len(tech_futurists)} ({len(tech_futurists)/len(df)*100:.1f}%)")
print(f"General Population: {len(general_pop)} ({len(general_pop)/len(df)*100:.1f}%)")

if len(tech_futurists) == 0:
    print("\nNo Tech-First Futurists found with current criteria. Adjusting...")
    # More lenient criteria
    df['is_tech_futurist'] = (
        (df['ai_excitement'].notna()) & 
        (~df['ai_excitement'].str.contains('concerned', case=False, na=False)) &
        (df['ai_chatbot_trust'].astype(str).str.strip().astype(float, errors='coerce') >= 3)
    )
    tech_futurists = df[df['is_tech_futurist']]
    general_pop = df[~df['is_tech_futurist']]
    print(f"Adjusted Tech-First Futurists: {len(tech_futurists)} ({len(tech_futurists)/len(df)*100:.1f}%)")

# Analyze Q76: Ecocentric AI Society Appeal
print(f"\n=== Q76: APPEAL OF ECOCENTRIC AI-GOVERNED SOCIETY ===")

if len(tech_futurists) > 0:
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
    
    # Chi-square test
    contingency = pd.crosstab(df['is_tech_futurist'], df['ecocentric_ai_society'])
    if contingency.shape[0] > 1 and contingency.shape[1] > 1:
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

if len(tech_futurists) > 0:
    for col, label in [
        ('restrict_to_professionals', 'Q82: Restrict to Professionals'),
        ('everyone_should_listen', 'Q83: Everyone Should Listen'),
        ('regulate_companies', 'Q84: Regulate Companies')
    ]:
        tech_vals = tech_futurists[col].apply(likert_to_numeric).dropna()
        gen_vals = general_pop[col].apply(likert_to_numeric).dropna()
        
        if len(tech_vals) > 0 and len(gen_vals) > 0:
            tech_mean = tech_vals.mean()
            gen_mean = gen_vals.mean()
            
            statistic, p_value = mannwhitneyu(tech_vals, gen_vals, alternative='two-sided')
            
            print(f"\n{label}:")
            print(f"  Tech-First Futurists mean: {tech_mean:.2f} (n={len(tech_vals)})")
            print(f"  General Population mean: {gen_mean:.2f} (n={len(gen_vals)})")
            print(f"  Difference: {tech_mean - gen_mean:+.2f}")
            print(f"  P-value: {p_value:.4f} {'(SIGNIFICANT)' if p_value < 0.05 else ''}")

conn.close()