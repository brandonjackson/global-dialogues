#!/usr/bin/env python3
"""
Analysis script for Investigation Question 13.1.2: Creating an AI Sentiment Score
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def normalize_q5(response):
    """Normalize Q5 responses (excited vs concerned)"""
    if pd.isna(response) or response == '--':
        return None
    response = response.strip().lower()
    if 'more excited' in response:
        return 5  # Most positive
    elif 'equally' in response:
        return 3  # Neutral
    elif 'more concerned' in response:
        return 1  # Most negative
    else:
        return None

def normalize_q22(response):
    """Normalize Q22 responses (AI chatbot impact)"""
    if pd.isna(response) or response == '--':
        return None
    response = response.strip().lower()
    if 'benefits far outweigh' in response:
        return 5
    elif 'benefits slightly outweigh' in response:
        return 4
    elif 'equal' in response:
        return 3
    elif 'risks slightly outweigh' in response:
        return 2
    elif 'risks far outweigh' in response:
        return 1
    else:
        return None

def normalize_q45(response):
    """Normalize Q45 responses (overall impact on daily life)"""
    if pd.isna(response) or response == '--':
        return None
    response = response.strip().lower()
    if 'profoundly better' in response:
        return 5
    elif 'noticeably better' in response:
        return 4
    elif 'no major change' in response:
        return 3
    elif 'noticeably worse' in response:
        return 2
    elif 'profoundly worse' in response:
        return 1
    else:
        return None

def normalize_trust(response):
    """Normalize trust responses"""
    if pd.isna(response) or response == '--':
        return None
    response = response.strip().lower()
    if 'strongly trust' in response:
        return 5
    elif 'somewhat trust' in response:
        return 4
    elif 'neither' in response:
        return 3
    elif 'somewhat distrust' in response:
        return 2
    elif 'strongly distrust' in response:
        return 1
    else:
        return None

def normalize_q43(response):
    """Normalize Q43 responses (job availability)"""
    if pd.isna(response) or response == '--':
        return None
    response = response.strip().lower()
    if 'profoundly better' in response:
        return 5
    elif 'noticeably better' in response:
        return 4
    elif 'no major change' in response:
        return 3
    elif 'noticeably worse' in response:
        return 2
    elif 'profoundly worse' in response:
        return 1
    else:
        return None

def calculate_ai_sentiment_score(row):
    """
    Calculate AI Sentiment Score from Q5, Q22, Q45
    Higher score = more positive sentiment toward AI
    """
    scores = []
    
    # Q5 - Excitement vs Concern
    q5_val = normalize_q5(row['Q5'])
    if q5_val is not None:
        scores.append(q5_val)
    
    # Q22 - AI Chatbot Impact
    q22_val = normalize_q22(row['Q22'])
    if q22_val is not None:
        scores.append(q22_val)
    
    # Q45 - Overall Impact on Daily Life
    q45_val = normalize_q45(row['Q45'])
    if q45_val is not None:
        scores.append(q45_val)
    
    # Require at least 2 out of 3 questions
    if len(scores) < 2:
        return None
    
    # Return average score scaled to 0-100
    return (np.mean(scores) - 1) * 25  # Convert 1-5 scale to 0-100

def main():
    # Connect to database
    conn = sqlite3.connect('Data/GD4/GD4.db')
    
    # Load participant responses
    query = """
    SELECT p.participant_id, p.sample_provider_id,
           p.Q5, p.Q22, p.Q45,
           p.Q28, p.Q29, p.Q43,
           pp.pri_score
    FROM participant_responses p
    LEFT JOIN participants pp ON p.participant_id = pp.participant_id
    WHERE pp.pri_score >= 0.3
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Loaded {len(df)} participants with PRI >= 0.3")
    
    # Calculate AI Sentiment Score
    df['ai_sentiment_score'] = df.apply(calculate_ai_sentiment_score, axis=1)
    
    # Remove rows with missing scores
    df_valid = df.dropna(subset=['ai_sentiment_score'])
    print(f"\nValid AI sentiment scores calculated for {len(df_valid)} participants")
    
    # Basic statistics
    print("\n=== AI Sentiment Score Statistics ===")
    print(f"Mean: {df_valid['ai_sentiment_score'].mean():.2f}")
    print(f"Median: {df_valid['ai_sentiment_score'].median():.2f}")
    print(f"Std Dev: {df_valid['ai_sentiment_score'].std():.2f}")
    print(f"Min: {df_valid['ai_sentiment_score'].min():.2f}")
    print(f"Max: {df_valid['ai_sentiment_score'].max():.2f}")
    
    # Categorize sentiment
    def categorize_sentiment(score):
        if score < 25:
            return 'Pessimistic'
        elif score < 50:
            return 'Cautious'
        elif score < 75:
            return 'Optimistic'
        else:
            return 'Very Optimistic'
    
    df_valid['sentiment_category'] = df_valid['ai_sentiment_score'].apply(categorize_sentiment)
    print("\n=== Sentiment Distribution ===")
    print(df_valid['sentiment_category'].value_counts(normalize=True).round(3))
    
    # Research Question 1: Correlation with trust in social media and AI companies
    print("\n=== Research Question 1: Trust Correlations ===")
    
    # Normalize trust scores
    df_valid['trust_social_media'] = df_valid['Q28'].apply(normalize_trust)
    df_valid['trust_ai_companies'] = df_valid['Q29'].apply(normalize_trust)
    
    # Filter to valid responses
    df_trust = df_valid.dropna(subset=['trust_social_media', 'trust_ai_companies'])
    print(f"\nValid responses for trust analysis: {len(df_trust)}")
    
    # Correlations
    corr_social, p_social = stats.spearmanr(df_trust['ai_sentiment_score'], 
                                            df_trust['trust_social_media'])
    corr_ai, p_ai = stats.spearmanr(df_trust['ai_sentiment_score'], 
                                    df_trust['trust_ai_companies'])
    
    print(f"\nCorrelation with trust in social media companies: {corr_social:.4f} (p={p_social:.6f})")
    print(f"Correlation with trust in AI companies: {corr_ai:.4f} (p={p_ai:.6f})")
    
    # Compare pessimistic vs optimistic groups
    pessimistic = df_trust[df_trust['ai_sentiment_score'] < 25]
    optimistic = df_trust[df_trust['ai_sentiment_score'] >= 50]
    
    print(f"\n=== Trust Levels by Sentiment Group ===")
    print(f"Pessimistic (n={len(pessimistic)}):")
    print(f"  Trust social media: {pessimistic['trust_social_media'].mean():.2f}")
    print(f"  Trust AI companies: {pessimistic['trust_ai_companies'].mean():.2f}")
    print(f"Optimistic (n={len(optimistic)}):")
    print(f"  Trust social media: {optimistic['trust_social_media'].mean():.2f}")
    print(f"  Trust AI companies: {optimistic['trust_ai_companies'].mean():.2f}")
    
    # Research Question 2: Correlation with job availability beliefs (Q43)
    print("\n=== Research Question 2: Job Impact Beliefs ===")
    
    df_valid['job_impact'] = df_valid['Q43'].apply(normalize_q43)
    df_jobs = df_valid.dropna(subset=['job_impact'])
    print(f"\nValid responses for job impact analysis: {len(df_jobs)}")
    
    corr_jobs, p_jobs = stats.spearmanr(df_jobs['ai_sentiment_score'], 
                                        df_jobs['job_impact'])
    print(f"Correlation with job availability beliefs: {corr_jobs:.4f} (p={p_jobs:.6f})")
    
    # Group analysis
    job_groups = df_jobs.groupby('sentiment_category')['job_impact'].agg(['mean', 'std', 'count'])
    print("\nJob impact beliefs by sentiment category (1=much worse, 5=much better):")
    print(job_groups)
    
    # Additional analysis: Components of sentiment score
    print("\n=== Component Analysis ===")
    df_components = df_valid.copy()
    df_components['Q5_norm'] = df_components['Q5'].apply(normalize_q5)
    df_components['Q22_norm'] = df_components['Q22'].apply(normalize_q22)
    df_components['Q45_norm'] = df_components['Q45'].apply(normalize_q45)
    
    # Correlation matrix between components
    components = ['Q5_norm', 'Q22_norm', 'Q45_norm']
    corr_matrix = df_components[components].corr(method='spearman')
    print("\nCorrelation between sentiment components:")
    print(corr_matrix.round(3))
    
    # Which component drives trust correlation most?
    print("\n=== Individual Component Correlations with AI Company Trust ===")
    df_comp_trust = df_components.dropna(subset=['trust_ai_companies'])
    
    for comp in components:
        df_temp = df_comp_trust.dropna(subset=[comp])
        if len(df_temp) > 1:
            corr, p = stats.spearmanr(df_temp[comp], df_temp['trust_ai_companies'])
            print(f"{comp}: r={corr:.4f}, p={p:.6f}")
    
    conn.close()
    
    print("\n=== Analysis Complete ===")
    return df_valid

if __name__ == "__main__":
    main()