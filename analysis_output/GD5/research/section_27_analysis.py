#!/usr/bin/env python3
"""
Section 27: Economic Anxiety and Interspecies Generosity
This analysis explores how economic concerns influence attitudes toward animal rights
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Get participant responses with PRI filtering
def get_participant_data():
    query = """
    SELECT pr.*, p.pri_score
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    """
    return pd.read_sql_query(query, conn)

print("Loading participant data...")
df = get_participant_data()
print(f"Total reliable participants: {len(df)}")

# Helper function for parsing Q91 (economic rights)
def has_economic_support(response):
    """Check if response supports economic rights for animals"""
    if pd.isna(response) or response == '--':
        return False
    response_lower = str(response).lower()
    return (('earn money' in response_lower or 
             'own' in response_lower or 
             'sell' in response_lower) and 
            'none of the above' not in response_lower)

# ============================================================================
# ANALYSIS 27.1: Economic Anxiety and Animal Rights Opposition
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 27.1: ECONOMIC ANXIETY AND ANIMAL RIGHTS OPPOSITION")
print("="*80)

def analyze_economic_anxiety_rights(df):
    print("\nDo economically anxious respondents show less support for animal rights?")
    
    # Define economic anxiety groups
    # Q23: Cost of living expectations
    # Q26: Job availability expectations
    
    # Create anxiety scores
    outlook_map = {
        'Profoundly Worse': -2,
        'Noticeably Worse': -1,
        'No Major Change': 0,
        'Noticeably Better': 1,
        'Profoundly Better': 2
    }
    
    df['cost_outlook'] = df['Q23'].map(outlook_map)
    df['job_outlook'] = df['Q26'].map(outlook_map)
    
    # Combined economic anxiety (negative = anxious)
    df['economic_anxiety'] = df[['cost_outlook', 'job_outlook']].mean(axis=1)
    
    # Define anxiety groups
    anxious = df[df['economic_anxiety'] < 0].copy()
    optimistic = df[df['economic_anxiety'] > 0].copy()
    neutral = df[df['economic_anxiety'] == 0].copy()
    
    print(f"\nEconomic outlook groups:")
    print(f"  Anxious (negative outlook): {len(anxious)} ({len(anxious)/len(df)*100:.1f}%)")
    print(f"  Neutral: {len(neutral)} ({len(neutral)/len(df)*100:.1f}%)")
    print(f"  Optimistic (positive outlook): {len(optimistic)} ({len(optimistic)/len(df)*100:.1f}%)")
    
    # Analyze Q91 (economic rights) support
    print("\n" + "-"*60)
    print("Support for animal economic rights (Q91) by economic outlook:")
    
    anxious['supports_economic'] = anxious['Q91'].apply(has_economic_support)
    optimistic['supports_economic'] = optimistic['Q91'].apply(has_economic_support)
    neutral['supports_economic'] = neutral['Q91'].apply(has_economic_support)
    
    anxious_support = anxious['supports_economic'].mean() * 100
    optimistic_support = optimistic['supports_economic'].mean() * 100
    neutral_support = neutral['supports_economic'].mean() * 100
    
    print(f"  Anxious: {anxious_support:.1f}%")
    print(f"  Neutral: {neutral_support:.1f}%")
    print(f"  Optimistic: {optimistic_support:.1f}%")
    print(f"  Difference (Anxious - Optimistic): {anxious_support - optimistic_support:.1f} percentage points")
    
    # Statistical test
    if len(anxious) > 0 and len(optimistic) > 0:
        # Chi-square test
        anxious_yes = anxious['supports_economic'].sum()
        anxious_no = len(anxious) - anxious_yes
        optimistic_yes = optimistic['supports_economic'].sum()
        optimistic_no = len(optimistic) - optimistic_yes
        
        contingency = np.array([[anxious_yes, anxious_no], 
                                [optimistic_yes, optimistic_no]])
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
        
        print(f"\nStatistical significance: p={p_value:.4f}")
        print(f"Result: {'Significant' if p_value < 0.05 else 'Not significant'} difference")
    
    # Analyze Q77 (political representation) support
    print("\n" + "-"*60)
    print("Support for animal political representation (Q77) by economic outlook:")
    
    political_support = [
        'Yes, they should be able to vote through human proxies or guardians.',
        'Yes, they should be able to vote, but only on laws or decisions that directly affect them.',
        'Yes, they should have a voice, but their vote should not be binding.',
        'Yes, they should be recognized as a formal political constituency with dedicated representatives in government.'
    ]
    
    anxious_political = anxious['Q77'].isin(political_support).mean() * 100
    optimistic_political = optimistic['Q77'].isin(political_support).mean() * 100
    neutral_political = neutral['Q77'].isin(political_support).mean() * 100
    
    print(f"  Anxious: {anxious_political:.1f}%")
    print(f"  Neutral: {neutral_political:.1f}%")
    print(f"  Optimistic: {optimistic_political:.1f}%")
    print(f"  Difference (Anxious - Optimistic): {anxious_political - optimistic_political:.1f} percentage points")
    
    # Correlation analysis
    print("\n" + "-"*60)
    print("Correlation analysis:")
    
    df['supports_economic'] = df['Q91'].apply(has_economic_support)
    df['supports_political'] = df['Q77'].isin(political_support)
    
    # Calculate correlations
    econ_corr = df['economic_anxiety'].corr(df['supports_economic'].astype(int))
    political_corr = df['economic_anxiety'].corr(df['supports_political'].astype(int))
    
    print(f"  Economic anxiety vs. economic rights support: r={econ_corr:.3f}")
    print(f"  Economic anxiety vs. political rights support: r={political_corr:.3f}")
    
    # Extreme anxiety analysis
    print("\n" + "-"*60)
    print("Extreme economic anxiety analysis:")
    
    very_anxious = df[df['economic_anxiety'] <= -1.5]
    very_optimistic = df[df['economic_anxiety'] >= 1.5]
    
    if len(very_anxious) > 0:
        very_anxious_econ = very_anxious['supports_economic'].mean() * 100
        print(f"  Very anxious (score <= -1.5, n={len(very_anxious)}): {very_anxious_econ:.1f}% support economic rights")
    
    if len(very_optimistic) > 0:
        very_optimistic_econ = very_optimistic['supports_economic'].mean() * 100
        print(f"  Very optimistic (score >= 1.5, n={len(very_optimistic)}): {very_optimistic_econ:.1f}% support economic rights")

analyze_economic_anxiety_rights(df)

# ============================================================================
# ANALYSIS 27.2: Community Optimism and Relational Approaches
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 27.2: COMMUNITY OPTIMISM AND RELATIONAL APPROACHES")
print("="*80)

def analyze_community_optimism_relationships(df):
    print("\nCorrelation between community well-being optimism and relational approaches")
    
    # Q25: Community well-being expectations
    # Q70: Preferred future (Future A = Building Relationships)
    
    # Map community outlook
    outlook_map = {
        'Profoundly Worse': -2,
        'Noticeably Worse': -1,
        'No Major Change': 0,
        'Noticeably Better': 1,
        'Profoundly Better': 2
    }
    
    df['community_outlook'] = df['Q25'].map(outlook_map)
    
    # Identify Future A preference
    future_a = 'Future A: Building ongoing relationships and communication'
    df['prefers_relationships'] = df['Q70'] == future_a
    
    # Group by community outlook
    print("\nPreference for Building Relationships (Future A) by community outlook:")
    
    outlook_groups = df.groupby('community_outlook')
    for outlook_score, group in outlook_groups:
        if pd.notna(outlook_score) and len(group) > 10:
            relationship_pct = group['prefers_relationships'].mean() * 100
            outlook_label = {-2: 'Profoundly Worse', -1: 'Noticeably Worse', 
                           0: 'No Change', 1: 'Noticeably Better', 
                           2: 'Profoundly Better'}.get(outlook_score, f'Score {outlook_score}')
            print(f"  {outlook_label}: {relationship_pct:.1f}% (n={len(group)})")
    
    # Calculate correlation
    correlation = df['community_outlook'].corr(df['prefers_relationships'].astype(int))
    print(f"\nCorrelation: r={correlation:.3f}")
    
    # Compare extremes
    print("\n" + "-"*60)
    print("Comparing community outlook extremes:")
    
    pessimistic_community = df[df['Q25'].isin(['Profoundly Worse', 'Noticeably Worse'])]
    optimistic_community = df[df['Q25'].isin(['Profoundly Better', 'Noticeably Better'])]
    
    if len(pessimistic_community) > 0:
        pess_relationships = (pessimistic_community['Q70'] == future_a).mean() * 100
        print(f"  Community pessimists (n={len(pessimistic_community)}): {pess_relationships:.1f}% prefer relationships")
    
    if len(optimistic_community) > 0:
        opt_relationships = (optimistic_community['Q70'] == future_a).mean() * 100
        print(f"  Community optimists (n={len(optimistic_community)}): {opt_relationships:.1f}% prefer relationships")
    
    if len(pessimistic_community) > 0 and len(optimistic_community) > 0:
        print(f"  Difference: {opt_relationships - pess_relationships:.1f} percentage points")
        
        # Statistical test
        pess_yes = (pessimistic_community['Q70'] == future_a).sum()
        pess_no = len(pessimistic_community) - pess_yes
        opt_yes = (optimistic_community['Q70'] == future_a).sum()
        opt_no = len(optimistic_community) - opt_yes
        
        contingency = np.array([[pess_yes, pess_no], [opt_yes, opt_no]])
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
        
        print(f"\nStatistical significance: p={p_value:.4f}")
        print(f"Result: {'Significant' if p_value < 0.05 else 'Not significant'} difference")
    
    # Analyze other future preferences
    print("\n" + "-"*60)
    print("Full breakdown of future preferences by community outlook:")
    
    future_b = 'Future B: Including all voices in shared decision-making'
    future_c = 'Future C: Granting legal rights and representation'
    
    for outlook_label, outlook_values in [
        ('Pessimistic', ['Profoundly Worse', 'Noticeably Worse']),
        ('Neutral', ['No Major Change']),
        ('Optimistic', ['Profoundly Better', 'Noticeably Better'])
    ]:
        group = df[df['Q25'].isin(outlook_values)]
        if len(group) > 0:
            print(f"\n{outlook_label} about community (n={len(group)}):")
            a_pct = (group['Q70'] == future_a).mean() * 100
            b_pct = (group['Q70'] == future_b).mean() * 100
            c_pct = (group['Q70'] == future_c).mean() * 100
            print(f"  Future A (Relationships): {a_pct:.1f}%")
            print(f"  Future B (Shared Decision): {b_pct:.1f}%")
            print(f"  Future C (Legal Rights): {c_pct:.1f}%")
    
    # Test if community optimism is strongest predictor
    print("\n" + "-"*60)
    print("Comparing predictors of relational approach preference:")
    
    # Compare with other optimism measures
    predictors = {
        'Community outlook': df['community_outlook'],
        'Cost of living outlook': df['cost_outlook'],
        'Job outlook': df['job_outlook'],
        'Overall economic anxiety': df['economic_anxiety']
    }
    
    for predictor_name, predictor_values in predictors.items():
        if predictor_name in ['Community outlook', 'Cost of living outlook', 'Job outlook', 'Overall economic anxiety']:
            corr = predictor_values.corr(df['prefers_relationships'].astype(int))
            print(f"  {predictor_name}: r={corr:.3f}")

analyze_community_optimism_relationships(df)

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 27 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")