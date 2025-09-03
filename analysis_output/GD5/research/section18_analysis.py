import sqlite3
import pandas as pd
import numpy as np

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=" * 80)
print("SECTION 18: EXPERIENTIAL & EXPOSURE EFFECTS")
print("=" * 80)

# First, let's understand Q38 - animal encounter types
print("\nUnderstanding Q38 - Animal Encounter Types")
print("-" * 40)

query_q38 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%types of animals%encounter%life%week%'
ORDER BY "all" DESC
"""
df_q38 = pd.read_sql_query(query_q38, conn)
print(f"\nAnimal encounter responses found: {len(df_q38)}")
if not df_q38.empty:
    print("\nAnimal encounter frequencies:")
    for _, row in df_q38.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response'][:50]}...: {row['agreement_score']:.3f}")

# Identify key groups for analysis
working_animals_text = "Working Animals (police dogs, work mules)"
zoo_animals_text = "Zoo/Aquarium Animals"
urban_wildlife_text = "Wild Animals in urban environments"
companion_animals_text = "Companion Animals"

# Question 18.1: Working Animals and AI Uses
print("\n18.1. Working Animals and AI Uses")
print("-" * 40)

# Find responses about AI uses - looking for instrumental vs conservation
query_ai_uses = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%AI%use%'
   OR question LIKE '%technology%animal%'
   OR question LIKE '%benefit%understand%animals%'
LIMIT 20
"""
df_ai_uses = pd.read_sql_query(query_ai_uses, conn)
print(f"\nAI use preference responses found: {len(df_ai_uses)}")

# Check for specific working animal encounters
working_animals = df_q38[df_q38['response'].str.contains('Working Animals|police dogs|mules', case=False, na=False)]
if not working_animals.empty:
    print(f"\nWorking animal encounter rate: {working_animals.iloc[0]['agreement_score']:.3f}")

# Question 18.2: Zoo Visitors and Entertainment
print("\n18.2. Zoo Visitors and Entertainment")
print("-" * 40)

zoo_visitors = df_q38[df_q38['response'].str.contains('Zoo|Aquarium', case=False, na=False)]
if not zoo_visitors.empty:
    print(f"\nZoo/Aquarium visitor rate: {zoo_visitors.iloc[0]['agreement_score']:.3f}")

# Look for entertainment-related AI uses
query_entertainment = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%entertainment%'
   OR question LIKE '%What would you be most interested%'
   OR question LIKE '%biggest benefit%'
"""
df_entertainment = pd.read_sql_query(query_entertainment, conn)
print(f"Entertainment-related responses found: {len(df_entertainment)}")

# Question 18.3: Urban vs. Companion Animal Ethics
print("\n18.3. Urban vs. Companion Animal Ethics")
print("-" * 40)

urban_wildlife = df_q38[df_q38['response'].str.contains('urban environments|rats|pigeons|squirrels', case=False, na=False)]
companion_animals = df_q38[df_q38['response'].str.contains('Companion Animals|cats|dogs', case=False, na=False)]

if not urban_wildlife.empty:
    print(f"\nUrban wildlife encounter rate: {urban_wildlife.iloc[0]['agreement_score']:.3f}")
if not companion_animals.empty:
    print(f"Companion animal encounter rate: {companion_animals.iloc[0]['agreement_score']:.3f}")

# Look for ethical priorities - rights, welfare, etc.
query_ethics = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%ethical%'
   OR question LIKE '%rights%'
   OR question LIKE '%welfare%'
   OR question LIKE '%approach%appropriate%protecting%'
LIMIT 20
"""
df_ethics = pd.read_sql_query(query_ethics, conn)
print(f"\nEthical priority responses found: {len(df_ethics)}")
if not df_ethics.empty:
    for _, row in df_ethics.head(5).iterrows():
        print(f"  Q: {row['question'][:50]}...")
        score_str = f"{row['agreement_score']:.3f}" if row['agreement_score'] is not None else 'N/A'
        print(f"  R: {row['response'][:50]}... - Score: {score_str}")

# Cross-analysis: Animal encounter patterns
print("\n" + "=" * 80)
print("CROSS-ANALYSIS: EXPOSURE PATTERNS")
print("=" * 80)

# Create exposure profile
exposure_profile = {}
for _, row in df_q38.iterrows():
    animal_type = row['response']
    score = row['agreement_score']
    if score is not None:
        if 'Companion' in animal_type:
            exposure_profile['companion'] = score
        elif 'Working' in animal_type:
            exposure_profile['working'] = score
        elif 'Zoo' in animal_type:
            exposure_profile['zoo'] = score
        elif 'urban' in animal_type:
            exposure_profile['urban'] = score
        elif 'Farmed' in animal_type:
            exposure_profile['farmed'] = score
        elif 'Wild Animals in Nature' in animal_type:
            exposure_profile['wild_nature'] = score
        elif 'Laboratory' in animal_type:
            exposure_profile['laboratory'] = score
        elif 'Service' in animal_type:
            exposure_profile['service'] = score
        elif 'Sanctuary' in animal_type:
            exposure_profile['sanctuary'] = score

print("\nAnimal Exposure Profile Summary:")
for animal_type, score in sorted(exposure_profile.items(), key=lambda x: x[1], reverse=True):
    print(f"  {animal_type:15s}: {score:.3f}")

# Analyze potential correlations (note: can't do individual-level due to data structure)
print("\nNote: Individual-level correlations between exposure types and")
print("ethical priorities cannot be calculated due to aggregated data structure.")
print("Analysis limited to comparing overall agreement scores.")

# Look for patterns in what people want from AI communication
query_interests = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%interested%know%animals%'
   OR question LIKE '%What would you want to know%'
"""
df_interests = pd.read_sql_query(query_interests, conn)
print(f"\nInterest/desire responses found: {len(df_interests)}")
if not df_interests.empty and len(df_interests) <= 10:
    print("\nWhat people want to know from animals:")
    for _, row in df_interests.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response'][:60]}...: {row['agreement_score']:.3f}")

# Summary statistics
print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)

print("\n1. Exposure Hierarchy:")
print(f"   Most common: Companion animals ({exposure_profile.get('companion', 0):.1%})")
print(f"   Least common: Sanctuary animals ({exposure_profile.get('sanctuary', 0):.1%})")

print("\n2. Special Interest Groups:")
print(f"   Working animal exposure: {exposure_profile.get('working', 0):.1%} of population")
print(f"   Zoo/aquarium exposure: {exposure_profile.get('zoo', 0):.1%} of population")
print(f"   Urban wildlife exposure: {exposure_profile.get('urban', 0):.1%} of population")

print("\n3. Data Limitations:")
print("   - Cannot link individual exposure to ethical preferences")
print("   - Cannot determine if exposure influences AI use preferences")
print("   - Aggregated scores prevent causal analysis")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete for Section 18")
print("=" * 80)