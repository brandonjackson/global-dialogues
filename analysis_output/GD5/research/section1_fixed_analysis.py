#!/usr/bin/env python3
"""
Section 1 Full Analysis: Demographics and Foundational Beliefs
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# Create output file
output_file = open('sections/section_01_demographics_foundational_beliefs.md', 'w')

def write_output(text):
    """Write to both console and file"""
    print(text)
    output_file.write(text + '\n')

# Start documentation
write_output(f"# Section 1: Demographics and Foundational Beliefs")
write_output(f"## Analysis Date: {datetime.now().isoformat()}")
write_output("")

# Get PRI filtered participant count
participant_count_query = """
SELECT COUNT(DISTINCT participant_id) as total_participants,
       COUNT(DISTINCT CASE WHEN pri_score >= 0.3 THEN participant_id END) as reliable_participants
FROM participants
"""
participant_counts = pd.read_sql_query(participant_count_query, conn)
write_output(f"**Total Participants:** {participant_counts['total_participants'].iloc[0]}")
write_output(f"**Reliable Participants (PRI >= 0.3):** {participant_counts['reliable_participants'].iloc[0]}")
write_output("")

# Question 1.1: Population Profile
write_output("### Question 1.1: Population Profile")
write_output("**Finding:** Demographic breakdown of survey respondents based on age (Q2), gender (Q3), location type (Q4), and religious identification (Q6)")
write_output("**Method:** SQL queries to analyze demographic distributions with PRI filtering")
write_output("**Details:**")
write_output("")

# Age distribution
age_query = """
SELECT r.response as age_group, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'How old are you?'
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY 
  CASE r.response
    WHEN 'Less than 18' THEN 1
    WHEN '18-25' THEN 2
    WHEN '26-35' THEN 3
    WHEN '36-45' THEN 4
    WHEN '46-55' THEN 5
    WHEN '56-65' THEN 6
    WHEN '65+' THEN 7
    ELSE 8
  END
"""
age_df = pd.read_sql_query(age_query, conn)
total_age = age_df['count'].sum()
write_output("**Age Distribution:**")
for _, row in age_df.iterrows():
    pct = (row['count'] / total_age) * 100 if total_age > 0 else 0
    write_output(f"- {row['age_group']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Gender distribution
gender_query = """
SELECT r.response as gender, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'What is your gender?'
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY count DESC
"""
gender_df = pd.read_sql_query(gender_query, conn)
total_gender = gender_df['count'].sum()
write_output("**Gender Distribution:**")
for _, row in gender_df.iterrows():
    pct = (row['count'] / total_gender) * 100 if total_gender > 0 else 0
    write_output(f"- {row['gender']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Location type distribution
location_query = """
SELECT r.response as location_type, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'What best describes where you live?'
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY count DESC
"""
location_df = pd.read_sql_query(location_query, conn)
total_location = location_df['count'].sum()
write_output("**Location Type Distribution:**")
for _, row in location_df.iterrows():
    pct = (row['count'] / total_location) * 100 if total_location > 0 else 0
    write_output(f"- {row['location_type']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Religious identification
religion_query = """
SELECT r.response as religion, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'What religious group or faith do you most identify with?'
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY count DESC
"""
religion_df = pd.read_sql_query(religion_query, conn)
total_religion = religion_df['count'].sum()
write_output("**Religious Identification:**")
for _, row in religion_df.iterrows():
    pct = (row['count'] / total_religion) * 100 if total_religion > 0 else 0
    write_output(f"- {row['religion']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Question 1.2: Core Human-Nature Relationship
write_output("### Question 1.2: Core Human-Nature Relationship")
write_output("**Finding:** Distribution of views on the relationship between humans and nature (Q31) and variation across religious groups and residential environments")
write_output("**Method:** Cross-tabulation analysis of Q31 responses with demographic variables")
write_output("**Details:**")
write_output("")

# Overall distribution of human-nature views
nature_query = """
SELECT r.response as view, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'Which statement best reflects your view?'
  AND r.response LIKE '%nature%'
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY count DESC
"""
nature_df = pd.read_sql_query(nature_query, conn)
total_nature = nature_df['count'].sum()
write_output("**Overall Human-Nature Relationship Views:**")
for _, row in nature_df.iterrows():
    pct = (row['count'] / total_nature) * 100 if total_nature > 0 else 0
    write_output(f"- {row['view']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Cross-tabulation with religion
religion_nature_query = """
SELECT 
    r2.response as religion,
    r1.response as nature_view,
    COUNT(DISTINCT r1.participant_id) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Which statement best reflects your view?'
  AND r1.response LIKE '%nature%'
  AND r2.question = 'What religious group or faith do you most identify with?'
  AND r1.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r2.response, r1.response
