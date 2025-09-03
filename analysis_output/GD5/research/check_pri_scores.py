#!/usr/bin/env python3
"""
Check PRI score distribution in GD5 database
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Check participants table
query = """
SELECT COUNT(*) as total_participants,
       MIN(pri_score) as min_pri,
       MAX(pri_score) as max_pri,
       AVG(pri_score) as avg_pri,
       SUM(CASE WHEN pri_score >= 0.3 THEN 1 ELSE 0 END) as above_0_3,
       SUM(CASE WHEN pri_score >= 0.2 THEN 1 ELSE 0 END) as above_0_2,
       SUM(CASE WHEN pri_score >= 0.1 THEN 1 ELSE 0 END) as above_0_1,
       SUM(CASE WHEN pri_score >= 0.0 THEN 1 ELSE 0 END) as above_0_0
FROM participants
"""

result = pd.read_sql_query(query, conn)
print("PRI Score Statistics:")
print(result.to_string())

# Check distribution
query2 = """
SELECT 
    CASE 
        WHEN pri_score < 0.0 THEN '< 0.0'
        WHEN pri_score < 0.1 THEN '0.0-0.1'
        WHEN pri_score < 0.2 THEN '0.1-0.2'
        WHEN pri_score < 0.3 THEN '0.2-0.3'
        WHEN pri_score < 0.4 THEN '0.3-0.4'
        WHEN pri_score < 0.5 THEN '0.4-0.5'
        ELSE '>= 0.5'
    END as pri_range,
    COUNT(*) as count
FROM participants
GROUP BY pri_range
ORDER BY pri_range
"""

dist = pd.read_sql_query(query2, conn)
print("\n\nPRI Score Distribution:")
print(dist.to_string())

# Check if PRI scores are NULL
query3 = """
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN pri_score IS NULL THEN 1 ELSE 0 END) as null_count,
    SUM(CASE WHEN pri_score IS NOT NULL THEN 1 ELSE 0 END) as non_null_count
FROM participants
"""

null_check = pd.read_sql_query(query3, conn)
print("\n\nNULL Check:")
print(null_check.to_string())

# Sample some actual PRI scores
query4 = """
SELECT participant_id, pri_score
FROM participants
WHERE pri_score IS NOT NULL
LIMIT 20
"""

sample = pd.read_sql_query(query4, conn)
print("\n\nSample PRI Scores:")
print(sample.to_string())

conn.close()