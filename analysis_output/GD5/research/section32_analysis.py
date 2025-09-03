import sqlite3
import pandas as pd
import numpy as np
from collections import Counter
import re

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=" * 80)
print("SECTION 32: ADDITIONAL GAP-FILLING QUESTIONS")
print("=" * 80)

# Section 32.1: Economic Anxiety and Animal Rights
print("\n32.1. Economic Anxiety and Animal Rights")
print("-" * 40)

# Find Q23 (cost of living) and Q26 (jobs)
query_economic = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE (question LIKE '%cost of living%' AND question LIKE '%AI%')
   OR (question LIKE '%job%' AND question LIKE '%AI%')
"""
df_economic = pd.read_sql_query(query_economic, conn)
print(f"\nEconomic outlook responses found: {len(df_economic)}")

# Find Q70 (animal protection approaches)
query_q70 = """
SELECT response, 
       "all" as agreement_score,
       branch_a, branch_b, branch_c
FROM responses
WHERE question LIKE '%approach%appropriate%protecting animals%'
"""
df_q70 = pd.read_sql_query(query_q70, conn)
print(f"Animal protection approach responses found: {len(df_q70)}")

# Find Q73 (legal representation) and Q91 (economic agency)
query_rights = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%legal representative%'
   OR question LIKE '%earn money%own property%'
"""
df_rights = pd.read_sql_query(query_rights, conn)
print(f"Rights/agency responses found: {len(df_rights)}")

# Section 32.2: Community Optimism and Relational Approaches
print("\n32.2. Community Optimism and Relational Approaches")
print("-" * 40)

query_q25 = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%community%well-being%'
   AND question LIKE '%AI%'
"""
df_q25 = pd.read_sql_query(query_q25, conn)
print(f"\nCommunity well-being responses found: {len(df_q25)}")

if not df_q25.empty:
    print("Community well-being outlook:")
    for _, row in df_q25.iterrows():
        if row['agreement_score'] is not None:
            print(f"  {row['response']}: {row['agreement_score']:.3f}")

# Check branch_a (building relationships) support
if not df_q70.empty and 'branch_a' in df_q70.columns:
    branch_a_support = df_q70['branch_a'].mean()
    if branch_a_support is not None:
        print(f"\nBranch A (Building Relationships) average support: {branch_a_support:.3f}")

# Section 32.3-32.5: Open Text Analysis
print("\n32.3-32.5. Open Text Themes Analysis")
print("-" * 40)

# Q33 - justifications for human-nature views
query_q33 = """
SELECT response, originalresponse, categories
FROM responses
WHERE question LIKE '%Why do you believe%'
   OR question LIKE '%Please explain why%'
LIMIT 100
"""
df_q33 = pd.read_sql_query(query_q33, conn)
print(f"\nQ33 open text responses found: {len(df_q33)}")

# Analyze themes in Q33
if not df_q33.empty:
    theme_patterns = {
        'Religious': r'god|divine|creator|faith|soul|spirit|bible|religious',
        'Scientific': r'evolution|biology|science|research|intelligence|brain|cognitive',
        'Philosophical': r'consciousness|sentience|moral|ethics|rights|responsibility',
        'Personal': r'experience|observe|seen|feel|believe|think',
        'Practical': r'use|tool|benefit|superior|control|dominate'
    }
    
    theme_counts = Counter()
    for _, row in df_q33.iterrows():
        text = str(row['response'] or '') + ' ' + str(row['originalresponse'] or '')
        text_lower = text.lower()
        
        for theme, pattern in theme_patterns.items():
            if re.search(pattern, text_lower):
                theme_counts[theme] += 1
    
    if theme_counts:
        print("\nTheme distribution in Q33 responses:")
        for theme, count in theme_counts.most_common():
            print(f"  {theme}: {count} ({count*100/len(df_q33):.1f}%)")

# Q59 - concerns about AI communication
query_q59 = """
SELECT response, categories
FROM responses
WHERE question LIKE '%concerns%AI%interspecies communication%'
   OR question LIKE '%What concerns%use of AI%'
