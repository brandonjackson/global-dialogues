#!/usr/bin/env python3
"""
Complete analysis for Section 5: Ethics, Rights, and Governance
Final version with correct question text
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# Connect to database in read-only mode
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("=" * 80)
print("SECTION 5: ETHICS, RIGHTS, AND GOVERNANCE")
print("Analysis Date:", datetime.now().isoformat())
print("=" * 80)

# Get reliable participants (PRI >= 0.3)
participants_query = """
SELECT participant_id, pri_score
FROM participants
WHERE pri_score >= 0.3
"""
df_participants = pd.read_sql_query(participants_query, conn)
reliable_participants = df_participants['participant_id'].tolist()
print(f"\nTotal reliable participants (PRI >= 0.3): {len(reliable_participants)}")

# Create a placeholders string for the participant IDs
placeholders = ','.join(['?' for _ in reliable_participants])

print("\n" + "=" * 80)
print("Question 5.1: PREFERRED FUTURE FOR ANIMAL PROTECTION")
print("=" * 80)

# Q70: Which approach feels most appropriate?
q70_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'Which approach feels most appropriate to you for protecting animals?'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'Which approach feels most appropriate to you for protecting animals?'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q70_df = pd.read_sql_query(q70_query, conn, params=reliable_participants + reliable_participants)
print("\n**Finding:** ")
if not q70_df.empty:
    top_approach = q70_df.iloc[0]
    print(f"{top_approach['response']} is preferred by {top_approach['percentage']}% of respondents")
    print("\n**Method:** SQL query grouping responses by preferred future approach")
    print("\n**Details:**")
    for idx, row in q70_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")
else:
    print("No data available for this question")

# Check correlation with human superiority beliefs
print("\nCorrelation with Human-Animal Equality Views:")
superiority_query = f"""
SELECT r1.response as future_preference,
       r2.response as human_view,
       COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Which approach feels most appropriate to you for protecting animals?'
AND r2.question LIKE '%humans are fundamentally%'
AND r1.participant_id IN ({placeholders})
GROUP BY r1.response, r2.response
ORDER BY count DESC
LIMIT 10
"""
superiority_df = pd.read_sql_query(superiority_query, conn, params=reliable_participants)
if not superiority_df.empty:
    print(superiority_df)

print("\n" + "=" * 80)
print("Question 5.2: ANIMAL REPRESENTATION")
print("=" * 80)

# Should animals have legal representatives?
q73_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'If AI helped us understand what an animal really needs, should that animal have the right to a representative such as a lawyer to defend its rights and protections?'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'If AI helped us understand what an animal really needs, should that animal have the right to a representative such as a lawyer to defend its rights and protections?'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q73_df = pd.read_sql_query(q73_query, conn, params=reliable_participants + reliable_participants)
print("\n**Finding:**")
if not q73_df.empty:
    yes_pct = q73_df[q73_df['response'] == 'Yes']['percentage'].values
    if len(yes_pct) > 0:
        print(f"{yes_pct[0]}% believe animals should have the right to legal representation")
    print("\n**Method:** SQL query on legal representation question")
    print("\n**Details:**")
    for idx, row in q73_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

# How should they be represented?
q74_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'If AI could accurately express the voice of non-human animals, we might want to allow them to participate in decision-making. In this situation, which of these do you think is best?'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'If AI could accurately express the voice of non-human animals, we might want to allow them to participate in decision-making. In this situation, which of these do you think is best?'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q74_df = pd.read_sql_query(q74_query, conn, params=reliable_participants + reliable_participants)
if not q74_df.empty:
    print("\nRepresentation Method Preferences:")
    for idx, row in q74_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

print("\n" + "=" * 80)
print("Question 5.3: WHO SHOULD REPRESENT ANIMALS")
print("=" * 80)

# Who should represent animals in decision-making bodies?
q75_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'If animals were represented in decision-making bodies (e.g. the UN, local government, or corporate boards), who do you think should be given the responsibility of representing them?'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'If animals were represented in decision-making bodies (e.g. the UN, local government, or corporate boards), who do you think should be given the responsibility of representing them?'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
LIMIT 5
"""
q75_df = pd.read_sql_query(q75_query, conn, params=reliable_participants + reliable_participants)
print("\n**Finding:**")
if not q75_df.empty:
    top_3 = q75_df.head(3)['response'].tolist()
    print(f"Top 3 choices for animal representation: {', '.join(top_3)}")
    print("\n**Method:** SQL query ranking representation choices")
    print("\n**Details:**")
    for idx, row in q75_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

