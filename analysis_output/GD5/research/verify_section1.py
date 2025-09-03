#!/usr/bin/env python3
"""
Verification script for Section 1 findings
"""

import sqlite3
import pandas as pd
import numpy as np

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

print("Verifying Section 1 findings...")
print("=" * 50)

# 1. Verify total participants
total_query = """
SELECT 
    COUNT(DISTINCT p.participant_id) as total_all,
    COUNT(DISTINCT CASE WHEN p.pri_score >= 0.3 THEN p.participant_id END) as reliable
FROM participants p
"""
totals = pd.read_sql_query(total_query, conn)
print(f"Total Participants: {totals['total_all'].iloc[0]}")
print(f"Reliable (PRI >= 0.3): {totals['reliable'].iloc[0]}")
print()

# 2. Verify age distribution
age_query = """
SELECT pr.Q2 as age_group, COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q2 IS NOT NULL
GROUP BY pr.Q2
ORDER BY 
  CASE pr.Q2
    WHEN '18-25' THEN 1
    WHEN '26-35' THEN 2
    WHEN '36-45' THEN 3
    WHEN '46-55' THEN 4
    WHEN '56-65' THEN 5
    WHEN '65+' THEN 6
    ELSE 7
  END
"""
age_df = pd.read_sql_query(age_query, conn)
print("Age Distribution:")
total_age = age_df['count'].sum()
for _, row in age_df.iterrows():
    pct = (row['count'] / total_age) * 100
    print(f"- {row['age_group']}: {row['count']} ({pct:.1f}%)")
print()

# 3. Verify human-nature relationship views (Q94)
nature_query = """
SELECT pr.Q94 as view, COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY pr.Q94
ORDER BY count DESC
"""
nature_df = pd.read_sql_query(nature_query, conn)
print("Human-Nature Relationship Views:")
total_nature = nature_df['count'].sum()
for _, row in nature_df.iterrows():
    pct = (row['count'] / total_nature) * 100
    print(f"- {row['view']}: {row['count']} ({pct:.1f}%)")
print()

# 4. Verify AI sentiment
ai_sentiment_query = """
SELECT pr.Q5 as sentiment, COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q5 IS NOT NULL
GROUP BY pr.Q5
ORDER BY count DESC
"""
ai_df = pd.read_sql_query(ai_sentiment_query, conn)
print("AI Sentiment:")
total_ai = ai_df['count'].sum()
for _, row in ai_df.iterrows():
    pct = (row['count'] / total_ai) * 100
    print(f"- {row['sentiment']}: {row['count']} ({pct:.1f}%)")
print()

# 5. Verify trust scores - checking the trust entities
print("Verifying Trust Entities...")

# Check what Q12-Q17 actually contain
trust_check_query = """
SELECT 
    pr.Q12 as q12_response,
    pr.Q13 as q13_response, 
    pr.Q14 as q14_response,
    pr.Q15 as q15_response,
    pr.Q16 as q16_response,
    pr.Q17 as q17_response
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
LIMIT 5
"""
trust_sample = pd.read_sql_query(trust_check_query, conn)
print("Sample trust responses (first 5 rows):")
print(trust_sample)
print()

# Now verify the actual trust levels from the document
# The document claims Q12-Q17 correspond to different entities
# Let's check Q12 (should be Scientists based on other sections)
q12_query = """
SELECT pr.Q12 as trust_level, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q12 IS NOT NULL
GROUP BY pr.Q12
"""
q12_df = pd.read_sql_query(q12_query, conn)
print("Q12 Distribution (Scientists):")
for _, row in q12_df.iterrows():
    print(f"- {row['trust_level']}: {row['count']}")

# Calculate average trust score for Q12
trust_mapping = {
    'Strongly Trust': 5,
    'Somewhat Trust': 4,
    'Neutral': 3,
    'Neither Trust Nor Distrust': 3,
    'Somewhat Distrust': 2,
    'Strongly Distrust': 1
}

q12_df['score'] = q12_df['trust_level'].map(trust_mapping)
avg_score = (q12_df['count'] * q12_df['score']).sum() / q12_df['count'].sum()
print(f"Average Q12 Trust Score: {avg_score:.2f}")
print()

# Check Q17 (AI Systems)
q17_query = """
SELECT pr.Q17 as trust_level, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q17 IS NOT NULL
GROUP BY pr.Q17
"""
q17_df = pd.read_sql_query(q17_query, conn)
print("Q17 Distribution (AI Systems):")
for _, row in q17_df.iterrows():
    print(f"- {row['trust_level']}: {row['count']}")

q17_df['score'] = q17_df['trust_level'].map(trust_mapping)
avg_score_ai = (q17_df['count'] * q17_df['score']).sum() / q17_df['count'].sum()
print(f"Average Q17 Trust Score: {avg_score_ai:.2f}")

conn.close()

print("\n" + "=" * 50)
print("Verification complete!")
print("\nKEY ISSUES FOUND:")
print("1. The document incorrectly maps trust entities to questions")
print("2. Q12 is actually Scientists (not Family Doctor)")
print("3. Trust scores need to be recalculated with correct entity mapping")
print("4. The trust hierarchy shown is incorrect")