LIMIT 100
"""
df_q59 = pd.read_sql_query(query_q59, conn)
print(f"\nQ59 concern responses found: {len(df_q59)}")

# Section 32.6-32.8: Neutrality and Ambivalence
print("\n32.6-32.8. Neutrality and Ambivalence")
print("-" * 40)

# Find neutral responses across key questions
neutral_queries = {
    'Q17_AI_trust': "question LIKE '%trust%AI chatbot%' AND response LIKE '%Neither%'",
    'Q39_language': "question LIKE '%believe%animals%language%' AND response = 'Neutral'",
    'Q40_emotion': "question LIKE '%believe%animals%emotion%' AND response = 'Neutral'",
    'Q41_culture': "question LIKE '%believe%animals%culture%' AND response = 'Neutral'",
    'Q53_AI_good': "question LIKE '%good use of%technology%' AND response LIKE '%depends%'",
    'Q73_representation': "question LIKE '%legal representative%' AND response LIKE '%Not sure%'"
}

neutral_rates = {}
for label, condition in neutral_queries.items():
    query = f"""
    SELECT COUNT(*) as count, "all" as agreement_score
    FROM responses
    WHERE {condition}
    """
    df_neutral = pd.read_sql_query(query, conn)
    if not df_neutral.empty and df_neutral.iloc[0]['count'] > 0:
        neutral_rates[label] = df_neutral.iloc[0]['agreement_score']

print("\nNeutral/ambivalent response rates:")
for label, rate in neutral_rates.items():
    if rate is not None:
        print(f"  {label}: {rate:.3f}")

# Q53 "It depends" and regulation preferences
query_q53_depends = """
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%good use%technology%'
   AND response LIKE '%depends%'
"""
df_q53_depends = pd.read_sql_query(query_q53_depends, conn)

if not df_q53_depends.empty:
    depends_rate = df_q53_depends.iloc[0]['agreement_score']
    print(f"\n'It depends' rate for AI technology use (Q53): {depends_rate:.3f}")

# Check regulation preferences (Q82, Q84)
query_regulation = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE (question LIKE '%restricted to authorized professionals%' 
       OR question LIKE '%Companies%profit%strict rules%')
   AND response LIKE '%agree%'
"""
df_regulation = pd.read_sql_query(query_regulation, conn)
print(f"\nRegulation support responses found: {len(df_regulation)}")

# Q93-Q94 changes (survey intervention)
print("\n32.7. Survey Intervention Effects")
print("-" * 40)

# Check for questions at beginning and end about human-nature views
query_intervention = """
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%part of nature%'
   OR question LIKE '%superior%inferior%equal%'
ORDER BY question
"""
df_intervention = pd.read_sql_query(query_intervention, conn)
print(f"Human-nature view responses found: {len(df_intervention)}")

# Summary Statistics
print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)

print("\n1. Economic Anxiety Analysis:")
if not df_economic.empty:
    print(f"   Economic outlook questions found: {len(df_economic)}")
else:
    print("   Limited economic anxiety data available")

print("\n2. Community Optimism:")
if not df_q25.empty:
    optimistic = df_q25[df_q25['response'].str.contains('Better', case=False, na=False)]
    if not optimistic.empty:
        opt_rate = optimistic['agreement_score'].sum()
        print(f"   Community optimism rate: {opt_rate:.1%}")

print("\n3. Open Text Themes:")
if theme_counts:
    top_theme = theme_counts.most_common(1)[0]
    print(f"   Dominant justification theme: {top_theme[0]} ({top_theme[1]*100/len(df_q33):.1f}%)")

print("\n4. Neutrality Patterns:")
if neutral_rates:
    avg_neutral = np.mean([r for r in neutral_rates.values() if r is not None])
    print(f"   Average neutral rate across questions: {avg_neutral:.3f}")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete for Section 32")
print("=" * 80)