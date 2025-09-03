#!/usr/bin/env python3
"""
Analysis for Section 4: AI as an Interspecies Communication Tool
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
import re

# Database path
DB_PATH = "../../../Data/GD5/GD5.db"

def connect_db():
    """Connect to the GD5 database in read-only mode"""
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def get_question_mapping(conn):
    """Get mapping of question IDs to question text"""
    query = """
    SELECT DISTINCT question_id, question 
    FROM responses 
    ORDER BY question_id
    """
    df = pd.read_sql_query(query, conn)
    return dict(zip(df['question'], df['question_id']))

def find_question_id(conn, keywords):
    """Find question ID by searching for keywords in question text"""
    query = """
    SELECT DISTINCT question_id, question 
    FROM responses 
    WHERE LOWER(question) LIKE ?
    """
    for keyword in keywords:
        df = pd.read_sql_query(query, conn, params=[f'%{keyword.lower()}%'])
        if not df.empty:
            return df.iloc[0]['question_id'], df.iloc[0]['question']
    return None, None

def analyze_trust_in_ai_translation(conn):
    """4.1. Trust in AI Translation (Q57)"""
    print("\n=== 4.1. Trust in AI Translation ===")
    
    # Find Q57 - trust in AI translation
    q57_id, q57_text = find_question_id(conn, ['truly and comprehensively reflect', 'animal is communicating'])
    
    if not q57_id:
        print("Could not find Q57 about trust in AI translation")
        return None
    
    print(f"Found Q57: {q57_text[:100]}...")
    
    # Get trust distribution with PRI filtering
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY count DESC
    """
    
    trust_dist = pd.read_sql_query(query, conn, params=[q57_id])
    print("\nTrust Distribution:")
    print(trust_dist)
    
    # Find Q17 - general trust in AI chatbots  
    q17_id, q17_text = find_question_id(conn, ['trust AI chatbots', 'How much do you trust'])
    
    if q17_id:
        print(f"\nFound Q17: {q17_text[:100]}...")
        
        # Correlation between general AI trust and translation trust
        query = """
        SELECT 
            r1.participant_id,
            r1.response as ai_translation_trust,
            r2.response as ai_chatbot_trust
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = ? 
        AND r2.question_id = ?
        AND p.pri_score >= 0.3
        """
        
        correlation_data = pd.read_sql_query(query, conn, params=[q57_id, q17_id])
        
        # Cross-tabulation
        crosstab = pd.crosstab(correlation_data['ai_chatbot_trust'], 
                               correlation_data['ai_translation_trust'],
                               normalize='index')
        print("\nCross-tabulation (% by row) - AI Chatbot Trust vs AI Translation Trust:")
        print(crosstab.round(2))
    
    return trust_dist

