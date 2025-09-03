import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Connect to database
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)
cursor = conn.cursor()

# Map questions to their IDs
def get_question_mapping():
    query = """
    SELECT DISTINCT question_id, question 
    FROM responses 
    ORDER BY question
    """
    df = pd.read_sql_query(query, conn)
    return df

def find_specific_questions():
    # Questions for Section 3
    questions_needed = {
        'Q39': 'Do you believe that other animals have their own forms of language?',
        'Q40': 'Do you believe that other animals have their own forms of emotion?',
        'Q41': 'Do you believe that other animals have their own forms of culture?',
        'Q43': 'Humans are not the only animals that use names',  # The scientific facts
        'Q44': 'To what extent does knowing this impact your perspective on animals?',
        'Q45': 'How does this knowledge make you feel?',
        'Q35': 'Caring for animals',
        'Q37': 'Noticing or observing animals',
        'Q48': 'Have you ever tried to imagine experiencing',
        'Q50': 'How important do you think it is for humans to understand'
    }
    
    result = {}
    for key, search_term in questions_needed.items():
        query = f"""
        SELECT DISTINCT question_id, question 
        FROM responses 
        WHERE question LIKE '%{search_term}%'
        LIMIT 1
        """
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            result[key] = {
                'id': df.iloc[0]['question_id'],
                'text': df.iloc[0]['question']
            }
    
    return result

# Get specific questions for Section 3
section3_questions = find_specific_questions()
print("\nSection 3 Questions Found:")
for key, val in section3_questions.items():
    print(f"{key}: {val['id'][:8]}... - {val['text'][:80]}...")