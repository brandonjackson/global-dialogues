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
Main table containing ALL data from the aggregate_standardized.csv file. **IMPORTANT**: Each row represents different things depending on the question type:

##### What Each Row Represents

**Poll Questions (Poll Single Select, Poll Multi Select)**
- Each row represents one poll option
- The `response` column contains the option text (e.g., "Yes", "No", "Strongly Agree")
- Agreement rate columns show the exact percentage of participants in each segment who selected that option
- Example: If `africa` = 0.65 for a "Yes" option, then 65% of African participants selected "Yes"

**Ask Opinion Questions**
- Each row represents ONE individual participant's text response
- The `response` column contains their written answer
- Agreement rate columns show the estimated agreement rate from other participants in that segment who voted on this response
- These estimates come from participants voting "agree/disagree" on a random selection of others' responses
- Example: If `o1_english` = 0.72, then approximately 72% of English-speaking participants who saw this response agreed with it

**Ask Experience Questions**
- Each row represents ONE individual participant's text response about their experience
- Participants did NOT vote on each other's responses for these questions
- If the survey creator specified categories, agreement rates show the percentage of participants in each segment who categorized their own response in the same category
- If no categories were specified, agreement rate columns will be NULL

| Column | Type | Description |
|--------|------|-------------|
| response_id | INTEGER | Auto-incrementing primary key |
| question_id | TEXT | Unique question identifier |
| question_type | TEXT | Type of question (Poll Single Select, Poll Multi Select, Ask Opinion, Ask Experience) |
| participant_id | TEXT | Unique participant identifier (NULL for poll option rows, populated for individual responses) |
| question | TEXT | Full text of the question (may include "Branch A/B/C -" prefix for branched questions) |
| response | TEXT | Poll option text OR individual participant's response text |
| sentiment | TEXT | Sentiment classification from tags (Positive, Negative, Neutral) if available |
| language | TEXT | Response language |
| divergence_score | REAL | Calculated divergence score (if available) |
| consensus_minagree_50pct | REAL | **Median consensus**: Minimum agreement rate among the top 50% of demographic segments (see explanation below) |
| consensus_minagree_95pct | REAL | **Near-universal consensus**: Minimum agreement rate among the top 95% of demographic segments |
| consensus_minagree_100pct | REAL | **Universal consensus**: Minimum agreement rate across ALL demographic segments (strictest threshold) |
| **Agreement Rate Columns** | **REAL** | **All remaining columns represent agreement rates (0.0-1.0) from different demographic segments** |
| all | REAL | Agreement rate from all participants |
| africa, asia, europe, etc. | REAL | Agreement rates by geographic region |
| o1_english, o1_spanish, etc. | REAL | Agreement rates by language preference |
| o2_18_25, o2_26_35, etc. | REAL | Agreement rates by age group |
| o3_male, o3_female, etc. | REAL | Agreement rates by gender |
| o4_rural, o4_urban, etc. | REAL | Agreement rates by location type |
| branch_a, branch_b, branch_c | REAL | Agreement rates within poll-based branches (see Branching section below) |
| branches_* | TEXT | Branch metadata columns (see Branching section below) |
| ... | REAL | Additional demographic segment agreement rates |

**Note:** No unique constraint since participants can have multiple responses per question.

##### Understanding Consensus Metrics

The consensus metrics measure how broadly a response is agreed upon across different demographic segments. Each metric represents the minimum agreement rate among a percentage of segments, sorted from highest to lowest agreement:

- **`consensus_minagree_100pct` (Universal Consensus)**: The minimum agreement rate across ALL demographic segments. This is the strictest measure - if this value is 0.7, it means EVERY demographic group (every region, age group, language, etc.) had at least 70% agreement with this response.

- **`consensus_minagree_95pct` (Near-Universal Consensus)**: The minimum agreement rate among the top 95% of demographic segments. This excludes the bottom 5% of segments (outliers), providing a more robust measure of broad agreement while still being quite strict.

- **`consensus_minagree_50pct` (Median Consensus)**: The minimum agreement rate among the top 50% of demographic segments. This is the median measure, showing the agreement level that at least half of all segments reached or exceeded.

**Example**: Consider a response with these agreement rates across 10 segments:
- Sorted rates: [0.95, 0.92, 0.88, 0.85, 0.82, 0.75, 0.45, 0.32, 0.28, 0.15]
- `consensus_minagree_100pct` = 0.15 (the lowest agreement from any segment)
- `consensus_minagree_95pct` = 0.28 (excluding the bottom 1 segment: minimum of top 9)
- `consensus_minagree_50pct` = 0.75 (the lowest agreement among the top 5 segments)

**Interpretation Guide**:
- High `100pct` values (>0.6) = Truly universal agreement across ALL groups
- High `95pct` values (>0.7) = Near-universal agreement, robust to outliers
- High `50pct` values (>0.8) = Strong median consensus, at least half of groups strongly agree

These metrics help identify responses with broad cross-demographic appeal and are particularly useful for finding viewpoints that resonate across diverse populations.

##### Understanding Branching in Survey Flow

The survey supports "branching" where a poll question can lead to different follow-up questions based on the answer selected. This creates focused discussion groups where only participants who gave similar answers vote on each other's explanations.

**How Branching Works:**
1. A poll question (e.g., "Have you used AI?") can have up to 3 branches
2. Each branch leads to ONE "Ask Opinion" question immediately after the poll
3. Only participants who selected the option(s) for that branch see and vote on responses within that branch
4. After the branched question, all participants rejoin the main survey flow

