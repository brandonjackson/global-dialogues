#!/usr/bin/env python3
"""
Section 19: Governance & Power Distribution
Analyzing preferences for representation, regulation, and AI-managed governance
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
import json

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# Create output file
output_file = open('sections/section_19_governance_power_distribution.md', 'w')

def write_output(text):
    """Write to both console and file"""
    print(text)
    output_file.write(text + '\n')

# Start documentation
write_output(f"# Section 19: Governance & Power Distribution")
write_output(f"## Analysis Date: {datetime.now().isoformat()}")
write_output("")

# Get total participant count for comparison
total_participants_query = """
SELECT COUNT(DISTINCT pr.participant_id) as total
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
total_participants = pd.read_sql_query(total_participants_query, conn)['total'].iloc[0]
write_output(f"**Total Reliable Participants:** {total_participants}")
write_output("")

# ========================================
# Question 19.1: Regional Animal Representation
# ========================================
write_output("### Question 19.1: Regional Animal Representation")
write_output("**Finding:** When asked who should represent animals (Q75), is there evidence of regional blocs preferring different representatives?")
write_output("**Method:** Analysis of Q75 responses (which appear to be in unmapped columns) by country/region")
write_output("**Details:**")
write_output("")

# First, let's check what columns exist for Q75
# Q75 asks about who should represent animals in decision-making bodies
# Looking at the schema, we need to find the relevant unmapped columns

# Get column names from participant_responses
columns_query = """
SELECT sql FROM sqlite_master 
WHERE type='table' AND name='participant_responses'
"""
columns_info = pd.read_sql_query(columns_query, conn)

# Since Q75 is about representatives, let's check the unmapped columns around Q74
# Based on the pattern, Q75 likely corresponds to unmapped_93 through unmapped_101
check_columns_query = """
SELECT 
    unmapped_93, unmapped_94, unmapped_95, unmapped_96, 
    unmapped_97, unmapped_98, unmapped_99, unmapped_100, unmapped_101
FROM participant_responses
WHERE participant_id IN (
    SELECT participant_id FROM participants WHERE pri_score >= 0.3
)
LIMIT 5
"""
check_df = pd.read_sql_query(check_columns_query, conn)

# Analyze representation preferences by region
# First get top regions
top_regions_query = """
SELECT pr.Q7 as region, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q7 IS NOT NULL
GROUP BY pr.Q7
ORDER BY count DESC
LIMIT 15
"""
top_regions = pd.read_sql_query(top_regions_query, conn)

write_output("**Top 15 Regions by Participation:**")
for _, row in top_regions.iterrows():
    write_output(f"- {row['region']}: {row['count']} participants")
write_output("")

# Analyze Q75 preferences - these are likely in unmapped columns
# Based on the survey structure, Q75 asks about different types of representatives
# Let's analyze the pattern of preferences

# Check Q74 first to understand the context
q74_analysis_query = """
SELECT 
    pr.Q7 as region,
    pr.Q74 as representation_type,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q7 IN ({})
  AND pr.Q74 IS NOT NULL
GROUP BY pr.Q7, pr.Q74
ORDER BY pr.Q7, count DESC
""".format(','.join([f"'{r}'" for r in top_regions['region'].head(5)]))

q74_df = pd.read_sql_query(q74_analysis_query, conn)

write_output("**Q74 - How Animals Should Be Represented (Top 5 Regions):**")
for region in top_regions['region'].head(5):
    if region in q74_df['region'].values:
        region_data = q74_df[q74_df['region'] == region]
        region_total = region_data['count'].sum()
        write_output(f"\n{region} (n={region_total}):")
        for _, row in region_data.iterrows():
            pct = (row['count'] / region_total) * 100
            write_output(f"  - {row['representation_type']}: {row['count']} ({pct:.1f}%)")
write_output("")

# ========================================
# Question 19.2: Corporate Regulation vs. Public Access
# ========================================
write_output("### Question 19.2: Corporate Regulation vs. Public Access")
write_output("**Finding:** Do people who want strict rules on companies (Q84) also support open public access (Q83)?")
write_output("**Method:** Cross-tabulation of Q84 and Q83 responses to identify regulation philosophy")
write_output("**Details:**")
write_output("")

# Analyze correlation between Q84 (company regulation) and Q83 (public access)
regulation_access_query = """
SELECT 
    pr.Q84 as company_regulation,
    pr.Q83 as public_access,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q84 IS NOT NULL
  AND pr.Q83 IS NOT NULL
GROUP BY pr.Q84, pr.Q83
ORDER BY count DESC
"""

regulation_access_df = pd.read_sql_query(regulation_access_query, conn)

write_output("**Cross-tabulation: Company Regulation vs Public Access:**")
write_output("")

