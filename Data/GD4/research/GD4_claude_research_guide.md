# GD4 Research Guide for Claude

## Overview

Global Dialogues is a recurring international survey series that collects public perspectives on artificial intelligence across multiple countries. Each Global Dialogue involves online surveys where participants answer multiple-choice poll questions and provide open-ended text responses. On certain open-ended questions ("ask opinion" types) they are able to vote in agreement or disagreement with a random selection of other participants' responses. This data is then used to inform a model that estimates the level of agreement from each 'Segment' (demographic) in the dialogue on every Response to that question. That is where the agreement data comes from for the agreement rates on responses in the GD data. Agreement rates by Segment on Poll question Responses, however, simply show the % of that Segment that selected that poll option.

Global Dialogues 4 (GD4) focuses on **human-AI relationships**, exploring how people form relationships with AI systems, their feelings about these relationships, concerns about societal impacts, and governance preferences.

## Research Task

Your task is to answer the investigation questions located in `analysis_output/GD4/research/GD4_investigation_questions.md` one at a time, following the guidelines in this guide, and document your answers rigorously and thoroughly according to the guidance in this document in `analysis_output/GD4/research/GD4_investigation_answers.md`, using the connection to the Sqlite db to run queries on the GD4 data (refer to the `docs/database_guide.md`) and any Python scripts needed to complete the analysis. After documenting your answer, commit your work to git with a succinct message clearly indicating the investigation question number answered.

## Essential Resources

### Database Access
```bash
# Connect to database
make db-connect GD=4

# Or directly
sqlite3 Data/GD4/GD4.db
```

### Key Files
- **Investigation Questions**: `analysis_output/GD4/research/GD4_investigation_questions.md`
- **Survey Structure**: `Data/GD4/GD4_survey_human_readable.md`
- **Database Guide**: `docs/database_guide.md`

## Database Schema

### Core Tables
- **`responses`**: All participant responses (11,554 total responses across 12 unique questions)
- **`participants`**: Participant-level metrics including PRI scores
- **`tags`**: Response categorization
- **`consensus_profiles`**: Agreement patterns across segments

### Key Columns in `responses`
- `question_id`: UUID format (e.g., "05f81a31-a904-4ed2-8fa1-68fb561de3b9")
- `question`: Full question text
- `response`: Participant's response
- `participant_id`: Unique participant identifier
- `star`: Number of votes received
- `language`: Response language
- Geographic segments: `africa`, `asia`, `europe`, `north_america`, etc.
- Demographic segments: `o1_english`, `o2_18_25`, `o3_male`, etc.

## Analysis Standards

### 1. Database Connection
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('Data/GD4/GD4.db')
```

### 2. Question Mapping
**Critical**: The database uses UUID question IDs, not the numbered IDs from the human-readable survey. Always query the actual question text to identify questions:

```sql
-- Create question mapping for reference
SELECT DISTINCT question_id, question 
FROM responses 
ORDER BY question_id;
```

### 3. PRI Filtering
Filter for reliable participants:
```sql
SELECT r.*, p.pri_score
FROM responses r
JOIN participants p ON r.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
```

### 4. Segment Analysis
Cast segment columns to REAL for numeric operations:
```sql
SELECT AVG(CAST(africa AS REAL)) as africa_avg,
       AVG(CAST(asia AS REAL)) as asia_avg
FROM responses
WHERE question_id = 'your_question_id'
```

### 5. Composite Score Creation
For loneliness score (Q51-58 in human-readable):
```sql
-- Reverse score positive items (Q51, Q55, Q56, Q58)
-- Higher score = more loneliness
SELECT participant_id,
       (CASE WHEN q51_response = 'Never' THEN 4 
             WHEN q51_response = 'Rarely' THEN 3
             WHEN q51_response = 'Sometimes' THEN 2
             WHEN q51_response = 'Often' THEN 1 END) +
       -- Continue for all 8 questions...
       AS loneliness_score
FROM responses
WHERE question_id = 'actual_uuid_here'
```

### 6. User Archetype Identification
```sql
-- AI-Reliant: Multiple intimate AI activities
SELECT participant_id, COUNT(DISTINCT question_id) as ai_activities
FROM responses
WHERE question_id IN ('uuid1', 'uuid2', 'uuid3')  -- Usage questions
  AND response = 'Yes'
GROUP BY participant_id
HAVING ai_activities >= 4;
```

## Investigation Approach

1. **Start with question mapping**: Query all questions to understand the actual question IDs
2. **Filter by PRI**: Use reliable participants (pri_score >= 0.3)
3. **Create composite scores**: Build loneliness, AI sentiment, and usage pattern scores
4. **Identify archetypes**: Segment users by behavior patterns
5. **Cross-demographic analysis**: Compare patterns across age, gender, country
6. **Detect contradictions**: Find internal inconsistencies in beliefs vs. behavior

## Output Requirements

For each investigation question, provide and document as needed to answer the question:
- Statistical findings with significance tests
- Demographic breakdowns
- Visualizations where appropriate
- SQL queries and any scripts used
- Narrative insights about human-AI relationships

## Documentation Format

### Investigation Answer Structure
Each answer in `GD4_investigation_answers.md` should follow this format:

```markdown
## [Question Number] [Question Title]

**Question:** [Exact question text from investigation_questions.md]

**Analysis Approach:** [Brief description of methodology and data needed]

**Key Findings:**
- [Finding 1 with statistics]
- [Finding 2 with statistics]
- [Finding 3, etc. with statistics]

**Demographic Breakdowns:**
- [Age groups, gender, countries, etc. as relevant to the question]

**Statistical Significance:** [Chi-square, t-test, correlation results as applicable]

**SQL Queries Used:**
```sql
-- Query 1: [Description]
SELECT ...

-- Query 2: [Description]  
SELECT ...
```

**Scripts Used:** [Python code, if applicable for analysis beyond SQL queries]
```python
# any relevant code used for scripting analysis functions or generating visualizations
```

**Visualizations:** [Description of any charts/graphs created as applicable, or name of generated visualization files. Only if visualization is clearly helpful and clarifying to the findings.]

**Insights:** [Narrative interpretation of what this reveals about human-AI relationships]

**Limitations:** [Any data quality issues, sample size concerns, etc.]
```

### Documentation Standards
- Use the exact question numbering hierarchy from `investigation_questions.md`
- Include all SQL queries that produced key results
- Provide specific statistics (percentages, counts, p-values)
- Note any data filtering applied (PRI scores, missing data, etc.)
- Document any assumptions made during analysis
- Include sample sizes for all reported statistics

## Important Notes

- Question IDs are UUIDs, not numbers
- Always verify question content before analysis
- Use PRI filtering for reliability
- Cast segment columns to REAL for calculations
- Document all SQL queries and methodology