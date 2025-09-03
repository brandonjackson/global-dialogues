import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database with read-only mode
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Question IDs from mapping
QUESTION_IDS = {
    'Q39_language': 'd33d3a8f-817f-464c-9fb3-50ed96c1d48c',  # Animal language
    'Q40_emotion': '874762a8-dc8f-44c2-b815-383147ffcb2f',   # Animal emotion  
    'Q41_culture': 'fe992270-ffe7-4e20-93f6-12c71be79ad7',   # Animal culture
    'Q44_impact': '22656d2a-8284-4bee-8c5a-11de280fe9c6',    # Impact of knowing
    'Q45_feeling': '20043bb7-adb9-4e36-866f-becd7f3f7c7d',   # How does it make you feel
    'Q35_caring': '9641f2fa-0622-4172-93d9-6f1452de9e41',    # Caring for animals
    'Q37_observing': 'c1a66a5d-5389-45d3-8bef-c99cf0e5a1a4', # Observing animals
    'Q48_imagine': 'c5d4780d-c202-429f-abcb-e4e93b3ec282',   # Imagine animal senses
    'Q50_important': '2cbc3472-c993-4fdf-b6e2-529b240e4ccb'  # Importance of understanding
}

print("=" * 80)
print("SECTION 3: BELIEFS ABOUT ANIMAL COGNITION AND COMMUNICATION")
print("=" * 80)

# Question 3.1: Animal Capacities
print("\n3.1. Animal Capacities")
print("-" * 40)

query_31 = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id  
    WHERE p.pri_score >= 0.3
)
SELECT 
    question,
    response,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY question), 2) as percentage
FROM responses r
JOIN reliable_participants rp ON r.participant_id = rp.participant_id
WHERE question_id IN (
    'd33d3a8f-817f-464c-9fb3-50ed96c1d48c',  -- language
    '874762a8-dc8f-44c2-b815-383147ffcb2f',  -- emotion
    'fe992270-ffe7-4e20-93f6-12c71be79ad7'   -- culture
)
GROUP BY question, response
ORDER BY question, 
    CASE response 
        WHEN 'Strongly believe' THEN 1
        WHEN 'Believe' THEN 2
        WHEN 'Not sure' THEN 3
        WHEN 'Disbelieve' THEN 4
        WHEN 'Strongly disbelieve' THEN 5
        ELSE 6
    END
"""

df_31 = pd.read_sql_query(query_31, conn)
print("\nPercentage who 'Strongly believe' in animal capacities:")
for _, row in df_31[df_31['response'] == 'Strongly believe'].iterrows():
    capacity = row['question'].split('forms of ')[-1].rstrip('?')
    print(f"  {capacity.capitalize()}: {row['percentage']:.1f}%")

# Question 3.2: Impact of New Information  
print("\n3.2. Impact of New Information")
print("-" * 40)

query_32 = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
)
SELECT 
    response,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM responses r
JOIN reliable_participants rp ON r.participant_id = rp.participant_id
WHERE question_id = '22656d2a-8284-4bee-8c5a-11de280fe9c6'  -- Q44
GROUP BY response
ORDER BY 
    CASE response
        WHEN 'A great deal' THEN 1
        WHEN 'Noticeably' THEN 2
        WHEN 'A bit' THEN 3
        WHEN 'A little' THEN 4
        WHEN 'Not at all' THEN 5
        ELSE 6
    END
"""

df_32 = pd.read_sql_query(query_32, conn)
print("\nDistribution of impact from scientific facts:")
for _, row in df_32.iterrows():
    print(f"  {row['response']}: {row['percentage']:.1f}% (n={row['count']})")

# Question 3.3: Beliefs and Animal Encounters
print("\n3.3. Beliefs and Animal Encounters")
print("-" * 40)

query_33 = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
),
caring_frequency AS (
    SELECT 
        participant_id,
        response as caring_freq
    FROM responses
    WHERE question_id = '9641f2fa-0622-4172-93d9-6f1452de9e41'  -- Q35 caring
),
observing_frequency AS (
    SELECT 
        participant_id,
        response as observing_freq
    FROM responses
    WHERE question_id = 'c1a66a5d-5389-45d3-8bef-c99cf0e5a1a4'  -- Q37 observing
),
belief_scores AS (
    SELECT 
        participant_id,
        AVG(CASE 
            WHEN response = 'Strongly believe' THEN 5
            WHEN response = 'Believe' THEN 4
            WHEN response = 'Not sure' THEN 3
            WHEN response = 'Disbelieve' THEN 2
            WHEN response = 'Strongly disbelieve' THEN 1
            ELSE NULL
        END) as avg_belief_score
    FROM responses
    WHERE question_id IN (
        'd33d3a8f-817f-464c-9fb3-50ed96c1d48c',  -- language
        '874762a8-dc8f-44c2-b815-383147ffcb2f',  -- emotion
        'fe992270-ffe7-4e20-93f6-12c71be79ad7'   -- culture
    )
    GROUP BY participant_id
)
SELECT 
    cf.caring_freq,
    COUNT(*) as n,
    ROUND(AVG(bs.avg_belief_score), 2) as avg_belief
