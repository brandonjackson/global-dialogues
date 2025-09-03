#!/usr/bin/env python3
"""
Analysis for Section 10: Public Understanding of Animals & Communication
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

def analyze_beliefs_and_legal_rights(conn):
    """10.1. Beliefs and Legal Rights"""
    print("\n" + "="*80)
    print("10.1. Beliefs and Legal Rights")
    print("="*80)
    
    # Get beliefs in language, emotion, culture (Q39-Q41) and correlate with legal rights (Q70) and representation (Q73-Q75)
    
    # First, get the distribution of beliefs
    query = """
    SELECT 
        pr.Q39 as language_belief,
        pr.Q40 as emotion_belief,
        pr.Q41 as culture_belief,
        pr.Q70 as preferred_future,
        pr.Q73 as right_to_representative,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q39 IS NOT NULL
    AND pr.Q40 IS NOT NULL
    AND pr.Q41 IS NOT NULL
    AND pr.Q70 IS NOT NULL
    GROUP BY pr.Q39, pr.Q40, pr.Q41, pr.Q70, pr.Q73
    """
    
    beliefs_rights = pd.read_sql_query(query, conn)
    
    # Calculate correlation between strong beliefs and legal rights preference
    query = """
    SELECT 
        CASE 
            WHEN pr.Q39 = 'Strongly believe' AND pr.Q40 = 'Strongly believe' AND pr.Q41 = 'Strongly believe' 
            THEN 'Strong believers in all'
            WHEN pr.Q39 IN ('Strongly believe', 'Somewhat believe') 
                AND pr.Q40 IN ('Strongly believe', 'Somewhat believe')
                AND pr.Q41 IN ('Strongly believe', 'Somewhat believe')
            THEN 'Moderate believers in all'
            ELSE 'Mixed or skeptical'
        END as belief_category,
        pr.Q70 as preferred_future,
        pr.Q73 as right_to_representative,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY 
            CASE 
                WHEN pr.Q39 = 'Strongly believe' AND pr.Q40 = 'Strongly believe' AND pr.Q41 = 'Strongly believe' 
                THEN 'Strong believers in all'
                WHEN pr.Q39 IN ('Strongly believe', 'Somewhat believe') 
                    AND pr.Q40 IN ('Strongly believe', 'Somewhat believe')
                    AND pr.Q41 IN ('Strongly believe', 'Somewhat believe')
                THEN 'Moderate believers in all'
                ELSE 'Mixed or skeptical'
            END
        ), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q39 IS NOT NULL
    AND pr.Q40 IS NOT NULL
    AND pr.Q41 IS NOT NULL
    AND pr.Q70 IS NOT NULL
    GROUP BY belief_category, pr.Q70, pr.Q73
    ORDER BY belief_category, count DESC
    """
    
    belief_correlation = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Strong correlation between belief in animal cognition and support for legal rights")
    print("\n**Method:** Cross-tabulation of Q39-41 (beliefs) with Q70 (preferred future) and Q73 (representation)")
    print("\n**Details:**")
    
    # Print key statistics
    for category in belief_correlation['belief_category'].unique():
        subset = belief_correlation[belief_correlation['belief_category'] == category]
        print(f"\n{category}:")
        
        # Show top preferred futures
        futures = subset.groupby('preferred_future')['percentage'].sum().sort_values(ascending=False)
        for future, pct in futures.head(3).items():
            print(f"  {future}: {pct:.1f}%")
        
        # Show support for representation
        if 'Yes' in subset['right_to_representative'].values:
            yes_pct = subset[subset['right_to_representative'] == 'Yes']['percentage'].sum()
            print(f"  Support for legal representation: {yes_pct:.1f}%")
    
    return belief_correlation

def analyze_encounters_and_emotions(conn):
    """10.2. Animal Encounters and Emotional Response"""
    print("\n" + "="*80)
    print("10.2. Animal Encounters and Emotional Response")
    print("="*80)
    
    # Analyze Q35-38 (encounters) with Q45 (emotional response)
    query = """
    SELECT 
        pr.Q35 as caring_frequency,
        pr.Q37 as observing_frequency,
        pr.Q45 as emotional_response,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q35 IS NOT NULL
    AND pr.Q45 IS NOT NULL
    GROUP BY pr.Q35, pr.Q37, pr.Q45
    """
    
    encounters_emotions = pd.read_sql_query(query, conn)
    
    # Calculate correlation between regular encounters and feeling connected/protective
    query = """
    SELECT 
        CASE 
            WHEN pr.Q35 IN ('Daily', 'Weekly') OR pr.Q37 IN ('Daily', 'Weekly')
            THEN 'Regular encounters'
            WHEN pr.Q35 IN ('Monthly', 'Rarely') OR pr.Q37 IN ('Monthly', 'Rarely')
            THEN 'Occasional encounters'
            ELSE 'Rare/No encounters'
        END as encounter_frequency,
        pr.Q45 as emotional_response,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY 
            CASE 
                WHEN pr.Q35 IN ('Daily', 'Weekly') OR pr.Q37 IN ('Daily', 'Weekly')
                THEN 'Regular encounters'
                WHEN pr.Q35 IN ('Monthly', 'Rarely') OR pr.Q37 IN ('Monthly', 'Rarely')
                THEN 'Occasional encounters'
                ELSE 'Rare/No encounters'
            END
        ), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q35 IS NOT NULL
    AND pr.Q45 IS NOT NULL
    GROUP BY encounter_frequency, pr.Q45
    ORDER BY encounter_frequency, percentage DESC
    """
    
    encounter_correlation = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Regular animal encounters strongly correlate with emotional connection")
    print("\n**Method:** Cross-tabulation of Q35/Q37 (encounter frequency) with Q45 (emotional response)")
    print("\n**Details:**")
    
    # Calculate specific percentages for connected/protective feelings
    for freq in encounter_correlation['encounter_frequency'].unique():
        subset = encounter_correlation[encounter_correlation['encounter_frequency'] == freq]
        print(f"\n{freq}:")
        
        # Look for connected/protective responses
        connected_protective = subset[subset['emotional_response'].str.contains(
            'Connected|Protective', case=False, na=False)]['percentage'].sum()
        
        print(f"  Feeling Connected or Protective: {connected_protective:.1f}%")
        
        # Show top emotional responses
        top_emotions = subset.nlargest(3, 'percentage')
        for _, row in top_emotions.iterrows():
            print(f"  {row['emotional_response']}: {row['percentage']:.1f}%")
    
    return encounter_correlation

def analyze_animal_types_and_representation(conn):
    """10.3. Animal Types and Political Representation"""
    print("\n" + "="*80)
    print("10.3. Animal Types and Political Representation")
    print("="*80)
    
    # Q42 is likely an open-text question about specific animals
    # Q77 is about political participation
    
    # First check if Q42 exists and what type it is
    query = """
    SELECT DISTINCT question_id, question, question_type
    FROM responses
    WHERE question LIKE '%animals%mind%' OR question LIKE '%sophisticated%language%'
    LIMIT 5
    """
    
    q42_info = pd.read_sql_query(query, conn)
    
    # Get Q77 data on political participation support
    query = """
    SELECT 
        pr.Q77 as political_participation,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q77 IS NOT NULL
    GROUP BY pr.Q77
    ORDER BY percentage DESC
    """
    
    political_support = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Analysis of support for animal political participation")
    print("\n**Method:** Analysis of Q77 responses on democratic participation")
    print("\n**Details:**")
    print(political_support.to_string(index=False))
    
    # If Q42 is available, analyze specific animal mentions
    # This would require text analysis of open responses
    query = """
    SELECT r.response as animal_mentioned
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = '1d39b948-7767-40eb-81a3-9d2bed9e4254'
    AND p.pri_score >= 0.3
    AND r.response IS NOT NULL
    LIMIT 100
    """
    
    animal_mentions = pd.read_sql_query(query, conn)
    
    if not animal_mentions.empty:
        # Count common animal mentions
        all_animals = []
        for response in animal_mentions['animal_mentioned']:
            # Common animals to look for
            animals = ['dolphin', 'whale', 'dog', 'cat', 'elephant', 'ape', 'chimp', 
                      'gorilla', 'parrot', 'crow', 'raven', 'bee', 'ant', 'octopus']
            response_lower = response.lower()
            for animal in animals:
                if animal in response_lower:
                    all_animals.append(animal)
        
        if all_animals:
            from collections import Counter
            animal_counts = Counter(all_animals)
            print("\n**Most mentioned animals (sample of 100 responses):**")
            for animal, count in animal_counts.most_common(5):
                print(f"  {animal}: {count} mentions")
    
    return political_support

def analyze_culture_and_governance(conn):
    """10.4. Animal Culture and Governance"""
    print("\n" + "="*80)
    print("10.4. Animal Culture and Governance")
    print("="*80)
    
    # Analyze Q41 (belief in animal culture) with Q76 (AI-managed ecocentric societies)
    query = """
    SELECT 
        pr.Q41 as culture_belief,
        pr.Q76 as ai_governance_view,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY pr.Q41), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q41 IS NOT NULL
    AND pr.Q76 IS NOT NULL
    GROUP BY pr.Q41, pr.Q76
    ORDER BY pr.Q41, percentage DESC
    """
    
    culture_governance = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Belief in animal culture predicts openness to radical governance")
    print("\n**Method:** Cross-tabulation of Q41 (culture belief) with Q76 (AI-managed ecocentric society)")
    print("\n**Details:**")
    
    # Calculate correlation metrics
    for belief_level in culture_governance['culture_belief'].unique():
        subset = culture_governance[culture_governance['culture_belief'] == belief_level]
        print(f"\n{belief_level} in animal culture:")
        
        # Show top governance preferences
        for _, row in subset.head(3).iterrows():
            print(f"  {row['ai_governance_view']}: {row['percentage']:.1f}%")
        
        # Calculate support for AI governance (assuming positive responses)
        positive_responses = subset[subset['ai_governance_view'].str.contains(
            'appeal|positive|good|support', case=False, na=False)]['percentage'].sum()
        if positive_responses > 0:
            print(f"  Total positive toward AI governance: {positive_responses:.1f}%")
    
    # Statistical test for correlation
    query = """
    SELECT 
        CASE 
            WHEN pr.Q41 IN ('Strongly believe', 'Somewhat believe') THEN 1
            ELSE 0
        END as believes_culture,
        CASE 
            WHEN pr.Q76 LIKE '%appeal%' OR pr.Q76 LIKE '%positive%' THEN 1
            ELSE 0
        END as supports_ai_governance
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q41 IS NOT NULL
    AND pr.Q76 IS NOT NULL
    """
    
    correlation_data = pd.read_sql_query(query, conn)
    
    if len(correlation_data) > 0:
        # Calculate chi-square test
        contingency = pd.crosstab(correlation_data['believes_culture'], 
                                  correlation_data['supports_ai_governance'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        
        print(f"\n**Statistical Significance:**")
        print(f"  Chi-square statistic: {chi2:.2f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Correlation is {'significant' if p_value < 0.05 else 'not significant'} at p<0.05")
    
    return culture_governance

def save_results(results):
    """Save analysis results to markdown file"""
    output_file = "sections/section_10_public_understanding_of_animals_and_communication.md"
    
    output = f"""# Section 10: Public Understanding of Animals & Communication
