import sqlite3
import pandas as pd
import numpy as np
import json
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Section 13.2.2: Identify and Profile the "Reluctant Professional"
# Create a segment of respondents who are "expected to use an AI system at work" "daily" (Q14) 
# AND also "Strongly Distrust" or "Somewhat Distrust" companies building AI (Q29)

print("\n" + "="*80)
print("13.2.2 The 'Reluctant Professional' Profile")
print("="*80)

# Get participant data
query = """
SELECT 
    pr.participant_id,
    pr.Q14 as work_ai_frequency,  -- How often required to use AI at work
    pr.Q29 as trust_ai_companies,  -- Trust in companies building AI
    pr.Q38 as trust_reason,  -- Why they trust/distrust (text)
    pr.Q115 as greatest_fears,  -- JSON array of fears
    pr.Q5 as ai_sentiment,  -- More excited vs concerned
    pr.Q16 as personal_ai_frequency,  -- How often personally use AI
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q7 as country,
    pr.Q43 as ai_impact_jobs,  -- AI impact on job availability
    pr.Q44 as ai_impact_purpose,  -- AI impact on sense of purpose
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# 1. Work AI frequency distribution
print("\n1. Work AI Frequency Distribution:")
work_counts = df['work_ai_frequency'].value_counts()
for freq, count in work_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {freq}: {count} ({pct:.1f}%)")

# 2. Trust in AI companies distribution
print("\n2. Trust in AI Companies Distribution:")
trust_counts = df['trust_ai_companies'].value_counts()
for trust, count in trust_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {trust}: {count} ({pct:.1f}%)")

# 3. Identify the "Reluctant Professional" segment
reluctant_professionals = df[
    (df['work_ai_frequency'] == 'daily') & 
    (df['trust_ai_companies'].isin(['Strongly Distrust', 'Somewhat Distrust']))
]

print(f"\n3. The 'Reluctant Professional' Segment:")
print(f"   {len(reluctant_professionals)} people ({len(reluctant_professionals)/len(df)*100:.1f}% of all participants)")
print(f"   are expected to use AI DAILY at work BUT DISTRUST AI companies")

# 4. Demographic profile
if len(reluctant_professionals) > 0:
    print("\n4. Demographic Profile of Reluctant Professionals:")
    
    # Age distribution
    print("\n   Age Distribution:")
    age_counts = reluctant_professionals['age_group'].value_counts()
    for age, count in age_counts.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {age}: {count} ({pct:.1f}%)")
    
    # Gender distribution
    print("\n   Gender Distribution:")
    gender_counts = reluctant_professionals['gender'].value_counts()
    for gender, count in gender_counts.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {gender}: {count} ({pct:.1f}%)")
    
    # Top countries
    print("\n   Top 5 Countries:")
    country_counts = reluctant_professionals['country'].value_counts().head(5)
    for country, count in country_counts.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {country}: {count} ({pct:.1f}%)")

# 5. Trust breakdown
print("\n5. Specific Trust Levels (Reluctant Professionals):")
if len(reluctant_professionals) > 0:
    specific_trust = reluctant_professionals['trust_ai_companies'].value_counts()
    for trust, count in specific_trust.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {trust}: {count} ({pct:.1f}%)")

# 6. Primary reason for distrust (sample from text responses)
print("\n6. Sample Reasons for Distrust (first 5):")
if len(reluctant_professionals) > 0:
    reasons = reluctant_professionals['trust_reason'].dropna().head(5)
    for i, reason in enumerate(reasons, 1):
        if len(reason) > 100:
            reason = reason[:100] + "..."
        print(f"   {i}. {reason}")

# Parse fears JSON
def parse_fears(fears_str):
    if pd.isna(fears_str) or fears_str == '' or fears_str == 'null':
        return []
    try:
        fears = json.loads(fears_str)
        if isinstance(fears, list):
            return fears
        return []
    except:
        return []

df['fears_list'] = df['greatest_fears'].apply(parse_fears)
reluctant_professionals['fears_list'] = reluctant_professionals['greatest_fears'].apply(parse_fears)

# 7. Greatest fears analysis
print("\n7. Top Fears Among Reluctant Professionals:")
if len(reluctant_professionals) > 0:
    all_fears = {}
    for fears in reluctant_professionals['fears_list']:
        for fear in fears:
            if fear:
                all_fears[fear] = all_fears.get(fear, 0) + 1
    
    sorted_fears = sorted(all_fears.items(), key=lambda x: x[1], reverse=True)
    for fear, count in sorted_fears[:5]:
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   - {fear}: {count} ({pct:.1f}%)")

# Check for specific fears
if len(reluctant_professionals) > 0:
    reluctant_professionals['fears_manipulation'] = reluctant_professionals['fears_list'].apply(
        lambda fears: any('manipulation' in str(fear).lower() or 'exploitation' in str(fear).lower() 
                         for fear in fears)
    )
    
    manipulation_count = reluctant_professionals['fears_manipulation'].sum()
    print(f"\n   Fear manipulation/exploitation: {manipulation_count} ({manipulation_count/len(reluctant_professionals)*100:.1f}%)")

# 8. Compare with general population
print("\n8. Comparison with General Population:")
general_manipulation = df['fears_list'].apply(
    lambda fears: any('manipulation' in str(fear).lower() or 'exploitation' in str(fear).lower() 
                     for fear in fears)
).mean() * 100
print(f"   General population fearing manipulation: {general_manipulation:.1f}%")

if len(reluctant_professionals) > 0:
    reluctant_manipulation = reluctant_professionals['fears_manipulation'].mean() * 100
    print(f"   Reluctant professionals fearing manipulation: {reluctant_manipulation:.1f}%")
    print(f"   Difference: {reluctant_manipulation - general_manipulation:+.1f} percentage points")

# 9. Personal AI use despite work requirements
print("\n9. Personal AI Use Among Reluctant Professionals:")
if len(reluctant_professionals) > 0:
    personal_use = reluctant_professionals['personal_ai_frequency'].value_counts()
    for freq, count in personal_use.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {freq}: {count} ({pct:.1f}%)")
    
    daily_personal = len(reluctant_professionals[reluctant_professionals['personal_ai_frequency'] == 'daily'])
    print(f"\n   Also use AI daily in personal life: {daily_personal} ({daily_personal/len(reluctant_professionals)*100:.1f}%)")

# 10. Impact on jobs and purpose
print("\n10. Views on AI's Impact (Reluctant Professionals):")
if len(reluctant_professionals) > 0:
    print("\n   Impact on Job Availability:")
    jobs_impact = reluctant_professionals['ai_impact_jobs'].value_counts()
    for impact, count in jobs_impact.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {impact}: {count} ({pct:.1f}%)")
    
    print("\n   Impact on Sense of Purpose:")
    purpose_impact = reluctant_professionals['ai_impact_purpose'].value_counts()
    for impact, count in purpose_impact.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {impact}: {count} ({pct:.1f}%)")

# 11. Overall sentiment
print("\n11. Overall AI Sentiment (Reluctant Professionals):")
if len(reluctant_professionals) > 0:
    sentiment_counts = reluctant_professionals['ai_sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        pct = (count / len(reluctant_professionals)) * 100
        print(f"   {sentiment}: {count} ({pct:.1f}%)")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: {len(reluctant_professionals)/len(df)*100:.1f}% are 'Reluctant Professionals' -")
print("required to use AI daily at work despite distrusting AI companies.")
if len(reluctant_professionals) > 0:
    if reluctant_manipulation > general_manipulation:
        print(f"They are {(reluctant_manipulation/general_manipulation):.1f}x more likely to fear manipulation")
        print("compared to the general population.")
print("="*80)