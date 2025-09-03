#!/usr/bin/env python3
"""
Section 2: AI in Society and Personal Life Analysis
This script analyzes questions 18-27 and related correlations for GD5 survey data
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# First, let's get the question mapping to find the actual question IDs
def get_question_mapping():
    query = """
    SELECT DISTINCT question_id, question 
    FROM responses 
    ORDER BY question_id;
    """
    return pd.read_sql_query(query, conn)

# Get all questions to identify the UUIDs we need
questions_df = get_question_mapping()
print("Getting question mapping...")
print("\nLooking for relevant questions (Q5, Q17, Q18-Q27)...")

# Filter for our relevant questions
relevant_questions = []
for idx, row in questions_df.iterrows():
    q_text = row['question'].lower()
    # Q5: AI excitement/concern
    if 'increased use of artificial intelligence' in q_text and 'daily life makes you feel' in q_text:
        relevant_questions.append(('Q5', row['question_id'], row['question']))
    # Q17: Trust AI chatbot
    elif 'trust your ai chatbot' in q_text:
        relevant_questions.append(('Q17', row['question_id'], row['question']))
    # Q18: Required to use AI at work
    elif 'expected to use an ai system at work' in q_text:
        relevant_questions.append(('Q18', row['question_id'], row['question']))
    # Q19: Chosen to use AI at work
    elif 'personally chosen to use an ai system at work' in q_text:
        relevant_questions.append(('Q19', row['question_id'], row['question']))
    # Q20: Use AI in personal life
    elif 'personally chosen to use an ai system in your personal life' in q_text:
        relevant_questions.append(('Q20', row['question_id'], row['question']))
    # Q21: AI for sensitive issues
    elif 'sensitive personal issue' in q_text:
        relevant_questions.append(('Q21', row['question_id'], row['question']))
    # Q22: AI for autonomous actions
    elif 'complete an action in the real world' in q_text:
        relevant_questions.append(('Q22', row['question_id'], row['question']))
    # Q23: Cost of living
    elif 'cost of living' in q_text:
        relevant_questions.append(('Q23', row['question_id'], row['question']))
    # Q24: Free time
    elif 'amount of free time' in q_text:
        relevant_questions.append(('Q24', row['question_id'], row['question']))
    # Q25: Community well-being
    elif "community's well-being" in q_text:
        relevant_questions.append(('Q25', row['question_id'], row['question']))
    # Q26: Job availability
    elif 'availability of good jobs' in q_text:
        relevant_questions.append(('Q26', row['question_id'], row['question']))
    # Q27: Sense of purpose
    elif 'sense of purpose' in q_text:
        relevant_questions.append(('Q27', row['question_id'], row['question']))

print("\nFound questions:")
for q_num, q_id, q_text in relevant_questions:
    print(f"{q_num}: {q_id[:8]}... - {q_text[:60]}...")

# Create a dictionary for easy access
question_ids = {q[0]: q[1] for q in relevant_questions}

# Filter for reliable participants (PRI >= 0.3)
def get_reliable_responses(question_id):
    query = f"""
    SELECT r.*, p.pri_score
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3 AND r.question_id = '{question_id}'
    """
    return pd.read_sql_query(query, conn)

# Analysis 2.1: AI Usage Patterns
print("\n" + "="*80)
print("ANALYSIS 2.1: AI USAGE PATTERNS")
print("="*80)

def analyze_usage_patterns():
    results = {}
    
    # Get frequency distributions for each usage type
    for q_num in ['Q18', 'Q19', 'Q20', 'Q21', 'Q22']:
        if q_num in question_ids:
            df = get_reliable_responses(question_ids[q_num])
            freq_dist = df['response'].value_counts(normalize=True).sort_index() * 100
            results[q_num] = freq_dist
            
            print(f"\n{q_num} Frequency Distribution:")
            for val, pct in freq_dist.items():
                print(f"  {val}: {pct:.1f}%")
    
    # Check if people required to use AI at work are more likely to use it personally
    if 'Q18' in question_ids and 'Q20' in question_ids:
        # Get participants who answered both questions
        q18_df = get_reliable_responses(question_ids['Q18'])
        q20_df = get_reliable_responses(question_ids['Q20'])
        
        merged_df = pd.merge(
            q18_df[['participant_id', 'response']], 
            q20_df[['participant_id', 'response']], 
            on='participant_id', 
            suffixes=('_work_required', '_personal')
        )
        
        # Convert frequency to numeric scale
        freq_map = {'never': 0, 'annually': 1, 'monthly': 2, 'weekly': 3, 'daily': 4}
        merged_df['work_required_num'] = merged_df['response_work_required'].map(freq_map)
        merged_df['personal_num'] = merged_df['response_personal'].map(freq_map)
        
        # Calculate correlation
        correlation = merged_df['work_required_num'].corr(merged_df['personal_num'])
        print(f"\nCorrelation between required work use and personal use: {correlation:.3f}")
        
        # Compare daily work users vs non-users
        daily_work = merged_df[merged_df['response_work_required'] == 'daily']
        never_work = merged_df[merged_df['response_work_required'] == 'never']
        
        print(f"\nAmong those required to use AI daily at work:")
        print(f"  Use AI daily in personal life: {(daily_work['response_personal'] == 'daily').mean() * 100:.1f}%")
        print(f"\nAmong those never required to use AI at work:")
        print(f"  Use AI daily in personal life: {(never_work['response_personal'] == 'daily').mean() * 100:.1f}%")
    
    return results

usage_results = analyze_usage_patterns()

# Analysis 2.2: AI and Future Outlook
print("\n" + "="*80)
print("ANALYSIS 2.2: AI AND FUTURE OUTLOOK")
print("="*80)

def analyze_future_outlook():
    results = {}
    
    # Get expectations for each future impact area
    for q_num in ['Q23', 'Q24', 'Q25', 'Q26', 'Q27']:
        if q_num in question_ids:
            df = get_reliable_responses(question_ids[q_num])
            outlook_dist = df['response'].value_counts(normalize=True).sort_index() * 100
            results[q_num] = outlook_dist
            
            # Calculate net optimism score
            outlook_map = {
                'Profoundly Worse': -2, 
                'Noticeably Worse': -1, 
                'No Major Change': 0, 
                'Noticeably Better': 1, 
                'Profoundly Better': 2
            }
            df['outlook_score'] = df['response'].map(outlook_map)
            mean_score = df['outlook_score'].mean()
            
            print(f"\n{q_num} Future Outlook Distribution:")
            for val, pct in outlook_dist.items():
                print(f"  {val}: {pct:.1f}%")
            print(f"  Mean outlook score: {mean_score:.2f} (-2=very pessimistic, +2=very optimistic)")
    
    return results

outlook_results = analyze_future_outlook()

# Analysis 2.3: Optimism vs. Pessimism Correlation
print("\n" + "="*80)
print("ANALYSIS 2.3: OPTIMISM VS. PESSIMISM CORRELATION")
print("="*80)

def analyze_optimism_correlation():
    if 'Q5' not in question_ids:
        print("Q5 not found in question mapping")
        return
    
    # Get Q5 responses
    q5_df = get_reliable_responses(question_ids['Q5'])
    
    # Analyze correlation with future predictions
    future_questions = ['Q23', 'Q24', 'Q25', 'Q26', 'Q27']
    
    for q_num in future_questions:
        if q_num in question_ids:
            future_df = get_reliable_responses(question_ids[q_num])
            
            # Merge datasets
            merged = pd.merge(
                q5_df[['participant_id', 'response']],
                future_df[['participant_id', 'response']],
                on='participant_id',
                suffixes=('_q5', '_future')
            )
            
            # Cross-tabulation
            print(f"\n{q_num} by General AI Sentiment (Q5):")
            crosstab = pd.crosstab(
                merged['response_q5'], 
                merged['response_future'],
                normalize='index'
            ) * 100
            
            # Focus on key insights
            if 'More excited than concerned' in crosstab.index:
                excited_row = crosstab.loc['More excited than concerned']
                if 'Profoundly Better' in excited_row.index:
                    print(f"  Among 'More excited': {excited_row.get('Profoundly Better', 0):.1f}% expect 'Profoundly Better'")
                if 'Noticeably Better' in excited_row.index:
                    print(f"  Among 'More excited': {excited_row.get('Noticeably Better', 0):.1f}% expect 'Noticeably Better'")
            
            if 'More concerned than excited' in crosstab.index:
                concerned_row = crosstab.loc['More concerned than excited']
                if 'Profoundly Worse' in concerned_row.index:
                    print(f"  Among 'More concerned': {concerned_row.get('Profoundly Worse', 0):.1f}% expect 'Profoundly Worse'")
                if 'Noticeably Worse' in concerned_row.index:
                    print(f"  Among 'More concerned': {concerned_row.get('Noticeably Worse', 0):.1f}% expect 'Noticeably Worse'")

analyze_optimism_correlation()

# Analysis 2.4: Trust and Usage
print("\n" + "="*80)
print("ANALYSIS 2.4: TRUST AND USAGE CORRELATION")
print("="*80)

def analyze_trust_usage():
    if 'Q17' not in question_ids or 'Q21' not in question_ids:
        print("Required questions not found")
        return
    
    # Get Q17 (trust AI chatbot) and Q21 (use for sensitive issues)
    q17_df = get_reliable_responses(question_ids['Q17'])
    q21_df = get_reliable_responses(question_ids['Q21'])
    
    # Merge datasets
    merged = pd.merge(
        q17_df[['participant_id', 'response']],
        q21_df[['participant_id', 'response']],
        on='participant_id',
        suffixes=('_trust', '_sensitive')
    )
    
    # Analyze correlation
    trust_map = {
        'Strongly Distrust': 1,
        'Somewhat Distrust': 2,
        'Neither Trust Nor Distrust': 3,
        'Somewhat Trust': 4,
        'Strongly Trust': 5
    }
    
    freq_map = {'never': 0, 'annually': 1, 'monthly': 2, 'weekly': 3, 'daily': 4}
    
    merged['trust_score'] = merged['response_trust'].map(trust_map)
    merged['sensitive_freq'] = merged['response_sensitive'].map(freq_map)
    
    # Calculate correlation
    correlation = merged['trust_score'].corr(merged['sensitive_freq'])
    print(f"\nCorrelation between AI trust and sensitive use frequency: {correlation:.3f}")
    
    # Detailed breakdown
    print("\nUsage of AI for sensitive issues by trust level:")
    trust_levels = ['Strongly Trust', 'Somewhat Trust', 'Neither Trust Nor Distrust', 
                    'Somewhat Distrust', 'Strongly Distrust']
    
    for trust_level in trust_levels:
        if trust_level in merged['response_trust'].values:
            subset = merged[merged['response_trust'] == trust_level]
            daily_pct = (subset['response_sensitive'] == 'daily').mean() * 100
            weekly_pct = (subset['response_sensitive'] == 'weekly').mean() * 100
            never_pct = (subset['response_sensitive'] == 'never').mean() * 100
            print(f"\n  {trust_level}:")
            print(f"    Use daily: {daily_pct:.1f}%")
            print(f"    Use weekly: {weekly_pct:.1f}%")
            print(f"    Never use: {never_pct:.1f}%")

analyze_trust_usage()

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 2 ANALYSIS COMPLETE")
print("="*80)