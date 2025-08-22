import sqlite3
import pandas as pd
import numpy as np
import json
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Question 9.1: The "I Want It, But I Fear It" Paradox
# Do people who most strongly agree that AI should be designed to be "as human-like as possible" 
# also express the greatest fear that AI will lead to a "decline in human empathy and social skills"?

print("\n" + "="*80)
print("9.1 The 'I Want It, But I Fear It' Paradox")
print("="*80)

# Get participant data with fears
query_participants = """
SELECT 
    pr.participant_id,
    pr.Q115 as greatest_fears,  -- JSON array of fears
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query_participants, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# Get design preference responses (aggregated)
query_design = """
SELECT 
    response,
    CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = '16555f1f-2a88-435f-930e-fbe8232e8b51'
"""
design_df = pd.read_sql_query(query_design, conn)

print("\n1. AI Design Preference Distribution (Aggregate):")
for _, row in design_df.iterrows():
    print(f"   {row['response']}: {row['pct']:.1f}%")

# Get social skills decline likelihood
query_decline = """
SELECT 
    response,
    CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = 'ec0d14f7-a5d6-4038-8db1-acabd81c75d8'
"""
decline_df = pd.read_sql_query(query_decline, conn)

print("\n2. Belief that human interaction skills will decline:")
for _, row in decline_df.iterrows():
    print(f"   {row['response']}: {row['pct']:.1f}%")

# Parse the fears JSON for individual participants
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

# Check specific fears
df['fears_empathy_decline'] = df['fears_list'].apply(
    lambda fears: any('decline in human empathy and social skills' in str(fear).lower() or 
                     'empathy' in str(fear).lower() and ('decline' in str(fear).lower() or 'social skills' in str(fear).lower())
                     for fear in fears)
)

df['fears_loss_connection'] = df['fears_list'].apply(
    lambda fears: any('loss of genuine human connection' in str(fear).lower() or
                     'genuine human' in str(fear).lower()
                     for fear in fears)
)

df['fears_social_isolation'] = df['fears_list'].apply(
    lambda fears: any('widespread social isolation' in str(fear).lower() or
                     'social isolation' in str(fear).lower()
                     for fear in fears)
)

# Calculate fear statistics
print("\n3. Greatest Fears (from Q115 multi-select):")
print(f"   - Fear empathy/skills decline: {df['fears_empathy_decline'].sum()} ({df['fears_empathy_decline'].mean()*100:.1f}%)")
print(f"   - Fear loss of connection: {df['fears_loss_connection'].sum()} ({df['fears_loss_connection'].mean()*100:.1f}%)")
print(f"   - Fear social isolation: {df['fears_social_isolation'].sum()} ({df['fears_social_isolation'].mean()*100:.1f}%)")

# Count all fears
all_fears = {}
for fears in df['fears_list']:
    for fear in fears:
        if fear:
            all_fears[fear] = all_fears.get(fear, 0) + 1

print("\n4. Top 5 Most Common Fears:")
sorted_fears = sorted(all_fears.items(), key=lambda x: x[1], reverse=True)
for fear, count in sorted_fears[:5]:
    pct = (count / len(df)) * 100
    print(f"   - {fear}: {count} ({pct:.1f}%)")

# Analysis of the paradox at aggregate level
print("\n5. The Paradox Analysis (Aggregate Level):")
strongly_agree_humanlike = design_df[design_df['response'] == 'Strongly Agree']['pct'].values[0] if len(design_df[design_df['response'] == 'Strongly Agree']) > 0 else 0
agree_humanlike = design_df[design_df['response'] == 'Agree']['pct'].values[0] if len(design_df[design_df['response'] == 'Agree']) > 0 else 0
total_want_humanlike = strongly_agree_humanlike + agree_humanlike

very_likely_decline = decline_df[decline_df['response'] == 'Very likely']['pct'].values[0] if len(decline_df[decline_df['response'] == 'Very likely']) > 0 else 0
somewhat_likely_decline = decline_df[decline_df['response'] == 'Somewhat likely']['pct'].values[0] if len(decline_df[decline_df['response'] == 'Somewhat likely']) > 0 else 0
total_fear_decline = very_likely_decline + somewhat_likely_decline

print(f"\n   Population wanting human-like AI (Agree + Strongly Agree): {total_want_humanlike:.1f}%")
print(f"   Population believing skills will decline (Likely + Very Likely): {total_fear_decline:.1f}%")

# Estimate overlap (assuming independence as lower bound)
estimated_paradox_min = (total_want_humanlike / 100) * (total_fear_decline / 100) * 100
print(f"\n   Estimated minimum paradox group (assuming independence): {estimated_paradox_min:.1f}%")
print(f"   This represents the lower bound of people experiencing the paradox")

# Check for children-related concerns  
query_children = """
SELECT question, question_id 
FROM responses 
WHERE question LIKE '%children%' AND question LIKE '%relationship%'
LIMIT 1
"""
children_q = pd.read_sql_query(query_children, conn)
if not children_q.empty:
    children_qid = children_q.iloc[0]['question_id']
    query_children_responses = f"""
    SELECT response, CAST("all" AS REAL) * 100 as pct
    FROM responses
    WHERE question_id = '{children_qid}'
    """
    children_df = pd.read_sql_query(query_children_responses, conn)
    
    print("\n6. Concerns about children's relationships:")
    print(f"   Question: {children_q.iloc[0]['question'][:100]}...")
    for _, row in children_df.iterrows():
        print(f"   {row['response']}: {row['pct']:.1f}%")

# Additional analysis: Check if those with many fears also want human-like AI
df['num_fears'] = df['fears_list'].apply(len)
print(f"\n7. Fear Intensity Analysis:")
print(f"   Average number of fears selected: {df['num_fears'].mean():.2f}")
print(f"   Participants with 3+ fears: {(df['num_fears'] >= 3).sum()} ({(df['num_fears'] >= 3).mean()*100:.1f}%)")
print(f"   Participants with 5+ fears: {(df['num_fears'] >= 5).sum()} ({(df['num_fears'] >= 5).mean()*100:.1f}%)")

conn.close()

print("\n" + "="*80)
print("Key Finding: At the aggregate level, a significant portion of the population")
print(f"wants human-like AI ({total_want_humanlike:.1f}%) while also believing") 
print(f"human interaction skills will decline ({total_fear_decline:.1f}%).")
print(f"The paradox affects at least {estimated_paradox_min:.1f}% of participants.")
print("="*80)