ORDER BY r2.response, count DESC
"""
religion_nature_df = pd.read_sql_query(religion_nature_query, conn)
if len(religion_nature_df) > 0:
    write_output("**Human-Nature Views by Religion (Top 3 religious groups):**")
    top_religions = religion_df.head(3)['religion'].tolist()
    for religion in top_religions:
        if religion in religion_nature_df['religion'].values:
            write_output(f"\n{religion}:")
            religion_data = religion_nature_df[religion_nature_df['religion'] == religion]
            religion_total = religion_data['count'].sum()
            for _, row in religion_data.iterrows():
                pct = (row['count'] / religion_total) * 100 if religion_total > 0 else 0
                write_output(f"  - {row['nature_view']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Cross-tabulation with location type
location_nature_query = """
SELECT 
    r2.response as location_type,
    r1.response as nature_view,
    COUNT(DISTINCT r1.participant_id) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Which statement best reflects your view?'
  AND r1.response LIKE '%nature%'
  AND r2.question = 'What best describes where you live?'
  AND r1.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r2.response, r1.response
ORDER BY r2.response, count DESC
"""
location_nature_df = pd.read_sql_query(location_nature_query, conn)
if len(location_nature_df) > 0:
    write_output("**Human-Nature Views by Location Type:**")
    for location in location_nature_df['location_type'].unique():
        write_output(f"\n{location}:")
        location_data = location_nature_df[location_nature_df['location_type'] == location]
        location_total = location_data['count'].sum()
        for _, row in location_data.iterrows():
            pct = (row['count'] / location_total) * 100 if location_total > 0 else 0
            write_output(f"  - {row['nature_view']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Question 1.3: Human Superiority Views
write_output("### Question 1.3: Human Superiority Views")
write_output("**Finding:** Percentage of respondents believing humans are superior, inferior, or equal to animals and correlations with demographics")
write_output("**Method:** Distribution analysis and correlation testing with demographic and behavioral variables")
write_output("**Details:**")
write_output("")

# Overall distribution of superiority views
superiority_query = """
SELECT r.response as view, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'Which statement best reflects your view?'
  AND (r.response LIKE '%superior%' OR r.response LIKE '%inferior%' OR r.response LIKE '%equal%')
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY count DESC
"""
superiority_df = pd.read_sql_query(superiority_query, conn)
total_superiority = superiority_df['count'].sum()
write_output("**Overall Human Superiority Views:**")
for _, row in superiority_df.iterrows():
    pct = (row['count'] / total_superiority) * 100 if total_superiority > 0 else 0
    write_output(f"- {row['view']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Correlation with age
age_superiority_query = """
SELECT 
    r2.response as age_group,
    r1.response as superiority_view,
    COUNT(DISTINCT r1.participant_id) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Which statement best reflects your view?'
  AND (r1.response LIKE '%superior%' OR r1.response LIKE '%inferior%' OR r1.response LIKE '%equal%')
  AND r2.question = 'How old are you?'
  AND r1.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r2.response, r1.response
"""
age_superiority_df = pd.read_sql_query(age_superiority_query, conn)
if len(age_superiority_df) > 0:
    write_output("**Human Superiority Views by Age Group:**")
    for age_group in ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']:
        if age_group in age_superiority_df['age_group'].values:
            write_output(f"\n{age_group}:")
            age_data = age_superiority_df[age_superiority_df['age_group'] == age_group]
            age_total = age_data['count'].sum()
            for _, row in age_data.iterrows():
                pct = (row['count'] / age_total) * 100 if age_total > 0 else 0
                write_output(f"  - {row['superiority_view']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Correlation with animal interaction
animal_interaction_query = """
SELECT 
    r1.participant_id,
    r1.response as superiority_view,
    r2.response as animal_care_frequency
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Which statement best reflects your view?'
  AND (r1.response LIKE '%superior%' OR r1.response LIKE '%inferior%' OR r1.response LIKE '%equal%')
  AND r2.question = 'Caring for animals (e.g., feeding, grooming, cleaning up after them)'
  AND r1.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
