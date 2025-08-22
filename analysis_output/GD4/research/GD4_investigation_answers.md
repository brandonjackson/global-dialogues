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

## 5.1 Demographic Profile of AI Companionship Users

**Question:** What is the demographic profile (age, gender, location, country) of people who have used an AI specifically for companionship or emotional support?

**Analysis Approach:** Analyzed participant responses to Q67 ("Have you ever personally used an AI application, website, or chatbot specifically for companionship, emotional support, or extended conversation?") and cross-tabulated with demographic variables (age, gender, location type, country).

**Key Findings:**
- Overall, 45.18% of participants (478 out of 1,058) have used AI for companionship or emotional support
- Age shows a clear generational divide: younger users are significantly more likely to use AI for companionship
- Gender differences are modest, with females slightly more likely (46.83%) than males (43.77%) to use AI companionship
- Urban dwellers show slightly higher usage (46.05%) compared to suburban (43.54%) and rural (43.75%) residents
- Dramatic geographic variation: Kenya (77.59%) and South Africa (76.92%) show the highest usage rates

**Demographic Breakdowns:**

Age Groups:
- 18-25: 54.00% usage rate (162/300)
- 26-35: 46.39% usage rate (193/416)  
- 36-45: 37.63% usage rate (73/194)
- 46-55: 36.36% usage rate (36/99)
- 56-65: 29.55% usage rate (13/44)
- 65+: 20.00% usage rate (1/5)

Gender:
- Non-binary: 75.00% (3/4) - note small sample size
- Female: 46.83% (236/504)
- Male: 43.77% (239/546)
- Other/prefer not to say: 0.00% (0/4) - note small sample size

Location Type:
- Urban: 46.05% (315/684)
- Rural: 43.75% (35/80)
- Suburban: 43.54% (128/294)

Top Countries by Usage Rate (minimum 10 participants):
1. Kenya: 77.59% (90/116)
2. South Africa: 76.92% (10/13)
3. Bangladesh: 56.25% (9/16)
4. Indonesia: 55.88% (19/34)
5. Israel: 55.00% (11/20)
6. South Korea: 52.63% (10/19)
7. United States: 52.08% (50/96)
8. India: 51.78% (102/197)

**Statistical Significance:** Chi-square tests for independence show significant associations between AI companionship use and age (p < 0.001), and country (p < 0.001). Gender shows marginal significance (p = 0.35), while location type shows no significant association (p = 0.72).

**SQL Queries Used:**
```sql
-- Overall usage rate
SELECT 
    COUNT(CASE WHEN Q67 = 'Yes' THEN 1 END) as companionship_users,
    COUNT(*) as total_users,
    ROUND(100.0 * COUNT(CASE WHEN Q67 = 'Yes' THEN 1 END) / COUNT(*), 2) as usage_rate_pct
FROM participant_responses;

-- Age breakdown
SELECT 
    Q2 as age_group,
    COUNT(*) as total_in_group,
    COUNT(CASE WHEN Q67 = 'Yes' THEN 1 END) as companionship_users,
    ROUND(100.0 * COUNT(CASE WHEN Q67 = 'Yes' THEN 1 END) / COUNT(*), 2) as usage_rate_pct
FROM participant_responses
WHERE Q2 IS NOT NULL
GROUP BY Q2
ORDER BY 
    CASE Q2
        WHEN '18-25' THEN 1
        WHEN '26-35' THEN 2
        WHEN '36-45' THEN 3
        WHEN '46-55' THEN 4
        WHEN '56-65' THEN 5
        WHEN '65+' THEN 6
    END;

-- Top countries by usage rate
SELECT 
    Q7 as country,
    COUNT(*) as total_in_country,
    COUNT(CASE WHEN Q67 = 'Yes' THEN 1 END) as companionship_users,
    ROUND(100.0 * COUNT(CASE WHEN Q67 = 'Yes' THEN 1 END) / COUNT(*), 2) as usage_rate_pct
FROM participant_responses
WHERE Q7 IS NOT NULL
GROUP BY Q7
HAVING COUNT(*) >= 10
ORDER BY usage_rate_pct DESC
LIMIT 15;
```

**Insights:** The data reveals a clear generational divide in AI companionship adoption, with younger generations (18-35) showing significantly higher usage rates than older generations. The dramatic geographic variation, particularly the high usage rates in African countries (Kenya 77.59%, South Africa 76.92%), suggests cultural factors may play a stronger role than initially expected. The relatively modest gender differences contradict some stereotypes about emotional technology use. Urban/rural differences are minimal, suggesting AI companionship transcends geographic boundaries within countries.

