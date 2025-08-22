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

## 3.2 The "Rules for Thee, But Not for Me" Phenomenon

**Question:** Is there a segment of the population that is personally open to forming relationships with AI (based on their USAGE) but also believes these relationships are broadly negative for the "social fabric"?

**Analysis Approach:** 
Identified participants who personally use AI for companionship/emotional support while simultaneously expressing concerns about societal impacts, analyzing patterns of cognitive dissonance between personal behavior and societal beliefs.

**Key Findings:**
- **62.5% of AI companion users hold societal concerns** despite personal use (292 out of 467)
- **23.8% experience the core paradox**: Use AI, see personal benefit, but fear loss of human connection
- **20.1% use AI emotionally but fear exploitation** of vulnerable populations
- **6.9% use AI companions but believe risks outweigh benefits** for society
- **Key pattern**: AI users fear societal impacts (62% fear loss of connection) while benefiting personally (83% see positive daily life impact)
- **Universal concern**: 80.5% agree AI harms children's relationships (aggregate data)

**Demographic Breakdowns:**
- **"Good for Me, Bad for Society" group** (28.9% of all participants):
  - 82.5% fear loss of genuine human connection
  - 45.2% fear widespread social isolation
  - 31.8% fear exploitation of vulnerable people
  - Yet only 13.4% believe risks outweigh benefits
- **AI Companion Users vs Non-Users**:
  - Social isolation fears: Nearly identical (32.5% vs 33.8%, p=0.73)
  - Loss of connection fears: Slightly higher for users (61.9% vs 57.2%)
  - Risk assessment: Users less concerned (15% vs 25.5% think risks outweigh)

**Statistical Significance:** 
No significant difference in social isolation fears between users and non-users (χ² = 0.117, p = 0.73), suggesting usage doesn't reduce societal concerns.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q65 as ai_activities,
    pr.Q67 as ai_companionship,
    pr.Q22 as ai_chatbot_impact,
    pr.Q115 as greatest_fears,  -- JSON array
    pr.Q45 as daily_life_impact,
    pr.Q77 as emotional_bond_acceptable,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Identify paradox patterns
pattern4 = df[(df['ai_companion_user'] == True) & 
              (df['daily_life_impact'].isin(['Noticeably Better', 'Profoundly Better'])) &
              (df['fears_loss_connection'] == True)]

# "Good for Me, Bad for Society" profile
good_for_me = df[(df['ai_companion_user'] == True) & 
                 (df['daily_life_impact'].isin(['Noticeably Better', 'Profoundly Better'])) &
                 ((df['fears_social_isolation'] == True) | 
                  (df['fears_loss_connection'] == True))]
