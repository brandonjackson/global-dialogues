#!/usr/bin/env python3
"""
Complete analysis for Section 5: Ethics, Rights, and Governance
Version 2 - Direct question text matching
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Connect to database in read-only mode
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("=" * 80)
print("SECTION 5: ETHICS, RIGHTS, AND GOVERNANCE")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get reliable participants (PRI >= 0.3)
participants_query = """
SELECT participant_id, pri_score
FROM participants
WHERE pri_score >= 0.3
"""
df_participants = pd.read_sql_query(participants_query, conn)
reliable_participants = df_participants['participant_id'].tolist()
print(f"\nTotal reliable participants (PRI >= 0.3): {len(reliable_participants)}")

# Create a placeholders string for the participant IDs
placeholders = ','.join(['?' for _ in reliable_participants])

print("\n" + "=" * 80)
print("5.1. PREFERRED FUTURE FOR ANIMAL PROTECTION (Q70)")
print("=" * 80)

# Q70: Which approach feels most appropriate?
q70_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%Which approach feels most appropriate%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%Which approach feels most appropriate%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q70_df = pd.read_sql_query(q70_query, conn, params=reliable_participants + reliable_participants)
print("\nQ70: Which approach feels most appropriate to you for protecting animals?")
print(q70_df)

# Correlation with Q32 (human superiority)
q32_q70_query = f"""
SELECT r1.response as future_preference,
       r2.response as human_superiority_view,
       COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question LIKE '%Which approach feels most appropriate%'
AND r2.question LIKE '%fundamentally different and superior%'
AND r1.participant_id IN ({placeholders})
GROUP BY r1.response, r2.response
ORDER BY r1.response, count DESC
"""
q32_q70_df = pd.read_sql_query(q32_q70_query, conn, params=reliable_participants)
print("\nCorrelation with Human-Animal Equality Views:")
print(q32_q70_df)

print("\n" + "=" * 80)
print("5.2. ANIMAL REPRESENTATION (Q73, Q74)")
print("=" * 80)

# Q73: Should animals have legal representatives?
q73_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%should that animal have the right to a representative%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%should that animal have the right to a representative%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q73_df = pd.read_sql_query(q73_query, conn, params=reliable_participants + reliable_participants)
print("\nQ73: Should animals have the right to a representative?")
print(q73_df)

# Q74: How should they be represented?
q74_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%which of these do you think is best%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%which of these do you think is best%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q74_df = pd.read_sql_query(q74_query, conn, params=reliable_participants + reliable_participants)
print("\nQ74: How should animals be represented in decision-making?")
print(q74_df)

print("\n" + "=" * 80)
print("5.3. WHO SHOULD REPRESENT ANIMALS (Q75)")
print("=" * 80)

# Q75: Who should represent animals in decision-making bodies?
q75_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%who do you think should be given the responsibility%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%who do you think should be given the responsibility%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q75_df = pd.read_sql_query(q75_query, conn, params=reliable_participants + reliable_participants)
print("\nQ75: Who should represent animals in decision-making bodies?")
print(q75_df)

print("\n" + "=" * 80)
print("5.4. ANIMAL PARTICIPATION IN DEMOCRACY (Q77)")
print("=" * 80)

# Q77: Should animals participate in democratic processes?
q77_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%should they be allowed to participate in human democratic%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%should they be allowed to participate in human democratic%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q77_df = pd.read_sql_query(q77_query, conn, params=reliable_participants + reliable_participants)
print("\nQ77: Should animals participate in human democratic processes?")
print(q77_df)

# Correlation with belief in animal culture (Q41)
culture_democracy_query = f"""
SELECT r1.response as democracy_view,
       r2.response as culture_belief,
       COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question LIKE '%should they be allowed to participate in human democratic%'