FROM reliable_participants rp
JOIN caring_frequency cf ON rp.participant_id = cf.participant_id
JOIN belief_scores bs ON rp.participant_id = bs.participant_id
WHERE cf.caring_freq IS NOT NULL
GROUP BY cf.caring_freq
ORDER BY 
    CASE cf.caring_freq
        WHEN 'Daily' THEN 1
        WHEN 'Weekly' THEN 2
        WHEN 'Monthly' THEN 3
        WHEN 'Rarely' THEN 4
        WHEN 'Never' THEN 5
        ELSE 6
    END
"""

df_33_caring = pd.read_sql_query(query_33, conn)
print("\nAverage belief score (1-5) by caring frequency:")
for _, row in df_33_caring.iterrows():
    print(f"  {row['caring_freq']}: {row['avg_belief']:.2f} (n={row['n']})")

# Similar analysis for observing
query_33_obs = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
),
observing_frequency AS (
    SELECT 
        participant_id,
        response as observing_freq
    FROM responses
    WHERE question_id = 'c1a66a5d-5389-45d3-8bef-c99cf0e5a1a4'  -- Q37 observing
),
belief_scores AS (
    SELECT 
        participant_id,
        AVG(CASE 
            WHEN response = 'Strongly believe' THEN 5
            WHEN response = 'Believe' THEN 4
            WHEN response = 'Not sure' THEN 3
            WHEN response = 'Disbelieve' THEN 2
            WHEN response = 'Strongly disbelieve' THEN 1
            ELSE NULL
        END) as avg_belief_score
    FROM responses
    WHERE question_id IN (
        'd33d3a8f-817f-464c-9fb3-50ed96c1d48c',  -- language
        '874762a8-dc8f-44c2-b815-383147ffcb2f',  -- emotion
        'fe992270-ffe7-4e20-93f6-12c71be79ad7'   -- culture
    )
    GROUP BY participant_id
)
SELECT 
    of.observing_freq,
    COUNT(*) as n,
    ROUND(AVG(bs.avg_belief_score), 2) as avg_belief
FROM reliable_participants rp
JOIN observing_frequency of ON rp.participant_id = of.participant_id
JOIN belief_scores bs ON rp.participant_id = bs.participant_id
WHERE of.observing_freq IS NOT NULL
GROUP BY of.observing_freq
ORDER BY 
    CASE of.observing_freq
        WHEN 'Daily' THEN 1
        WHEN 'Weekly' THEN 2
        WHEN 'Monthly' THEN 3
        WHEN 'Rarely' THEN 4
        WHEN 'Never' THEN 5
        ELSE 6
    END
"""
df_33_obs = pd.read_sql_query(query_33_obs, conn)
print("\nAverage belief score (1-5) by observing frequency:")
for _, row in df_33_obs.iterrows():
    print(f"  {row['observing_freq']}: {row['avg_belief']:.2f} (n={row['n']})")

# Question 3.4: Does Knowing More Change How We Feel?
print("\n3.4. Does Knowing More Change How We Feel?")
print("-" * 40)

# First get Q45 question ID
query_45_id = """
SELECT DISTINCT question_id 
FROM responses 
WHERE question LIKE '%How does this knowledge make you feel%'
LIMIT 1
"""
df_45_id = pd.read_sql_query(query_45_id, conn)
if not df_45_id.empty:
    q45_id = df_45_id.iloc[0]['question_id']
else:
    q45_id = '20043bb7-adb9-4e36-866f-becd7f3f7c7d'  # fallback

query_34 = f"""
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
),
great_impact AS (
    SELECT participant_id
    FROM responses
    WHERE question_id = '22656d2a-8284-4bee-8c5a-11de280fe9c6'  -- Q44
    AND response = 'A great deal'
)
SELECT 
    r.response as emotion,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM responses r
JOIN reliable_participants rp ON r.participant_id = rp.participant_id
JOIN great_impact gi ON r.participant_id = gi.participant_id
WHERE r.question_id = '{q45_id}'  -- Q45
GROUP BY r.response
ORDER BY count DESC
"""