print("\n" + "=" * 80)
print("Question 5.4: ANIMAL PARTICIPATION IN DEMOCRACY")
print("=" * 80)

# Should animals participate in democratic processes?
q77_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'If other animals had a voice and representation, should they be allowed to participate in human democratic processes?'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'If other animals had a voice and representation, should they be allowed to participate in human democratic processes?'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q77_df = pd.read_sql_query(q77_query, conn, params=reliable_participants + reliable_participants)
print("\n**Finding:**")
if not q77_df.empty:
    support_democracy = q77_df[q77_df['response'].str.contains('Yes', na=False)]['percentage'].sum()
    print(f"{support_democracy}% support some form of animal participation in democratic processes")
    print("\n**Method:** SQL query on democratic participation")
    print("\n**Details:**")
    for idx, row in q77_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

# Correlation with belief in animal culture
culture_democracy_query = f"""
SELECT r1.response as democracy_view,
       r2.response as culture_belief,
       COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'If other animals had a voice and representation, should they be allowed to participate in human democratic processes?'
AND r2.question = 'Do you believe that other animals have their own forms of culture?'
AND r1.participant_id IN ({placeholders})
GROUP BY r1.response, r2.response
ORDER BY r1.response, r2.response
"""
culture_democracy_df = pd.read_sql_query(culture_democracy_query, conn, params=reliable_participants)
if not culture_democracy_df.empty:
    print("\nCorrelation with Belief in Animal Culture:")
    # Calculate percentage who believe in culture AND support democracy
    strong_culture = culture_democracy_df[culture_democracy_df['culture_belief'] == 'Strongly believe']
    if not strong_culture.empty:
        democracy_yes = strong_culture[strong_culture['democracy_view'].str.contains('Yes', na=False)]['count'].sum()
        total_strong = strong_culture['count'].sum()
        if total_strong > 0:
            print(f"Among those who strongly believe animals have culture: {democracy_yes}/{total_strong} ({democracy_yes*100/total_strong:.1f}%) support democratic participation")

print("\n" + "=" * 80)
print("Question 5.5: REGULATING COMMUNICATION")
print("=" * 80)

# Restrict to authorized professionals?
q82_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'Animal communication should be restricted to authorized professionals with certified credentials and appropriate training.'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'Animal communication should be restricted to authorized professionals with certified credentials and appropriate training.'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q82_df = pd.read_sql_query(q82_query, conn, params=reliable_participants + reliable_participants)

# Everyone allowed to listen?
q83_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'Everyone should be allowed to listen to animals, but responding should be restricted to certain people.'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'Everyone should be allowed to listen to animals, but responding should be restricted to certain people.'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q83_df = pd.read_sql_query(q83_query, conn, params=reliable_participants + reliable_participants)

print("\n**Finding:**")
if not q82_df.empty and not q83_df.empty:
    restrict_prof = q82_df[q82_df['response'].str.contains('agree', case=False, na=False)]['percentage'].sum()
    open_listen = q83_df[q83_df['response'].str.contains('agree', case=False, na=False)]['percentage'].sum()
    print(f"{restrict_prof}% support restricting to professionals; {open_listen}% support open listening with restricted responding")
    print("\n**Method:** SQL queries on communication restriction questions")
    print("\n**Details:**")
    print("Professional Restriction:")
    for idx, row in q82_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")
    print("\nOpen Listening:")
    for idx, row in q83_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

