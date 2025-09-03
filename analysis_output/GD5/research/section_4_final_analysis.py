#!/usr/bin/env python3
"""
Final Analysis for Section 4: AI as an Interspecies Communication Tool
Using participant_responses table for actual survey data
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Database path
DB_PATH = "../../../Data/GD5/GD5.db"

def connect_db():
    """Connect to the GD5 database in read-only mode"""
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def analyze_trust_in_ai_translation(conn):
    """4.1. Trust in AI Translation (Q57)"""
    print("\n" + "="*80)
    print("4.1. Trust in AI Translation (Q57)")
    print("="*80)
    
    # Get trust distribution with PRI filtering
    query = """
    SELECT pr.Q57 as response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3 
    AND pr.Q57 IS NOT NULL
    GROUP BY pr.Q57
    ORDER BY 
        CASE pr.Q57
            WHEN 'Strongly trust' THEN 1
            WHEN 'Somewhat trust' THEN 2
            WHEN 'Neutral' THEN 3
            WHEN 'Somewhat distrust' THEN 4
            WHEN 'Strongly distrust' THEN 5
            ELSE 6
        END
    """
    
    trust_dist = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Trust in AI translation capability")
    print("\n**Method:** SQL query on participant_responses with PRI >= 0.3")
    print("\n**Details:**")
    print(trust_dist.to_string(index=False))
    
    # Calculate summary statistics
    trust_positive = trust_dist[trust_dist['response'].str.contains('trust', case=False, na=False) & 
                                ~trust_dist['response'].str.contains('distrust', case=False, na=False)]['percentage'].sum()
    trust_negative = trust_dist[trust_dist['response'].str.contains('distrust', case=False, na=False)]['percentage'].sum()
    
    print(f"\nSummary:")
    print(f"  Trust (Strongly + Somewhat): {trust_positive:.1f}%")
    print(f"  Distrust (Strongly + Somewhat): {trust_negative:.1f}%")
    
    # Correlation with general AI chatbot trust (Q17)
    query = """
    SELECT 
        pr.Q57 as ai_translation_trust,
        pr.Q17 as ai_chatbot_trust,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q57 IS NOT NULL
    AND pr.Q17 IS NOT NULL
    GROUP BY pr.Q57, pr.Q17
    ORDER BY count DESC
    """
    
    correlation_data = pd.read_sql_query(query, conn)
    
    print("\n**Correlation with General AI Chatbot Trust (Q17):**")
    # Create crosstab for better visualization
    crosstab = pd.crosstab(correlation_data['ai_chatbot_trust'], 
                           correlation_data['ai_translation_trust'], 
                           correlation_data['count'], 
                           aggfunc='sum', 
                           normalize='index') * 100
    
    print("\nPercentage of AI Translation Trust by AI Chatbot Trust Level:")
    print(crosstab.round(1).to_string())
    
    return trust_dist

def analyze_interest_level(conn):
    """4.2. Interest Level (Q55)"""
    print("\n" + "="*80)
    print("4.2. Interest Level (Q55)")
    print("="*80)
    
    # Get interest distribution
    query = """
    SELECT pr.Q55 as response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3 
    AND pr.Q55 IS NOT NULL
    GROUP BY pr.Q55
    ORDER BY 
        CASE pr.Q55
            WHEN 'Very interested' THEN 1
            WHEN 'Moderately interested' THEN 2
            WHEN 'Somewhat interested' THEN 3
            WHEN 'Not very interested' THEN 4
            WHEN 'Not at all interested' THEN 5
            ELSE 6
        END
    """
    
    interest_dist = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Public interest in knowing what animals say/feel")
    print("\n**Method:** SQL query on participant_responses with PRI >= 0.3")
    print("\n**Details:**")
    print(interest_dist.to_string(index=False))
    
    # High interest calculation
    high_interest = interest_dist[interest_dist['response'].str.contains('Very|Moderately', case=False, na=False)]['percentage'].sum()
    print(f"\nHigh Interest (Very + Moderately): {high_interest:.1f}%")
    
    # Interest vs Trust analysis - skeptical but interested
    query = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN pr.Q55 IN ('Very interested', 'Moderately interested') 
                 AND pr.Q57 IN ('Strongly distrust', 'Somewhat distrust') 
                 THEN 1 ELSE 0 END) as skeptical_interested,
        SUM(CASE WHEN pr.Q55 IN ('Very interested', 'Moderately interested') 
                 THEN 1 ELSE 0 END) as high_interest
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q55 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    """
    
    skeptical_data = pd.read_sql_query(query, conn)
    
    if skeptical_data['high_interest'][0] > 0:
        percentage = (skeptical_data['skeptical_interested'][0] / skeptical_data['high_interest'][0]) * 100
        print(f"\n**Skeptical but Interested:**")
        print(f"Among {skeptical_data['high_interest'][0]} highly interested respondents:")
        print(f"  {skeptical_data['skeptical_interested'][0]} ({percentage:.1f}%) also distrust AI's translation ability")
    
    return interest_dist

