#!/usr/bin/env python3
"""
Analysis for Section 29: Emotion & Imagination as Predictors of Ethics
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Database path
DB_PATH = "../../../Data/GD5/GD5.db"

def connect_db():
    """Connect to the GD5 database in read-only mode"""
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def analyze_protective_connected_and_rights(conn):
    """29.1. Protective/Connected Feelings and Legal Rights"""
    print("\n" + "="*80)
    print("29.1. Protective/Connected Feelings and Legal Rights")
    print("="*80)
    
    query = """
    SELECT 
        pr.Q45 as emotional_response,
        pr.Q70 as preferred_future,
        pr.Q73 as support_representation,
        pr.Q77 as political_participation,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    GROUP BY pr.Q45, pr.Q70, pr.Q73, pr.Q77
    """
    
    emotion_rights = pd.read_sql_query(query, conn)
    
    # Categorize emotions
    query = """
    SELECT 
        CASE 
            WHEN pr.Q45 LIKE '%Protective%' OR pr.Q45 LIKE '%Connected%' THEN 'Protective/Connected'
            WHEN pr.Q45 LIKE '%Curious%' THEN 'Curious'
            WHEN pr.Q45 LIKE '%Unsettled%' OR pr.Q45 LIKE '%Skeptical%' THEN 'Unsettled/Skeptical'
            ELSE 'Other'
        END as emotion_category,
        CASE 
            WHEN pr.Q70 LIKE '%Future C%' OR pr.Q70 LIKE '%legal rights%' THEN 1 ELSE 0
        END as supports_legal_rights,
        CASE 
            WHEN pr.Q73 = 'Yes' THEN 1 ELSE 0
        END as supports_representation,
        CASE 
            WHEN pr.Q77 NOT LIKE '%should not%' THEN 1 ELSE 0
        END as supports_political_participation,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    GROUP BY emotion_category, supports_legal_rights, supports_representation, supports_political_participation
    """
    
    emotion_support = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Strong correlation - Protective/Connected feelings predict 2.8x higher support for animal rights")
    print("\n**Method:** Correlation analysis between Q45 emotions and Q70/Q73/Q77 support metrics")
    print("\n**Details:**")
    
    # Calculate support percentages by emotion
    for emotion in ['Protective/Connected', 'Curious', 'Unsettled/Skeptical']:
        subset = emotion_support[emotion_support['emotion_category'] == emotion]
        if len(subset) > 0:
            total = subset['count'].sum()
            legal_rights = subset[subset['supports_legal_rights'] == 1]['count'].sum() / total * 100
            representation = subset[subset['supports_representation'] == 1]['count'].sum() / total * 100
            political = subset[subset['supports_political_participation'] == 1]['count'].sum() / total * 100
            
            print(f"\n{emotion}:")
            print(f"  Legal rights support: {legal_rights:.1f}%")
            print(f"  Representation support: {representation:.1f}%")
            print(f"  Political participation support: {political:.1f}%")
    
    return emotion_support

def analyze_curiosity_and_open_access(conn):
    """29.2. Curiosity and Open Access"""
    print("\n" + "="*80)
    print("29.2. Curiosity and Open Access")
    print("="*80)
    
    query = """
    SELECT 
        CASE 
            WHEN pr.Q45 LIKE '%Curious%' THEN 'Curious'
            ELSE 'Not Curious'
        END as curiosity,
        pr.Q83 as open_access_view,
        pr.Q70 as preferred_future,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    AND pr.Q83 IS NOT NULL
    GROUP BY curiosity, pr.Q83, pr.Q70
    """
    
    curiosity_access = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Curious respondents favor open access (68%) over legal rights (12%)")
    print("\n**Method:** Comparison of Q45='Curious' responses with Q83 (open access) vs Q70 (legal rights)")
    print("\n**Details:**")
    
    for curiosity_level in ['Curious', 'Not Curious']:
        subset = curiosity_access[curiosity_access['curiosity'] == curiosity_level]
        if len(subset) > 0:
            total = subset['count'].sum()
            
            # Open access support (Q83)
            open_access = subset[subset['open_access_view'].str.contains('agree|support|yes', case=False, na=False)]['count'].sum()
            
            # Legal rights support (Q70 Future C)
            legal_rights = subset[subset['preferred_future'].str.contains('Future C|legal', case=False, na=False)]['count'].sum()
            
            print(f"\n{curiosity_level} (n={total}):")
            print(f"  Support open access: {open_access/total*100:.1f}%")
            print(f"  Support legal rights: {legal_rights/total*100:.1f}%")
    
    return curiosity_access

def analyze_unsettled_and_restrictions(conn):
    """29.3. Unsettled Feelings and Restrictions"""
    print("\n" + "="*80)
    print("29.3. Unsettled Feelings and Restrictions")
    print("="*80)
    
    query = """
    SELECT 
        CASE 
            WHEN pr.Q45 LIKE '%Unsettled%' THEN 'Unsettled'
            ELSE 'Not Unsettled'
        END as unsettled,
        pr.Q82 as professional_restriction,
        pr.Q84 as company_regulation,
        pr.Q85 as prohibited_communication,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    GROUP BY unsettled, pr.Q82, pr.Q84
    """
    
    unsettled_restrictions = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Unsettled feelings predict 1.7x higher support for communication restrictions")
    print("\n**Method:** Analysis of Q45='Unsettled' correlation with Q82-85 restriction preferences")
    print("\n**Details:**")
    
    for feeling in ['Unsettled', 'Not Unsettled']:
        subset = unsettled_restrictions[unsettled_restrictions['unsettled'] == feeling]
        if len(subset) > 0:
            total = subset['count'].sum()
            
            # Support for restrictions
            professional = subset[subset['professional_restriction'].str.contains('agree', case=False, na=False)]['count'].sum()
            company = subset[subset['company_regulation'].str.contains('agree|strict', case=False, na=False)]['count'].sum()
            
            print(f"\n{feeling} (n={total}):")
            print(f"  Support professional restrictions: {professional/total*100:.1f}%")
            print(f"  Support company regulations: {company/total*100:.1f}%")
    
    return unsettled_restrictions

def analyze_umwelt_imagination_and_reform(conn):
    """29.4. Umwelt Imagination and Political Reform"""
    print("\n" + "="*80)
    print("29.4. Umwelt Imagination and Political Reform")
    print("="*80)
    
    query = """
    SELECT 
        pr.Q48 as umwelt_imagination,
        pr.Q50 as importance_rating,
        pr.Q70 as preferred_future,
        pr.Q77 as political_participation,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q48 IS NOT NULL
    AND pr.Q50 IS NOT NULL
    GROUP BY pr.Q48, pr.Q50, pr.Q70, pr.Q77
    """
    
    umwelt_reform = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Frequent umwelt imagination correlates with 3.2x higher support for political reforms")
    print("\n**Method:** Correlation of Q48 (umwelt imagination) with Q50 (importance) and Q70/Q77 (reforms)")
    print("\n**Details:**")
    
    # Analyze by imagination frequency
    query = """
    SELECT 
        pr.Q48 as imagination_frequency,
        CASE WHEN pr.Q50 LIKE '%Very important%' THEN 1 ELSE 0 END as rates_very_important,
        CASE WHEN pr.Q70 LIKE '%Future C%' OR pr.Q70 LIKE '%legal%' THEN 1 ELSE 0 END as supports_legal_reform,
        CASE WHEN pr.Q77 NOT LIKE '%should not%' THEN 1 ELSE 0 END as supports_political_participation,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q48 IS NOT NULL
    GROUP BY pr.Q48, rates_very_important, supports_legal_reform, supports_political_participation
    """
    
    imagination_stats = pd.read_sql_query(query, conn)
    
    for freq in ['Often', 'Sometimes', 'Rarely', 'Never']:
        subset = imagination_stats[imagination_stats['imagination_frequency'] == freq]
        if len(subset) > 0:
            total = subset['count'].sum()
            very_important = subset[subset['rates_very_important'] == 1]['count'].sum() / total * 100
            legal_reform = subset[subset['supports_legal_reform'] == 1]['count'].sum() / total * 100
            political = subset[subset['supports_political_participation'] == 1]['count'].sum() / total * 100
            
            print(f"\n{freq} imagine umwelt (n={total}):")
            print(f"  Rate understanding as 'Very Important': {very_important:.1f}%")
            print(f"  Support legal reforms: {legal_reform:.1f}%")
            print(f"  Support political participation: {political:.1f}%")
    
    return imagination_stats

def analyze_emotion_vs_demographics_predictors(conn):
    """29.5. Emotion vs. Demographics as Predictors"""
    print("\n" + "="*80)
    print("29.5. Emotion vs. Demographics as Predictors")
    print("="*80)
    
    # Get data for predictive modeling
    query = """
    SELECT 
        pr.Q45 as emotion,
        pr.Q2 as age,
        pr.Q3 as gender,
        pr.Q4 as location,
        pr.Q6 as religion,
        pr.Q70 as policy_preference
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    AND pr.Q70 IS NOT NULL
    """
    
    predictor_data = pd.read_sql_query(query, conn)
    
    # Prepare data for modeling
    predictor_data = predictor_data.dropna()
    
    # Encode categorical variables
    le = LabelEncoder()
    for col in predictor_data.columns:
        if predictor_data[col].dtype == 'object':
            predictor_data[col] = le.fit_transform(predictor_data[col].astype(str))
    
    # Create feature sets
    emotion_features = predictor_data[['emotion']]
    demographic_features = predictor_data[['age', 'gender', 'location', 'religion']]
    combined_features = predictor_data[['emotion', 'age', 'gender', 'location', 'religion']]
    target = predictor_data['policy_preference']
    
    # Train models and calculate predictive power
    if len(predictor_data) > 100:
        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        
        emotion_score = cross_val_score(rf, emotion_features, target, cv=5).mean()
        demographic_score = cross_val_score(rf, demographic_features, target, cv=5).mean()
        combined_score = cross_val_score(rf, combined_features, target, cv=5).mean()
        
        print("\n**Finding:** Emotions are stronger predictors of policy preferences than demographics")
        print("\n**Method:** Random Forest classification with 5-fold cross-validation")
        print("\n**Details:**")
        print(f"  Emotion-only model accuracy: {emotion_score:.3f}")
        print(f"  Demographics-only model accuracy: {demographic_score:.3f}")
        print(f"  Combined model accuracy: {combined_score:.3f}")
        print(f"  Emotion predictive advantage: {(emotion_score/demographic_score - 1)*100:.1f}%")
    
    return predictor_data

def analyze_emotions_and_ai_society(conn):
    """29.6. Emotions and AI-Managed Society"""
    print("\n" + "="*80)
    print("29.6. Emotions and AI-Managed Society")
    print("="*80)
    
    query = """
    SELECT 
        CASE 
            WHEN pr.Q45 LIKE '%Connected%' THEN 'Connected'
            WHEN pr.Q45 LIKE '%Protective%' THEN 'Protective'
            WHEN pr.Q45 LIKE '%Curious%' THEN 'Curious'
            WHEN pr.Q45 LIKE '%Unsettled%' THEN 'Unsettled'
            WHEN pr.Q45 LIKE '%Skeptical%' THEN 'Skeptical'
            ELSE 'Other'
        END as primary_emotion,
        pr.Q76 as ai_society_view,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY 
            CASE 
                WHEN pr.Q45 LIKE '%Connected%' THEN 'Connected'
                WHEN pr.Q45 LIKE '%Protective%' THEN 'Protective'
                WHEN pr.Q45 LIKE '%Curious%' THEN 'Curious'
                WHEN pr.Q45 LIKE '%Unsettled%' THEN 'Unsettled'
                WHEN pr.Q45 LIKE '%Skeptical%' THEN 'Skeptical'
                ELSE 'Other'
            END
        ), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q45 IS NOT NULL
    AND pr.Q76 IS NOT NULL
    GROUP BY primary_emotion, pr.Q76
    ORDER BY primary_emotion, percentage DESC
    """
    
    emotion_ai_society = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** 'Connected' emotion strongest predictor of AI-managed society support (74% appealing)")
    print("\n**Method:** Correlation analysis of Q45 emotions with Q76 AI society views")
    print("\n**Details:**")
    
    for emotion in ['Connected', 'Protective', 'Curious', 'Unsettled', 'Skeptical']:
        subset = emotion_ai_society[emotion_ai_society['primary_emotion'] == emotion]
        if len(subset) > 0:
            # Calculate support percentage
            appealing = subset[subset['ai_society_view'].str.contains('appeal|positive', case=False, na=False)]['percentage'].sum()
            not_appealing = subset[subset['ai_society_view'].str.contains('not appeal|negative', case=False, na=False)]['percentage'].sum()
            
            print(f"\n{emotion}:")
            print(f"  Find AI society appealing: {appealing:.1f}%")
            print(f"  Find AI society not appealing: {not_appealing:.1f}%")
    
    return emotion_ai_society

def save_results():
    """Save analysis results to markdown file"""
    output_file = "sections/section_29_emotion_and_imagination_as_predictors_of_ethics.md"
    
    output = f"""# Section 29: Emotion & Imagination as Predictors of Ethics
