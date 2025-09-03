import sqlite3
import pandas as pd
import numpy as np

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=" * 80)
print("SECTION 23: ADDITIONAL CROSS-ANALYSIS QUESTIONS")
print("=" * 80)

# Question 23.1: Companion Animals and Economic Rights
print("\n23.1. Companion Animals and Economic Rights")
print("-" * 40)

# Find Q35 (caring for animals) and Q38 (types of animals encountered)
query_q35 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%Caring for animals%'
ORDER BY response
"""
df_q35 = pd.read_sql_query(query_q35, conn)
print(f"\nCaring for animals (Q35) responses found: {len(df_q35)}")
if not df_q35.empty:
    print("Caring frequency distribution:")
    for _, row in df_q35.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

query_q38_companion = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%types of animals%encounter%'
  AND response LIKE '%Companion Animals%'
"""
df_q38_companion = pd.read_sql_query(query_q38_companion, conn)
if not df_q38_companion.empty:
    print(f"\nCompanion animal encounter rate: {df_q38_companion.iloc[0]['agreement_score']:.3f}")

# Find Q91 (economic rights)
query_q91 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%earn money%own property%'
   OR question LIKE '%non-humans%able to earn%'
   OR question LIKE '%animals%economic%'
"""
df_q91 = pd.read_sql_query(query_q91, conn)
print(f"\nEconomic rights (Q91) responses found: {len(df_q91)}")
if not df_q91.empty:
    print("Economic rights support:")
    for _, row in df_q91.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response'][:60]}...: {row['agreement_score']:.3f}")
else:
    print("  No data available for Q91 (economic rights)")

# Question 23.2: Age and Political Voice
print("\n23.2. Age and Political Voice")
print("-" * 40)

# Find Q77 (political participation) with age breakdown
query_q77_age = """
SELECT response,
       "all" as overall,
       o2_18_25 as age_18_25,
       o2_26_35 as age_26_35,
       o2_36_45 as age_36_45,
       o2_46_55 as age_46_55,
       o2_56_65 as age_56_65,
       o2_65 as age_65_plus
FROM responses
WHERE question LIKE '%participate in human democratic processes%'
ORDER BY "all" DESC
"""
df_q77_age = pd.read_sql_query(query_q77_age, conn)
print(f"\nPolitical participation (Q77) responses with age data: {len(df_q77_age)}")

if not df_q77_age.empty:
    print("\nSupport for animal political participation by age:")
    
    # Calculate support (any "Yes" response) vs opposition ("No")
    yes_responses = df_q77_age[df_q77_age['response'].str.contains('Yes', case=False, na=False)]
    no_responses = df_q77_age[df_q77_age['response'].str.contains('No', case=False, na=False)]
    
    if not yes_responses.empty:
        # Sum all "Yes" variants by age group
        age_cols = ['age_18_25', 'age_26_35', 'age_36_45', 'age_46_55', 'age_56_65', 'age_65_plus']
        yes_by_age = {}
        for col in age_cols:
            if col in yes_responses.columns:
                yes_by_age[col] = yes_responses[col].sum()
        
        print("\nTotal 'Yes' support by age group:")
        for age, support in yes_by_age.items():
            if support is not None:
                print(f"  {age}: {support:.3f}")
        
        if 'age_18_25' in yes_by_age and 'age_56_65' in yes_by_age:
            diff = yes_by_age['age_18_25'] - yes_by_age['age_56_65']
            print(f"\nDifference (18-25 vs 56-65): {diff:+.3f}")
    
    # Show individual response breakdowns
    print("\nDetailed responses by age:")
    for _, row in df_q77_age.iterrows():
        if row['overall'] is not None:
            print(f"\n{row['response'][:60]}...")
            print(f"  Overall: {row['overall']:.3f}")
            if row['age_18_25'] is not None and row['age_56_65'] is not None:
                print(f"  18-25: {row['age_18_25']:.3f}, 56-65: {row['age_56_65']:.3f}")

# Question 23.3: Hearing vs. Political Participation
print("\n23.3. Hearing vs. Political Participation")
print("-" * 40)

# Find Q55 (interest in hearing animals)
query_q55 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%interested%know what animals%'
   OR question LIKE '%How interested%animals%say%feel%'
ORDER BY "all" DESC
"""
df_q55 = pd.read_sql_query(query_q55, conn)
print(f"\nInterest in hearing animals (Q55) responses: {len(df_q55)}")

if not df_q55.empty:
    print("\nInterest in hearing what animals say:")
    for _, row in df_q55.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")
    
    # Calculate total interest (Very + Somewhat interested)
    interested = df_q55[df_q55['response'].str.contains('interested', case=False, na=False)]
    if not interested.empty:
        total_interest = interested['agreement_score'].sum()
        print(f"\nTotal interested (Very + Somewhat): {total_interest:.3f}")

# Compare with Q77 political participation
if not df_q77_age.empty:
    print("\nPolitical participation support (Q77):")
    yes_total = yes_responses['overall'].sum() if not yes_responses.empty else 0
    no_total = no_responses['overall'].iloc[0] if not no_responses.empty else 0
    print(f"  Support participation (all Yes variants): {yes_total:.3f}")
    print(f"  Oppose participation (No): {no_total:.3f}")
    
    if not df_q55.empty and not interested.empty:
        total_interest = interested['agreement_score'].sum()
        interest_participation_gap = total_interest - yes_total
        print(f"\nGap (Interest in hearing - Political participation support): {interest_participation_gap:+.3f}")

# Summary Analysis
print("\n" + "=" * 80)
print("CROSS-ANALYSIS SUMMARY")
print("=" * 80)

# Companion animal exposure summary
if not df_q38_companion.empty:
    companion_rate = df_q38_companion.iloc[0]['agreement_score']
    print(f"\n1. Companion Animal Exposure:")
    print(f"   {companion_rate:.1%} of population encounters companion animals weekly")
    if df_q91.empty:
        print("   Cannot assess correlation with economic rights (Q91 data missing)")

# Age patterns summary
if not df_q77_age.empty and not yes_responses.empty:
    print(f"\n2. Age and Political Voice:")
    if 'age_18_25' in yes_by_age and 'age_56_65' in yes_by_age:
        young_support = yes_by_age['age_18_25']
        older_support = yes_by_age['age_56_65']
        print(f"   Young (18-25) support: {young_support:.1%}")
        print(f"   Older (56-65) support: {older_support:.1%}")
        if young_support > older_support:
            print(f"   Younger respondents show {(young_support-older_support):.1%} more support")
        else:
            print(f"   Older respondents show {(older_support-young_support):.1%} more support")

# Interest vs participation summary
if not df_q55.empty and not df_q77_age.empty:
    print(f"\n3. Interest vs. Participation:")
    if not interested.empty and not yes_responses.empty:
        interest_total = interested['agreement_score'].sum()
        participation_total = yes_responses['overall'].sum()
        print(f"   Interest in hearing animals: {interest_total:.1%}")
        print(f"   Support for political participation: {participation_total:.1%}")
        print(f"   Gap: {(interest_total - participation_total):.1%} more interested than supportive")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete for Section 23")
print("=" * 80)