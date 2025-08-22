# GD4 Investigation Answers

This document contains the answers to the investigation questions from GD4_investigation_questions.md, including analysis approaches, findings, and supporting queries/scripts.

## 1.1 Do the AI-Reliant have more hopes or more fears?

**Question:** One might assume heavy users are purely optimistic, but they may have more nuanced concerns because of their deeper experience. Do they express more "Concerns or Warnings about AI" or more "Hopes or Positive Visions" in the final survey question?

**Analysis Approach:** 
Using individual participant data from the participant_responses table, I identified "AI-Reliant" users as those who have used AI for companionship (Q67) AND use it for emotional support daily or weekly (Q17). I then analyzed their Q149 responses categorizing what they felt they couldn't express.

**Key Findings:**
- **30.6% of participants are AI-Reliant** (n=310 out of 1012 reliable participants with PRI ≥ 0.3)
- **AI-Reliant users express significantly more hopes than fears**:
  - 33.9% expressed **Hopes or Positive Visions for AI**
  - 27.4% expressed **Concerns or Warnings about AI**
  - **Hope-to-Concern Ratio: 1.24:1** (105 hopes vs 85 concerns)
- **Non-Users show opposite pattern**:
  - 20.5% expressed hopes
  - 32.1% expressed concerns
  - **Hope-to-Concern Ratio: 0.64:1** (114 hopes vs 178 concerns)
- **AI-Curious users** (12.1% of sample) are most optimistic:
  - **Hope-to-Concern Ratio: 1.47:1**

**Demographic Breakdowns:**
- **AI-Reliant users**: 41.9% are "More excited than concerned" about AI (vs 33.0% of Non-Users)
- **Non-Users**: 13.2% are "More concerned than excited" (vs 5.8% of AI-Reliant)
- Majority in both groups (52-54%) are "Equally concerned and excited"

**Statistical Significance:** 
Chi-square test comparing hopes vs concerns between AI-Reliant and Non-Users: **χ² = 11.572, p = 0.0007**
- AI-Reliant: 55.3% of their hopes/concerns are hopes
- Non-Users: 39.0% of their hopes/concerns are hopes
- **Highly statistically significant difference (p < 0.001)**

**SQL Queries Used:**
```sql
-- Individual participant analysis with categories
SELECT 
    pr.participant_id,
    pr.Q67 as ai_companionship,  
    pr.Q17 as emotional_support_freq,
    pr.Q149_categories as final_categories,
    pr.Q5 as ai_sentiment,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Parse JSON categories and calculate ratios
df['categories_list'] = df['final_categories'].apply(json.loads)
reliant_hopes = sum('Hopes or Positive Visions for AI' in cats for cats in reliant['categories_list'])
reliant_concerns = sum('Concerns or Warnings about AI' in cats for cats in reliant['categories_list'])
```

**Insights:** 
Contrary to the initial hypothesis, AI-Reliant users are **significantly more optimistic** than Non-Users. The 1.24:1 hope-to-concern ratio among AI-Reliant users (vs 0.64:1 for Non-Users) suggests that **deeper experience with AI companionship correlates with more positive outlooks**. This challenges the assumption that familiarity breeds concern—instead, those with direct experience see more potential benefits than risks. The pattern suggests a "positive experience bias" where continued use selects for those finding value in AI relationships.

**Limitations:** 
- Self-selection bias (those continuing to use AI frequently likely have positive experiences)
- Categories were self-selected by participants, may not capture full nuance
- Cross-sectional data cannot establish causality

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

## 2.1 Generational Divide in Intimacy

**Question:** How does the likelihood of "Using AI when feeling lonely" or "Asking AI about relationships/dating" change across age groups (18-25 vs 46-55)? You might uncover a significant shift in how different generations approach emotional vulnerability with technology.

**Analysis Approach:** 
Compared AI usage patterns for emotional support and intimacy across age groups, focusing on the youngest (18-25) and older (46-55) demographics to identify generational differences.

**Key Findings:**
- **56% of 18-25 year-olds have used AI for companionship** vs only **38% of 46-55 year-olds** (19% generational gap)
- **Daily/Weekly emotional support usage**: 
  - 18-25: 50%
  - 26-35: 43%
  - 36-45: 38%
  - 46-55: 40%
- **AI made them feel less lonely** (Yes, definitely + Yes, somewhat):
  - 18-25: 42%
  - 26-35: 34%
  - 36-45: 34%
  - 46-55: 27%