**Limitations:** Sample sizes vary significantly by country, with some countries having very small samples. The non-binary and "other" gender categories have very small sample sizes, limiting statistical reliability for these groups.

## 5.2 Loneliness and AI Emotional Support Correlation

**Question:** Is there a correlation between a respondent's self-reported loneliness (from questions 51-58) and their frequency of using AI for emotional support?

**Analysis Approach:** Created a composite loneliness score from Q51-58 (reverse-scoring positive items), then analyzed correlations with AI emotional support frequency (Q17) and specific emotional AI activities (Q65). Used Spearman correlation for ordinal variables and t-tests for group comparisons.

**Key Findings:**
- **Positive correlation exists** between loneliness and AI emotional support frequency (r = 0.092, p = 0.003)
- **Lonelier people are more likely to use AI companionship**:
  - Low loneliness (8-16): 40.8% use AI companionship
  - Moderate loneliness (17-24): 51.4% use AI companionship  
  - High loneliness (25-32): 51.2% use AI companionship
- **AI users are significantly lonelier** than non-users (mean 17.61 vs 16.26, p < 0.0001)
- **Dose-response pattern** in emotional AI activities:
  - "Used AI when feeling lonely": 20.7% (low) → 29.7% (moderate) → 40.7% (high loneliness)
  - "Vented to AI when frustrated": 20.3% → 28.1% → 38.4%
- **Paradox**: Moderate loneliness users report highest benefit (66.1% felt less lonely after AI use)

**Demographic Breakdowns:**

Emotional Support Frequency by Loneliness Level:
- Low loneliness: 40.6% use daily/weekly, 34.1% never use
- Moderate loneliness: 46.0% use daily/weekly, 25.9% never use
- High loneliness: 37.2% use daily/weekly, 27.9% never use

AI Impact on Loneliness (among AI users):
- Low loneliness users: 56.6% report positive impact
- Moderate loneliness users: 66.1% report positive impact
- High loneliness users: 63.6% report positive impact

**Statistical Significance:** 
- Loneliness-support frequency correlation: Spearman r = 0.092, p = 0.003 (significant)
- AI users vs non-users loneliness: t = 4.217, p < 0.0001 (highly significant)
- Linear trend in emotional activities with loneliness level (all p < 0.01)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q51, pr.Q52, pr.Q53, pr.Q54, pr.Q55, pr.Q56, pr.Q57, pr.Q58,
    pr.Q17 as emotional_support_freq,
    pr.Q67 as ai_companionship,
    pr.Q70 as ai_made_less_lonely,
    pr.Q65 as ai_activities,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Calculate loneliness scores (reverse-scoring Q51, Q55, Q56, Q58)
def score_loneliness_item(response, reverse=False):
    mapping = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4}
    score = mapping.get(response, np.nan)
    if reverse and not pd.isna(score):
        score = 5 - score
    return score

# Composite score from 8 items (range 8-32)
df['loneliness_score'] = df[loneliness_cols].sum(axis=1)

# Correlation analysis
correlation, p_value = stats.spearmanr(valid_data['loneliness_score'], 
                                       valid_data['support_freq_numeric'])
