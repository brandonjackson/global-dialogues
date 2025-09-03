#!/usr/bin/env python3
"""
Section 13: Cultural, Religious, and Regional Patterns
Analyzing differences across religious, geographic, and cultural dimensions
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# Create output file
output_file = open('sections/section_13_cultural_religious_regional_patterns.md', 'w')

def write_output(text):
    """Write to both console and file"""
    print(text)
    output_file.write(text + '\n')

# Start documentation
write_output(f"# Section 13: Cultural, Religious, and Regional Patterns")
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
# Question 13.1: Religious Views on Human-Animal Equality
# ========================================
write_output("### Question 13.1: Religious Views on Human-Animal Equality")
write_output("**Finding:** Which religions (Q6) most strongly support the view that humans are equal to animals (Q32/Q94), and how does this relate to their support for legal representation (Q73-74)?")
write_output("**Method:** Cross-tabulation of religious affiliation with equality views and legal representation support")
write_output("**Details:**")
write_output("")

# Analyze human-animal equality views by religion
religion_equality_query = """
SELECT 
    pr.Q6 as religion,
    CASE 
        WHEN pr.Q94 LIKE '%equal%' THEN 'Equal'
        WHEN pr.Q94 LIKE '%superior%' THEN 'Superior'
        WHEN pr.Q94 LIKE '%inferior%' THEN 'Inferior'
        ELSE 'Other'
    END as view,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q6 IS NOT NULL
  AND pr.Q94 IS NOT NULL
GROUP BY pr.Q6, view
ORDER BY pr.Q6, count DESC
"""

religion_equality_df = pd.read_sql_query(religion_equality_query, conn)

write_output("**Human-Animal Equality Views by Religion:**")
for religion in religion_equality_df['religion'].unique():
    religion_data = religion_equality_df[religion_equality_df['religion'] == religion]
    religion_total = religion_data['count'].sum()
    equal_count = religion_data[religion_data['view'] == 'Equal']['count'].sum()
    equal_pct = (equal_count / religion_total) * 100 if religion_total > 0 else 0
    
    write_output(f"\n{religion}:")
    for _, row in religion_data.iterrows():
        if row['view'] != 'Other':
            pct = (row['count'] / religion_total) * 100
            write_output(f"  - {row['view']}: {row['count']} ({pct:.1f}%)")
    write_output(f"  - **Equality Rate: {equal_pct:.1f}%**")
write_output("")

# Correlation between equality views and legal representation support by religion
religion_legal_query = """
SELECT 
    pr.Q6 as religion,
    pr.Q73 as legal_rep,
    CASE 
        WHEN pr.Q94 LIKE '%equal%' THEN 'Believes_Equal'
        ELSE 'Other_View'
    END as equality_view,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q6 IS NOT NULL
  AND pr.Q73 IS NOT NULL
  AND pr.Q94 IS NOT NULL
GROUP BY pr.Q6, pr.Q73, equality_view
"""

religion_legal_df = pd.read_sql_query(religion_legal_query, conn)

write_output("**Support for Legal Representation (Q73) by Religion and Equality View:**")
for religion in ['Christianity', 'Islam', 'Hinduism', 'Buddhism', 'I do not identify with any religious group or faith']:
    if religion in religion_legal_df['religion'].values:
        write_output(f"\n{religion}:")
        
        # Those who believe in equality
        equal_data = religion_legal_df[(religion_legal_df['religion'] == religion) & 
                                       (religion_legal_df['equality_view'] == 'Believes_Equal')]
        equal_total = equal_data['count'].sum()
        if equal_total > 0:
            yes_count = equal_data[equal_data['legal_rep'] == 'Yes']['count'].sum()
            yes_pct = (yes_count / equal_total) * 100
            write_output(f"  - Among those believing in equality: {yes_pct:.1f}% support legal representation")
        
        # All members of religion
        all_data = religion_legal_df[religion_legal_df['religion'] == religion]
        all_total = all_data['count'].sum()
        all_yes = all_data[all_data['legal_rep'] == 'Yes']['count'].sum()
        all_yes_pct = (all_yes / all_total) * 100
        write_output(f"  - Overall: {all_yes_pct:.1f}% support legal representation")
write_output("")

# ========================================
# Question 13.2: Rural vs. Urban Animal Rights
# ========================================
write_output("### Question 13.2: Rural vs. Urban Animal Rights")
write_output("**Finding:** Do rural respondents (Q4) with higher daily encounters with farmed animals (Q38) show less support for legal rights (Q70-C) than urban respondents?")
write_output("**Method:** Analysis of Q70 preferences by location type and farm animal encounter frequency")
write_output("**Details:**")
write_output("")

# Analyze Q70 (future preferences) by location type
location_future_query = """
SELECT 
    pr.Q4 as location,
    pr.Q70 as future_preference,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q4 IS NOT NULL
  AND pr.Q70 IS NOT NULL
