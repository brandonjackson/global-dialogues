import sqlite3
import pandas as pd
import numpy as np
import json

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Question 9.2: The Meaningful vs. Automated Job
# How many people believe their job is both "making a meaningful contribution to the world" 
# and that it *should* be automated in the next 10 years? 
# What does this group believe AI's impact on their personal "sense of purpose" will be?

print("\n" + "="*80)
print("9.2 The Meaningful vs. Automated Job Paradox")
print("="*80)

# Get participant data with job-related questions
# Q46: Is your job making a meaningful contribution to the world?
# Q48: Do you think your job should be automated in the next 10 years?
# Q47: Do you think your job is likely to be automated in the next 10 years?
# Q44: Do you think the increased use of AI across society is likely to make your sense of purpose better, worse or stay the same in the next 10 years?
# Q43: Do you think the increased use of AI across society is likely to improve or worsen the availability of good jobs in the next 10 years?
query = """
SELECT 
    pr.participant_id,
    pr.Q46 as job_meaningful,  -- Does your job make a meaningful contribution?
    pr.Q48 as job_should_automate,  -- Should your job be automated in next 10 years?
    pr.Q44 as ai_impact_purpose,  -- AI's impact on sense of purpose  
    pr.Q47 as job_automation_likely,  -- How likely is your job to be automated?
    pr.Q43 as ai_impact_jobs,  -- AI impact on availability of good jobs
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""

df = pd.read_sql_query(query, conn)
print(f"\nAnalyzing {len(df)} participants with PRI >= 0.3")

# Remove non-workers
df_workers = df[df['job_meaningful'].notna() & (df['job_meaningful'] != 'I am not currently employed')]
print(f"Filtering to {len(df_workers)} employed participants")

# 1. Distribution of job meaningfulness
print("\n1. Job Meaningfulness Distribution:")
meaningful_counts = df_workers['job_meaningful'].value_counts()
for response, count in meaningful_counts.items():
    pct = (count / len(df_workers)) * 100
    print(f"   {response}: {count} ({pct:.1f}%)")

# 2. Distribution of automation preference
print("\n2. Should Job Be Automated (Next 10 Years):")
automate_counts = df_workers['job_should_automate'].value_counts()
for response, count in automate_counts.items():
    pct = (count / len(df_workers)) * 100
    print(f"   {response}: {count} ({pct:.1f}%)")

# 3. Find the paradox group: Meaningful AND should be automated
paradox_group = df_workers[
    (df_workers['job_meaningful'] == 'Yes') &
    (df_workers['job_should_automate'] == 'Yes')
]

print(f"\n3. The Paradox Group:")
print(f"   {len(paradox_group)} people ({len(paradox_group)/len(df_workers)*100:.1f}% of workers)")
print(f"   believe their job is meaningful AND should be automated")

# No levels of agreement for Yes/No questions
# strongly_both removed

# 4. What does the paradox group believe about AI's impact on purpose?
print("\n4. Paradox Group's View on AI Impact on Sense of Purpose:")
if len(paradox_group) > 0:
    purpose_counts = paradox_group['ai_impact_purpose'].value_counts()
    for response, count in purpose_counts.items():
        pct = (count / len(paradox_group)) * 100
        print(f"   {response}: {count} ({pct:.1f}%)")
    
    # Compare to non-paradox workers
    non_paradox = df_workers[~df_workers.index.isin(paradox_group.index)]
    print(f"\n   Comparison - Non-Paradox Workers' View on Purpose (n={len(non_paradox)}):")
    non_purpose_counts = non_paradox['ai_impact_purpose'].value_counts()
    for response, count in non_purpose_counts.items():
        pct = (count / len(non_paradox)) * 100
        print(f"   {response}: {count} ({pct:.1f}%)")

# 5. How likely do they think automation is?
print("\n5. Paradox Group's Belief About Automation Likelihood:")
if len(paradox_group) > 0:
    likely_counts = paradox_group['job_automation_likely'].value_counts()
    for response, count in likely_counts.items():
        pct = (count / len(paradox_group)) * 100
        print(f"   {response}: {count} ({pct:.1f}%)")

# 6. Views on job availability
print("\n6. Paradox Group's View on AI Impact on Job Availability:")
if len(paradox_group) > 0:
    jobs_counts = paradox_group['ai_impact_jobs'].value_counts()
    for response, count in jobs_counts.items():
        pct = (count / len(paradox_group)) * 100
        print(f"   {response}: {count} ({pct:.1f}%)")

# 7. Create detailed breakdown
print("\n7. Detailed Breakdown of Paradox Combinations:")
combinations = df_workers.groupby(['job_meaningful', 'job_should_automate']).size()
meaningful_yes = df_workers[df_workers['job_meaningful'] == 'Yes']
meaningful_no = df_workers[df_workers['job_meaningful'] == 'No']

print(f"\n   Meaningful job + Should automate: {len(paradox_group)} ({len(paradox_group)/len(df_workers)*100:.1f}%)")
print(f"   Meaningful job + Should NOT automate: {len(meaningful_yes[meaningful_yes['job_should_automate'] == 'No'])} ({len(meaningful_yes[meaningful_yes['job_should_automate'] == 'No'])/len(df_workers)*100:.1f}%)")
print(f"   NOT meaningful + Should automate: {len(meaningful_no[meaningful_no['job_should_automate'] == 'Yes'])} ({len(meaningful_no[meaningful_no['job_should_automate'] == 'Yes'])/len(df_workers)*100:.1f}%)")
print(f"   NOT meaningful + Should NOT automate: {len(meaningful_no[meaningful_no['job_should_automate'] == 'No'])} ({len(meaningful_no[meaningful_no['job_should_automate'] == 'No'])/len(df_workers)*100:.1f}%)")

# 8. Statistical summary
print("\n8. Statistical Summary:")
print(f"   Workers believing job is meaningful: {len(meaningful_yes)} ({len(meaningful_yes)/len(df_workers)*100:.1f}%)")
print(f"   Workers believing job should be automated: {len(df_workers[df_workers['job_should_automate'] == 'Yes'])} ({len(df_workers[df_workers['job_should_automate'] == 'Yes'])/len(df_workers)*100:.1f}%)")

# Calculate correlation between meaningfulness and automation preference
# Convert to numeric for Yes/No questions
binary_map = {'Yes': 1, 'No': 0, "Don't Know": None}
df_workers['meaningful_numeric'] = df_workers['job_meaningful'].map(binary_map)
df_workers['automate_numeric'] = df_workers['job_should_automate'].map(binary_map)

# Drop NaN values for correlation
valid_corr = df_workers[['meaningful_numeric', 'automate_numeric']].dropna()
if len(valid_corr) > 0:
    correlation = valid_corr.corr().iloc[0, 1]
    print(f"\n   Correlation between meaningfulness and automation preference: {correlation:.3f}")
    if correlation < -0.2:
        print("   (Negative correlation: meaningful jobs less likely to want automation)")
    elif correlation > 0.2:
        print("   (Positive correlation: meaningful jobs more likely to want automation)")
    else:
        print("   (Weak/no correlation)")

conn.close()

print("\n" + "="*80)
print(f"Key Finding: {len(paradox_group)/len(df_workers)*100:.1f}% of workers experience the paradox -")
print("believing their job makes a meaningful contribution AND should be automated.")
if len(paradox_group) > 0:
    better_purpose = len(paradox_group[paradox_group['ai_impact_purpose'].isin(['Noticeably Better', 'Profoundly Better'])])
    worse_purpose = len(paradox_group[paradox_group['ai_impact_purpose'].isin(['Noticeably Worse', 'Profoundly Worse'])])
    same_purpose = len(paradox_group[paradox_group['ai_impact_purpose'] == 'No Major Change'])
    if better_purpose > worse_purpose and better_purpose > same_purpose:
        print(f"Most paradox workers ({better_purpose/len(paradox_group)*100:.1f}%) believe AI will make their sense of purpose BETTER.")
    elif worse_purpose > better_purpose and worse_purpose > same_purpose:
        print(f"Most paradox workers ({worse_purpose/len(paradox_group)*100:.1f}%) believe AI will make their sense of purpose WORSE.")
    else:
        print(f"Most paradox workers ({same_purpose/len(paradox_group)*100:.1f}%) believe their sense of purpose will STAY THE SAME.")
print("="*80)