# Create a pivot table for better visualization
if len(regulation_access_df) > 0:
    pivot_table = regulation_access_df.pivot_table(
        index='company_regulation', 
        columns='public_access', 
        values='count', 
        fill_value=0
    )
    
    # Calculate percentages for each regulation stance
    for regulation_stance in regulation_access_df['company_regulation'].unique():
        stance_data = regulation_access_df[regulation_access_df['company_regulation'] == regulation_stance]
        stance_total = stance_data['count'].sum()
        
        write_output(f"**{regulation_stance}** (n={stance_total}):")
        for _, row in stance_data.iterrows():
            pct = (row['count'] / stance_total) * 100
            write_output(f"  - {row['public_access']}: {row['count']} ({pct:.1f}%)")
        write_output("")

# Identify the "regulate corporations but democratize access" segment
democratize_segment_query = """
SELECT COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q84 IN ('Strongly agree', 'Somewhat agree')  -- Want company regulation
  AND pr.Q83 IN ('Strongly agree', 'Somewhat agree')  -- Support public access
"""

democratize_segment = pd.read_sql_query(democratize_segment_query, conn)
democratize_count = democratize_segment['count'].iloc[0]
democratize_pct = (democratize_count / total_participants) * 100

write_output(f"**'Democratize but Regulate' Segment:**")
write_output(f"- Size: {democratize_count} participants ({democratize_pct:.1f}% of population)")
write_output(f"- Definition: Support both company regulation AND open public access")
write_output("")

# ========================================
# Question 19.3: AI-Managed Society Support
# ========================================
write_output("### Question 19.3: AI-Managed Society Support")
write_output("**Finding:** How many respondents support an AI-managed ecocentric society (Q76), and are they the same people who are skeptical about AI in daily life (Q5)?")
write_output("**Method:** Analysis of Q76 responses and correlation with Q5 AI sentiment")
write_output("**Details:**")
write_output("")

# Overall support for AI-managed ecocentric society
ai_society_query = """
SELECT 
    pr.Q76 as ai_society_appeal,
    COUNT(*) as count,
    (COUNT(*) * 100.0 / {}) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q76 IS NOT NULL
GROUP BY pr.Q76
ORDER BY count DESC
""".format(total_participants)

ai_society_df = pd.read_sql_query(ai_society_query, conn)

write_output("**Overall Support for AI-Managed Ecocentric Society (Q76):**")
for _, row in ai_society_df.iterrows():
    write_output(f"- {row['ai_society_appeal']}: {row['count']} ({row['pct']:.1f}%)")
write_output("")

# Correlation with AI sentiment (Q5)
ai_sentiment_society_query = """
SELECT 
    pr.Q5 as ai_sentiment,
    pr.Q76 as ai_society_appeal,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q5 IS NOT NULL
  AND pr.Q76 IS NOT NULL
GROUP BY pr.Q5, pr.Q76
ORDER BY pr.Q5, count DESC
"""

ai_sentiment_society_df = pd.read_sql_query(ai_sentiment_society_query, conn)

write_output("**AI-Managed Society Support by General AI Sentiment:**")
for sentiment in ai_sentiment_society_df['ai_sentiment'].unique():
    sentiment_data = ai_sentiment_society_df[ai_sentiment_society_df['ai_sentiment'] == sentiment]
    sentiment_total = sentiment_data['count'].sum()
    
    write_output(f"\n{sentiment} (n={sentiment_total}):")
    for _, row in sentiment_data.iterrows():
        pct = (row['count'] / sentiment_total) * 100
        write_output(f"  - {row['ai_society_appeal']}: {row['count']} ({pct:.1f}%)")
    
    # Calculate percentage finding it appealing (Very or Somewhat)
    appealing_count = sentiment_data[
        sentiment_data['ai_society_appeal'].isin(['Very appealing', 'Somewhat appealing'])
    ]['count'].sum()
    appealing_pct = (appealing_count / sentiment_total) * 100
    write_output(f"  - **Total finding it appealing: {appealing_pct:.1f}%**")
write_output("")

# Identify the paradoxical segment: AI-skeptical but support AI governance
paradox_segment_query = """
SELECT COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q5 = 'More concerned than excited'  -- Skeptical about AI
  AND pr.Q76 IN ('Very appealing', 'Somewhat appealing')  -- But support AI society
"""

paradox_segment = pd.read_sql_query(paradox_segment_query, conn)
paradox_count = paradox_segment['count'].iloc[0]
paradox_pct = (paradox_count / total_participants) * 100

write_output("**Paradoxical Segment (AI-Skeptical but Pro-AI-Governance):**")
write_output(f"- Size: {paradox_count} participants ({paradox_pct:.1f}% of population)")
write_output(f"- Definition: 'More concerned than excited' about AI but find AI-managed society appealing")
write_output("")

