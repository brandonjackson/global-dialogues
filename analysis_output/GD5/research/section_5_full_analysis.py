#!/usr/bin/env python3
"""
Complete analysis for Section 5: Ethics, Rights, and Governance
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

# Helper function to get question ID by searching question text
def find_question_id(search_text):
    query = f"""
    SELECT DISTINCT question_id, question 
    FROM responses 
    WHERE LOWER(question) LIKE LOWER('%{search_text}%')
    LIMIT 1
    """
    result = pd.read_sql_query(query, conn)
    if not result.empty:
        return result.iloc[0]['question_id'], result.iloc[0]['question']
    return None, None

# Helper function to get response distribution
def analyze_question(question_id, question_text):
    query = f"""
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses r2 
                                     JOIN participants p2 ON r2.participant_id = p2.participant_id
                                     WHERE r2.question_id = '{question_id}' 
                                     AND p2.pri_score >= 0.3), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = '{question_id}'
    AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)

# Helper function for demographic analysis
def demographic_analysis(question_id, demographic_col, response_value=None):
    if response_value:
        query = f"""
        SELECT AVG(CAST({demographic_col} AS REAL)) as avg_score
        FROM responses r
        JOIN participants p ON r.participant_id = p.participant_id
        WHERE r.question_id = '{question_id}'
        AND r.response = '{response_value}'
        AND p.pri_score >= 0.3
        """
    else:
        query = f"""
        SELECT r.response, AVG(CAST({demographic_col} AS REAL)) as avg_score
        FROM responses r
        JOIN participants p ON r.participant_id = p.participant_id
        WHERE r.question_id = '{question_id}'
        AND p.pri_score >= 0.3
        GROUP BY r.response
        """
    return pd.read_sql_query(query, conn)

print("\n" + "=" * 80)
print("5.1. PREFERRED FUTURE FOR ANIMAL PROTECTION")
print("=" * 80)

# Find Q70 about preferred futures
q70_id, q70_text = find_question_id("Which approach feels most appropriate")
if q70_id:
    print(f"\nQuestion: {q70_text[:150]}...")
    print(f"Question ID: {q70_id}")
    
    # Get response distribution
    q70_dist = analyze_question(q70_id, q70_text)
    print("\nResponse Distribution:")
    print(q70_dist)
    
    # Check correlation with human-animal equality belief (Q32)
    q32_id, q32_text = find_question_id("fundamentally different and superior")
    if q32_id:
        correlation_query = f"""
        SELECT r1.response as future_preference,
               r2.response as human_superiority_view,
               COUNT(*) as count
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = '{q70_id}'
        AND r2.question_id = '{q32_id}'
        AND p.pri_score >= 0.3
        GROUP BY r1.response, r2.response
        ORDER BY r1.response, count DESC
        """
        correlation_df = pd.read_sql_query(correlation_query, conn)
        print("\nCorrelation with Human-Animal Equality Views:")
        print(correlation_df.head(15))

print("\n" + "=" * 80)
print("5.2. ANIMAL REPRESENTATION")
print("=" * 80)

# Q73: Should animals have legal representatives?
q73_id, q73_text = find_question_id("should that animal have the right to a representative")
if q73_id:
    print(f"\nQuestion: {q73_text[:150]}...")
    q73_dist = analyze_question(q73_id, q73_text)
    print("\nResponse Distribution:")
    print(q73_dist)

# Q74: Who should represent them?
q74_id, q74_text = find_question_id("represented in legal proceedings by")
if q74_id:
    print(f"\nQuestion: {q74_text[:150]}...")
    q74_dist = analyze_question(q74_id, q74_text)
    print("\nResponse Distribution:")
    print(q74_dist)

print("\n" + "=" * 80)
print("5.3. WHO SHOULD REPRESENT ANIMALS")
print("=" * 80)

# Q75: Top 3 choices for representation
q75_id, q75_text = find_question_id("represented in decision-making bodies")
if q75_id:
    print(f"\nQuestion: {q75_text[:150]}...")
    q75_dist = analyze_question(q75_id, q75_text)
    print("\nTop Choices for Animal Representation:")
    print(q75_dist.head(10))

print("\n" + "=" * 80)
print("5.4. ANIMAL PARTICIPATION IN DEMOCRACY")
print("=" * 80)

