#!/usr/bin/env python3
"""
Check GD5 database structure and tables
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Get all tables
tables_query = """
SELECT name FROM sqlite_master 
WHERE type='table'
ORDER BY name;
"""
tables = pd.read_sql_query(tables_query, conn)
print("Tables in database:")
print(tables)

# Check each table's schema and row count
for table_name in tables['name']:
    print(f"\n{'='*60}")
    print(f"Table: {table_name}")
    print('='*60)
    
    # Get schema
    schema_query = f"PRAGMA table_info({table_name})"
    schema = pd.read_sql_query(schema_query, conn)
    print("\nSchema:")
    print(schema[['name', 'type']].to_string())
    
    # Get row count
    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
    count = pd.read_sql_query(count_query, conn)
    print(f"\nRow count: {count['count'][0]}")
    
    # Show sample data
    if count['count'][0] > 0:
        sample_query = f"SELECT * FROM {table_name} LIMIT 3"
        sample = pd.read_sql_query(sample_query, conn)
        print(f"\nSample data (first 3 rows):")
        print(sample.head())

conn.close()