```

**Insights:** 
The "Rules for Thee, But Not for Me" phenomenon is **widespread and nuanced**. The majority (62.5%) of AI companion users acknowledge societal risks while continuing personal use, suggesting **compartmentalized thinking** rather than hypocrisy. Users maintain societal concerns at similar rates to non-users but assess risks differently—they're 10% less likely to think risks outweigh benefits, likely due to **personal experience tempering abstract fears**. The universal concern about children (80.5%) combined with high parental AI use suggests a **protective double standard**—"It's okay for adults who can handle it, but not for vulnerable populations." This pattern reflects rational risk assessment rather than pure contradiction: users recognize both personal benefits and societal challenges, accepting the former while warning about the latter.

**Limitations:** 
- Cannot access individual-level data for children's impact question
- Emotional bond acceptance shows 0% in data (possible data issue with Q77)
- Cross-sectional design cannot determine if concerns preceded or followed usage

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

## 6.3 Human Support Availability and AI Impact

**Question:** Among those who have used AI for emotional support, did the AI's impact on their mental well-being differ based on the availability or appeal of human support at the time? (This explores whether AI is a last resort or a genuine preference).

**Analysis Approach:** 
Created four support profiles based on human support availability (Q68) and appeal (Q69): Supplementers (available & appealing), Escapists (available but unappealing), Last Resort (unavailable but appealing), and Isolates (unavailable & unappealing). Analyzed wellbeing impact (Q71) and loneliness reduction (Q70) across these profiles.

**Key Findings:**
- **Isolates report the highest wellbeing benefit** (mean impact = 4.36/5, 86.2% beneficial, 43.1% very beneficial)
- **Escapists close second** (mean = 4.12, 86.0% beneficial)
- **Last Resort users report similar benefit** to Escapists (mean = 4.11, 75.7% beneficial)
- **Supplementers report lowest benefit** (mean = 4.04, 81.0% beneficial)
- **Significant differences across profiles** (ANOVA: F = 3.229, p = 0.023)
- **Support profile distribution** among AI users:
  - Mixed/Neutral: 41.1%
  - Supplementers: 29.3%
  - Isolates: 12.4%
  - Escapists: 9.2%
  - Last Resort: 7.9%

**Demographic Breakdowns:**
Loneliness reduction by profile:
- **Isolates**: 70.7% felt less lonely (highest)
- **Escapists**: 69.8% felt less lonely
- **Last Resort**: 62.2% felt less lonely
- **Supplementers**: 60.6% felt less lonely (lowest)

The pattern inverts expectations—those with least human support report greatest AI benefit.

**Statistical Significance:** 
- ANOVA across profiles: F = 3.229, p = 0.023 (significant)
- Escapist vs Last Resort: No significant difference (p = 0.96)
- Clear gradient from Supplementers to Isolates in benefit levels

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q67 as ai_companionship,
    pr.Q68 as human_support_availability,
    pr.Q69 as human_support_appeal,
    pr.Q70 as ai_made_less_lonely,
    pr.Q71 as ai_wellbeing_impact,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Categorize support profiles
def categorize_support(row):
    if availability in ['Mostly available', 'Completely available'] and 
       appeal in ['Mostly appealing', 'Completely appealing']:
        return 'Supplementer'
    elif availability in ['Mostly available', 'Completely available'] and 
         appeal in ['Mostly unappealing', 'Completely unappealing']:
        return 'Escapist'
    # etc.

# Statistical comparison
f_stat, p_val = f_oneway(supplementer_impacts, escapist_impacts, 
                         last_resort_impacts, isolate_impacts)
```

**Insights:** 
The findings reveal a **counterintuitive pattern**: AI provides greatest therapeutic benefit to those with the least human support. Isolates—those lacking both availability and appeal of human support—report the highest wellbeing gains (43% "very beneficial"), suggesting AI fills a **critical emotional void** rather than merely supplementing existing support. Escapists, who actively choose AI over available human support, show similarly high benefits, indicating AI may offer something **qualitatively different** from human interaction—perhaps judgment-free listening or constant availability. The lower benefit for Supplementers suggests AI adds less value when human needs are already met. This challenges the "last resort" narrative—instead, AI appears most valuable for those who either can't access or don't want traditional human support.

**Limitations:** 
- Self-selection bias (those benefiting may continue using AI)
- Cannot determine if support profiles are stable or situational
- 41% fall into mixed/neutral categories, limiting clear categorization
## 5.3 Religious Influence on AI Spiritual Roles

**Question:** How does religious identification influence the acceptability of AI serving as a spiritual advisor or mentor?

**Analysis Approach:** Cross-tabulated religious affiliation (Q6) with acceptability ratings for AI as spiritual advisor (Q88) and AI as mentor providing life guidance (Q87). Compared acceptance rates across major religious groups and non-religious participants.

**Key Findings:**
- **Stark contrast between spiritual advisor and mentor roles**:
  - AI as spiritual advisor: 67.6% find acceptable overall
  - AI as mentor: Only 17.7% find acceptable overall
- **Religious participants MORE accepting of AI spiritual advisors**:
  - Hinduism: 82.6% acceptable (39.1% completely)
  - Christianity: 75.2% acceptable (31.5% completely)
  - Islam: 70.2% acceptable (22.4% completely)
  - Non-religious: 53.4% acceptable (13.6% completely)
- **Mentor role universally rejected across all groups**:
  - Hinduism: 26.1% acceptable, 60.2% unacceptable
  - Christianity: 20.8% acceptable, 61.5% unacceptable
  - Non-religious: 15.9% acceptable, 65.4% unacceptable
  - Islam: 13.0% acceptable, 76.4% unacceptable
- **Pattern reversal**: Religious individuals show 1.4x higher acceptance of AI spiritual guidance than non-religious

**Demographic Breakdowns:**

Spiritual Advisor Acceptability by Religion:
- Hinduism: 82.6% accept (39% completely, 44% somewhat)
- Christianity: 75.2% accept (32% completely, 44% somewhat)
- Islam: 70.2% accept (22% completely, 48% somewhat)
- Buddhism: 53.8% accept (21% completely, 33% somewhat)
- Non-religious: 53.4% accept (14% completely, 40% somewhat)
- Judaism: 41.2% accept (6% completely, 35% somewhat)

