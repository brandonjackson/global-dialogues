#!/usr/bin/env python3
"""
Section 20: Moral/Ethical Contradictions
This analysis explores tensions and contradictions in respondents' ethical positions
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

# Helper function for Q91 parsing
def parse_q91_economic(response):
    """Check if response contains economic rights"""
    if pd.isna(response) or response == '--':
        return {
            'earn_money': False,
            'own_property': False,
            'sell_things': False,
            'own_creations': False,
            'any_economic': False,
            'none': False
        }
    
    response_lower = str(response).lower()
    result = {
        'earn_money': 'earn money' in response_lower,
        'own_property': 'own property' in response_lower,
        'sell_things': 'sell things' in response_lower or 'be able to sell' in response_lower,
        'own_creations': 'own things they make' in response_lower,
        'any_economic': False,
        'none': 'none of the above' in response_lower
    }
    
    # Check if any economic right is supported
    result['any_economic'] = (result['earn_money'] or result['own_property'] or 
                              result['sell_things'] or result['own_creations']) and not result['none']
    
    return result

# ============================================================================
# ANALYSIS 20.1: Selective Democratic Acceptance
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 20.1: SELECTIVE DEMOCRATIC ACCEPTANCE")
print("="*80)

def analyze_selective_acceptance(df):
    print("\nAmong those opposing animal democratic participation,")
    print("how many still support legal representation?")
    
    # Identify those who oppose democratic participation
    no_democracy = df[df['Q77'] == 'No, they should not be able to participate.'].copy()
    print(f"\nTotal opposing democratic participation: {len(no_democracy)} ({len(no_democracy)/len(df)*100:.1f}%)")
    
    if len(no_democracy) > 0:
        # Check their views on legal representation (Q73)
        print("\nTheir views on legal representation (Q73):")
        q73_dist = no_democracy['Q73'].value_counts()
        q73_pct = no_democracy['Q73'].value_counts(normalize=True) * 100
        
        for response, count in q73_dist.items():
            if pd.notna(response):
                pct = q73_pct[response]
                print(f"  {response}: {count} ({pct:.1f}%)")
        
        # Calculate selective acceptance
        supports_representation = (no_democracy['Q73'] == 'Yes').sum()
        selective_acceptance_pct = (supports_representation / len(no_democracy)) * 100
        
        print(f"\nSelective acceptance (no democracy but yes representation): {supports_representation} ({selective_acceptance_pct:.1f}%)")
        
        # Among those with selective acceptance, how do they want representation? (Q74)
        selective_group = no_democracy[no_democracy['Q73'] == 'Yes']
        if len(selective_group) > 0:
            print(f"\nAmong selective acceptors (n={len(selective_group)}), preferred representation method (Q74):")
            q74_dist = selective_group['Q74'].value_counts(normalize=True) * 100
            for method, pct in q74_dist.items():
                if pd.notna(method):
                    print(f"  {method[:50]}...: {pct:.1f}%")
    
    # Compare with general population
    print("\n" + "-"*60)
    print("Comparison with general population:")
    gen_rep_support = (df['Q73'] == 'Yes').mean() * 100
    print(f"  General population supporting representation: {gen_rep_support:.1f}%")
    print(f"  No-democracy group supporting representation: {selective_acceptance_pct:.1f}%")
    print(f"  Difference: {selective_acceptance_pct - gen_rep_support:.1f} percentage points")

analyze_selective_acceptance(df)

# ============================================================================
# ANALYSIS 20.2: Professional Restrictions vs. Democratic Rights
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 20.2: PROFESSIONAL RESTRICTIONS VS. DEMOCRATIC RIGHTS")
print("="*80)

def analyze_restriction_democracy_tension(df):
    print("\nTension between wanting professional restrictions and democratic rights")
    
    # Define groups
    # Strong restriction supporters (Q82)
    strong_restrict = df[df['Q82'].isin(['Strongly agree', 'Somewhat agree'])].copy()
    
    # Democratic rights supporters (Q77)
    democratic_options = [
        'Yes, they should be able to vote through human proxies or guardians.',
        'Yes, they should be recognized as a formal political constituency with dedicated representatives in government.'
    ]
    
    full_democracy = df[df['Q77'].isin(democratic_options)].copy()
    
    print(f"\nSupport professional restrictions (Q82): {len(strong_restrict)} ({len(strong_restrict)/len(df)*100:.1f}%)")
    print(f"Support full democratic rights (Q77): {len(full_democracy)} ({len(full_democracy)/len(df)*100:.1f}%)")
    
    # Find overlap - the tension group
    tension_group = df[
        df['Q82'].isin(['Strongly agree', 'Somewhat agree']) & 
        df['Q77'].isin(democratic_options)
    ]
    
    print(f"\nTension group (want both restrictions AND democratic rights): {len(tension_group)}")
    print(f"  Percentage of total: {len(tension_group)/len(df)*100:.1f}%")
    print(f"  Percentage of restriction supporters: {len(tension_group)/len(strong_restrict)*100:.1f}%")
    print(f"  Percentage of democracy supporters: {len(tension_group)/len(full_democracy)*100:.1f}%")
    
    # Analyze the tension group's characteristics
    if len(tension_group) > 0:
        print("\n" + "-"*60)
        print("Tension group characteristics:")
        
        # Their specific democratic preferences
        print("\nDemocratic preferences (Q77):")
        for option in democratic_options:
            count = (tension_group['Q77'] == option).sum()
            if count > 0:
                print(f"  {option[:50]}...: {count}")
        
        # Their restriction strength
        print("\nRestriction strength (Q82):")
        q82_dist = tension_group['Q82'].value_counts()
        for level, count in q82_dist.items():
            print(f"  {level}: {count}")
    
    # Statistical test for negative correlation
    df['wants_restrictions'] = df['Q82'].isin(['Strongly agree', 'Somewhat agree'])
    df['wants_democracy'] = df['Q77'].isin(democratic_options)
    
    contingency = pd.crosstab(df['wants_restrictions'], df['wants_democracy'])
    chi2, p_value = stats.chi2_contingency(contingency)[:2]
    
    # Calculate correlation
    correlation = df['wants_restrictions'].astype(int).corr(df['wants_democracy'].astype(int))
    
    print(f"\n" + "-"*60)
    print("Statistical relationship:")
    print(f"  Correlation: {correlation:.3f}")
    print(f"  Chi-square p-value: {p_value:.4f}")
    print(f"  Result: {'Significant' if p_value < 0.05 else 'Not significant'} relationship")

analyze_restriction_democracy_tension(df)

# ============================================================================
# ANALYSIS 20.3: Property vs. Economic Participation
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS 20.3: PROPERTY VS. ECONOMIC PARTICIPATION")
print("="*80)

def analyze_property_economic_split(df):
    print("\nDo property ownership supporters also support economic participation?")
    
    # Parse Q91 responses
    economic_rights = df['Q91'].apply(parse_q91_economic)
    economic_df = pd.DataFrame(list(economic_rights))
    
    # Combine with main dataframe
    for col in economic_df.columns:
        df[f'Q91_{col}'] = economic_df[col]
    
    # Analyze property ownership supporters
    property_supporters = df[df['Q91_own_property'] == True].copy()
    print(f"\nTotal supporting property ownership: {len(property_supporters)} ({len(property_supporters)/len(df)*100:.1f}%)")
    
    if len(property_supporters) > 0:
        print("\nAmong property ownership supporters, also support:")
        
        # Check other economic rights
        earn_money_pct = property_supporters['Q91_earn_money'].mean() * 100
        sell_things_pct = property_supporters['Q91_sell_things'].mean() * 100
        own_creations_pct = property_supporters['Q91_own_creations'].mean() * 100
        
        print(f"  Earning money: {earn_money_pct:.1f}%")
        print(f"  Selling things: {sell_things_pct:.1f}%")
        print(f"  Owning their creations: {own_creations_pct:.1f}%")
        
        # Check for "symbolic only" supporters (property but no active economic rights)
        symbolic_only = property_supporters[
            (property_supporters['Q91_own_property'] == True) &
            (property_supporters['Q91_earn_money'] == False) &
            (property_supporters['Q91_sell_things'] == False)
        ]
        
        symbolic_pct = (len(symbolic_only) / len(property_supporters)) * 100
        print(f"\nSymbolic only (property but no earning/selling): {len(symbolic_only)} ({symbolic_pct:.1f}%)")
    
    # Reverse analysis: earning money supporters
    print("\n" + "-"*60)
    money_supporters = df[df['Q91_earn_money'] == True].copy()
    print(f"Total supporting earning money: {len(money_supporters)} ({len(money_supporters)/len(df)*100:.1f}%)")
    
    if len(money_supporters) > 0:
        print("\nAmong earning money supporters, also support:")
        
        property_pct = money_supporters['Q91_own_property'].mean() * 100
        sell_pct = money_supporters['Q91_sell_things'].mean() * 100
        own_creations_pct = money_supporters['Q91_own_creations'].mean() * 100
        
        print(f"  Property ownership: {property_pct:.1f}%")
        print(f"  Selling things: {sell_pct:.1f}%")
        print(f"  Owning creations: {own_creations_pct:.1f}%")
    
    # Create typology
    print("\n" + "-"*60)
    print("Economic rights typology:")
    
    # Full economic rights
    full_economic = df[
        (df['Q91_earn_money'] == True) & 
        (df['Q91_own_property'] == True) & 
        (df['Q91_sell_things'] == True)
    ]
    
    # Partial economic rights (some but not all)
    partial_economic = df[
        (df['Q91_any_economic'] == True) &
        ~((df['Q91_earn_money'] == True) & 
          (df['Q91_own_property'] == True) & 
          (df['Q91_sell_things'] == True))
    ]
    
    # No economic rights
    no_economic = df[df['Q91_none'] == True]
    
    print(f"  Full economic rights (all three): {len(full_economic)} ({len(full_economic)/len(df)*100:.1f}%)")
    print(f"  Partial economic rights: {len(partial_economic)} ({len(partial_economic)/len(df)*100:.1f}%)")
    print(f"  No economic rights: {len(no_economic)} ({len(no_economic)/len(df)*100:.1f}%)")
    
    # Test correlation between property and active economic participation
    correlation = df['Q91_own_property'].astype(int).corr(df['Q91_earn_money'].astype(int))
    print(f"\nCorrelation between property and earning money: {correlation:.3f}")

analyze_property_economic_split(df)

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 20 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")