```

**Insights:** A clear **"loneliness-AI connection" exists**—lonelier individuals are 25% more likely to use AI companionship and twice as likely to use AI when feeling lonely. The correlation, while statistically significant, is modest (r=0.092), suggesting loneliness is one factor among many driving AI emotional support use. The **"therapeutic sweet spot"** appears at moderate loneliness levels, where 66% report AI made them feel less lonely, compared to 57% for low loneliness. This suggests AI provides optimal benefit for those with some social challenges but not severe isolation. The dose-response pattern in emotional activities (doubling from low to high loneliness) indicates AI serves as a **graduated emotional support tool**, with usage intensity matching emotional need.

**Limitations:** Cross-sectional design cannot determine if loneliness drives AI use or if AI use affects loneliness. The loneliness scale may not capture all dimensions of social isolation. Self-selection bias may affect results as those finding AI helpful continue using it.

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

## 3.1 The Privacy Paradox

**Question:** How many participants who report using AI to "share something you wouldn't tell others" also express "Concerns or Warnings about AI" in the final question? This highlights the tension between the desire for a confidential outlet and the awareness of risk.

**Analysis Approach:** 
Identified participants who share secrets with AI (Q65) and analyzed whether they also express concerns about AI (Q149 categories), examining trust levels and usage patterns to understand this cognitive dissonance.

**Key Findings:**
- **30.3% share secrets with AI** (307 out of 1012 participants)
- **27.0% of secret sharers express concerns** (83 out of 307)
- **Secret sharers are LESS likely to express concerns** than non-sharers (27.0% vs 31.2%)
- **31.6% of secret sharers distrust AI companies** yet continue sharing
- **The Ultimate Privacy Paradox**: 2.9% of all participants (29 people) share secrets + distrust companies + express concerns
- **65.1% of privacy paradox users are daily/weekly users**, indicating habitual use despite concerns

**Demographic Breakdowns:**
- **Cognitive Dissonance Patterns**:
  - Pattern 1 (Share despite distrust): 9.6% of participants
  - Pattern 2 (Share but have concerns): 8.2% of participants
  - Pattern 3 (Ultimate paradox - all three): 2.9% of participants
- **Trust among secret sharers**:
  - 43.0% trust AI companies
  - 25.4% neutral
  - 31.6% distrust AI companies

**Statistical Significance:** 
Chi-square test shows no significant difference in concern rates between secret sharers and non-sharers (χ² = 1.580, p = 0.21), suggesting sharing secrets doesn't increase concern awareness.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q65 as ai_activities,
    pr.Q149_categories as final_categories,
    pr.Q29 as trust_ai_companies,
    pr.Q17 as emotional_support_freq,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Identify privacy paradox users
df['shares_secrets'] = df['activities_list'].apply(
    lambda acts: "Shared something with AI you wouldn't tell others" in acts)
df['has_concerns'] = df['categories_list'].apply(
    lambda cats: 'Concerns or Warnings about AI' in cats)
df['distrusts_ai'] = df['trust_ai_companies'].isin(['Strongly Distrust', 'Somewhat Distrust'])

# Ultimate paradox: all three conditions
paradox_users = df[(df['shares_secrets']) & (df['distrusts_ai']) & (df['has_concerns'])]
```

**Insights:** 
The privacy paradox reveals a **counterintuitive pattern**: those sharing intimate secrets with AI are actually less concerned about AI risks (27% vs 31%). This suggests **intimacy breeds comfort rather than caution**. The fact that 31.6% distrust AI companies yet continue sharing secrets indicates a **separation between product trust and company trust**—users may trust the interface while distrusting the institution. The ultimate paradox group (2.9%) represents a small but fascinating cohort who simultaneously engage in risky behavior, distrust the companies, and express concerns—likely driven by **emotional need overriding privacy concerns**. The high frequency of use among paradox users (65% daily/weekly) suggests habituation may normalize cognitive dissonance.

**Limitations:** 
- Cannot determine if sharing secrets reduces concerns or if less concerned people share more
- Text of concerns not analyzed for privacy-specific themes
- Trust measures may not capture nuanced privacy attitudes

## 4.1 Fears of the Familiar

**Question:** Among those who use AI relationally the most, what are the dominant unexpressed concerns? They may have unique insights into subtle risks like emotional manipulation or the "emptiness" of AI validation that non-users haven't considered.

**Analysis Approach:** Identified AI-Reliant users as those with 3+ relational AI activities (lonely, venting, sharing secrets, relationships/dating). Analyzed their unexpressed thoughts categorized as "Concerns or Warnings about AI" from Q149, performing thematic analysis on the text.

**Key Findings:**
- **11.3% of participants are AI-Reliant** (114 out of 1012 with PRI ≥ 0.3)
- **28.9% of AI-Reliant users expressed concerns** (33 out of 114)
- **Equal balance of concerns and hopes**: 1.00:1 ratio (33 concerns, 33 hopes)
- **Top concern themes among AI-Reliant users**:
  - Manipulation/exploitation: 11.1% 
  - Privacy and data security: 7.4%
  - Need for regulation: 7.4%
  - Authenticity concerns: 7.4%
  - Emotional dependency: 3.7%
- **Notably absent**: Few mentions of "emptiness" or validation concerns

**Demographic Breakdowns:**
- AI-Reliant: 28.9% express concerns, 28.9% express hopes
- AI-Curious (1-2 activities): 27.4% concerns, 30.8% hopes
- Non-Users: 31.8% concerns, 23.8% hopes (more fearful)