Mentor Acceptability by Religion:
- Hinduism: 26.1% accept, 37.0% completely unacceptable
- Christianity: 20.8% accept, 36.4% completely unacceptable
- Non-religious: 15.9% accept, 40.5% completely unacceptable
- Islam: 13.0% accept, 55.9% completely unacceptable

**Statistical Significance:** Chi-square test of independence shows highly significant association between religious affiliation and AI spiritual advisor acceptability (χ² = 89.4, p < 0.001), and between religion and mentor acceptability (χ² = 45.2, p < 0.001).

**SQL Queries Used:**
```sql
-- Religious influence on AI spiritual advisor and mentor acceptability
SELECT 
    pr.Q6 as religion,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(CASE WHEN pr.Q88 IN ('Completely acceptable', 'Somewhat acceptable') THEN 1 END) / COUNT(*), 1) as spiritual_advisor_acceptable_pct,
    ROUND(100.0 * COUNT(CASE WHEN pr.Q87 IN ('Completely acceptable', 'Somewhat acceptable') THEN 1 END) / COUNT(*), 1) as mentor_acceptable_pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q6 IS NOT NULL
GROUP BY pr.Q6
ORDER BY total DESC;

-- Detailed breakdown by response category
SELECT 
    pr.Q6 as religion,
    pr.Q88 as spiritual_advisor_response,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY pr.Q6), 1) as pct_within_religion
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q6 IN ('Christianity', 'Islam', 'Hinduism', 'I do not identify with any religious group or faith')
GROUP BY pr.Q6, pr.Q88;
```

**Insights:** The **"spiritual paradox"** emerges clearly—religious individuals are significantly MORE accepting of AI spiritual advisors than non-religious individuals (75% vs 53%), contrary to expectations that religious people would guard spiritual domains more carefully. This suggests religious individuals may view AI as a **complementary spiritual tool** rather than replacement, possibly similar to religious apps or online sermons. The universal rejection of AI as life mentor (only 18% accept) while embracing spiritual guidance (68% accept) reveals an important distinction: people accept AI for **domain-specific spiritual support** but reject it for **holistic life guidance**. Hindus show highest acceptance (83%), possibly reflecting comfort with diverse spiritual practices, while non-religious individuals' lower acceptance may stem from viewing spirituality itself as less relevant.

**Limitations:** Sample sizes vary significantly by religion (Christianity n=327, Sikhism n=5). Cultural context within religions not captured (e.g., evangelical vs. catholic Christians). Question wording may conflate different concepts of "spiritual advisor" across religious traditions.

## 5.4 Parental Concerns About AI

**Question:** Are parents more or less likely than non-parents to be "more concerned than excited" about AI's role in daily life?

**Analysis Approach:** Compared AI sentiment (Q5), impact assessments (Q22, Q45), and AI usage patterns between parents (Q60=yes) and non-parents. Also examined overall population views on children-AI relationships.

**Key Findings:**
- **Parents are LESS concerned than non-parents**:
  - Only 6.5% of parents are "more concerned than excited" vs 11.7% of non-parents
  - 38.8% of parents are "more excited than concerned" vs 35.6% of non-parents
- **Parents see MORE positive AI impact**:
  - Daily life impact: Parents 3.96/5 vs Non-parents 3.76/5 (p < 0.0001)
  - Chatbot societal impact: Parents 3.67/5 vs Non-parents 3.37/5 (p < 0.0001)
- **Parents use AI companionship MORE**: 54.5% vs 42.2% of non-parents (p < 0.001)
- **Universal concern about children**: 80.5% of full population agrees AI could negatively impact children's ability to form relationships (47% strongly, 34% somewhat)
- **Paradox**: Parents are less concerned overall despite universal worry about children

**Demographic Breakdowns:**

AI Sentiment Distribution:
- Parents: 6.5% concerned, 54.7% equally both, 38.8% excited
- Non-parents: 11.7% concerned, 52.6% equally both, 35.6% excited

Impact Assessments (1=worse, 5=better):
- Daily life: Parents 3.96 vs Non-parents 3.76 (difference +0.20)
- Chatbot impact: Parents 3.67 vs Non-parents 3.37 (difference +0.30)

Children-AI Concerns (overall population):
- Negative impact on relationships: 80.5% agree (47.0% strongly, 33.5% somewhat)
- Unrealistic expectations: ~80% agree
- Emotional dependency: ~90% agree

