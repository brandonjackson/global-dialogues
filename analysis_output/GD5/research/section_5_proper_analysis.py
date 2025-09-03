#!/usr/bin/env python3
"""
Section 5: Ethics, Rights, and Governance - Complete Analysis
Using the participant_responses table for poll data
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter

# Connect to database in read-only mode
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("=" * 80)
print("SECTION 5: ETHICS, RIGHTS, AND GOVERNANCE")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get reliable participants from participant_responses table
query = """
SELECT pr.*, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
df = pd.read_sql_query(query, conn)
print(f"\nTotal reliable participants (PRI >= 0.3): {len(df)}")

# Helper function for value counts with percentages
def analyze_column(df, col_name, question_text):
    if col_name not in df.columns:
        return None
    
    # Remove NaN values
    valid_data = df[col_name].dropna()
    if len(valid_data) == 0:
        return None
    
    value_counts = valid_data.value_counts()
    percentages = (value_counts / len(valid_data) * 100).round(2)
    
    result = pd.DataFrame({
        'response': value_counts.index,
        'count': value_counts.values,
        'percentage': percentages.values
    })
    
    return result

print("\n" + "=" * 80)
print("Question 5.1: PREFERRED FUTURE FOR ANIMAL PROTECTION (Q70)")
print("=" * 80)

q70_results = analyze_column(df, 'Q70', 'Which approach feels most appropriate to you for protecting animals?')
if q70_results is not None:
    print("\n**Finding:**")
    top_approach = q70_results.iloc[0]
    print(f"{top_approach['response']} is preferred by {top_approach['percentage']}% of respondents")
    print("\n**Method:** Analysis of Q70 responses in participant_responses table")
    print("\n**Details:**")
    for idx, row in q70_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")
    
    # Check correlation with Q33 (human superiority)
    if 'Q33' in df.columns:
        cross_tab = pd.crosstab(df['Q70'], df['Q33'], normalize='columns') * 100
        print("\n**Correlation with Human-Animal Views (Q33):**")
        print(cross_tab.round(1))

print("\n" + "=" * 80)
print("Question 5.2: ANIMAL REPRESENTATION (Q73, Q74)")
print("=" * 80)

# Q73: Should animals have legal representatives?
q73_results = analyze_column(df, 'Q73', 'Should animals have the right to a representative?')
if q73_results is not None:
    print("\n**Finding:**")
    yes_pct = q73_results[q73_results['response'] == 'Yes']['percentage'].values
    if len(yes_pct) > 0:
        print(f"{yes_pct[0]}% believe animals should have the right to legal representation")
    print("\n**Method:** Analysis of Q73 responses")
    print("\n**Details:**")
    for idx, row in q73_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")

# Q74: How should they be represented?
q74_results = analyze_column(df, 'Q74', 'How should animals be represented in decision-making?')
if q74_results is not None:
    print("\n**Representation Method Preferences (Q74):**")
    for idx, row in q74_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")

print("\n" + "=" * 80)
print("Question 5.3: WHO SHOULD REPRESENT ANIMALS (Q75)")
print("=" * 80)

# Q75 appears to be stored in unmapped columns - check which ones
# Since it's a multi-select, it might be in columns like unmapped_93, unmapped_94, etc.
print("\n**Note:** Q75 is a multi-select question. Checking unmapped columns...")

# Let's check unmapped columns that might contain Q75 data
possible_q75_cols = [col for col in df.columns if 'unmapped_9' in col and col.replace('unmapped_', '').replace('_agree_pct', '').isdigit()]
for col in possible_q75_cols[:10]:  # Check first 10
    if df[col].notna().sum() > 0:
        sample_values = df[col].dropna().head(3).tolist()
        if any('Scientists' in str(v) or 'organizations' in str(v) or 'AI' in str(v) for v in sample_values):
            print(f"Found Q75 data in {col}")
            q75_results = analyze_column(df, col, 'Who should represent animals?')
            if q75_results is not None:
                print("\n**Finding:**")
                top_3 = q75_results.head(3)['response'].tolist()
                print(f"Top 3 choices: {', '.join(str(x) for x in top_3)}")
                print("\n**Details:**")
                for idx, row in q75_results.head(5).iterrows():
                    print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")
            break

print("\n" + "=" * 80)
print("Question 5.4: ANIMAL PARTICIPATION IN DEMOCRACY (Q77)")
print("=" * 80)

q77_results = analyze_column(df, 'Q77', 'Should animals participate in democratic processes?')
if q77_results is not None:
    print("\n**Finding:**")
    yes_responses = q77_results[q77_results['response'].str.contains('Yes', na=False)]
    if not yes_responses.empty:
        total_yes = yes_responses['percentage'].sum()
        print(f"{total_yes:.1f}% support some form of animal participation in democratic processes")
    print("\n**Method:** Analysis of Q77 responses")
    print("\n**Details:**")
    for idx, row in q77_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")
    
    # Correlation with belief in animal culture (Q41)
    if 'Q41' in df.columns:
        culture_democracy = pd.crosstab(df['Q77'], df['Q41'], normalize='columns') * 100
        print("\n**Correlation with Belief in Animal Culture (Q41):**")
        # Show percentage supporting democracy among those who strongly believe in culture
        strongly_believe = culture_democracy.columns[culture_democracy.columns.str.contains('Strongly', na=False)]
        if len(strongly_believe) > 0:
            yes_among_believers = culture_democracy.loc[
                culture_democracy.index.str.contains('Yes', na=False), 
                strongly_believe[0]
            ].sum()
            print(f"Among those who strongly believe animals have culture: {yes_among_believers:.1f}% support democratic participation")

