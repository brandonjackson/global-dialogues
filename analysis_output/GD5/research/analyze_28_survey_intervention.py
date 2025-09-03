#!/usr/bin/env python3
"""
Section 28: Survey as Intervention — Measuring Persuasion & Change
Analyzing opinion shifts from beginning to end of survey
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get data comparing initial and final worldview questions
# Q31/Q93 are about human-nature relationship
# Q32/Q94 are about human superiority/equality
df = pd.read_sql_query("""
SELECT 
    participant_id,
    Q2 as age,
    Q7 as region,
    Q44 as facts_impact,
    Q45 as emotional_response,
    Q48 as imagine_umwelt,
    Q31 as initial_nature_view,
    Q93 as final_nature_view,
    unmapped_32 as initial_superiority,
    Q94 as final_superiority
FROM participant_responses
""", conn)

print("=== SECTION 28: SURVEY AS INTERVENTION ===\n")

# Check if unmapped_32 exists and what it contains
print("Checking Q32/unmapped_32 data...")
print(df['initial_superiority'].value_counts().head())
print("\nQ94 (final superiority) data:")
print(df['final_superiority'].value_counts().head())

# Since unmapped_32 might not be Q32, let's check Q31/Q93 which are clearer
print("\n=== Q28.1: WORLDVIEW CHANGE MEASUREMENT ===")
print("\nQ31 (Initial nature view):")
print(df['initial_nature_view'].value_counts())
print("\nQ93 (Final nature view):")
print(df['final_nature_view'].value_counts())

# Calculate changes in Q93 vs Q31 (nature relationship)
df['nature_changed'] = df['initial_nature_view'] != df['final_nature_view']
valid_pairs = df[df['initial_nature_view'].notna() & df['final_nature_view'].notna() & 
                  (df['initial_nature_view'] != '--') & (df['final_nature_view'] != '--')]

change_count = valid_pairs['nature_changed'].sum()
total_valid = len(valid_pairs)
change_rate = (change_count / total_valid * 100) if total_valid > 0 else 0

print(f"\nNature relationship view changes:")
print(f"  Valid pairs: {total_valid}")
print(f"  Changed views: {change_count} ({change_rate:.1f}%)")
print(f"  Unchanged: {total_valid - change_count} ({100-change_rate:.1f}%)")

# Q94 superiority changes
df['superiority_changed'] = df['initial_superiority'] != df['final_superiority']
valid_sup = df[df['initial_superiority'].notna() & df['final_superiority'].notna() & 
                (df['initial_superiority'] != '--') & (df['final_superiority'] != '--')]

if len(valid_sup) > 0:
    sup_change_count = valid_sup['superiority_changed'].sum()
    sup_change_rate = sup_change_count / len(valid_sup) * 100
    print(f"\nSuperiority view changes:")
    print(f"  Valid pairs: {len(valid_sup)}")
    print(f"  Changed views: {sup_change_count} ({sup_change_rate:.1f}%)")

# === Q28.2: DIRECTION OF BELIEF SHIFTS ===
print("\n=== Q28.2: DIRECTION OF BELIEF SHIFTS ===")

# For Q94 (superiority), track movement toward equality
changers = valid_sup[valid_sup['superiority_changed']]
if len(changers) > 0:
    # Movement analysis
    towards_equal = changers[
        (changers['final_superiority'].str.contains('equal', case=False, na=False)) &
        (~changers['initial_superiority'].str.contains('equal', case=False, na=False))
    ]
    away_from_equal = changers[
        (~changers['final_superiority'].str.contains('equal', case=False, na=False)) &
        (changers['initial_superiority'].str.contains('equal', case=False, na=False))
    ]
    
    print(f"Among {len(changers)} who changed superiority views:")
    print(f"  Moved toward equality: {len(towards_equal)} ({len(towards_equal)/len(changers)*100:.1f}%)")
    print(f"  Moved away from equality: {len(away_from_equal)} ({len(away_from_equal)/len(changers)*100:.1f}%)")

# === Q28.3: SCIENTIFIC FACTS IMPACT ===
print("\n=== Q28.3: SCIENTIFIC FACTS IMPACT ON CHANGE ===")

# Group by facts impact level
impact_groups = df.groupby('facts_impact')['superiority_changed'].agg(['mean', 'count'])
impact_groups['change_rate'] = impact_groups['mean'] * 100

print("Change rate by facts impact level:")
for impact, row in impact_groups.iterrows():
    if pd.notna(impact) and impact != '--' and row['count'] >= 10:
        print(f"  {impact}: {row['change_rate']:.1f}% (n={row['count']:.0f})")

# === Q28.4: EMOTIONAL RESPONSE AND OPINION CHANGE ===
print("\n=== Q28.4: EMOTIONAL RESPONSE AND OPINION CHANGE ===")

# Categorize emotions
df['feels_connected'] = df['emotional_response'].str.contains('Connected', case=False, na=False)
df['feels_protective'] = df['emotional_response'].str.contains('Protective', case=False, na=False)
df['feels_skeptical'] = df['emotional_response'].str.contains('Skeptical', case=False, na=False)
df['feels_curious'] = df['emotional_response'].str.contains('Curious', case=False, na=False)

for emotion, label in [
    ('feels_connected', 'Connected'),
    ('feels_protective', 'Protective'),
    ('feels_skeptical', 'Skeptical'),
    ('feels_curious', 'Curious')
]:
    emotion_group = df[df[emotion]]
    if len(emotion_group) > 10:
        change_rate = emotion_group['superiority_changed'].mean() * 100
        print(f"  {label}: {change_rate:.1f}% changed views (n={len(emotion_group)})")

# === Q28.5: UMWELT IMAGINATION ===
print("\n=== Q28.5: UMWELT IMAGINATION AND WORLDVIEW CHANGE ===")

imagine_groups = df.groupby('imagine_umwelt')['superiority_changed'].agg(['mean', 'count'])
imagine_groups['change_rate'] = imagine_groups['mean'] * 100

print("Change rate by umwelt imagination:")
for imagine, row in imagine_groups.iterrows():
    if pd.notna(imagine) and imagine != '--' and row['count'] >= 10:
        print(f"  {imagine}: {row['change_rate']:.1f}% (n={row['count']:.0f})")

# === Q28.6: GENERATIONAL DIFFERENCES ===
print("\n=== Q28.6: GENERATIONAL DIFFERENCES IN PERSUASION ===")

age_groups = df.groupby('age')['superiority_changed'].agg(['mean', 'count'])
age_groups['change_rate'] = age_groups['mean'] * 100

print("Change rate by age group:")
for age, row in age_groups.iterrows():
    if pd.notna(age) and row['count'] >= 10:
        print(f"  {age}: {row['change_rate']:.1f}% (n={row['count']:.0f})")

# === Q28.7: REGIONAL CLUSTERING ===
print("\n=== Q28.7: REGIONAL CLUSTERING OF SHIFTS ===")

# Top regions by response count
major_regions = df['region'].value_counts().head(10).index
regional_changes = df[df['region'].isin(major_regions)].groupby('region')['superiority_changed'].agg(['mean', 'count'])
regional_changes['change_rate'] = regional_changes['mean'] * 100
regional_changes = regional_changes.sort_values('change_rate', ascending=False)

print("Change rate by major regions:")
for region, row in regional_changes.iterrows():
    print(f"  {region}: {row['change_rate']:.1f}% (n={row['count']:.0f})")

conn.close()