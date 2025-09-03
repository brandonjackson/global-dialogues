#!/usr/bin/env python3
"""
Section 2: AI in Society and Personal Life Analysis
Using participant_responses table which has Q numbers directly
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

# ============================================================================
# ANALYSIS 2.1: AI USAGE PATTERNS
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 2.1: AI USAGE PATTERNS")
print("="*80)

def analyze_usage_patterns(df):
    print("\nFrequency distributions for AI usage:")
    
    # Questions 18-22 usage patterns
    usage_questions = {
        'Q18': 'Expected to use AI at work',
        'Q19': 'Chosen to use AI at work', 
        'Q20': 'Chosen to use AI in personal life',
        'Q21': 'AI for sensitive personal issues',
        'Q22': 'AI for autonomous real-world actions'
    }
    
    for q_num, description in usage_questions.items():
        if q_num in df.columns:
            freq_dist = df[q_num].value_counts(normalize=True).sort_index() * 100
            print(f"\n{q_num}: {description}")
            for val, pct in freq_dist.items():
                if pd.notna(val):
                    print(f"  {val}: {pct:.1f}%")
    
    # Analyze correlation between required work use and personal use
    print("\n" + "-"*60)
    print("Correlation: Required work use (Q18) vs Personal use (Q20)")
    print("-"*60)
    
    # Filter to those who answered both questions
    both_answered = df[df['Q18'].notna() & df['Q20'].notna()].copy()
    
    # Convert to numeric scale
    freq_map = {'never': 0, 'annually': 1, 'monthly': 2, 'weekly': 3, 'daily': 4}
    both_answered['Q18_num'] = both_answered['Q18'].map(freq_map)
    both_answered['Q20_num'] = both_answered['Q20'].map(freq_map)
    
    # Calculate correlation
    correlation = both_answered['Q18_num'].corr(both_answered['Q20_num'])
    print(f"Pearson correlation: {correlation:.3f}")
    
    # Compare daily work users vs never work users
    daily_work = both_answered[both_answered['Q18'] == 'daily']
    never_work = both_answered[both_answered['Q18'] == 'never']
    
    print(f"\nAmong those REQUIRED to use AI daily at work (n={len(daily_work)}):")
    if len(daily_work) > 0:
        print(f"  Use AI daily in personal life: {(daily_work['Q20'] == 'daily').mean() * 100:.1f}%")
        print(f"  Use AI weekly+ in personal life: {daily_work['Q20'].isin(['daily', 'weekly']).mean() * 100:.1f}%")
    
    print(f"\nAmong those NEVER required to use AI at work (n={len(never_work)}):")
    if len(never_work) > 0:
        print(f"  Use AI daily in personal life: {(never_work['Q20'] == 'daily').mean() * 100:.1f}%")
        print(f"  Use AI weekly+ in personal life: {never_work['Q20'].isin(['daily', 'weekly']).mean() * 100:.1f}%")
    
    # Statistical test
    if len(daily_work) > 0 and len(never_work) > 0:
        chi2, p_value = stats.chi2_contingency(pd.crosstab(
            both_answered['Q18'].isin(['daily', 'weekly']),
            both_answered['Q20'].isin(['daily', 'weekly'])
        ))[:2]
        print(f"\nChi-square test (frequent work use vs frequent personal use): p={p_value:.4f}")

analyze_usage_patterns(df)

# ============================================================================
# ANALYSIS 2.2: AI AND FUTURE OUTLOOK
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 2.2: AI AND FUTURE OUTLOOK")
print("="*80)

def analyze_future_outlook(df):
    outlook_questions = {
        'Q23': 'Cost of living',
        'Q24': 'Free time',
        'Q25': "Community's well-being",
        'Q26': 'Availability of good jobs',
        'Q27': 'Sense of purpose'
    }
    
    outlook_map = {
        'Profoundly Worse': -2,
        'Noticeably Worse': -1,
        'No Major Change': 0,
        'Noticeably Better': 1,
        'Profoundly Better': 2
    }
    
    summary_stats = []
    
    for q_num, description in outlook_questions.items():
        if q_num in df.columns:
            print(f"\n{q_num}: {description}")
            
            # Get distribution
            dist = df[q_num].value_counts(normalize=True) * 100
            
            # Order by optimism level
            ordered_responses = ['Profoundly Worse', 'Noticeably Worse', 'No Major Change', 
                               'Noticeably Better', 'Profoundly Better']
            
            for response in ordered_responses:
                if response in dist.index:
                    print(f"  {response}: {dist[response]:.1f}%")
            
            # Calculate mean outlook score
            valid_data = df[df[q_num].notna()].copy()
            valid_data[f'{q_num}_score'] = valid_data[q_num].map(outlook_map)
            mean_score = valid_data[f'{q_num}_score'].mean()
            
            # Calculate net optimism (% better - % worse)
            pct_better = df[q_num].isin(['Noticeably Better', 'Profoundly Better']).mean() * 100
            pct_worse = df[q_num].isin(['Noticeably Worse', 'Profoundly Worse']).mean() * 100
            net_optimism = pct_better - pct_worse
            
            print(f"  Mean score: {mean_score:.2f} (-2=worst, +2=best)")
            print(f"  Net optimism: {net_optimism:.1f}% (better - worse)")
            
            summary_stats.append({
                'Area': description,
                'Mean Score': mean_score,
                'Net Optimism': net_optimism
            })
    
    # Summary comparison
    print("\n" + "-"*60)
    print("Summary: Future Outlook Comparison")
    print("-"*60)
    summary_df = pd.DataFrame(summary_stats)
    summary_df = summary_df.sort_values('Net Optimism', ascending=False)
    print(summary_df.to_string(index=False))

analyze_future_outlook(df)

# ============================================================================
# ANALYSIS 2.3: OPTIMISM VS. PESSIMISM CORRELATION
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 2.3: HEADLINE - OPTIMISM VS. PESSIMISM CORRELATION")
print("="*80)

def analyze_optimism_correlation(df):
    print("\nCorrelation between general AI sentiment (Q5) and future predictions")
    
    if 'Q5' not in df.columns:
        print("Q5 not found in data")
        return
    
    # Map future outlook to numeric
    outlook_map = {
        'Profoundly Worse': -2,
        'Noticeably Worse': -1,
        'No Major Change': 0,
        'Noticeably Better': 1,
        'Profoundly Better': 2
    }
    
    future_questions = ['Q23', 'Q24', 'Q25', 'Q26', 'Q27']
    
    # Focus on key comparison: excited vs concerned
    excited = df[df['Q5'] == 'More excited than concerned']
    concerned = df[df['Q5'] == 'More concerned than excited']
    
    print(f"\nSample sizes:")
    print(f"  More excited than concerned: n={len(excited)}")
    print(f"  More concerned than excited: n={len(concerned)}")
    
    for q_num in future_questions:
        if q_num in df.columns:
            q_label = {'Q23': 'Cost of living', 'Q24': 'Free time', 
                      'Q25': 'Community well-being', 'Q26': 'Jobs', 
                      'Q27': 'Purpose'}[q_num]
            
            print(f"\n{q_num}: {q_label}")
            
            # Calculate % expecting improvement for each group
            excited_better = excited[q_num].isin(['Noticeably Better', 'Profoundly Better']).mean() * 100
            concerned_better = concerned[q_num].isin(['Noticeably Better', 'Profoundly Better']).mean() * 100
            
            excited_worse = excited[q_num].isin(['Noticeably Worse', 'Profoundly Worse']).mean() * 100
            concerned_worse = concerned[q_num].isin(['Noticeably Worse', 'Profoundly Worse']).mean() * 100
            
            print(f"  'More excited' group: {excited_better:.1f}% expect better, {excited_worse:.1f}% expect worse")
            print(f"  'More concerned' group: {concerned_better:.1f}% expect better, {concerned_worse:.1f}% expect worse")
            
            # Statistical test
            if len(excited) > 0 and len(concerned) > 0:
                # Create numeric scores
                excited_scores = excited[q_num].map(outlook_map)
                concerned_scores = concerned[q_num].map(outlook_map)
                
                # Remove NaN values
                excited_scores = excited_scores.dropna()
                concerned_scores = concerned_scores.dropna()
                
                if len(excited_scores) > 0 and len(concerned_scores) > 0:
                    t_stat, p_value = stats.ttest_ind(excited_scores, concerned_scores)
                    print(f"  Difference is {'significant' if p_value < 0.05 else 'not significant'} (p={p_value:.4f})")

analyze_optimism_correlation(df)

# ============================================================================
# ANALYSIS 2.4: TRUST AND USAGE
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 2.4: TRUST AND USAGE CORRELATION")
print("="*80)

def analyze_trust_usage(df):
    print("\nCorrelation: Trust in AI chatbots (Q17) vs Use for sensitive issues (Q21)")
    
    if 'Q17' not in df.columns or 'Q21' not in df.columns:
        print("Required questions not found")
        return
    
    # Filter to those who answered both
    both_answered = df[df['Q17'].notna() & df['Q21'].notna()].copy()
    print(f"Sample size: n={len(both_answered)}")
    
    # Convert to numeric scales
    trust_map = {
        'Strongly Distrust': 1,
        'Somewhat Distrust': 2,
        'Neither Trust Nor Distrust': 3,
        'Somewhat Trust': 4,
        'Strongly Trust': 5
    }
    
    freq_map = {'never': 0, 'annually': 1, 'monthly': 2, 'weekly': 3, 'daily': 4}
    
    both_answered['trust_score'] = both_answered['Q17'].map(trust_map)
    both_answered['sensitive_freq'] = both_answered['Q21'].map(freq_map)
    
    # Calculate correlation
    correlation = both_answered['trust_score'].corr(both_answered['sensitive_freq'])
    print(f"\nPearson correlation: {correlation:.3f}")
    
    # Spearman rank correlation (more appropriate for ordinal data)
    spearman_corr = both_answered['trust_score'].corr(both_answered['sensitive_freq'], method='spearman')
    print(f"Spearman correlation: {spearman_corr:.3f}")
    
    # Detailed breakdown by trust level
    print("\n" + "-"*60)
    print("Frequency of AI use for sensitive issues by trust level:")
    print("-"*60)
    
    trust_levels = ['Strongly Trust', 'Somewhat Trust', 'Neither Trust Nor Distrust',
                   'Somewhat Distrust', 'Strongly Distrust']
    
    for trust_level in trust_levels:
        subset = both_answered[both_answered['Q17'] == trust_level]
        if len(subset) > 0:
            print(f"\n{trust_level} (n={len(subset)}):")
            
            # Get frequency distribution
            freq_dist = subset['Q21'].value_counts(normalize=True) * 100
            
            # Report key frequencies
            daily_pct = freq_dist.get('daily', 0)
            weekly_pct = freq_dist.get('weekly', 0)
            monthly_pct = freq_dist.get('monthly', 0)
            never_pct = freq_dist.get('never', 0)
            
            print(f"  Daily: {daily_pct:.1f}%")
            print(f"  Weekly: {weekly_pct:.1f}%")
            print(f"  Monthly: {monthly_pct:.1f}%")
            print(f"  Never: {never_pct:.1f}%")
            print(f"  Regular use (daily/weekly): {daily_pct + weekly_pct:.1f}%")
    
    # Statistical test
    # Test if high trust (4-5) correlates with frequent use (3-4)
    high_trust = both_answered['trust_score'] >= 4
    frequent_use = both_answered['sensitive_freq'] >= 3
    
    chi2, p_value = stats.chi2_contingency(pd.crosstab(high_trust, frequent_use))[:2]
    print(f"\n" + "-"*60)
    print(f"Chi-square test (high trust vs frequent sensitive use): p={p_value:.4f}")
    print(f"Result: {'Significant' if p_value < 0.05 else 'Not significant'} relationship")

analyze_trust_usage(df)

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 2 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")