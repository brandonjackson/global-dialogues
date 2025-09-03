#!/usr/bin/env python3
"""
Section 7: Probing for Ideological Consistency and Contradictions
This analysis examines tensions and patterns within individual belief systems
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

# Map Q91 responses - it's a multi-select question
def parse_q91_responses(response_str):
    """Parse Q91 multi-select responses"""
    if pd.isna(response_str):
        return []
    # Split by common delimiters
    items = str(response_str).split(',') if ',' in str(response_str) else [str(response_str)]
    return [item.strip() for item in items]

# ============================================================================
# ANALYSIS 7.1: From Equality to Economics
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 7.1: FROM EQUALITY TO ECONOMICS")
print("="*80)

def analyze_equality_to_economics(df):
    print("\nAmong those who believe humans are 'fundamentally equal to other animals' (Q32),")
    print("what percentage endorse economic rights for animals (Q91)?")
    
    # First, check Q94 distribution (Q94 is the repeated Q32 at end of survey)
    q94_dist = df['Q94'].value_counts()
    print("\nQ94 Distribution (human superiority/equality):")
    for val, count in q94_dist.items():
        if pd.notna(val):
            print(f"  {val}: {count} ({count/len(df)*100:.1f}%)")
    
    # Filter for those who believe in equality
    equal_believers = df[df['Q94'] == 'Humans are fundamentally equal to other animals'].copy()
    print(f"\nParticipants believing in equality: {len(equal_believers)}")
    
    if len(equal_believers) > 0:
        # Check their Q91 responses
        economic_rights_keywords = ['Earn money', 'Own property', 'Own things they make', 
                                  'sell things to humans', 'Pay humans for services']
        
        # Count support for each economic right
        results = {}
        for _, row in equal_believers.iterrows():
            q91_responses = parse_q91_responses(row['Q91'])
            for response in q91_responses:
                if response and response != 'None of the above':
                    results[response] = results.get(response, 0) + 1
        
        print("\nAmong equality believers, support for economic rights:")
        for right, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(equal_believers)) * 100
            print(f"  {right}: {percentage:.1f}%")
        
        # Check for any economic rights support
        any_economic = 0
        for _, row in equal_believers.iterrows():
            q91_responses = parse_q91_responses(row['Q91'])
            if any('money' in r.lower() or 'own' in r.lower() or 'sell' in r.lower() 
                   for r in q91_responses if r and r != 'None of the above'):
                any_economic += 1
        
        print(f"\nSupport ANY economic right: {any_economic/len(equal_believers)*100:.1f}%")
        
        # Compare with non-equality believers
        non_equal = df[df['Q94'] != 'Humans are fundamentally equal to other animals']
        non_equal_economic = 0
        for _, row in non_equal.iterrows():
            q91_responses = parse_q91_responses(row['Q91'])
            if any('money' in r.lower() or 'own' in r.lower() or 'sell' in r.lower() 
                   for r in q91_responses if r and r != 'None of the above'):
                non_equal_economic += 1
        
        if len(non_equal) > 0:
            print(f"\nComparison:")
            print(f"  Equality believers supporting economic rights: {any_economic/len(equal_believers)*100:.1f}%")
            print(f"  Non-equality believers supporting economic rights: {non_equal_economic/len(non_equal)*100:.1f}%")

analyze_equality_to_economics(df)

# ============================================================================
# ANALYSIS 7.2: The Skeptic's Interest
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 7.2: THE SKEPTIC'S INTEREST")
print("="*80)

def analyze_skeptics_interest(df):
    print("\nAmong AI skeptics who distrust translation, how many are still interested?")
    
    # Find skeptics: "More concerned" about AI (Q5) AND "Strongly distrust" translation (Q57)
    skeptics = df[
        (df['Q5'] == 'More concerned than excited') & 
        (df['Q57'] == 'Strongly distrust')
    ].copy()
    
    print(f"\nTotal skeptics (concerned + strongly distrust): {len(skeptics)}")
    
    if len(skeptics) > 0:
        # Check their interest level (Q55)
        interest_dist = skeptics['Q55'].value_counts()
        print("\nInterest distribution among skeptics:")
        for interest, count in interest_dist.items():
            if pd.notna(interest):
                print(f"  {interest}: {count} ({count/len(skeptics)*100:.1f}%)")
        
        # Count "Very interested" despite skepticism
        very_interested = (skeptics['Q55'] == 'Very interested').sum()
        somewhat_interested = (skeptics['Q55'] == 'Somewhat interested').sum()
        any_interested = very_interested + somewhat_interested
        
        print(f"\nKey finding:")
        print(f"  Very interested despite skepticism: {very_interested} ({very_interested/len(skeptics)*100:.1f}%)")
        print(f"  At least somewhat interested: {any_interested} ({any_interested/len(skeptics)*100:.1f}%)")
    
    # Compare with general population
    print("\n" + "-"*60)
    print("General population interest (Q55):")
    gen_interest = df['Q55'].value_counts(normalize=True) * 100
    for interest, pct in gen_interest.items():
        if pd.notna(interest):
            print(f"  {interest}: {pct:.1f}%")

analyze_skeptics_interest(df)

# ============================================================================
# ANALYSIS 7.3: The Regulation Paradox
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 7.3: THE REGULATION PARADOX")
print("="*80)

def analyze_regulation_paradox(df):
    print("\nCorrelation between strict company regulation (Q84) and open access (Q83)")
    
    # First check if Q83 and Q84 exist in the data
    if 'Q83' not in df.columns or 'Q84' not in df.columns:
        print("Note: Q83 or Q84 not found in participant_responses table")
        # Try to get from responses table
        query = """
        SELECT DISTINCT question_id, question
        FROM responses
        WHERE question LIKE '%everyone should be allowed to listen%'
           OR question LIKE '%companies that profit from animals%'
        LIMIT 10
        """
        questions = pd.read_sql_query(query, conn)
        print("\nSearching for regulation questions in responses table...")
        print(questions)
        return
    
    # Get those who answered both questions
    both_answered = df[df['Q83'].notna() & df['Q84'].notna()].copy()
    print(f"Participants who answered both: {len(both_answered)}")
    
    if len(both_answered) > 0:
        # Map to numeric scale
        agreement_map = {
            'Strongly disagree': 1,
            'Somewhat disagree': 2,
            'Neutral': 3,
            'Somewhat agree': 4,
            'Strongly agree': 5
        }
        
        both_answered['Q83_num'] = both_answered['Q83'].map(agreement_map)
        both_answered['Q84_num'] = both_answered['Q84'].map(agreement_map)
        
        # Calculate correlation
        correlation = both_answered['Q83_num'].corr(both_answered['Q84_num'])
        print(f"\nCorrelation coefficient: {correlation:.3f}")
        
        # Create crosstab for detailed analysis
        # High regulation support = Agree/Strongly agree on Q84
        high_regulation = both_answered['Q84'].isin(['Strongly agree', 'Somewhat agree'])
        open_access = both_answered['Q83'].isin(['Strongly agree', 'Somewhat agree'])
        
        crosstab = pd.crosstab(high_regulation, open_access)
        print("\nCrosstab: Company Regulation (Q84) vs Open Access (Q83)")
        print("Rows: Support strict company regulation")
        print("Cols: Support open public access")
        print(crosstab)
        
        # Calculate the paradox group
        paradox_group = both_answered[high_regulation & open_access]
        print(f"\nParadox group (want both regulation AND open access): {len(paradox_group)} ({len(paradox_group)/len(both_answered)*100:.1f}%)")

analyze_regulation_paradox(df)

# ============================================================================
# ANALYSIS 7.4: Does Believing in Animal Culture Make You a Political Radical?
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 7.4: HEADLINE - BELIEVING IN ANIMAL CULTURE & POLITICAL RADICALISM")
print("="*80)

def analyze_culture_political_correlation(df):
    print("\nCorrelation between belief in animal culture (Q41) and radical representation")
    
    # Get strong believers in animal culture
    culture_believers = df[df['Q41'] == 'Strongly believe'].copy()
    culture_skeptics = df[df['Q41'].isin(['Strongly skeptical', 'Somewhat skeptical'])].copy()
    
    print(f"\nStrongly believe animals have culture: {len(culture_believers)}")
    print(f"Skeptical about animal culture: {len(culture_skeptics)}")
    
    # Check Q77 (democratic participation)
    if 'Q77' in df.columns:
        print("\n" + "-"*60)
        print("Support for animal democratic participation (Q77):")
        
        # Define "radical" positions
        radical_positions = [
            'Yes, they should be able to vote through human proxies or guardians.',
            'Yes, they should be recognized as a formal political constituency with dedicated representatives in government.'
        ]
        
        # Among culture believers
        if len(culture_believers) > 0:
            q77_dist = culture_believers['Q77'].value_counts()
            print("\nAmong strong culture believers:")
            for position, count in q77_dist.items():
                if pd.notna(position):
                    pct = count/len(culture_believers)*100
                    marker = " [RADICAL]" if position in radical_positions else ""
                    print(f"  {position[:50]}...: {pct:.1f}%{marker}")
            
            radical_support = culture_believers['Q77'].isin(radical_positions).sum()
            print(f"\nTotal supporting radical positions: {radical_support/len(culture_believers)*100:.1f}%")
        
        # Among culture skeptics
        if len(culture_skeptics) > 0:
            print("\nAmong culture skeptics:")
            skeptic_radical = culture_skeptics['Q77'].isin(radical_positions).sum()
            print(f"  Supporting radical positions: {skeptic_radical/len(culture_skeptics)*100:.1f}%")
    
    # Check Q91 (economic rights)
    print("\n" + "-"*60)
    print("Support for AI managing animal rights (Q91):")
    
    if len(culture_believers) > 0:
        # Check for AI management support
        ai_manage_count = 0
        for _, row in culture_believers.iterrows():
            q91_responses = parse_q91_responses(row['Q91'])
            if any('AI manage' in r for r in q91_responses):
                ai_manage_count += 1
        
        print(f"\nAmong culture believers:")
        print(f"  Support AI managing animal data/rights: {ai_manage_count/len(culture_believers)*100:.1f}%")
    
    if len(culture_skeptics) > 0:
        ai_manage_skeptics = 0
        for _, row in culture_skeptics.iterrows():
            q91_responses = parse_q91_responses(row['Q91'])
            if any('AI manage' in r for r in q91_responses):
                ai_manage_skeptics += 1
        
        print(f"\nAmong culture skeptics:")
        print(f"  Support AI managing animal data/rights: {ai_manage_skeptics/len(culture_skeptics)*100:.1f}%")
    
    # Statistical test
    if 'Q77' in df.columns and len(culture_believers) > 0 and len(culture_skeptics) > 0:
        # Test if culture belief predicts radical positions
        df['culture_strong'] = df['Q41'] == 'Strongly believe'
        df['political_radical'] = df['Q77'].isin(radical_positions)
        
        # Chi-square test
        contingency = pd.crosstab(df['culture_strong'], df['political_radical'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        
        print(f"\n" + "-"*60)
        print(f"Statistical test (culture belief vs radical politics):")
        print(f"  Chi-square: {chi2:.2f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Result: {'Significant' if p_value < 0.05 else 'Not significant'} correlation")

analyze_culture_political_correlation(df)

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 7 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")