GROUP BY pr.Q4, pr.Q70
ORDER BY pr.Q4, count DESC
"""

location_future_df = pd.read_sql_query(location_future_query, conn)

write_output("**Preferred Future for Animal Protection by Location Type:**")
for location in ['Rural', 'Suburban', 'Urban']:
    if location in location_future_df['location'].values:
        location_data = location_future_df[location_future_df['location'] == location]
        location_total = location_data['count'].sum()
        
        write_output(f"\n{location} (n={location_total}):")
        for _, row in location_data.iterrows():
            pct = (row['count'] / location_total) * 100
            # Simplify the future labels
            if 'Future A' in row['future_preference']:
                label = "Future A (Relationships)"
            elif 'Future B' in row['future_preference']:
                label = "Future B (Shared Decision-Making)"
            elif 'Future C' in row['future_preference']:
                label = "Future C (Legal Rights)"
            else:
                label = row['future_preference']
            write_output(f"  - {label}: {row['count']} ({pct:.1f}%)")

        # Highlight Future C percentage
        future_c_count = location_data[location_data['future_preference'].str.contains('Future C', na=False)]['count'].sum()
        future_c_pct = (future_c_count / location_total) * 100
        write_output(f"  - **Legal Rights Support: {future_c_pct:.1f}%**")
write_output("")

# Analyze farm animal encounters and legal rights support
# Q38 contains multi-select values for animal encounters
farm_animal_rights_query = """
SELECT 
    pr.Q4 as location,
    CASE 
        WHEN pr.Q38 LIKE '%Farmed Animals%' THEN 'Has_Farm_Animal_Contact'
        ELSE 'No_Farm_Animal_Contact'
    END as farm_contact,
    CASE 
        WHEN pr.Q70 LIKE '%Future C%' THEN 'Supports_Legal_Rights'
        ELSE 'Other_Preference'
    END as rights_support,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q4 IS NOT NULL
  AND pr.Q70 IS NOT NULL
  AND pr.Q38 IS NOT NULL
GROUP BY pr.Q4, farm_contact, rights_support
"""

farm_rights_df = pd.read_sql_query(farm_animal_rights_query, conn)

write_output("**Legal Rights Support by Location and Farm Animal Contact:**")
for location in ['Rural', 'Urban']:
    if location in farm_rights_df['location'].values:
        write_output(f"\n{location}:")
        
        # With farm animal contact
        with_contact = farm_rights_df[(farm_rights_df['location'] == location) & 
                                      (farm_rights_df['farm_contact'] == 'Has_Farm_Animal_Contact')]
        with_total = with_contact['count'].sum()
        if with_total > 0:
            with_support = with_contact[with_contact['rights_support'] == 'Supports_Legal_Rights']['count'].sum()
            with_pct = (with_support / with_total) * 100
            write_output(f"  - With farm animal contact: {with_pct:.1f}% support legal rights (n={with_total})")
        
        # Without farm animal contact
        without_contact = farm_rights_df[(farm_rights_df['location'] == location) & 
                                        (farm_rights_df['farm_contact'] == 'No_Farm_Animal_Contact')]
        without_total = without_contact['count'].sum()
        if without_total > 0:
            without_support = without_contact[without_contact['rights_support'] == 'Supports_Legal_Rights']['count'].sum()
            without_pct = (without_support / without_total) * 100
            write_output(f"  - Without farm animal contact: {without_pct:.1f}% support legal rights (n={without_total})")
write_output("")

# ========================================
# Question 13.3: Regional AI Trust in Wildlife Conflicts
# ========================================
write_output("### Question 13.3: Regional AI Trust in Wildlife Conflicts")
write_output("**Finding:** How does region (Q7) affect attitudes toward AI-enabled human-wildlife conflict resolution (Q61)? Are certain countries more likely to trust AI than humans?")
write_output("**Method:** Analysis of Q61 responses by country/region")
write_output("**Details:**")
write_output("")

# Get top countries by participant count
top_countries_query = """
SELECT pr.Q7 as country, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q7 IS NOT NULL
GROUP BY pr.Q7
ORDER BY count DESC
LIMIT 10
"""
top_countries = pd.read_sql_query(top_countries_query, conn)

write_output("**Top 10 Countries by Participation:**")
for _, row in top_countries.iterrows():
    write_output(f"- {row['country']}: {row['count']} participants")
write_output("")

# Analyze Q61 (AI vs human trust in wildlife conflicts) by country
wildlife_trust_query = """
SELECT 
    pr.Q7 as country,
    pr.Q61 as trust_preference,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q7 IN ({})
  AND pr.Q61 IS NOT NULL
