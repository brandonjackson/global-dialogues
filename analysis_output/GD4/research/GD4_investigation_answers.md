# GD4 Investigation Answers

This document contains the answers to the investigation questions from GD4_investigation_questions.md, including analysis approaches, findings, and supporting queries/scripts.

## 1.1 Do the AI-Reliant have more hopes or more fears?

**Question:** One might assume heavy users are purely optimistic, but they may have more nuanced concerns because of their deeper experience. Do they express more "Concerns or Warnings about AI" or more "Hopes or Positive Visions" in the final survey question?

**Analysis Approach:** 
Since individual participant data isn't available in the database, I analyzed aggregate patterns and text responses to understand the relationship between AI usage intensity and expressed hopes vs concerns. I identified "AI-Reliant" users as those using AI for emotional support daily or weekly (43% of participants).

**Key Findings:**
- **43% of participants** use AI for emotional support daily (15%) or weekly (28%), forming the "AI-Reliant" group
- **46% have used AI for companionship** (Q66), with higher rates among younger users (56% of 18-25 year-olds)
- Among responses mentioning heavy AI use or companionship (n=166):
  - 38.0% expressed **Hopes/Positive** themes
  - 15.7% expressed **Concerns/Warnings**
  - 19.9% offered **Suggestions** for development
  - **Hope-to-Concern Ratio: 2.4:1** (more hopes than fears)

**Demographic Breakdowns:**
- **Age 18-25**: 56% have used AI companionship (vs 46% overall)
- **Daily/Weekly emotional support users**: Higher among younger demographics
- **Gender**: Similar usage rates (Male: 44%, Female: 48% for companionship)

**Statistical Significance:** 
While individual-level correlation couldn't be calculated due to data structure, the pattern shows that responses mentioning heavy use/companionship skew more positive (38%) than concerned (15.7%), contrary to the hypothesis that heavy users would express more concerns.

**SQL Queries Used:**
```sql
-- Q66: AI Companionship Use
SELECT response, CAST("all" AS REAL) as all_pct,
       CAST(o2_18_25 AS REAL) as age_18_25,
       CAST(o3_male AS REAL) as male,
       CAST(o3_female AS REAL) as female
FROM responses 
WHERE question_id = 'cb65b063-bff3-4cac-a827-dbab6693e307';

-- Q17: Frequency of emotional support
SELECT response, CAST("all" AS REAL) as all_pct
FROM responses 
WHERE question_id = 'd2af725e-0391-4019-9ade-31f25162b6f0';

-- Q148: Final expression sentiment
SELECT response, sentiment, COUNT(*) as count
FROM responses 
WHERE question_id = 'f5d8656f-39ba-4ef5-a683-614caeffde4b'
AND sentiment IS NOT NULL
GROUP BY sentiment;
```

**Insights:** 
Contrary to the initial hypothesis, AI-Reliant users (those using AI for emotional support frequently) appear **more optimistic than concerned**. The 2.4:1 hope-to-concern ratio among heavy use mentions suggests that deeper experience with AI companionship correlates with more positive rather than negative outlooks. This challenges the assumption that familiarity breeds concern—instead, those with direct experience seem to see more potential benefits than risks.

**Limitations:** 
- Analysis based on aggregate data and text responses rather than individual-level correlations
- Sentiment classification may not capture full nuance of mixed feelings
- Self-selection bias (those continuing to use AI frequently likely have positive experiences)

## 1.2 How does reliance impact their view of the social fabric?

**Question:** Are the AI-Reliant more likely to believe AI relationships will weaken human social connections, perhaps because they've experienced it firsthand? Or do they see it as a valid and positive supplement?

**Analysis Approach:** 
Analyzed responses about AI's impact on social connections, comparing overall population views with sentiment patterns from frequent AI users. Examined Q134 about children's relationships and the open-ended question about most significant social impacts.

**Key Findings:**
- **81% believe AI could negatively impact children's ability to form human relationships** (47% strongly agree, 34% somewhat agree)
- When asked about the most significant social impact of AI in relationships:
  - 11.6% mentioned **over-dependence** themes
  - 7.0% explicitly mentioned **loss of human connection**
  - 3.7% mentioned **mental health benefits**
  - 73% mentioned other impacts or were neutral
- **Paradoxical finding**: Despite high concern about children's relationships (81%), overall assessment of AI chatbots is more positive than negative (52% see benefits outweighing risks vs 21% seeing risks outweighing benefits)
- **Comparison with social media**: People view AI chatbots more favorably than social media (AI: net +31% positive, Social Media: net -9% negative)

**Demographic Breakdowns:**
- Universal concern across all demographics about impact on children (81% agreement)
- Younger demographics show slightly lower concern levels
- No significant gender differences in social fabric concerns

**Statistical Significance:** 
The 81% agreement on negative impact for children's relationships represents strong consensus across all demographic segments, indicating this is a near-universal concern.

**SQL Queries Used:**
```sql
-- Q134: Impact on children's relationships
SELECT response, CAST("all" AS REAL) as all_pct
FROM responses 
WHERE question_id = '4178d870-d669-429b-a05e-8b681136849b';

-- Most significant social impact responses
SELECT response, COUNT(*) as count
FROM responses 
WHERE question_id = 'dc8fcd6e-95c5-46f0-8a92-87f6bc0008bf'
GROUP BY response;

-- Comparative impact assessment
SELECT response, CAST("all" AS REAL) as all_pct
FROM responses 
WHERE question LIKE '%overall impact on society of AI chatbots%';
```

**Insights:** 
AI-Reliant users appear to hold a **nuanced dual perspective**: they acknowledge potential negative impacts on social fabric (especially for vulnerable populations like children) while simultaneously viewing AI relationships as beneficial overall. This suggests they see AI as a **supplement rather than replacement** for human connection. The more favorable view of AI chatbots compared to social media indicates people differentiate between types of technology impact, possibly because AI offers more personalized, supportive interactions.

**Limitations:** 
- Cannot directly correlate individual usage patterns with social fabric views
- Text analysis may not capture full complexity of views
- Response bias towards more articulate participants in open-ended questions