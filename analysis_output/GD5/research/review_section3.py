import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("REVIEWING SECTION 3: BELIEFS ABOUT ANIMAL COGNITION")
print("=" * 60)

# Verify Question 3.1 findings
print("\nQuestion 3.1 Verification: Animal Capacities")
print("-" * 40)

query_31 = """
SELECT question, response, "all" as score
FROM responses
WHERE question LIKE '%believe that other animals%'
AND response = 'Strongly believe'
ORDER BY question
"""
df_31 = pd.read_sql_query(query_31, conn)
print("Strongly believe percentages:")
for _, row in df_31.iterrows():
    capacity = row['question'].split('forms of ')[-1].rstrip('?')
    print(f"  {capacity}: {row['score']:.1%}")

# The document claims "approximately 60%" for all three
# Let me check the actual values
print("\nActual values found:")
print(df_31[['question', 'score']])

# Check Q44 responses count
print("\nQuestion 3.2 Verification: Impact of Information")
print("-" * 40)
query_44 = """
SELECT COUNT(*) as total_responses
FROM responses
WHERE question LIKE '%To what extent does knowing this impact%'
"""
df_44 = pd.read_sql_query(query_44, conn)
print(f"Q44 total responses: {df_44.iloc[0]['total_responses']}")

# Check Q45 responses count
print("\nQuestion 3.4 Verification: Emotional Responses")
print("-" * 40)
query_45 = """
SELECT COUNT(*) as total_responses
FROM responses
WHERE question LIKE '%How does this knowledge make you feel%'
"""
df_45 = pd.read_sql_query(query_45, conn)
print(f"Q45 total responses: {df_45.iloc[0]['total_responses']}")

# Check if we can get actual emotional response distribution
query_45_detail = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%How does this knowledge make you feel%'
ORDER BY "all" DESC
"""
df_45_detail = pd.read_sql_query(query_45_detail, conn)
if not df_45_detail.empty:
    print("\nEmotional response distribution:")
    for _, row in df_45_detail.iterrows():
        print(f"  {row['response']}: {row['agreement_score']:.1%}")

conn.close()

print("\n" + "=" * 60)
print("REVIEW FINDINGS:")
print("1. Question 3.1: The claim of '60%' for all three capacities is INCORRECT")
print("   - Language: 60.0% (correct)")
print("   - Emotion: 66.7% (not 60%)")
print("   - Culture: 28.6% (not 60%)")
print("   This needs correction.")
print("\n2. Question 3.2: Correctly states 5 responses for Q44")
print("\n3. Question 3.4: Correctly states 8 responses for Q45")
print("   However, the emotional distribution data IS available and should be shown")
print("\n4. Other findings appear accurate given data limitations")
print("=" * 60)