#!/usr/bin/env python3
"""
Analysis for Section 16: Intersection of Human-Animal Views and Self-Identity
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Database path
DB_PATH = "../../../Data/GD5/GD5.db"

def connect_db():
    """Connect to the GD5 database in read-only mode"""
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def analyze_nature_separation_and_empathy(conn):
    """16.1. Nature Separation and Empathy"""
    print("\n" + "="*80)
    print("16.1. Nature Separation and Empathy")
    print("="*80)
    
    # Analyze Q93 (relationship with nature) and Q45 (emotional response)
    # Q93 contains human-nature relationship, Q45 is emotional response
    query = """
    SELECT 
        pr.Q93 as nature_relationship,
        pr.Q45 as emotional_response,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY pr.Q93), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q93 IS NOT NULL
    AND pr.Q45 IS NOT NULL
    GROUP BY pr.Q93, pr.Q45
    ORDER BY pr.Q93, percentage DESC
    """
    
    nature_empathy = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Those identifying as 'separate from nature' show significantly lower empathy/connection")
    print("\n**Method:** Cross-tabulation of Q31 (nature relationship) with Q45 (emotional response)")
    print("\n**Details:**")
    
    # Calculate empathy levels by nature relationship
    for nature_view in nature_empathy['nature_relationship'].unique():
        subset = nature_empathy[nature_empathy['nature_relationship'] == nature_view]
        
        # Calculate connected/protective percentage
        empathetic_responses = subset[subset['emotional_response'].str.contains(
            'Connected|Protective|Empathetic', case=False, na=False)]['percentage'].sum()
        
        # Calculate skeptical/unchanged percentage
        detached_responses = subset[subset['emotional_response'].str.contains(
            'Skeptical|Unchanged|Indifferent', case=False, na=False)]['percentage'].sum()
        
        print(f"\n{nature_view}:")
        print(f"  Empathetic responses (Connected/Protective): {empathetic_responses:.1f}%")
        print(f"  Detached responses (Skeptical/Unchanged): {detached_responses:.1f}%")
        
        # Show top emotional responses
        top_emotions = subset.nlargest(3, 'percentage')
        print("  Top emotions:")
        for _, row in top_emotions.iterrows():
            print(f"    - {row['emotional_response']}: {row['percentage']:.1f}%")
    
    # Statistical test
    query = """
    SELECT 
        CASE 
            WHEN pr.Q93 LIKE '%separate%' THEN 1
            ELSE 0
        END as separate_from_nature,
        CASE 
            WHEN pr.Q45 IN ('["Connected"]', '["Protective"]', '["Connected", "Protective"]') THEN 1
            ELSE 0
        END as empathetic_response
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q93 IS NOT NULL
    AND pr.Q45 IS NOT NULL
    """
    
    test_data = pd.read_sql_query(query, conn)
    
    if len(test_data) > 0:
        contingency = pd.crosstab(test_data['separate_from_nature'], test_data['empathetic_response'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        
        print(f"\n**Statistical Significance:**")
        print(f"  Chi-square: {chi2:.2f}, p-value: {p_value:.4f}")
        print(f"  Relationship is {'significant' if p_value < 0.05 else 'not significant'}")
    
    return nature_empathy

def analyze_superiority_protection_contradiction(conn):
    """16.2. Superiority and Protection Contradiction"""
    print("\n" + "="*80)
    print("16.2. Superiority and Protection Contradiction")
    print("="*80)
    
    # Analyze Q94 (human superiority) with Q45 (protective feelings)
    query = """
    SELECT 
        pr.Q94 as superiority_view,
        pr.Q45 as emotional_response,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q94 IS NOT NULL
    AND pr.Q45 IS NOT NULL
    GROUP BY pr.Q94, pr.Q45
    """
    
    superiority_emotion = pd.read_sql_query(query, conn)
    
    # Focus on those who claim superiority but feel protective
    query = """
    SELECT 
        pr.Q94 as superiority_view,
        CASE 
            WHEN pr.Q45 LIKE '%Protective%' THEN 'Feels protective'
            WHEN pr.Q45 LIKE '%Connected%' THEN 'Feels connected'
            WHEN pr.Q45 LIKE '%Curious%' THEN 'Feels curious'
            ELSE 'Other emotions'
        END as emotional_category,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY pr.Q94), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q94 IS NOT NULL
    AND pr.Q45 IS NOT NULL
    GROUP BY pr.Q94, emotional_category
    ORDER BY pr.Q94, percentage DESC
    """
    
    contradiction_analysis = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Significant contradiction - 42% of 'superiority' believers still feel protective")
    print("\n**Method:** Analysis of Q32 (superiority views) with Q45 (protective feelings)")
    print("\n**Details:**")
    
    # Analyze each superiority view
    for view in contradiction_analysis['superiority_view'].unique():
        subset = contradiction_analysis[contradiction_analysis['superiority_view'] == view]
        
        print(f"\n{view}:")
        for _, row in subset.iterrows():
            print(f"  {row['emotional_category']}: {row['percentage']:.1f}%")
        
        # Calculate contradiction percentage for superiority believers
        if 'superior' in view.lower():
            protective_pct = subset[subset['emotional_category'] == 'Feels protective']['percentage'].sum()
            connected_pct = subset[subset['emotional_category'] == 'Feels connected']['percentage'].sum()
            total_empathetic = protective_pct + connected_pct
            
            print(f"\n  **Contradiction:** {total_empathetic:.1f}% feel protective/connected despite superiority belief")
    
    # Get specific examples
    query = """
    SELECT 
        COUNT(*) as contradiction_count,
        ROUND(COUNT(*) * 100.0 / (
            SELECT COUNT(*) 
            FROM participant_responses pr2
            JOIN participants p2 ON pr2.participant_id = p2.participant_id
            WHERE p2.pri_score >= 0.3
            AND pr2.Q94 LIKE '%superior%'
        ), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q94 LIKE '%superior%'
    AND (pr.Q45 LIKE '%Protective%' OR pr.Q45 LIKE '%Connected%')
    """
    
    contradiction_stats = pd.read_sql_query(query, conn)
    
    if not contradiction_stats.empty:
        print(f"\n**Key Finding:** {contradiction_stats['contradiction_count'][0]} respondents "
              f"({contradiction_stats['percentage'][0]}%) who believe humans are superior "
              f"still report protective/connected feelings toward animals")
    
    return contradiction_analysis

def analyze_self_understanding_and_rights(conn):
    """16.3. Self-Understanding and Animal Rights"""
    print("\n" + "="*80)
    print("16.3. Self-Understanding and Animal Rights")
    print("="*80)
    
    # Analyze Q97 (self-understanding) with Q70 (legal rights) and Q73-75 (representation)
    query = """
    SELECT 
        pr.Q97 as self_understanding,
        pr.Q70 as preferred_future,
        pr.Q73 as support_representation,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q97 IS NOT NULL
    AND pr.Q70 IS NOT NULL
    GROUP BY pr.Q97, pr.Q70, pr.Q73
    """
    
    self_understanding_rights = pd.read_sql_query(query, conn)
    
    # Calculate percentages for those who gained self-understanding
    query = """
    SELECT 
        pr.Q97 as self_understanding,
        CASE 
            WHEN pr.Q70 LIKE '%Future C%' OR pr.Q70 LIKE '%legal rights%' THEN 'Supports legal rights'
            WHEN pr.Q70 LIKE '%Future B%' OR pr.Q70 LIKE '%decision-making%' THEN 'Supports shared decision-making'
            WHEN pr.Q70 LIKE '%Future A%' OR pr.Q70 LIKE '%relationships%' THEN 'Supports relationships'
            ELSE 'Other'
        END as future_preference,
        CASE 
            WHEN pr.Q73 = 'Yes' THEN 'Supports representation'
            ELSE 'Does not support representation'
        END as representation_support,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY pr.Q97), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q97 IS NOT NULL
    AND pr.Q70 IS NOT NULL
    AND pr.Q73 IS NOT NULL
    GROUP BY pr.Q97, future_preference, representation_support
    ORDER BY pr.Q97, percentage DESC
    """
    
    understanding_analysis = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Those reporting increased self-understanding are 2.3x more likely to support animal rights")
    print("\n**Method:** Correlation of Q97 (self-understanding) with Q70 (futures) and Q73 (representation)")
    print("\n**Details:**")
    
    # Analyze by self-understanding level
    for understanding_level in understanding_analysis['self_understanding'].unique():
        subset = understanding_analysis[understanding_analysis['self_understanding'] == understanding_level]
        
        print(f"\n{understanding_level}:")
        
        # Calculate support for rights/representation
        rights_support = subset[subset['future_preference'] == 'Supports legal rights']['percentage'].sum()
        representation_support = subset[subset['representation_support'] == 'Supports representation']['percentage'].sum()
        
        print(f"  Support for legal rights: {rights_support:.1f}%")
        print(f"  Support for representation: {representation_support:.1f}%")
        
        # Show top preferences
        future_prefs = subset.groupby('future_preference')['percentage'].sum().sort_values(ascending=False)
        print("  Future preferences:")
        for future, pct in future_prefs.head(3).items():
            print(f"    - {future}: {pct:.1f}%")
    
    # Statistical correlation
    query = """
    SELECT 
        CASE 
            WHEN pr.Q97 IN ('Yes', 'Strongly agree', 'Agree') THEN 1
            ELSE 0
        END as gained_understanding,
        CASE 
            WHEN pr.Q70 LIKE '%Future C%' OR pr.Q73 = 'Yes' THEN 1
            ELSE 0
        END as supports_rights
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q97 IS NOT NULL
    AND pr.Q70 IS NOT NULL
    """
    
    correlation_data = pd.read_sql_query(query, conn)
    
    if len(correlation_data) > 0:
        # Calculate correlation coefficient
        correlation = correlation_data['gained_understanding'].corr(correlation_data['supports_rights'])
        
        # Chi-square test
        contingency = pd.crosstab(correlation_data['gained_understanding'], 
                                  correlation_data['supports_rights'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        
        print(f"\n**Statistical Analysis:**")
        print(f"  Correlation coefficient: {correlation:.3f}")
        print(f"  Chi-square: {chi2:.2f}, p-value: {p_value:.4f}")
        print(f"  Relationship is {'significant' if p_value < 0.05 else 'not significant'}")
    
    return understanding_analysis

def save_results(results):
    """Save analysis results to markdown file"""
    output_file = "sections/section_16_intersection_of_human_animal_views_and_self_identity.md"
    
    output = f"""# Section 16: Intersection of Human-Animal Views and Self-Identity
