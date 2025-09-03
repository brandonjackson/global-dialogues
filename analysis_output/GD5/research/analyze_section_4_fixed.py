#!/usr/bin/env python3
"""
Analysis for Section 4: AI as an Interspecies Communication Tool
Using correct question IDs from database exploration
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import re

# Database path
DB_PATH = "../../../Data/GD5/GD5.db"

# Correct Question IDs (discovered through exploration)
QUESTION_IDS = {
    'Q57': 'cc8d6e1d-2617-4e7c-9e9b-9f8293e23247',  # Trust in AI translation
    'Q55': '524213d3-fc60-47b6-b08d-dda406130652',  # Interest level  
    'Q59': '809479c1-4172-49c7-84d7-9ef121d5f171',  # Concerns
    'Q61': '727719e2-4557-4ef8-a29d-b9c6b316cb80',  # AI vs humans trust
    'Q66': 'a7601187-0c2a-4f65-a95a-0a4da9cf1b53',  # Approach for interaction
    'Q17': 'b2a655a0-daed-4687-a70c-15e0c7f1b4a3',  # Trust in AI chatbots
}

def connect_db():
    """Connect to the GD5 database in read-only mode"""
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def analyze_trust_in_ai_translation(conn):
    """4.1. Trust in AI Translation (Q57)"""
    print("\n=== 4.1. Trust in AI Translation ===")
    
    q57_id = QUESTION_IDS['Q57']
    
    # Get trust distribution with PRI filtering
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY percentage DESC
    """
    
    trust_dist = pd.read_sql_query(query, conn, params=[q57_id])
    print("\nTrust Distribution in AI Translation:")
    print(trust_dist)
    
    # Correlation with general AI chatbot trust (Q17)
    q17_id = QUESTION_IDS['Q17']
    
    query = """
    SELECT 
        r1.response as ai_translation_trust,
        r2.response as ai_chatbot_trust,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r1
    JOIN responses r2 ON r1.participant_id = r2.participant_id
    JOIN participants p ON r1.participant_id = p.participant_id
    WHERE r1.question_id = ? 
    AND r2.question_id = ?
    AND p.pri_score >= 0.3
    GROUP BY r1.response, r2.response
    ORDER BY count DESC
    LIMIT 10
    """
    
    correlation_data = pd.read_sql_query(query, conn, params=[q57_id, q17_id])
    
    print("\nTop 10 Correlations - AI Translation Trust vs AI Chatbot Trust:")
    print(correlation_data)
    
    return trust_dist

def analyze_interest_level(conn):
    """4.2. Interest Level (Q55)"""
    print("\n=== 4.2. Interest Level ===")
    
    q55_id = QUESTION_IDS['Q55']
    
    # Get interest distribution
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY percentage DESC
    """
    
    interest_dist = pd.read_sql_query(query, conn, params=[q55_id])
    print("\nInterest Distribution:")
    print(interest_dist)
    
    # Interest vs Trust analysis
    q57_id = QUESTION_IDS['Q57']
    
    # High interest with skepticism
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
    
    # Calculate skeptical but interested
    high_interest = interest_trust[interest_trust['interest_level'].str.contains('Very|Moderately', case=False, na=False)]
    skeptical = high_interest[high_interest['trust_level'].str.contains('distrust|Distrust', case=False, na=False)]
    
    total_high_interest = high_interest['count'].sum()
    total_skeptical_interested = skeptical['count'].sum()
    
    if total_high_interest > 0:
        percentage = (total_skeptical_interested / total_high_interest) * 100
        print(f"\nAmong highly interested respondents:")
        print(f"  Skeptical but interested: {total_skeptical_interested} ({percentage:.1f}%)")
    
    return interest_dist

def analyze_top_concerns(conn):
    """4.3. Top Concerns (Q59)"""
    print("\n=== 4.3. Top Concerns ===")
    
    q59_id = QUESTION_IDS['Q59']
    
    # Get all text responses
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
    
    # Enhanced categorization of concerns
    categories = {
        'Technical Limitations': ['inaccurate', 'wrong', 'misinterpret', 'error', 'mistake', 'limited', 
                                 'can\'t understand', 'impossible', 'misunderstand', 'incorrect'],
        'Human Error/Bias': ['bias', 'human error', 'programmed', 'human agenda', 'anthropomorph',
                            'projection', 'assumptions'],
        'Philosophical Barriers': ['never truly know', 'impossible to understand', 'different experience', 
                                  'consciousness', 'subjective', 'unknowable'],
        'Exploitation': ['exploit', 'abuse', 'harm', 'manipulate', 'control', 'use', 'advantage'],
        'Privacy': ['privacy', 'surveillance', 'monitoring', 'tracking', 'invasion'],
        'Trust Issues': ['trust', 'reliability', 'confidence', 'depend', 'believe'],
        'Ethical Concerns': ['ethical', 'moral', 'rights', 'consent', 'welfare'],
        'Commercialization': ['commercial', 'profit', 'money', 'corporate', 'business', 'sell']
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
    
    return concern_counts

def analyze_simulation_vs_direct(conn):
    """4.4. Simulation vs. Direct Communication (Q66)"""
    print("\n=== 4.4. Simulation vs. Direct Communication ===")
    
    q66_id = QUESTION_IDS['Q66']
    
    # Get preference distribution
    query = """
    SELECT r.response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? AND p.pri_score >= 0.3
    GROUP BY r.response
    ORDER BY percentage DESC
    """
    
    preference_dist = pd.read_sql_query(query, conn, params=[q66_id])
    print("\nApproach Preference Distribution:")
    print(preference_dist)
    
    # Link to trust in AI accuracy (Q57)
    q57_id = QUESTION_IDS['Q57']
    
    query = """
    SELECT 
        r1.response as preference,
        r2.response as trust_level,
        COUNT(*) as count
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
    
    if not preference_trust.empty:
        print("\nPreference by Trust Level (Top patterns):")
        # Group by preference and show trust distribution
        for pref in preference_dist['response'].head(3):
            subset = preference_trust[preference_trust['preference'] == pref]
            if not subset.empty:
                print(f"\n{pref}:")
                top_trust = subset.nlargest(3, 'count')
                for _, row in top_trust.iterrows():
                    print(f"  {row['trust_level']}: {row['count']}")
    
    return preference_dist

