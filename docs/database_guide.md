# Global Dialogues SQLite Database Guide

## Overview

Each Global Dialogue has its own SQLite database file stored at `Data/GD<N>/GD<N>.db`. These databases provide a structured, queryable interface to all response data, analysis metrics, participant reliability scores, and tags.

**Important:** All column names are automatically normalized to `lowercase_underscored` format for consistency. This means:
- `Question ID` becomes `question_id`
- `Participant ID` becomes `participant_id`
- Special characters and spaces are replaced with underscores

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
Main table containing ALL data from the aggregate_standardized.csv file, including both poll questions and open-ended responses.

| Column | Type | Description |
|--------|------|-------------|
| response_id | INTEGER | Auto-incrementing primary key |
| question_id | TEXT | Unique question identifier |
| question_type | TEXT | Type of question (Poll Single Select, Poll Multi Select, Ask Opinion, Ask Experience) |
| participant_id | TEXT | Unique participant identifier (may be NULL for aggregate rows) |
| question | TEXT | Full text of the question |
| response | TEXT | Participant's response text or poll option selected |
| sentiment | TEXT | Sentiment classification from tags (Positive, Negative, Neutral) if available |
| language | TEXT | Response language |
| divergence_score | REAL | Calculated divergence score (if available) |
| consensus_minagree_50pct | REAL | Consensus score at 50% threshold (if available) |
| **Agreement Rate Columns** | **REAL** | **All remaining columns represent agreement rates (0.0-1.0) from different demographic segments** |
| all | REAL | Agreement rate from all participants |
| africa, asia, europe, etc. | REAL | Agreement rates by geographic region |
| o1_english, o1_spanish, etc. | REAL | Agreement rates by language preference |
| o2_18_25, o2_26_35, etc. | REAL | Agreement rates by age group |
| o3_male, o3_female, etc. | REAL | Agreement rates by gender |
| o4_rural, o4_urban, etc. | REAL | Agreement rates by location type |
| ... | REAL | Additional demographic segment agreement rates |

**Note:** No unique constraint since participants can have multiple responses per question.

#### `participants`
Participant-level metrics including PRI scores.

| Column | Type | Description |
|--------|------|-------------|
| participant_id | TEXT | Primary key, matches participant_id in responses |
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
SELECT question, response, tags 
FROM responses_with_tags 
WHERE tags LIKE '%climate%';
```

## Example Queries

### Basic Queries

```sql
-- Count total responses
SELECT COUNT(*) FROM responses;

-- Find all poll questions
SELECT DISTINCT question, question_type 
FROM responses 
WHERE question_type LIKE 'Poll%';

-- Get questions with highest divergence
SELECT DISTINCT question_id, question, divergence_score
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
JOIN responses r ON p.participant_id = r.participant_id
WHERE p.pri_score < 0.3
GROUP BY p.participant_id
ORDER BY p.pri_score;

-- Responses with high divergence by language
SELECT language, AVG(divergence_score) as avg_divergence
FROM responses
WHERE divergence_score IS NOT NULL
GROUP BY language
ORDER BY avg_divergence DESC;

-- Find responses with high agreement across all segments
SELECT question, response, "all" as overall_agreement
FROM responses
WHERE "all" > 0.8
AND question_type IN ('Ask Opinion', 'Ask Experience')
ORDER BY "all" DESC;
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
SELECT r.question, r.response, r.star
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
-- Compare average PRI scores by language
SELECT r.language, AVG(p.pri_score) as avg_pri, 
       COUNT(DISTINCT r.participant_id) as participant_count
FROM responses r
JOIN participants p ON r.participant_id = p.participant_id
GROUP BY r.language
ORDER BY avg_pri DESC;

-- Consensus profiles table query
SELECT question_id, response_text, 
       minagree_50pct as median_consensus,
       minagree_90pct as high_consensus
FROM consensus_profiles
WHERE minagree_50pct > 0.7
ORDER BY minagree_50pct DESC
LIMIT 10;

-- Segment-specific analysis (using normalized column names)
SELECT AVG(CAST(africa AS REAL)) as africa_avg,
       AVG(CAST(asia AS REAL)) as asia_avg,
       AVG(CAST(europe AS REAL)) as europe_avg
FROM responses
WHERE question_id = 'some_question_id';
```

## Python Usage

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('Data/GD4/GD4.db')

# Query into pandas DataFrame
query = """
SELECT question, response, star, divergence_score
FROM responses
WHERE divergence_score > 0.7
ORDER BY star DESC
"""
df = pd.read_sql_query(query, conn)

# Work with the data
print(df.head())
print(f"High divergence responses: {len(df)}")

# Access segment columns programmatically
segment_query = """
SELECT * FROM responses 
WHERE CAST(africa AS REAL) > 0.5
"""
df_segment = pd.read_sql_query(segment_query, conn)

# Close connection
conn.close()
```

## Column Name Normalization

The database creation script automatically normalizes all column names:

| Original CSV Column | Normalized Database Column | Data Type | Description |
|---------------------|---------------------------|-----------|-------------|
| Question ID | question_id | TEXT | Question identifier |
| Participant ID | participant_id | TEXT | Participant identifier |
| Question | question | TEXT | Question text |
| Response | response | TEXT | Response text |
| Sentiment | sentiment | TEXT | Sentiment from tags file |
| All | all | REAL | Agreement rate (0.0-1.0) |
| O1: English | o1_english | REAL | Agreement rate for English speakers |
| O2: 18-25 | o2_18_25 | REAL | Agreement rate for age 18-25 |
| Africa | africa | REAL | Agreement rate for Africa region |

## Tips

1. **Indexes**: The database includes indexes on commonly queried columns (question_id, participant_id, language) for better performance.

2. **NULL handling**: Analysis scores (divergence_score, consensus_minagree_50pct) may be NULL if analysis hasn't been run or if the metric couldn't be calculated.

3. **Data freshness**: The database reflects the state of files at creation time. Rerun `make db GD=<N>` after running new analyses to update scores.

4. **Memory**: For large queries, consider using LIMIT and OFFSET for pagination.

5. **Backup**: The database can be recreated anytime from source CSVs, but consider backing up if you create custom tables or views.

6. **Agreement rate columns**: All columns after `participant_id` (except divergence_score and consensus_minagree_50pct) represent agreement rates from different demographic segments. These are stored as REAL type with values from 0.0 to 1.0 representing the percentage of that segment that agreed with the response.

## Troubleshooting

- **Database not found**: Run `make db GD=<N>` first
- **Missing scores**: Ensure analysis has been run (`make analyze GD=<N>`) before creating database
- **Missing tags**: Tags require preprocessed tag files in `Data/GD<N>/tags/`
- **Column not found**: Remember all columns are lowercase_underscored (e.g., use `question_id` not `Question ID`)
- **Corrupted database**: Simply recreate with `make db GD=<N>`