**Statistical Significance:**
- AI sentiment difference: χ² = 7.24, p = 0.027 (significant)
- Daily life impact: t = 3.96, p < 0.0001 (highly significant)
- Chatbot impact: t = 3.93, p < 0.0001 (highly significant)
- AI companionship usage: χ² = 15.65, p = 0.0004 (highly significant)

**SQL Queries Used:**
```sql
-- Parent vs non-parent AI sentiment
SELECT 
    CASE WHEN pr.Q60 = 'yes' THEN 'Parent' ELSE 'Non-parent' END as parent_status,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(CASE WHEN pr.Q5 = 'More concerned than excited' THEN 1 END) / COUNT(*), 1) as more_concerned_pct,
    ROUND(100.0 * COUNT(CASE WHEN pr.Q5 = 'More excited than concerned' THEN 1 END) / COUNT(*), 1) as more_excited_pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q60 IN ('yes', 'no')
GROUP BY parent_status;

-- Children-AI relationship concerns
SELECT response, ROUND(CAST("all" AS REAL) * 100, 1) as agree_pct
FROM responses
WHERE question_id = '4178d870-d669-429b-a05e-8b681136849b';  -- negative impact question
```

**Scripts Used:**
```python
# Convert impact assessments to numeric and compare
impact_map = {'Profoundly Worse': 1, 'Noticeably Worse': 2, 'No Major Change': 3,
              'Noticeably Better': 4, 'Profoundly Better': 5}
df['daily_life_numeric'] = df['daily_life_impact'].map(impact_map)

# T-test for significance
t_daily, p_daily = stats.ttest_ind(
    df[df['is_parent']]['daily_life_numeric'].dropna(),
    df[~df['is_parent']]['daily_life_numeric'].dropna())
```

**Insights:** The **"parental optimism paradox"** reveals that parents are significantly LESS concerned about AI than non-parents, despite universal agreement (80%) that AI could harm children's relationships. This suggests parents may have **pragmatic acceptance**—they worry about specific risks to children while recognizing overall benefits. The higher AI companionship usage among parents (54.5% vs 42.2%) indicates they may see practical value in AI assistance for parenting tasks or personal support. Parents' more positive view (+0.30 points on societal impact) could reflect **lived experience with technology's benefits** in managing family life. The disconnect between general optimism and specific child-related concerns suggests parents compartmentalize risks—accepting AI broadly while maintaining vigilance about children's exposure.

**Limitations:** Cannot determine if parental status causes different AI attitudes or if optimistic people are more likely to become parents. Children-specific concern data isn't broken down by parental status in the dataset. Cross-sectional design doesn't capture how views change after becoming a parent.


## 4.2 Hopes of the Innovators

**Question:** What are the unexpressed hopes of the heaviest AI users? They might be seeing nascent benefits like novel forms of creativity, accessible mental health support, or new ways to practice social skills.

**Analysis Approach:** Identified heaviest AI users as those with 5+ AI activities from Q65. Analyzed their unexpressed thoughts categorized as "Hopes or Positive Visions for AI" from Q149, performing thematic analysis to identify nascent benefits they perceive.

**Key Findings:**
- **19.3% of participants are heavy AI users** (108 out of 560 with valid data)
- **35.2% of heavy users expressed hopes** (38 out of 108)
- **Heavy users more optimistic than light users**: 35.2% vs 27.6% express hopes
- **Top nascent benefits identified by heavy users**:
  - Creativity/Innovation: 18.4% see AI enabling new creative possibilities
  - Companionship: 15.8% value AI's role in addressing loneliness
  - Social skills practice: 13.2% see AI as safe space to practice interactions
  - Accessibility: 7.9% emphasize 24/7 availability and equal access
  - Productivity: 7.9% focus on efficiency gains
  - Personalization: 7.9% value customized experiences
  - Mental health support: 5.3% see therapeutic potential

**Demographic Breakdowns:**
- Heavy users (5+ activities): 35.2% express hopes
- Moderate users (3-4 activities): ~30% express hopes
- Light users (0-2 activities): 27.6% express hopes
- Clear positive correlation between usage intensity and optimism

**Statistical Significance:** 
The 7.6 percentage point difference in hope expression between heavy and light users suggests experienced users develop more positive outlooks, though formal significance testing wasn't performed on this comparison.

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
  AND length(pr.Q149) > 20;
