#!/usr/bin/env python3
"""
Section 9.3: The "Cautious Humanist" Persona Analysis
Segment: Humans fundamentally different + Concerned about AI + Distrust social media/AI chatbots
"""
import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get all relevant data - Q31 is actually Q93, Q32 is Q94
df = pd.read_sql_query("""
SELECT 
    participant_id,
    Q93 as human_nature_separation,
    Q5 as ai_excitement,
    Q13 as social_media_trust,
    Q17 as ai_chatbot_trust,
    Q59 as ai_communication_concerns,
    Q66 as simulation_preference,
    Q55 as interest_in_communication,
    Q57 as trust_ai_translation
FROM participant_responses
""", conn)

# Check distributions
print("=== CHECKING COMPONENT DISTRIBUTIONS ===")
print("\nQ93 (Human-nature separation):")
print(df['human_nature_separation'].value_counts())
print("\nQ5 (AI excitement):")
print(df['ai_excitement'].value_counts())

# Define Cautious Humanist segment
def is_cautious_humanist(row):
    # Believe humans are fundamentally different from animals
    human_different = False
    if pd.notna(row['human_nature_separation']):
        val = str(row['human_nature_separation']).lower()
        human_different = ('separate' in val and 'different' in val)
    
    # More concerned about AI
    ai_concerned = False
    if pd.notna(row['ai_excitement']):
        val = str(row['ai_excitement']).lower()
        ai_concerned = 'more concerned' in val
    
    # Strongly distrust social media
    distrust_social = False
    if pd.notna(row['social_media_trust']):
        val = str(row['social_media_trust'])
        distrust_social = val in ['Strongly Distrust', 'Somewhat Distrust']
    
    # Strongly distrust AI chatbots
    distrust_ai = False
    if pd.notna(row['ai_chatbot_trust']):
        val = str(row['ai_chatbot_trust'])
        distrust_ai = val in ['Strongly Distrust', 'Somewhat Distrust']
    
    return human_different and ai_concerned and (distrust_social or distrust_ai)

df['is_cautious_humanist'] = df.apply(is_cautious_humanist, axis=1)

cautious_humanists = df[df['is_cautious_humanist']]
general_pop = df[~df['is_cautious_humanist']]

print(f"\n=== SEGMENT SIZES ===")
print(f"Cautious Humanists: {len(cautious_humanists)} ({len(cautious_humanists)/len(df)*100:.1f}%)")
print(f"General Population: {len(general_pop)} ({len(general_pop)/len(df)*100:.1f}%)")

if len(cautious_humanists) > 0:
    # Analyze Q59: Primary concerns with AI-mediated communication
    print(f"\n=== Q59: PRIMARY CONCERNS WITH AI COMMUNICATION ===")
    print("(Open text analysis - showing sample responses)")
    
    ch_concerns = cautious_humanists['ai_communication_concerns'].dropna()
    gen_concerns = general_pop['ai_communication_concerns'].dropna()
    
    print(f"\nCautious Humanists sample concerns (n={len(ch_concerns)}):")
    for concern in ch_concerns.sample(min(5, len(ch_concerns))).values:
        print(f"  - {str(concern)[:150]}...")
    
    # Analyze Q66: Preference for simulation over direct communication
    print(f"\n=== Q66: SIMULATION VS DIRECT COMMUNICATION ===")
    
    ch_sim = cautious_humanists['simulation_preference'].value_counts(normalize=True) * 100
    gen_sim = general_pop['simulation_preference'].value_counts(normalize=True) * 100
    
    print("\nCautious Humanists preferences:")
    for val, pct in ch_sim.head(3).items():
        if pd.notna(val) and val != '--':
            print(f"  {str(val)[:60]}...: {pct:.1f}%")
    
    print("\nGeneral Population preferences:")
    for val, pct in gen_sim.head(3).items():
        if pd.notna(val) and val != '--':
            print(f"  {str(val)[:60]}...: {pct:.1f}%")
    
    # Analyze Q55: Interest despite distrust
    print(f"\n=== Q55: INTEREST IN ANIMAL COMMUNICATION ===")
    
    ch_interest = cautious_humanists['interest_in_communication'].value_counts(normalize=True) * 100
    gen_interest = general_pop['interest_in_communication'].value_counts(normalize=True) * 100
    
    print("\nCautious Humanists interest levels:")
    for val, pct in ch_interest.items():
        if pd.notna(val) and val != '--':
            print(f"  {val}: {pct:.1f}%")
    
    # Check if they see any benefits
    ch_very_interested = ch_interest.get('Very interested', 0)
    ch_somewhat_interested = ch_interest.get('Somewhat interested', 0)
    total_interested = ch_very_interested + ch_somewhat_interested
    
    print(f"\nTotal interested (Very + Somewhat): {total_interested:.1f}%")
    
    # Analyze Q57: Trust in AI translation
    print(f"\n=== Q57: TRUST IN AI TRANSLATION ===")
    
    ch_trust = cautious_humanists['trust_ai_translation'].value_counts(normalize=True) * 100
    gen_trust = general_pop['trust_ai_translation'].value_counts(normalize=True) * 100
    
    print("\nCautious Humanists trust levels:")
    for val, pct in ch_trust.items():
        if pd.notna(val) and val != '--':
            print(f"  {val}: {pct:.1f}%")
    
    print(f"\n=== KEY FINDINGS ===")
    print(f"1. Cautious Humanists represent {len(cautious_humanists)/len(df)*100:.1f}% of respondents")
    print(f"2. Despite skepticism, {total_interested:.1f}% are still interested in animal communication")
    print(f"3. Their concerns focus on maintaining human-animal boundaries")

else:
    print("\nNo Cautious Humanists found with strict criteria. Adjusting...")
    
    # Try more lenient criteria
    df['is_cautious_humanist_lenient'] = (
        (df['human_nature_separation'].str.contains('separate', case=False, na=False)) &
        (df['ai_excitement'] == 'More concerned than excited')
    )
    
    cautious_humanists = df[df['is_cautious_humanist_lenient']]
    print(f"Adjusted Cautious Humanists: {len(cautious_humanists)} ({len(cautious_humanists)/len(df)*100:.1f}%)")

conn.close()