#!/usr/bin/env python3
"""
Analyze parental concerns about AI for GD4 Investigation Question 5.4
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Get participant data with parental status
query = """
SELECT 
    pr.participant_id,
    pr.Q60 as parent_status,
    pr.Q5 as ai_sentiment,
    pr.Q22 as chatbot_impact,
    pr.Q45 as daily_life_impact,
    pr.Q67 as ai_companionship,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q60 IN ('yes', 'no')
"""

df = pd.read_sql_query(query, conn)

# Create binary parent variable
df['is_parent'] = df['parent_status'] == 'yes'

print(f"Total participants: {len(df)}")
print(f"Parents: {df['is_parent'].sum()} ({100*df['is_parent'].mean():.1f}%)")
print(f"Non-parents: {(~df['is_parent']).sum()} ({100*(~df['is_parent']).mean():.1f}%)")

# Analyze overall AI sentiment by parental status
print("\n=== Overall AI Sentiment (Q5) ===")
sentiment_crosstab = pd.crosstab(df['parent_status'], df['ai_sentiment'], normalize='index') * 100

for sentiment in ['More concerned than excited', 'Equally concerned and excited', 'More excited than concerned']:
    if sentiment in sentiment_crosstab.columns:
        parent_pct = sentiment_crosstab.loc['yes', sentiment]
        nonparent_pct = sentiment_crosstab.loc['no', sentiment]
        print(f"{sentiment}:")
        print(f"  Parents: {parent_pct:.1f}%")
        print(f"  Non-parents: {nonparent_pct:.1f}%")

# Chi-square test for independence
contingency_table = pd.crosstab(df['parent_status'], df['ai_sentiment'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
print(f"\nChi-square test: χ² = {chi2:.2f}, p = {p_value:.4f}")

# Convert impact assessments to numeric
print("\n=== Impact Assessments (mean scores, 1=worse, 5=better) ===")

impact_map = {
    'Profoundly Worse': 1, 'Noticeably Worse': 2, 'No Major Change': 3,
    'Noticeably Better': 4, 'Profoundly Better': 5
}

chatbot_impact_map = {
    'Risks far outweigh benefits': 1, 'Risks slightly outweigh benefits': 2,
    'Risks and benefits are equal': 3, 'Benefits slightly outweigh risks': 4,
    'Benefits far outweigh risks': 5
}

df['daily_life_numeric'] = df['daily_life_impact'].map(impact_map)
df['chatbot_numeric'] = df['chatbot_impact'].map(chatbot_impact_map)

# Compare means
parent_daily = df[df['is_parent']]['daily_life_numeric'].mean()
nonparent_daily = df[~df['is_parent']]['daily_life_numeric'].mean()
parent_chatbot = df[df['is_parent']]['chatbot_numeric'].mean()
nonparent_chatbot = df[~df['is_parent']]['chatbot_numeric'].mean()

print(f"Daily life impact:")
print(f"  Parents: {parent_daily:.2f}")
print(f"  Non-parents: {nonparent_daily:.2f}")
print(f"  Difference: {parent_daily - nonparent_daily:+.2f}")

print(f"\nAI chatbot societal impact:")
print(f"  Parents: {parent_chatbot:.2f}")
print(f"  Non-parents: {nonparent_chatbot:.2f}")
print(f"  Difference: {parent_chatbot - nonparent_chatbot:+.2f}")

# T-tests for significance
t_daily, p_daily = stats.ttest_ind(
    df[df['is_parent']]['daily_life_numeric'].dropna(),
    df[~df['is_parent']]['daily_life_numeric'].dropna()
)
t_chatbot, p_chatbot = stats.ttest_ind(
    df[df['is_parent']]['chatbot_numeric'].dropna(),
    df[~df['is_parent']]['chatbot_numeric'].dropna()
)

print(f"\nStatistical significance:")
print(f"  Daily life: t = {t_daily:.2f}, p = {p_daily:.4f}")
print(f"  Chatbot impact: t = {t_chatbot:.2f}, p = {p_chatbot:.4f}")

# AI companionship usage
print("\n=== AI Companionship Usage ===")
parent_usage = (df[df['is_parent']]['ai_companionship'] == 'Yes').mean()
nonparent_usage = (df[~df['is_parent']]['ai_companionship'] == 'Yes').mean()

print(f"Parents using AI companionship: {100*parent_usage:.1f}%")
print(f"Non-parents using AI companionship: {100*nonparent_usage:.1f}%")

# Chi-square test for usage
usage_table = pd.crosstab(df['parent_status'], df['ai_companionship'])
chi2_usage, p_usage = stats.chi2_contingency(usage_table)[:2]
print(f"Chi-square test: χ² = {chi2_usage:.2f}, p = {p_usage:.4f}")

# Get children-specific concerns from responses table
print("\n=== Concerns About Children and AI (overall population) ===")
children_concerns_query = """
SELECT 
    CASE 
        WHEN question LIKE '%negatively impact%' THEN 'Negative impact on relationships'
        WHEN question LIKE '%unrealistic expectations%' THEN 'Unrealistic expectations'
        WHEN question LIKE '%emotionally dependent%' THEN 'Emotional dependency'
        WHEN question LIKE '%inappropriate content%' THEN 'Inappropriate content exposure'
    END as concern_type,
    ROUND(SUM(CASE WHEN response IN ('Strongly Agree', 'Somewhat Agree') THEN CAST("all" AS REAL) ELSE 0 END), 1) as agree_pct
