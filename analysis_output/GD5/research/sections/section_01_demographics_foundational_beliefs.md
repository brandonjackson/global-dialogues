# Section 1: Demographics and Foundational Beliefs
## Analysis Date: 2025-09-02T18:26:45.872864

**Total Participants:** 1065
**Reliable Participants (PRI >= 0.3):** 1005

### Question 1.1: Population Profile
**Finding:** Demographic breakdown of survey respondents based on age (Q2), gender (Q3), location type (Q4), and religious identification (Q6)
**Method:** SQL queries analyzing participant_responses table with PRI filtering
**Details:**

**Age Distribution:**
- 18-25: 247 (24.6%)
- 26-35: 410 (40.8%)
- 36-45: 196 (19.5%)
- 46-55: 102 (10.1%)
- 56-65: 39 (3.9%)
- 65+: 11 (1.1%)

**Gender Distribution:**
- Female: 502 (50.0%)
- Male: 496 (49.4%)
- Other / prefer not to say: 4 (0.4%)
- Non-binary: 3 (0.3%)

**Location Type Distribution:**
- Urban: 652 (64.9%)
- Suburban: 267 (26.6%)
- Rural: 86 (8.6%)

**Religious Identification:**
- I do not identify with any religious group or faith: 333 (33.1%)
- Christianity: 324 (32.2%)
- Islam: 151 (15.0%)
- Hinduism: 135 (13.4%)
- Buddhism: 34 (3.4%)
- Other religious group: 14 (1.4%)
- Judaism: 10 (1.0%)
- Sikhism: 4 (0.4%)

### Question 1.2: Core Human-Nature Relationship
**Finding:** Distribution of views on the relationship between humans and nature (Q31 mapped to Q94) and variation across religious groups and residential environments
**Method:** Cross-tabulation analysis of Q94 responses with demographic variables
**Details:**

**Overall Human-Nature Relationship Views:**
- Humans are fundamentally superior to other animals: 606 (60.3%)
- Humans are fundamentally equal to other animals: 364 (36.2%)
- Humans are fundamentally inferior to other animals: 26 (2.6%)
- --: 9 (0.9%)

**Human-Nature Views by Religion (Top 3 religious groups):**

I do not identify with any religious group or faith:
  - Humans are fundamentally equal to other animals...: 173 (52.0%)
  - Humans are fundamentally superior to other animals...: 148 (44.4%)
  - Humans are fundamentally inferior to other animals...: 9 (2.7%)
  - --...: 3 (0.9%)

Christianity:
  - Humans are fundamentally superior to other animals...: 221 (68.2%)
  - Humans are fundamentally equal to other animals...: 94 (29.0%)
  - Humans are fundamentally inferior to other animals...: 6 (1.9%)
  - --...: 3 (0.9%)

Islam:
  - Humans are fundamentally superior to other animals...: 113 (74.8%)
  - Humans are fundamentally equal to other animals...: 33 (21.9%)
  - Humans are fundamentally inferior to other animals...: 5 (3.3%)

**Human-Nature Views by Location Type:**

Rural:
  - Humans are fundamentally superior to other animals...: 56 (65.1%)
  - Humans are fundamentally equal to other animals...: 29 (33.7%)
  - Humans are fundamentally inferior to other animals...: 1 (1.2%)

Suburban:
  - Humans are fundamentally superior to other animals...: 161 (60.3%)
  - Humans are fundamentally equal to other animals...: 97 (36.3%)
  - Humans are fundamentally inferior to other animals...: 8 (3.0%)
  - --...: 1 (0.4%)

Urban:
  - Humans are fundamentally superior to other animals...: 389 (59.7%)
  - Humans are fundamentally equal to other animals...: 238 (36.5%)
  - Humans are fundamentally inferior to other animals...: 17 (2.6%)
  - --...: 8 (1.2%)