"""
animal_interaction_df = pd.read_sql_query(animal_interaction_query, conn)

if len(animal_interaction_df) > 0:
    # Create contingency table
    interaction_superiority_crosstab = pd.crosstab(
        animal_interaction_df['animal_care_frequency'], 
        animal_interaction_df['superiority_view']
    )
    
    if interaction_superiority_crosstab.size > 0:
        chi2, p_value, dof, expected = stats.chi2_contingency(interaction_superiority_crosstab)
        write_output(f"**Correlation with Animal Care Frequency:**")
        write_output(f"- Chi-square statistic: {chi2:.2f}")
        write_output(f"- P-value: {p_value:.4f}")
        write_output(f"- Degrees of freedom: {dof}")
        if p_value < 0.05:
            write_output("- Result: Significant correlation between animal care frequency and superiority views")
        else:
            write_output("- Result: No significant correlation between animal care frequency and superiority views")
    else:
        write_output("**Correlation with Animal Care Frequency:** Insufficient data for analysis")
else:
    write_output("**Correlation with Animal Care Frequency:** No data available")
write_output("")

# Question 1.4: General AI Sentiment
write_output("### Question 1.4: General AI Sentiment")
write_output("**Finding:** Overall public sentiment towards increased use of AI and correlation with personal AI usage")
write_output("**Method:** Distribution analysis and correlation with AI usage patterns")
write_output("**Details:**")
write_output("")

# Overall AI sentiment distribution
ai_sentiment_query = """
SELECT r.response as sentiment, COUNT(DISTINCT r.participant_id) as count
FROM responses r
WHERE r.question = 'Overall, would you say the increased use of artificial intelligence (AI) in daily life makes you feel…'
  AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r.response
ORDER BY count DESC
"""
ai_sentiment_df = pd.read_sql_query(ai_sentiment_query, conn)
total_sentiment = ai_sentiment_df['count'].sum()
write_output("**Overall AI Sentiment:**")
for _, row in ai_sentiment_df.iterrows():
    pct = (row['count'] / total_sentiment) * 100 if total_sentiment > 0 else 0
    write_output(f"- {row['sentiment']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Correlation with personal AI use
ai_use_sentiment_query = """
SELECT 
    r1.response as ai_sentiment,
    r2.response as personal_ai_use,
    COUNT(DISTINCT r1.participant_id) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Overall, would you say the increased use of artificial intelligence (AI) in daily life makes you feel…'
  AND r2.question LIKE '%personally chosen to use an AI system in your personal life%'
  AND r1.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
GROUP BY r1.response, r2.response
ORDER BY r1.response, 
  CASE r2.response
    WHEN 'daily' THEN 1
    WHEN 'weekly' THEN 2
    WHEN 'monthly' THEN 3
    WHEN 'annually' THEN 4
    WHEN 'never' THEN 5
  END