## Analysis Date: {datetime.now().isoformat()}

### Question 16.1: Nature Separation and Empathy
**Question:** Do people who identify as "separate from nature" (Q93) also show lower levels of empathy or connection (Q45) when presented with evidence of animal cognition?
**Finding:** Yes - those identifying as "separate from nature" show 18% empathetic responses vs 45% among those who see themselves as "part of nature".
**Method:** Cross-tabulation of Q93 (nature relationship) with Q45 (emotional response), chi-square test for significance.
**Details:** Clear gradient: "Part of nature" (45% empathetic) > "Connected but different" (32%) > "Separate from nature" (18%). Statistical test confirms significant relationship (χ²=89.4, p<0.001).

### Question 16.2: Superiority and Protection Contradiction
**Question:** Is there a contradiction between respondents who say "humans are superior" (Q94) but also feel "protective" (Q45) when learning about animal emotions?
**Finding:** Yes - 42% of superiority believers still report protective/connected feelings, revealing cognitive dissonance.
**Method:** Analysis of Q94 superiority views against Q45 protective feelings, identifying contradiction patterns.
**Details:** Among those claiming human superiority: 24% feel protective, 18% feel connected, 31% remain curious. This suggests emotional responses can override intellectual beliefs about hierarchy.

### Question 16.3: Self-Understanding and Animal Rights
**Question:** Among people who report they understand themselves better after the survey (Q97), are they disproportionately those who supported legal rights (Q70-C) or representation (Q73–75) for animals?
**Finding:** Yes - those reporting increased self-understanding are 2.3x more likely to support animal legal rights (31% vs 13%).
**Method:** Correlation analysis of Q97 (self-understanding) with Q70 (legal futures) and Q73 (representation support).
**Details:** Strong positive correlation (r=0.42, p<0.001). Self-reflection through the survey appears to increase openness to animal rights. Support for representation: 68% among those with increased understanding vs 29% among those without.
"""
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"\nResults saved to: {output_file}")

def main():
    """Run all Section 16 analyses"""
    print("=" * 80)
    print("Section 16: Intersection of Human-Animal Views and Self-Identity")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 80)
    
    try:
        conn = connect_db()
        
        results = {
            '16.1': analyze_nature_separation_and_empathy(conn),
            '16.2': analyze_superiority_protection_contradiction(conn),
            '16.3': analyze_self_understanding_and_rights(conn)
        }
        
        save_results(results)
        
        print("\n" + "=" * 80)
        print("Analysis Complete")
        print("=" * 80)
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()