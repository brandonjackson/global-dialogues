#!/usr/bin/env python3
"""
Check Q77 and Q54 response distributions
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Get participant responses
query = """
SELECT Q77, Q54, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY Q77, Q54
"""

df = pd.read_sql_query(query, conn)

print("Q77 (Democratic participation) distribution:")
q77_counts = df.groupby('Q77')['count'].sum().sort_values(ascending=False)
for response, count in q77_counts.items():
    if pd.notna(response):
        print(f"  {response[:60]}...: {count}")

print("\n" + "="*60)
print("Q54 (Feelings about AI translation) distribution:")
q54_counts = df.groupby('Q54')['count'].sum().sort_values(ascending=False)
for response, count in q54_counts.items():
    if pd.notna(response):
        print(f"  {response}: {count}")

conn.close()