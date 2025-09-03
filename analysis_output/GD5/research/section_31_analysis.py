#!/usr/bin/env python3
"""
Section 31: Contradiction & Tension Mapping
This comprehensive analysis explores contradictions and tensions in respondents' beliefs
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
def has_economic_support(response, specific_type=None):
    """Check if response supports economic rights"""
    if pd.isna(response) or response == '--':
        return False
    response_lower = str(response).lower()
    
    if specific_type == 'property':
        return 'own property' in response_lower
    elif specific_type == 'money':
        return 'earn money' in response_lower
    elif specific_type == 'any':
        return (('earn money' in response_lower or 
                 'own' in response_lower or 
                 'sell' in response_lower) and 
                'none of the above' not in response_lower)
    return False

print("\n" + "="*80)
print("SECTION 31: CONTRADICTION & TENSION MAPPING")
print("="*80)

# ============================================================================
# 31.1: Superiority Claims and Legal Rights
# ============================================================================
print("\n31.1. SUPERIORITY CLAIMS AND LEGAL RIGHTS")
print("-"*60)

# Q94 is the repeated Q32 at end of survey
superior = df[df['Q94'] == 'Humans are fundamentally superior to other animals'].copy()
print(f"Total claiming human superiority: {len(superior)} ({len(superior)/len(df)*100:.1f}%)")

if len(superior) > 0:
    # Check support for legal rights (Q70-C)
    legal_rights = superior[superior['Q70'] == 'Future C: Granting legal rights and representation']
    print(f"  Support legal rights (Q70-C): {len(legal_rights)} ({len(legal_rights)/len(superior)*100:.1f}%)")
    
    # Check economic rights (Q91)
    superior['has_economic'] = superior['Q91'].apply(lambda x: has_economic_support(x, 'any'))
    econ_support = superior['has_economic'].sum()
    print(f"  Support economic rights (Q91): {econ_support} ({econ_support/len(superior)*100:.1f}%)")
    
    # Both legal and economic
    both = superior[(superior['Q70'] == 'Future C: Granting legal rights and representation') & 
                   (superior['has_economic'] == True)]
    print(f"  Support BOTH legal and economic: {len(both)} ({len(both)/len(superior)*100:.1f}%)")

# ============================================================================
# 31.2: Culture Belief and Political Representation
# ============================================================================
print("\n31.2. CULTURE BELIEF AND POLITICAL REPRESENTATION")
print("-"*60)

culture_believers = df[df['Q41'] == 'Strongly believe'].copy()
print(f"Strongly believe animals have culture: {len(culture_believers)} ({len(culture_believers)/len(df)*100:.1f}%)")

if len(culture_believers) > 0:
    # Check those who reject political representation
    no_politics = culture_believers[culture_believers['Q77'] == 'No, they should not be able to participate.']
    print(f"  Reject political representation: {len(no_politics)} ({len(no_politics)/len(culture_believers)*100:.1f}%)")

# ============================================================================
# 31.3: Professional Restrictions vs. Political Participation
# ============================================================================
print("\n31.3. PROFESSIONAL RESTRICTIONS VS. POLITICAL PARTICIPATION")
print("-"*60)

restrict_prof = df[df['Q82'].isin(['Strongly agree', 'Somewhat agree'])].copy()
print(f"Want professional restrictions: {len(restrict_prof)} ({len(restrict_prof)/len(df)*100:.1f}%)")

political_options = [
    'Yes, they should be able to vote through human proxies or guardians.',
    'Yes, they should be recognized as a formal political constituency with dedicated representatives in government.'
]

if len(restrict_prof) > 0:
    full_politics = restrict_prof[restrict_prof['Q77'].isin(political_options)]
    print(f"  Also support full political participation: {len(full_politics)} ({len(full_politics)/len(restrict_prof)*100:.1f}%)")

# ============================================================================
# 31.4: Democratic Participation vs. Legal Representation
# ============================================================================
print("\n31.4. DEMOCRATIC PARTICIPATION VS. LEGAL REPRESENTATION")
print("-"*60)

no_democracy = df[df['Q77'] == 'No, they should not be able to participate.'].copy()
print(f"Oppose democratic participation: {len(no_democracy)} ({len(no_democracy)/len(df)*100:.1f}%)")

if len(no_democracy) > 0:
    yes_legal = no_democracy[no_democracy['Q73'] == 'Yes']
    print(f"  Still support legal representation: {len(yes_legal)} ({len(yes_legal)/len(no_democracy)*100:.1f}%)")

# ============================================================================
# 31.5: Property Ownership vs. Protection Rights
# ============================================================================
print("\n31.5. PROPERTY OWNERSHIP VS. PROTECTION RIGHTS")
print("-"*60)

df['supports_property'] = df['Q91'].apply(lambda x: has_economic_support(x, 'property'))
property_supporters = df[df['supports_property'] == True].copy()
print(f"Support property ownership: {len(property_supporters)} ({len(property_supporters)/len(df)*100:.1f}%)")

if len(property_supporters) > 0:
    # Check if they DON'T support protection rights (not choosing Future C)
    no_protection = property_supporters[property_supporters['Q70'] != 'Future C: Granting legal rights and representation']
    print(f"  Do NOT support legal protection rights: {len(no_protection)} ({len(no_protection)/len(property_supporters)*100:.1f}%)")
    
    # Breakdown of what they do support
    print("  Their preferred futures:")
    future_counts = property_supporters['Q70'].value_counts()
    for future, count in future_counts.head().items():
        print(f"    {future[:40]}...: {count}")

# ============================================================================
# 31.6: Distrust vs. Interest Tension
# ============================================================================
print("\n31.6. DISTRUST VS. INTEREST TENSION")
print("-"*60)

distrust_ai = df[df['Q57'].isin(['Strongly distrust', 'Somewhat distrust'])].copy()
print(f"Distrust AI translation: {len(distrust_ai)} ({len(distrust_ai)/len(df)*100:.1f}%)")

if len(distrust_ai) > 0:
    very_interested = distrust_ai[distrust_ai['Q55'] == 'Very interested']
    print(f"  Still 'Very interested' in hearing animals: {len(very_interested)} ({len(very_interested)/len(distrust_ai)*100:.1f}%)")
    
    # Show full interest distribution among distrusters
    print("  Interest levels among those who distrust:")
    for interest, count in distrust_ai['Q55'].value_counts().items():
        print(f"    {interest}: {count} ({count/len(distrust_ai)*100:.1f}%)")

# ============================================================================
# 31.7: Human-Nature Views and Emotional Closeness
# ============================================================================
print("\n31.7. HUMAN-NATURE VIEWS AND EMOTIONAL CLOSENESS")
print("-"*60)

# Q93 is the repeated Q31
part_different = df[df['Q93'] == 'Humans are a part of nature but fundamentally different from other animals'].copy()
print(f"'Part of nature but different': {len(part_different)} ({len(part_different)/len(df)*100:.1f}%)")

if len(part_different) > 0:
    # Q45 is emotional response (multi-select stored as list)
    emotional_responses = ['Connected', 'Protective', 'Curious']
    
    # Count emotional closeness indicators
    close_emotions = 0
    for response in part_different['Q45']:
        if pd.notna(response):
            response_str = str(response)
            if any(emotion in response_str for emotion in emotional_responses):
                close_emotions += 1
    
    closeness_pct = (close_emotions / len(part_different)) * 100
    print(f"  Express emotional closeness (Connected/Protective/Curious): {close_emotions} ({closeness_pct:.1f}%)")
    
    # Compare with other nature views
    print("\nComparison across nature views:")
    for view in df['Q93'].unique():
        if pd.notna(view) and view != '--':
            view_df = df[df['Q93'] == view]
            view_close = 0
            for response in view_df['Q45']:
                if pd.notna(response):
                    if any(emotion in str(response) for emotion in emotional_responses):
                        view_close += 1
            if len(view_df) > 0:
                print(f"  {view[:40]}...: {view_close/len(view_df)*100:.1f}% express closeness")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "="*80)
print("SUMMARY: KEY CONTRADICTIONS AND TENSIONS")
print("="*80)

contradictions = [
    ("Superiority + Legal Rights", len(superior[superior['Q70'] == 'Future C: Granting legal rights and representation']) if len(superior) > 0 else 0, len(superior) if 'superior' in locals() else 0),
    ("Culture Belief + No Politics", len(no_politics) if 'no_politics' in locals() else 0, len(culture_believers) if 'culture_believers' in locals() else 0),
    ("Restrictions + Full Politics", len(full_politics) if 'full_politics' in locals() else 0, len(restrict_prof) if 'restrict_prof' in locals() else 0),
    ("No Democracy + Yes Legal Rep", len(yes_legal) if 'yes_legal' in locals() else 0, len(no_democracy) if 'no_democracy' in locals() else 0),
    ("Property + No Protection", len(no_protection) if 'no_protection' in locals() else 0, len(property_supporters) if 'property_supporters' in locals() else 0),
    ("Distrust AI + Very Interested", len(very_interested) if 'very_interested' in locals() else 0, len(distrust_ai) if 'distrust_ai' in locals() else 0)
]

print("\nContradiction rates:")
for name, count, total in contradictions:
    if total > 0:
        pct = (count / total) * 100
        print(f"  {name}: {count}/{total} ({pct:.1f}%)")

# Close connection
conn.close()

print("\n" + "="*80)
print("SECTION 31 ANALYSIS COMPLETE")
print("="*80)
print(f"\nAnalysis timestamp: {datetime.now().isoformat()}")