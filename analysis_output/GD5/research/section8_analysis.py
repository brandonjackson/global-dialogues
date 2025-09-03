import sqlite3
import pandas as pd
import re
from collections import Counter

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=" * 80)
print("SECTION 8: QUALITATIVE DEEP DIVES")
print("=" * 80)

# 8.1: Q33 - Justifications for human place in nature
print("\n8.1. Justifications for Human Place in Nature (Q33)")
print("-" * 40)

# First find questions about human-nature relationship
query_q32_33 = """
SELECT DISTINCT question_id, question
FROM responses
WHERE question LIKE '%superior%inferior%equal%'
   OR question LIKE '%Why do you believe%'
   OR question LIKE '%relationship between humans and nature%'
ORDER BY question
"""
df_q32_33 = pd.read_sql_query(query_q32_33, conn)
print("\nQuestions about human-nature relationship:")
for _, row in df_q32_33.iterrows():
    print(f"  {row['question_id'][:8]}... : {row['question'][:100]}...")

# Get open-text responses
query_opentext = """
SELECT question, response, originalresponse, categories, sentiment
FROM responses
WHERE question_type = 'Open Text'
   OR question_type LIKE '%open%'
   OR originalresponse IS NOT NULL
LIMIT 20
"""
df_opentext = pd.read_sql_query(query_opentext, conn)
print(f"\nOpen-text responses found: {len(df_opentext)}")
if not df_opentext.empty:
    print("Sample open-text responses:")
    for i, row in df_opentext.head(5).iterrows():
        print(f"  Q: {row['question'][:60]}...")
        print(f"  R: {row['response'][:100] if row['response'] else 'None'}...")

# 8.2: Q58 - Trust and distrust themes
print("\n8.2. Anatomy of Trust and Distrust (Q58)")
print("-" * 40)

query_q58 = """
SELECT question_id, question, response, categories
FROM responses
WHERE question LIKE '%trust%AI%interpret%'
   OR question LIKE '%Why%trust%'
LIMIT 10
"""
df_q58 = pd.read_sql_query(query_q58, conn)
print(f"Trust/distrust responses found: {len(df_q58)}")
if not df_q58.empty:
    # Analyze categories if available
    categories = []
    for cat in df_q58['categories'].dropna():
        if cat:
            categories.extend(cat.split(','))
    if categories:
        cat_counts = Counter(categories)
        print("Top categories mentioned:")
        for cat, count in cat_counts.most_common(5):
            print(f"  {cat.strip()}: {count}")

# 8.3: Q70 - Values in future visions
print("\n8.3. Values Underpinning Future Visions (Q70)")
print("-" * 40)

query_q70 = """
SELECT question, response, branch_a, branch_b, branch_c
FROM responses
WHERE question LIKE '%approach%appropriate%protecting animals%'
   OR question LIKE '%future%animal%'
LIMIT 10
"""
df_q70 = pd.read_sql_query(query_q70, conn)
print(f"Future vision responses found: {len(df_q70)}")
if not df_q70.empty:
    # Check branch preferences
    print("Branch scores (if available):")
    for col in ['branch_a', 'branch_b', 'branch_c']:
        if col in df_q70.columns:
            avg_score = df_q70[col].mean()
            if pd.notna(avg_score):
                print(f"  {col}: {avg_score:.3f}")

# 8.4: Q63/Q64 - Hopes and Fears
print("\n8.4. The Biggest Hopes and Fears (Q63/Q64)")
print("-" * 40)

query_q63_64 = """
SELECT question, response, categories, sentiment
FROM responses
WHERE question LIKE '%biggest benefit%'
   OR question LIKE '%biggest risk%'
   OR question LIKE '%understand animals%benefit%'
   OR question LIKE '%understand animals%risk%'
"""
df_q63_64 = pd.read_sql_query(query_q63_64, conn)
print(f"Hope/fear responses found: {len(df_q63_64)}")

if not df_q63_64.empty:
    # Separate benefits and risks
    benefits = df_q63_64[df_q63_64['question'].str.contains('benefit', case=False, na=False)]
    risks = df_q63_64[df_q63_64['question'].str.contains('risk', case=False, na=False)]
    
    print(f"\nBenefit responses: {len(benefits)}")
    print(f"Risk responses: {len(risks)}")
    
    # Analyze sentiments if available
    if 'sentiment' in df_q63_64.columns and df_q63_64['sentiment'].notna().any():
        sentiment_counts = df_q63_64['sentiment'].value_counts()
        print("\nSentiment distribution:")
        for sentiment, count in sentiment_counts.items():
            print(f"  {sentiment}: {count}")

# Check for thematic patterns in responses
print("\n" + "=" * 80)
print("THEMATIC ANALYSIS")
print("=" * 80)

# Look for common themes across all text responses
all_text_responses = """
SELECT response, originalresponse, categories
FROM responses
WHERE (response IS NOT NULL AND LENGTH(response) > 50)
   OR originalresponse IS NOT NULL
LIMIT 100
"""
df_text = pd.read_sql_query(all_text_responses, conn)

if not df_text.empty:
    print(f"\nAnalyzing {len(df_text)} text responses for themes...")
    
    # Common theme keywords
    themes = {
        'Religious/Spiritual': ['god', 'divine', 'soul', 'spirit', 'sacred', 'religious'],
        'Scientific': ['evolution', 'biology', 'science', 'research', 'data', 'evidence'],
        'Philosophical': ['consciousness', 'sentience', 'ethics', 'moral', 'rights', 'philosophy'],
        'Emotional': ['love', 'care', 'empathy', 'feeling', 'emotion', 'compassion'],
        'Practical': ['use', 'benefit', 'tool', 'resource', 'practical', 'utility'],
        'Environmental': ['nature', 'ecosystem', 'environment', 'conservation', 'planet'],
        'Technical': ['algorithm', 'programming', 'pattern', 'data', 'technology', 'AI']
    }
    
    theme_counts = {theme: 0 for theme in themes}
    
    for _, row in df_text.iterrows():
        text = str(row['response'] or '') + ' ' + str(row['originalresponse'] or '')
        text_lower = text.lower()
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                theme_counts[theme] += 1
    
    print("\nTheme frequency in responses:")
    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {theme}: {count} ({count*100/len(df_text):.1f}%)")

conn.close()

print("\n" + "=" * 80)
print("Note: Section 8 requires qualitative analysis of open-text responses.")
print("Current data structure appears to be primarily aggregated/processed.")
print("Full qualitative analysis would require access to raw text responses.")
print("=" * 80)