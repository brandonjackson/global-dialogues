#!/usr/bin/env python3
"""
Analysis script for Investigation Question 13.1.1: Creating a Loneliness Score
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def normalize_response(response):
    """Normalize response variations to standard format"""
    if pd.isna(response) or response == '--':
        return None
    response = response.strip().lower()
    if 'never' in response:
        return 'Never'
    elif 'rarely' in response:
        return 'Rarely' 
    elif 'sometimes' in response:
        return 'Sometimes'
    elif 'often' in response or 'always' in response:
        return 'Often'
    else:
        return None

def calculate_loneliness_score(row):
    """
    Calculate loneliness score from Q51-Q58
    Higher score = more loneliness
    
    Q51, Q55, Q56, Q58 are reverse scored (positive items)
    Q52, Q53, Q54, Q57 are regular scored (negative items)
    """
    
    # Define scoring
    regular_scoring = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4}
    reverse_scoring = {'Never': 4, 'Rarely': 3, 'Sometimes': 2, 'Often': 1}
    
    score = 0
    valid_items = 0
    
    # Reverse scored items (positive - higher frequency means less loneliness)
    for q in ['Q51', 'Q55', 'Q56', 'Q58']:
        val = normalize_response(row[q])
        if val and val in reverse_scoring:
            score += reverse_scoring[val]
            valid_items += 1
    
    # Regular scored items (negative - higher frequency means more loneliness)  
    for q in ['Q52', 'Q53', 'Q54', 'Q57']:
        val = normalize_response(row[q])
        if val and val in regular_scoring:
            score += regular_scoring[val]
            valid_items += 1
    
    # Return None if too many missing items
    if valid_items < 6:  # Require at least 6 out of 8 items
        return None
    
    # Return average score scaled to 8 items
    return (score / valid_items) * 8

def main():
    # Connect to database
    conn = sqlite3.connect('Data/GD4/GD4.db')
    
    # Load participant responses
    query = """
    SELECT p.participant_id, p.sample_provider_id,
           p.Q51, p.Q52, p.Q53, p.Q54, p.Q55, p.Q56, p.Q57, p.Q58,
           p.Q97, p.Q71, p.Q67, p.Q68, p.Q69,
           pp.pri_score
    FROM participant_responses p
    LEFT JOIN participants pp ON p.participant_id = pp.participant_id
    WHERE pp.pri_score >= 0.3
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Loaded {len(df)} participants with PRI >= 0.3")
    
    # Calculate loneliness scores
    df['loneliness_score'] = df.apply(calculate_loneliness_score, axis=1)
    
    # Remove rows with missing loneliness scores
    df_valid = df.dropna(subset=['loneliness_score'])
    print(f"\nValid loneliness scores calculated for {len(df_valid)} participants")
    
    # Basic statistics
    print("\n=== Loneliness Score Statistics ===")
    print(f"Mean: {df_valid['loneliness_score'].mean():.2f}")
    print(f"Median: {df_valid['loneliness_score'].median():.2f}")
    print(f"Std Dev: {df_valid['loneliness_score'].std():.2f}")
    print(f"Min: {df_valid['loneliness_score'].min():.2f}")
    print(f"Max: {df_valid['loneliness_score'].max():.2f}")
    
    # Research Question 1: Correlation with romantic relationship with AI (Q97)
    print("\n=== Research Question 1: Loneliness & AI Romance ===")
    
    # Normalize Q97 responses
    df_valid['Q97_normalized'] = df_valid['Q97'].apply(normalize_q96_response)
    
    # Filter to valid Q97 responses
    df_q96 = df_valid.dropna(subset=['Q97_normalized'])
    print(f"\nValid responses for Q97 analysis: {len(df_q96)}")
    
    # Group analysis
    q96_groups = df_q96.groupby('Q97_normalized')['loneliness_score'].agg(['mean', 'std', 'count'])
    print("\nLoneliness scores by AI romance willingness:")
    print(q96_groups)
    
    # Statistical test (ANOVA for multiple groups)
    groups = [group['loneliness_score'].values for name, group in df_q96.groupby('Q97_normalized')]
    f_stat, p_value = stats.f_oneway(*groups)
    print(f"\nANOVA F-statistic: {f_stat:.4f}")
    print(f"P-value: {p_value:.6f}")
    
    # Correlation using numeric scale
    q96_numeric = {'Definitely not': 1, 'Probably not': 2, 'Unsure': 3, 'Possibly': 4, 'Definitely': 5}
    df_q96['Q97_numeric'] = df_q96['Q97_normalized'].map(q96_numeric)
    
    df_corr = df_q96.dropna(subset=['Q97_numeric'])
    correlation, p_corr = stats.spearmanr(df_corr['loneliness_score'], df_corr['Q97_numeric'])
    print(f"\nSpearman correlation: {correlation:.4f}")
    print(f"P-value: {p_corr:.6f}")
    
    # Research Question 2: Mental well-being impact (Q71)
    print("\n=== Research Question 2: Loneliness & Mental Well-being Impact ===")
    
    # Q67 appears to be the question about using AI for support
    
    # Filter to those who used AI for support
    df_ai_users = df_valid[df_valid['Q67'] == 'Yes'].copy()
    print(f"\nParticipants who used AI for emotional support: {len(df_ai_users)}")
    
    if len(df_ai_users) > 0:
        # Normalize Q71 responses
        df_ai_users['Q71_normalized'] = df_ai_users['Q71'].apply(normalize_q70_response)
        df_q70 = df_ai_users.dropna(subset=['Q71_normalized'])
        
        print(f"Valid Q71 responses: {len(df_q70)}")
        
        # Quartile analysis
        quartiles = pd.qcut(df_q70['loneliness_score'], q=4, labels=['Q1 (Least lonely)', 'Q2', 'Q3', 'Q4 (Most lonely)'])
        df_q70['loneliness_quartile'] = quartiles
        
        # Create numeric scale for Q71
        q70_numeric = {
            'Very negative': 1, 'Somewhat negative': 2, 'Neutral': 3,
            'Somewhat positive': 4, 'Very positive': 5
        }
        df_q70['Q71_numeric'] = df_q70['Q71_normalized'].map(q70_numeric)
        
        # Group analysis
        q70_groups = df_q70.groupby('loneliness_quartile')['Q71_numeric'].agg(['mean', 'std', 'count'])
        print("\nMental well-being impact by loneliness quartile:")
        print(q70_groups)
        
        # Correlation
        df_q70_corr = df_q70.dropna(subset=['Q71_numeric'])
        if len(df_q70_corr) > 1:
            correlation2, p_corr2 = stats.spearmanr(df_q70_corr['loneliness_score'], df_q70_corr['Q71_numeric'])
            print(f"\nSpearman correlation (loneliness vs positive impact): {correlation2:.4f}")
            print(f"P-value: {p_corr2:.6f}")
    
    conn.close()
    
    print("\n=== Analysis Complete ===")
    return df_valid

def normalize_q96_response(response):
    """Normalize Q97 responses about romantic relationship with AI"""
    if pd.isna(response) or response == '--' or response == '':
        return None
    response = response.strip().lower()
    if 'definitely not' in response:
        return 'Definitely not'
    elif 'probably not' in response:
        return 'Probably not'
    elif 'unsure' in response or 'maybe' in response:
        return 'Unsure'
    elif 'possibly' in response:
        return 'Possibly'
    elif 'yes' in response and 'definitely' in response:
        return 'Definitely'
    else:
        return None

def normalize_q70_response(response):
    """Normalize Q71 responses about mental well-being impact"""
    if pd.isna(response) or response == '--' or response == '' or 'never used' in response.lower():
        return None
    response = response.strip().lower()
    if 'very harmful' in response:
        return 'Very negative'
    elif 'harmful' in response and 'very' not in response:
        return 'Somewhat negative'
    elif 'no real impact' in response or 'neutral' in response:
        return 'Neutral'
    elif 'beneficial' in response and 'very' not in response:
        return 'Somewhat positive'
    elif 'very beneficial' in response:
        return 'Very positive'
    else:
        return None

if __name__ == "__main__":
    main()