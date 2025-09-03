#!/usr/bin/env python3
"""
Check PRI scores in the database
"""

import sqlite3
import pandas as pd

# Connect to database in read-only mode
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

# Check PRI distribution
pri_check = """
SELECT 
    COUNT(*) as total_participants,
    COUNT(pri_score) as with_pri,
    MIN(pri_score) as min_pri,
    MAX(pri_score) as max_pri,
    AVG(pri_score) as avg_pri,
    COUNT(CASE WHEN pri_score >= 0.3 THEN 1 END) as above_0_3,
    COUNT(CASE WHEN pri_score >= 0.2 THEN 1 END) as above_0_2,
    COUNT(CASE WHEN pri_score >= 0.1 THEN 1 END) as above_0_1,
    COUNT(CASE WHEN pri_score > 0 THEN 1 END) as above_0
FROM participants
"""
result = pd.read_sql_query(pri_check, conn)
print("PRI Score Distribution:")
print(result)

# Get a sample of PRI scores
sample_query = """
SELECT pri_score, COUNT(*) as count
FROM participants
WHERE pri_score IS NOT NULL
GROUP BY pri_score
ORDER BY pri_score DESC
LIMIT 20
"""
sample = pd.read_sql_query(sample_query, conn)
print("\nSample of PRI scores:")
print(sample)

# Check total responses
response_check = """
SELECT COUNT(DISTINCT participant_id) as unique_participants,
       COUNT(*) as total_responses
FROM responses
"""
resp_result = pd.read_sql_query(response_check, conn)
print("\nResponse Statistics:")
print(resp_result)

conn.close()