def analyze_interest_level(conn):
    """4.2. Interest Level (Q55)"""
    print("\n=== 4.2. Interest Level ===")
    
    # Find Q55 - interest in knowing what animals say/feel
    q55_id, q55_text = find_question_id(conn, ['interested', 'animals might', 'say or feel'])
    
    if not q55_id:
        print("Could not find Q55 about interest level")
        return None
    
    print(f"Found Q55: {q55_text[:100]}...")
    
    # Get interest distribution
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY count DESC
    """
    
    interest_dist = pd.read_sql_query(query, conn, params=[q55_id])
    print("\nInterest Distribution:")
    print(interest_dist)
    
    # Find Q57 for cross-analysis with trust
    q57_id, _ = find_question_id(conn, ['truly and comprehensively reflect', 'animal is communicating'])
    
    if q57_id:
        # Interest vs Trust correlation
        query = """
        SELECT 
            r1.response as interest_level,
            r2.response as trust_level,
            COUNT(*) as count
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = ? 
        AND r2.question_id = ?
        AND p.pri_score >= 0.3
        GROUP BY r1.response, r2.response
        """
        
        interest_trust = pd.read_sql_query(query, conn, params=[q55_id, q57_id])
        
        # High interest with skepticism
        query = """
        SELECT COUNT(*) as skeptical_but_interested
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = ? 
        AND r2.question_id = ?
        AND r1.response IN ('Very interested', 'Moderately interested')
        AND r2.response IN ('Strongly distrust', 'Somewhat distrust')
        AND p.pri_score >= 0.3
        """
        
        skeptical_interested = pd.read_sql_query(query, conn, params=[q55_id, q57_id])
        
        total_count_query = """
        SELECT COUNT(*) as total
        FROM responses r
        JOIN participants p ON r.participant_id = p.participant_id
        WHERE r.question_id = ? AND p.pri_score >= 0.3
        """
        total = pd.read_sql_query(total_count_query, conn, params=[q55_id])['total'][0]
        
        percentage = (skeptical_interested['skeptical_but_interested'][0] / total) * 100
        print(f"\nSkeptical but interested: {skeptical_interested['skeptical_but_interested'][0]} ({percentage:.1f}% of total)")
    
    return interest_dist

def analyze_top_concerns(conn):
    """4.3. Top Concerns (Q59)"""
    print("\n=== 4.3. Top Concerns ===")
    
    # Find Q59 - concerns about AI in interspecies communication
    q59_id, q59_text = find_question_id(conn, ['concerns', 'AI', 'interspecies communication', 'biggest concern'])
    
    if not q59_id:
        print("Could not find Q59 about concerns")
        return None
    
    print(f"Found Q59: {q59_text[:100]}...")
    
    # Get all responses
    query = """
    SELECT r.response
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? 
    AND p.pri_score >= 0.3
    AND r.response IS NOT NULL 
    AND LENGTH(TRIM(r.response)) > 0
    """
    
    concerns_df = pd.read_sql_query(query, conn, params=[q59_id])
    
    if concerns_df.empty:
        print("No text responses found for Q59")
        return None
    
    # Basic categorization of concerns
    categories = {
        'Technical Limitations': ['inaccurate', 'wrong', 'misinterpret', 'error', 'mistake', 'limited', 'can\'t understand', 'impossible'],
        'Human Error/Bias': ['bias', 'human error', 'programmed', 'human agenda', 'anthropomorph'],
        'Philosophical Barriers': ['never truly know', 'impossible to understand', 'different experience', 'consciousness'],
        'Exploitation': ['exploit', 'abuse', 'harm', 'manipulate', 'control'],
        'Privacy': ['privacy', 'surveillance', 'monitoring'],
        'Trust Issues': ['trust', 'reliability', 'confidence'],
        'Ethical Concerns': ['ethical', 'moral', 'rights'],
        'Commercialization': ['commercial', 'profit', 'money', 'corporate']
    }
    
    concern_counts = {cat: 0 for cat in categories}
    total_responses = len(concerns_df)
    
    for response in concerns_df['response']:
        response_lower = response.lower()
        for category, keywords in categories.items():
            if any(keyword in response_lower for keyword in keywords):
                concern_counts[category] += 1
    
    # Sort by frequency
    sorted_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTop Concerns (n={total_responses}):")
    for concern, count in sorted_concerns[:5]:
        percentage = (count / total_responses) * 100
        print(f"  {concern}: {count} ({percentage:.1f}%)")
    
    # Sample responses for top categories
    print("\nSample responses for top concerns:")
    for concern, _ in sorted_concerns[:3]:
        print(f"\n{concern}:")
        keywords = categories[concern]
        for i, row in concerns_df.iterrows():
            if any(keyword in row['response'].lower() for keyword in keywords):
                print(f"  - {row['response'][:150]}...")
                break
    
    return concern_counts

def analyze_simulation_vs_direct(conn):
    """4.4. Simulation vs. Direct Communication (Q66)"""
    print("\n=== 4.4. Simulation vs. Direct Communication ===")
    
    # Find Q66 - preference for direct vs simulation
    q66_id, q66_text = find_question_id(conn, ['prefer', 'direct communication', 'computer simulation'])
    
    if not q66_id:
        print("Could not find Q66 about simulation vs direct communication")
        return None
    
    print(f"Found Q66: {q66_text[:100]}...")
    
    # Get preference distribution
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY count DESC
    """
    
    preference_dist = pd.read_sql_query(query, conn, params=[q66_id])
    print("\nPreference Distribution:")
    print(preference_dist)
    
    # Link to trust in AI accuracy (Q57)
    q57_id, _ = find_question_id(conn, ['truly and comprehensively reflect', 'animal is communicating'])
    
    if q57_id:
        query = """
        SELECT 
            r1.response as preference,
            r2.response as trust_level,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY r1.response), 2) as percentage
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = ? 
        AND r2.question_id = ?
        AND p.pri_score >= 0.3
        GROUP BY r1.response, r2.response
        ORDER BY r1.response, count DESC
        """
        
        preference_trust = pd.read_sql_query(query, conn, params=[q66_id, q57_id])
        
        print("\nPreference by Trust Level:")
        for pref in preference_trust['preference'].unique():
            print(f"\n{pref}:")
            subset = preference_trust[preference_trust['preference'] == pref]
            for _, row in subset.iterrows():
                print(f"  {row['trust_level']}: {row['count']} ({row['percentage']}%)")
    
    return preference_dist

