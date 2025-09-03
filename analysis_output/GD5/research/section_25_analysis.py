#!/usr/bin/env python3
"""
Section 25: The Survey as an Intervention — Measuring Opinion Shifts
Comparing Q31/Q32 (initial) with Q93/Q94 (final) to detect belief changes
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Connect to database
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("=" * 80)
print("SECTION 25: THE SURVEY AS AN INTERVENTION — MEASURING OPINION SHIFTS")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get participant responses with reliable PRI scores
query = """
SELECT pr.*, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
df = pd.read_sql_query(query, conn)
print(f"\nTotal reliable participants: {len(df)}")

# Check which columns exist for the questions
print("\nChecking for relevant columns...")
relevant_cols = ['Q31', 'Q32', 'Q93', 'Q94', 'Q44', 'Q45']
for col in relevant_cols:
    if col in df.columns:
        non_null = df[col].notna().sum()
        print(f"  {col}: {non_null} non-null responses")
    else:
        print(f"  {col}: NOT FOUND")

print("\n" + "=" * 80)
print("Question 25.1: Belief Change Measurement")
print("=" * 80)

# Compare Q31 (initial) with Q93 (final) - human-nature relationship
# Compare Q32 (initial) with Q94 (final) - human superiority

# Q31 vs Q93: Human-nature relationship
if 'Q31' in df.columns and 'Q93' in df.columns:
    print("\n**Human-Nature Relationship (Q31 → Q93):**")
    
    # Create comparison dataframe
    comparison_31_93 = df[['participant_id', 'Q31', 'Q93']].dropna()
    
    # Check for changes
    comparison_31_93['changed'] = comparison_31_93['Q31'] != comparison_31_93['Q93']
    
    total_valid = len(comparison_31_93)
    changed_count = comparison_31_93['changed'].sum()
    changed_pct = (changed_count / total_valid * 100) if total_valid > 0 else 0
    
    print(f"Total participants with both responses: {total_valid}")
    print(f"Changed their answer: {changed_count} ({changed_pct:.1f}%)")
    
    if changed_count > 0:
        # Analyze direction of change
        print("\nDirection of changes:")
        change_patterns = comparison_31_93[comparison_31_93['changed']].groupby(['Q31', 'Q93']).size()
        for (initial, final), count in change_patterns.items():
            pct_of_changes = (count / changed_count * 100)
            print(f"  {initial[:50]} → {final[:50]}: {count} ({pct_of_changes:.1f}%)")

# Q32 vs Q94: Human superiority/equality
if 'Q32' in df.columns and 'Q94' in df.columns:
    print("\n**Human Superiority/Equality (Q32 → Q94):**")
    
    # Create comparison dataframe
    comparison_32_94 = df[['participant_id', 'Q32', 'Q94']].dropna()
    
    # Check for changes
    comparison_32_94['changed'] = comparison_32_94['Q32'] != comparison_32_94['Q94']
    
    total_valid = len(comparison_32_94)
    changed_count = comparison_32_94['changed'].sum()
    changed_pct = (changed_count / total_valid * 100) if total_valid > 0 else 0
    
    print(f"Total participants with both responses: {total_valid}")
    print(f"Changed their answer: {changed_count} ({changed_pct:.1f}%)")
    
    if changed_count > 0:
        # Analyze direction of change
        print("\nDirection of changes:")
        
        # Categorize beliefs
        def categorize_belief(response):
            if pd.isna(response):
                return 'Unknown'
            response_lower = str(response).lower()
            if 'superior' in response_lower and 'different' in response_lower:
                return 'Superior'
            elif 'equal' in response_lower:
                return 'Equal'
            elif 'inferior' in response_lower:
                return 'Inferior'
            else:
                return 'Other'
        
        comparison_32_94['initial_category'] = comparison_32_94['Q32'].apply(categorize_belief)
        comparison_32_94['final_category'] = comparison_32_94['Q94'].apply(categorize_belief)
        
        # Show category changes
        category_changes = comparison_32_94[comparison_32_94['changed']].groupby(['initial_category', 'final_category']).size()
        print("\nCategory shifts:")
        for (initial, final), count in category_changes.items():
            pct_of_changes = (count / changed_count * 100)
            print(f"  {initial} → {final}: {count} ({pct_of_changes:.1f}%)")
        
        # Store for later analysis
        changers_32_94 = comparison_32_94[comparison_32_94['changed']]['participant_id'].tolist()

