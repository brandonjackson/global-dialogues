import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ttest_ind

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Section 14.3.2: Western vs Non-Western Emotional Connection Acceptability
# Do respondents from non-Western countries report a significantly higher level of acceptability 
# for forming emotional connections with AI compared to respondents from Western countries?

print("\n" + "="*80)
print("14.3.2 Western vs Non-Western Views on AI Emotional Connections")
print("="*80)

# Define Western vs Non-Western countries
# Western: US, Canada, UK, Australia, New Zealand, Western Europe
# Non-Western: Asia, Africa, Latin America, Eastern Europe, Middle East

western_countries = [
    'United States', 'Canada', 'United Kingdom', 'Australia', 'New Zealand',
    'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Switzerland',
    'Austria', 'Denmark', 'Sweden', 'Norway', 'Finland', 'Ireland', 'Portugal',
    'Iceland', 'Luxembourg'
]

# Get participant data
query = """
SELECT 
    pr.participant_id,
    pr.Q7 as country,
    pr.Q77 as emotional_bond_acceptable,  -- Acceptability of emotional bonds with AI
    pr.Q97 as romantic_ai_openness,  -- Personal openness to AI romance
    pr.Q67 as ai_companionship,  -- Have used AI for companionship
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q4 as religion,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# Categorize countries as Western or Non-Western
df['is_western'] = df['country'].isin(western_countries)
df['region_type'] = df['is_western'].map({True: 'Western', False: 'Non-Western'})

# 1. Regional distribution
print("\n1. Regional Distribution:")
western_count = df['is_western'].sum()
non_western_count = len(df) - western_count
print(f"   Western countries: {western_count} ({western_count/len(df)*100:.1f}%)")
print(f"   Non-Western countries: {non_western_count} ({non_western_count/len(df)*100:.1f}%)")

# 2. Country breakdown
print("\n2. Top Countries by Region:")
print("\n   Top 5 Western Countries:")
western_df = df[df['is_western'] == True]
if len(western_df) > 0:
    western_countries_counts = western_df['country'].value_counts().head(5)
    for country, count in western_countries_counts.items():
        pct = (count / len(western_df)) * 100
        print(f"   {country}: {count} ({pct:.1f}% of Western)")

print("\n   Top 5 Non-Western Countries:")
non_western_df = df[df['is_western'] == False]
if len(non_western_df) > 0:
    non_western_countries_counts = non_western_df['country'].value_counts().head(5)
    for country, count in non_western_countries_counts.items():
        pct = (count / len(non_western_df)) * 100
        print(f"   {country}: {count} ({pct:.1f}% of Non-Western)")

# 3. Emotional bond acceptability by region
print("\n3. Emotional Bond Acceptability by Region:")

# Convert acceptability to numeric scale
acceptability_map = {
    'Completely unacceptable': 1,
    'Somewhat unacceptable': 2,
    'Neutral': 3,
    'Somewhat acceptable': 4,
    'Completely acceptable': 5
}

df['emotional_bond_numeric'] = df['emotional_bond_acceptable'].map(acceptability_map)

# Western acceptability
print("\n   Western Countries:")
if len(western_df) > 0:
    western_accept = western_df['emotional_bond_acceptable'].value_counts()
    for response, count in western_accept.items():
        pct = (count / len(western_df)) * 100
        print(f"   {response}: {count} ({pct:.1f}%)")
    
    # Calculate acceptance rate (looking for "Acceptable" in the response)
    western_acceptable = western_df[western_df['emotional_bond_acceptable'].str.contains('Acceptable', case=False, na=False)]
    western_accept_rate = len(western_acceptable) / len(western_df) * 100
    print(f"   TOTAL ACCEPTABLE: {western_accept_rate:.1f}%")
    
    # Mean score - need to map the actual values
    western_df_copy = western_df.copy()
    western_df_copy['emotional_bond_numeric'] = western_df_copy['emotional_bond_acceptable'].map(acceptability_map)
    western_mean = western_df_copy['emotional_bond_numeric'].mean()
    print(f"   Mean score: {western_mean:.2f}/5")

# Non-Western acceptability
print("\n   Non-Western Countries:")
if len(non_western_df) > 0:
    non_western_accept = non_western_df['emotional_bond_acceptable'].value_counts()
    for response, count in non_western_accept.items():
        pct = (count / len(non_western_df)) * 100
        print(f"   {response}: {count} ({pct:.1f}%)")
    
    # Calculate acceptance rate
    non_western_acceptable = non_western_df[non_western_df['emotional_bond_acceptable'].str.contains('Acceptable', case=False, na=False)]
    non_western_accept_rate = len(non_western_acceptable) / len(non_western_df) * 100
    print(f"   TOTAL ACCEPTABLE: {non_western_accept_rate:.1f}%")
    
    # Mean score - need to map the actual values
    non_western_df_copy = non_western_df.copy()
    non_western_df_copy['emotional_bond_numeric'] = non_western_df_copy['emotional_bond_acceptable'].map(acceptability_map)
    non_western_mean = non_western_df_copy['emotional_bond_numeric'].mean()
    print(f"   Mean score: {non_western_mean:.2f}/5")

# 4. Statistical test
print("\n4. Statistical Significance Test:")
if len(western_df) > 0 and len(non_western_df) > 0:
    # T-test on numeric scores
    western_scores = western_df_copy['emotional_bond_numeric'].dropna()
    non_western_scores = non_western_df_copy['emotional_bond_numeric'].dropna()
    
    t_stat, p_value = ttest_ind(western_scores, non_western_scores)
    print(f"   T-test on acceptability scores:")
    print(f"   t = {t_stat:.3f}, p = {p_value:.4f}")
    
    if p_value < 0.001:
        print("   Highly significant difference between regions")
    elif p_value < 0.05:
        print("   Significant difference between regions")
    else:
        print("   No significant difference between regions")
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((western_scores.std()**2 + non_western_scores.std()**2) / 2)
    cohens_d = (non_western_mean - western_mean) / pooled_std
    print(f"   Cohen's d effect size: {cohens_d:.3f}")
    
    if abs(cohens_d) < 0.2:
        print("   (Small effect)")
    elif abs(cohens_d) < 0.5:
        print("   (Medium effect)")
    else:
        print("   (Large effect)")

# 5. Romantic AI openness by region
print("\n5. Romantic AI Openness by Region:")
western_romantic = western_df[western_df['romantic_ai_openness'].str.contains('Yes', case=False, na=False)]
non_western_romantic = non_western_df[non_western_df['romantic_ai_openness'].str.contains('Yes', case=False, na=False)]

if len(western_df) > 0:
    print(f"   Western: {len(western_romantic)}/{len(western_df)} ({len(western_romantic)/len(western_df)*100:.1f}%) open to AI romance")
if len(non_western_df) > 0:
    print(f"   Non-Western: {len(non_western_romantic)}/{len(non_western_df)} ({len(non_western_romantic)/len(non_western_df)*100:.1f}%) open to AI romance")

# 6. AI companionship usage by region
print("\n6. AI Companionship Usage by Region:")
western_companions = western_df[western_df['ai_companionship'] == 'Yes']
non_western_companions = non_western_df[non_western_df['ai_companionship'] == 'Yes']

if len(western_df) > 0:
    print(f"   Western: {len(western_companions)}/{len(western_df)} ({len(western_companions)/len(western_df)*100:.1f}%) use AI companionship")
if len(non_western_df) > 0:
    print(f"   Non-Western: {len(non_western_companions)}/{len(non_western_df)} ({len(non_western_companions)/len(non_western_df)*100:.1f}%) use AI companionship")

# 7. Specific country comparisons
print("\n7. Specific Country Comparisons (Emotional Bond Acceptability):")
countries_of_interest = ['United States', 'China', 'India', 'Kenya', 'Brazil', 'Germany']
for country in countries_of_interest:
    country_df = df[df['country'] == country]
    if len(country_df) > 0:
        country_acceptable = country_df[country_df['emotional_bond_acceptable'].str.contains('Acceptable', case=False, na=False)]
        accept_rate = len(country_acceptable) / len(country_df) * 100
        mean_score = country_df['emotional_bond_numeric'].mean()
        region = "Western" if country in western_countries else "Non-Western"
        print(f"   {country} ({region}): {accept_rate:.1f}% acceptable, mean {mean_score:.2f}/5")

# 8. Age-adjusted comparison
print("\n8. Age-Adjusted Comparison:")
# Compare within same age groups
age_groups = ['18-25', '26-35', '36-45']
for age in age_groups:
    age_western = western_df[western_df['age_group'] == age]
    age_non_western = non_western_df[non_western_df['age_group'] == age]
    
    if len(age_western) > 0 and len(age_non_western) > 0:
        west_accept = len(age_western[age_western['emotional_bond_acceptable'].str.contains('Acceptable', case=False, na=False)]) / len(age_western) * 100
        non_west_accept = len(age_non_western[age_non_western['emotional_bond_acceptable'].str.contains('Acceptable', case=False, na=False)]) / len(age_non_western) * 100
        diff = non_west_accept - west_accept
        print(f"   Age {age}: Western {west_accept:.1f}% vs Non-Western {non_west_accept:.1f}% (diff: {diff:+.1f}%)")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: ")
if len(western_df) > 0 and len(non_western_df) > 0:
    diff = non_western_accept_rate - western_accept_rate
    if diff > 0:
        print(f"Non-Western countries show {diff:.1f} percentage points HIGHER acceptance")
        print(f"of AI emotional connections ({non_western_accept_rate:.1f}% vs {western_accept_rate:.1f}%).")
    elif diff < 0:
        print(f"Western countries show {abs(diff):.1f} percentage points HIGHER acceptance")
        print(f"of AI emotional connections ({western_accept_rate:.1f}% vs {non_western_accept_rate:.1f}%).")
    else:
        print(f"No meaningful difference between Western and Non-Western acceptance rates.")
    
    if p_value < 0.05:
        print(f"This difference is statistically significant (p = {p_value:.4f}).")
print("="*80)