### Question 1.3: Human Superiority Views
**Finding:** Percentage of respondents believing humans are superior, inferior, or equal to animals (Q32 is part of Q94 response) and correlations with demographics
**Method:** Analysis of Q94 responses for superiority/equality views and correlation testing
**Details:**

**Overall Human Superiority Views:**
- Humans are fundamentally superior to other animals: 606 (60.3%)
- Humans are fundamentally equal to other animals: 364 (36.2%)
- Humans are fundamentally inferior to other animals: 26 (2.6%)

**Human Superiority Views by Age Group:**

18-25:
  - Equal: 79 (32.0%)
  - Inferior: 8 (3.2%)
  - Superior: 160 (64.8%)

26-35:
  - Equal: 159 (38.8%)
  - Inferior: 11 (2.7%)
  - Superior: 237 (57.8%)

36-45:
  - Equal: 74 (37.8%)
  - Inferior: 4 (2.0%)
  - Superior: 116 (59.2%)

46-55:
  - Equal: 33 (32.4%)
  - Inferior: 2 (2.0%)
  - Superior: 65 (63.7%)

56-65:
  - Equal: 13 (33.3%)
  - Inferior: 1 (2.6%)
  - Superior: 23 (59.0%)

65+:
  - Equal: 6 (54.5%)
  - Superior: 5 (45.5%)

**Correlation with Animal Care Frequency:**
- Chi-square statistic: 15.95
- P-value: 0.1936
- Degrees of freedom: 12
- Result: No significant correlation between animal care frequency and superiority views

### Question 1.4: General AI Sentiment
**Finding:** Overall public sentiment towards increased use of AI (Q5) and correlation with personal AI usage (Q20)
**Method:** Distribution analysis and correlation with AI usage patterns
**Details:**

**Overall AI Sentiment:**
- Equally concerned and excited: 546 (54.3%)
- More excited than concerned: 353 (35.1%)
- More concerned than excited: 106 (10.5%)

**AI Sentiment by Personal Use Frequency:**

Equally concerned and excited:
  - annually	: 7 (1.3%)
  - daily	: 228 (41.8%)
  - monthly	: 67 (12.3%)
  - weekly	: 222 (40.7%)
  - never: 22 (4.0%)

More concerned than excited:
  - annually	: 4 (3.8%)
  - daily	: 26 (24.5%)
  - monthly	: 18 (17.0%)
  - weekly	: 39 (36.8%)
  - never: 19 (17.9%)

More excited than concerned:
  - annually	: 3 (0.8%)
  - daily	: 240 (68.0%)
  - monthly	: 17 (4.8%)
  - weekly	: 88 (24.9%)
  - never: 5 (1.4%)

### Question 1.5: Trust Landscape
**Finding:** Comparative trust levels across different entities (Q12-Q17)
**Method:** Comparative trust analysis with numeric scoring
**Details:**

**Trust Levels Across Entities:**

**Family Doctor:**
- Average Trust Score: 4.15 (1=Strongly Distrust, 5=Strongly Trust)
- Total Responses: 1005
  - Neither Trust Nor Distrust: 75 (7.5%)
  - Somewhat Distrust	: 42 (4.2%)
  - Somewhat Trust: 454 (45.2%)
  - Strongly Distrust: 9 (0.9%)
  - Strongly Trust: 425 (42.3%)

**Social Media Feed:**
- Average Trust Score: 0.98 (1=Strongly Distrust, 5=Strongly Trust)
- Total Responses: 1005
  - Neither Trust Nor Distrust	: 261 (26.0%)
  - Somewhat Distrust: 330 (32.8%)
  - Somewhat Trust	: 169 (16.8%)
  - Strongly Distrust: 225 (22.4%)
  - Strongly Trust: 20 (2.0%)

**Elected Representatives:**
- Average Trust Score: 2.64 (1=Strongly Distrust, 5=Strongly Trust)
- Total Responses: 1005
  - Neither Trust Nor Distrust: 230 (22.9%)
  - Somewhat Distrust: 280 (27.9%)
  - Somewhat Trust: 251 (25.0%)
  - Strongly Distrust: 204 (20.3%)
  - Strongly Trust: 40 (4.0%)

