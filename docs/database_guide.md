# Global Dialogues SQLite Database Guide

## Overview

Each Global Dialogue has its own SQLite database file stored at `Data/GD<N>/GD<N>.db`. These databases provide a structured, queryable interface to all response data, analysis metrics, participant reliability scores, and tags.

**Important:** Column names in the database preserve their original format from the CSV files, which means many contain spaces (e.g., `"Question ID"`, `"Participant ID"`). Always use double quotes around column names with spaces in your SQL queries.

## Quick Start

### Create Database
```bash
# Create/recreate database for GD4
make db GD=4

# Or directly with Python
python tools/scripts/create_gd_database.py 4 --force
```

### Connect to Database
```bash
# Interactive SQLite CLI
make db-connect GD=4

# Or directly
sqlite3 Data/GD4/GD4.db
```

## Database Schema

### Core Tables

#### `responses`
Main table containing all participant responses with analysis metrics.

| Column | Type | Description |
|--------|------|-------------|
| response_id | INTEGER | Auto-incrementing primary key |
| "Question ID" | TEXT | Unique question identifier |
| "Participant ID" | TEXT | Unique participant identifier |
| "Question" | TEXT | Full text of the question |
| "Response" | TEXT | Participant's response text |
| "Star" | REAL | Number of votes received |
| "Language" | TEXT | Response language |
| divergence_score | REAL | Calculated divergence score (if available) |
| consensus_minagree_50pct | REAL | Consensus score at 50% threshold (if available) |
| ... | | All segment columns (e.g., "Africa", "Asia", "O1: English") |

**Note:** No unique constraint since participants can have multiple responses per question.

#### `participants`
Participant-level metrics including PRI scores.

| Column | Type | Description |
|--------|------|-------------|
| participant_id | TEXT | Primary key, matches "Participant ID" in responses |
| pri_score | REAL | Participant Reliability Index score |
| pri_scale_1_5 | REAL | PRI score scaled to 1-5 range |
| duration_seconds | REAL | Time spent on survey |
| lowqualitytag_perc | REAL | Percentage of low quality responses |
| universaldisagreement_perc | REAL | Percentage of universal disagreement |
| asc_score_raw | REAL | Answer similarity coefficient |

#### `tags`
Lookup table for all unique tags.

| Column | Type | Description |
|--------|------|-------------|
| tag_id | INTEGER | Auto-incrementing primary key |
| tag_name | TEXT | Unique tag name |

#### `response_tags`
Many-to-many relationship between responses and tags.

| Column | Type | Description |
|--------|------|-------------|
| response_id | INTEGER | Foreign key to responses table |
| tag_id | INTEGER | Foreign key to tags table |

#### `consensus_profiles`
Detailed consensus agreement profiles for each response.

| Column | Type | Description |
|--------|------|-------------|
| question_id | TEXT | Question identifier |
| response_text | TEXT | Response text |
| num_valid_segments | INTEGER | Number of valid segments |
| minagree_100pct | REAL | Min agreement among all segments |
| minagree_95pct | REAL | Min agreement among top 95% of segments |
| minagree_90pct | REAL | Min agreement among top 90% of segments |
| minagree_80pct | REAL | Min agreement among top 80% of segments |
| minagree_70pct | REAL | Min agreement among top 70% of segments |
| minagree_60pct | REAL | Min agreement among top 60% of segments |
| minagree_50pct | REAL | Min agreement among top 50% of segments |
| minagree_40pct | REAL | Min agreement among top 40% of segments |
| minagree_30pct | REAL | Min agreement among top 30% of segments |
| minagree_20pct | REAL | Min agreement among top 20% of segments |
| minagree_10pct | REAL | Min agreement among top 10% of segments |

### Views

#### `responses_with_pri`
Convenience view joining responses with PRI scores.
```sql
SELECT * FROM responses_with_pri WHERE pri_score < 0.5;
```

#### `responses_with_tags`
Responses with concatenated tag names.
```sql
SELECT Question_Text, Response_Text, tags 
FROM responses_with_tags 
WHERE tags LIKE '%climate%';
```

## Example Queries

### Basic Queries

