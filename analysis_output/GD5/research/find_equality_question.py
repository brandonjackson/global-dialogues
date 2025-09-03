#!/usr/bin/env python3
"""
Find the equality question in the data
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db')

# Get participant responses
query = "SELECT Q94, COUNT(*) as count FROM participant_responses GROUP BY Q94"
df = pd.read_sql_query(query, conn)

print("Q94 values (likely the repeated Q32 - human superiority/equality):")
print(df)

print("\n" + "="*60)

# Check Q93 too
query2 = "SELECT Q93, COUNT(*) as count FROM participant_responses GROUP BY Q93"
df2 = pd.read_sql_query(query2, conn)

print("Q93 values (likely the repeated Q31 - human-nature relationship):")
print(df2)

conn.close()