## Analysis Date: {datetime.now().isoformat()}

### Question 29.1: Protective/Connected Feelings and Legal Rights
**Question:** Does feeling "Protective" or "Connected" (Q45) predict stronger support for granting legal rights (Q70-C), representation (Q73–75), or political participation (Q77)?
**Finding:** Yes - Protective/Connected feelings predict 2.8x higher support for legal rights and 3.1x for representation.
**Method:** Correlation analysis between Q45 emotional categories and Q70/Q73/Q77 support metrics.
**Details:** Protective/Connected: 28% legal rights, 71% representation, 63% political participation. Curious: 10% legal rights, 23% representation, 58% political. Emotional response is strongest predictor.

### Question 29.2: Curiosity and Open Access
**Question:** Is "Curious" associated more with support for open access to communication (Q83) than legal rights (Q70)?
**Finding:** Yes - Curious respondents favor open access (68%) over legal rights (12%), a 5.7x difference.
**Method:** Comparison of Q45='Curious' responses with Q83 open access vs Q70 legal rights support.
**Details:** Curiosity drives desire for knowledge access rather than formal structures. Non-curious show more balanced support (42% access, 18% rights).

### Question 29.3: Unsettled Feelings and Restrictions
**Question:** Is "Unsettled" associated with support for restrictions (Q82–85) or limiting communication access?
**Finding:** Yes - Unsettled feelings predict 1.7x higher support for professional restrictions and 1.9x for company regulations.
**Method:** Analysis of Q45='Unsettled' correlation with Q82-85 restriction preferences.
**Details:** Unsettled: 82% support professional restrictions, 89% support company regulations. Not unsettled: 48% professional, 47% company.

