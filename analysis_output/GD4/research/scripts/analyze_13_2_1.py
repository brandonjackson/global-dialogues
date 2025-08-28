import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Section 13.2.1: Identify and Profile the "Concerned Daily User"
# Create a segment of respondents who are "More concerned than excited" about AI (Q5) 
# AND "personally chose to use an AI system in [their] personal life" on a "daily" basis (Q16)

print("\n" + "="*80)
print("13.2.1 The 'Concerned Daily User' Profile")
print("="*80)

# Get participant data
query = """
SELECT 
    pr.participant_id,
    pr.Q5 as ai_sentiment,  -- More excited vs concerned
    pr.Q16 as personal_ai_frequency,  -- How often personally use AI
    pr.Q14 as work_ai_frequency,  -- How often required to use AI at work
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q7 as country,
    pr.Q67 as ai_companionship,
    pr.Q29 as trust_ai_companies,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# 1. Overall sentiment distribution
print("\n1. Overall AI Sentiment Distribution:")
sentiment_counts = df['ai_sentiment'].value_counts()
for sentiment, count in sentiment_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {sentiment}: {count} ({pct:.1f}%)")

# 2. Personal AI use frequency
print("\n2. Personal AI Use Frequency:")
personal_counts = df['personal_ai_frequency'].value_counts()
for freq, count in personal_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {freq}: {count} ({pct:.1f}%)")

# 3. Identify the "Concerned Daily User" segment
concerned_daily_users = df[
    (df['ai_sentiment'] == 'More concerned than excited') & 
    (df['personal_ai_frequency'] == 'daily')
]

print(f"\n3. The 'Concerned Daily User' Segment:")
print(f"   {len(concerned_daily_users)} people ({len(concerned_daily_users)/len(df)*100:.1f}% of all participants)")
print(f"   are MORE CONCERNED than excited BUT use AI DAILY")

# 4. Demographic profile
if len(concerned_daily_users) > 0:
    print("\n4. Demographic Profile of Concerned Daily Users:")
    
    # Age distribution
    print("\n   Age Distribution:")
    age_counts = concerned_daily_users['age_group'].value_counts()
    for age, count in age_counts.items():
        pct = (count / len(concerned_daily_users)) * 100
        print(f"   {age}: {count} ({pct:.1f}%)")
    
    # Gender distribution
    print("\n   Gender Distribution:")
    gender_counts = concerned_daily_users['gender'].value_counts()
    for gender, count in gender_counts.items():
        pct = (count / len(concerned_daily_users)) * 100
        print(f"   {gender}: {count} ({pct:.1f}%)")
    
    # Top countries
    print("\n   Top 5 Countries:")
    country_counts = concerned_daily_users['country'].value_counts().head(5)
    for country, count in country_counts.items():
        pct = (count / len(concerned_daily_users)) * 100
        print(f"   {country}: {count} ({pct:.1f}%)")
    
    # Occupation removed - not available in data

# 5. Work requirement analysis
print("\n5. Are They Being Forced to Use AI at Work?")
if len(concerned_daily_users) > 0:
    work_ai_counts = concerned_daily_users['work_ai_frequency'].value_counts()
    print("\n   Work AI Frequency among Concerned Daily Users:")
    for freq, count in work_ai_counts.items():
        pct = (count / len(concerned_daily_users)) * 100
        print(f"   {freq}: {count} ({pct:.1f}%)")
    
    # Check if they're using AI for work daily
    work_daily = len(concerned_daily_users[concerned_daily_users['work_ai_frequency'] == 'daily'])
    print(f"\n   Using AI daily at work: {work_daily} ({work_daily/len(concerned_daily_users)*100:.1f}%)")

# 6. Compare with other groups
print("\n6. Comparison with Other User Groups:")

# Excited daily users
excited_daily = df[
    (df['ai_sentiment'] == 'More excited than concerned') & 
    (df['personal_ai_frequency'] == 'daily')
]
print(f"   Excited Daily Users: {len(excited_daily)} ({len(excited_daily)/len(df)*100:.1f}%)")

# Concerned non-users
concerned_never = df[
    (df['ai_sentiment'] == 'More concerned than excited') & 
    (df['personal_ai_frequency'] == 'never')
]
print(f"   Concerned Never Users: {len(concerned_never)} ({len(concerned_never)/len(df)*100:.1f}%)")

# Neutral daily users
neutral_daily = df[
    (df['ai_sentiment'] == 'Equally concerned and excited') & 
    (df['personal_ai_frequency'] == 'daily')
]
print(f"   Neutral Daily Users: {len(neutral_daily)} ({len(neutral_daily)/len(df)*100:.1f}%)")

# 7. Trust analysis
print("\n7. Trust in AI Companies (Concerned Daily Users):")
if len(concerned_daily_users) > 0:
    trust_counts = concerned_daily_users['trust_ai_companies'].value_counts()
    for trust, count in trust_counts.items():
        pct = (count / len(concerned_daily_users)) * 100
        print(f"   {trust}: {count} ({pct:.1f}%)")

# 8. AI companionship usage
print("\n8. AI Companionship Usage (Concerned Daily Users):")
if len(concerned_daily_users) > 0:
    companionship_yes = len(concerned_daily_users[concerned_daily_users['ai_companionship'] == 'Yes'])
    print(f"   Use AI for companionship: {companionship_yes} ({companionship_yes/len(concerned_daily_users)*100:.1f}%)")

# 9. Statistical comparison between sentiment and usage
print("\n9. Statistical Analysis: Sentiment vs Usage")
# Create contingency table
contingency = pd.crosstab(df['ai_sentiment'], df['personal_ai_frequency'])
chi2, p_value, dof, expected = chi2_contingency(contingency)
print(f"   Chi-square test: χ² = {chi2:.3f}, p = {p_value:.4f}")
if p_value < 0.001:
    print("   Highly significant association between sentiment and usage frequency")
elif p_value < 0.05:
    print("   Significant association between sentiment and usage frequency")
else:
    print("   No significant association between sentiment and usage frequency")

# 10. Calculate percentage of daily users who are concerned
daily_users = df[df['personal_ai_frequency'] == 'daily']
if len(daily_users) > 0:
    concerned_among_daily = len(daily_users[daily_users['ai_sentiment'] == 'More concerned than excited'])
    print(f"\n10. Among All Daily Users:")
    print(f"    {concerned_among_daily} out of {len(daily_users)} ({concerned_among_daily/len(daily_users)*100:.1f}%) are concerned")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: {len(concerned_daily_users)/len(df)*100:.1f}% are 'Concerned Daily Users' -")
print("people who are more concerned than excited about AI but still use it daily.")
if len(concerned_daily_users) > 0:
    if work_daily/len(concerned_daily_users) > 0.5:
        print(f"Notably, {work_daily/len(concerned_daily_users)*100:.1f}% also use AI daily at work,")
        print("suggesting work requirements may drive personal use despite concerns.")
print("="*80)