def analyze_ai_vs_humans_trust(conn):
    """4.5. Who Trusts AI More Than Humans (Q61)"""
    print("\n=== 4.5. Who Trusts AI More Than Humans ===")
    
    q61_id = QUESTION_IDS['Q61']
    
    # This is an open-text question, so we need to analyze the text
    query = """
    SELECT r.response
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = ? 
    AND p.pri_score >= 0.3
    AND r.response IS NOT NULL
    """
    
    responses_df = pd.read_sql_query(query, conn, params=[q61_id])
    
    if responses_df.empty:
        print("No responses found for Q61")
        return None
    
    # Categorize responses
    trust_ai_more = 0
    trust_humans_more = 0
    equal_trust = 0
    unclear = 0
    
    for response in responses_df['response']:
        response_lower = response.lower()
        
        # Keywords for categorization
        if any(phrase in response_lower for phrase in ['ai more', 'trust ai', 'ai would be better', 
                                                        'ai is more', 'prefer ai', 'ai over human']):
            trust_ai_more += 1
        elif any(phrase in response_lower for phrase in ['human more', 'trust human', 'humans better',
                                                          'prefer human', 'human over ai', 'less than human']):
            trust_humans_more += 1
        elif any(phrase in response_lower for phrase in ['both', 'equal', 'same', 'combination', 'together']):
            equal_trust += 1
        else:
            # Try more detailed analysis
            if 'yes' in response_lower[:50]:  # Check if starts with yes
                trust_ai_more += 1
            elif 'no' in response_lower[:50]:  # Check if starts with no
                trust_humans_more += 1
            else:
                unclear += 1
    
    total = len(responses_df)
    
    print(f"\nTrust Distribution (AI vs Humans in Wildlife Conflicts):")
    print(f"  Trust AI more: {trust_ai_more} ({trust_ai_more/total*100:.1f}%)")
    print(f"  Trust humans more: {trust_humans_more} ({trust_humans_more/total*100:.1f}%)")
    print(f"  Equal/Both: {equal_trust} ({equal_trust/total*100:.1f}%)")
    print(f"  Unclear: {unclear} ({unclear/total*100:.1f}%)")
    
    # Sample responses for each category
    print("\nSample responses:")
    samples_shown = {'ai': False, 'human': False, 'both': False}
    
    for response in responses_df['response'].sample(min(20, len(responses_df))):
        response_lower = response.lower()
        
        if not samples_shown['ai'] and 'ai more' in response_lower:
            print(f"\nTrust AI more:")
            print(f"  \"{response[:150]}...\"")
            samples_shown['ai'] = True
            
        elif not samples_shown['human'] and 'human' in response_lower and 'less' in response_lower:
            print(f"\nTrust humans more:")
            print(f"  \"{response[:150]}...\"")
            samples_shown['human'] = True
            
        elif not samples_shown['both'] and 'both' in response_lower:
            print(f"\nEqual/Both:")
            print(f"  \"{response[:150]}...\"")
            samples_shown['both'] = True
            
        if all(samples_shown.values()):
            break
    
    return {'ai_more': trust_ai_more, 'humans_more': trust_humans_more, 
            'equal': equal_trust, 'unclear': unclear, 'total': total}

def main():
    """Run all Section 4 analyses"""
    print("=" * 80)
    print("Section 4: AI as an Interspecies Communication Tool")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 80)
    
    try:
        conn = connect_db()
        
        # Run each analysis
        results = {
            '4.1': analyze_trust_in_ai_translation(conn),
            '4.2': analyze_interest_level(conn),
            '4.3': analyze_top_concerns(conn),
            '4.4': analyze_simulation_vs_direct(conn),
            '4.5': analyze_ai_vs_humans_trust(conn)
        }
        
        print("\n" + "=" * 80)
        print("Analysis Complete")
        print("=" * 80)
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()