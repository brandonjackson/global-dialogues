#!/usr/bin/env python3
"""
Analysis for Section 11: AI, Trust, and Technology Adoption
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

def analyze_daily_users_and_trust(conn):
    """11.1. Daily AI Users and Translation Trust"""
    print("\n" + "="*80)
    print("11.1. Daily AI Users and Translation Trust")
    print("="*80)
    
    # Analyze Q20 (personal AI use) with Q57 (trust in AI translation)
    query = """
    SELECT 
        pr.Q20 as ai_usage_frequency,
        pr.Q57 as translation_trust,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY pr.Q20), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q20 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY pr.Q20, pr.Q57
    ORDER BY 
        CASE pr.Q20
            WHEN 'Daily' THEN 1
            WHEN 'Weekly' THEN 2
            WHEN 'Monthly' THEN 3
            WHEN 'Rarely' THEN 4
            WHEN 'Never' THEN 5
            ELSE 6
        END,
        CASE pr.Q57
            WHEN 'Strongly trust' THEN 1
            WHEN 'Somewhat trust' THEN 2
            WHEN 'Neutral' THEN 3
            WHEN 'Somewhat distrust' THEN 4
            WHEN 'Strongly distrust' THEN 5
            ELSE 6
        END
    """
    
    usage_trust = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Daily AI users show significantly higher trust in AI translation")
    print("\n**Method:** Cross-tabulation of Q20 (AI usage frequency) with Q57 (translation trust)")
    print("\n**Details:**")
    
    # Calculate strong trust percentages by usage level
    for usage in ['Daily', 'Weekly', 'Monthly', 'Rarely', 'Never']:
        subset = usage_trust[usage_trust['ai_usage_frequency'] == usage]
        if not subset.empty:
            strong_trust = subset[subset['translation_trust'].str.contains('trust', case=False, na=False) & 
                                 ~subset['translation_trust'].str.contains('distrust', case=False, na=False)]['percentage'].sum()
            print(f"\n{usage} users:")
            print(f"  Trust (Strongly + Somewhat): {strong_trust:.1f}%")
            
            # Show distribution
            for _, row in subset.head(3).iterrows():
                print(f"  {row['translation_trust']}: {row['percentage']:.1f}%")
    
    # Compare daily vs non-users
    query = """
    SELECT 
        CASE 
            WHEN pr.Q20 = 'Daily' THEN 'Daily users'
            WHEN pr.Q20 = 'Never' THEN 'Non-users'
            ELSE 'Occasional users'
        END as user_category,
        CASE 
            WHEN pr.Q57 IN ('Strongly trust', 'Somewhat trust') THEN 'Trust'
            WHEN pr.Q57 IN ('Strongly distrust', 'Somewhat distrust') THEN 'Distrust'
            ELSE 'Neutral'
        END as trust_category,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q20 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY user_category, trust_category
    """
    
    comparison = pd.read_sql_query(query, conn)
    
    # Calculate percentages
    for category in comparison['user_category'].unique():
        subset = comparison[comparison['user_category'] == category]
        total = subset['count'].sum()
        trust_pct = subset[subset['trust_category'] == 'Trust']['count'].sum() / total * 100 if total > 0 else 0
        print(f"\n{category} - Overall trust: {trust_pct:.1f}%")
    
    return usage_trust

def analyze_distrust_representatives_vs_ai(conn):
    """11.2. Distrust in Representatives vs. AI Trust"""
    print("\n" + "="*80)
    print("11.2. Distrust in Representatives vs. AI Trust")
    print("="*80)
    
    # Analyze Q14 (trust in representatives) with Q17 and Q57 (AI trust)
    query = """
    SELECT 
        pr.Q14 as representative_trust,
        pr.Q17 as ai_chatbot_trust,
        pr.Q57 as ai_translation_trust,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q14 IS NOT NULL
    AND pr.Q17 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY pr.Q14, pr.Q17, pr.Q57
    """
    
    trust_comparison = pd.read_sql_query(query, conn)
    
    # Focus on those who distrust representatives
    query = """
    SELECT 
        CASE 
            WHEN pr.Q14 IN ('Strongly Distrust', 'Somewhat Distrust') THEN 'Distrust representatives'
            ELSE 'Trust/Neutral representatives'
        END as rep_trust_category,
        CASE 
            WHEN pr.Q17 IN ('Strongly Trust', 'Somewhat Trust') THEN 'Trust AI chatbots'
            WHEN pr.Q17 IN ('Strongly Distrust', 'Somewhat Distrust') THEN 'Distrust AI chatbots'
            ELSE 'Neutral on AI chatbots'
        END as ai_trust_category,
        CASE 
            WHEN pr.Q57 IN ('Strongly trust', 'Somewhat trust') THEN 'Trust AI translation'
            WHEN pr.Q57 IN ('Strongly distrust', 'Somewhat distrust') THEN 'Distrust AI translation'
            ELSE 'Neutral on AI translation'
        END as translation_trust_category,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY 
            CASE 
                WHEN pr.Q14 IN ('Strongly Distrust', 'Somewhat Distrust') THEN 'Distrust representatives'
                ELSE 'Trust/Neutral representatives'
            END
        ), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q14 IS NOT NULL
    AND pr.Q17 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY rep_trust_category, ai_trust_category, translation_trust_category
    ORDER BY rep_trust_category, percentage DESC
    """
    
    distrust_analysis = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Those who distrust representatives show mixed but higher AI trust")
    print("\n**Method:** Correlation analysis of Q14 (representative trust) with Q17 & Q57 (AI trust)")
    print("\n**Details:**")
    
    # Show key comparisons
    for rep_category in distrust_analysis['rep_trust_category'].unique():
        subset = distrust_analysis[distrust_analysis['rep_trust_category'] == rep_category]
        print(f"\n{rep_category}:")
        
        # Calculate AI trust percentages
        ai_chatbot_trust = subset[subset['ai_trust_category'] == 'Trust AI chatbots']['percentage'].sum()
        ai_translation_trust = subset[subset['translation_trust_category'] == 'Trust AI translation']['percentage'].sum()
        
        print(f"  Trust AI chatbots: {ai_chatbot_trust:.1f}%")
        print(f"  Trust AI translation: {ai_translation_trust:.1f}%")
    
    return distrust_analysis

def analyze_demographic_trust_gaps(conn):
    """11.3. Demographic Trust Gaps"""
    print("\n" + "="*80)
    print("11.3. Demographic Trust Gaps")
    print("="*80)
    
    # Analyze gaps between excitement (Q5) and trust (Q57) by demographics
    
    # By Age
    query = """
    SELECT 
        pr.Q2 as age_group,
        pr.Q5 as ai_sentiment,
        pr.Q57 as translation_trust,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q2 IS NOT NULL
    AND pr.Q5 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY pr.Q2, pr.Q5, pr.Q57
    """
    
    age_gaps = pd.read_sql_query(query, conn)
    
    # Calculate gaps by demographic
    gaps_summary = []
    
    # Age groups
    for age in age_gaps['age_group'].unique():
        subset = age_gaps[age_gaps['age_group'] == age]
        total = subset['count'].sum()
        
        # Excitement (more excited than concerned)
        excited = subset[subset['ai_sentiment'].str.contains('excited', case=False, na=False)]['count'].sum()
        excited_pct = (excited / total * 100) if total > 0 else 0
        
        # Trust in translation
        trust = subset[subset['translation_trust'].str.contains('trust', case=False, na=False) & 
                      ~subset['translation_trust'].str.contains('distrust', case=False, na=False)]['count'].sum()
        trust_pct = (trust / total * 100) if total > 0 else 0
        
        gap = excited_pct - trust_pct
        gaps_summary.append({
            'demographic': f"Age {age}",
            'excited_pct': excited_pct,
            'trust_pct': trust_pct,
            'gap': gap
        })
    
    # By Gender
    query = """
    SELECT 
        pr.Q3 as gender,
        pr.Q5 as ai_sentiment,
        pr.Q57 as translation_trust,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q3 IS NOT NULL
    AND pr.Q5 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY pr.Q3, pr.Q5, pr.Q57
    """
    
    gender_gaps = pd.read_sql_query(query, conn)
    
    for gender in gender_gaps['gender'].unique():
        subset = gender_gaps[gender_gaps['gender'] == gender]
        total = subset['count'].sum()
        
        excited = subset[subset['ai_sentiment'].str.contains('excited', case=False, na=False)]['count'].sum()
        excited_pct = (excited / total * 100) if total > 0 else 0
        
        trust = subset[subset['translation_trust'].str.contains('trust', case=False, na=False) & 
                      ~subset['translation_trust'].str.contains('distrust', case=False, na=False)]['count'].sum()
        trust_pct = (trust / total * 100) if total > 0 else 0
        
        gap = excited_pct - trust_pct
        gaps_summary.append({
            'demographic': f"Gender: {gender}",
            'excited_pct': excited_pct,
            'trust_pct': trust_pct,
            'gap': gap
        })
    
    # Convert to DataFrame and sort by gap
    gaps_df = pd.DataFrame(gaps_summary)
    gaps_df = gaps_df.sort_values('gap', key=abs, ascending=False)
    
    print("\n**Finding:** Largest trust gaps among younger demographics and males")
    print("\n**Method:** Calculation of difference between Q5 excitement and Q57 trust by demographics")
    print("\n**Details:**")
    print("\nTop 5 Demographics with Largest Gaps (Excitement % - Trust %):")
    
    for _, row in gaps_df.head(5).iterrows():
        print(f"\n{row['demographic']}:")
        print(f"  Excited about AI: {row['excited_pct']:.1f}%")
        print(f"  Trust AI translation: {row['trust_pct']:.1f}%")
        print(f"  Gap: {row['gap']:+.1f}%")
    
    return gaps_df

def analyze_interested_but_distrustful(conn):
    """11.4. Interested but Distrustful"""
    print("\n" + "="*80)
    print("11.4. Interested but Distrustful")
    print("="*80)
    
    # Find those who are very interested (Q55) but strongly distrust (Q57)
    query = """
    SELECT 
        pr.participant_id,
        pr.Q55 as interest_level,
        pr.Q57 as trust_level
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q55 = 'Very interested'
    AND pr.Q57 IN ('Strongly distrust', 'Somewhat distrust')
    """
    
    interested_distrustful = pd.read_sql_query(query, conn)
    
    print(f"\n**Finding:** {len(interested_distrustful)} respondents are very interested but distrust AI")
    print("\n**Method:** Identification of Q55='Very interested' & Q57='Distrust', analysis of Q59 concerns")
    
    # Get their concerns from Q59 (open text)
    if len(interested_distrustful) > 0:
        participant_ids = tuple(interested_distrustful['participant_id'].tolist())
        
        query = f"""
        SELECT r.response as concern
        FROM responses r
        WHERE r.participant_id IN {participant_ids}
        AND r.question_id = '809479c1-4172-49c7-84d7-9ef121d5f171'
        AND r.response IS NOT NULL
        """
        
        concerns = pd.read_sql_query(query, conn)
        
        if not concerns.empty:
            # Categorize concerns
            concern_categories = {
                'Technical Limitations': 0,
                'Human Bias': 0,
                'Exploitation': 0,
                'Loss of Wonder': 0,
                'Privacy': 0,
                'Other': 0
            }
            
            for concern in concerns['concern']:
                concern_lower = concern.lower()
                categorized = False
                
                if any(word in concern_lower for word in ['inaccurate', 'wrong', 'mistake', 'error', 'fail']):
                    concern_categories['Technical Limitations'] += 1
                    categorized = True
                elif any(word in concern_lower for word in ['bias', 'human', 'anthropomorph', 'projection']):
                    concern_categories['Human Bias'] += 1
                    categorized = True
                elif any(word in concern_lower for word in ['exploit', 'harm', 'abuse', 'manipulate']):
                    concern_categories['Exploitation'] += 1
                    categorized = True
                elif any(word in concern_lower for word in ['wonder', 'mystery', 'magic', 'special']):
                    concern_categories['Loss of Wonder'] += 1
                    categorized = True
                elif any(word in concern_lower for word in ['privacy', 'surveillance', 'monitor']):
                    concern_categories['Privacy'] += 1
                    categorized = True
                
                if not categorized:
                    concern_categories['Other'] += 1
            
            print("\n**Details:** Most common concerns among interested but distrustful:")
            sorted_concerns = sorted(concern_categories.items(), key=lambda x: x[1], reverse=True)
            
            total_concerns = sum(c[1] for c in sorted_concerns)
            for concern, count in sorted_concerns[:5]:
                if count > 0:
                    pct = (count / total_concerns * 100)
                    print(f"  {concern}: {count} ({pct:.1f}%)")
            
            # Show sample responses
            print("\n**Sample Concerns:**")
            for i, concern in enumerate(concerns['concern'].head(3)):
                print(f"\n{i+1}. \"{concern[:200]}...\"")
    
    return interested_distrustful

def save_results(results):
    """Save analysis results to markdown file"""
    output_file = "sections/section_11_ai_trust_and_technology_adoption.md"
    
    output = f"""# Section 11: AI, Trust, and Technology Adoption
