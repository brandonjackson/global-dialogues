#!/usr/bin/env python3
"""
Section 9.1: The "Tech-First Futurist" Persona Analysis
Segment: Excited about AI + Trust AI chatbots + Believe AI will improve lives
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# First, identify the Tech-First Futurist segment
# Q5: More excited about AI
# Q17: Trust AI chatbots 
# Q23-Q27: AI will improve lives (need to check these columns)

# Check what Q23-Q27 contain
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(participant_responses)")
columns = cursor.fetchall()
q23_27_cols = [col[1] for col in columns if col[1] in ['Q23', 'Q24', 'Q25', 'Q26', 'Q27']]
print("Q23-Q27 columns found:", q23_27_cols)

# Get sample values
for col in q23_27_cols:
    cursor.execute(f"SELECT DISTINCT {col} FROM participant_responses WHERE {col} IS NOT NULL LIMIT 3")
    vals = cursor.fetchall()
    print(f"\n{col} sample values:")
    for v in vals:
        print(f"  {v[0]}")

# Define the Tech-First Futurist segment
segment_query = """
SELECT 
    participant_id,
    Q5 as ai_excitement,
    Q17 as ai_chatbot_trust,
    Q23 as ai_workplace,
    Q24 as ai_mental_health,
    Q25 as ai_education,
    Q26 as ai_environment,
    Q27 as ai_justice,
    -- Governance questions
    Q82 as restrict_to_professionals,
    Q83 as everyone_should_listen,
    Q84 as regulate_companies,
    Q85 as prohibit_harmful_uses,
    Q76 as ecocentric_ai_society
FROM participant_responses
WHERE Q5 IS NOT NULL AND Q17 IS NOT NULL
"""

df = pd.read_sql_query(segment_query, conn)

# Create Tech-First Futurist flag
def is_tech_futurist(row):
    # More excited about AI
    excited = 'excited' in str(row['ai_excitement']).lower() if pd.notna(row['ai_excitement']) else False
    
    # Trust AI chatbots (4 or 5 on scale)
    trust_ai = False
    if pd.notna(row['ai_chatbot_trust']):
        try:
            trust_val = int(row['ai_chatbot_trust'])
            trust_ai = trust_val >= 4
        except:
            trust_ai = 'trust' in str(row['ai_chatbot_trust']).lower()
    
    # Believe AI will improve life (at least 3 areas marked as "Noticeably Better" or "Profoundly Better")
    ai_improve_count = 0
    for col in ['ai_workplace', 'ai_mental_health', 'ai_education', 'ai_environment', 'ai_justice']:
        if pd.notna(row[col]) and ('better' in str(row[col]).lower()):
            ai_improve_count += 1
    
    return excited and trust_ai and ai_improve_count >= 3

df['is_tech_futurist'] = df.apply(is_tech_futurist, axis=1)

print(f"\n=== TECH-FIRST FUTURIST SEGMENT ===")
print(f"Total respondents: {len(df)}")
print(f"Tech-First Futurists: {df['is_tech_futurist'].sum()} ({df['is_tech_futurist'].mean()*100:.1f}%)")
print(f"General population: {(~df['is_tech_futurist']).sum()} ({(~df['is_tech_futurist']).mean()*100:.1f}%)")

# Now analyze governance attitudes (Q82-Q85, Q76)
# Need to check what these columns contain
governance_cols = ['Q82', 'Q83', 'Q84', 'Q85', 'Q76']
for col in governance_cols:
    try:
        cursor.execute(f"SELECT DISTINCT {col} FROM participant_responses WHERE {col} IS NOT NULL LIMIT 5")
        vals = cursor.fetchall()
        print(f"\n{col} values:")
        for v in vals[:3]:
            print(f"  {str(v[0])[:100]}")
    except:
        print(f"\n{col}: column not found")

conn.close()