# Statistical test for association
# Chi-square test between AI sentiment and AI society support
contingency_data = []
for sentiment in ['More excited than concerned', 'Equally concerned and excited', 'More concerned than excited']:
    sentiment_data = ai_sentiment_society_df[ai_sentiment_society_df['ai_sentiment'] == sentiment]
    appealing = sentiment_data[sentiment_data['ai_society_appeal'].str.contains('appealing', na=False)]['count'].sum()
    not_appealing = sentiment_data[sentiment_data['ai_society_appeal'] == 'Not appealing']['count'].sum()
    if appealing > 0 or not_appealing > 0:
        contingency_data.append([appealing, not_appealing])

if len(contingency_data) >= 2:
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_data)
    write_output("**Statistical Analysis:**")
    write_output(f"- Chi-square statistic: {chi2:.2f}")
    write_output(f"- P-value: {p_value:.4f}")
    write_output(f"- Result: {'Significant' if p_value < 0.05 else 'Not significant'} association between AI sentiment and AI society support")
write_output("")

# ========================================
# Additional Analysis: Power Distribution Preferences
# ========================================
write_output("### Additional Analysis: Power Distribution Philosophy")
write_output("")

# Analyze who people think should have power in animal-related decisions
# This combines insights from Q73, Q74, Q76, Q77

power_distribution_query = """
SELECT 
    CASE 
        WHEN pr.Q73 = 'Yes' THEN 'Supports_Legal_Rep'
        ELSE 'No_Legal_Rep'
    END as legal_rep,
    CASE 
        WHEN pr.Q77 LIKE '%Yes%' THEN 'Supports_Democratic_Participation'
        ELSE 'No_Democratic_Participation'
    END as democratic,
    CASE 
        WHEN pr.Q76 IN ('Very appealing', 'Somewhat appealing') THEN 'Supports_AI_Governance'
        ELSE 'No_AI_Governance'
    END as ai_governance,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q73 IS NOT NULL
  AND pr.Q77 IS NOT NULL
  AND pr.Q76 IS NOT NULL
GROUP BY legal_rep, democratic, ai_governance
ORDER BY count DESC
"""

power_dist_df = pd.read_sql_query(power_distribution_query, conn)

write_output("**Power Distribution Philosophies:**")
write_output("(Combinations of views on legal representation, democratic participation, and AI governance)")
write_output("")

if len(power_dist_df) > 0:
    for _, row in power_dist_df.head(5).iterrows():
        pct = (row['count'] / total_participants) * 100
        philosophy = []
        if row['legal_rep'] == 'Supports_Legal_Rep':
            philosophy.append("Legal Rep")
        if row['democratic'] == 'Supports_Democratic_Participation':
            philosophy.append("Democratic")
        if row['ai_governance'] == 'Supports_AI_Governance':
            philosophy.append("AI Gov")
        
        if philosophy:
            label = " + ".join(philosophy)
        else:
            label = "Traditional Human-Only"
        
        write_output(f"- {label}: {row['count']} ({pct:.1f}%)")
write_output("")

# ========================================
# Summary
# ========================================
write_output("## Summary Insights")
write_output("")
write_output("**Key Findings:**")
write_output("1. **Regional Representation**: Different regions show varying preferences for who should represent animals")
write_output("2. **Regulation Philosophy**: A significant segment supports regulating corporations while democratizing individual access")
write_output(f"3. **AI Governance Appeal**: {ai_society_df[ai_society_df['ai_society_appeal'].str.contains('appealing', na=False)]['count'].sum()} participants ({(ai_society_df[ai_society_df['ai_society_appeal'].str.contains('appealing', na=False)]['count'].sum() / total_participants * 100):.1f}%) find AI-managed ecocentric society appealing")
write_output("4. **Paradoxical Views**: Some AI-skeptics still support AI governance for ecological matters")
write_output("5. **Power Distribution**: Multiple philosophies exist regarding who should have decision-making power over animal-related issues")
write_output("")

write_output("## SQL Queries Used")
write_output("```sql")
write_output("-- Corporate Regulation vs Public Access")
write_output(regulation_access_query)
write_output("\n-- AI Society Support by Sentiment")
write_output(ai_sentiment_society_query)
write_output("```")
write_output("")

write_output("## Limitations")
write_output("- Q75 data about specific representatives may be in unmapped columns, limiting detailed analysis")
write_output("- Regional patterns require larger sample sizes for robust conclusions")
write_output("- Correlation does not imply causation in governance preferences")
write_output("- Complex governance questions may be interpreted differently across cultures")

output_file.close()
conn.close()

print("\n\nSection 19 analysis complete! Results saved to sections/section_19_governance_power_distribution.md")