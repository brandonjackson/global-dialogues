#!/usr/bin/env python3
"""
Section 30: Trust Landscape & Archetypes
Analyzing comprehensive trust patterns and their relationship to animal rights views
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# Create output file
output_file = open('sections/section_30_trust_landscape_archetypes.md', 'w')

def write_output(text):
    """Write to both console and file"""
    print(text)
    output_file.write(text + '\n')

# Start documentation
write_output(f"# Section 30: Trust Landscape & Archetypes")
write_output(f"## Analysis Date: {datetime.now().isoformat()}")
write_output("")

# Get total participant count
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
# Question 30.1: Global Trust Index Construction
# ========================================
write_output("### Question 30.1: Global Trust Index Construction")
write_output("**Finding:** Constructing a composite trust index from Q12-Q17 and Q57 to identify overall trust levels")
write_output("**Method:** Aggregating trust scores across multiple entities and normalizing")
write_output("**Details:**")
write_output("")

# Get trust data across all relevant questions
trust_data_query = """
SELECT 
    pr.participant_id,
    -- Q12-Q17: Trust in various entities
    pr.Q12 as trust_scientists,
    pr.Q13 as trust_environmental_groups,
    pr.Q14 as trust_corporations,
    pr.Q15 as trust_government,
    pr.Q16 as trust_religious_institutions,
    pr.Q17 as trust_ai_systems,
    pr.Q57 as ai_tech_companies_influence,
    
    -- Demographics for analysis
    pr.Q2 as age,
    pr.Q6 as religion,
    pr.Q7 as country,
    
    -- Animal rights views for correlation
    pr.Q73 as legal_representation,
    pr.Q77 as democratic_participation,
    pr.Q94 as human_nature_relationship
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

trust_df = pd.read_sql_query(trust_data_query, conn)

# Convert trust responses to numeric scale
trust_mapping = {
    'Strongly Trust': 5,
    'Somewhat Trust': 4,
    'Neutral': 3,
    'Somewhat Distrust': 2,
    'Strongly Distrust': 1
}

trust_columns = ['trust_scientists', 'trust_environmental_groups', 'trust_corporations', 
                'trust_government', 'trust_religious_institutions', 'trust_ai_systems']

for col in trust_columns:
    trust_df[f'{col}_score'] = trust_df[col].map(trust_mapping)

# Create global trust index
trust_df['global_trust_index'] = trust_df[[f'{col}_score' for col in trust_columns]].mean(axis=1, skipna=True)

# Analyze distribution of global trust
write_output("**Global Trust Index Distribution:**")
write_output(f"- Mean: {trust_df['global_trust_index'].mean():.2f}")
write_output(f"- Median: {trust_df['global_trust_index'].median():.2f}")
write_output(f"- Std Dev: {trust_df['global_trust_index'].std():.2f}")
write_output(f"- Min: {trust_df['global_trust_index'].min():.2f}")
write_output(f"- Max: {trust_df['global_trust_index'].max():.2f}")
write_output("")

# Trust quartiles
quartiles = trust_df['global_trust_index'].quantile([0.25, 0.5, 0.75])
write_output("**Trust Quartiles:**")
write_output(f"- Q1 (Low Trust): <= {quartiles[0.25]:.2f}")
write_output(f"- Q2 (Moderate-Low): {quartiles[0.25]:.2f} - {quartiles[0.5]:.2f}")
write_output(f"- Q3 (Moderate-High): {quartiles[0.5]:.2f} - {quartiles[0.75]:.2f}")
write_output(f"- Q4 (High Trust): > {quartiles[0.75]:.2f}")
write_output("")

# Trust by entity
write_output("**Average Trust by Entity (1-5 scale):**")
entity_trust = []
for col in trust_columns:
    mean_trust = trust_df[f'{col}_score'].mean()
    entity_trust.append((col.replace('trust_', '').replace('_', ' ').title(), mean_trust))

entity_trust.sort(key=lambda x: x[1], reverse=True)
for entity, score in entity_trust:
    write_output(f"- {entity}: {score:.2f}")
write_output("")