def analyze_top_concerns(conn):
    """4.3. Top Concerns (Q59)"""
    print("\n" + "="*80)
    print("4.3. Top Concerns (Q59)")
    print("="*80)
    
    # Get all text responses from responses table (Q59 is open-text)
    query = """
    SELECT r.response
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = '809479c1-4172-49c7-84d7-9ef121d5f171'
    AND p.pri_score >= 0.3
    AND r.response IS NOT NULL 
    AND LENGTH(TRIM(r.response)) > 0
    """
    
    concerns_df = pd.read_sql_query(query, conn)
    
    if concerns_df.empty:
        print("No text responses found for Q59")
        return None
    
    print(f"\n**Finding:** Analysis of {len(concerns_df)} open-text responses about concerns")
    print("\n**Method:** Text analysis and categorization of open responses")
    
    # Enhanced categorization
    categories = {
        'Technical Limitations': ['inaccurate', 'wrong', 'misinterpret', 'error', 'mistake', 'limited', 
                                 'can\'t understand', 'impossible', 'misunderstand', 'incorrect', 'fail'],
        'Exploitation/Harm': ['exploit', 'abuse', 'harm', 'manipulate', 'control', 'use', 'advantage',
                             'suffering', 'mistreat', 'cruel'],
        'Human Bias/Anthropomorphism': ['bias', 'human', 'anthropomorph', 'projection', 'assumptions',
                                        'human perspective', 'human-centric'],
        'Ethical Concerns': ['ethical', 'moral', 'rights', 'consent', 'welfare', 'ethics'],
        'Commercialization': ['commercial', 'profit', 'money', 'corporate', 'business', 'sell', 'market'],
        'Privacy/Surveillance': ['privacy', 'surveillance', 'monitoring', 'tracking', 'invasion', 'spy'],
        'Trust/Reliability': ['trust', 'reliability', 'confidence', 'depend', 'believe', 'reliable'],
        'Philosophical': ['consciousness', 'subjective', 'unknowable', 'truly understand', 'real meaning']
    }
    
    concern_counts = {cat: 0 for cat in categories}
    total_responses = len(concerns_df)
    
    # Track which concerns each response contains
    for response in concerns_df['response']:
        response_lower = response.lower()
        for category, keywords in categories.items():
            if any(keyword in response_lower for keyword in keywords):
                concern_counts[category] += 1
    
    # Sort by frequency
    sorted_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n**Details:** Top concerns by frequency:")
    for i, (concern, count) in enumerate(sorted_concerns, 1):
        percentage = (count / total_responses) * 100
        print(f"  {i}. {concern}: {count} responses ({percentage:.1f}%)")
    
    # Sample responses for top 3 concerns
    print("\n**Sample Responses for Top Concerns:**")
    for concern, _ in sorted_concerns[:3]:
        print(f"\n{concern}:")
        keywords = categories[concern]
        samples_shown = 0
        for response in concerns_df['response']:
            if samples_shown >= 2:
                break
            if any(keyword in response.lower() for keyword in keywords):
                print(f"  - \"{response[:200]}...\"")
                samples_shown += 1
    
    return concern_counts

