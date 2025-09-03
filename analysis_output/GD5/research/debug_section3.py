import sqlite3
import pandas as pd

# Connect to database with read-only mode
conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Check if participants table exists and has data
query_check = """
SELECT COUNT(*) as participant_count,
       MIN(pri_score) as min_pri,
       MAX(pri_score) as max_pri,
       AVG(pri_score) as avg_pri
FROM participants
"""
df_check = pd.read_sql_query(query_check, conn)
print(f"Total participants: {df_check.iloc[0]['participant_count']}")
print(f"PRI score range: {df_check.iloc[0]['min_pri']} to {df_check.iloc[0]['max_pri']}")
print(f"Average PRI: {df_check.iloc[0]['avg_pri']}")

query_check2 = """
SELECT COUNT(*) as participant_count 
FROM participants
WHERE pri_score >= 0.3
"""
df_check2 = pd.read_sql_query(query_check2, conn)
print(f"Reliable participants (PRI >= 0.3): {df_check2.iloc[0]['participant_count']}")

# Check response table structure
query_struct = """
SELECT * FROM responses
WHERE question LIKE '%believe that other animals%'
LIMIT 5
"""
df_struct = pd.read_sql_query(query_struct, conn)
print("\nSample responses structure:")
print(df_struct.columns.tolist())
if not df_struct.empty:
    print("\nFirst response:")
    print(df_struct.iloc[0].to_dict())

# Check for Q39, Q40, Q41 responses
queries = {
    'Q39_language': "Do you believe that other animals have their own forms of language?",
    'Q40_emotion': "Do you believe that other animals have their own forms of emotion?",
    'Q41_culture': "Do you believe that other animals have their own forms of culture?"
}

for label, question in queries.items():
    query = f"""
    SELECT 
        COUNT(*) as total_responses,
        COUNT(DISTINCT participant_id) as unique_participants
    FROM responses
    WHERE question = '{question}'
    """
    df = pd.read_sql_query(query, conn)
    print(f"\n{label}:")
    print(f"  Total responses: {df.iloc[0]['total_responses']}")
    print(f"  Unique participants: {df.iloc[0]['unique_participants']}")
    
    # Get response distribution
    query_dist = f"""
    SELECT response, COUNT(*) as count
    FROM responses
    WHERE question = '{question}'
    GROUP BY response
    ORDER BY count DESC
    """
    df_dist = pd.read_sql_query(query_dist, conn)
    if not df_dist.empty:
        print("  Response distribution:")
        for _, row in df_dist.iterrows():
            print(f"    {row['response']}: {row['count']}")

# Check for Q44 and Q45
query_44 = """
SELECT COUNT(*) as count
FROM responses
WHERE question LIKE '%To what extent does knowing this impact%'
"""
df_44 = pd.read_sql_query(query_44, conn)
print(f"\nQ44 (Impact) responses: {df_44.iloc[0]['count']}")

query_45 = """
SELECT COUNT(*) as count
FROM responses
WHERE question LIKE '%How does this knowledge make you feel%'
"""
df_45 = pd.read_sql_query(query_45, conn)
print(f"Q45 (Feeling) responses: {df_45.iloc[0]['count']}")

conn.close()