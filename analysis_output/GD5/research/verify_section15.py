#!/usr/bin/env python3
"""
Verification script for Section 15 findings
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

print("Verifying Section 15 findings...")
print("=" * 50)

# Question 15.1: Umwelt imagination and importance
print("\nQuestion 15.1: Umwelt Imagination")
print("-" * 30)

umwelt_query = """
SELECT 
    pr.Q48 as imagination_freq,
    pr.Q50 as importance_rating,
    pr.Q73 as legal_rep,
    pr.Q77 as democratic_participation
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q48 IS NOT NULL
    AND pr.Q50 IS NOT NULL
"""
umwelt_df = pd.read_sql_query(umwelt_query, conn)

# Map to numeric for correlation
freq_map = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4, 'Very often': 5}
import_map = {'Not important': 1, 'Somewhat unimportant': 2, 'Neutral': 3, 'Somewhat important': 4, 'Very important': 5}

umwelt_df['freq_numeric'] = umwelt_df['imagination_freq'].map(freq_map)
umwelt_df['import_numeric'] = umwelt_df['importance_rating'].map(import_map)

# Calculate correlation
valid_data = umwelt_df.dropna(subset=['freq_numeric', 'import_numeric'])
if len(valid_data) > 1:
    corr, p_val = stats.spearmanr(valid_data['freq_numeric'], valid_data['import_numeric'])
    print(f"Spearman correlation: r={corr:.3f}, p={p_val:.6f}, n={len(valid_data)}")

# Frequent imaginers analysis
frequent = umwelt_df[umwelt_df['imagination_freq'].isin(['Often', 'Very often'])]
others = umwelt_df[~umwelt_df['imagination_freq'].isin(['Often', 'Very often'])]

print(f"\nFrequent imaginers: {len(frequent)} ({len(frequent)/len(umwelt_df)*100:.1f}%)")
print(f"Others: {len(others)}")

# Importance ratings
freq_very_important = (frequent['importance_rating'] == 'Very important').sum()
others_very_important = (others['importance_rating'] == 'Very important').sum()
print(f"\nRate as 'Very important':")
print(f"  Frequent imaginers: {freq_very_important}/{len(frequent)} ({freq_very_important/len(frequent)*100:.1f}%)")
print(f"  Others: {others_very_important}/{len(others)} ({others_very_important/len(others)*100:.1f}%)")

# Question 15.2: Emotions and restrictions
print("\n\nQuestion 15.2: Emotions and Restrictions")
print("-" * 30)

emotions_query = """
SELECT 
    pr.Q45 as emotion,
    pr.Q82 as professional_restriction,
    pr.Q83 as public_access,
    pr.Q84 as company_regulation,
    pr.Q85 as prohibited_uses
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
"""
emotions_df = pd.read_sql_query(emotions_query, conn)

# Count emotions
emotion_counts = emotions_df['emotion'].value_counts()
print("\nEmotion distribution:")
for emotion, count in emotion_counts.head(10).items():
    print(f"  {emotion}: {count} ({count/len(emotions_df)*100:.1f}%)")

# Focus on key emotions
unsettled = emotions_df[emotions_df['emotion'] == 'Unsettled']
curious = emotions_df[emotions_df['emotion'] == 'Curious']
connected = emotions_df[emotions_df['emotion'] == 'Connected']

print(f"\nUnsettled: {len(unsettled)}")
print(f"Curious: {len(curious)}")
print(f"Connected: {len(connected)}")

# Company regulation support
if len(unsettled) > 0:
    unsettled_reg = unsettled['company_regulation'].isin(['Strongly agree', 'Somewhat agree']).sum()
    print(f"\nCompany regulation support:")
    print(f"  Unsettled: {unsettled_reg}/{len(unsettled)} ({unsettled_reg/len(unsettled)*100:.0f}%)")
    
if len(curious) > 0:
    curious_reg = curious['company_regulation'].isin(['Strongly agree', 'Somewhat agree']).sum()
    print(f"  Curious: {curious_reg}/{len(curious)} ({curious_reg/len(curious)*100:.0f}%)")

# Question 15.3: Emotions and radical governance
print("\n\nQuestion 15.3: Emotions and Radical Governance")
print("-" * 30)

governance_query = """
SELECT 
    pr.Q45 as emotion,
    pr.Q76 as ai_society,
    pr.Q77 as democratic_participation
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    AND pr.Q76 IS NOT NULL
"""
governance_df = pd.read_sql_query(governance_query, conn)

# AI society appeal by emotion
for emotion in ['Connected', 'Curious', 'Protective', 'Unchanged']:
    emotion_data = governance_df[governance_df['emotion'] == emotion]
    if len(emotion_data) > 0:
        appealing = emotion_data['ai_society'].isin(['Very appealing', 'Somewhat appealing']).sum()
        very_appealing = (emotion_data['ai_society'] == 'Very appealing').sum()
        print(f"\n{emotion} (n={len(emotion_data)}):")
        print(f"  Find AI society appealing: {appealing}/{len(emotion_data)} ({appealing/len(emotion_data)*100:.1f}%)")
        print(f"  Very appealing: {very_appealing} ({very_appealing/len(emotion_data)*100:.1f}%)")

# Democratic participation support
demo_support_query = """
SELECT 
    pr.Q45 as emotion,
    CASE 
        WHEN pr.Q77 LIKE '%should not be able to participate%' THEN 'No'
        ELSE 'Yes'
    END as supports_participation,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q45 IN ('Connected', 'Curious', 'Protective', 'Unchanged')
    AND pr.Q77 IS NOT NULL
GROUP BY pr.Q45, supports_participation
"""
demo_df = pd.read_sql_query(demo_support_query, conn)

print("\n\nDemocratic Participation Support:")
for emotion in ['Connected', 'Curious', 'Protective', 'Unchanged']:
    emotion_data = demo_df[demo_df['emotion'] == emotion]
    if len(emotion_data) > 0:
        total = emotion_data['count'].sum()
        yes_count = emotion_data[emotion_data['supports_participation'] == 'Yes']['count'].sum() if 'Yes' in emotion_data['supports_participation'].values else 0
        print(f"  {emotion}: {yes_count}/{total} ({yes_count/total*100:.1f}% support)")

conn.close()

print("\n" + "=" * 50)
print("Verification complete!")