# Q77: Should animals participate in democratic processes?
q77_id, q77_text = find_question_id("participate in human democratic processes")
if q77_id:
    print(f"\nQuestion: {q77_text[:150]}...")
    q77_dist = analyze_question(q77_id, q77_text)
    print("\nResponse Distribution:")
    print(q77_dist)
    
    # Check correlation with belief in animal culture
    q41_id, q41_text = find_question_id("animals have their own forms of culture")
    if q41_id:
        culture_democracy_query = f"""
        SELECT r1.response as democracy_view,
               r2.response as culture_belief,
               COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) 
                                         FROM responses r3 
                                         JOIN participants p3 ON r3.participant_id = p3.participant_id
                                         WHERE r3.question_id = '{q77_id}'
                                         AND p3.pri_score >= 0.3), 2) as percentage
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = '{q77_id}'
        AND r2.question_id = '{q41_id}'
        AND p.pri_score >= 0.3
        GROUP BY r1.response, r2.response
        ORDER BY r1.response, r2.response
        """
        culture_democracy_df = pd.read_sql_query(culture_democracy_query, conn)
        print("\nCorrelation with Belief in Animal Culture:")
        print(culture_democracy_df.head(20))

print("\n" + "=" * 80)
print("5.5. REGULATING COMMUNICATION")
print("=" * 80)

# Q82: Restrict to authorized professionals?
q82_id, q82_text = find_question_id("restricted to authorized professionals")
if q82_id:
    print(f"\nQuestion: {q82_text[:150]}...")
    q82_dist = analyze_question(q82_id, q82_text)
    print("\nResponse Distribution - Professional Restriction:")
    print(q82_dist)

# Q83: Everyone should be allowed to listen?
q83_id, q83_text = find_question_id("Everyone should be allowed to listen")
if q83_id:
    print(f"\nQuestion: {q83_text[:150]}...")
    q83_dist = analyze_question(q83_id, q83_text)
    print("\nResponse Distribution - Open Access:")
    print(q83_dist)

# Q85: Types of communication to prohibit
q85_id, q85_text = find_question_id("types of human-to-animal communication should be strictly regulated")
if q85_id:
    print(f"\nQuestion: {q85_text[:150]}...")
    q85_dist = analyze_question(q85_id, q85_text)
    print("\nTypes of Communication to Prohibit (Top 10):")
    print(q85_dist.head(10))

print("\n" + "=" * 80)
print("5.6. OWNERSHIP OF ANIMAL CREATIONS")
print("=" * 80)

# Q90: Who owns animal recordings?
q90_id, q90_text = find_question_id("who should own that recording")
if q90_id:
    print(f"\nQuestion: {q90_text[:150]}...")
    q90_dist = analyze_question(q90_id, q90_text)
    print("\nResponse Distribution - Ownership:")
    print(q90_dist)

print("\n" + "=" * 80)
print("5.7. SHOULD ANIMALS BE ABLE TO EARN MONEY?")
print("=" * 80)

# Q91: Economic rights for animals
q91_id, q91_text = find_question_id("non-humans should be able to")
if q91_id:
    print(f"\nQuestion: {q91_text[:150]}...")
    q91_dist = analyze_question(q91_id, q91_text)
    print("\nResponse Distribution - Economic Rights:")
    print(q91_dist)
    
    # Age group analysis
    print("\nAge Group Analysis:")
    age_groups = [
        ('o2_18_25', '18-25'),
        ('o2_26_35', '26-35'),
        ('o2_36_45', '36-45'),
        ('o2_46_55', '46-55'),
        ('o2_56_65', '56-65'),
        ('o2_65', '65+')
    ]
    
    for age_col, age_label in age_groups:
        age_query = f"""
        SELECT '{age_label}' as age_group,
               r.response,
               AVG(CAST({age_col} AS REAL)) as avg_score,
               COUNT(*) as count
        FROM responses r
        JOIN participants p ON r.participant_id = p.participant_id
        WHERE r.question_id = '{q91_id}'
        AND p.pri_score >= 0.3
        GROUP BY r.response
        """
        age_df = pd.read_sql_query(age_query, conn)
        if not age_df.empty:
            print(f"\n{age_label}:")
            print(age_df)

print("\n" + "=" * 80)
print("CROSS-CUTTING ANALYSIS")
print("=" * 80)

# Analyze consistency between views
if q32_id and q91_id:
    consistency_query = f"""
    SELECT r1.response as human_superiority,
           r2.response as economic_rights,
           COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) 
                                     FROM responses r3 
                                     JOIN participants p3 ON r3.participant_id = p3.participant_id
                                     WHERE r3.question_id = '{q32_id}'
                                     AND p3.pri_score >= 0.3), 2) as percentage
    FROM responses r1
    JOIN responses r2 ON r1.participant_id = r2.participant_id
    JOIN participants p ON r1.participant_id = p.participant_id
    WHERE r1.question_id = '{q32_id}'
    AND r2.question_id = '{q91_id}'
    AND p.pri_score >= 0.3
    GROUP BY r1.response, r2.response
    ORDER BY count DESC
    """
    consistency_df = pd.read_sql_query(consistency_query, conn)
    print("\nConsistency between Human Superiority Views and Economic Rights Support:")
    print(consistency_df.head(15))

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)