df_34 = pd.read_sql_query(query_34, conn)
print("\nAmong those whose perspective changed 'A great deal', emotions reported:")
for _, row in df_34.iterrows():
    print(f"  {row['emotion']}: {row['percentage']:.1f}% (n={row['count']})")

# Question 3.5: Importance of "Umwelt"
print("\n3.5. Importance of 'Umwelt'")
print("-" * 40)

query_35 = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
),
importance AS (
    SELECT 
        participant_id,
        response as importance_level
    FROM responses
    WHERE question_id = '2cbc3472-c993-4fdf-b6e2-529b240e4ccb'  -- Q50
),
imagination AS (
    SELECT 
        participant_id,
        response as imagine_freq
    FROM responses
    WHERE question_id = 'c5d4780d-c202-429f-abcb-e4e93b3ec282'  -- Q48
)
SELECT 
    im.imagine_freq,
    imp.importance_level,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY im.imagine_freq), 2) as percentage
FROM reliable_participants rp
JOIN importance imp ON rp.participant_id = imp.participant_id
JOIN imagination im ON rp.participant_id = im.participant_id
WHERE imp.importance_level = 'Very important'
GROUP BY im.imagine_freq, imp.importance_level
ORDER BY 
    CASE im.imagine_freq
        WHEN 'Often' THEN 1
        WHEN 'Sometimes' THEN 2
        WHEN 'Rarely' THEN 3
        WHEN 'Never' THEN 4
        ELSE 5
    END
"""

df_35 = pd.read_sql_query(query_35, conn)
print("\nPercentage who think understanding animal umwelt is 'Very important' by imagination frequency:")
for _, row in df_35.iterrows():
    print(f"  {row['imagine_freq']}: {row['percentage']:.1f}% (n={row['count']})")

# Overall importance distribution
query_35_overall = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
)
SELECT 
    response,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM responses r
JOIN reliable_participants rp ON r.participant_id = rp.participant_id
WHERE question_id = '2cbc3472-c993-4fdf-b6e2-529b240e4ccb'  -- Q50
GROUP BY response
ORDER BY 
    CASE response
        WHEN 'Very important' THEN 1
        WHEN 'Important' THEN 2
        WHEN 'Somewhat important' THEN 3
        WHEN 'Not very important' THEN 4
        WHEN 'Not at all important' THEN 5
        ELSE 6
    END
"""

df_35_overall = pd.read_sql_query(query_35_overall, conn)
print("\nOverall distribution of importance of understanding animal experience:")
for _, row in df_35_overall.iterrows():
    print(f"  {row['response']}: {row['percentage']:.1f}% (n={row['count']})")

# Statistical tests
print("\n" + "=" * 80)
print("STATISTICAL ANALYSIS")
print("=" * 80)

# Correlation between imagination frequency and importance
query_corr = """
WITH reliable_participants AS (
    SELECT DISTINCT r.participant_id
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
),
coded_data AS (
    SELECT 
        imp.participant_id,
        CASE im.response
            WHEN 'Often' THEN 4
            WHEN 'Sometimes' THEN 3
            WHEN 'Rarely' THEN 2
            WHEN 'Never' THEN 1
            ELSE NULL
        END as imagine_score,
        CASE imp.response
            WHEN 'Very important' THEN 5
            WHEN 'Important' THEN 4
            WHEN 'Somewhat important' THEN 3
            WHEN 'Not very important' THEN 2
            WHEN 'Not at all important' THEN 1
            ELSE NULL
        END as importance_score
    FROM reliable_participants rp
    JOIN responses imp ON rp.participant_id = imp.participant_id
    JOIN responses im ON rp.participant_id = im.participant_id
    WHERE imp.question_id = '2cbc3472-c993-4fdf-b6e2-529b240e4ccb'  -- Q50
    AND im.question_id = 'c5d4780d-c202-429f-abcb-e4e93b3ec282'  -- Q48
)
SELECT 
    imagine_score,
    importance_score
FROM coded_data
WHERE imagine_score IS NOT NULL 
AND importance_score IS NOT NULL
"""

df_corr = pd.read_sql_query(query_corr, conn)
if len(df_corr) > 10:
    correlation, p_value = stats.spearmanr(df_corr['imagine_score'], df_corr['importance_score'])
    print(f"\nCorrelation between imagination frequency and perceived importance:")
    print(f"  Spearman's rho = {correlation:.3f}, p = {p_value:.4f}")
    print(f"  n = {len(df_corr)}")

conn.close()
print("\n" + "=" * 80)
print("Analysis complete for Section 3")
print("=" * 80)