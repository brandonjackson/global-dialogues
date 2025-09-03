import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("REVIEWING SECTION 17: SURPRISING CROSS-TRUST DYNAMICS")
print("=" * 60)

# Question 17.1: Global Trust Rankings
print("\nQuestion 17.1 Verification: Global Trust Rankings")
print("-" * 40)

# Check if we can get trust scores - but the data structure is aggregated
# Let me check what trust questions exist
query_trust = """
SELECT DISTINCT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%trust%'
   AND (question LIKE '%doctor%' 
        OR question LIKE '%AI chatbot%'
        OR question LIKE '%faith%leader%'
        OR question LIKE '%social media%')
ORDER BY question, response
"""
df_trust = pd.read_sql_query(query_trust, conn)
print(f"Trust-related responses found: {len(df_trust)}")

# Check AI translator trust
query_ai_translator = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%trust%AI%truly%comprehensively%'
   OR question LIKE '%trust%AI%translate%'
ORDER BY response
"""
df_ai_translator = pd.read_sql_query(query_ai_translator, conn)
print(f"\nAI translator trust responses: {len(df_ai_translator)}")
if not df_ai_translator.empty:
    print("AI translator trust distribution:")
    for _, row in df_ai_translator.iterrows():
        print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Question 17.2: AI vs Doctors Trust
print("\nQuestion 17.2 Verification: AI vs Doctors Trust")
print("-" * 40)

# Check age patterns - but with aggregated data we can't get individual comparisons
query_age_trust = """
SELECT response,
       o2_18_25 as age_18_25,
       o2_65 as age_65_plus
FROM responses
WHERE question LIKE '%trust%AI%translate%'
   AND response LIKE '%trust%'
"""
df_age_trust = pd.read_sql_query(query_age_trust, conn)
if not df_age_trust.empty:
    print("Age patterns in AI translator trust:")
    for _, row in df_age_trust.head(2).iterrows():
        print(f"  {row['response']}: 18-25={row['age_18_25']:.3f if row['age_18_25'] else 'N/A'}, "
              f"65+={row['age_65_plus']:.3f if row['age_65_plus'] else 'N/A'}")

# Question 17.3: Social Media and AI Distrust
print("\nQuestion 17.3 Verification: Social Media and AI Distrust")
print("-" * 40)

# Check social media trust
query_social = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%trust%social media%'
ORDER BY response
"""
df_social = pd.read_sql_query(query_social, conn)
print(f"Social media trust responses: {len(df_social)}")
if not df_social.empty:
    print("Social media trust distribution:")
    for _, row in df_social.iterrows():
        print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Note about participant count
query_participants = """
SELECT COUNT(*) as total
FROM participants
WHERE pri_score >= 0.3
"""
df_participants = pd.read_sql_query(query_participants, conn)
print(f"\nReliable participants (PRI >= 0.3): {df_participants.iloc[0]['total']}")

conn.close()

print("\n" + "=" * 60)
print("REVIEW FINDINGS:")
print("1. The document claims specific trust scores (e.g., doctors 4.24/5) but")
print("   the data is aggregated agreement scores, not individual 5-point scales")
print("2. The claim of 1005 participants is correct (actual: 1005)")
print("3. Cannot verify individual-level comparisons (6.6% trust AI more than doctors)")
print("   because data is aggregated at segment level")
print("4. Cannot verify correlations (r=0.347) due to aggregated structure")
print("5. The analysis appears to use different data than what's in the database")
print("\nCONCLUSION: Section 17 appears to analyze individual-level data that")
print("is not available in the aggregated database structure we have access to.")
print("=" * 60)