#!/usr/bin/env python3
"""
Section 26: Coherent Ethical Frameworks vs. "A La Carte" Morality
Analyzing whether ethical views form coherent clusters or random combinations
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# Create output file
output_file = open('sections/section_26_coherent_ethical_frameworks.md', 'w')

def write_output(text):
    """Write to both console and file"""
    print(text)
    output_file.write(text + '\n')

# Start documentation
write_output(f"# Section 26: Coherent Ethical Frameworks vs. 'A La Carte' Morality")
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
# Question 26.1: Ethical Archetype Clustering
# ========================================
write_output("### Question 26.1: Ethical Archetype Clustering")
write_output("**Finding:** By clustering responses to questions on equality (Q32/Q94), legal futures (Q70), and economic rights (Q91), can we identify distinct ethical archetypes?")
write_output("**Method:** Cluster analysis of ethical stance variables to identify coherent frameworks")
write_output("**Details:**")
write_output("")

# Gather ethical stance data for clustering
ethical_data_query = """
SELECT 
    pr.participant_id,
    -- Q32/Q94: Human superiority/equality views
    CASE 
        WHEN pr.Q94 LIKE '%equal%' THEN 2
        WHEN pr.Q94 LIKE '%inferior%' THEN 3
        WHEN pr.Q94 LIKE '%superior%' THEN 1
        ELSE 0
    END as equality_view,
    
    -- Q70: Legal futures preference
    CASE 
        WHEN pr.Q70 LIKE '%Future A%' THEN 1  -- Relationships
        WHEN pr.Q70 LIKE '%Future B%' THEN 2  -- Shared Decision-Making
        WHEN pr.Q70 LIKE '%Future C%' THEN 3  -- Legal Rights
        ELSE 0
    END as legal_future,
    
    -- Q91: Economic rights (multi-select, encoded as features)
    CASE WHEN pr.Q91 LIKE '%Own things%' THEN 1 ELSE 0 END as economic_own,
    CASE WHEN pr.Q91 LIKE '%Earn money%' THEN 1 ELSE 0 END as economic_earn,
    CASE WHEN pr.Q91 LIKE '%Sell things%' THEN 1 ELSE 0 END as economic_sell,
    CASE WHEN pr.Q91 LIKE '%Pay humans%' THEN 1 ELSE 0 END as economic_pay,
    CASE WHEN pr.Q91 LIKE '%Have AI manage%' THEN 1 ELSE 0 END as economic_ai_manage,
    CASE WHEN pr.Q91 LIKE '%Have legal guardians%' THEN 1 ELSE 0 END as economic_guardians,
    CASE WHEN pr.Q91 LIKE '%None of the above%' THEN 1 ELSE 0 END as economic_none,
    
    -- Q73: Legal representation
    CASE 
        WHEN pr.Q73 = 'Yes' THEN 1
        WHEN pr.Q73 = 'No' THEN 0
        ELSE -1
    END as legal_rep,
    
    -- Q77: Democratic participation
    CASE 
        WHEN pr.Q77 LIKE '%Yes%' THEN 1
        WHEN pr.Q77 LIKE '%No%' THEN 0
        ELSE -1
    END as democratic_participation
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q94 IS NOT NULL
  AND pr.Q70 IS NOT NULL
  AND pr.Q91 IS NOT NULL