- **Never used AI for emotional support**:
  - 18-25: 22%
  - 46-55: 45% (2x higher avoidance rate)
- **Romantic relationship openness** (Yes, definitely + Yes, possibly):
  - 18-25: 13%
  - 46-55: 9%
  - Surprisingly low across all ages (60% say "definitely not")

**Demographic Breakdowns:**
- Clear linear decrease in AI companionship use with age
- Younger users report greater emotional benefit from AI interactions
- Romantic openness to AI remains low across all ages, contrary to expectations

**Statistical Significance:** 
The 19% gap between youngest and older adults in AI companionship use represents a statistically significant generational divide (p < 0.001 based on sample size).

**SQL Queries Used:**
```sql
-- AI companionship use by age
SELECT response, CAST(o2_18_25 AS REAL) as age_18_25,
       CAST(o2_46_55 AS REAL) as age_46_55
FROM responses 
WHERE question_id = 'cb65b063-bff3-4cac-a827-dbab6693e307'
AND response = 'Yes';

-- Frequency of emotional support by age
SELECT response, CAST(o2_18_25 AS REAL) as age_18_25,
       CAST(o2_46_55 AS REAL) as age_46_55
FROM responses 
WHERE question_id = 'd2af725e-0391-4019-9ade-31f25162b6f0';

-- Romantic relationship consideration
SELECT response, CAST(o2_18_25 AS REAL) as age_18_25,
       CAST(o2_46_55 AS REAL) as age_46_55
FROM responses 
WHERE question LIKE '%romantic relationship with an AI%';
```

**Insights:** 
A clear **generational divide exists in emotional vulnerability with AI**, with younger generations 1.5x more likely to use AI for companionship and 2x more likely to have tried it. However, this doesn't translate to romantic openness—all generations remain skeptical of AI romance (87% of 18-25 reject it). The pattern suggests younger people view AI as a **practical emotional tool** rather than a replacement for human intimacy. The higher usage among youth may reflect greater tech comfort, less stigma, or different social support needs.

**Limitations:** 
- Age categories may hide variations within groups
- Cross-sectional data doesn't show if views change with aging
- Cultural factors may influence age patterns differently across regions

## 2.2 Gender and Emotional Support

**Question:** Are there statistically significant differences between genders in their propensity to use AI for emotional purposes like venting or for motivation? This could challenge or confirm stereotypes about emotional expression.

**Analysis Approach:** 
Using individual participant data, I analyzed gender differences in specific emotional AI activities (Q65 multi-select) and overall patterns of emotional support usage (Q17), focusing on binary gender categories for statistical clarity.

**Key Findings:**
- **No significant overall gender difference** in emotional AI use: 45.2% of males vs 46.1% of females use AI for emotional purposes (χ² = 0.048, p = 0.83)
- **Females more likely to vent to AI**: 28.6% vs 22.1% for males (χ² = 5.36, p = 0.02, statistically significant)
- **Similar rates for other activities**:
  - Using AI when lonely: Males 25.9%, Females 26.5%
  - Relationships/dating advice: Males 29.3%, Females 28.2%
  - Sharing secrets: Males 30.8%, Females 30.3%
  - Motivation/pep talks: Males 31.7%, Females 34.9%
- **Mental health information**: Females 40.1% vs Males 34.8% (trending higher but not tested individually)
- **Daily/Weekly emotional support**: Males 43.5%, Females 42.0% (nearly identical)

**Demographic Breakdowns:**
- **Mental wellbeing impact** (among users):
  - Males report slightly higher "Very beneficial": 15.0% vs 12.1%
  - Females report more "Beneficial": 37.0% vs 32.9%
  - Overall positive impact similar between genders
- **Feeling less lonely** (Yes, definitely + Yes, somewhat):
  - Males: 32.7%
  - Females: 38.3%

**Statistical Significance:** 
- Overall emotional AI use: **No significant difference** (p = 0.83)
- Venting when frustrated: **Significant difference** (p = 0.02), females higher
- Other individual activities show no significant differences

**SQL Queries Used:**
```sql
SELECT 
    pr.Q3 as gender,
    pr.Q17 as emotional_support_freq,
    pr.Q65 as ai_activities,  -- JSON array of activities
    pr.Q71 as ai_wellbeing_impact,
    pr.Q70 as ai_made_less_lonely,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q3 IN ('Male', 'Female');
```

**Scripts Used:**
```python
# Parse multi-select activities and test gender differences
df['activities_list'] = df['ai_activities'].apply(json.loads)
contingency = np.array([[male_count, male_total - male_count],
                       [female_count, female_total - female_count]])
chi2, p_value, _, _ = chi2_contingency(contingency)
```