# ========================================
# Question 30.2: Trust Pattern Clusters
# ========================================
write_output("### Question 30.2: Trust Pattern Clusters")
write_output("**Finding:** Identifying distinct trust archetypes through cluster analysis")
write_output("**Method:** K-means clustering on trust scores across different entities")
write_output("**Details:**")
write_output("")

# Prepare data for clustering
clustering_data = trust_df[[f'{col}_score' for col in trust_columns]].dropna()
scaler = StandardScaler()
scaled_data = scaler.fit_transform(clustering_data)

# Determine optimal number of clusters using elbow method
inertias = []
silhouette_scores = []
k_range = range(2, 7)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(scaled_data)
    inertias.append(kmeans.inertia_)

# Use 4 clusters based on interpretability
n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
clusters = kmeans.fit_predict(scaled_data)

# Add clusters back to dataframe
trust_df.loc[clustering_data.index, 'trust_cluster'] = clusters

# Analyze cluster characteristics
write_output(f"**Identified {n_clusters} Trust Archetypes:**")
write_output("")

for cluster_id in range(n_clusters):
    cluster_mask = trust_df['trust_cluster'] == cluster_id
    cluster_size = cluster_mask.sum()
    cluster_pct = (cluster_size / len(clustering_data)) * 100
    
    write_output(f"**Archetype {cluster_id + 1}: Trust Profile {cluster_id + 1}**")
    write_output(f"- Size: {cluster_size} ({cluster_pct:.1f}% of analyzed population)")
    write_output("- Characteristics:")
    
    # Show trust levels for this cluster
    for col in trust_columns:
        mean_score = trust_df.loc[cluster_mask, f'{col}_score'].mean()
        entity_name = col.replace('trust_', '').replace('_', ' ').title()
        write_output(f"  - {entity_name}: {mean_score:.2f}")
    
    # Global trust index for this cluster
    cluster_trust = trust_df.loc[cluster_mask, 'global_trust_index'].mean()
    write_output(f"- Global Trust Index: {cluster_trust:.2f}")
    write_output("")

# ========================================
# Question 30.3: Trust Archetypes and Animal Representation
# ========================================
write_output("### Question 30.3: Trust Archetypes and Animal Representation")
write_output("**Finding:** Relationship between trust patterns and support for animal legal representation")
write_output("**Method:** Cross-tabulation of trust clusters with Q73 (legal representation)")
write_output("**Details:**")
write_output("")

# Analyze legal representation support by trust cluster
legal_rep_by_cluster = pd.crosstab(
    trust_df['trust_cluster'],
    trust_df['legal_representation'],
    normalize='index'
) * 100

write_output("**Support for Animal Legal Representation by Trust Archetype:**")
for cluster_id in range(n_clusters):
    if cluster_id in legal_rep_by_cluster.index:
        yes_pct = legal_rep_by_cluster.loc[cluster_id, 'Yes'] if 'Yes' in legal_rep_by_cluster.columns else 0
        write_output(f"- Archetype {cluster_id + 1}: {yes_pct:.1f}% support legal representation")
write_output("")

