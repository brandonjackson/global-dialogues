#!/usr/bin/env python3
"""
Explore GD5 database to find correct question IDs
"""

import sqlite3
import pandas as pd

# Database path
DB_PATH = "../../../Data/GD5/GD5.db"

def explore_questions():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    
    # Get all unique questions
    query = """
    SELECT DISTINCT question_id, question, question_type
    FROM responses
    ORDER BY question_id
    """
    
    questions = pd.read_sql_query(query, conn)
    
    # Filter for relevant questions based on keywords
    keywords = {
        'Q57': ['trust', 'AI', 'accurately', 'translate', 'animal'],
        'Q55': ['interested', 'know', 'animal', 'say', 'feel'],
        'Q61': ['trust', 'AI', 'humans', 'wildlife', 'conflict'],
        'Q66': ['prefer', 'direct', 'communication', 'simulation'],
        'Q17': ['trust', 'AI', 'chatbot']
    }
    
    print("=" * 80)
    print("SEARCHING FOR SECTION 4 QUESTIONS")
    print("=" * 80)
    
    for q_num, terms in keywords.items():
        print(f"\nSearching for {q_num} with terms: {terms}")
        print("-" * 40)
        
        for _, row in questions.iterrows():
            q_text = row['question'].lower()
            if any(term.lower() in q_text for term in terms):
                print(f"ID: {row['question_id']}")
                print(f"Type: {row['question_type']}")
                print(f"Question: {row['question'][:150]}...")
                print()
    
    # Also look for questions by type
    print("\n" + "=" * 80)
    print("POLL QUESTIONS (likely multiple choice)")
    print("=" * 80)
    
    poll_questions = questions[questions['question_type'] == 'poll']
    for _, row in poll_questions.iterrows():
        if any(word in row['question'].lower() for word in ['trust', 'interest', 'prefer', 'AI', 'animal']):
            print(f"ID: {row['question_id']}")
            print(f"Question: {row['question'][:150]}...")
            
            # Get sample responses for this question
            sample_query = """
            SELECT DISTINCT response
            FROM responses
            WHERE question_id = ?
            LIMIT 5
            """
            samples = pd.read_sql_query(sample_query, conn, params=[row['question_id']])
            print("Sample responses:", list(samples['response']))
            print()
    
    conn.close()

if __name__ == "__main__":
    explore_questions()