#!/usr/bin/env python3
"""
Review Section 11: AI, Trust, and Technology Adoption
Verifying the analysis claims and calculations
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, spearmanr

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== REVIEWING SECTION 11 ANALYSIS ===\n")

# === Question 11.1: Daily AI Users and Translation Trust ===
print("=== Q11.1: AI USAGE vs TRANSLATION TRUST ===")

# Check Q20 (AI usage frequency) and Q57 (translation trust) distributions
q20_query = """
SELECT Q20, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q20 IS NOT NULL AND Q20 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q20 IS NOT NULL AND Q20 != '--'
GROUP BY Q20
ORDER BY count DESC
"""
q20_results = pd.read_sql_query(q20_query, conn)
print("Q20 AI Usage Distribution:")
print(q20_results)

q57_query = """
SELECT Q57, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q57 IS NOT NULL AND Q57 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q57
ORDER BY count DESC
"""
q57_results = pd.read_sql_query(q57_query, conn)
print("\nQ57 Translation Trust Distribution:")
print(q57_results)

# Cross-tabulation of Q20 and Q57
q20_q57_query = """
SELECT Q20, Q57, COUNT(*) as count
FROM participant_responses
WHERE Q20 IS NOT NULL AND Q20 != '--' AND Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q20, Q57
"""
q20_q57_df = pd.read_sql_query(q20_q57_query, conn)

if len(q20_q57_df) > 0:
    pivot = q20_q57_df.pivot(index='Q20', columns='Q57', values='count').fillna(0)
    print("\nQ20 x Q57 Cross-tabulation:")
    print(pivot)
    
    # Calculate trust percentages by usage frequency
    percentages = pivot.div(pivot.sum(axis=1), axis=0) * 100
    print("\nTrust percentages by usage frequency:")
    print(percentages.round(1))
    
    # Check for "trust" responses (assuming these contain "trust")
    trust_cols = [col for col in percentages.columns if 'trust' in col.lower() and 'distrust' not in col.lower()]
    if trust_cols:
        trust_by_usage = percentages[trust_cols].sum(axis=1)
        print("\nTotal trust percentages by usage:")
        for idx, val in trust_by_usage.items():
            print(f"  {idx}: {val:.1f}%")

# === Question 11.2: Representative distrust vs AI trust ===
print("\n\n=== Q11.2: REPRESENTATIVE DISTRUST vs AI TRUST ===")

# Check Q14 (representative trust) distribution
q14_query = """
SELECT Q14, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q14 IS NOT NULL AND Q14 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q14 IS NOT NULL AND Q14 != '--'
GROUP BY Q14
ORDER BY count DESC
"""
q14_results = pd.read_sql_query(q14_query, conn)
print("Q14 Representative Trust Distribution:")
print(q14_results)

# Cross-tabulation of Q14 and Q57
q14_q57_query = """
SELECT Q14, Q57, COUNT(*) as count
FROM participant_responses
WHERE Q14 IS NOT NULL AND Q14 != '--' AND Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q14, Q57
"""
q14_q57_df = pd.read_sql_query(q14_q57_query, conn)

if len(q14_q57_df) > 0:
    pivot_14 = q14_q57_df.pivot(index='Q14', columns='Q57', values='count').fillna(0)
    print("\nQ14 x Q57 Cross-tabulation:")
    print(pivot_14)
    
    # Calculate trust percentages by representative trust level
    percentages_14 = pivot_14.div(pivot_14.sum(axis=1), axis=0) * 100
    print("\nAI translation trust by representative trust:")
    print(percentages_14.round(1))

# === Question 11.3: Demographic Trust Gaps ===
print("\n\n=== Q11.3: DEMOGRAPHIC TRUST GAPS ===")

# Check Q5 (AI excitement) distribution
q5_query = """
SELECT Q5, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q5 IS NOT NULL AND Q5 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q5 IS NOT NULL AND Q5 != '--'
GROUP BY Q5
ORDER BY count DESC
"""
q5_results = pd.read_sql_query(q5_query, conn)
print("Q5 AI Excitement Distribution:")
print(q5_results)

# Get demographic data for gap analysis
demo_gap_query = """
SELECT Q1 as age, Q2_Gender as gender, Q5, Q57, COUNT(*) as count
FROM participant_responses
WHERE Q1 IS NOT NULL AND Q1 != '--' 
  AND Q2_Gender IS NOT NULL AND Q2_Gender != '--'
  AND Q5 IS NOT NULL AND Q5 != '--'
  AND Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q1, Q2_Gender, Q5, Q57
"""
demo_gap_df = pd.read_sql_query(demo_gap_query, conn)

if len(demo_gap_df) > 0:
    print("\nSample of demographic gap data:")
    print(demo_gap_df.head(10))

# === Question 11.4: Interested but Distrustful ===
print("\n\n=== Q11.4: INTERESTED BUT DISTRUSTFUL ===")

# Check Q55 (interest) distribution
q55_query = """
SELECT Q55, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q55 IS NOT NULL AND Q55 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q55 IS NOT NULL AND Q55 != '--'
GROUP BY Q55
ORDER BY count DESC
"""
q55_results = pd.read_sql_query(q55_query, conn)
print("Q55 Interest Distribution:")
print(q55_results)

# Find conflicted respondents (Very interested + Strongly distrust)
conflicted_query = """
SELECT Q55, Q57, Q59, COUNT(*) as count
FROM participant_responses
WHERE Q55 = 'Very interested'
  AND Q57 = 'Strongly distrust'
  AND Q59 IS NOT NULL AND Q59 != '--'
GROUP BY Q55, Q57, Q59
"""
conflicted_df = pd.read_sql_query(conflicted_query, conn)

if len(conflicted_df) > 0:
    print(f"\nConflicted respondents (Very interested + Strongly distrust): {conflicted_df['count'].sum()}")
    print("Sample concerns:")
    print(conflicted_df['Q59'].head(5).tolist())

# Also check broader "interested but distrust" pattern
broader_conflicted_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q55 = 'Very interested'
  AND (Q57 = 'Strongly distrust' OR Q57 = 'Somewhat distrust')
"""
broader_conflicted = pd.read_sql_query(broader_conflicted_query, conn)
print(f"\nBroader conflicted pattern (Very interested + any distrust): {broader_conflicted['count'].iloc[0]}")

# Total very interested
total_interested_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q55 = 'Very interested'
"""
total_interested = pd.read_sql_query(total_interested_query, conn)
print(f"Total Very interested: {total_interested['count'].iloc[0]}")

conn.close()

print("\n=== REVIEW SUMMARY ===")
print("Key numbers to verify against the analysis:")
print("- Daily AI users trust rate: claimed 65.2%")
print("- Non-users trust rate: claimed 38.4%")
print("- Difference: claimed 26.8 percentage points")
print("- Representative distrust -> AI trust correlation")
print("- Males 18-25 gap: claimed -28.5%")
print("- Conflicted respondents: claimed 123 (12.2% of interested)")