def analyze_ai_vs_humans_trust(conn):
    """4.5. Who Trusts AI More Than Humans (Q61)"""
    print("\n=== 4.5. Who Trusts AI More Than Humans ===")
    
    # Find Q61 - trust in AI vs humans for wildlife conflict
    q61_id, q61_text = find_question_id(conn, ['wildlife conflict', 'trust', 'AI', 'interpret'])
    
    if not q61_id:
        print("Could not find Q61 about AI vs human trust in wildlife conflicts")
        return None
    
    print(f"Found Q61: {q61_text[:100]}...")
    
    # Get trust distribution
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY count DESC
    """
    
    trust_dist = pd.read_sql_query(query, conn, params=[q61_id])
    print("\nTrust Distribution (AI vs Humans):")
    print(trust_dist)
    
    # Calculate percentage who trust AI more
    ai_more_trust = trust_dist[trust_dist['response'].str.contains('AI', case=False, na=False)]['percentage'].sum()
    print(f"\nPercentage who trust AI more than humans: {ai_more_trust:.1f}%")
    
    # Demographic analysis - by age
    query = """
    SELECT 
        CASE 
            WHEN r2.response = '18-25' THEN '18-25'
            WHEN r2.response = '26-35' THEN '26-35'
            WHEN r2.response = '36-45' THEN '36-45'
            WHEN r2.response = '46-55' THEN '46-55'
            WHEN r2.response = '56+' THEN '56+'
            ELSE 'Unknown'
        END as age_group,
        r1.response as trust_choice,
        COUNT(*) as count
    FROM responses r1
    JOIN responses r2 ON r1.participant_id = r2.participant_id
    JOIN participants p ON r1.participant_id = p.participant_id
    WHERE r1.question_id = ?
    AND r2.question LIKE '%How old are you%'
    AND p.pri_score >= 0.3
    GROUP BY age_group, trust_choice
    """
    
    age_trust = pd.read_sql_query(query, conn, params=[q61_id])
    
    if not age_trust.empty:
        print("\nTrust by Age Group:")
        age_pivot = age_trust.pivot_table(index='age_group', columns='trust_choice', values='count', fill_value=0)
        age_pivot_pct = age_pivot.div(age_pivot.sum(axis=1), axis=0) * 100
        print(age_pivot_pct.round(1))
    
    # Get reasons (if there's an open-text follow-up)
    q61_followup_id, q61_followup_text = find_question_id(conn, ['Why', 'trust', 'AI', 'humans', 'conflict'])
    
    if q61_followup_id:
        print(f"\nFound follow-up: {q61_followup_text[:100]}...")
        
        query = """
        SELECT r2.response as reason
        FROM responses r1
        JOIN responses r2 ON r1.participant_id = r2.participant_id
        JOIN participants p ON r1.participant_id = p.participant_id
        WHERE r1.question_id = ?
        AND r2.question_id = ?
        AND r1.response LIKE '%AI%'
        AND p.pri_score >= 0.3
        AND r2.response IS NOT NULL
        LIMIT 5
        """
        
        reasons = pd.read_sql_query(query, conn, params=[q61_id, q61_followup_id])
        
        if not reasons.empty:
            print("\nSample reasons for trusting AI more:")
            for i, row in reasons.iterrows():
                print(f"  - {row['reason'][:150]}...")
    
    return trust_dist

def main():
    """Run all Section 4 analyses"""
    print("=" * 60)
    print("Section 4: AI as an Interspecies Communication Tool")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 60)
    
    try:
        conn = connect_db()
        
        # Get question mapping first
        print("\nMapping questions...")
        question_map = get_question_mapping(conn)
        print(f"Found {len(question_map)} unique questions in database")
        
        # Run each analysis
        results = {
            '4.1': analyze_trust_in_ai_translation(conn),
            '4.2': analyze_interest_level(conn),
            '4.3': analyze_top_concerns(conn),
            '4.4': analyze_simulation_vs_direct(conn),
            '4.5': analyze_ai_vs_humans_trust(conn)
        }
        
        print("\n" + "=" * 60)
        print("Analysis Complete")
        print("=" * 60)
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()