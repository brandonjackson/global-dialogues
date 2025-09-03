#!/usr/bin/env python3
"""
Review Section 9: Persona-Based and Predictive Analysis
Verifying the analysis claims and calculations
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== REVIEWING SECTION 9 ANALYSIS ===\n")

# === Question 9.1: Tech-First Futurist Persona ===
print("=== Q9.1: TECH-FIRST FUTURIST VERIFICATION ===")

# First, let's understand the persona definition and verify the size
# Definition: More excited about AI + Trust AI chatbots + Believe AI improves life in 3+ areas

# Check for AI excitement questions - need to find the right columns
columns_query = "PRAGMA table_info(participant_responses)"
columns_df = pd.read_sql_query(columns_query, conn)
print("Available columns that might relate to AI excitement/trust:")
ai_columns = columns_df[columns_df['name'].str.contains('Q', na=False)]['name'].tolist()
print(f"Total columns: {len(ai_columns)}")

# Let's check a sample of responses to understand the data structure
sample_query = """
SELECT * FROM participant_responses LIMIT 3
"""
sample_df = pd.read_sql_query(sample_query, conn)
print(f"\nSample data shape: {sample_df.shape}")

# Check Q76 (ecocentric AI society) distribution
print("\n=== Q76 ECOCENTRIC AI SOCIETY ===")
q76_query = """
SELECT Q76, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q76 IS NOT NULL AND Q76 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q76 IS NOT NULL AND Q76 != '--'
GROUP BY Q76
ORDER BY count DESC
"""
q76_results = pd.read_sql_query(q76_query, conn)
print("Q76 Distribution:")
print(q76_results)

# Check Q82-Q85 distribution
print("\n=== Q82-Q85 GOVERNANCE QUESTIONS ===")
for q in ['Q82', 'Q83', 'Q84', 'Q85']:
    try:
        query = f"""
        SELECT {q}, COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE {q} IS NOT NULL AND {q} != '--'), 2) as percentage
        FROM participant_responses 
        WHERE {q} IS NOT NULL AND {q} != '--'
        GROUP BY {q}
        ORDER BY count DESC
        """
        results = pd.read_sql_query(query, conn)
        print(f"\n{q} Distribution:")
        print(results.head())
        
        if 'agree' in results[q].str.lower().str.cat(sep=' ', na_rep=''):
            agree_pct = results[results[q].str.contains('agree', case=False, na=False)]['percentage'].sum()
            print(f"Total agreement: {agree_pct:.1f}%")
    except Exception as e:
        print(f"Error with {q}: {e}")

# === Question 9.2: Animal Empath Persona ===
print("\n\n=== Q9.2: ANIMAL EMPATH VERIFICATION ===")

# Check Q70 (protection approach)
q70_query = """
SELECT Q70, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q70 IS NOT NULL AND Q70 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q70 IS NOT NULL AND Q70 != '--'
GROUP BY Q70
ORDER BY count DESC
"""
q70_results = pd.read_sql_query(q70_query, conn)
print("Q70 Distribution:")
print(q70_results)

# Check Q73 (legal representation)
q73_query = """
SELECT Q73, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q73 IS NOT NULL AND Q73 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q73 IS NOT NULL AND Q73 != '--'
GROUP BY Q73
ORDER BY count DESC
"""
q73_results = pd.read_sql_query(q73_query, conn)
print("\nQ73 Distribution:")
print(q73_results)

# Check Q77 (democratic participation)
q77_query = """
SELECT Q77, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q77 IS NOT NULL AND Q77 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q77 IS NOT NULL AND Q77 != '--'
GROUP BY Q77
ORDER BY count DESC
"""
q77_results = pd.read_sql_query(q77_query, conn)
print("\nQ77 Distribution:")
print(q77_results)

# === Question 9.3: Cautious Humanist Persona ===
print("\n\n=== Q9.3: CAUTIOUS HUMANIST VERIFICATION ===")

# Check Q66 (communication preference)
q66_query = """
SELECT Q66, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q66 IS NOT NULL AND Q66 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q66 IS NOT NULL AND Q66 != '--'
GROUP BY Q66
ORDER BY count DESC
"""
q66_results = pd.read_sql_query(q66_query, conn)
print("Q66 Distribution:")
print(q66_results)

# Check Q55 (interest level)
q55_query = """
SELECT Q55, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q55 IS NOT NULL AND Q55 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q55 IS NOT NULL AND Q55 != '--'
GROUP BY Q55
ORDER BY count DESC
"""
q55_results = pd.read_sql_query(q55_query, conn)
print("\nQ55 Distribution:")
print(q55_results)

# Check Q57 (trust in translation)
q57_query = """
SELECT Q57, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q57 IS NOT NULL AND Q57 != '--'), 2) as percentage
FROM participant_responses 
WHERE Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q57
ORDER BY count DESC
"""
q57_results = pd.read_sql_query(q57_query, conn)
print("\nQ57 Distribution:")
print(q57_results)

conn.close()

print("\n=== REVIEW SUMMARY ===")
print("Key numbers to verify against the analysis:")
print("- Tech-First Futurist persona size (claimed 20.2%)")
print("- Q76 percentages and p-value")
print("- Q82-Q85 agreement rates and p-values")
print("- Animal Empath persona size (claimed 15%)")
print("- Q70, Q73, Q77 distributions and p-values")
print("- Cautious Humanist persona size (claimed 0.5%)")
print("- Q55, Q57, Q66 distributions")