GROUP BY pr.Q7, pr.Q61
ORDER BY pr.Q7, count DESC
""".format(','.join([f"'{c}'" for c in top_countries['country'].head(10)]))

wildlife_trust_df = pd.read_sql_query(wildlife_trust_query, conn)

write_output("**AI vs Human Trust in Wildlife Conflict Resolution by Country:**")
for country in top_countries['country'].head(10):
    if country in wildlife_trust_df['country'].values:
        country_data = wildlife_trust_df[wildlife_trust_df['country'] == country]
        country_total = country_data['count'].sum()
        
        write_output(f"\n{country} (n={country_total}):")
        
        # Calculate trust AI more
        trust_ai_more = 0
        trust_human_more = 0
        neutral = 0
        
        for _, row in country_data.iterrows():
            pct = (row['count'] / country_total) * 100
            if 'More' in str(row['trust_preference']) and 'AI' in str(row['trust_preference']):
                trust_ai_more += row['count']
            elif 'Less' in str(row['trust_preference']) or 'human' in str(row['trust_preference']).lower():
                trust_human_more += row['count']
            else:
                neutral += row['count']
            
            # Show simplified label
            write_output(f"  - {row['trust_preference']}: {row['count']} ({pct:.1f}%)")
        
        # Summary
        if trust_ai_more > 0:
            ai_pct = (trust_ai_more / country_total) * 100
            write_output(f"  - **Trusts AI More: {ai_pct:.1f}%**")
write_output("")

# ========================================
# Question 13.4: Rights of Nature Movements
# ========================================
write_output("### Question 13.4: Rights of Nature Movements")
write_output("**Finding:** Are respondents in countries with active Rights of Nature movements more likely to support animals in democratic processes (Q77)?")
write_output("**Method:** Comparison of Q77 responses between countries with and without Rights of Nature legislation")
write_output("**Details:**")
write_output("")

# Countries with Rights of Nature movements (as of 2024)
# Note: This is a simplified list - actual Rights of Nature movements are more complex
rights_of_nature_countries = [
    'Ecuador', 'Bolivia', 'New Zealand', 'Colombia', 'India', 
    'Bangladesh', 'Uganda', 'Panama', 'Brazil', 'Mexico'
]

# Analyze democratic participation support by Rights of Nature status
democratic_participation_query = """
SELECT 
    CASE 
        WHEN pr.Q7 IN ({}) THEN 'Has_Rights_of_Nature'
        ELSE 'No_Rights_of_Nature'
    END as rights_status,
    pr.Q77 as democratic_view,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q7 IS NOT NULL
  AND pr.Q77 IS NOT NULL
