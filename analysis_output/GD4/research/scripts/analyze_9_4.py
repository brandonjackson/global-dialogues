import sqlite3
import pandas as pd
import numpy as np
import json

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Question 9.4: Personal Openness vs. Societal Fear
# Are individuals who are personally open to a romantic relationship with an AI 
# also likely to list "loss of genuine human connection" as one of their greatest fears for society's future?

print("\n" + "="*80)
print("9.4 Personal Openness vs. Societal Fear")
print("="*80)

# Get participant data with relevant questions
query = """
SELECT 
    pr.participant_id,
    pr.Q97 as romantic_ai_openness,  -- Q97: Romantic relationship with AI
    pr.Q115 as greatest_fears,  -- JSON array of fears
    pr.Q67 as ai_companionship,  -- Have used AI for companionship
    pr.Q5 as ai_sentiment,  -- Excited vs concerned
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# Parse the fears JSON
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

# Check for loss of genuine human connection fear
df['fears_loss_connection'] = df['fears_list'].apply(
    lambda fears: any('loss of genuine human connection' in str(fear).lower() or
                     'genuine human' in str(fear).lower()
                     for fear in fears)
)

# Check for social isolation fear
df['fears_social_isolation'] = df['fears_list'].apply(
    lambda fears: any('widespread social isolation' in str(fear).lower() or
                     'social isolation' in str(fear).lower()
                     for fear in fears)
)

# 1. Romantic openness distribution
print("\n1. Romantic Relationship with AI - Openness:")
romantic_counts = df['romantic_ai_openness'].value_counts()
for response, count in romantic_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {response}: {count} ({pct:.1f}%)")

# Categorize romantic openness - need to handle variations in text
df['romantically_open'] = df['romantic_ai_openness'].str.contains('Yes', case=False, na=False)
df['romantically_closed'] = df['romantic_ai_openness'].str.contains('No, definitely', case=False, na=False)

print(f"\n   Romantically open (Yes definitely/possibly): {df['romantically_open'].sum()} ({df['romantically_open'].mean()*100:.1f}%)")
print(f"   Romantically closed (No definitely not): {df['romantically_closed'].sum()} ({df['romantically_closed'].mean()*100:.1f}%)")

# 2. Fear analysis by romantic openness
print("\n2. Fears by Romantic Openness:")
open_group = df[df['romantically_open'] == True]
closed_group = df[df['romantically_closed'] == True]
unsure_group = df[df['romantic_ai_openness'].str.contains('unsure|Maybe', case=False, na=False)]

print(f"\n   Among romantically OPEN to AI (n={len(open_group)}):")
print(f"   - Fear loss of connection: {open_group['fears_loss_connection'].sum()} ({open_group['fears_loss_connection'].mean()*100:.1f}%)")
print(f"   - Fear social isolation: {open_group['fears_social_isolation'].sum()} ({open_group['fears_social_isolation'].mean()*100:.1f}%)")

print(f"\n   Among romantically CLOSED to AI (n={len(closed_group)}):")
print(f"   - Fear loss of connection: {closed_group['fears_loss_connection'].sum()} ({closed_group['fears_loss_connection'].mean()*100:.1f}%)")
print(f"   - Fear social isolation: {closed_group['fears_social_isolation'].sum()} ({closed_group['fears_social_isolation'].mean()*100:.1f}%)")

print(f"\n   Among UNSURE about AI romance (n={len(unsure_group)}):")
print(f"   - Fear loss of connection: {unsure_group['fears_loss_connection'].sum()} ({unsure_group['fears_loss_connection'].mean()*100:.1f}%)")
print(f"   - Fear social isolation: {unsure_group['fears_social_isolation'].sum()} ({unsure_group['fears_social_isolation'].mean()*100:.1f}%)")

# 3. The paradox group
paradox_group = df[(df['romantically_open'] == True) & (df['fears_loss_connection'] == True)]
print(f"\n3. The Paradox Group:")
print(f"   {len(paradox_group)} people ({len(paradox_group)/len(df)*100:.1f}% of all participants)")
print(f"   are personally open to AI romance BUT fear loss of genuine human connection")

# 4. All fears among romantically open
print("\n4. Top Fears Among Romantically Open to AI:")
all_fears_open = {}
for fears in open_group['fears_list']:
    for fear in fears:
        if fear:
            all_fears_open[fear] = all_fears_open.get(fear, 0) + 1

sorted_fears_open = sorted(all_fears_open.items(), key=lambda x: x[1], reverse=True)
for fear, count in sorted_fears_open[:5]:
    pct = (count / len(open_group)) * 100
    print(f"   - {fear}: {count} ({pct:.1f}%)")

# 5. Compare with companionship users
print("\n5. Romantic Openness by AI Companionship Experience:")
companion_users = df[df['ai_companionship'] == 'Yes']
non_users = df[df['ai_companionship'] == 'No']

print(f"\n   AI Companionship Users (n={len(companion_users)}):")
print(f"   - Romantically open: {companion_users['romantically_open'].sum()} ({companion_users['romantically_open'].mean()*100:.1f}%)")
print(f"   - Fear loss of connection: {companion_users['fears_loss_connection'].sum()} ({companion_users['fears_loss_connection'].mean()*100:.1f}%)")

print(f"\n   Non-Users (n={len(non_users)}):")
print(f"   - Romantically open: {non_users['romantically_open'].sum()} ({non_users['romantically_open'].mean()*100:.1f}%)")
print(f"   - Fear loss of connection: {non_users['fears_loss_connection'].sum()} ({non_users['fears_loss_connection'].mean()*100:.1f}%)")

# 6. Statistical comparison
from scipy.stats import chi2_contingency

# Create contingency table for romantic openness vs fear of loss
contingency = pd.crosstab(df['romantically_open'], df['fears_loss_connection'])
chi2, p_value, dof, expected = chi2_contingency(contingency)

print(f"\n6. Statistical Analysis:")
print(f"   Chi-square test (romantic openness vs fear of loss):")
print(f"   χ² = {chi2:.3f}, p = {p_value:.4f}")
if p_value < 0.05:
    print("   There IS a significant association")
else:
    print("   There is NO significant association")

# 7. Sentiment analysis of paradox group
print("\n7. AI Sentiment of Paradox Group:")
if len(paradox_group) > 0:
    sentiment_counts = paradox_group['ai_sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        pct = (count / len(paradox_group)) * 100
        print(f"   {sentiment}: {count} ({pct:.1f}%)")

# 8. Calculate percentage experiencing different combinations
print("\n8. Combination Analysis:")
total = len(df)
open_no_fear = len(df[(df['romantically_open'] == True) & (df['fears_loss_connection'] == False)])
closed_with_fear = len(df[(df['romantically_closed'] == True) & (df['fears_loss_connection'] == True)])
open_with_fear = len(paradox_group)
closed_no_fear = len(df[(df['romantically_closed'] == True) & (df['fears_loss_connection'] == False)])

print(f"   Open to romance + Fear loss: {open_with_fear} ({open_with_fear/total*100:.1f}%)")
print(f"   Open to romance + No fear loss: {open_no_fear} ({open_no_fear/total*100:.1f}%)")
print(f"   Closed to romance + Fear loss: {closed_with_fear} ({closed_with_fear/total*100:.1f}%)")
print(f"   Closed to romance + No fear loss: {closed_no_fear} ({closed_no_fear/total*100:.1f}%)")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: {len(paradox_group)/len(df)*100:.1f}% experience the paradox -")
print(f"personally open to AI romance while fearing loss of human connection.")
if len(open_group) > 0:
    fear_rate_open = open_group['fears_loss_connection'].mean() * 100
    print(f"{fear_rate_open:.1f}% of romantically open individuals fear connection loss,")
    print("suggesting personal openness coexists with societal concerns.")
print("="*80)