```sql
-- Count total responses
SELECT COUNT(*) FROM responses;

-- Find all responses from a specific country
SELECT * FROM responses WHERE Country = 'United States';

-- Get questions with highest divergence
SELECT DISTINCT Question_ID, Question_Text, divergence_score
FROM responses
WHERE divergence_score IS NOT NULL
ORDER BY divergence_score DESC
LIMIT 10;
```

### Analysis Queries

```sql
-- Find low-reliability participants
SELECT p.participant_id, p.pri_score, COUNT(r.response_id) as response_count
FROM participants p
JOIN responses r ON p.participant_id = r.Participant_ID
WHERE p.pri_score < 0.3
GROUP BY p.participant_id
ORDER BY p.pri_score;

-- Responses with high divergence by segment
SELECT Segment, AVG(divergence_score) as avg_divergence
FROM responses
WHERE divergence_score IS NOT NULL
GROUP BY Segment
ORDER BY avg_divergence DESC;

-- Most voted responses per question
SELECT Question_ID, Question_Text, Response_Text, Vote_Count
FROM responses r1
WHERE Vote_Count = (
    SELECT MAX(Vote_Count) 
    FROM responses r2 
    WHERE r2.Question_ID = r1.Question_ID
);
```

### Tag Analysis

```sql
-- Most common tags
SELECT t.tag_name, COUNT(*) as usage_count
FROM tags t
JOIN response_tags rt ON t.tag_id = rt.tag_id
GROUP BY t.tag_name
ORDER BY usage_count DESC
LIMIT 20;

-- Responses with specific tag
SELECT r.Question_Text, r.Response_Text, r.Vote_Count
FROM responses r
JOIN response_tags rt ON r.response_id = rt.response_id
JOIN tags t ON rt.tag_id = t.tag_id
WHERE t.tag_name = 'environmental concern';

-- Tag co-occurrence
SELECT t1.tag_name as tag1, t2.tag_name as tag2, COUNT(*) as co_occurrence
FROM response_tags rt1
JOIN response_tags rt2 ON rt1.response_id = rt2.response_id
JOIN tags t1 ON rt1.tag_id = t1.tag_id
JOIN tags t2 ON rt2.tag_id = t2.tag_id
WHERE t1.tag_id < t2.tag_id
GROUP BY t1.tag_name, t2.tag_name
ORDER BY co_occurrence DESC
LIMIT 10;
```

### Cross-Segment Analysis

```sql
-- Compare average PRI scores by country
SELECT r.Country, AVG(p.pri_score) as avg_pri
FROM responses r
JOIN participants p ON r.Participant_ID = p.participant_id
GROUP BY r.Country
ORDER BY avg_pri DESC;

-- Consensus variance by segment
SELECT Segment, 
       AVG(consensus_score) as avg_consensus,
       STDEV(consensus_score) as consensus_variance
FROM responses
WHERE consensus_score IS NOT NULL
GROUP BY Segment;
```

## Python Usage

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Query into pandas DataFrame
query = """
SELECT Question_Text, Response_Text, Vote_Count, divergence_score
FROM responses
WHERE divergence_score > 0.7
ORDER BY Vote_Count DESC
"""
df = pd.read_sql_query(query, conn)

# Work with the data
print(df.head())
print(f"High divergence responses: {len(df)}")

# Close connection
conn.close()
```

## Tips

1. **Indexes**: The database includes indexes on commonly queried columns (Question_ID, Participant_ID, Segment, Country) for better performance.

2. **NULL handling**: Analysis scores (divergence_score, consensus_score) may be NULL if analysis hasn't been run or if the metric couldn't be calculated.

3. **Data freshness**: The database reflects the state of files at creation time. Rerun `make db GD=<N>` after running new analyses to update scores.

4. **Memory**: For large queries, consider using LIMIT and OFFSET for pagination.

5. **Backup**: The database can be recreated anytime from source CSVs, but consider backing up if you create custom tables or views.

## Troubleshooting

- **Database not found**: Run `make db GD=<N>` first
- **Missing scores**: Ensure analysis has been run (`make analyze GD=<N>`) before creating database
- **Missing tags**: Tags require preprocessed tag files in `Data/GD<N>/tags/`
- **Corrupted database**: Simply recreate with `make db GD=<N>`