print("\n" + "=" * 80)
print("Question 25.2: Emotional Response and Mind Change")
print("=" * 80)

# Among those who changed their minds, analyze Q44 (impact) and Q45 (emotions)
if 'Q32' in df.columns and 'Q94' in df.columns and 'Q44' in df.columns and 'Q45' in df.columns:
    
    # Get mind changers
    changers_df = df[df['participant_id'].isin(changers_32_94)]
    non_changers_df = df[~df['participant_id'].isin(changers_32_94)]
    
    print(f"\nAnalyzing {len(changers_df)} mind-changers vs {len(non_changers_df)} non-changers")
    
    # Q44: Impact of scientific facts
    print("\n**Impact of Scientific Facts (Q44):**")
    
    if 'Q44' in changers_df.columns:
        # Changers
        changers_impact = changers_df['Q44'].value_counts(normalize=True) * 100
        print("\nMind-changers:")
        for impact, pct in changers_impact.items():
            print(f"  {impact}: {pct:.1f}%")
        
        # Non-changers
        non_changers_impact = non_changers_df['Q44'].value_counts(normalize=True) * 100
        print("\nNon-changers:")
        for impact, pct in non_changers_impact.items():
            print(f"  {impact}: {pct:.1f}%")
        
        # Statistical test
        # Convert to numeric for comparison
        impact_map = {
            'Not at all': 1,
            'A little': 2,
            'Somewhat': 3,
            'A moderate amount': 4,
            'A great deal': 5
        }
        
        changers_numeric = changers_df['Q44'].map(impact_map).dropna()
        non_changers_numeric = non_changers_df['Q44'].map(impact_map).dropna()
        
        if len(changers_numeric) > 0 and len(non_changers_numeric) > 0:
            t_stat, p_value = stats.ttest_ind(changers_numeric, non_changers_numeric)
            print(f"\nt-test: t={t_stat:.2f}, p={p_value:.4f}")
            if p_value < 0.05:
                print("Significant difference in impact between changers and non-changers")
    
    # Q45: Emotional response
    print("\n**Emotional Response (Q45):**")
    
    if 'Q45' in changers_df.columns:
        # Note: Q45 might be multi-select, need to handle accordingly
        print("\nMind-changers' emotions:")
        changers_emotions = changers_df['Q45'].dropna()
        
        # Count emotions (handling potential multi-select)
        emotion_counts = {}
        for response in changers_emotions:
            if isinstance(response, str):
                # Check for common emotions
                emotions = ['Curious', 'Connected', 'Protective', 'Hopeful', 'Unsettled', 
                           'Skeptical', 'Concerned', 'Excited', 'Overwhelmed']
                for emotion in emotions:
                    if emotion.lower() in response.lower():
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Calculate percentages
        total_changers = len(changers_emotions)
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_changers * 100) if total_changers > 0 else 0
            print(f"  {emotion}: {count} ({pct:.1f}%)")
        
        # Compare with non-changers
        print("\nNon-changers' emotions:")
        non_changers_emotions = non_changers_df['Q45'].dropna()
        
        emotion_counts_nc = {}
        for response in non_changers_emotions:
            if isinstance(response, str):
                for emotion in emotions:
                    if emotion.lower() in response.lower():
                        emotion_counts_nc[emotion] = emotion_counts_nc.get(emotion, 0) + 1
        
        total_non_changers = len(non_changers_emotions)
        for emotion, count in sorted(emotion_counts_nc.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_non_changers * 100) if total_non_changers > 0 else 0
            print(f"  {emotion}: {count} ({pct:.1f}%)")

# Overall summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if 'Q32' in df.columns and 'Q94' in df.columns:
    print(f"\n**Finding:** {changed_pct:.1f}% of participants changed their human-animal equality beliefs during the survey")
    
    if 'Q44' in df.columns:
        # Check if high impact correlates with change
        high_impact_changers = changers_df[changers_df['Q44'] == 'A great deal']['participant_id'].count()
        high_impact_non_changers = non_changers_df[non_changers_df['Q44'] == 'A great deal']['participant_id'].count()
        
        if len(changers_df) > 0:
            high_impact_rate_changers = (high_impact_changers / len(changers_df) * 100)
            high_impact_rate_non_changers = (high_impact_non_changers / len(non_changers_df) * 100)
            
            print(f"'Great deal' of impact: {high_impact_rate_changers:.1f}% of changers vs {high_impact_rate_non_changers:.1f}% of non-changers")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)