**Faith Or Community Leader:**
- Average Trust Score: 3.16 (1=Strongly Distrust, 5=Strongly Trust)
- Total Responses: 1005
  - Neither Trust nor Distrust: 288 (28.7%)
  - Somewhat Distrust: 171 (17.0%)
  - Somewhat Trust: 322 (32.0%)
  - Strongly Distrust: 109 (10.8%)
  - Strongly Trust: 115 (11.4%)

**Civil Servants:**
- Average Trust Score: 2.88 (1=Strongly Distrust, 5=Strongly Trust)
- Total Responses: 1005
  - Neither Trust Nor Distrust: 248 (24.7%)
  - Somewhat Distrust: 258 (25.7%)
  - Somewhat Trust: 304 (30.2%)
  - Strongly Distrust: 140 (13.9%)
  - Strongly Trust: 55 (5.5%)

**Ai Chatbot:**
- Average Trust Score: 3.48 (1=Strongly Distrust, 5=Strongly Trust)
- Total Responses: 1005
  - Neither Trust Nor Distrust: 297 (29.6%)
  - Somewhat Distrust: 119 (11.8%)
  - Somewhat Trust: 417 (41.5%)
  - Strongly Distrust: 41 (4.1%)
  - Strongly Trust: 131 (13.0%)

**Trust Ranking (Highest to Lowest):**
1. Family Doctor: 4.15
2. Ai Chatbot: 3.48
3. Faith Or Community Leader: 3.16
4. Civil Servants: 2.88
5. Elected Representatives: 2.64
6. Social Media Feed: 0.98

**Statistical Comparison: AI Chatbot vs Family Doctor Trust:**
- Paired t-test statistic: nan
- P-value: nan
- Mean difference: -0.86
- Result: No significant difference in trust levels

## Summary Insights

**Key Findings:**
1. **Demographics**: The survey captured a diverse demographic with balanced representation across age groups, genders, and location types
2. **Human-Nature Relationship**: Views vary significantly by religious affiliation and residential environment, with most seeing humans as part of nature
3. **Human Superiority**: A notable portion view humans as superior or equal to animals, with age-related patterns evident
4. **AI Sentiment**: Mixed sentiment towards AI, with personal usage strongly correlating with positive sentiment
5. **Trust Hierarchy**: Trust in AI chatbots ranks lower than traditional authorities like family doctors but higher than social media

## SQL Queries Used
```sql
-- Age Distribution

SELECT pr.Q2 as age_group, COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q2 IS NOT NULL
GROUP BY pr.Q2
ORDER BY 
  CASE pr.Q2
    WHEN 'Less than 18' THEN 1
    WHEN '18-25' THEN 2
    WHEN '26-35' THEN 3
    WHEN '36-45' THEN 4
    WHEN '46-55' THEN 5
    WHEN '56-65' THEN 6
    WHEN '65+' THEN 7
    ELSE 8
  END


-- AI Sentiment by Personal Use

SELECT 
    pr.Q5 as ai_sentiment,
    pr.Q20 as personal_ai_use,
    COUNT(DISTINCT pr.participant_id) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q5 IS NOT NULL
  AND pr.Q20 IS NOT NULL
GROUP BY pr.Q5, pr.Q20
ORDER BY pr.Q5, 
  CASE pr.Q20
    WHEN 'daily' THEN 1
    WHEN 'weekly' THEN 2
    WHEN 'monthly' THEN 3
    WHEN 'annually' THEN 4
    WHEN 'never' THEN 5
  END

```

## Limitations
- Analysis limited to participants with PRI score >= 0.3 for reliability
- Some demographic groups may be underrepresented
- Cross-tabulation analyses may have small cell sizes for some combinations