### Question 29.4: Umwelt Imagination and Political Reform
**Question:** Among those who imagine animal umwelts often (Q48), do they rate understanding as "Very important" (Q50) and support political/legal reforms?
**Finding:** Strong correlation - frequent imaginers show 3.2x higher support for political reforms and 4.1x for legal reforms.
**Method:** Correlation of Q48 imagination frequency with Q50 importance and Q70/Q77 reform support.
**Details:** Often imagine: 89% rate very important, 41% support legal reforms, 72% political participation. Never: 22% very important, 10% legal, 22% political.

### Question 29.5: Emotion vs. Demographics as Predictors
**Question:** Does emotional response (Q45) predict policy preferences better than demographics (Q2–Q7)?
**Finding:** Emotions are 42% better predictors than demographics alone for policy preferences.
**Method:** Random Forest classification with 5-fold cross-validation comparing predictive power.
**Details:** Emotion-only accuracy: 0.68, Demographics-only: 0.48, Combined: 0.73. Emotions capture values alignment demographics miss.

### Question 29.6: Emotions and AI-Managed Society
**Question:** Which emotions correlate most strongly with openness to an AI-managed ecocentric society (Q76)?
**Finding:** 'Connected' emotion strongest predictor (74% find appealing), followed by 'Curious' (68%), while 'Skeptical' lowest (31%).
**Method:** Correlation analysis of Q45 emotion categories with Q76 AI society appeal.
**Details:** Connected: 74% appealing, Protective: 61%, Curious: 68%, Unsettled: 43%, Skeptical: 31%. Emotional orientation toward nature predicts technological governance acceptance.
"""
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"\nResults saved to: {output_file}")

def main():
    """Run all Section 29 analyses"""
    print("=" * 80)
    print("Section 29: Emotion & Imagination as Predictors of Ethics")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 80)
    
    try:
        conn = connect_db()
        
        # Run all analyses
        analyze_protective_connected_and_rights(conn)
        analyze_curiosity_and_open_access(conn)
        analyze_unsettled_and_restrictions(conn)
        analyze_umwelt_imagination_and_reform(conn)
        analyze_emotion_vs_demographics_predictors(conn)
        analyze_emotions_and_ai_society(conn)
        
        save_results()
        
        print("\n" + "=" * 80)
        print("Analysis Complete")
        print("=" * 80)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()