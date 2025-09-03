#!/usr/bin/env python3
"""
Section 1 Analysis: Demographics and Foundational Beliefs
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# First, let's map all the questions
print("Mapping questions...")
question_mapping_query = """
SELECT DISTINCT question_id, question 
FROM responses 
ORDER BY question
"""

question_df = pd.read_sql_query(question_mapping_query, conn)

# Save question mapping for reference
with open('question_mapping.txt', 'w') as f:
    for idx, row in question_df.iterrows():
        f.write(f"{row['question_id']}: {row['question']}\n")
        print(f"{row['question_id']}: {row['question'][:100]}...")

print(f"\nTotal unique questions: {len(question_df)}")
print("\nQuestion mapping saved to question_mapping.txt")

# Now let's look at the participant table structure
print("\n\nParticipant table structure:")
participant_info = pd.read_sql_query("SELECT * FROM participants LIMIT 5", conn)
print(participant_info.columns.tolist())
print(participant_info.head())