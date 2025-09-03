#!/usr/bin/env python3
"""
Check the distribution of outlook questions Q23, Q25, Q26
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Get participant responses
query = """
SELECT Q23, Q25, Q26, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY Q23, Q25, Q26
ORDER BY count DESC
"""

df = pd.read_sql_query(query, conn)

print("Distribution of outlook responses:")
print(df.head(20))

print("\n" + "="*60)

# Check individual distributions
for q in ['Q23', 'Q25', 'Q26']:
    query = f"""
    SELECT {q}, COUNT(*) as count
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
    GROUP BY {q}
    ORDER BY count DESC
    """
    
    result = pd.read_sql_query(query, conn)
    print(f"\n{q} distribution:")
    print(result)

conn.close()