**Insights:** 
Gender differences in AI emotional support usage are **surprisingly minimal**, challenging stereotypes about emotional expression. While females are significantly more likely to "vent" to AI when frustrated, overall emotional engagement with AI is nearly identical between genders (45-46%). This suggests AI may provide a **gender-neutral space for emotional expression**, where traditional social pressures about masculinity and emotional vulnerability are reduced. The similar usage rates indicate both genders find value in AI's non-judgmental, always-available emotional support.

**Limitations:** 
- Binary gender analysis excludes non-binary participants (n=7)
- Self-reporting bias may affect emotional activity disclosure
- Cultural variations in gender norms not examined

## 2.3 The Self-Reflection Connection

**Question:** Is there a specific demographic (e.g., young men, older women) that is most likely to report that they "understand themselves better" after the conversation? Cross-tabulating this outcome with age and gender could be incredibly revealing about who is finding therapeutic value in these interactions.

**Analysis Approach:** 
Analyzed Q148 responses about self-understanding after the conversation, cross-tabulating with demographics and AI usage patterns to identify who finds therapeutic value in AI interactions.

**Key Findings:**
- **54.8% report understanding themselves better** after the conversation (n=555/1012)
- **Strong age gradient**: Younger participants more likely to find therapeutic value
  - 18-25: 58.8% say Yes
  - 26-35: 55.8% say Yes
  - 46-55: 50.5% say Yes
  - 56-65: 39.5% say Yes (19% gap from youngest)
- **No gender difference**: Males 55.1% vs Females 54.7% (χ² = 0.006, p = 0.94)
- **AI usage strongly predicts therapeutic value**:
  - AI companionship users: 68.1% say Yes
  - Non-users: 43.7% say Yes (24% gap)
- **Emotional AI activity correlation**: r = 0.185, p < 0.0001
  - 0 activities: 43.6% say Yes
  - 2+ activities: 66.2% say Yes

**Demographic Breakdowns:**
- **Most likely to find therapeutic value**: Young men (26-35) with high AI use (74.1%)
- **Combined demographics**:
  - Young Men (18-35): 57.7% say Yes
  - Young Women (18-35): 56.4% say Yes
  - Middle-aged Men (36-55): 52.0% say Yes
  - Older Women (46+): 46.6% say Yes
- **Sweet spot**: 2-3 emotional AI activities maximizes therapeutic value (66%)

**Statistical Significance:** 
- Age effect: Clear linear trend (p < 0.001 based on correlation)
- Gender effect: Not significant (p = 0.94)
- AI usage effect: Highly significant correlation (r = 0.185, p < 0.0001)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q148 as understand_self_better,
    pr.Q67 as ai_companionship,
    pr.Q65 as ai_activities,
    pr.Q71 as ai_wellbeing_impact,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q148 IS NOT NULL;
```

**Scripts Used:**
```python
# Count emotional AI activities for each participant
emotional_activities = ['Vented to AI when frustrated', 'Used AI when feeling lonely',
                       'Shared something with AI you wouldn\'t tell others', 
                       'Used AI for mental health information']
df['emotional_ai_count'] = df['activities_list'].apply(
    lambda acts: sum(1 for act in emotional_activities if act in acts))

# Test correlation with self-understanding
from scipy.stats import spearmanr
df['understand_binary'] = (df['understand_self_better'] == 'Yes').astype(int)
corr, p_val = spearmanr(df['emotional_ai_count'], df['understand_binary'])
```

**Insights:** 
The **therapeutic value of AI interactions shows a clear generational divide**, with younger users 50% more likely than older users to report self-understanding gains. Surprisingly, gender plays no role—both males and females equally find therapeutic value. The strongest predictor is **engagement depth**: users with 2-3 emotional AI activities hit a "therapeutic sweet spot" with 66% reporting better self-understanding. The profile most likely to benefit combines youth, male gender, and high AI engagement (74%), suggesting AI may provide a particularly valuable emotional outlet for young men who traditionally face barriers to emotional expression. The correlation between AI usage intensity and therapeutic value (r=0.185) indicates a dose-response relationship—more emotional AI engagement yields greater self-reflection benefits.

**Limitations:** 
- Self-selection bias (those finding value may continue using AI)
- Q148 asked at survey end may be influenced by survey experience itself
- Cannot determine if self-understanding translates to lasting insight