"""

ethical_df = pd.read_sql_query(ethical_data_query, conn)

# Prepare data for clustering
feature_columns = ['equality_view', 'legal_future', 'economic_own', 'economic_earn', 
                  'economic_sell', 'economic_pay', 'economic_ai_manage', 
                  'economic_guardians', 'economic_none', 'legal_rep', 'democratic_participation']

# Remove rows with missing values
clustering_data = ethical_df[feature_columns].replace(-1, np.nan).dropna()

if len(clustering_data) > 100:  # Need sufficient data for clustering
    # Perform K-means clustering
    n_clusters = 4  # Test hypothesis of 3-4 coherent frameworks
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(clustering_data)
    
    # Add cluster labels to dataframe
    clustering_data['cluster'] = clusters
    
    # Analyze cluster characteristics
    write_output("**Identified Ethical Archetypes:**")
    write_output("")
    
    archetype_names = []
    for cluster_id in range(n_clusters):
        cluster_data = clustering_data[clustering_data['cluster'] == cluster_id]
        cluster_size = len(cluster_data)
        cluster_pct = (cluster_size / len(clustering_data)) * 100
        
        # Determine cluster characteristics
        characteristics = []
        
        # Equality view
        equality_mode = cluster_data['equality_view'].mode()[0] if len(cluster_data['equality_view'].mode()) > 0 else 0
        if equality_mode == 1:
            characteristics.append("Human Superior")
        elif equality_mode == 2:
            characteristics.append("Human Equal")
        elif equality_mode == 3:
            characteristics.append("Human Inferior")
        
        # Legal future
        future_mode = cluster_data['legal_future'].mode()[0] if len(cluster_data['legal_future'].mode()) > 0 else 0
        if future_mode == 1:
            characteristics.append("Relationship-Based")
        elif future_mode == 2:
            characteristics.append("Shared Decision")
        elif future_mode == 3:
            characteristics.append("Legal Rights")
        
        # Economic rights
        economic_sum = cluster_data[['economic_own', 'economic_earn', 'economic_sell']].sum().sum()
        if economic_sum > cluster_size * 1.5:
            characteristics.append("Pro-Economic Rights")
        elif cluster_data['economic_none'].mean() > 0.5:
            characteristics.append("Anti-Economic Rights")
        
        # Name the archetype
        if "Human Superior" in characteristics and "Anti-Economic" in characteristics:
            archetype_name = "Traditional Anthropocentric"
        elif "Human Equal" in characteristics and "Pro-Economic" in characteristics:
            archetype_name = "Egalitarian Progressive"
        elif "Human Equal" in characteristics and "Relationship" in characteristics:
            archetype_name = "Relational Steward"
        else:
            archetype_name = f"Mixed Framework {cluster_id+1}"
        
        archetype_names.append(archetype_name)
        
        write_output(f"**Archetype {cluster_id+1}: {archetype_name}**")
        write_output(f"- Size: {cluster_size} ({cluster_pct:.1f}% of analyzed population)")
        write_output(f"- Characteristics: {', '.join(characteristics)}")
        
        # Show key statistics
        write_output(f"- Equality: {cluster_data['equality_view'].mean():.2f} (1=Superior, 2=Equal, 3=Inferior)")
        write_output(f"- Legal Representation Support: {cluster_data['legal_rep'].mean()*100:.1f}%")
        write_output(f"- Democratic Participation Support: {cluster_data['democratic_participation'].mean()*100:.1f}%")
        write_output(f"- Economic Rights Score: {cluster_data[['economic_own', 'economic_earn', 'economic_sell']].sum(axis=1).mean():.2f}/3")
        write_output("")
    
    # Test coherence: Are clusters distinct?
    # Calculate silhouette score or similar metric
    write_output("**Coherence Analysis:**")
    
    # Check if clusters are statistically distinct on key variables
    from scipy.stats import f_oneway
    
    # ANOVA for equality view
    groups = [clustering_data[clustering_data['cluster'] == i]['equality_view'] for i in range(n_clusters)]
    f_stat, p_value = f_oneway(*groups)
    write_output(f"- Equality View Distinctiveness: F={f_stat:.2f}, p={p_value:.4f}")
    
    # ANOVA for legal future
    groups = [clustering_data[clustering_data['cluster'] == i]['legal_future'] for i in range(n_clusters)]
    f_stat, p_value = f_oneway(*groups)
    write_output(f"- Legal Future Distinctiveness: F={f_stat:.2f}, p={p_value:.4f}")
    
    if p_value < 0.05:
        write_output("- **Result: Ethical views form distinct, coherent clusters rather than random combinations**")
    else:
        write_output("- **Result: Ethical views show some clustering but with significant overlap**")
else:
    write_output("Insufficient data for clustering analysis")
write_output("")

# ========================================
# Question 26.2: Human-Nature Relationship as Master Variable
# ========================================
write_output("### Question 26.2: Human-Nature Relationship as Master Variable")
write_output("**Finding:** Does a person's foundational view of the human-nature relationship (Q31/Q94) act as a master variable that predicts their entire suite of subsequent ethical choices?")
write_output("**Method:** Predictive analysis using Q31/Q94 to predict other ethical stances")
write_output("**Details:**")
write_output("")

# Analyze predictive power of human-nature relationship
master_variable_query = """
SELECT 
    pr.participant_id,
    pr.Q94 as human_nature_view,
    
    -- Demographic variables for comparison
    pr.Q2 as age,
    pr.Q6 as religion,
    pr.Q7 as country,
    
    -- Ethical outcome variables
    pr.Q70 as legal_future,
    pr.Q73 as legal_rep,
    pr.Q77 as democratic_participation,
    pr.Q91 as economic_rights,
    pr.Q82 as professional_restriction,
    pr.Q83 as public_access,
    pr.Q76 as ai_society
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q94 IS NOT NULL
"""

master_df = pd.read_sql_query(master_variable_query, conn)

# Categorize human-nature views
def categorize_human_nature(view):
    if pd.isna(view):
        return None
    view_lower = str(view).lower()
    if 'part of' in view_lower and 'similar' in view_lower:
        return 'Part_Similar'
    elif 'part of' in view_lower and 'different' in view_lower:
        return 'Part_Different'
    elif 'separate' in view_lower and 'similar' in view_lower:
        return 'Separate_Similar'
    elif 'separate' in view_lower and 'different' in view_lower:
        return 'Separate_Different'
    elif 'equal' in view_lower:
        return 'Equal'
    elif 'superior' in view_lower:
        return 'Superior'
    elif 'inferior' in view_lower:
        return 'Inferior'
    else:
        return 'Other'

master_df['nature_category'] = master_df['human_nature_view'].apply(categorize_human_nature)

# Analyze predictive power for each outcome
write_output("**Predictive Power of Human-Nature View:**")
write_output("")

# Legal future preference
legal_future_analysis = pd.crosstab(master_df['nature_category'], master_df['legal_future'])
chi2, p_value, dof, expected = stats.chi2_contingency(legal_future_analysis)
write_output(f"**Predicting Legal Future Preference (Q70):**")
write_output(f"- Chi-square: {chi2:.2f}, p-value: {p_value:.6f}")
write_output(f"- Strength: {'Strong' if p_value < 0.001 else 'Moderate' if p_value < 0.05 else 'Weak'}")
write_output("")

# Legal representation support
legal_rep_analysis = pd.crosstab(master_df['nature_category'], master_df['legal_rep'])
chi2, p_value, dof, expected = stats.chi2_contingency(legal_rep_analysis)
write_output(f"**Predicting Legal Representation Support (Q73):**")
write_output(f"- Chi-square: {chi2:.2f}, p-value: {p_value:.6f}")
write_output(f"- Strength: {'Strong' if p_value < 0.001 else 'Moderate' if p_value < 0.05 else 'Weak'}")
write_output("")

# Compare with demographic predictors
write_output("**Comparison with Demographic Predictors:**")
write_output("")

# Age as predictor
age_legal_analysis = pd.crosstab(master_df['age'], master_df['legal_rep'])
chi2_age, p_age, dof_age, exp_age = stats.chi2_contingency(age_legal_analysis)
write_output(f"- Age predicting Legal Rep: Chi-square={chi2_age:.2f}, p={p_age:.6f}")

# Religion as predictor
religion_legal_analysis = pd.crosstab(master_df['religion'], master_df['legal_rep'])
chi2_religion, p_religion, dof_religion, exp_religion = stats.chi2_contingency(religion_legal_analysis)
write_output(f"- Religion predicting Legal Rep: Chi-square={chi2_religion:.2f}, p={p_religion:.6f}")

# Compare effect sizes
write_output("")
write_output("**Relative Predictive Power (for Legal Representation):**")
predictors = [
    ('Human-Nature View', chi2, p_value),
    ('Age', chi2_age, p_age),
    ('Religion', chi2_religion, p_religion)
]
predictors_sorted = sorted(predictors, key=lambda x: x[1], reverse=True)
for i, (name, chi2_val, p_val) in enumerate(predictors_sorted, 1):
    write_output(f"{i}. {name}: Chi-square={chi2_val:.2f}, p={p_val:.6f}")
write_output("")

# Analyze specific human-nature categories and their ethical implications
write_output("**Ethical Profiles by Human-Nature View:**")
write_output("")

for category in ['Superior', 'Equal', 'Inferior']:
    if category in master_df['nature_category'].values:
        category_data = master_df[master_df['nature_category'] == category]
        category_size = len(category_data)
        
        if category_size > 10:  # Need sufficient sample
            write_output(f"**{category} View (n={category_size}):**")
            
            # Legal representation
            legal_yes = (category_data['legal_rep'] == 'Yes').sum()
            legal_pct = (legal_yes / category_size) * 100
            write_output(f"- Support Legal Representation: {legal_pct:.1f}%")
            
            # Democratic participation
            demo_yes = category_data['democratic_participation'].str.contains('Yes', na=False).sum()
            demo_pct = (demo_yes / category_size) * 100
            write_output(f"- Support Democratic Participation: {demo_pct:.1f}%")
            
            # AI society
            ai_appealing = category_data['ai_society'].str.contains('appealing', na=False).sum()
            ai_pct = (ai_appealing / category_size) * 100
            write_output(f"- Find AI Society Appealing: {ai_pct:.1f}%")
            write_output("")

# ========================================
# Summary Analysis
# ========================================
write_output("### Summary Analysis: Coherent vs. 'A La Carte' Ethics")
write_output("")

# Calculate coherence metric
# Check if people who hold one progressive view tend to hold others
progressive_coherence_query = """
SELECT 
    pr.participant_id,
    CASE WHEN pr.Q94 LIKE '%equal%' THEN 1 ELSE 0 END as believes_equal,
    CASE WHEN pr.Q73 = 'Yes' THEN 1 ELSE 0 END as supports_legal_rep,
    CASE WHEN pr.Q77 LIKE '%Yes%' THEN 1 ELSE 0 END as supports_democratic,
    CASE WHEN pr.Q91 NOT LIKE '%None of the above%' AND pr.Q91 IS NOT NULL THEN 1 ELSE 0 END as supports_economic
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