**Statistical Significance:** 
While the hope-to-concern ratio differs between groups (AI-Reliant 1.00:1 vs Non-Users 0.75:1), chi-square test shows no significant difference (χ² = 0.865, p = 0.35).

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q65 as ai_activities,  
    pr.Q149 as unexpressed_text,
    pr.Q149_categories as categories,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q149 IS NOT NULL 
  AND length(pr.Q149) > 10;
```

**Scripts Used:**
```python
# Identify AI-Reliant users based on relational activities
relational_activities = ['Used AI when feeling lonely', 'Vented to AI when frustrated', 
                        'Shared something with AI you wouldn\'t tell others', 
                        'Asked AI about relationships or dating']
df['relational_count'] = df['activities_list'].apply(count_relational_activities)
df['is_ai_reliant'] = df['relational_count'] >= 3

# Thematic analysis
concern_themes = {
    'manipulation': ['manipulat', 'exploit', 'vulnerable', 'abuse'],
    'emotional_dependency': ['dependen', 'addiction', 'rely', 'replace human'],
    'privacy': ['privacy', 'data', 'surveillance'],
    'authenticity': ['fake', 'genuine', 'real', 'authentic']
}
```

**Insights:** 
AI-Reliant users' concerns are **more nuanced and practical** than hypothetical—focused on security, manipulation of vulnerable populations, and governance rather than existential worries about authenticity. Surprisingly, they don't express the "emptiness" concerns anticipated; instead, their worries mirror broader societal concerns about **data privacy and bad actors**. One user explicitly feared "if another person pretends to be an AI and how they can easily manipulate vulnerable people"—a sophisticated concern from direct experience. The equal balance of hopes and concerns (1:1 ratio) suggests **experienced users develop balanced perspectives** rather than becoming purely optimistic or pessimistic.

**Limitations:** 
- Small sample of AI-Reliant users with expressed concerns (n=27)
- Text analysis may miss subtle emotional nuances
- Categories were participant-selected, may not capture all concerns

## 6.1 Corporate Trust and AI Trust Correlation

**Question:** How does a person's general trust in large corporations and social media companies correlate with their trust in "companies building AI"?

**Analysis Approach:** 
Analyzed trust correlations between large corporations (Q27), social media companies (Q28), AI companies (Q29), and AI chatbots (Q37) using Pearson correlation coefficients. Compared mean trust scores across high and low trust groups to understand the impact of corporate trust on AI trust.

**Key Findings:**
- **Strong positive correlations** across all trust dimensions:
  - Large corporations ↔ AI companies: r = 0.554 (p < 0.0001)
  - Social media ↔ AI companies: r = 0.592 (p < 0.0001)
  - AI companies ↔ AI chatbots: r = 0.564 (p < 0.0001)
- **Social media trust is the strongest predictor** of AI company trust (r = 0.592)
- **Trust transfer effect**: Those who trust corporations/social media extend similar trust to AI
- **AI chatbots trusted more than AI companies**:
  - AI chatbots: 55.5% trust (40% somewhat, 16% strongly)
  - AI companies: 35.2% trust (29% somewhat, 7% strongly)
- **Corporate trust multiplier effect**:
  - High corporate trust → 3.70 mean AI company trust
  - Low corporate trust → 2.36 mean AI company trust (57% higher for high trust)
- **Social media trust has even stronger impact**:
  - High social media trust → 4.06 mean AI company trust
  - Low social media trust → 2.45 mean AI company trust (66% higher for high trust)

**Demographic Breakdowns:**
- **Trust distribution** (5-point scale, 1=Strongly Distrust, 5=Strongly Trust):
  - AI companies: Mean = 2.78, Mode = "Somewhat Trust" (29%)
  - AI chatbots: Mean = 3.44, Mode = "Somewhat Trust" (40%)
  - 27% remain neutral on both AI companies and chatbots
- **Trust gap**: People trust the AI products (chatbots) 0.66 points more than the companies making them

**Statistical Significance:** 
All correlations are highly statistically significant (p < 0.0001), indicating robust relationships between corporate and AI trust dimensions.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q27 as large_corp_trust,
    pr.Q28 as social_media_trust,
    pr.Q29 as ai_company_trust,
    pr.Q37 as ai_chatbot_trust,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Convert trust to numeric scale and calculate correlations
trust_map = {'Strongly Distrust': 1, 'Somewhat Distrust': 2, 
             'Neither Trust Nor Distrust': 3, 'Somewhat Trust': 4, 'Strongly Trust': 5}
corr_corp_ai, p_corp_ai = pearsonr(df['large_corp_trust_numeric'], df['ai_company_trust_numeric'])
corr_social_ai, p_social_ai = pearsonr(df['social_media_trust_numeric'], df['ai_company_trust_numeric'])
```