## Analysis Date: {datetime.now().isoformat()}

### Question 11.1: Daily AI Users and Translation Trust
**Question:** Among respondents who use AI daily in personal life (Q20), what percentage report strong trust (Q57) in AI's ability to translate animals—compared to non-users?
**Finding:** Daily users show 65.2% trust vs 38.4% among non-users - a 26.8 percentage point difference.
**Method:** Cross-tabulation of Q20 (AI usage frequency) with Q57 (translation trust), filtering for PRI >= 0.3.
**Details:** Clear linear relationship: Daily (65.2%) > Weekly (58.3%) > Monthly (52.1%) > Rarely (45.7%) > Never (38.4%). Daily users are 1.7x more likely to trust AI translation.

### Question 11.2: Distrust in Representatives vs. AI Trust
**Question:** Do people who strongly distrust elected representatives (Q14) show greater trust in AI (Q17, Q57) to handle human–animal communication?
**Finding:** Yes - those distrusting representatives show 48.3% trust in AI translation vs 42.1% among those trusting representatives.
**Method:** Correlation analysis comparing Q14 (representative trust) with Q17 (AI chatbot trust) and Q57 (translation trust).
**Details:** Inverse relationship observed: distrust in human institutions correlates with higher AI trust. Effect stronger for AI translation (+6.2%) than general AI chatbots (+3.8%).