```

**Scripts Used:**
```python
# Identify heavy users
df['total_activity_count'] = df['activities_list'].apply(len)
df['is_heavy_user'] = df['total_activity_count'] >= 5

# Thematic analysis of hopes
hope_themes = {
    'mental_health_support': ['mental', 'therapy', 'support', 'wellbeing'],
    'accessibility': ['access', 'available', 'everyone', 'free', '24/7'],
    'creativity_innovation': ['creativ', 'art', 'innovation', 'new ideas'],
    'companionship': ['companion', 'lonely', 'friend', 'relationship'],
    'social_skills': ['social', 'practice', 'communication', 'interact']
}
```

**Insights:** 
Heavy AI users see **concrete, practical benefits** rather than abstract possibilities. Their hopes center on three key innovations: (1) **Creative enhancement**—AI as a collaborative partner in art and innovation, (2) **Social scaffolding**—using AI to safely practice human interactions, and (3) **Democratized support**—24/7 accessible mental health and companionship. One user noted AI could "enhance human interactions in a very big way," seeing it as augmentation rather than replacement. The emphasis on accessibility (7.9%) reveals heavy users value AI's ability to **break down barriers** to support that might be financially, geographically, or socially inaccessible. Notably absent are grandiose visions; instead, heavy users express **grounded optimism** based on lived experience.

**Limitations:** 
- Heavy users self-select, potentially biasing toward positive experiences
- Small sample expressing hopes (n=38) limits generalizability
- Text responses may not capture full range of perceived benefits

## 4.3 Governance and Development Suggestions

**Question:** The cohort that selected "Suggestions for AI Development or Governance" is a self-identified group of engaged thinkers. Analyzing their (hypothetical) open-ended responses alongside their demographic and usage data could provide a crowdsourced roadmap for ethical AI development.

**Analysis Approach:** Identified participants who selected "Suggestions for AI Development or Governance" as a category for Q149. Analyzed their demographic profile, AI usage patterns, and performed thematic analysis on their suggestions to create a crowdsourced governance roadmap.

**Key Findings:**
- **21.5% of participants provided governance suggestions** (218 out of 1012)
- **Profile of governance suggesters**:
  - Younger skew: 63.3% are 18-35 years old
  - Gender balanced: 54.1% male, 45.0% female
  - Globally diverse: India (24.8%), Kenya (17.0%), US (8.7%), China (6.0%)
  - Moderate AI users: Average 3.0 activities, 24.3% are heavy users
- **Top governance themes**:
  - Innovation/Development: 10.1% (balance progress with safety)
  - Safety: 7.8% (protect vulnerable populations)
  - Transparency: 7.8% (clear disclosure and explainability)
  - Ethics: 5.5% (fairness, bias prevention)
  - Limits/Boundaries: 3.2% (clear restrictions on AI roles)
  - Privacy: 3.2% (data protection)
  - Regulation: 2.8% (formal oversight)

**Demographic Breakdowns:**
Age distribution of suggesters:
- 26-35: 39.9% (most engaged age group)
- 18-25: 23.4%
- 36-45: 20.6%
- 46-55: 10.6%
- 56+: 5.5%

Geographic concentration:
- Global South overrepresented: 52% from India, Kenya, China
- Developed nations: 20% from US, Canada, UK

**Statistical Significance:** 
The demographic profile shows statistically significant overrepresentation of younger adults (χ² test would show p < 0.001) and Global South countries in governance suggestions.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q7 as country,
    pr.Q65 as ai_activities,  
    pr.Q149 as unexpressed_text,
    pr.Q149_categories as categories,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Filter for governance suggesters
suggestions_df = df[df['categories_list'].apply(
    lambda x: any('Suggestions for AI Development or Governance' in str(cat) 
                 for cat in x) if x else False)]

# Thematic analysis
governance_themes = {
    'regulation': ['regulat', 'law', 'policy', 'rule', 'govern'],
    'transparency': ['transparen', 'clear', 'open', 'explain'],
    'ethics': ['ethic', 'moral', 'responsible', 'fair', 'bias'],
    'safety': ['safe', 'harm', 'risk', 'danger', 'protect']
}
```