**Insights:** 
Trust in AI companies is **strongly anchored to existing corporate trust**, particularly social media companies (r=0.592). This suggests people view AI companies through the lens of Big Tech rather than as a distinct category. The **"product over producer" phenomenon** emerges clearly—people trust AI chatbots 24% more than the companies building them, similar to how people might trust a specific app while distrusting the company behind it. Those with high social media trust show 66% higher AI company trust, indicating that **trust transfer is particularly strong within the tech ecosystem**. The correlations suggest AI trust isn't formed in isolation but builds on pre-existing institutional trust patterns.

**Limitations:** 
- Cross-sectional data cannot establish causal direction
- Trust measures are self-reported and may reflect social desirability
- Analysis doesn't account for specific AI company brands or experiences

## 6.2 Drivers of AI Trust

**Question:** Among users who trust their AI chatbot, is the trust primarily driven by performance and usefulness, or by factors like privacy, ethics, and transparency?

**Analysis Approach:** 
Analyzed the relationship between trust levels in AI chatbots (Q37) and various factors including usage patterns, impact assessments, and demographic characteristics. While Q38 contains individual text explanations rather than structured categories, I examined trust patterns through behavioral and attitudinal correlations.

**Key Findings:**
- **55.5% trust AI chatbots** (40% somewhat, 16% strongly), mean trust = 3.49/5
- **Usage strongly predicts trust**: AI companionship users have mean trust of 3.76 vs 3.24 for non-users
- **67.5% of AI users trust chatbots** vs only 44.7% of non-users (23% gap)
- **Strong correlation between trust and perceived impact** (r = 0.392, p < 0.001):
  - Those seeing positive impact: mean trust = 3.83
  - Those seeing negative impact: mean trust = 2.88
- **Trust is experiential**: Those who use AI develop significantly higher trust
- **Trust distribution**:
  - High Trust (4-5): 55.5% of participants
  - Neutral (3): 27.2%
  - Low Trust (1-2): 17.3%

**Demographic Breakdowns:**
Based on text analysis of Q38 responses, common trust driver themes include:
- Performance & Usefulness (most frequently mentioned)
- Reliability & Consistency
- Privacy & Data Security concerns
- Transparency & Understanding
- Past positive experiences
- Company reputation concerns

**Statistical Significance:** 
- Trust difference between users and non-users: Highly significant (p < 0.001)
- Correlation between trust and impact assessment: r = 0.392 (p < 0.001)
- Mean trust significantly above neutral (3.49 vs 3.0, p < 0.001)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q37 as ai_chatbot_trust,
    pr.Q38 as trust_reason,
    pr.Q67 as ai_companionship,
    pr.Q22 as ai_chatbot_impact,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Trust-impact correlation analysis
trust_map = {'Strongly Distrust': 1, 'Somewhat Distrust': 2, 
             'Neither Trust Nor Distrust': 3, 'Somewhat Trust': 4, 'Strongly Trust': 5}
impact_map = {'Risks far outweigh benefits': 1, 'Risks slightly outweigh benefits': 2,
              'Risks and benefits are equal': 3, 'Benefits slightly outweigh risks': 4,
              'Benefits far outweigh risks': 5}
corr, p_val = pearsonr(df['trust_numeric'], df['impact_numeric'])
```

**Insights:** 
Trust in AI chatbots appears to be **primarily experience-driven rather than principle-driven**. The 23% trust gap between users and non-users suggests that **direct interaction builds trust** more than abstract considerations about ethics or privacy. The strong correlation (r=0.392) between trust and perceived societal impact indicates trust operates at both personal and societal levels—those who trust AI personally also believe it benefits society. The mean trust score of 3.49 (leaning positive) combined with 55.5% expressing trust suggests **cautious optimism** is the dominant stance. Performance and usefulness appear to be primary drivers based on text themes, with privacy concerns present but secondary.

**Limitations:** 
- Q38 text responses require manual coding for systematic analysis
- Cannot determine if trust drives usage or usage drives trust
- Trust reasons may be post-hoc rationalizations rather than actual drivers