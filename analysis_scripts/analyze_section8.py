#!/usr/bin/env python3
"""
Analyze Section 8 "Headline Grabber" questions for GD4 Investigation
"""

import sqlite3
import pandas as pd
import numpy as np
import json
from collections import Counter

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Get participant data with Q115 (hopes and fears)
query = """
SELECT 
    pr.participant_id,
    pr.Q115 as hopes_fears,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q115 IS NOT NULL
"""

df = pd.read_sql_query(query, conn)

# Parse JSON arrays
df['items_list'] = df['hopes_fears'].apply(lambda x: json.loads(x) if x else [])

# Separate hopes and fears
hopes = [
    "Significant reduction in loneliness",
    "More accessible mental health support",
    "Enhanced learning and personal growth",
    "New forms of self-expression and creativity",
    "Increased overall happiness"
]

fears = [
    "Widespread social isolation",
    "Loss of genuine human connection",
    "Decline in human empathy and social skills",
    "Manipulation or exploitation of vulnerable people",
    "Over-dependence on AI for emotional needs",
    "Erosion of privacy on a mass scale"
]

print("=== Q8.5: Society's Greatest Fears about AI in Personal Relationships ===")
print(f"Total participants: {len(df)}")

# Count fears
fear_counts = Counter()
for items in df['items_list']:
    for item in items:
        if item in fears:
            fear_counts[item] += 1

print("\nFears Ranking (n=1012 participants):")
for fear, count in fear_counts.most_common():
    pct = 100.0 * count / len(df)
    print(f"{count:3d} ({pct:5.1f}%) - {fear}")

# Top 3 fears
top_fears = fear_counts.most_common(3)
print(f"\nTOP 3 FEARS:")
for i, (fear, count) in enumerate(top_fears, 1):
    pct = 100.0 * count / len(df)
    print(f"{i}. {fear}: {pct:.1f}% ({count}/{len(df)})")

print("\n=== Q8.6: Top Hopes for AI in Our Lives ===")

# Count hopes
hope_counts = Counter()
for items in df['items_list']:
    for item in items:
        if item in hopes:
            hope_counts[item] += 1

print("\nHopes Ranking (n=1012 participants):")
for hope, count in hope_counts.most_common():
    pct = 100.0 * count / len(df)
    print(f"{count:3d} ({pct:5.1f}%) - {hope}")

# Top 3 hopes
top_hopes = hope_counts.most_common(3)
print(f"\nTOP 3 HOPES:")
for i, (hope, count) in enumerate(top_hopes, 1):
    pct = 100.0 * count / len(df)
    print(f"{i}. {hope}: {pct:.1f}% ({count}/{len(df)})")

# Calculate how many selected each
print("\n=== Selection Patterns ===")
total_fears_selected = sum(fear_counts.values())
total_hopes_selected = sum(hope_counts.values())
avg_fears = total_fears_selected / len(df)
avg_hopes = total_hopes_selected / len(df)

print(f"Average fears selected per person: {avg_fears:.2f}")
print(f"Average hopes selected per person: {avg_hopes:.2f}")
print(f"Total fears expressed: {total_fears_selected}")
print(f"Total hopes expressed: {total_hopes_selected}")

# Most common combinations
print("\n=== Most Common Fear Combinations ===")
fear_combinations = Counter()
for items in df['items_list']:
    fear_items = tuple(sorted([item for item in items if item in fears]))
    if len(fear_items) >= 2:
        fear_combinations[fear_items] += 1

for combo, count in fear_combinations.most_common(5):
    pct = 100.0 * count / len(df)
    if len(combo) == 2:
        print(f"{count:3d} ({pct:4.1f}%) - {combo[0]} + {combo[1]}")

conn.close()