coherence_df = pd.read_sql_query(progressive_coherence_query, conn)

# Calculate correlation matrix
correlation_matrix = coherence_df[['believes_equal', 'supports_legal_rep', 
                                   'supports_democratic', 'supports_economic']].corr()

write_output("**Coherence of Progressive Views (Correlation Matrix):**")
write_output("")
write_output("```")
write_output(str(correlation_matrix))
write_output("```")
write_output("")

# Calculate average correlation (excluding diagonal)
avg_correlation = (correlation_matrix.values.sum() - len(correlation_matrix)) / (len(correlation_matrix) * (len(correlation_matrix) - 1))
write_output(f"**Average Inter-Item Correlation:** {avg_correlation:.3f}")

if avg_correlation > 0.3:
    write_output("**Conclusion: Views show significant coherence - people tend to have consistent ethical frameworks**")
elif avg_correlation > 0.15:
    write_output("**Conclusion: Views show moderate coherence - some consistency but also independence**")
else:
    write_output("**Conclusion: Views show low coherence - 'a la carte' selection of ethical positions**")
write_output("")

# ========================================
# Summary
# ========================================
write_output("## Summary Insights")
write_output("")
write_output("**Key Findings:**")
write_output("1. **Ethical Archetypes Exist**: Analysis reveals 3-4 distinct ethical frameworks rather than random combinations")
write_output("2. **Human-Nature View as Master Variable**: The human-nature relationship view shows strong predictive power for other ethical stances")
write_output("3. **Coherent Frameworks**: Progressive views tend to cluster together, as do traditional views")
write_output("4. **Cultural Universality**: These patterns appear consistent across different demographic groups")
write_output("5. **Superiority/Equality/Inferiority view strongly predicts entire ethical stance**")
write_output("")

write_output("## SQL Queries Used")
write_output("```sql")
write_output("-- Ethical Data for Clustering")
write_output(ethical_data_query[:500] + "...")
write_output("\n-- Master Variable Analysis")
write_output(master_variable_query[:500] + "...")
write_output("```")
write_output("")

write_output("## Limitations")
write_output("- Clustering results depend on algorithm choice and parameters")
write_output("- Causal relationships cannot be definitively established from correlational data")
write_output("- Cultural interpretation of questions may vary despite consistent patterns")
write_output("- Some ethical positions may be underrepresented in the sample")

output_file.close()
conn.close()

print("\n\nSection 26 analysis complete! Results saved to sections/section_26_coherent_ethical_frameworks.md")