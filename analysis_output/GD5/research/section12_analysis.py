import sqlite3
import pandas as pd
import numpy as np

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=" * 80)
print("SECTION 12: ETHICS, RIGHTS, AND GOVERNANCE")
print("=" * 80)

# Question 12.1: Prohibited Communication Consensus
print("\n12.1. Prohibited Communication Consensus")
print("-" * 40)

query_q85 = """
SELECT response, 
       "all" as global_consensus,
       africa, asia, europe, north_america, south_america, oceania
FROM responses
WHERE question LIKE '%types of human-to-animal communication%prohibited%'
   OR question LIKE '%Which of the following%regulated or prohibited%'
ORDER BY "all" DESC
"""
df_q85 = pd.read_sql_query(query_q85, conn)
print(f"\nProhibited communication responses found: {len(df_q85)}")

if not df_q85.empty:
    print("\nGlobal consensus on prohibited communications:")
    for _, row in df_q85.head(10).iterrows():
        if row['global_consensus'] is not None:
            print(f"  {row['response'][:60]}... : {row['global_consensus']:.3f}")
    
    # Regional variations
    print("\nRegional variations (top response):")
    if len(df_q85) > 0:
        top_row = df_q85.iloc[0]
        regions = ['africa', 'asia', 'europe', 'north_america', 'south_america', 'oceania']
        for region in regions:
            if region in top_row and top_row[region] is not None:
                print(f"  {region}: {top_row[region]:.3f}")

# Question 12.2: Professional Restrictions and Company Regulation
print("\n12.2. Professional Restrictions and Company Regulation")
print("-" * 40)

query_q82 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%restricted to authorized professionals%'
   OR question LIKE '%Animal communication should be restricted%'
"""
df_q82 = pd.read_sql_query(query_q82, conn)
print(f"\nProfessional restriction responses found: {len(df_q82)}")
if not df_q82.empty:
    for _, row in df_q82.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

query_q84 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%Companies that profit from animals%strict rules%'
   OR question LIKE '%companies%regulate%communicate%animals%'
"""
df_q84 = pd.read_sql_query(query_q84, conn)
print(f"\nCompany regulation responses found: {len(df_q84)}")
if not df_q84.empty:
    for _, row in df_q84.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Question 12.3: Animal Representatives in Decision-Making
print("\n12.3. Animal Representatives in Decision-Making")
print("-" * 40)

query_q75 = """
SELECT response, 
       "all" as global_score,
       africa, asia, europe, north_america, south_america, oceania
FROM responses
WHERE question LIKE '%who%should be given the responsibility of representing%'
   OR question LIKE '%animals were represented%decision-making%'
ORDER BY "all" DESC
"""
df_q75 = pd.read_sql_query(query_q75, conn)
print(f"\nAnimal representative responses found: {len(df_q75)}")

if not df_q75.empty:
    print("\nGlobal preferences for animal representatives:")
    for _, row in df_q75.head(10).iterrows():
        if row['global_score'] is not None:
            print(f"  {row['response'][:50]}... : {row['global_score']:.3f}")
    
    # Check for "Animals themselves" option
    animals_themselves = df_q75[df_q75['response'].str.contains('Animals themselves|animal ambassador', case=False, na=False)]
    if not animals_themselves.empty:
        print("\n'Animals themselves/ambassador' support by region:")
        row = animals_themselves.iloc[0]
        for region in ['africa', 'asia', 'europe', 'north_america', 'south_america', 'oceania']:
            if region in row and row[region] is not None:
                print(f"  {region}: {row[region]:.3f}")

# Question 12.4: Economic Agency by Age
print("\n12.4. Economic Agency by Age")
print("-" * 40)

query_q91 = """
SELECT response,
       "all" as overall,
       o2_18_25 as age_18_25,
       o2_26_35 as age_26_35,
       o2_36_45 as age_36_45,
       o2_46_55 as age_46_55,
       o2_56_65 as age_56_65,
       o2_65 as age_65_plus
FROM responses
WHERE question LIKE '%earn money%own property%'
   OR question LIKE '%non-humans%able to earn%'
"""
df_q91 = pd.read_sql_query(query_q91, conn)
print(f"\nEconomic agency responses found: {len(df_q91)}")

if not df_q91.empty:
    print("\nEconomic agency support by response type:")
    for _, row in df_q91.iterrows():
        if row['overall'] is not None:
            print(f"\n{row['response'][:60]}...")
            print(f"  Overall: {row['overall']:.3f}")
            
            # Age comparison
            if row['age_18_25'] is not None and row['age_56_65'] is not None:
                print(f"  Age 18-25: {row['age_18_25']:.3f}")
                print(f"  Age 56-65: {row['age_56_65']:.3f}")
                print(f"  Age 65+: {row['age_65_plus']:.3f if row['age_65_plus'] is not None else 'N/A'}")
                
                # Calculate difference
                young_old_diff = row['age_18_25'] - row['age_56_65']
                print(f"  Difference (18-25 vs 56-65): {young_old_diff:+.3f}")

# Additional Analysis: Cross-tabulation
print("\n" + "=" * 80)
print("CROSS-ANALYSIS")
print("=" * 80)

# Check for correlation between professional restrictions and company regulation
print("\nAnalyzing relationship between professional restrictions and company regulation...")
print("Note: Due to aggregated data structure, direct correlation cannot be calculated")
print("but we can compare overall agreement levels:")

if not df_q82.empty and not df_q84.empty:
    prof_agree = df_q82[df_q82['response'].str.contains('Strongly agree|Agree', case=False, na=False)]
    comp_agree = df_q84[df_q84['response'].str.contains('Strongly agree|Agree', case=False, na=False)]
    
    if not prof_agree.empty:
        print(f"  Professional restriction support: {prof_agree['agreement_score'].mean():.3f}")
    if not comp_agree.empty:
        print(f"  Company regulation support: {comp_agree['agreement_score'].mean():.3f}")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

total_responses = sum([len(df_q85), len(df_q82), len(df_q84), len(df_q75), len(df_q91)])
print(f"Total responses analyzed: {total_responses}")
print(f"Questions with data: {sum([1 for df in [df_q85, df_q82, df_q84, df_q75, df_q91] if not df.empty])}/5")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete for Section 12")
print("=" * 80)