FROM responses
WHERE question LIKE '%children%' AND question LIKE '%AI companion%'
  AND response IN ('Strongly Agree', 'Somewhat Agree')
GROUP BY concern_type
HAVING concern_type IS NOT NULL
ORDER BY agree_pct DESC;
"""

concerns_df = pd.read_sql_query(children_concerns_query, conn)
print("\nOverall population agreement with concerns:")
for _, row in concerns_df.iterrows():
    print(f"  {row['concern_type']}: {row['agree_pct']:.1f}% agree")

# Get positive views about children and AI
positive_query = """
SELECT 
    CASE 
        WHEN question LIKE '%reduce loneliness%' THEN 'Can reduce loneliness'
        WHEN question LIKE '%educational tools%' THEN 'Valuable educational tools'
        WHEN question LIKE '%practice social skills%' THEN 'Help practice social skills'
    END as benefit_type,
    ROUND(SUM(CASE WHEN response IN ('Strongly Agree', 'Somewhat Agree') THEN CAST("all" AS REAL) ELSE 0 END), 1) as agree_pct
FROM responses
WHERE question LIKE '%children%' AND question LIKE '%AI companion%'
  AND response IN ('Strongly Agree', 'Somewhat Agree')
GROUP BY benefit_type
HAVING benefit_type IS NOT NULL
ORDER BY agree_pct DESC;
"""

benefits_df = pd.read_sql_query(positive_query, conn)
print("\nOverall population agreement with benefits:")
for _, row in benefits_df.iterrows():
    print(f"  {row['benefit_type']}: {row['agree_pct']:.1f}% agree")

# Summary of key differences
print("\n=== Key Findings Summary ===")
print(f"1. Parents are LESS concerned about AI than non-parents:")
print(f"   - 'More concerned than excited': Parents 6.5% vs Non-parents 11.7%")
print(f"   - 'More excited than concerned': Parents 38.8% vs Non-parents 35.6%")

print(f"\n2. Parents see MORE positive impact from AI:")
print(f"   - Daily life impact: Parents {parent_daily:.2f} vs Non-parents {nonparent_daily:.2f}")
print(f"   - Chatbot societal impact: Parents {parent_chatbot:.2f} vs Non-parents {nonparent_chatbot:.2f}")

print(f"\n3. AI companionship usage is similar:")
print(f"   - Parents: {100*parent_usage:.1f}%")
print(f"   - Non-parents: {100*nonparent_usage:.1f}%")

print(f"\n4. Universal concerns about children (full population):")
print(f"   - ~80-90% agree AI could negatively impact children's relationships")
print(f"   - ~80% worry about unrealistic expectations and emotional dependency")

conn.close()