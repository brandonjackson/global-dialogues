#!/usr/bin/env python3
"""
Deep investigation of Section 15 data structure issues
"""

import sqlite3
import pandas as pd
import json

conn = sqlite3.connect('../../../Data/GD5/GD5.db')

print("Investigating Section 15 Data Structure Issues")
print("=" * 50)

# Check Q48 structure (umwelt imagination)
print("\nQ48 (Umwelt Imagination) Structure:")
q48_query = """
SELECT Q48, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY Q48
ORDER BY count DESC
LIMIT 10
"""
q48_df = pd.read_sql_query(q48_query, conn)
print(q48_df)

# Check Q50 structure (importance)
print("\nQ50 (Importance) Structure:")
q50_query = """
SELECT Q50, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY Q50
ORDER BY count DESC
LIMIT 10
"""
q50_df = pd.read_sql_query(q50_query, conn)
print(q50_df)

# Check Q45 structure (emotions)
print("\nQ45 (Emotions) Structure:")
q45_query = """
SELECT Q45, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY Q45
ORDER BY count DESC
LIMIT 15
"""
q45_df = pd.read_sql_query(q45_query, conn)
print(q45_df)

# Try to parse Q45 as JSON
print("\n\nParsing Q45 as JSON arrays:")
q45_all = """
SELECT pr.participant_id, pr.Q45
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND Q45 IS NOT NULL
"""
q45_data = pd.read_sql_query(q45_all, conn)

# Count individual emotions
emotion_counts = {}
for _, row in q45_data.iterrows():
    try:
        emotions = json.loads(row['Q45'])
        if isinstance(emotions, list):
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    except:
        # Try as single value
        emotion = row['Q45']
        if emotion:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

print("Individual emotion counts (parsed from arrays):")
for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {emotion}: {count} ({count/len(q45_data)*100:.1f}%)")

# Check if people marking "Unsettled" exist
unsettled_count = 0
for _, row in q45_data.iterrows():
    try:
        emotions = json.loads(row['Q45'])
        if isinstance(emotions, list) and 'Unsettled' in emotions:
            unsettled_count += 1
    except:
        if row['Q45'] == 'Unsettled':
            unsettled_count += 1

print(f"\nTotal participants with 'Unsettled' emotion: {unsettled_count}")

# Check Q48 for "Often" or "Very often" responses
print("\n\nQ48 Frequent Imaginers Investigation:")
q48_often = """
SELECT COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND (Q48 = 'Often' OR Q48 = 'Very often' 
         OR Q48 LIKE '%Often%' OR Q48 LIKE '%Very often%')
"""
often_count = pd.read_sql_query(q48_often, conn)
print(f"Participants with 'Often' or 'Very often': {often_count['count'].iloc[0]}")

# Sample some Q48 values to understand format
print("\nSample Q48 values:")
q48_sample = """
SELECT Q48 FROM participant_responses 
WHERE Q48 IS NOT NULL 
LIMIT 20
"""
samples = pd.read_sql_query(q48_sample, conn)
for val in samples['Q48'].unique()[:10]:
    print(f"  '{val}'")

conn.close()