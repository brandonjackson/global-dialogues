import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Question 9.3: Accepting the Role, Rejecting the Method
# Is there a significant group of people who find it acceptable for an AI to act as a therapist 
# but also believe it's "Completely Unacceptable" for an AI to lie to a human to prevent psychological harm? 
# This probes the perceived ethical boundaries of AI in caring roles.

print("\n" + "="*80)
print("9.3 Accepting the Role, Rejecting the Method")
print("="*80)

# Get data from responses table for therapist acceptability
query_therapist = """
SELECT 
    response,
    CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%therapist%' 
  AND question_id IN (
    SELECT DISTINCT question_id 
    FROM responses 
    WHERE question LIKE '%therapist%'
  )
"""
therapist_df = pd.read_sql_query(query_therapist, conn)

print("\n1. AI as Therapist - Acceptability:")
for _, row in therapist_df.iterrows():
    print(f"   {row['response']}: {row['pct']:.1f}%")

# Calculate acceptance rate
acceptable_therapist = therapist_df[therapist_df['response'].isin(['Completely acceptable', 'Somewhat acceptable'])]['pct'].sum()
unacceptable_therapist = therapist_df[therapist_df['response'].isin(['Completely unacceptable', 'Somewhat unacceptable'])]['pct'].sum()
print(f"\n   Total Acceptable: {acceptable_therapist:.1f}%")
print(f"   Total Unacceptable: {unacceptable_therapist:.1f}%")

# Get data for AI lying to prevent psychological harm
query_lying = """
SELECT 
    response,
    CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%lie to a human%psychological harm%'
"""
lying_df = pd.read_sql_query(query_lying, conn)

print("\n2. AI Lying to Prevent Psychological Harm - Acceptability:")
for _, row in lying_df.iterrows():
    print(f"   {row['response']}: {row['pct']:.1f}%")

# Calculate acceptance rates
acceptable_lying = lying_df[lying_df['response'].isin(['Completely acceptable', 'Somewhat acceptable'])]['pct'].sum()
unacceptable_lying = lying_df[lying_df['response'].isin(['Completely Unacceptable', 'Somewhat unacceptable'])]['pct'].sum()
completely_unacceptable_lying = lying_df[lying_df['response'] == 'Completely Unacceptable']['pct'].values[0] if len(lying_df[lying_df['response'] == 'Completely Unacceptable']) > 0 else 0

print(f"\n   Total Acceptable: {acceptable_lying:.1f}%")
print(f"   Total Unacceptable: {unacceptable_lying:.1f}%")
print(f"   Completely Unacceptable: {completely_unacceptable_lying:.1f}%")

# Estimate the paradox group size (aggregate level)
# Those who find therapist acceptable BUT lying completely unacceptable
print("\n3. The Paradox Analysis (Aggregate Level):")
print(f"   Accept AI as therapist: {acceptable_therapist:.1f}%")
print(f"   Find lying completely unacceptable: {completely_unacceptable_lying:.1f}%")

# Minimum paradox estimate (assuming independence)
min_paradox = (acceptable_therapist / 100) * (completely_unacceptable_lying / 100) * 100
print(f"\n   Estimated minimum paradox group (assuming independence): {min_paradox:.1f}%")
print(f"   This represents those who accept AI therapists but completely reject lying")

# Get other caring roles for comparison
print("\n4. Comparison with Other Caring Roles:")

# Primary companion
query_companion = """
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%primary companion%lonely%'
"""
companion_df = pd.read_sql_query(query_companion, conn)
if not companion_df.empty:
    acceptable_companion = companion_df[companion_df['response'].isin(['Completely acceptable', 'Somewhat acceptable'])]['pct'].sum()
    print(f"   Primary companion for lonely: {acceptable_companion:.1f}% acceptable")

# Caregiver for elderly
query_caregiver = """
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%caregiver%elderly%'
"""
caregiver_df = pd.read_sql_query(query_caregiver, conn)
if not caregiver_df.empty:
    acceptable_caregiver = caregiver_df[caregiver_df['response'].isin(['Completely acceptable', 'Somewhat acceptable'])]['pct'].sum()
    print(f"   Caregiver for elderly: {acceptable_caregiver:.1f}% acceptable")

# Tutor/teacher
query_tutor = """
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%tutor%teacher%'
"""
tutor_df = pd.read_sql_query(query_tutor, conn)
if not tutor_df.empty:
    acceptable_tutor = tutor_df[tutor_df['response'].isin(['Completely acceptable', 'Somewhat acceptable'])]['pct'].sum()
    print(f"   Tutor/teacher: {acceptable_tutor:.1f}% acceptable")

# Look at other ethical boundaries
print("\n5. Other Ethical Boundaries:")

# AI changing from practical to emotional
query_change = """
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%initially designed%practical%emotional%'
"""
change_df = pd.read_sql_query(query_change, conn)
if not change_df.empty:
    print("\n   AI changing from practical to emotional role:")
    unacceptable_change = change_df[change_df['response'].isin(['Completely unacceptable', 'Somewhat unacceptable'])]['pct'].sum()
    print(f"   Unacceptable: {unacceptable_change:.1f}%")

# Summary of ethical boundaries
print("\n6. Summary of Ethical Boundaries in Caring Roles:")
print(f"   - AI as therapist is {acceptable_therapist:.1f}% acceptable")
print(f"   - AI lying to prevent harm is {acceptable_lying:.1f}% acceptable")
print(f"   - Gap: {acceptable_therapist - acceptable_lying:.1f} percentage points")
print(f"\n   This suggests people accept AI in caring roles but maintain strict")
print(f"   ethical boundaries about deception, even when well-intentioned.")

# Calculate correlation between acceptability rankings
print("\n7. Acceptability Rankings:")
roles_acceptability = [
    ("Therapist", acceptable_therapist),
    ("Primary companion", acceptable_companion) if 'acceptable_companion' in locals() else ("Primary companion", 0),
    ("Caregiver", acceptable_caregiver) if 'acceptable_caregiver' in locals() else ("Caregiver", 0),
    ("Tutor/teacher", acceptable_tutor) if 'acceptable_tutor' in locals() else ("Tutor/teacher", 0),
    ("Lying to prevent harm", acceptable_lying)
]

# Sort by acceptability
roles_acceptability = [(r, a) for r, a in roles_acceptability if a > 0]
roles_acceptability.sort(key=lambda x: x[1], reverse=True)

print("\n   Ranked by acceptability:")
for i, (role, accept) in enumerate(roles_acceptability, 1):
    print(f"   {i}. {role}: {accept:.1f}%")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: An estimated {min_paradox:.1f}% experience the paradox -")
print(f"accepting AI as therapist ({acceptable_therapist:.1f}%) while completely")
print(f"rejecting lying even to prevent harm ({completely_unacceptable_lying:.1f}%).")
print("This reveals strict ethical boundaries persist even in caring contexts.")
print("="*80)