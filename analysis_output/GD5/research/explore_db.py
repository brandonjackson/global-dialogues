#!/usr/bin/env python3
"""
Explore GD5 database structure
"""

import sqlite3
import pandas as pd

# Connect to database in read-only mode
db_path = '/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

print("Database Tables:")
print("=" * 80)

# Get all tables
tables_query = """
SELECT name FROM sqlite_master 
WHERE type='table'
ORDER BY name;
"""
tables = pd.read_sql_query(tables_query, conn)
print(tables)

print("\n" + "=" * 80)
print("Responses table columns:")
print("=" * 80)

# Get columns from responses table
columns_query = """
PRAGMA table_info(responses);
"""
columns = pd.read_sql_query(columns_query, conn)
print(columns[['name', 'type']])

print("\n" + "=" * 80)
print("Sample of responses table:")
print("=" * 80)

# Get a sample of responses
sample_query = """
SELECT * FROM responses LIMIT 2;
"""
sample = pd.read_sql_query(sample_query, conn)
print(sample.columns.tolist())

# Check if there's a participants table or if PRI info is in responses
print("\n" + "=" * 80)
print("Checking for PRI score column:")
print("=" * 80)

pri_check = """
SELECT COUNT(DISTINCT participant_id) as total_participants,
       COUNT(CASE WHEN pri_score IS NOT NULL THEN 1 END) as with_pri
FROM responses
LIMIT 1;
"""
try:
    pri_result = pd.read_sql_query(pri_check, conn)
    print("PRI score found in responses table:")
    print(pri_result)
except:
    print("No pri_score column in responses table")

# Check for participants table
print("\n" + "=" * 80)
print("Checking participants table structure (if exists):")
print("=" * 80)

try:
    part_columns_query = """
    PRAGMA table_info(participants);
    """
    part_columns = pd.read_sql_query(part_columns_query, conn)
    print(part_columns[['name', 'type']])
    
    # Get sample from participants
    part_sample = """
    SELECT * FROM participants LIMIT 2;
    """
    part_data = pd.read_sql_query(part_sample, conn)
    print("\nSample data:")
    print(part_data)
except:
    print("No participants table found")

conn.close()