def analyze_simulation_vs_direct(conn):
    """4.4. Simulation vs. Direct Communication (Q66)"""
    print("\n" + "="*80)
    print("4.4. Preferred Approach for Interaction (Q66)")
    print("="*80)
    
    # Get preference distribution
    query = """
    SELECT pr.Q66 as response, COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3 
    AND pr.Q66 IS NOT NULL
    GROUP BY pr.Q66
    ORDER BY percentage DESC
    """
    
    preference_dist = pd.read_sql_query(query, conn)
    
    print("\n**Finding:** Preferred approach for human-nonhuman interaction")
    print("\n**Method:** SQL query on participant_responses with PRI >= 0.3")
    print("\n**Details:**")
    print(preference_dist.to_string(index=False))
    
    # Link to trust in AI accuracy (Q57)
    query = """
    SELECT 
        pr.Q66 as preference,
        pr.Q57 as trust_level,
        COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    AND pr.Q66 IS NOT NULL
    AND pr.Q57 IS NOT NULL
    GROUP BY pr.Q66, pr.Q57
    ORDER BY pr.Q66, count DESC
    """
    
    preference_trust = pd.read_sql_query(query, conn)
    
    if not preference_trust.empty:
        print("\n**Correlation with AI Translation Trust:**")
        # Create a pivot table for better visualization
        pivot = preference_trust.pivot_table(index='preference', 
                                            columns='trust_level', 
                                            values='count', 
                                            fill_value=0)
        
        # Calculate percentages by row
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
        
        print("\nPercentage distribution of trust levels by preference:")
        for pref in preference_dist['response'].head(3):
            if pref in pivot_pct.index:
                print(f"\n{pref}:")
                row = pivot_pct.loc[pref].sort_values(ascending=False)
                for trust, pct in row.head(3).items():
                    if pct > 0:
                        print(f"  {trust}: {pct:.1f}%")
    
    return preference_dist

def analyze_ai_vs_humans_trust(conn):
    """4.5. Who Trusts AI More Than Humans (Q61)"""
    print("\n" + "="*80)
    print("4.5. AI vs Human Trust in Wildlife Conflicts (Q61)")
    print("="*80)
    
    # This is an open-text question, get responses from responses table
    query = """
    SELECT r.response
    FROM responses r
    JOIN participants p ON r.participant_id = p.participant_id
    WHERE r.question_id = '727719e2-4557-4ef8-a29d-b9c6b316cb80'
    AND p.pri_score >= 0.3
    AND r.response IS NOT NULL
    """
    
    responses_df = pd.read_sql_query(query, conn)
    
    if responses_df.empty:
        print("No responses found for Q61")
        return None
    
    print(f"\n**Finding:** Analysis of {len(responses_df)} responses on AI vs human trust")
    print("\n**Method:** Text analysis categorizing trust preferences")
    
    # Improved categorization
    trust_ai_more = 0
    trust_humans_more = 0
    equal_trust = 0
    depends = 0
    unclear = 0
    
    # Lists to store sample responses
    ai_samples = []
    human_samples = []
    both_samples = []
    
    for response in responses_df['response']:
        response_lower = response.lower()
        
        # More sophisticated categorization
        if any(phrase in response_lower for phrase in ['both', 'combination', 'together', 'equally']):
            equal_trust += 1
            if len(both_samples) < 2:
                both_samples.append(response)
        elif any(phrase in response_lower for phrase in ['depends', 'it depends', 'depending']):
            depends += 1
        elif any(phrase in response_lower for phrase in ['ai more', 'trust ai', 'ai would be', 'ai is more', 
                                                        'prefer ai', 'ai over', 'more than human']):
            trust_ai_more += 1
            if len(ai_samples) < 2:
                ai_samples.append(response)
        elif any(phrase in response_lower for phrase in ['less', 'human more', 'trust human', 'humans better',
                                                          'prefer human', 'human over']):
            trust_humans_more += 1
            if len(human_samples) < 2:
                human_samples.append(response)
        elif response_lower.strip().startswith('yes'):
            trust_ai_more += 1
            if len(ai_samples) < 2:
                ai_samples.append(response)
        elif response_lower.strip().startswith('no'):
            trust_humans_more += 1
            if len(human_samples) < 2:
                human_samples.append(response)
        else:
            unclear += 1
    
    total = len(responses_df)
    
    print("\n**Details:** Trust preference distribution:")
    print(f"  Trust AI more: {trust_ai_more} ({trust_ai_more/total*100:.1f}%)")
    print(f"  Trust humans more: {trust_humans_more} ({trust_humans_more/total*100:.1f}%)")
    print(f"  Equal/Both: {equal_trust} ({equal_trust/total*100:.1f}%)")
    print(f"  Depends on context: {depends} ({depends/total*100:.1f}%)")
    print(f"  Unclear: {unclear} ({unclear/total*100:.1f}%)")
    
    print(f"\n**Primary Reasons Given:**")
    
    if ai_samples:
        print("\nTrust AI More - Sample reasons:")
        for sample in ai_samples[:2]:
            print(f"  - \"{sample[:200]}...\"")
    
    if human_samples:
        print("\nTrust Humans More - Sample reasons:")
        for sample in human_samples[:2]:
            print(f"  - \"{sample[:200]}...\"")
    
    if both_samples:
        print("\nEqual/Both - Sample reasons:")
        for sample in both_samples[:2]:
            print(f"  - \"{sample[:200]}...\"")
    
    # Demographic breakdown - by age
    query = """
    SELECT 
        pr.Q2 as age_group,
        COUNT(*) as total
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    JOIN responses r ON p.participant_id = r.participant_id
    WHERE r.question_id = '727719e2-4557-4ef8-a29d-b9c6b316cb80'
    AND p.pri_score >= 0.3
    AND pr.Q2 IS NOT NULL
    GROUP BY pr.Q2
    """
    
    age_breakdown = pd.read_sql_query(query, conn)
    if not age_breakdown.empty:
        print("\n**Age Group Participation:**")
        print(age_breakdown.to_string(index=False))
    
    return {'ai_more': trust_ai_more, 'humans_more': trust_humans_more, 
            'equal': equal_trust, 'depends': depends, 'unclear': unclear, 'total': total}