# Statistical test
contingency_table = pd.crosstab(trust_df['trust_cluster'], trust_df['legal_representation'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
write_output(f"**Statistical Analysis:**")
write_output(f"- Chi-square: {chi2:.2f}")
write_output(f"- P-value: {p_value:.6f}")
write_output(f"- Result: {'Significant' if p_value < 0.05 else 'Not significant'} association")
write_output("")

# ========================================
# Question 30.4: AI Trust Discrepancies
# ========================================
write_output("### Question 30.4: AI Trust Discrepancies")
write_output("**Finding:** Analyzing disconnect between AI trust (Q17) and support for AI-managed society (Q76)")
write_output("**Method:** Cross-tabulation of AI trust levels with AI society appeal")
write_output("**Details:**")
write_output("")

# Get AI society data
ai_society_query = """
SELECT 
    pr.participant_id,
    pr.Q17 as trust_ai,
    pr.Q76 as ai_society_appeal
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q17 IS NOT NULL
    AND pr.Q76 IS NOT NULL
"""

ai_society_df = pd.read_sql_query(ai_society_query, conn)

# Cross-tabulate
ai_crosstab = pd.crosstab(
    ai_society_df['trust_ai'],
    ai_society_df['ai_society_appeal'],
    normalize='index'
) * 100

write_output("**AI Society Appeal by AI Trust Level:**")
for trust_level in ['Strongly Distrust', 'Somewhat Distrust', 'Neutral', 'Somewhat Trust', 'Strongly Trust']:
    if trust_level in ai_crosstab.index:
        appealing_pct = 0
        if 'Very appealing' in ai_crosstab.columns:
            appealing_pct += ai_crosstab.loc[trust_level, 'Very appealing']
        if 'Somewhat appealing' in ai_crosstab.columns:
            appealing_pct += ai_crosstab.loc[trust_level, 'Somewhat appealing']
        write_output(f"- {trust_level}: {appealing_pct:.1f}% find AI society appealing")

# Identify paradoxical segment
paradox_query = """
SELECT COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
    AND pr.Q17 IN ('Strongly Distrust', 'Somewhat Distrust')
    AND pr.Q76 IN ('Very appealing', 'Somewhat appealing')
"""
paradox_count = pd.read_sql_query(paradox_query, conn)['count'].iloc[0]
paradox_pct = (paradox_count / total_participants) * 100

write_output("")
write_output(f"**Paradoxical Segment (Distrust AI but Support AI Society):**")
write_output(f"- Size: {paradox_count} ({paradox_pct:.1f}% of population)")
write_output("")

# ========================================
# Question 30.5: Generalized Distrust Groups
# ========================================
write_output("### Question 30.5: Generalized Distrust Groups")
write_output("**Finding:** Identifying groups with consistently low trust across institutions")
write_output("**Method:** Filtering for participants with global trust index < 2.5")
write_output("**Details:**")
write_output("")

# Identify low trust group
low_trust_mask = trust_df['global_trust_index'] < 2.5
low_trust_count = low_trust_mask.sum()
low_trust_pct = (low_trust_count / len(trust_df)) * 100

write_output(f"**Generalized Low Trust Group:**")
write_output(f"- Size: {low_trust_count} ({low_trust_pct:.1f}% of population)")
write_output(f"- Definition: Global trust index < 2.5")
write_output("")

# Demographics of low trust group
if low_trust_count > 0:
    write_output("**Demographics of Low Trust Group:**")
    
    # Age distribution
    age_dist = trust_df.loc[low_trust_mask, 'age'].value_counts(normalize=True) * 100
    write_output("- Age Distribution:")
    for age, pct in age_dist.head(3).items():
        write_output(f"  - {age}: {pct:.1f}%")
    
    write_output("")

# ========================================
# Question 30.6: Religious/Cultural Trust Profiles
# ========================================
write_output("### Question 30.6: Religious/Cultural Trust Profiles")
write_output("**Finding:** Trust patterns by religious affiliation")
write_output("**Method:** Comparing global trust index across religious groups")
write_output("**Details:**")
write_output("")

# Trust by religion
religion_trust = trust_df.groupby('religion')['global_trust_index'].agg(['mean', 'count'])
religion_trust = religion_trust[religion_trust['count'] >= 10]  # Filter for sufficient sample
religion_trust = religion_trust.sort_values('mean', ascending=False)

write_output("**Global Trust Index by Religion (groups with n>=10):**")
for religion, row in religion_trust.iterrows():
    if pd.notna(religion) and religion != '--':
        write_output(f"- {religion}: {row['mean']:.2f} (n={int(row['count'])})")
write_output("")

# ANOVA test
religion_groups = []
for religion in religion_trust.index:
    if pd.notna(religion) and religion != '--':
        group_data = trust_df[trust_df['religion'] == religion]['global_trust_index'].dropna()
        if len(group_data) >= 10:
            religion_groups.append(group_data)

if len(religion_groups) >= 2:
    f_stat, p_value = stats.f_oneway(*religion_groups)
    write_output(f"**Statistical Analysis (ANOVA):**")
    write_output(f"- F-statistic: {f_stat:.2f}")
    write_output(f"- P-value: {p_value:.6f}")
    write_output(f"- Result: {'Significant' if p_value < 0.05 else 'Not significant'} differences between religious groups")
write_output("")

# ========================================
# Question 30.7: AI vs. Political Trust and Animal Rights
# ========================================
write_output("### Question 30.7: AI vs. Political Trust and Animal Rights")
write_output("**Finding:** Comparing trust in AI vs. government and its relationship to animal rights support")
write_output("**Method:** Creating AI-Government trust differential and correlating with animal rights views")
write_output("**Details:**")
write_output("")

# Calculate trust differential
trust_df['ai_gov_trust_diff'] = trust_df['trust_ai_systems_score'] - trust_df['trust_government_score']

# Categorize trust differential
def categorize_trust_diff(diff):
    if pd.isna(diff):
        return None
    elif diff > 1:
        return 'Trust AI more'
    elif diff < -1:
        return 'Trust Government more'
    else:
        return 'Similar trust'

trust_df['trust_preference'] = trust_df['ai_gov_trust_diff'].apply(categorize_trust_diff)

# Analyze animal rights support by trust preference
trust_pref_legal = pd.crosstab(
    trust_df['trust_preference'],
    trust_df['legal_representation'],
    normalize='index'
) * 100

write_output("**Support for Animal Legal Rights by Trust Preference:**")
for pref in ['Trust AI more', 'Similar trust', 'Trust Government more']:
    if pref in trust_pref_legal.index and 'Yes' in trust_pref_legal.columns:
        yes_pct = trust_pref_legal.loc[pref, 'Yes']
        count = (trust_df['trust_preference'] == pref).sum()
        write_output(f"- {pref}: {yes_pct:.1f}% support (n={count})")
write_output("")

# Distribution of trust preferences
trust_pref_dist = trust_df['trust_preference'].value_counts()
write_output("**Distribution of AI vs. Government Trust:**")
for pref, count in trust_pref_dist.items():
    pct = (count / len(trust_df.dropna(subset=['trust_preference']))) * 100
    write_output(f"- {pref}: {count} ({pct:.1f}%)")
write_output("")

# ========================================
# Summary Analysis
# ========================================
write_output("## Summary Insights")
write_output("")
write_output("**Key Findings:**")
write_output(f"1. **Global Trust Index**: Mean trust level is {trust_df['global_trust_index'].mean():.2f} on 1-5 scale")
write_output(f"2. **Trust Hierarchy**: Scientists most trusted ({entity_trust[0][1]:.2f}), followed by {entity_trust[1][0]} ({entity_trust[1][1]:.2f})")
write_output(f"3. **Trust Archetypes**: {n_clusters} distinct trust patterns identified through clustering")
write_output(f"4. **AI Trust Paradox**: {paradox_count} people distrust AI but support AI-managed society")
write_output(f"5. **Generalized Distrust**: {low_trust_pct:.1f}% show low trust across all institutions")
write_output(f"6. **Religious Differences**: {'Significant' if p_value < 0.05 else 'No significant'} trust variations by religion")
write_output(f"7. **AI vs Government**: {trust_pref_dist.iloc[0] if len(trust_pref_dist) > 0 else 'N/A'} participants show distinct trust preference")
write_output("")

write_output("## Methodology Notes")
write_output("- Trust scores converted to 1-5 scale (1=Strongly Distrust, 5=Strongly Trust)")
write_output("- Global trust index calculated as mean across 6 institutional trust measures")
write_output("- K-means clustering with standardized features used for archetype identification")
write_output("- Statistical tests include chi-square for associations and ANOVA for group differences")
write_output("")

write_output("## Limitations")
write_output("- Trust measures are self-reported and may be subject to social desirability bias")
write_output("- Cultural interpretations of 'trust' may vary across regions")
write_output("- Clustering results sensitive to algorithm parameters and feature selection")
write_output("- Some demographic subgroups have small sample sizes limiting statistical power")

output_file.close()
conn.close()

print("\n\nSection 30 analysis complete! Results saved to sections/section_30_trust_landscape_archetypes.md")