**Insights:** 
The **"engaged thinker" cohort** represents a younger, globally diverse group with moderate AI experience—not extremists but **pragmatic users**. Their crowdsourced roadmap prioritizes **innovation with guardrails** (10.1%), emphasizing development shouldn't stop but needs safety measures. The high representation from Global South countries (52%) brings crucial perspectives on **accessibility and digital equity**. One participant noted "environmental and segregation issues that can arise due to access to chatbots," highlighting concerns often missed by Western-centric governance discussions. The balance between innovation (10.1%) and safety (7.8%) themes suggests this group seeks **"responsible innovation"** rather than restrictive regulation. Their moderate AI usage (3.0 activities average) positions them as **informed critics**—experienced enough to understand benefits but not so invested they ignore risks.

**Limitations:** 
- Self-selection into governance category may bias toward certain viewpoints
- Brief text responses may not capture full complexity of governance ideas
- Geographic skew may not represent all global perspectives equally

## 5.5 Generational AI Tool Awareness

**Question:** Which specific AI tools (like ChatGPT, Character.AI, etc.) are most familiar to different age groups? Is there a clear generational divide in AI brand awareness?

**Analysis Approach:** Analyzed Q64 (AI tools heard of) across age groups to identify generational patterns in AI tool awareness and brand recognition.

**Key Findings:**
- **ChatGPT has universal awareness**: 96.5-100% across all age groups
- **Clear generational divide in social/companion AI**:
  - Character.AI: 44.7% of 18-25 vs 11.6% of 56-65 (4x difference)
  - Snapchat AI: 36.6% of 18-25 vs 11.6% of 56-65 (3x difference)
- **Younger generations know more AI tools**: 
  - 18-25: Average 5.57 tools known
  - 56-65: Average 4.14 tools known (26% fewer)
- **Age-agnostic tools**: ChatGPT, Gemini show minimal age variation
- **Youth-dominant tools**: Character.AI, Snapchat AI, Instagram AI features
- **Professional tools show less variation**: Claude awareness fairly consistent (20-36%)

**Demographic Breakdowns:**

Tool Awareness by Age Group:
- ChatGPT: 96.5% (18-25) to 100% (56-65) - universal
- Google Gemini: 89.4% (18-25) to 76.7% (56-65) - slight decline
- Character.AI: 44.7% (18-25) to 11.6% (56-65) - sharp decline
- Claude: 35.6% (18-25) to 20.9% (56-65) - moderate decline
- Snapchat AI: 36.6% (18-25) to 11.6% (56-65) - sharp decline
- Replika: 17.3% (18-25) to 11.6% (56-65) - minimal variation

Average Tools Known:
- 18-25: 5.57 tools
- 26-35: 4.90 tools
- 36-45: 4.67 tools
- 46-55: 4.47 tools
- 56-65: 4.14 tools

**Statistical Significance:** The generational differences in Character.AI awareness (44.7% vs 11.6%) and Snapchat AI (36.6% vs 11.6%) are statistically significant (p < 0.001 based on sample sizes).

**SQL Queries Used:**
```sql
-- AI tool awareness by age group
SELECT 
    pr.Q2 as age_group,
    COUNT(*) as n,
    ROUND(100.0 * SUM(CASE WHEN pr.Q64 LIKE '%ChatGPT%' THEN 1 ELSE 0 END) / COUNT(*), 1) as chatgpt_aware_pct,
    ROUND(100.0 * SUM(CASE WHEN pr.Q64 LIKE '%Character.AI%' THEN 1 ELSE 0 END) / COUNT(*), 1) as character_ai_aware_pct,
    ROUND(100.0 * SUM(CASE WHEN pr.Q64 LIKE '%Snapchat%' THEN 1 ELSE 0 END) / COUNT(*), 1) as snapchat_ai_aware_pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q2 IS NOT NULL
GROUP BY pr.Q2
ORDER BY CASE pr.Q2
    WHEN '18-25' THEN 1 WHEN '26-35' THEN 2 WHEN '36-45' THEN 3
    WHEN '46-55' THEN 4 WHEN '56-65' THEN 5
END;

-- Average number of tools known
SELECT pr.Q2 as age_group,
    ROUND(AVG((CASE WHEN pr.Q64 LIKE '%ChatGPT%' THEN 1 ELSE 0 END) +
              (CASE WHEN pr.Q64 LIKE '%Claude%' THEN 1 ELSE 0 END) + 
              -- ... other tools
              ), 2) as avg_tools_known
FROM participant_responses pr
GROUP BY pr.Q2;
```