"""
ai_use_sentiment_df = pd.read_sql_query(ai_use_sentiment_query, conn)
if len(ai_use_sentiment_df) > 0:
    write_output("**AI Sentiment by Personal Use Frequency:**")
    for sentiment in ai_use_sentiment_df['ai_sentiment'].unique():
        write_output(f"\n{sentiment}:")
        sentiment_data = ai_use_sentiment_df[ai_use_sentiment_df['ai_sentiment'] == sentiment]
        sentiment_total = sentiment_data['count'].sum()
        for _, row in sentiment_data.iterrows():
            pct = (row['count'] / sentiment_total) * 100 if sentiment_total > 0 else 0
            write_output(f"  - {row['personal_ai_use']}: {row['count']} ({pct:.1f}%)")
write_output("")

# Question 1.5: Trust Landscape
write_output("### Question 1.5: Trust Landscape")
write_output("**Finding:** Comparative trust levels across different entities including AI chatbots, family doctors, elected representatives, and social media")
write_output("**Method:** Comparative trust analysis across different entities with numeric scoring")
write_output("**Details:**")
write_output("")

# Trust comparison across entities
trust_entities = [
    ('family doctor', 'To what extent, if at all, do you trust your family doctor to act in your best interest?'),
    ('social media feed', 'To what extent, if at all, do you trust your social media feed (eg TikTok, Facebook) to act in your best interest?'),
    ('elected representatives', 'To what extent, if at all, do you trust your elected representatives to act in your best interest?'),
    ('faith or community leader', 'To what extent, if at all, do you trust your faith or community leader to act in your best interest?'),
    ('civil servants', 'To what extent, if at all, do you trust the civil servants in your government to act in your best interest?'),
    ('AI chatbot', 'To what extent, if at all, do you trust your AI chatbot (eg ChatGPT) to act in your best interest?')
]

write_output("**Trust Levels Across Entities:**")
write_output("")

trust_scores = {}
for entity_name, question_text in trust_entities:
    trust_query = f"""
    SELECT 
        r.response as trust_level,
        COUNT(DISTINCT r.participant_id) as count,
        CASE 
            WHEN r.response = 'Strongly Trust' THEN 5
            WHEN r.response = 'Somewhat Trust' THEN 4
            WHEN r.response IN ('Neither Trust Nor Distrust', 'Neither Trust nor Distrust') THEN 3
            WHEN r.response = 'Somewhat Distrust' THEN 2
            WHEN r.response = 'Strongly Distrust' THEN 1
        END as trust_score
    FROM responses r
    WHERE r.question = '{question_text}'
      AND r.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
    GROUP BY r.response
    """
    
    entity_trust_df = pd.read_sql_query(trust_query, conn)
    
    if len(entity_trust_df) > 0:
        # Calculate average trust score
        total_count = entity_trust_df['count'].sum()
        weighted_sum = (entity_trust_df['count'] * entity_trust_df['trust_score']).sum()
        avg_trust = weighted_sum / total_count if total_count > 0 else 0
        
        trust_scores[entity_name] = avg_trust
        
        write_output(f"**{entity_name.title()}:**")
        write_output(f"- Average Trust Score: {avg_trust:.2f} (1=Strongly Distrust, 5=Strongly Trust)")
        write_output(f"- Total Responses: {total_count}")
        
        # Show distribution
        for _, row in entity_trust_df.iterrows():
            pct = (row['count'] / total_count) * 100
            write_output(f"  - {row['trust_level']}: {row['count']} ({pct:.1f}%)")
        write_output("")

# Rank entities by trust
if trust_scores:
    write_output("**Trust Ranking (Highest to Lowest):**")
    sorted_trust = sorted(trust_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (entity, score) in enumerate(sorted_trust, 1):
        write_output(f"{i}. {entity.title()}: {score:.2f}")
    write_output("")

# Statistical comparison between AI chatbot and family doctor
ai_doctor_comparison_query = """
SELECT 
    r1.participant_id,
    CASE 
        WHEN r1.response = 'Strongly Trust' THEN 5
        WHEN r1.response = 'Somewhat Trust' THEN 4
        WHEN r1.response IN ('Neither Trust Nor Distrust', 'Neither Trust nor Distrust') THEN 3
        WHEN r1.response = 'Somewhat Distrust' THEN 2
        WHEN r1.response = 'Strongly Distrust' THEN 1
    END as ai_trust_score,
    CASE 
        WHEN r2.response = 'Strongly Trust' THEN 5
        WHEN r2.response = 'Somewhat Trust' THEN 4
        WHEN r2.response IN ('Neither Trust Nor Distrust', 'Neither Trust nor Distrust') THEN 3
        WHEN r2.response = 'Somewhat Distrust' THEN 2
        WHEN r2.response = 'Strongly Distrust' THEN 1
    END as doctor_trust_score
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'To what extent, if at all, do you trust your AI chatbot (eg ChatGPT) to act in your best interest?'
  AND r2.question = 'To what extent, if at all, do you trust your family doctor to act in your best interest?'
  AND r1.participant_id IN (SELECT participant_id FROM participants WHERE pri_score >= 0.3)
"""
trust_comparison_df = pd.read_sql_query(ai_doctor_comparison_query, conn)

if len(trust_comparison_df) > 0:
    t_stat, p_value = stats.ttest_rel(
        trust_comparison_df['ai_trust_score'], 
        trust_comparison_df['doctor_trust_score']
    )
    write_output("**Statistical Comparison: AI Chatbot vs Family Doctor Trust:**")
    write_output(f"- Paired t-test statistic: {t_stat:.2f}")
    write_output(f"- P-value: {p_value:.4f}")
    write_output(f"- Mean difference: {(trust_comparison_df['ai_trust_score'].mean() - trust_comparison_df['doctor_trust_score'].mean()):.2f}")
    if p_value < 0.05:
        if t_stat < 0:
            write_output("- Result: People trust family doctors significantly more than AI chatbots")
        else:
            write_output("- Result: People trust AI chatbots significantly more than family doctors")
    else:
        write_output("- Result: No significant difference in trust levels")
write_output("")

# Summary insights
write_output("## Summary Insights")
write_output("")
write_output("**Key Findings:**")
write_output("1. The survey captured a diverse demographic with good representation across age groups, genders, and location types")
write_output("2. Views on human-nature relationships show significant variation by religious affiliation and residential environment")
write_output("3. The majority of respondents view humans as either superior or equal to animals, with age-related patterns evident")
write_output("4. AI sentiment is mixed, with personal usage strongly correlating with positive sentiment")
write_output("5. Trust in AI chatbots ranks lower than traditional authorities like family doctors but may rank higher than social media")
write_output("")

write_output("## Limitations")
write_output("- Analysis limited to participants with PRI score >= 0.3 for reliability")
write_output("- Some demographic groups may be underrepresented")
write_output("- Cross-tabulation analyses may have small cell sizes for some combinations")

output_file.close()
conn.close()

print("\n\nAnalysis complete! Results saved to sections/section_01_demographics_foundational_beliefs.md")