print("\n" + "=" * 80)
print("Question 5.5: REGULATING COMMUNICATION (Q82, Q83, Q85)")
print("=" * 80)

# Q82: Restrict to authorized professionals
q82_results = analyze_column(df, 'Q82', 'Should communication be restricted to professionals?')
if q82_results is not None:
    print("\n**Professional Restriction (Q82):**")
    agree_responses = q82_results[q82_results['response'].str.contains('agree', case=False, na=False)]
    if not agree_responses.empty:
        total_agree = agree_responses['percentage'].sum()
        print(f"{total_agree:.1f}% support restricting to professionals")
    for idx, row in q82_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")

# Q83: Everyone allowed to listen
q83_results = analyze_column(df, 'Q83', 'Should everyone be allowed to listen?')
if q83_results is not None:
    print("\n**Open Listening (Q83):**")
    agree_responses = q83_results[q83_results['response'].str.contains('agree', case=False, na=False)]
    if not agree_responses.empty:
        total_agree = agree_responses['percentage'].sum()
        print(f"{total_agree:.1f}% support open listening with restricted responding")
    for idx, row in q83_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")

# Q85: Types to prohibit (multi-select)
if 'Q85' in df.columns:
    print("\n**Types of Communication to Prohibit (Q85):**")
    q85_data = df['Q85'].dropna()
    if len(q85_data) > 0:
        # This is likely a multi-select stored as a string
        all_selections = []
        for response in q85_data:
            if isinstance(response, str):
                # Split by common delimiters
                selections = [s.strip() for s in response.split(',')]
                all_selections.extend(selections)
        
        if all_selections:
            selection_counts = Counter(all_selections)
            total_respondents = len(q85_data)
            print("Top prohibited communication types:")
            for item, count in selection_counts.most_common(5):
                pct = (count / total_respondents * 100)
                print(f"- {item[:60]}...: {count} ({pct:.1f}%)")

print("\n" + "=" * 80)
print("Question 5.6: OWNERSHIP OF ANIMAL CREATIONS (Q90)")
print("=" * 80)

q90_results = analyze_column(df, 'Q90', 'Who should own animal recordings?')
if q90_results is not None:
    print("\n**Finding:**")
    top_owner = q90_results.iloc[0]
    print(f"Most popular ownership view: {top_owner['response']} ({top_owner['percentage']}%)")
    print("\n**Method:** Analysis of Q90 responses")
    print("\n**Details:**")
    for idx, row in q90_results.iterrows():
        print(f"- {row['response']}: {int(row['count'])} ({row['percentage']}%)")

print("\n" + "=" * 80)
print("Question 5.7: SHOULD ANIMALS BE ABLE TO EARN MONEY? (Q91)")
print("=" * 80)

# Q91 is a multi-select question
if 'Q91' in df.columns:
    print("\n**Economic Rights for Non-Humans (Q91):**")
    q91_data = df['Q91'].dropna()
    if len(q91_data) > 0:
        all_selections = []
        for response in q91_data:
            if isinstance(response, str):
                selections = [s.strip() for s in response.split(',')]
                all_selections.extend(selections)
        
        if all_selections:
            selection_counts = Counter(all_selections)
            total_respondents = len(q91_data)
            
            print("\n**Finding:**")
            earn_money = selection_counts.get('Earn money', 0)
            own_property = selection_counts.get('Own property', 0)
            none_above = selection_counts.get('None of the above', 0)
            
            print(f"{earn_money/total_respondents*100:.1f}% support animals earning money")
            print(f"{own_property/total_respondents*100:.1f}% support animals owning property")
            print(f"{none_above/total_respondents*100:.1f}% oppose all economic rights")
            
            print("\n**Method:** Analysis of Q91 multi-select responses")
            print("\n**Details:**")
            for item, count in selection_counts.most_common():
                pct = (count / total_respondents * 100)
                print(f"- {item}: {count} ({pct:.1f}%)")
            
            # Age analysis
            if 'Q2' in df.columns:
                print("\n**Age Group Analysis:**")
                age_groups = df.groupby('Q2')
                for age, group in age_groups:
                    if age in ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']:
                        age_q91 = group['Q91'].dropna()
                        if len(age_q91) > 0:
                            age_earn = sum('Earn money' in str(r) for r in age_q91)
                            print(f"{age}: {age_earn}/{len(age_q91)} ({age_earn/len(age_q91)*100:.1f}%) support earning money")

print("\n" + "=" * 80)
print("CROSS-CUTTING ANALYSIS")
print("=" * 80)

# Consistency between human superiority views (Q33) and economic rights (Q91)
if 'Q33' in df.columns and 'Q91' in df.columns:
    print("\n**Consistency between Human Views and Economic Rights:**")
    
    # Create binary indicators
    df['supports_economic'] = df['Q91'].apply(lambda x: 'None of the above' not in str(x) if pd.notna(x) else False)
    df['believes_equal'] = df['Q33'].apply(lambda x: 'equal' in str(x).lower() if pd.notna(x) else False)
    
    cross_analysis = pd.crosstab(df['believes_equal'], df['supports_economic'], normalize='index') * 100
    print("\nAmong those who believe humans and animals are equal:")
    if True in cross_analysis.index:
        support_pct = cross_analysis.loc[True, True] if True in cross_analysis.columns else 0
        print(f"  {support_pct:.1f}% support economic rights for animals")
    
    print("\nAmong those who believe humans are superior:")
    if False in cross_analysis.index:
        support_pct = cross_analysis.loc[False, True] if True in cross_analysis.columns else 0
        print(f"  {support_pct:.1f}% support economic rights for animals")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)