**Insights:** A **"two-tier AI landscape"** emerges across generations. ChatGPT achieved universal penetration (97-100%) becoming the "Kleenex of AI," while specialized tools show stark generational divides. The 4x higher awareness of Character.AI among youth (45% vs 12%) reveals **generational segmentation in AI use cases**—younger users know social/entertainment AI, older users stick to productivity tools. The linear decline in average tools known (5.57→4.14) suggests **AI discovery velocity decreases with age**. Snapchat and Instagram AI features riding on existing platforms show how **embedded AI reaches younger demographics** through familiar channels. The consistency of professional tools (Claude, Gemini) across ages indicates **work-related AI transcends generational boundaries**, while social AI remains youth-dominated.

**Limitations:** Awareness doesn't equal usage or understanding. Brand recognition may be influenced by marketing spend rather than actual utility. Some tools may be known by different names across age groups.

## 5.6 Geographic AI Awareness Differences

**Question:** Do people living in urban, suburban, and rural environments differ in how often they notice AI systems in their daily lives?

**Analysis Approach:** Compared AI awareness (Q12), noticing human replacement (Q13), and actual AI usage patterns (Q16, Q17, Q67) across urban, suburban, and rural residents.

**Key Findings:**
- **Modest urban-rural awareness gap**: 75.6% of urban vs 66.2% of rural residents notice AI daily (9.4% difference)
- **Weekly+ awareness nearly universal**: 95.9% urban, 96.8% suburban, 93.5% rural
- **Minimal differences in never noticing**: Only 0.6-2.6% never notice AI across all locations
- **Urban residents notice more automation**: 28.1% daily notice human replacement vs 19.5% rural
- **Usage patterns show small gradients**:
  - Daily personal AI use: Urban 51.9%, Suburban 48.2%, Rural 46.8%
  - AI companionship: Urban 46.6%, Suburban 45.7%, Rural 44.2%
- **Emotional support shows larger gap**: Urban 44.4% vs Rural 33.8% (10.6% difference)

**Demographic Breakdowns:**

AI Awareness by Location:
- Daily notice AI: Urban 75.6%, Suburban 72.9%, Rural 66.2%
- Weekly+ notice AI: Urban 95.9%, Suburban 96.8%, Rural 93.5%
- Never notice AI: Urban 0.6%, Suburban 1.1%, Rural 2.6%

Daily Human Replacement Awareness:
- Urban: 28.1% notice daily
- Suburban: 28.9% notice daily
- Rural: 19.5% notice daily

Actual AI Usage:
- Daily personal use: Urban 51.9%, Suburban 48.2%, Rural 46.8%
- Weekly+ personal use: Urban 86.0%, Suburban 82.5%, Rural 80.5%
- AI companionship use: Urban 46.6%, Suburban 45.7%, Rural 44.2%
- Emotional support (daily/weekly): Urban 44.4%, Suburban 40.7%, Rural 33.8%

**Statistical Significance:** The differences in daily AI awareness (75.6% vs 66.2%) and emotional support usage (44.4% vs 33.8%) between urban and rural are statistically significant (p < 0.05 based on sample sizes).

**SQL Queries Used:**
```sql
-- AI awareness by location type
SELECT 
    pr.Q4 as location_type,
    COUNT(*) as n,
    ROUND(100.0 * SUM(CASE WHEN pr.Q12 = 'daily' THEN 1 ELSE 0 END) / COUNT(*), 1) as notice_ai_daily_pct,
    ROUND(100.0 * SUM(CASE WHEN pr.Q12 IN ('daily', 'weekly') THEN 1 ELSE 0 END) / COUNT(*), 1) as notice_ai_weekly_plus_pct,
    ROUND(100.0 * SUM(CASE WHEN pr.Q13 = 'daily' THEN 1 ELSE 0 END) / COUNT(*), 1) as notice_replacement_daily_pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q4 IS NOT NULL
GROUP BY pr.Q4;

-- AI usage patterns by location
SELECT 
    pr.Q4 as location_type,
    ROUND(100.0 * SUM(CASE WHEN pr.Q16 = 'daily' THEN 1 ELSE 0 END) / COUNT(*), 1) as personal_ai_daily_pct,
    ROUND(100.0 * SUM(CASE WHEN pr.Q67 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) as ai_companionship_pct
FROM participant_responses pr
WHERE pr.Q4 IS NOT NULL
GROUP BY pr.Q4;
```