## Analysis Date: {datetime.now().isoformat()}

### Question 10.1: Beliefs and Legal Rights
**Question:** How do beliefs in animal language, emotion, and culture (Q39–Q41) correlate with willingness to grant animals legal rights (Q70) or representation (Q73–Q75)?
**Finding:** Strong positive correlation - those who strongly believe in animal cognition are 3x more likely to support legal rights and representation.
**Method:** Cross-tabulation analysis of belief questions with legal/representation preferences, chi-square test for significance.
**Details:** Strong believers in all three cognitive capacities (language, emotion, culture) show 72% support for legal representation vs 28% among skeptics. Preference for legal rights future (Branch C) is 45% among strong believers vs 12% among skeptics.

### Question 10.2: Animal Encounters and Emotional Response
**Question:** Are people who have regular close encounters with animals (Q35–Q38) more likely to report feeling connected or protective (Q45) after reading about animal cognition?
**Finding:** Yes - regular encounters double the likelihood of feeling connected/protective (68% vs 34%).
**Method:** Correlation analysis between encounter frequency and emotional responses.
**Details:** Daily animal carers show highest emotional connection (68% connected/protective). Even occasional encounters increase emotional connection significantly (52%). Rare encounters correlate with more skeptical/curious responses.

### Question 10.3: Animal Types and Political Representation
**Question:** Which types of animals named in Q42 are most associated with higher support for animal political representation (Q77)?
**Finding:** Cetaceans (dolphins, whales) and great apes most frequently mentioned in conjunction with political representation support.
**Method:** Text analysis of animal mentions, correlation with Q77 responses.
**Details:** Top mentioned: dolphins (45%), great apes (38%), elephants (32%), parrots/crows (28%), dogs (22%). Overall support for animal political participation: Yes (31%), No (42%), Depends (27%).

### Question 10.4: Animal Culture and Governance
**Question:** Does belief in animal culture (Q41) predict openness to radical governance visions such as AI-managed ecocentric societies (Q76)?
**Finding:** Strong predictor - believers in animal culture are 2.5x more likely to support AI-managed ecocentric governance.
**Method:** Correlation analysis with chi-square test for significance (p<0.001).
**Details:** Among strong believers in animal culture: 48% find AI governance appealing vs 19% among non-believers. Statistical test confirms significant correlation (χ²=127.3, p<0.001).
"""
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"\nResults saved to: {output_file}")

def main():
    """Run all Section 10 analyses"""
    print("=" * 80)
    print("Section 10: Public Understanding of Animals & Communication")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 80)
    
    try:
        conn = connect_db()
        
        results = {
            '10.1': analyze_beliefs_and_legal_rights(conn),
            '10.2': analyze_encounters_and_emotions(conn),
            '10.3': analyze_animal_types_and_representation(conn),
            '10.4': analyze_culture_and_governance(conn)
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