# Types of communication to prohibit
q85_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question LIKE '%types of human-to-animal communication should be strictly regulated%'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question LIKE '%types of human-to-animal communication should be strictly regulated%'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
LIMIT 5
"""
q85_df = pd.read_sql_query(q85_query, conn, params=reliable_participants + reliable_participants)
if not q85_df.empty:
    print("\nTop prohibited communication types:")
    for idx, row in q85_df.iterrows():
        print(f"- {row['response'][:80]}: {row['count']} ({row['percentage']}%)")

print("\n" + "=" * 80)
print("Question 5.6: OWNERSHIP OF ANIMAL CREATIONS")
print("=" * 80)

# Who owns animal recordings?
q90_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'If we record an elephant\\'s conversation or a whale\\'s song, who should own that recording?'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'If we record an elephant\\'s conversation or a whale\\'s song, who should own that recording?'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q90_df = pd.read_sql_query(q90_query, conn, params=reliable_participants + reliable_participants)
print("\n**Finding:**")
if not q90_df.empty:
    top_owner = q90_df.iloc[0]
    print(f"Most popular ownership view: {top_owner['response']} ({top_owner['percentage']}%)")
    print("\n**Method:** SQL query on recording ownership")
    print("\n**Details:**")
    for idx, row in q90_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

print("\n" + "=" * 80)
print("Question 5.7: SHOULD ANIMALS BE ABLE TO EARN MONEY?")
print("=" * 80)

# Economic rights for animals
q91_query = f"""
SELECT response, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM responses 
                                 WHERE question = 'Do you think that in the future non-humans should be able to:'
                                 AND participant_id IN ({placeholders})), 2) as percentage
FROM responses
WHERE question = 'Do you think that in the future non-humans should be able to:'
AND participant_id IN ({placeholders})
GROUP BY response
ORDER BY count DESC
"""
q91_df = pd.read_sql_query(q91_query, conn, params=reliable_participants + reliable_participants)
print("\n**Finding:**")
if not q91_df.empty:
    earn_money = q91_df[q91_df['response'] == 'Earn money']['percentage'].values
    own_property = q91_df[q91_df['response'] == 'Own property']['percentage'].values
    none_above = q91_df[q91_df['response'] == 'None of the above']['percentage'].values
    
    if len(earn_money) > 0:
        print(f"{earn_money[0]}% support animals earning money")
    if len(own_property) > 0:
        print(f"{own_property[0]}% support animals owning property")
    if len(none_above) > 0:
        print(f"{none_above[0]}% oppose all economic rights for animals")
    
    print("\n**Method:** SQL query on economic rights multi-select question")
    print("\n**Details:**")
    for idx, row in q91_df.iterrows():
        print(f"- {row['response']}: {row['count']} ({row['percentage']}%)")

# Age analysis for economic rights
print("\n--- Age Group Analysis ---")
age_economic_query = f"""
SELECT 
    r2.response as age_group,
    r1.response as economic_right,
    COUNT(*) as count
FROM responses r1
JOIN responses r2 ON r1.participant_id = r2.participant_id
WHERE r1.question = 'Do you think that in the future non-humans should be able to:'
AND r2.question = 'How old are you?'
AND r1.participant_id IN ({placeholders})
AND r1.response IN ('Earn money', 'Own property', 'None of the above')
GROUP BY age_group, economic_right
ORDER BY 
    CASE age_group
        WHEN '18-25' THEN 1
        WHEN '26-35' THEN 2
        WHEN '36-45' THEN 3
        WHEN '46-55' THEN 4
        WHEN '56-65' THEN 5
        WHEN '65+' THEN 6
        ELSE 7
    END,
    count DESC
"""
age_df = pd.read_sql_query(age_economic_query, conn, params=reliable_participants)
if not age_df.empty:
    # Calculate support by age group
    for age in ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']:
        age_data = age_df[age_df['age_group'] == age]
        if not age_data.empty:
            earn_count = age_data[age_data['economic_right'] == 'Earn money']['count'].sum()
            total_count = age_data['count'].sum()
            print(f"{age}: {earn_count} support earning money ({earn_count*100/total_count:.1f}% of age group)")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)