**How Branches are Represented in the Database:**

1. **Branch Identification**: Branched questions have their question text prefixed with "Branch A -", "Branch B -", or "Branch C -"

2. **Branch Agreement Columns**: 
   - `branch_a`, `branch_b`, `branch_c` columns contain agreement rates ONLY from participants within that specific branch
   - These columns are reused across ALL branched questions in the survey

3. **Branch Mapping Table (`branch_mappings`)**:
   - Provides a clean, queryable way to connect branched responses to their source poll questions
   - Contains the source poll question text and the specific option(s) that led to each branch
   - Eliminates the need to parse dynamic column names with embedded question text

4. **Convenient View (`branched_responses`)**:
   - Joins responses with branch_mappings for easy analysis
   - Includes the appropriate branch agreement rate (branch_a/b/c) based on the branch_id

**Example:**
- Poll: "Have you used AI companions?" with options Yes/No
- Branch A follows "Yes" → "Branch A - What benefits did you experience?"
- Branch B follows "No" → "Branch B - What concerns prevented you from trying?"
- For responses to Branch A question:
  - `branch_a` shows agreement from other "Yes" voters only
  - `branches_have_you_used_ai_companions` = "Branch A - Yes"
  - All other segment columns (africa, o1_english, etc.) are NULL or show general population data

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

#### `branch_mappings`
Maps branched "Ask Opinion" questions back to their source poll questions.

| Column | Type | Description |
|--------|------|-------------|
| response_id | INTEGER | Primary key, foreign key to responses table |
| source_poll_question_id | TEXT | Question ID of the poll that created the branch |
| source_poll_question | TEXT | Full text of the source poll question |
| branch_id | TEXT | Branch identifier ('A', 'B', or 'C') |
| branch_condition | TEXT | The poll option(s) that led to this branch (e.g., "Yes", "No") |

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

#### `branched_responses`
Convenient view for analyzing branched questions with full context.
```sql
SELECT question, response, source_poll_question, branch_condition, branch_agreement
FROM branched_responses
WHERE branch_id = 'A' AND branch_agreement > 0.7;
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

### Working with Branched Questions

```sql
-- Find all branched questions
SELECT DISTINCT question, question_type
FROM responses
WHERE question LIKE 'Branch %'
ORDER BY question;

-- Get responses from a specific branch with high agreement
SELECT question, response, branch_a
FROM responses
WHERE question LIKE 'Branch A -%'
  AND branch_a > 0.7
ORDER BY branch_a DESC;

-- Identify which poll options led to each branch (using new branch_mappings table)
SELECT DISTINCT 
    bm.source_poll_question,
    bm.branch_id,
    bm.branch_condition,
    COUNT(*) as response_count
FROM branch_mappings bm
GROUP BY bm.source_poll_question, bm.branch_id, bm.branch_condition
ORDER BY bm.source_poll_question, bm.branch_id;

-- Compare agreement rates between branches for the same base question
SELECT 
    CASE 
        WHEN question LIKE 'Branch A -%' THEN 'Branch A'
        WHEN question LIKE 'Branch B -%' THEN 'Branch B'
        WHEN question LIKE 'Branch C -%' THEN 'Branch C'
    END as branch,
    AVG(CASE 
        WHEN question LIKE 'Branch A -%' THEN branch_a
        WHEN question LIKE 'Branch B -%' THEN branch_b
        WHEN question LIKE 'Branch C -%' THEN branch_c
    END) as avg_agreement_within_branch,
    COUNT(*) as response_count
FROM responses
WHERE question LIKE 'Branch %'
GROUP BY branch;

-- Find high-consensus responses within each branch
SELECT 
    substr(question, 1, 10) as branch,
    response,
    branch_a, branch_b, branch_c
FROM responses
WHERE question LIKE 'Branch %'
  AND (branch_a > 0.8 OR branch_b > 0.8 OR branch_c > 0.8)
ORDER BY COALESCE(branch_a, branch_b, branch_c) DESC
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

2. **NULL handling**: Analysis scores (divergence_score, consensus_minagree_50pct, consensus_minagree_95pct, consensus_minagree_100pct) may be NULL if analysis hasn't been run or if the metric couldn't be calculated.

3. **Data freshness**: The database reflects the state of files at creation time. Rerun `make db GD=<N>` after running new analyses to update scores.

4. **Memory**: For large queries, consider using LIMIT and OFFSET for pagination.

5. **Backup**: The database can be recreated anytime from source CSVs, but consider backing up if you create custom tables or views.

6. **Agreement rate columns**: All segment columns (africa, asia, o1_english, branch_a, etc.) represent different types of agreement:
   - For **poll options**: Exact percentage who selected that option (0.0-1.0)
   - For **Ask Opinion**: Estimated agreement rate from voting (0.0-1.0)
   - For **Ask Experience**: Percentage who used same category, if applicable
   - For **branches**: Agreement only from participants within that branch

## Troubleshooting

- **Database not found**: Run `make db GD=<N>` first
- **Missing scores**: Ensure analysis has been run (`make analyze GD=<N>`) before creating database
- **Missing tags**: Tags require preprocessed tag files in `Data/GD<N>/tags/`
- **Column not found**: Remember all columns are lowercase_underscored (e.g., use `question_id` not `Question ID`)
- **Corrupted database**: Simply recreate with `make db GD=<N>`