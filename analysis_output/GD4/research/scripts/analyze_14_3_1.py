import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Section 14.3.1: AI Infidelity Perception
# Among respondents in a committed relationship, what is the exact percentage who would consider 
# their partner's use of an AI for sexual or romantic gratification to be a form of infidelity?

print("\n" + "="*80)
print("14.3.1 Is AI Infidelity? Views from Committed Relationships")
print("="*80)

# Get participant data with relationship status and infidelity views
query = """
SELECT 
    pr.participant_id,
    pr.Q126 as ai_infidelity_view,  -- Consider AI romantic/sexual use as infidelity
    pr.Q62 as relationship_status,  -- Current relationship status
    pr.Q3 as gender,
    pr.Q2 as age_group,
    pr.Q7 as country,
    pr.Q97 as romantic_ai_openness,  -- Personal openness to AI romance
    pr.Q67 as ai_companionship,  -- Have used AI for companionship
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# 1. Overall relationship status distribution
print("\n1. Relationship Status Distribution:")
relationship_counts = df['relationship_status'].value_counts()
for status, count in relationship_counts.items():
    pct = (count / len(df)) * 100
    print(f"   {status}: {count} ({pct:.1f}%)")

# 2. Filter for committed relationships
# Assuming committed includes married, in relationship, etc. - need to check actual values
committed_statuses = ['Married', 'In a relationship', 'Partnered', 'Engaged']
# First let's see what statuses exist
unique_statuses = df['relationship_status'].unique()
print(f"\nUnique relationship statuses: {unique_statuses}")

# Identify committed relationships based on actual data
# Committed includes: Married, In a committed romantic relationship, Cohabiting, Civil union
committed = df[df['relationship_status'].str.contains('Married|committed romantic relationship|Cohabiting|civil union', 
                                                      case=False, na=False)]
single = df[df['relationship_status'].str.contains('Single|Divorced|Widowed|Separated', 
                                                   case=False, na=False)]

print(f"\n2. Committed Relationships: {len(committed)} ({len(committed)/len(df)*100:.1f}%)")
print(f"   Single/Not Committed: {len(single)} ({len(single)/len(df)*100:.1f}%)")

# 3. AI infidelity views among committed relationships
if len(committed) > 0:
    print("\n3. AI Infidelity Views Among Committed Relationships:")
    infidelity_counts = committed['ai_infidelity_view'].value_counts()
    for view, count in infidelity_counts.items():
        pct = (count / len(committed)) * 100
        print(f"   {view}: {count} ({pct:.1f}%)")
    
    # Calculate percentage who consider it infidelity
    consider_infidelity = committed[committed['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
    definitely_infidelity = committed[committed['ai_infidelity_view'].str.contains('definitely', case=False, na=False)]
    possibly_infidelity = committed[committed['ai_infidelity_view'].str.contains('possibly', case=False, na=False)]
    
    print(f"\n   CONSIDER IT INFIDELITY (Any Yes): {len(consider_infidelity)} ({len(consider_infidelity)/len(committed)*100:.1f}%)")
    if len(definitely_infidelity) > 0:
        print(f"   - Definitely infidelity: {len(definitely_infidelity)} ({len(definitely_infidelity)/len(committed)*100:.1f}%)")
    if len(possibly_infidelity) > 0:
        print(f"   - Possibly infidelity: {len(possibly_infidelity)} ({len(possibly_infidelity)/len(committed)*100:.1f}%)")

# 4. Compare with single people's views
if len(single) > 0:
    print("\n4. Comparison - Single People's Views:")
    single_infidelity = single[single['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
    print(f"   Single people who'd consider it infidelity: {len(single_infidelity)} ({len(single_infidelity)/len(single)*100:.1f}%)")

# 5. Gender differences among committed
if len(committed) > 0:
    print("\n5. Gender Differences (Committed Relationships):")
    for gender in committed['gender'].unique():
        if pd.notna(gender):
            gender_group = committed[committed['gender'] == gender]
            gender_yes = gender_group[gender_group['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
            print(f"   {gender}: {len(gender_yes)}/{len(gender_group)} ({len(gender_yes)/len(gender_group)*100:.1f}%) consider it infidelity")

# 6. Age differences among committed
if len(committed) > 0:
    print("\n6. Age Differences (Committed Relationships):")
    age_order = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    for age in age_order:
        age_group = committed[committed['age_group'] == age]
        if len(age_group) > 0:
            age_yes = age_group[age_group['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
            print(f"   {age}: {len(age_yes)}/{len(age_group)} ({len(age_yes)/len(age_group)*100:.1f}%) consider it infidelity")

# 7. Country differences (top 5)
if len(committed) > 0:
    print("\n7. Top 5 Countries (Committed Relationships):")
    top_countries = committed['country'].value_counts().head(5).index
    for country in top_countries:
        country_group = committed[committed['country'] == country]
        country_yes = country_group[country_group['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        print(f"   {country}: {len(country_yes)}/{len(country_group)} ({len(country_yes)/len(country_group)*100:.1f}%) consider it infidelity")

# 8. Personal AI romance openness vs infidelity views
if len(committed) > 0:
    print("\n8. Personal Openness to AI Romance vs Infidelity Views (Committed):")
    
    # Those open to AI romance
    open_to_romance = committed[committed['romantic_ai_openness'].str.contains('Yes', case=False, na=False)]
    if len(open_to_romance) > 0:
        open_infidelity = open_to_romance[open_to_romance['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        print(f"   Open to AI romance: {len(open_infidelity)}/{len(open_to_romance)} ({len(open_infidelity)/len(open_to_romance)*100:.1f}%) still consider partner's use infidelity")
    
    # Those closed to AI romance
    closed_to_romance = committed[committed['romantic_ai_openness'].str.contains('No, definitely', case=False, na=False)]
    if len(closed_to_romance) > 0:
        closed_infidelity = closed_to_romance[closed_to_romance['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        print(f"   Closed to AI romance: {len(closed_infidelity)}/{len(closed_to_romance)} ({len(closed_infidelity)/len(closed_to_romance)*100:.1f}%) consider it infidelity")

# 9. AI companionship users vs non-users
if len(committed) > 0:
    print("\n9. AI Companionship Experience (Committed Relationships):")
    
    companions = committed[committed['ai_companionship'] == 'Yes']
    non_companions = committed[committed['ai_companionship'] == 'No']
    
    if len(companions) > 0:
        comp_infidelity = companions[companions['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        print(f"   AI companionship users: {len(comp_infidelity)}/{len(companions)} ({len(comp_infidelity)/len(companions)*100:.1f}%) consider it infidelity")
    
    if len(non_companions) > 0:
        non_comp_infidelity = non_companions[non_companions['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        print(f"   Non-users: {len(non_comp_infidelity)}/{len(non_companions)} ({len(non_comp_infidelity)/len(non_companions)*100:.1f}%) consider it infidelity")

# 10. Statistical test for relationship status effect
print("\n10. Statistical Analysis:")
# Create binary variable for infidelity view
df['considers_infidelity'] = df['ai_infidelity_view'].str.contains('Yes', case=False, na=False)
df['is_committed'] = df['relationship_status'].str.contains('Married|relationship|Partnered|Engaged', 
                                                           case=False, na=False)

# Chi-square test
contingency = pd.crosstab(df['is_committed'], df['considers_infidelity'])
chi2, p_value, dof, expected = chi2_contingency(contingency)
print(f"   Chi-square test (relationship status vs infidelity view):")
print(f"   χ² = {chi2:.3f}, p = {p_value:.4f}")

if p_value < 0.05:
    print("   Significant difference between committed and non-committed views")
else:
    print("   No significant difference between committed and non-committed views")

conn.close()

print("\n" + "="*80)
if len(committed) > 0 and len(consider_infidelity) > 0:
    print(f"Key Finding: {len(consider_infidelity)/len(committed)*100:.1f}% of people in committed relationships")
    print("would consider their partner's use of AI for sexual/romantic gratification as infidelity.")
    
    # Highlight gender difference if substantial
    male_committed = committed[committed['gender'] == 'Male']
    female_committed = committed[committed['gender'] == 'Female']
    if len(male_committed) > 0 and len(female_committed) > 0:
        male_yes = male_committed[male_committed['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        female_yes = female_committed[female_committed['ai_infidelity_view'].str.contains('Yes', case=False, na=False)]
        male_pct = len(male_yes)/len(male_committed)*100
        female_pct = len(female_yes)/len(female_committed)*100
        if abs(male_pct - female_pct) > 10:
            print(f"Notable gender gap: {female_pct:.1f}% of women vs {male_pct:.1f}% of men")
print("="*80)