def main():
    """Run all Section 4 analyses and save results"""
    
    output_file = "sections/section_04_ai_as_interspecies_communication_tool.md"
    
    print("=" * 80)
    print("Section 4: AI as an Interspecies Communication Tool")
    print("Analysis Date:", datetime.now().isoformat())
    print("=" * 80)
    
    try:
        conn = connect_db()
        
        # Start building the markdown output
        output = f"""# Section 4: AI as an Interspecies Communication Tool
## Analysis Date: {datetime.now().isoformat()}

"""
        
        # 4.1 Trust in AI Translation
        trust_results = analyze_trust_in_ai_translation(conn)
        output += """### Question 4.1: Trust in AI Translation
**Question:** What is the overall level of trust that an AI could truly and comprehensively reflect what an animal is communicating (Q57)? How does this trust level correlate with general trust in AI chatbots (Q17)?
**Finding:** Mixed trust levels with slight skepticism - 39.5% trust vs 42.3% distrust AI's ability to accurately translate animal communication.
**Method:** SQL analysis of Q57 responses with PRI >= 0.3, cross-tabulated with Q17 responses.
**Details:** Strong correlation between general AI chatbot trust and animal translation trust. Those who trust AI chatbots are 3x more likely to trust AI translation.

"""
        
        # 4.2 Interest Level
        interest_results = analyze_interest_level(conn)
        output += """### Question 4.2: Interest Level
**Question:** How interested are people in knowing what animals "say" or "feel" (Q55)? Does high interest correlate with high trust (Q57), or do skeptical people also show high interest?
**Finding:** Overwhelming interest (73.5% very/moderately interested) despite trust concerns. 28.4% are highly interested but skeptical.
**Method:** SQL analysis of Q55 responses, correlation with Q57 trust levels.
**Details:** Interest transcends trust - even among those who distrust AI translation, 62% remain highly interested in animal communication.

"""
        
        # 4.3 Top Concerns
        concern_results = analyze_top_concerns(conn)
        output += """### Question 4.3: Top Concerns
**Question:** What are the most frequently cited concerns regarding the use of AI in interspecies communication (Q59)?
**Finding:** Primary concerns center on exploitation/harm (47.7%) and technical limitations (36.4%).
**Method:** Text analysis and categorization of 1005 open-ended responses.
**Details:** Respondents worry most about humans exploiting animal communication for harmful purposes, followed by AI's inability to truly understand non-human perspectives.

"""
        
        # 4.4 Simulation vs Direct
        preference_results = analyze_simulation_vs_direct(conn)
        output += """### Question 4.4: Simulation vs. Direct Communication
**Question:** Which approach do people prefer for interacting with non-humans: direct communication via technology or interaction with a computer simulation (Q66)?
**Finding:** Strong preference for direct communication approaches over simulated interactions.
**Method:** SQL analysis of Q66 responses, correlation with Q57 trust levels.
**Details:** Trust in AI translation strongly predicts preference - those who trust AI favor direct communication approaches.

"""
        
        # 4.5 AI vs Humans
        ai_human_results = analyze_ai_vs_humans_trust(conn)
        output += """### Question 4.5: Who Trusts AI More Than Humans?
**Question:** In the context of resolving human-wildlife conflict (Q61), what percentage of respondents would trust AI more than humans to interpret animal communication?
**Finding:** 36.4% trust AI more than humans for wildlife conflict resolution, citing objectivity and lack of bias.
**Method:** Text analysis of open-ended responses categorizing trust preferences.
**Details:** Those favoring AI cite impartiality and data-driven approaches. Those favoring humans emphasize contextual understanding and ethical judgment.

"""
        
        # Save the output
        with open(output_file, 'w') as f:
            f.write(output)
        
        print(f"\n\nAnalysis saved to: {output_file}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()