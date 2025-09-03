#!/usr/bin/env python3
"""
Section 5: Ethics, Rights, and Governance
This analysis explores ethical and societal shifts from AI-mediated interspecies communication
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from collections import Counter

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

# Helper function for multi-select questions
def parse_multiselect(response_str):
    """Parse multi-select responses"""
    if pd.isna(response_str):
        return []
    # Split by common delimiters
    items = str(response_str).split(',') if ',' in str(response_str) else [str(response_str)]
    return [item.strip() for item in items if item.strip()]

# ============================================================================
# ANALYSIS 5.1: Preferred Future for Animal Protection
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.1: PREFERRED FUTURE FOR ANIMAL PROTECTION")
print("="*80)

def analyze_preferred_future(df):
    print("\nDistribution of preferred approaches (Q70):")
    
    # Get Q70 distribution
    q70_dist = df['Q70'].value_counts()
    q70_pct = df['Q70'].value_counts(normalize=True) * 100
    
    for approach, count in q70_dist.items():
        if pd.notna(approach):
            pct = q70_pct[approach]
            print(f"\n{approach[:50]}...")
            print(f"  Count: {count} ({pct:.1f}%)")
    
    # Correlate with human-animal equality belief (Q94, which is Q32 repeated)
    print("\n" + "-"*60)
    print("Correlation with human-animal equality beliefs (Q94):")
    
    # Create crosstab
    crosstab = pd.crosstab(df['Q94'], df['Q70'], normalize='index') * 100
    
    # Focus on key relationships
    if 'Humans are fundamentally equal to other animals' in crosstab.index:
        equal_row = crosstab.loc['Humans are fundamentally equal to other animals']
        print("\nAmong those believing in equality:")
        for approach in equal_row.index:
            if pd.notna(approach):
                print(f"  {approach[:40]}...: {equal_row[approach]:.1f}%")
    
    if 'Humans are fundamentally superior to other animals' in crosstab.index:
        superior_row = crosstab.loc['Humans are fundamentally superior to other animals']
        print("\nAmong those believing in superiority:")
        for approach in superior_row.index:
            if pd.notna(approach):
                print(f"  {approach[:40]}...: {superior_row[approach]:.1f}%")
    
    # Statistical test
    chi2, p_value, dof, expected = stats.chi2_contingency(pd.crosstab(df['Q94'], df['Q70']))
    print(f"\nChi-square test: χ²={chi2:.2f}, p={p_value:.4f}")

analyze_preferred_future(df)

# ============================================================================
# ANALYSIS 5.2: Animal Representation
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.2: ANIMAL REPRESENTATION")
print("="*80)

def analyze_representation(df):
    # Q73: Should animals have legal representatives?
    print("\nQ73: Should animals have the right to a legal representative?")
    q73_dist = df['Q73'].value_counts(normalize=True) * 100
    for response, pct in q73_dist.items():
        if pd.notna(response):
            print(f"  {response}: {pct:.1f}%")
    
    # Q74: How should they be represented?
    print("\nQ74: How should animals be represented?")
    q74_dist = df['Q74'].value_counts(normalize=True) * 100
    for response, pct in q74_dist.items():
        if pd.notna(response):
            print(f"  {response[:50]}...: {pct:.1f}%")
    
    # Among those who support representation
    support_rep = df[df['Q73'] == 'Yes']
    if len(support_rep) > 0:
        print(f"\nAmong those supporting legal representation (n={len(support_rep)}):")
        rep_method = support_rep['Q74'].value_counts(normalize=True) * 100
        for method, pct in rep_method.items():
            if pd.notna(method):
                print(f"  {method[:50]}...: {pct:.1f}%")

analyze_representation(df)

# ============================================================================
# ANALYSIS 5.3: Who Should Represent Animals?
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.3: WHO SHOULD REPRESENT ANIMALS?")
print("="*80)

def analyze_who_represents(df):
    print("\nQ75 equivalent (unmapped columns): Who should represent animals?")
    
    # Q75 was multi-select, stored in unmapped_93 to unmapped_101
    representatives = {
        'unmapped_93': 'Scientists who study animals',
        'unmapped_94': 'Local community/traditional/indigenous wisdom holder',
        'unmapped_95': 'Democratically elected representative',
        'unmapped_96': 'Animals themselves/animal ambassador',
        'unmapped_97': 'Technologies, including AI',
        'unmapped_98': 'Animal protection organizations',
        'unmapped_99': 'Your national government',
        'unmapped_100': 'Non-profit institution',
        'unmapped_101': 'Anyone with training and mandate'
    }
    
    # Count selections
    selection_counts = {}
    for col, label in representatives.items():
        if col in df.columns:
            # Count non-null, non-dash responses
            count = df[col].notna().sum() - (df[col] == '--').sum()
            selection_counts[label] = count
    
    # Sort by frequency
    sorted_reps = sorted(selection_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\nMost frequently chosen representatives:")
    for i, (rep, count) in enumerate(sorted_reps[:3], 1):
        pct = (count / len(df)) * 100
        print(f"  {i}. {rep}: {count} selections ({pct:.1f}%)")
    
    print("\nAll representatives ranked by selection frequency:")
    for rep, count in sorted_reps:
        pct = (count / len(df)) * 100
        print(f"  {rep}: {pct:.1f}%")

analyze_who_represents(df)

# ============================================================================
# ANALYSIS 5.4: Animal Participation in Democracy
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.4: ANIMAL PARTICIPATION IN DEMOCRACY")
print("="*80)

def analyze_democratic_participation(df):
    print("\nQ77: Should animals participate in democratic processes?")
    
    q77_dist = df['Q77'].value_counts()
    for response, count in q77_dist.items():
        if pd.notna(response):
            pct = (count / len(df)) * 100
            print(f"\n{response[:60]}...")
            print(f"  Count: {count} ({pct:.1f}%)")
    
    # Correlation with belief in animal culture (Q41)
    print("\n" + "-"*60)
    print("Support by belief in animal culture (Q41):")
    
    # Define supportive positions
    supportive_positions = [
        'Yes, they should be able to vote through human proxies or guardians.',
        'Yes, they should be able to vote, but only on laws or decisions that directly affect them.',
        'Yes, they should have a voice, but their vote should not be binding.',
        'Yes, they should be recognized as a formal political constituency with dedicated representatives in government.'
    ]
    
    # Group by culture belief
    culture_groups = df.groupby('Q41')
    for culture_belief, group in culture_groups:
        if pd.notna(culture_belief) and len(group) > 10:  # Only show groups with sufficient size
            support_count = group['Q77'].isin(supportive_positions).sum()
            support_pct = (support_count / len(group)) * 100
            print(f"\n{culture_belief} (n={len(group)}):")
            print(f"  Support any form of participation: {support_pct:.1f}%")
    
    # Statistical test
    df['supports_democracy'] = df['Q77'].isin(supportive_positions)
    df['strong_culture_belief'] = df['Q41'] == 'Strongly believe'
    
    contingency = pd.crosstab(df['strong_culture_belief'], df['supports_democracy'])
    chi2, p_value = stats.chi2_contingency(contingency)[:2]
    print(f"\nChi-square (culture belief vs democratic support): p={p_value:.4f}")

analyze_democratic_participation(df)

# ============================================================================
# ANALYSIS 5.5: Regulating Communication
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.5: REGULATING COMMUNICATION")
print("="*80)

def analyze_regulation(df):
    # Q82: Restrict to professionals
    print("\nQ82: Communication should be restricted to authorized professionals")
    q82_dist = df['Q82'].value_counts(normalize=True) * 100
    for response, pct in q82_dist.items():
        if pd.notna(response):
            print(f"  {response}: {pct:.1f}%")
    
    agree_82 = df['Q82'].isin(['Strongly agree', 'Somewhat agree']).mean() * 100
    print(f"Total agreement: {agree_82:.1f}%")
    
    # Q83: Everyone should be allowed to listen
    print("\nQ83: Everyone should be allowed to listen to animals")
    q83_dist = df['Q83'].value_counts(normalize=True) * 100
    for response, pct in q83_dist.items():
        if pd.notna(response):
            print(f"  {response}: {pct:.1f}%")
    
    agree_83 = df['Q83'].isin(['Strongly agree', 'Somewhat agree']).mean() * 100
    print(f"Total agreement: {agree_83:.1f}%")
    
    # Q85: Types of communication to prohibit
    print("\n" + "-"*60)
    print("Q85: Types of communication to prohibit")
    
    # Parse multi-select responses
    all_prohibitions = []
    for response in df['Q85']:
        if pd.notna(response) and response != '--':
            prohibitions = parse_multiselect(response)
            all_prohibitions.extend(prohibitions)
    
    # Count frequencies
    prohibition_counts = Counter(all_prohibitions)
    
    print("\nMost wanted prohibitions:")
    for prohibition, count in prohibition_counts.most_common(5):
        pct = (count / len(df)) * 100
        print(f"  {prohibition[:50]}...: {pct:.1f}%")

analyze_regulation(df)

# ============================================================================
# ANALYSIS 5.6: Ownership of Animal Creations
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.6: OWNERSHIP OF ANIMAL CREATIONS")
print("="*80)

def analyze_ownership(df):
    print("\nQ90: Who should own animal creations (e.g., selfies, songs)?")
    
    q90_dist = df['Q90'].value_counts()
    q90_pct = df['Q90'].value_counts(normalize=True) * 100
    
    for owner, count in q90_dist.items():
        if pd.notna(owner) and owner != '--':
            pct = q90_pct[owner]
            print(f"\n{owner[:60]}...")
            print(f"  Count: {count} ({pct:.1f}%)")
    
    # Find most popular view
    if len(q90_dist) > 0:
        most_popular = q90_dist.index[0]
        print(f"\nMost popular view: {most_popular[:60]}...")

analyze_ownership(df)

# ============================================================================
# ANALYSIS 5.7: Should Animals Be Able to Earn Money?
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 5.7: HEADLINE - SHOULD ANIMALS BE ABLE TO EARN MONEY?")
print("="*80)

def analyze_economic_rights(df):
    print("\nQ91: Economic rights for non-humans")
    
    # Parse multi-select responses
    economic_rights = {
        'earn money': 0,
        'own property': 0,
        'own things they make': 0,
        'sell things to humans': 0,
        'any economic right': 0,
        'none': 0
    }
    
    for response in df['Q91']:
        if pd.notna(response):
            response_lower = str(response).lower()
            if 'earn money' in response_lower:
                economic_rights['earn money'] += 1
            if 'own property' in response_lower:
                economic_rights['own property'] += 1
            if 'own things they make' in response_lower:
                economic_rights['own things they make'] += 1
            if 'sell things' in response_lower:
                economic_rights['sell things to humans'] += 1
            if 'none of the above' in response_lower:
                economic_rights['none'] += 1
            elif response != '--':  # Any response other than none
                economic_rights['any economic right'] += 1
    
    print("\nSupport for economic rights:")
    for right, count in economic_rights.items():
        pct = (count / len(df)) * 100
        print(f"  {right}: {pct:.1f}%")
    
    # Age comparison
    print("\n" + "-"*60)
    print("Support by age group (Q2):")
    
    # Create age groups
    young = df[df['Q2'] == '18-25']
    older = df[df['Q2'].isin(['56-65', '65+'])]
    
    # Count support in each group
    def count_economic_support(group_df):
        count = 0
        for response in group_df['Q91']:
            if pd.notna(response) and response != '--':
                response_lower = str(response).lower()
                if ('earn money' in response_lower or 
                    'own property' in response_lower or 
                    'sell things' in response_lower) and \
                   'none of the above' not in response_lower:
                    count += 1
        return count
    
    if len(young) > 0:
        young_support = count_economic_support(young)
        young_pct = (young_support / len(young)) * 100
        print(f"\n18-25 years old (n={len(young)}):")
        print(f"  Support economic rights: {young_pct:.1f}%")
    
    if len(older) > 0:
        older_support = count_economic_support(older)
        older_pct = (older_support / len(older)) * 100
        print(f"\n56+ years old (n={len(older)}):")
        print(f"  Support economic rights: {older_pct:.1f}%")
    
    # Statistical test
    if len(young) > 0 and len(older) > 0:
        # Create binary variables
        young['supports_economic'] = young.apply(
            lambda x: 1 if pd.notna(x['Q91']) and 'none' not in str(x['Q91']).lower() 
            and x['Q91'] != '--' else 0, axis=1
        )
        older['supports_economic'] = older.apply(
            lambda x: 1 if pd.notna(x['Q91']) and 'none' not in str(x['Q91']).lower() 
            and x['Q91'] != '--' else 0, axis=1
        )
        
        # Chi-square test
        young_yes = young['supports_economic'].sum()
        young_no = len(young) - young_yes
        older_yes = older['supports_economic'].sum()
        older_no = len(older) - older_yes
        
        contingency = np.array([[young_yes, young_no], [older_yes, older_no]])
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
        
        print(f"\nAge difference significance: p={p_value:.4f}")
        print(f"Result: {'Significant' if p_value < 0.05 else 'Not significant'} difference")

analyze_economic_rights(df)

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 5 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")