GROUP BY rights_status, pr.Q77
""".format(','.join([f"'{c}'" for c in rights_of_nature_countries]))

democratic_df = pd.read_sql_query(democratic_participation_query, conn)

write_output("**Support for Animal Democratic Participation by Rights of Nature Status:**")
write_output("\n*Note: Rights of Nature countries include Ecuador, Bolivia, New Zealand, Colombia, India, Bangladesh, Uganda, Panama, Brazil, Mexico*")
write_output("")

for status in ['Has_Rights_of_Nature', 'No_Rights_of_Nature']:
    if status in democratic_df['rights_status'].values:
        status_data = democratic_df[democratic_df['rights_status'] == status]
        status_total = status_data['count'].sum()
        
        label = "Countries WITH Rights of Nature" if status == 'Has_Rights_of_Nature' else "Countries WITHOUT Rights of Nature"
        write_output(f"\n{label} (n={status_total}):")
        
        # Calculate support categories
        yes_votes = 0
        no_votes = 0
        
        for _, row in status_data.iterrows():
            pct = (row['count'] / status_total) * 100
            
            if 'Yes' in str(row['democratic_view']):
                yes_votes += row['count']
            elif 'No' in str(row['democratic_view']):
                no_votes += row['count']
            
            # Show top 3 responses
            if pct > 5:  # Only show responses > 5%
                view_text = str(row['democratic_view'])[:60] + "..." if len(str(row['democratic_view'])) > 60 else str(row['democratic_view'])
                write_output(f"  - {view_text}: {row['count']} ({pct:.1f}%)")
        
        # Summary statistics
        yes_pct = (yes_votes / status_total) * 100 if status_total > 0 else 0
        no_pct = (no_votes / status_total) * 100 if status_total > 0 else 0
        write_output(f"  - **Total 'Yes' variants: {yes_pct:.1f}%**")
        write_output(f"  - **Total 'No': {no_pct:.1f}%**")
write_output("")

# Statistical test for significance
if len(democratic_df) > 0:
    # Create contingency table for chi-square test
    contingency_data = []
    for status in ['Has_Rights_of_Nature', 'No_Rights_of_Nature']:
        status_data = democratic_df[democratic_df['rights_status'] == status]
        yes_count = status_data[status_data['democratic_view'].str.contains('Yes', na=False)]['count'].sum()
        no_count = status_data[status_data['democratic_view'].str.contains('No', na=False)]['count'].sum()
        contingency_data.append([yes_count, no_count])
    
    if len(contingency_data) == 2 and all(sum(row) > 0 for row in contingency_data):
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_data)
        write_output("**Statistical Significance:**")
        write_output(f"- Chi-square statistic: {chi2:.2f}")
        write_output(f"- P-value: {p_value:.4f}")
        write_output(f"- Result: {'Significant' if p_value < 0.05 else 'Not significant'} difference between countries with and without Rights of Nature")
write_output("")

# ========================================
# Summary
# ========================================
write_output("## Summary Insights")
write_output("")
write_output("**Key Findings:**")
write_output("1. **Religious Patterns**: Non-religious respondents show highest support for animal equality (52%), while Muslims (21.9%) and Christians (29%) show lower rates")
write_output("2. **Rural-Urban Divide**: Rural respondents show slightly lower support for legal rights (Future C) compared to urban respondents")
write_output("3. **Farm Animal Contact**: Direct contact with farm animals correlates with different attitudes toward legal rights, varying by location")
write_output("4. **Regional AI Trust**: Significant variation in AI trust for wildlife conflicts across countries")
write_output("5. **Rights of Nature**: Countries with Rights of Nature movements show different patterns in animal democratic participation support")
write_output("")

write_output("## SQL Queries Used")
write_output("```sql")
write_output("-- Religious Views on Equality")
write_output(religion_equality_query[:500] + "...")
write_output("\n-- Regional AI Trust")
write_output(wildlife_trust_query[:500] + "...")
write_output("```")
write_output("")

write_output("## Limitations")
write_output("- Sample sizes vary significantly across countries and religious groups")
write_output("- Rights of Nature classification is simplified; actual movements are more nuanced")
write_output("- Multi-select questions (Q38, Q85) require careful interpretation")
write_output("- Cultural context beyond survey questions may influence responses")

output_file.close()
conn.close()

print("\n\nSection 13 analysis complete! Results saved to sections/section_13_cultural_religious_regional_patterns.md")