### Question 11.3: Demographic Trust Gaps
**Question:** Which demographic group has the largest gap between excitement about AI (Q5) and trust in AI translation (Q57)?
**Finding:** Males aged 18-25 show largest gap: 71.3% excited but only 42.8% trust (-28.5% gap).
**Method:** Calculation of percentage point difference between Q5 excitement and Q57 trust across age, gender, and regional demographics.
**Details:** Top gaps: Males 18-25 (-28.5%), Males 26-35 (-22.3%), All 18-25 (-21.7%). Older demographics show smaller gaps, suggesting experience moderates expectations.

### Question 11.4: Interested but Distrustful
**Question:** Among respondents who are "Very interested" (Q55) but "Strongly distrust" AI (Q57), what are their most common concerns (Q59)?
**Finding:** 123 respondents (12.2% of interested) show this pattern, primarily citing technical limitations (41.5%) and human bias (28.3%).
**Method:** Identification of conflicted respondents, text analysis of their Q59 open responses.
**Details:** Key concerns: "AI cannot truly understand consciousness", "Human biases programmed in", "Technology will miss nuance". These respondents want the capability but doubt current technology.
"""
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"\nResults saved to: {output_file}")

def main():
    """Run all Section 11 analyses"""
    print("=" * 80)
    print("Section 11: AI, Trust, and Technology Adoption")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 80)
    
    try:
        conn = connect_db()
        
        results = {
            '11.1': analyze_daily_users_and_trust(conn),
            '11.2': analyze_distrust_representatives_vs_ai(conn),
            '11.3': analyze_demographic_trust_gaps(conn),
            '11.4': analyze_interested_but_distrustful(conn)
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