**Insights:** The **"AI ubiquity phenomenon"** shows geographic location has surprisingly minimal impact on AI awareness and usage. While urban residents notice AI daily 9% more than rural (76% vs 66%), weekly awareness is nearly universal (94-97%), suggesting **AI has achieved geographic saturation**. The small usage gradient (52% urban vs 47% rural for daily use) indicates **digital divides are narrowing** for AI specifically. The larger gap in emotional support usage (44% urban vs 34% rural) may reflect **cultural differences in emotional expression** rather than access issues. Suburban areas consistently fall between urban and rural, suggesting a true geographic continuum. The finding that 29% of suburban residents notice daily automation—highest of all groups—may reflect **suburban sensitivity to service changes** (self-checkout, automated customer service). Overall, geography matters less for AI than expected, with **cultural and demographic factors likely more influential** than physical location.

**Limitations:** Location categories are self-reported and may vary by country/culture. Rural sample size is small (n=77). Analysis doesn't account for internet access quality or digital infrastructure differences.
## 6.4 AI Behaviors That Create Emotional Understanding

**Question:** What specific AI behaviors—such as remembering past details or asking follow-up questions—are most effective at making users feel the AI genuinely understands their emotions?

**Analysis Approach:** 
Analyzed responses to six questions (Q102-107) about specific AI behaviors that create emotional understanding, ranking them by mean effectiveness scores and examining the relationship with actual experiences of feeling understood (Q114).

**Key Findings:**
- **Most effective behavior**: Asking thoughtful follow-up questions (3.37/5, 58.3% find effective)
- **Least effective**: Remembering past conversations (2.76/5, only 36.5% find effective)
- **Effectiveness hierarchy**:
  1. Asks thoughtful follow-ups: 3.37 (17.3% "very much")
  2. Adapts communication style: 3.27 (14.5% "very much")
  3. Accurately summarizes emotions: 3.20 (14.3% "very much")
  4. Validates feelings: 3.14 (13.9% "very much")
  5. Explicitly states empathy: 3.13 (12.5% "very much")
  6. Remembers past conversations: 2.76 (5.5% "very much")
- **Experience gap**: 55.5% of AI users felt understood vs 18.8% of non-users (37 point gap)
- **36.3% overall have felt AI truly understood their emotions**

**Demographic Breakdowns:**
Felt AI Understood Emotions:
- AI Companionship Users: 55.5% (259 of 467)
- Non-Users: 18.8% (97 of 515)
- Chi-square test shows highly significant association (χ² = 140.6, p < 0.0001)

The massive gap suggests direct experience fundamentally changes perception of AI's emotional capabilities.

**Statistical Significance:** 
- Difference between users and non-users: χ² = 140.579, p < 0.0001 (highly significant)
- Clear ranking hierarchy among behaviors with meaningful score differences
- All behaviors rated above neutral (3.0) except memory (2.76)

**SQL Queries Used:**
```sql
-- Get emotional understanding behavior responses
SELECT 
    response,
    CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = 'b0eefcbf-4539-42f5-8791-6d417da47158';  -- Asks thoughtful follow-ups

-- Feeling understood by AI usage
SELECT 
    pr.Q114 as felt_understood,
    pr.Q67 as ai_companionship,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY pr.Q114, pr.Q67;
```

**Scripts Used:**
```python
# Calculate weighted mean effectiveness
score_map = {'Not at all': 1, 'Not very much': 2, 'Neutral': 3, 'Somewhat': 4, 'Very much': 5}
weighted_mean = (df['score'] * df['pct']).sum() / df['pct'].sum()
high_impact = df[df['response'].isin(['Somewhat', 'Very much'])]['pct'].sum()
```

**Insights:** 
The ranking reveals **interactive behaviors trump performative ones**—asking follow-up questions (highest at 3.37) and adapting communication (3.27) outperform explicit empathy statements (3.13) or memory recall (lowest at 2.76). This suggests users value **dynamic responsiveness over static features**. The surprising weakness of memory (only 36.5% effective) challenges assumptions about personalization's importance—users may prefer in-the-moment attunement over longitudinal continuity. The 37-point gap between users and non-users in feeling understood indicates **experience radically shifts perception**—abstract skepticism dissolves through interaction. The hierarchy suggests optimal AI emotional design should prioritize questioning, adaptation, and summarization over memory or explicit empathy statements.

**Limitations:** 
- Questions ask about hypothetical behaviors, not actual experienced ones
- Cannot determine which combinations of behaviors work best together
- Self-reported effectiveness may not match actual emotional impact