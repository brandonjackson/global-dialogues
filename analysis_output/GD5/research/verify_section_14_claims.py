#!/usr/bin/env python3
"""
Verify key claims in Section 14: Headline-Friendly Insights
"""
import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== VERIFYING SECTION 14 CLAIMS ===\n")

# === Claim 1: 59.5% support animal democratic participation ===
print("=== CLAIM 1: ANIMAL DEMOCRATIC PARTICIPATION ===")

q77_query = """
SELECT Q77, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q77 IS NOT NULL AND Q77 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q77 IS NOT NULL AND Q77 != '--'
GROUP BY Q77
ORDER BY count DESC
"""
q77_results = pd.read_sql_query(q77_query, conn)
print("Q77 Democratic participation distribution:")
for _, row in q77_results.iterrows():
    print(f"  {row['Q77']}: {row['count']} ({row['percentage']}%)")

# Calculate support (all "Yes" options)
no_participation = q77_results[q77_results['Q77'].str.contains('No', na=False)]['percentage'].sum()
support_participation = 100 - no_participation
print(f"\nClaimed: 59.5% support some form of participation")  
print(f"No participation: {no_participation:.1f}%")
print(f"Support participation: {support_participation:.1f}%")

# === Claim 2: AI vs Politicians trust comparison ===
print("\n\n=== CLAIM 2: AI vs POLITICIANS TRUST ===")

# Q14 (representative trust) distribution
q14_query = """
SELECT Q14, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q14 IS NOT NULL AND Q14 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q14 IS NOT NULL AND Q14 != '--'
GROUP BY Q14
ORDER BY count DESC
"""
q14_results = pd.read_sql_query(q14_query, conn)
print("Q14 Representative trust distribution:")
for _, row in q14_results.iterrows():
    print(f"  {row['Q14']}: {row['count']} ({row['percentage']}%)")

# Q57 (AI translation trust) distribution
q57_query = """
SELECT Q57, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q57 IS NOT NULL AND Q57 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q57
ORDER BY count DESC
"""
q57_results = pd.read_sql_query(q57_query, conn)
print("\nQ57 AI translation trust distribution:")
for _, row in q57_results.iterrows():
    print(f"  {row['Q57']}: {row['count']} ({row['percentage']}%)")

# Calculate average trust scores (convert to 1-5 scale)
def trust_to_numeric(val):
    if pd.isna(val):
        return np.nan
    val_lower = str(val).lower()
    if 'strongly trust' in val_lower:
        return 5
    elif 'somewhat trust' in val_lower:
        return 4
    elif 'neutral' in val_lower or 'neither' in val_lower:
        return 3
    elif 'somewhat distrust' in val_lower:
        return 2
    elif 'strongly distrust' in val_lower:
        return 1
    return np.nan

# Get combined data for comparison
combined_query = """
SELECT Q14, Q57
FROM participant_responses
WHERE Q14 IS NOT NULL AND Q14 != '--' AND Q57 IS NOT NULL AND Q57 != '--'
"""
combined_df = pd.read_sql_query(combined_query, conn)

combined_df['q14_numeric'] = combined_df['Q14'].apply(trust_to_numeric)
combined_df['q57_numeric'] = combined_df['Q57'].apply(trust_to_numeric)

avg_rep_trust = combined_df['q14_numeric'].mean()
avg_ai_trust = combined_df['q57_numeric'].mean()

print(f"\nAverage trust scores:")
print(f"Representatives (Q14): {avg_rep_trust:.2f}")
print(f"AI translation (Q57): {avg_ai_trust:.2f}")
print(f"Difference: {avg_ai_trust - avg_rep_trust:.2f}")
print(f"Claimed: AI 3.21, Politicians 2.64, Difference 0.57")

# === Claim 3: Pet economic rights by age ===
print("\n\n=== CLAIM 3: PET ECONOMIC RIGHTS BY AGE ===")

# Check available age groups
age_query = """
SELECT Q2 as age, COUNT(*) as count
FROM participant_responses
WHERE Q2 IS NOT NULL AND Q2 != '--'
GROUP BY Q2
ORDER BY count DESC
"""
age_results = pd.read_sql_query(age_query, conn)
print("Age distribution:")
print(age_results)

# Check Q91 for economic rights by age
age_econ_query = """
SELECT Q2 as age, Q91, COUNT(*) as count
FROM participant_responses
WHERE Q2 IS NOT NULL AND Q2 != '--' AND Q91 IS NOT NULL AND Q91 != '--'
GROUP BY Q2, Q91
"""
age_econ_df = pd.read_sql_query(age_econ_query, conn)

# Calculate support percentages by age group
if len(age_econ_df) > 0:
    print("\nSample Q91 responses by age:")
    print(age_econ_df.head(10))

# === Claim 4: East vs West legal personhood ===
print("\n\n=== CLAIM 4: EAST vs WEST LEGAL PERSONHOOD ===")

# Q70 for legal rights preference
q70_query = """
SELECT Q70, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q70 IS NOT NULL AND Q70 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q70 IS NOT NULL AND Q70 != '--'
GROUP BY Q70
ORDER BY count DESC
"""
q70_results = pd.read_sql_query(q70_query, conn)
print("Q70 Animal protection approach:")
for _, row in q70_results.iterrows():
    if 'legal rights' in row['Q70'].lower():
        print(f"  Future C (Legal Rights): {row['count']} ({row['percentage']}%)")
        break

# === Claim 5: Hopeful but cautious bloc ===
print("\n\n=== CLAIM 5: HOPEFUL BUT CAUTIOUS BLOC ===")

# Q54 emotional responses
q54_query = """
SELECT Q54, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q54 IS NOT NULL AND Q54 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q54 IS NOT NULL AND Q54 != '--'
GROUP BY Q54
ORDER BY count DESC
LIMIT 10
"""
q54_results = pd.read_sql_query(q54_query, conn)
print("Top Q54 emotional responses:")
for _, row in q54_results.iterrows():
    print(f"  {row['Q54']}: {row['count']} ({row['percentage']}%)")

# Count hopeful responses
hopeful_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q54 IS NOT NULL AND Q54 != '--' AND Q54 LIKE '%Hopeful%'
"""
hopeful_count = pd.read_sql_query(hopeful_query, conn)['count'].iloc[0]

total_q54_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q54 IS NOT NULL AND Q54 != '--'
"""
total_q54 = pd.read_sql_query(total_q54_query, conn)['count'].iloc[0]

hopeful_pct = (hopeful_count / total_q54 * 100) if total_q54 > 0 else 0

print(f"\nHopeful responses: {hopeful_count}/{total_q54} ({hopeful_pct:.1f}%)")
print(f"Claimed: 47.3% express hopefulness")

conn.close()

print("\n=== SUMMARY ===")
print("Verify these key claims:")
print("1. Democratic participation support: claimed 59.5%")
print("2. AI vs politician trust scores: claimed AI 3.21 vs Politicians 2.64")  
print("3. Economic rights by age: claimed 26-35 highest at 45.9%")
print("4. East vs West personhood: claimed no significant difference")
print("5. Hopeful responses: claimed 47.3%")