AND r2.question LIKE '%animals have their own forms of culture%'
AND r1.participant_id IN ({placeholders})
GROUP BY r1.response, r2.response
ORDER BY r1.response, r2.response
"""
culture_democracy_df = pd.read_sql_query(culture_democracy_query, conn, params=reliable_participants)
print("\nCorrelation with Belief in Animal Culture:")
print(culture_democracy_df)

print("\n" + "=" * 80)
print("5.5. REGULATING COMMUNICATION (Q82, Q83, Q85)")
print("=" * 80)

# Q82: Restrict to authorized professionals?
q82_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%Animal communication should be restricted to authorized%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%Animal communication should be restricted to authorized%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q82_df = pd.read_sql_query(q82_query, conn, params=reliable_participants + reliable_participants)
print("\nQ82: Should animal communication be restricted to professionals?")
print(q82_df)

# Q83: Everyone allowed to listen?
q83_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%Everyone should be allowed to listen to animals%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%Everyone should be allowed to listen to animals%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q83_df = pd.read_sql_query(q83_query, conn, params=reliable_participants + reliable_participants)
print("\nQ83: Should everyone be allowed to listen to animals?")
print(q83_df)

# Q85: Types of communication to prohibit
q85_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%types of human-to-animal communication should be strictly regulated%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%types of human-to-animal communication should be strictly regulated%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
LIMIT 10
"""
q85_df = pd.read_sql_query(q85_query, conn, params=reliable_participants + reliable_participants)
print("\nQ85: Types of communication to prohibit (Top 10):")
print(q85_df)

print("\n" + "=" * 80)
print("5.6. OWNERSHIP OF ANIMAL CREATIONS (Q90)")
print("=" * 80)

# Q90: Who owns animal recordings?
q90_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%who should own that recording%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%who should own that recording%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q90_df = pd.read_sql_query(q90_query, conn, params=reliable_participants + reliable_participants)
print("\nQ90: Who should own animal recordings?")
print(q90_df)

print("\n" + "=" * 80)
print("5.7. SHOULD ANIMALS BE ABLE TO EARN MONEY? (Q91)")
print("=" * 80)

# Q91: Economic rights for animals
q91_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%think that in the future non-humans should be able%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%think that in the future non-humans should be able%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q91_df = pd.read_sql_query(q91_query, conn, params=reliable_participants + reliable_participants)
print("\nQ91: Economic rights for non-humans:")
print(q91_df)

# Age group analysis for Q91
print("\n--- Age Group Analysis for Economic Rights ---")
age_economic_query = f"""
SELECT 
    CASE 
        WHEN r2.response = '18-25' THEN '18-25'
        WHEN r2.response = '26-35' THEN '26-35'
        WHEN r2.response = '36-45' THEN '36-45'
        WHEN r2.response = '46-55' THEN '46-55'
        WHEN r2.response = '56-65' THEN '56-65'
        WHEN r2.response = '65+' THEN '65+'
        ELSE 'Other'
    END as age_group,
    r1.response as economic_right,
    COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question LIKE '%think that in the future non-humans should be able%'
AND r2.question LIKE 'How old are you%'
AND r1.participant_id IN ({placeholders})
GROUP BY age_group, r1.response
ORDER BY age_group, count DESC
"""
age_economic_df = pd.read_sql_query(age_economic_query, conn, params=reliable_participants)
print(age_economic_df)

print("\n" + "=" * 80)
print("CROSS-CUTTING ANALYSIS")
print("=" * 80)

# Consistency between human superiority views and economic rights
consistency_query = f"""
SELECT r1.response as human_superiority,
       r2.response as economic_rights,
       COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question LIKE '%fundamentally different and superior%'
AND r2.question LIKE '%think that in the future non-humans should be able%'
AND r1.participant_id IN ({placeholders})
GROUP BY r1.response, r2.response
ORDER BY count DESC
LIMIT 20
"""
consistency_df = pd.read_sql_query(consistency_query, conn, params=reliable_participants)
print("\nConsistency between Human Superiority Views and Economic Rights Support:")
print(consistency_df)

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)