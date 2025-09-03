#!/usr/bin/env python3
"""
Section 14: Headline-Friendly Insights
This analysis focuses on compelling, headline-worthy findings from the GD5 survey
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
    items = str(response_str).split(',') if ',' in str(response_str) else [str(response_str)]
    return [item.strip() for item in items if item.strip()]

# ============================================================================
# ANALYSIS 14.1: Global Animal Voting Support
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 14.1: GLOBAL ANIMAL VOTING SUPPORT")
print("="*80)

def analyze_voting_support(df):
    print("\nWhat percentage believe animals should vote (Q77)?")
    
    # Define voting support responses
    voting_support = [
        'Yes, they should be able to vote through human proxies or guardians.',
        'Yes, they should be able to vote, but only on laws or decisions that directly affect them.',
        'Yes, they should have a voice, but their vote should not be binding.',
        'Yes, they should be recognized as a formal political constituency with dedicated representatives in government.'
    ]
    
    # Calculate overall support
    supports_voting = df['Q77'].isin(voting_support)
    support_pct = supports_voting.mean() * 100
    
    print(f"\nOverall support for animal voting: {support_pct:.1f}%")
    
    # Break down by type of support
    print("\nBreakdown of support types:")
    for response in voting_support:
        count = (df['Q77'] == response).sum()
        pct = (count / len(df)) * 100
        print(f"  {response[:50]}...: {pct:.1f}%")
    
    # Demographic analysis
    print("\n" + "-"*60)
    print("Support by demographics:")
    
    # By age
    print("\nBy age group (Q2):")
    age_groups = df.groupby('Q2')
    for age, group in age_groups:
        if pd.notna(age) and age != '--' and len(group) > 10:
            age_support = group['Q77'].isin(voting_support).mean() * 100
            print(f"  {age}: {age_support:.1f}% (n={len(group)})")
    
    # By gender
    print("\nBy gender (Q3):")
    gender_groups = df.groupby('Q3')
    for gender, group in gender_groups:
        if pd.notna(gender) and gender != '--' and len(group) > 10:
            gender_support = group['Q77'].isin(voting_support).mean() * 100
            print(f"  {gender}: {gender_support:.1f}% (n={len(group)})")
    
    # By location type
    print("\nBy location (Q4):")
    location_groups = df.groupby('Q4')
    for location, group in location_groups:
        if pd.notna(location) and location != '--' and len(group) > 10:
            location_support = group['Q77'].isin(voting_support).mean() * 100
            print(f"  {location}: {location_support:.1f}% (n={len(group)})")

analyze_voting_support(df)

# ============================================================================
# ANALYSIS 14.2: AI vs. Politicians Trust
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 14.2: AI VS. POLITICIANS TRUST")
print("="*80)

def analyze_trust_comparison(df):
    print("\nDo more people trust AI than politicians for interpreting animals?")
    
    # Map trust levels to numeric
    trust_map = {
        'Strongly Distrust': 1,
        'Somewhat Distrust': 2,
        'Neither Trust Nor Distrust': 3,
        'Somewhat Trust': 4,
        'Strongly Trust': 5,
        'Strongly distrust': 1,
        'Somewhat distrust': 2,
        'Neutral': 3,
        'Somewhat trust': 4,
        'Strongly trust': 5
    }
    
    # Q14: Trust elected representatives
    df['Q14_score'] = df['Q14'].map(trust_map)
    
    # Q57: Trust AI to interpret animals
    df['Q57_score'] = df['Q57'].map(trust_map)
    
    # Calculate averages
    politician_trust = df['Q14_score'].mean()
    ai_translation_trust = df['Q57_score'].mean()
    
    print(f"\nAverage trust scores (1-5 scale):")
    print(f"  Politicians (Q14): {politician_trust:.2f}")
    print(f"  AI for animal translation (Q57): {ai_translation_trust:.2f}")
    
    # Direct comparison
    trusts_ai_more = (df['Q57_score'] > df['Q14_score']).sum()
    trusts_politicians_more = (df['Q14_score'] > df['Q57_score']).sum()
    trusts_equally = (df['Q14_score'] == df['Q57_score']).sum()
    
    print(f"\nDirect comparison:")
    print(f"  Trust AI more: {trusts_ai_more} ({trusts_ai_more/len(df)*100:.1f}%)")
    print(f"  Trust politicians more: {trusts_politicians_more} ({trusts_politicians_more/len(df)*100:.1f}%)")
    print(f"  Trust equally: {trusts_equally} ({trusts_equally/len(df)*100:.1f}%)")
    
    # Q61: Trust AI vs humans for wildlife conflict
    print("\n" + "-"*60)
    print("Q61: Trust for resolving wildlife conflicts")
    
    # Parse Q61 responses
    q61_ai_trust = 0
    q61_human_trust = 0
    q61_equal = 0
    
    for response in df['Q61_original']:
        if pd.notna(response):
            response_lower = str(response).lower()
            if 'ai more' in response_lower or 'trust ai' in response_lower:
                q61_ai_trust += 1
            elif 'human' in response_lower and 'more' in response_lower:
                q61_human_trust += 1
            elif 'equal' in response_lower or 'same' in response_lower:
                q61_equal += 1
    
    print(f"  Trust AI more: {q61_ai_trust/len(df)*100:.1f}%")
    print(f"  Trust humans more: {q61_human_trust/len(df)*100:.1f}%")
    print(f"  Trust equally: {q61_equal/len(df)*100:.1f}%")

analyze_trust_comparison(df)

# ============================================================================
# ANALYSIS 14.3: Pet Economic Rights by Age
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 14.3: PET ECONOMIC RIGHTS BY AGE")
print("="*80)

def analyze_economic_rights_by_age(df):
    print("\nWhich age group most supports pets earning money or owning things?")
    
    # Define economic rights keywords
    def has_economic_support(response):
        if pd.isna(response) or response == '--':
            return False
        response_lower = str(response).lower()
        return (('earn money' in response_lower or 
                 'own' in response_lower or 
                 'sell' in response_lower) and 
                'none of the above' not in response_lower)
    
    # Apply to Q91
    df['supports_economic'] = df['Q91'].apply(has_economic_support)
    
    # Group by age
    age_support = {}
    age_groups = df.groupby('Q2')
    
    for age, group in age_groups:
        if pd.notna(age) and age != '--' and len(group) > 10:
            support_pct = group['supports_economic'].mean() * 100
            age_support[age] = {
                'percent': support_pct,
                'count': group['supports_economic'].sum(),
                'total': len(group)
            }
    
    # Sort by support percentage
    sorted_ages = sorted(age_support.items(), key=lambda x: x[1]['percent'], reverse=True)
    
    print("\nEconomic rights support by age (highest to lowest):")
    for age, data in sorted_ages:
        print(f"  {age}: {data['percent']:.1f}% ({data['count']}/{data['total']})")
    
    # Identify winner
    if sorted_ages:
        winner = sorted_ages[0]
        print(f"\nMost supportive age group: {winner[0]} with {winner[1]['percent']:.1f}% support")
    
    # Statistical test between youngest and oldest
    young = df[df['Q2'] == '18-25']
    old = df[df['Q2'].isin(['56-65', '65+'])]
    
    if len(young) > 0 and len(old) > 0:
        young_support = young['supports_economic'].mean() * 100
        old_support = old['supports_economic'].mean() * 100
        
        # Chi-square test
        young_yes = young['supports_economic'].sum()
        young_no = len(young) - young_yes
        old_yes = old['supports_economic'].sum()
        old_no = len(old) - old_yes
        
        contingency = np.array([[young_yes, young_no], [old_yes, old_no]])
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
        
        print(f"\n" + "-"*60)
        print(f"Young (18-25) vs Old (56+) comparison:")
        print(f"  18-25: {young_support:.1f}%")
        print(f"  56+: {old_support:.1f}%")
        print(f"  Difference: {young_support - old_support:.1f} percentage points")
        print(f"  Statistical significance: p={p_value:.4f}")

analyze_economic_rights_by_age(df)

# ============================================================================
# ANALYSIS 14.4: East vs. West Legal Personhood
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 14.4: EAST VS. WEST LEGAL PERSONHOOD")
print("="*80)

def analyze_regional_personhood(df):
    print("\nRegional differences in granting legal personhood (Q70-C)")
    
    # First, need to identify regions from Q7
    # Create broad regional categories
    eastern_countries = ['China', 'Japan', 'South Korea', 'India', 'Indonesia', 
                        'Thailand', 'Vietnam', 'Philippines', 'Malaysia', 'Singapore']
    western_countries = ['United States', 'United Kingdom', 'Canada', 'Australia',
                        'France', 'Germany', 'Italy', 'Spain', 'Netherlands', 'Sweden']
    
    # Map countries to regions (simplified for this analysis)
    def get_region(country):
        if pd.isna(country):
            return None
        country_str = str(country)
        for east in eastern_countries:
            if east.lower() in country_str.lower():
                return 'East'
        for west in western_countries:
            if west.lower() in country_str.lower():
                return 'West'
        return 'Other'
    
    df['region'] = df['Q7'].apply(get_region)
    
    # Analyze Q70 preference for legal rights (Future C)
    legal_rights_option = 'Future C: Granting legal rights and representation'
    
    # Calculate by region
    print("\nSupport for legal personhood (Future C) by region:")
    
    for region in ['East', 'West', 'Other']:
        region_df = df[df['region'] == region]
        if len(region_df) > 0:
            support = (region_df['Q70'] == legal_rights_option).mean() * 100
            print(f"  {region}: {support:.1f}% (n={len(region_df)})")
    
    # Statistical test East vs West
    east_df = df[df['region'] == 'East']
    west_df = df[df['region'] == 'West']
    
    if len(east_df) > 0 and len(west_df) > 0:
        east_support = (east_df['Q70'] == legal_rights_option).sum()
        east_total = len(east_df)
        west_support = (west_df['Q70'] == legal_rights_option).sum()
        west_total = len(west_df)
        
        # Chi-square test
        contingency = np.array([
            [east_support, east_total - east_support],
            [west_support, west_total - west_support]
        ])
        
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
        
        print(f"\n" + "-"*60)
        print(f"East vs West comparison:")
        print(f"  Difference: {abs(east_support/east_total - west_support/west_total)*100:.1f} percentage points")
        print(f"  Statistical significance: p={p_value:.4f}")
        print(f"  Result: {'Significant' if p_value < 0.05 else 'Not significant'} regional divide")

analyze_regional_personhood(df)

# ============================================================================
# ANALYSIS 14.5: Hopeful but Cautious Bloc
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 14.5: HOPEFUL BUT CAUTIOUS BLOC")
print("="*80)

def analyze_hopeful_cautious(df):
    print("\nAmong those hopeful about AI translation, how many are also cautious?")
    
    # Identify hopeful respondents (Q54)
    hopeful = df[df['Q54'] == 'Hopeful'].copy()
    print(f"\nTotal hopeful about AI translation: {len(hopeful)} ({len(hopeful)/len(df)*100:.1f}%)")
    
    if len(hopeful) > 0:
        # Check their concerns (Q59 - open text, Q85 - prohibited communications)
        
        # For Q85, check if they selected privacy/manipulation concerns
        privacy_concerns = ['manipulation', 'deception', 'emotional manipulation', 'privacy']
        
        cautious_count = 0
        for idx, row in hopeful.iterrows():
            # Check Q59 for concerns
            q59_concerned = False
            if pd.notna(row['Q59_original']):
                concern_text = str(row['Q59_original']).lower()
                if any(word in concern_text for word in ['privacy', 'manipulat', 'exploit', 'misuse', 'abuse']):
                    q59_concerned = True
            
            # Check Q85 for wanting prohibitions
            q85_concerned = False
            if pd.notna(row['Q85']):
                q85_text = str(row['Q85']).lower()
                if any(word in q85_text for word in privacy_concerns):
                    q85_concerned = True
            
            if q59_concerned or q85_concerned:
                cautious_count += 1
        
        cautious_pct = (cautious_count / len(hopeful)) * 100
        
        print(f"\n'Hopeful but Cautious' bloc:")
        print(f"  Size: {cautious_count} people")
        print(f"  Percentage of hopeful: {cautious_pct:.1f}%")
        print(f"  Percentage of total: {cautious_count/len(df)*100:.1f}%")
        
        # Compare with other emotional responses
        print("\n" + "-"*60)
        print("Caution levels by emotional response (Q54):")
        
        emotions = ['Hopeful', 'Curious', 'Skeptical', 'Concerned', 'Indifferent']
        for emotion in emotions:
            emotion_df = df[df['Q54'] == emotion]
            if len(emotion_df) > 10:
                # Simple proxy: those who want strong restrictions (Q82)
                cautious_proxy = emotion_df['Q82'].isin(['Strongly agree', 'Somewhat agree']).mean() * 100
                print(f"  {emotion}: {cautious_proxy:.1f}% want professional restrictions (n={len(emotion_df)})")

analyze_hopeful_cautious(df)

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 14 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")