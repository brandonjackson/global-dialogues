import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=" * 80)
print("SECTION 10: PUBLIC UNDERSTANDING OF ANIMALS & COMMUNICATION")
print("=" * 80)

# Question 10.1: Beliefs and Legal Rights
print("\n10.1. Beliefs and Legal Rights")
print("-" * 40)

# Find Q39-41 (beliefs) and Q70, Q73-75 (rights/representation)
query_beliefs = """
SELECT response, 
       "all" as agreement_score,
       question
FROM responses
WHERE question LIKE '%believe that other animals have their own forms of%'
ORDER BY question, response
"""
df_beliefs = pd.read_sql_query(query_beliefs, conn)
print(f"\nBelief responses found: {len(df_beliefs)}")
if not df_beliefs.empty:
    for q in df_beliefs['question'].unique():
        print(f"\n{q[:60]}...")
        belief_data = df_beliefs[df_beliefs['question'] == q]
        for _, row in belief_data.iterrows():
            if row['agreement_score'] is not None:
                print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Find legal rights questions
query_rights = """
SELECT response, "all" as agreement_score, branch_a, branch_b, branch_c
FROM responses
WHERE question LIKE '%approach%appropriate%protecting animals%'
   OR question LIKE '%legal representative%'
   OR question LIKE '%represent%animals%decision%'
LIMIT 20
"""
df_rights = pd.read_sql_query(query_rights, conn)
print(f"\nLegal rights responses found: {len(df_rights)}")

# Question 10.2: Animal Encounters and Emotional Response
print("\n10.2. Animal Encounters and Emotional Response")
print("-" * 40)

query_encounters = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%Caring for animals%'
   OR question LIKE '%Sharing physical space%'
   OR question LIKE '%Noticing or observing%'
   OR question LIKE '%encounter%life%week%'
"""
df_encounters = pd.read_sql_query(query_encounters, conn)
print(f"\nEncounter responses found: {len(df_encounters)}")

query_emotions = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%How does this knowledge make you feel%'
"""
df_emotions = pd.read_sql_query(query_emotions, conn)
print(f"Emotional responses found: {len(df_emotions)}")
if not df_emotions.empty:
    print("\nEmotional responses (agreement scores):")
    for _, row in df_emotions.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Question 10.3: Animal Types and Political Representation
print("\n10.3. Animal Types and Political Representation")
print("-" * 40)

query_animal_types = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%animals come to mind%sophisticated language%'
   OR question LIKE '%types of animals%encounter%'
"""
df_animal_types = pd.read_sql_query(query_animal_types, conn)
print(f"\nAnimal type responses found: {len(df_animal_types)}")
if not df_animal_types.empty:
    for _, row in df_animal_types.head(10).iterrows():
        score = f"{row['agreement_score']:.3f}" if row['agreement_score'] is not None else 'N/A'
        print(f"  {row['response'][:50]}... : {score}")

query_political = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%participate in human democratic processes%'
"""
df_political = pd.read_sql_query(query_political, conn)
print(f"\nPolitical participation responses found: {len(df_political)}")
if not df_political.empty:
    for _, row in df_political.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Question 10.4: Animal Culture and Governance
print("\n10.4. Animal Culture and Governance")
print("-" * 40)

query_culture = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%believe that other animals have their own forms of culture%'
"""
df_culture = pd.read_sql_query(query_culture, conn)
print(f"\nCulture belief responses found: {len(df_culture)}")
if not df_culture.empty:
    for _, row in df_culture.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

query_ai_governance = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%AI%ecocentric%'
   OR question LIKE '%appeal%society%AI%'
"""
df_ai_governance = pd.read_sql_query(query_ai_governance, conn)
print(f"\nAI governance responses found: {len(df_ai_governance)}")
if not df_ai_governance.empty:
    for _, row in df_ai_governance.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response'][:50]}...: {row['agreement_score']:.3f}")

# Demographic Analysis
print("\n" + "=" * 80)
print("DEMOGRAPHIC PATTERNS")
print("=" * 80)

# Check age group patterns for beliefs
query_age_beliefs = """
SELECT 
    response,
    o2_18_25 as age_18_25,
    o2_26_35 as age_26_35,
    o2_36_45 as age_36_45,
    o2_46_55 as age_46_55,
    o2_56_65 as age_56_65,
    o2_65 as age_65_plus
FROM responses
WHERE question LIKE '%believe that other animals have their own forms of language%'
AND response = 'Strongly believe'
"""
df_age = pd.read_sql_query(query_age_beliefs, conn)
if not df_age.empty:
    print("\nAge patterns for 'Strongly believe' animals have language:")
    age_cols = ['age_18_25', 'age_26_35', 'age_36_45', 'age_46_55', 'age_56_65', 'age_65_plus']
    for col in age_cols:
        if col in df_age.columns and df_age[col].notna().any():
            print(f"  {col}: {df_age[col].iloc[0]:.3f}")

# Check regional patterns
query_regional = """
SELECT 
    response,
    africa, asia, europe, north_america, south_america, oceania
FROM responses
WHERE question LIKE '%participate in human democratic processes%'
AND response LIKE '%Yes%'
LIMIT 1
"""
df_regional = pd.read_sql_query(query_regional, conn)
if not df_regional.empty:
    print("\nRegional support for animal democratic participation:")
    for col in ['africa', 'asia', 'europe', 'north_america', 'south_america', 'oceania']:
        if col in df_regional.columns and df_regional[col].notna().any():
            val = df_regional[col].iloc[0]
            if val is not None:
                print(f"  {col}: {val:.3f}")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete for Section 10")
print("=" * 80)