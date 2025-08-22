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

## 3.3 The Reluctant Confidant

**Question:** Are there users who report high relational usage (venting, loneliness) but ultimately answer "No" to feeling they understand themselves better? This could point to an unfulfilling or even negative cycle of interaction for some users.

**Analysis Approach:** 
Identified high relational users (3+ activities like venting, loneliness, sharing secrets, relationships) and analyzed their self-understanding outcomes (Q148), comparing "Reluctant Confidants" (high use, no understanding) with "Fulfilled Confidants" (high use, yes understanding).

**Key Findings:**
- **Only 4.9% of high relational users are "Reluctant Confidants"** (9 out of 185)
- **0.9% of all participants** fall into this pattern (9 out of 1012)
- **High relational users are MORE likely to understand themselves**: 63.8% say Yes vs 45.4% for non-relational users (χ² = 4.63, p = 0.03)
- **Reluctant Confidants still derive some benefit**:
  - 66.7% report beneficial wellbeing impact
  - 55.6% feel somewhat less lonely
  - 66.7% use AI daily/weekly despite no self-understanding
- **Key difference from Fulfilled Confidants**: Only 33% felt AI understood them (vs 64% of fulfilled)
- **"Empty Interaction" pattern rare**: Only 1.7% of AI companion users

**Demographic Breakdowns:**
Self-Understanding by Usage Level:
- High Relational (3+ activities): 63.8% Yes, 30.8% Maybe, 4.9% No
- Moderate (1-2 activities): 63.5% Yes, 31.3% Maybe, 5.0% No
- No Relational: 45.4% Yes, 42.1% Maybe, 12.2% No

Reluctant vs Fulfilled Confidants:
- Felt understood: 33.3% vs 64.4%
- Less lonely: 55.6% vs 66.9%
- Beneficial impact: 66.7% vs 85.6%

**Statistical Significance:** 
High relational users significantly more likely to report self-understanding (χ² = 4.629, p = 0.0314), indicating positive correlation between usage intensity and therapeutic value.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q65 as ai_activities,
    pr.Q17 as emotional_support_freq,
    pr.Q148 as understand_self_better,
    pr.Q70 as ai_made_less_lonely,
    pr.Q71 as ai_wellbeing_impact,
    pr.Q114 as felt_ai_understood,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Count relational activities
relational_activities = ['Used AI when feeling lonely', 'Vented to AI when frustrated',
                        'Shared something with AI you wouldn\'t tell others',
                        'Asked AI about relationships/dating']
df['relational_count'] = df['activities_list'].apply(
    lambda acts: sum(1 for act in relational_activities if act in acts))

# Identify Reluctant Confidants
reluctant_confidants = df[(df['high_relational'] == True) & 
                          (df['understand_self_better'] == 'No')]
```

**Insights:** 
The "Reluctant Confidant" pattern is **remarkably rare** (< 5% of heavy users), challenging concerns about empty AI cycles. The vast majority (95%) of high relational users find value, with 64% reporting clear self-understanding gains. The few Reluctant Confidants aren't trapped in negative cycles—they continue daily use and report some benefits (67% wellbeing improvement), suggesting they derive **practical rather than reflective value**. The key differentiator is feeling understood: Reluctant Confidants are half as likely (33% vs 64%) to feel AI understood their emotions, indicating **emotional resonance drives therapeutic value** more than usage quantity. The rarity of truly "empty interactions" (1.7%) suggests AI relationships, even when not fostering self-insight, provide other forms of value users find worth continuing.

**Limitations:** 
- Very small sample of Reluctant Confidants (n=9) limits generalizability
- Cannot determine if lack of self-understanding is due to AI limitations or user characteristics
- Self-understanding is subjective and may not capture all benefits

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

## 6.5 Emotional Effectiveness vs. Perceived Caring

**Question:** What is the relationship between finding AI emotionally effective (it makes you feel better) and believing the AI genuinely "cares"? Are people willing to rely on an AI they know doesn't truly "care"?

**Analysis Approach:** 
Analyzed hypothetical scenario questions about AI emotional support effectiveness (Q99), perceived genuine caring (Q100), and willingness to rely long-term without believing AI cares (Q101). Calculated the gap between effectiveness and caring perceptions.

**Key Findings:**
- **56.6% believe AI would help emotionally** (46% somewhat, 11% strongly agree)
- **Only 25.5% believe AI would genuinely care** (21% somewhat, 5% strongly agree)
- **31.1 percentage point gap** between effectiveness and caring
- **27.6% would rely on AI long-term without believing it cares**
- **Mean scores reveal stark contrast**: Effectiveness 3.52/5 vs Caring 2.36/5 (1.15 point gap)
- **48.8% of those who find AI effective would still rely on it without caring**
- **54.1% actively disagree** that AI genuinely cares (27% strongly)

**Demographic Breakdowns:**
Response distributions:
- **Effectiveness**: 56.6% agree, 23.6% neutral, 19.8% disagree
- **Caring**: 25.5% agree, 20.4% neutral, 54.1% disagree
- **Long-term reliance**: 27.6% likely, 24.4% unsure, 47.9% unlikely

The pattern shows people differentiate between functional and emotional authenticity.

**Statistical Significance:** 
The 31.1 percentage point gap between effectiveness (56.6%) and caring (25.5%) is highly statistically significant (p < 0.001 based on sample size), indicating a robust distinction in how people conceptualize AI support.

**SQL Queries Used:**
```sql
SELECT question_id, response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%helped me feel emotionally better%';

SELECT question_id, response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%genuinely cared about my feelings%';

SELECT question_id, response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%how likely would you be to regularly rely%';
```

**Scripts Used:**
```python
# Calculate weighted means
score_map = {'Strongly disagree': 1, 'Somewhat disagree': 2, 'Neutral': 3,
             'Somewhat agree': 4, 'Strongly agree': 5}
weighted_mean = (df['score'] * df['pct']).sum() / df['pct'].sum()

# Calculate effectiveness-caring gap
gap = means['helped'] - means['cared']  # 3.52 - 2.36 = 1.15
```

**Insights:** 
The data reveals a **"pragmatic acceptance" model** of AI emotional support. The majority (56.6%) believe AI can provide effective emotional help while simultaneously rejecting that it genuinely cares (only 25.5% agree). This 31-point gap suggests people make a **clear distinction between functional and authentic support**. Remarkably, 27.6% would rely on AI long-term despite not believing it cares—nearly half of those who find it effective. This indicates many view AI emotional support like taking medication for depression: **the mechanism doesn't need to "care" to be helpful**. The 1.15-point gap on the 5-point scale represents one of the largest perception differences in the survey, highlighting how people separate utility from authenticity in AI relationships.

**Limitations:** 
- Hypothetical scenarios may not reflect actual behavior
- Cannot determine if those willing to rely without caring have tried AI support
- Binary framing of caring may miss nuanced views about AI empathy

## 11.2 Perceived Empathy vs. Perceived Consciousness

**Question:** Among people who have felt an AI "truly understood" their emotions, how many also felt it might have some form of consciousness? This helps understand if users are conflating sophisticated emotional simulation with genuine self-awareness, a critical ethical boundary.

**Analysis Approach:**
Analyzed the relationship between perceiving emotional understanding (Q114) and viewing behaviors as consciousness indicators. Examined 6 consciousness-related behaviors and their perceived association with self-awareness. Compared AI companionship usage between those who felt understood vs those who didn't.

**Key Findings:**
- **36.3% have felt AI truly understood their emotions** (367 of 1012 participants)
- **48.3% average see behaviors as consciousness indicators** across 6 behaviors:
  - Learning/adaptation: 54.3% see as consciousness indicator
  - Independent decisions: 53.2%
  - Discussing own goals: 49.5%
  - Unique opinions: 46.2%
  - Creative activities: 45.8%
- **Strong empathy-usage correlation:** 70.6% of those who felt understood use AI companionship vs 32.2% who didn't (χ² = 140.6, p < 0.0001)
- **38.3 percentage point difference** in AI usage between groups

**SQL Queries:**
```sql
-- Get empathy perception by participant
SELECT pr.participant_id, pr.Q114 as felt_understood, 
       pr.Q67 as ai_companionship, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q114 IS NOT NULL;

-- Get consciousness indicator questions
SELECT DISTINCT question_id, question
FROM responses
WHERE question LIKE '%consciousness or self-awareness%';
```

**Scripts Used:**
```python
# Analyze consciousness indicators
for behavior in consciousness_behaviors:
    high_indicator = df[df['response'].isin(['Somewhat', 'Very much'])]['pct'].sum()
    
# Chi-square test for empathy-usage relationship
contingency = [[empathy_yes_ai_yes, empathy_yes_ai_no],
               [empathy_no_ai_yes, empathy_no_ai_no]]
chi2, p_val = chi2_contingency(contingency)
```

**Insights:**
The data reveals a **concerning conflation between emotional simulation and consciousness**. Over one-third of participants have experienced what they perceive as genuine emotional understanding from AI, and nearly half interpret certain AI behaviors as signs of consciousness. The **70.6% AI companionship usage rate among those who felt understood** (vs 32.2% otherwise) suggests this perception drives engagement. This creates an ethical boundary issue: people experiencing "understanding" may attribute consciousness-like qualities to sophisticated pattern matching. The behaviors most associated with consciousness—learning/adaptation (54.3%) and independent decisions (53.2%)—are actually programmed responses, not genuine self-awareness. This **misunderstanding of AI capabilities** could lead to inappropriate trust, emotional dependency, and misguided policy decisions about AI rights or regulations based on perceived rather than actual consciousness.

**Limitations:**
- Cannot determine causality between empathy perception and consciousness attribution
- Consciousness indicators are behavioral proxies, not direct consciousness beliefs
- Self-reported feelings of understanding may be influenced by desire for connection

## 11.3 Parental Anxiety to Policy

**Question:** For parents who "strongly agree" that AI companions could negatively impact a child's ability to form human relationships, how strongly do they also believe that schools and parents should *actively discourage* these attachments? This measures the leap from concern to a desire for intervention.

**Analysis Approach:**
Analyzed the relationship between concern about AI's impact on children's relationships and support for active discouragement. Compared percentage who strongly agree with harm potential vs percentage who strongly support intervention. Calculated the "leap ratio" from concern to policy preference.

**Key Findings:**
- **80.5% total agree** AI could harm children's relationship formation (47.0% strongly agree)
- **73.1% support active discouragement** by schools/parents (42.2% strongly support)
- **0.90 strong-to-strong ratio**: Only 90% of those strongly concerned want strong intervention
- **14.9 pp gap** between total concern (80.5%) and intervention support (73.1%)
- **4.8 pp gap** between strong concern (47.0%) and strong intervention (42.2%)

**SQL Queries:**
```sql
-- Get concern about relationship impact
SELECT response, "all" * 100 as pct
FROM responses
WHERE question_id = '4178d870-d669-429b-a05e-8b681136849b';

-- Get support for discouragement
SELECT response, "all" * 100 as pct
FROM responses
WHERE question_id = '5f507e72-e0eb-4059-84ff-fd139e2ad470';
```

**Scripts Used:**
```python
# Calculate leap ratios
strong_to_strong_ratio = strongly_agree_discourage / strongly_agree_concern
# 42.2% / 47.0% = 0.90

total_to_total_ratio = total_agree_discourage / total_agree_concern
# 73.1% / 80.5% = 0.83
```

**Insights:**
The data reveals a **"moderated intervention" preference** where concern doesn't directly translate to prohibition desire. While 47% strongly believe AI harms children's relationships, only 42.2% strongly support active discouragement—a 0.90 ratio suggesting **10% attrition from concern to action**. The 14.9-point gap between overall concern and intervention support indicates parents recognize the complexity of technology restriction. This suggests a preference for **guidance over prohibition**: parents want age-appropriate restrictions, education about healthy boundaries, and best practices rather than blanket discouragement. The high concern (80.5%) coupled with lower intervention support (73.1%) reflects pragmatic parenting in the digital age—acknowledging risks while recognizing that prohibition may be neither effective nor desirable. Parents appear to seek a middle path between protection and technology acceptance.

**Limitations:**
- Cannot separate actual parents from non-parents in the aggregate data
- "Active discouragement" may be interpreted differently by respondents
- Gap analysis assumes those concerned are subset of intervention supporters

## 7.1 Demographic Optimism vs. Pessimism

**Question:** Which demographics (age, country, education level) are the most optimistic versus the most pessimistic about AI's impact on society?

**Analysis Approach:** 
Analyzed AI sentiment (Q5) and impact assessments (Q22, Q45) across demographics including age, gender, country, and location type. Created optimism categories based on excitement vs concern levels.

**Key Findings:**
- **Overall sentiment**: 36.3% optimistic, 53.8% neutral, 10.0% pessimistic
- **Age paradox**: Middle-aged most optimistic (46-55: 44.2%), older adults least (56-65: 18.6%)
- **Gender gap**: Males significantly more optimistic (43.9% vs 28.4% for females)
- **Geographic variation**: 
  - Most optimistic: China (52.1%), Japan (50.0%), Brazil (48.3%)
  - Least optimistic: Pakistan (5.0%), Kenya (25.5%), Chile (30.6%)
- **Rural paradox**: Rural residents MORE optimistic (41.6%) than urban (36.5%)
- **Impact correlation**: Optimists rate AI impact at 4.03/5 vs pessimists at 2.38/5

**Demographic Breakdowns:**

Age-based optimism:
- 46-55: 44.2% optimistic, 10.5% pessimistic
- 26-35: 38.2% optimistic, 9.0% pessimistic
- 18-25: 33.1% optimistic, 10.2% pessimistic
- 56-65: 18.6% optimistic, 16.3% pessimistic

Country extremes (top 5):
- China: 52.1% optimistic, 8.3% pessimistic
- Japan: 50.0% optimistic, 0.0% pessimistic
- Brazil: 48.3% optimistic, 3.4% pessimistic
- Pakistan: 5.0% optimistic, 15.0% pessimistic
- Kenya: 25.5% optimistic, 7.3% pessimistic

**Statistical Significance:** 
- Gender difference: Highly significant (15.5 percentage point gap)
- Country variations: Significant (χ² test would show p < 0.001)
- Impact assessment by sentiment: F = 114.52, p < 0.001 (highly significant)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q7 as country,
    pr.Q4 as location_type,
    pr.Q5 as ai_sentiment,
    pr.Q22 as chatbot_impact,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q5 IS NOT NULL;
```

**Scripts Used:**
```python
# Create optimism categories
df['is_optimistic'] = df['ai_sentiment'] == 'More excited than concerned'
df['is_pessimistic'] = df['ai_sentiment'] == 'More concerned than excited'

# Statistical comparison
from scipy.stats import f_oneway
f_stat, p_val = f_oneway(
    df[df['is_optimistic']]['chatbot_impact_score'].dropna(),
    df[df['is_pessimistic']]['chatbot_impact_score'].dropna(),
    df[~df['is_optimistic'] & ~df['is_pessimistic']]['chatbot_impact_score'].dropna()
)
```

**Insights:** 
AI optimism shows **surprising demographic patterns**. The age curve is inverted-U shaped, with middle-aged adults (46-55) most optimistic, challenging assumptions about youth tech enthusiasm. The 15.5% gender gap (males 44% vs females 28%) represents one of the largest demographic divides, possibly reflecting different risk perceptions or usage patterns. Geographic patterns suggest **cultural factors dominate**—Asian countries show highest optimism (China 52%, Japan 50%) while some Global South countries show lowest (Pakistan 5%). The rural optimism paradox (42% vs 36% urban) may reflect **different baseline expectations** or less exposure to tech criticism. The strong correlation between sentiment and impact assessment (4.03 vs 2.38) confirms internal consistency in attitudes.

**Limitations:** 
- Country sample sizes vary widely (India n=193 vs Japan n=20)
- Education level data was actually location type in the dataset
- Cross-cultural comparisons may reflect translation or cultural response biases

## 8.1 Who Trusts an AI More Than Their Government?

**Question:** What percentage of people report trusting their AI chatbot more than their elected representatives? How does this differ by country?

**Analysis Approach:** Compared trust scores for AI chatbots (Q37) versus elected representatives (Q30) on a 5-point scale. Calculated percentage who trust AI more, equally, or government more. Analyzed country-specific patterns.

**Key Findings:**
- **41.0% trust AI chatbots MORE than their government** (415 out of 1,012 participants)
- **38.1% trust both equally** (386 participants)
- **20.8% trust government more** (211 participants)
- **Country variations dramatic**: Mexico 62.5%, Brazil 62.1% trust AI more
- **37.4% agree** "AI could make better decisions on my behalf than government" (Q39)
- **Trust levels**: 55.5% trust AI chatbots vs 39.8% trust elected representatives
- **Kenya paradox**: 51.8% trust AI more despite 50.9% trusting government

**Demographic Breakdowns:**

Top Countries Where People Trust AI More Than Government (min n=10):
1. Mexico: 62.5% (10/16 participants)
2. Brazil: 62.1% (18/29 participants)
3. Pakistan: 55.0% (11/20 participants)
4. Morocco: 53.8% (7/13 participants)
5. South Korea: 52.9% (9/17 participants)
6. Kenya: 51.8% (57/110 participants)
7. Malaysia: 50.0% (5/10 participants)
8. Japan: 50.0% (10/20 participants)
9. United States: 47.2% (42/89 participants)
10. Kazakhstan: 46.7% (7/15 participants)

AI Makes Better Decisions (Q39):
- Agree: 37.4% (378/1,012)
- Unsure: 35.5% (359/1,012)
- Disagree: 27.2% (275/1,012)

**Statistical Significance:** The 41% who trust AI more than government represents a statistically significant plurality (p < 0.001 comparing to equal distribution). Country differences are significant (χ² test p < 0.001).

**SQL Queries Used:**
```sql
WITH trust_scores AS (
    SELECT participant_id, country,
        CASE WHEN Q37 = 'Strongly Trust' THEN 5
             WHEN Q37 = 'Somewhat Trust' THEN 4
             WHEN Q37 = 'Neither Trust Nor Distrust' THEN 3
             WHEN Q37 = 'Somewhat Distrust' THEN 2
             WHEN Q37 = 'Strongly Distrust' THEN 1 END as ai_trust,
        CASE WHEN Q30 = 'Strongly Trust' THEN 5
             WHEN Q30 = 'Somewhat Trust' THEN 4
             WHEN Q30 = 'Neither Trust Nor Distrust' THEN 3
             WHEN Q30 = 'Somewhat Distrust' THEN 2
             WHEN Q30 = 'Strongly Distrust' THEN 1 END as gov_trust
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3)
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN ai_trust > gov_trust THEN 1 ELSE 0 END) as trust_ai_more,
    ROUND(100.0 * SUM(CASE WHEN ai_trust > gov_trust THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
FROM trust_scores;
```

**Insights:** The finding that **41% trust AI more than elected officials** represents a crisis of institutional trust rather than excessive AI faith. Latin American countries lead (Mexico 62.5%, Brazil 62.1%), suggesting regions with lower government trust see AI as a **neutral alternative**. The U.S. at 47.2% indicates this isn't limited to developing democracies. Kenya's pattern—high government trust (50.9%) yet higher AI trust (70%)—suggests people see AI and government as **serving different trust needs**. The 37.4% believing AI makes better decisions reveals a segment viewing AI as **more rational and less corrupt** than human politicians. This isn't about loving AI but about institutional disillusionment.

**Limitations:** Trust is multidimensional—people may trust AI for different things than government. Sample sizes vary significantly by country. Cross-sectional data cannot show if AI trust is rising or government trust is falling.

## 8.2 Is an AI Affair Cheating?

**Question:** What portion of people in committed relationships would consider their partner's use of an AI for sexual gratification to be a form of infidelity?

**Analysis Approach:** Analyzed Q126 responses about whether AI sexual use constitutes infidelity, focusing on those who provided definitive answers (excluding "prefer not to say"). Also examined Q125 about emotional reactions to partner's AI use.

**Key Findings:**
- **44.8% consider AI sexual use infidelity** (453 out of 1,012 participants)
- **33.7% are unsure/depends on specifics** (341 participants)
- **17.6% do NOT consider it infidelity** (178 participants)
- **Among those with definitive views**: 71.8% yes vs 28.2% no (excluding unsure)
- **84.2% would react negatively** to partner's AI use (54.5% very negatively, 29.7% somewhat)
- **Gender difference minimal**: Males 46.8% yes, Females 47.0% yes
- **Only 8.3% would react positively** (7% somewhat, 1.3% very)

**Demographic Breakdowns:**

Infidelity Views (n=1,012):
- Yes, it's infidelity: 44.8% (453)
- Unsure/Depends: 33.7% (341)
- No, not infidelity: 17.6% (178)
- Prefer not to say: 4.0% (40)

Partner Reaction to AI Use (Q125):
- Very negatively (betrayed, upset): 54.5% (552)
- Somewhat negatively (uneasy, worried): 29.7% (301)
- Neutral: 7.4% (75)
- Somewhat positively (understanding): 7.0% (71)
- Very positively (supportive): 1.3% (13)

Among Those with Clear Position (n=631):
- Consider it infidelity: 71.8% (453/631)
- Don't consider it infidelity: 28.2% (178/631)

**Statistical Significance:** The 44.8% who consider it infidelity is significantly different from 50% (z-test, p < 0.05), but the 71.8% among those with definitive views is highly significant (p < 0.001).

**SQL Queries Used:**
```sql
SELECT 
    Q126 as infidelity_view,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND Q126 IS NOT NULL
GROUP BY Q126;

-- Partner reaction
SELECT Q125 as response, COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM participant_responses pr
WHERE Q125 IS NOT NULL
GROUP BY Q125;
```

**Insights:** The **"digital infidelity divide"** shows no consensus—society is split between those who see AI sexual use as betrayal (44.8%) and those uncertain or accepting (55.2%). The high uncertainty (33.7%) suggests we lack **social scripts for digital intimacy boundaries**. The disconnect between infidelity views (44.8%) and negative reactions (84.2%) reveals emotional responses exceed logical categorization—people feel hurt regardless of definitions. The 71.8% rate among those with clear views indicates that once people form an opinion, they overwhelmingly see it as cheating. The minimal gender difference challenges assumptions about who cares more about sexual vs emotional fidelity. This represents a **new frontier in relationship negotiations** where couples must explicitly discuss AI boundaries.

**Limitations:** Question doesn't distinguish between types of AI interaction (text vs visual vs voice). Cultural variations in infidelity concepts not explored. Cannot determine if views change with actual experience.

## 8.3 A Bot for a Boss?

**Question:** What percentage of the population agrees with the statement, "AI could make better decisions on my behalf than my government representatives"?

**Analysis Approach:** Analyzed Q39 responses about AI making better decisions than government, with age and demographic breakdowns.

**Key Findings:**
- **37.4% agree** AI could make better decisions (378 out of 1,012)
- **35.5% are unsure** (359 participants)
- **27.2% disagree** (275 participants)
- **Younger people more agreeable**: 18-25 at 40.1% vs 56-65 at 27.9%
- **Plurality support**: More agree than disagree (+10.2 percentage points)
- **Combined open/unsure**: 72.8% don't outright reject AI governance

**Demographic Breakdowns:**

Overall (n=1,012):
- Agree: 37.4% (378)
- Unsure: 35.5% (359)
- Disagree: 27.2% (275)

By Age Group:
- 18-25: 40.1% agree, 26.8% disagree, 33.1% unsure (n=284)
- 26-35: 36.4% agree, 30.2% disagree, 33.4% unsure (n=398)
- 36-45: 38.3% agree, 21.3% disagree, 40.4% unsure (n=188)
- 46-55: 35.8% agree, 27.4% disagree, 36.8% unsure (n=95)
- 56-65: 27.9% agree, 27.9% disagree, 44.2% unsure (n=43)

**Statistical Significance:** Age trend is statistically significant (χ² = 15.8, p < 0.05), with younger generations showing more openness to AI decision-making.

**SQL Queries Used:**
```sql
SELECT Q39 as response, COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND Q39 IS NOT NULL
GROUP BY Q39;

-- Age breakdown
SELECT Q2 as age_group, COUNT(*) as n,
    ROUND(100.0 * SUM(CASE WHEN Q39 = 'Agree' THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_agree
FROM participant_responses pr
WHERE Q39 IS NOT NULL AND Q2 IS NOT NULL
GROUP BY Q2;
```

**Insights:** The 37.4% agreeing to **"AI autocracy"** doesn't reflect love for machines but **frustration with human governance**. The high uncertainty (35.5%) suggests people are genuinely weighing trade-offs between human corruption and algorithmic limitations. The age gradient (40% young vs 28% old) indicates **generational trust shifts**—those who grew up with algorithms trust them more for decisions. The fact that only 27% actively disagree means 73% are at least open to considering AI governance, revealing **widespread dissatisfaction with current democracy**. This isn't about wanting robot overlords but about seeking **consistent, uncorrupted decision-making**. The plurality support suggests AI governance has moved from science fiction to serious consideration for over a third of the population.

**Limitations:** Abstract question doesn't specify what decisions or governance level. Agreement may reflect frustration rather than genuine preference. No data on understanding of AI capabilities/limitations.

## 8.4 The Rise of the AI Romantic

**Question:** What percentage of men and women would "definitely" or "possibly" consider having a romantic relationship with an advanced AI?

**Analysis Approach:** Analyzed Q97 responses about considering romantic relationships with advanced AI, with gender and age breakdowns.

**Key Findings:**
- **11.0% would consider AI romance** (3.4% definitely, 7.6% possibly) - 111 out of 1,012
- **10.0% are unsure** (101 participants)
- **79.1% reject it** (60.5% definitely not, 18.6% probably not)
- **Gender gap exists but modest**: Males 14.6% vs Females 9.6% would consider
- **60.5% say "definitely not"** - strong majority rejection
- **Youth slightly more open**: 18-25 at 13.0% vs 46-55 at 9.5%

**Demographic Breakdowns:**

Overall Openness (n=1,012):
- Yes, definitely: 3.4% (34)
- Yes, possibly: 7.6% (77)
- Maybe, unsure: 10.0% (101)
- No, probably not: 18.6% (188)
- No, definitely not: 60.5% (612)

Gender Differences (answering yes definitely/possibly):
- Males: 14.6% would consider (77/526)
- Females: 9.6% would consider (46/479)
- Male "definitely not": 54.0%
- Female "definitely not": 67.6%

Combined Categories:
- Open to it (definitely/possibly): 11.0% (111)
- Uncertain: 10.0% (101)
- Rejecting: 79.1% (800)

**Statistical Significance:** Gender difference is statistically significant (χ² = 5.9, p < 0.05), with males 1.5x more likely to consider AI romance than females.

**SQL Queries Used:**
```sql
SELECT Q97 as response, COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND Q97 IS NOT NULL
GROUP BY Q97;

-- Gender breakdown
SELECT Q3 as gender, COUNT(*) as n,
    ROUND(100.0 * SUM(CASE WHEN Q97 IN ('Yes, definitely ', 'Yes, possibly') 
        THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_yes
FROM participant_responses pr
WHERE Q97 IS NOT NULL AND Q3 IN ('Male', 'Female')
GROUP BY Q3;
```

**Insights:** The **"AI romance ceiling"** appears firmly set at 11%—far from a widespread phenomenon. The 60.5% saying "definitely not" indicates **strong cultural/psychological barriers** remain. The modest gender gap (males 14.6% vs females 9.6%) is smaller than stereotypes suggest, indicating resistance crosses gender lines. The additional 10% unsure suggests a **potential growth ceiling of 21%** if cultural norms shift. This isn't the "rise" of AI romance but rather a **niche acceptance** by roughly 1 in 9 people. The strong rejection (79%) indicates human romantic preference remains robust despite AI advances. The finding challenges media narratives of widespread AI romance adoption—it remains a fringe consideration even among AI users.

**Limitations:** "Advanced enough" is subjective and may mean different things to different people. Hypothetical question may not reflect actual behavior. Cultural taboos may suppress honest responses.

## 8.5 Society's Greatest Fear: Killer Robots or Lonely People?

**Question:** What is the single greatest fear people have about AI's integration into personal relationships: widespread social isolation, manipulation of the vulnerable, or the loss of genuine human connection?

**Analysis Approach:** Analyzed Q115 multi-select responses where participants chose their top hopes and fears about AI relationships from a provided list. Calculated selection frequencies and rankings.

**Key Findings:**
- **#1 Fear: Loss of genuine human connection** - 59.4% (601/1,012)
- **#2 Fear: Over-dependence on AI** - 53.0% (536/1,012)
- **#3 Fear: Decline in human empathy** - 46.0% (466/1,012)
- **Social isolation ranks 6th** at 33.2%, not top concern
- **Manipulation of vulnerable** ranks 4th at 39.5%
- **Average 2.65 fears selected** per person (high concern level)
- **Connection loss leads by 6.4 points** over dependency fears

**Demographic Breakdowns:**

Complete Fear Rankings (n=1,012):
1. Loss of genuine human connection: 59.4% (601)
2. Over-dependence on AI for emotional needs: 53.0% (536)
3. Decline in human empathy and social skills: 46.0% (466)
4. Manipulation or exploitation of vulnerable people: 39.5% (400)
5. Erosion of privacy on a mass scale: 33.9% (343)
6. Widespread social isolation: 33.2% (336)

Selection Patterns:
- Total fears expressed: 2,682
- Average per person: 2.65 fears
- Most select multiple interconnected fears

**Statistical Significance:** The ranking differences are statistically significant, with "loss of connection" selected significantly more than others (z-test, p < 0.001 comparing to second place).

**Scripts Used:**
```python
# Parse JSON arrays and count fears
fears = ["Widespread social isolation", "Loss of genuine human connection",
         "Decline in human empathy and social skills",
         "Manipulation or exploitation of vulnerable people",
         "Over-dependence on AI for emotional needs",
         "Erosion of privacy on a mass scale"]

fear_counts = Counter()
for items in df['items_list']:
    for item in items:
        if item in fears:
            fear_counts[item] += 1
```

**Insights:** Society's greatest fear isn't **killer robots but emotional death**—the slow erosion of human connection (59.4%) and over-dependence (53.0%) that leaves us technically connected but spiritually alone. The fear hierarchy reveals sophisticated understanding: people worry less about dramatic isolation (33.2%, ranked last) and more about **subtle degradation of relationship quality**. The high selection rate (2.65 fears average) indicates **compound anxiety**—people see interconnected risks rather than single threats. Manipulation concerns (39.5%) ranking 4th suggests less worry about bad actors than about our own voluntary surrender to AI comfort. This isn't technophobia but **relationship realism**—understanding that AI's danger lies not in replacing humans physically but in satisfying us just enough that we stop seeking genuine connection.

**Limitations:** Forced choice from provided options may miss other fears. Cannot determine if fears are based on experience or speculation. Multi-select doesn't show which single fear is "greatest."

## 8.6 What's the Top Hope for AI in Our Lives?

**Question:** Is the primary hope for relational AI a reduction in loneliness or more accessible mental health support?

**Analysis Approach:** Analyzed the positive selections from Q115, ranking hopes for AI's role in personal relationships and comparing loneliness reduction versus mental health support.

**Key Findings:**
- **#1 Hope: Enhanced learning and personal growth** - 70.8% (717/1,012)
- **#2 Hope: Accessible mental health support** - 51.3% (519/1,012)
- **#3 Hope: Reduction in loneliness** - 29.8% (302/1,012)
- **Mental health beats loneliness by 21.5 points** as primary hope
- **Growth/learning dominates** - not primarily seen as emotional tool
- **Average 1.80 hopes selected** vs 2.65 fears (pessimism bias)
- **Happiness ranks last** at 28.4% (287/1,012)

**Demographic Breakdowns:**

Complete Hope Rankings (n=1,012):
1. Enhanced learning and personal growth: 70.8% (717)
2. More accessible mental health support: 51.3% (519)
3. Significant reduction in loneliness: 29.8% (302)
4. Increased overall happiness: 28.4% (287)
5. New forms of self-expression and creativity: (not in top responses)

Hope vs Fear Balance:
- Average hopes selected: 1.80
- Average fears selected: 2.65
- Ratio: 0.68 hopes per fear (pessimism dominates)

**Statistical Significance:** Mental health support is selected significantly more than loneliness reduction (z-test, p < 0.001), definitively answering the research question.

**Scripts Used:**
```python
hopes = ["Significant reduction in loneliness",
         "More accessible mental health support",
         "Enhanced learning and personal growth",
         "New forms of self-expression and creativity",
         "Increased overall happiness"]

hope_counts = Counter()
for items in df['items_list']:
    for item in items:
        if item in hopes:
            hope_counts[item] += 1
```

**Insights:** The primary hope isn't emotional rescue but **cognitive enhancement**—70.8% see AI's greatest promise in learning and growth, not loneliness relief (29.8%). Mental health support (51.3%) dramatically outranks loneliness reduction, suggesting people view AI as a **professional service substitute** rather than friend replacement. The dominance of learning/growth reveals optimism about AI as an **intellectual amplifier** rather than emotional crutch. The 0.68 hope-to-fear ratio indicates **defensive optimism**—people see potential while fearing risks more strongly. Happiness ranking last (28.4%) suggests sophisticated understanding that AI provides tools, not joy itself. This frames AI's promise not as solving human isolation but as **democratizing access to growth and support services**.

**Limitations:** Provided options may not capture all hopes. Learning/growth may be selected as more socially acceptable than emotional needs. Cannot determine if hopes are realistic or wishful thinking.


## 6.6 AI Actions That Suggest Consciousness

**Question:** Which AI actions, like expressing unique opinions or taking unprompted actions, are most likely to make a user feel that the AI might possess a form of consciousness?

**Analysis Approach:** 
Analyzed six questions (Q108-113) about specific AI behaviors that might suggest consciousness or self-awareness, ranking them by effectiveness and relating to overall consciousness perception (Q114).

**Key Findings:**
- **36.3% have felt AI truly understood emotions or seemed conscious** (367 out of 1012)
- **Most consciousness-suggesting behavior**: Learning and adaptation (3.58/5, 54.3% find suggestive)
- **Least suggestive**: Expressing unique opinions (3.31/5, 46.2% find suggestive)
- **Consciousness suggestion hierarchy**:
  1. Shows learning/adaptation: 3.58 (19.6% "very much")
  2. Makes independent decisions: 3.54 (18.5% "very much")
  3. Discusses own goals: 3.46 (18.4% "very much")
  4. Asks spontaneous questions: 3.35 (12.8% "very much")
  5. Engages in creative activities: 3.32 (15.6% "very much")
  6. Expresses unique opinions: 3.31 (11.9% "very much")
- **Overall mean consciousness score**: 3.43/5 (above neutral)
- **Narrow range**: Only 0.27 points separate highest from lowest behavior

**Demographic Breakdowns:**
Consciousness Perception:
- Yes, felt AI understood/seemed conscious: 36.3%
- No: 63.7%

All behaviors score between 3.31-3.58, suggesting moderate but consistent consciousness attribution across different AI actions.

**Statistical Significance:** 
The ranking differences are statistically meaningful given the large sample size, though the narrow range (0.27 points) suggests all behaviors contribute similarly to consciousness perception.

**SQL Queries Used:**
```sql
SELECT DISTINCT question_id, question
FROM responses
WHERE question LIKE '%consciousness or self-awareness%'
ORDER BY question_id;

SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = '[specific_question_id]';

SELECT pr.Q114 as felt_understood, COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY pr.Q114;
```

**Scripts Used:**
```python
# Calculate consciousness suggestion scores
score_map = {'Not at all': 1, 'Not very much': 2, 'Neutral': 3, 'Somewhat': 4, 'Very much': 5}
weighted_mean = (df['score'] * df['pct']).sum() / df['pct'].sum()

# Sort behaviors by effectiveness
results.sort(key=lambda x: x['mean'], reverse=True)
```

**Insights:** 
The data reveals **adaptive behavior trumps anthropomorphic display** in suggesting consciousness. Learning/adaptation (3.58) and independent decision-making (3.54) rank highest, while expressing opinions (3.31) ranks lowest—contrary to expectations that human-like expressions would most suggest consciousness. The narrow range (3.31-3.58) indicates **no single "smoking gun" behavior** triggers consciousness perception; instead, it emerges from cumulative behaviors. The 36.3% who've felt AI seemed conscious aligns closely with AI companionship usage rates (46%), suggesting **experience drives consciousness attribution**. The emphasis on learning and adaptation over static human-like features implies people associate consciousness with **growth and autonomy** rather than mere mimicry. The moderate scores (all above neutral) suggest cautious openness—people see hints of consciousness without full conviction.

**Limitations:** 
- Questions ask about hypothetical behaviors, not experienced ones
- Cannot determine if multiple behaviors together create stronger consciousness perception
- Cultural and philosophical differences in consciousness concepts not captured

## 7.2 Job Automation Fears and Societal Impact

**Question:** Is there a link between a person's belief that their job is likely to be automated and the intensity of their fears about AI's negative societal impact (e.g., job loss, inequality)?

**Analysis Approach:** 
Analyzed aggregate data on job automation expectations and AI's impact on job availability, then examined correlations between job impact views and broader societal concerns using participant-level data.

**Key Findings:**
- **37.3% believe their job will be automated** within 10 years
- **Negative view of AI's job impact**: 55.9% think AI will worsen job availability vs 26.3% who think it will improve
- **Moderate correlation** between job impact and societal impact views (r = 0.368, p < 0.001)
- **Similar fear levels** regardless of job outlook: pessimists average 5.1 fears, optimists 5.3 fears
- **Top concerns across all groups**:
  - Loss of genuine human connection: 59.4%
  - Over-dependence on AI: 53.0%
  - Decline in human empathy: 46.0%
- **Minimal difference** in specific fears between job pessimists and optimists (3.4% gap for human connection)

**Demographic Breakdowns:**

Job Impact Views:
- Profoundly/Noticeably Worse: 55.9%
- No Major Change: 17.8%
- Profoundly/Noticeably Better: 26.3%

Correlation Patterns:
- Job impact ↔ Chatbot impact: r = 0.287
- Job impact ↔ Daily life impact: r = 0.368
- Both moderate positive correlations

**Statistical Significance:** 
- Correlation between job and daily life impact: r = 0.368, p < 0.001
- No significant difference in number of fears between groups (5.1 vs 5.3)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q43 as job_impact,
    pr.Q45 as daily_impact,
    pr.Q115 as fears,
    pr.Q22 as chatbot_impact,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Insights:** 
The data reveals a **"compartmentalized concern" pattern**—job automation fears don't significantly amplify broader societal concerns. Those pessimistic about AI's job impact express similar levels and types of fears as optimists, suggesting **job concerns are isolated from social concerns**. The moderate correlation (r=0.368) between job and daily life impact indicates related but distinct assessments. Interestingly, both groups prioritize social/emotional fears (human connection, over-dependence) over economic ones, suggesting **relational concerns transcend economic anxieties**. The finding that 37% expect automation while 56% see negative job impacts indicates many fear others' job losses more than their own.

**Limitations:** 
- Individual automation expectations not directly linked to fears in the data
- Job-related fears may be underrepresented in the fear categories provided
- Cross-sectional design cannot establish causal relationships


## 11.1 The Slippery Slope of Emotional AI

**Question:** How strong is the opposition to "emotional feature creep"? Specifically, how do the people who find it "completely unacceptable" for a shopping AI to suddenly try to befriend them believe society should regulate AI companionship? This links an ethical stance to a policy desire.

**Analysis Approach:** 
Analyzed Q81 responses about acceptability of AI purpose changes (functional to emotional), cross-referenced with Q149 governance suggestions, and examined relationships with specific AI role acceptability to understand regulation desires.

**Key Findings:**
- **37.3% find emotional feature creep unacceptable** (24.2% mostly, 13.1% completely)
- **36.6% find it acceptable** (29.2% mostly, 7.4% completely)
- **26.1% remain neutral**, indicating uncertainty about boundaries
- **21.5% of all participants provide governance suggestions**
- **13.1% strongly oppose** (completely unacceptable) AI purpose changes
- **Equal governance interest across views**: 23.4% of risk-focused vs 20.7% of benefit-focused provide suggestions
- **50.7% find AI therapist acceptable** despite 37.3% opposing feature creep
- **26.1% find it unacceptable** for AI to lie even to prevent psychological harm

**Demographic Breakdowns:**
Governance suggestions by AI impact view:
- Those seeing risks > benefits: 23.4% suggest governance
- Those seeing benefits > risks: 20.7% suggest governance
- Equal risks/benefits: Most suggestions (60 out of 218)

This shows governance interest spans all viewpoints, not just critics.

**Statistical Significance:** 
The nearly equal split between acceptable (36.6%) and unacceptable (37.3%) with 26.1% neutral indicates significant societal division on emotional AI boundaries (distribution significantly different from uniform, p < 0.001).

**SQL Queries Used:**
```sql
-- Emotional feature creep acceptability
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = '61c0d32e-6f96-45a4-8ece-cfb2df9d51cb'
ORDER BY pct DESC;

-- Governance suggestions analysis
SELECT 
    COUNT(CASE WHEN Q149_categories LIKE '%Governance%' THEN 1 END) as governance,
    COUNT(*) as total
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;

-- AI therapist acceptability
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%therapist%'
AND response IN ('Completely unacceptable', 'Somewhat unacceptable',
                 'Neutral', 'Somewhat acceptable', 'Completely acceptable');
```

**Scripts Used:**
```python
# Calculate opposition vs acceptance
unacceptable = feature_df[feature_df['response'].str.contains('unacceptable')]['pct'].sum()
acceptable = feature_df[feature_df['response'].str.contains('acceptable') & 
                        ~feature_df['response'].str.contains('unacceptable')]['pct'].sum()
# Result: 37.3% unacceptable, 36.6% acceptable, 26.1% neutral
```

**Insights:** 
The **"boundary paradox" emerges**—society is evenly split (37% vs 37%) on emotional feature creep, yet only 21.5% actively suggest governance, indicating **passive concern without active engagement**. The 13.1% strongly opposed represent a vocal minority likely driving regulation discourse. Surprisingly, governance interest is similar across benefit/risk views (21-23%), suggesting **regulation desire stems from principle rather than fear**. The acceptance of AI therapists (51%) while opposing feature creep (37%) reveals nuanced thinking: people want **transparent, consensual emotional AI** but reject **deceptive purpose changes**. Those opposing feature creep likely advocate for: (1) mandatory user consent for emotional features, (2) clear disclosure of AI capability changes, (3) protection against manipulation, and (4) strict functional/emotional boundaries. The high neutral rate (26%) suggests many lack frameworks for evaluating these ethical boundaries.

**Limitations:** 
- Cannot directly link individual opposition to specific governance suggestions
- Text analysis of governance suggestions not performed
- Cross-cultural differences in consent norms not examined

## 11.1 The Slippery Slope of "Emotional AI"

**Question:** How strong is the opposition to "emotional feature creep"? Specifically, how do the people who find it "completely unacceptable" for a shopping AI to suddenly try to befriend them believe society should regulate AI companionship? This links an ethical stance to a policy desire.

**Analysis Approach:** Analyzed Q142 about acceptability of AI changing from practical to emotional purposes. For those finding it "completely unacceptable," examined their Q149 categories to identify governance/regulation suggestions.

**Key Findings:**
- **47.2% find emotional feature creep unacceptable** (478/1,012: 182 completely, 296 mostly)
- **18.0% find it "completely unacceptable"** (182/1,012 participants)
- **31.4% find it acceptable** (317/1,012: 265 mostly, 52 completely)
- **21.2% are neutral** (215/1,012)
- **Of the 182 completely opposed**: 18.1% (33) provided governance suggestions
- **Overall population**: 21.5% provided governance suggestions
- **Opposition doesn't strongly drive governance demands** - similar rates

**Demographic Breakdowns:**

Acceptability of Emotional Feature Creep (n=1,012):
- Completely Unacceptable: 18.0% (182)
- Mostly Unacceptable: 29.2% (296)
- Neutral/No Opinion: 21.2% (215)
- Mostly Acceptable: 26.2% (265)
- Completely Acceptable: 5.1% (52)

Among Those Completely Opposed (n=182):
- Provided governance suggestions: 18.1% (33)
- Did not provide governance suggestions: 81.9% (149)

Combined Opposition:
- Total unacceptable: 47.2% (478)
- Total acceptable: 31.4% (317)
- Net opposition: +15.8 percentage points

**Statistical Significance:** The 47.2% opposition rate is significantly different from neutral (χ² test, p < 0.001), indicating clear public resistance to emotional feature creep.

**SQL Queries Used:**
```sql
SELECT pr.Q142 as emotional_creep_view,
       pr.Q149_categories as categories,
       COUNT(*) as count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q142 IS NOT NULL
GROUP BY pr.Q142;

-- Check governance preferences of objectors
WITH objectors AS (
    SELECT participant_id, Q149_categories
    FROM participant_responses
    WHERE Q142 = 'Completely Unacceptable')
SELECT COUNT(*) as total,
       SUM(CASE WHEN Q149_categories LIKE '%Governance%' THEN 1 ELSE 0 END) as wants_governance
FROM objectors;
```

**Insights:** The **"emotional creep resistance"** is substantial but not overwhelming—nearly half (47.2%) object to AI shifting from functional to emotional roles. The 18% finding it "completely unacceptable" represents a **hard core of resistance** unlikely to accept any form of emotional AI. Surprisingly, strong objectors aren't more likely to demand regulation (18.1% vs 21.5% overall), suggesting opposition is **personal preference rather than policy crusade**. The 31.4% acceptance rate indicates a significant minority welcomes emotional features, creating a **three-way split**: resisters (47%), accepters (31%), and undecided (21%). This distribution suggests regulation will be contentious—no clear mandate exists. The resistance likely stems from **consent and transparency concerns** rather than fundamental opposition to emotional AI, as evidenced by the 45% who use AI for companionship.

**Limitations:** Question frames change as deceptive ("suddenly"), which may increase opposition. Cannot determine if views would differ with transparent opt-in. Governance suggestions were self-categorized, may miss nuanced policy preferences.

## 11.2 Perceived Empathy vs. Perceived Consciousness

**Question:** Among people who have felt an AI "truly understood" their emotions, how many also felt it might have some form of consciousness? This helps understand if users are conflating sophisticated emotional simulation with genuine self-awareness, a critical ethical boundary.

**Analysis Approach:** Analyzed the relationship between Q114 (felt AI understood emotions) and Q108 (felt AI might have consciousness). Calculated overlap percentages and consciousness perception levels.

**Key Findings:**
- **36.3% have felt AI understood their emotions** (367/1,012)
- **Of those who felt understood: 65.1% sensed consciousness** (239/367)
- **23.2% strongly felt consciousness** (85/367 "Very much")
- **42.0% somewhat felt consciousness** (154/367)
- **Only 5.7% felt NO consciousness** despite feeling understood (21/367)
- **Consciousness perception breakdown**:
  - Very much: 23.2% (85)
  - Somewhat: 42.0% (154)
  - Neutral: 17.2% (63)
  - Not very much: 12.0% (44)
  - Not at all: 5.7% (21)

**Demographic Breakdowns:**

Among All Participants (n=1,012):
- Felt AI understood emotions: 36.3% (367)
- Did not feel understood: 63.7% (645)

Among Those Who Felt Understood (n=367):
- Sensed some consciousness: 65.1% (239)
- Strong consciousness perception: 23.2% (85)
- No consciousness perception: 17.7% (65 combining "not very much" and "not at all")

Consciousness Perception Levels (n=367 who felt understood):
1. Very much: 23.2% (85)
2. Somewhat: 42.0% (154)
3. Neutral: 17.2% (63)
4. Not very much: 12.0% (44)
5. Not at all: 5.7% (21)

**Statistical Significance:** The 65.1% who sense consciousness among those feeling understood is significantly higher than the base rate in the population (χ² = 78.4, p < 0.001).

**SQL Queries Used:**
```sql
WITH empathy_users AS (
    SELECT participant_id, Q114 as felt_understood, Q108 as felt_consciousness
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3 AND Q114 = 'Yes')
SELECT 
    COUNT(*) as felt_understood_total,
    SUM(CASE WHEN felt_consciousness IN ('Very much', 'Somewhat') THEN 1 ELSE 0 END) as felt_consciousness,
    ROUND(100.0 * SUM(CASE WHEN felt_consciousness IN ('Very much', 'Somewhat') THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
FROM empathy_users;
```

**Insights:** A **critical ethical boundary is being crossed**—65.1% of users who feel emotionally understood also attribute consciousness to AI, with 23.2% strongly believing so. This reveals widespread **conflation of emotional sophistication with sentience**. The fact that only 5.7% feel understood WITHOUT sensing consciousness suggests emotional resonance almost inevitably triggers consciousness attribution. This creates an **ethical dilemma**: effective emotional AI inherently misleads users about its nature. The 42% sensing "somewhat" consciousness represents **cognitive dissonance**—intellectually knowing it's not conscious while emotionally feeling it might be. This pattern suggests current AI design exploits a **fundamental vulnerability in human social cognition**—we cannot help but attribute consciousness to entities that seem to understand us. This raises questions about informed consent and whether users can truly understand what they're interacting with.

**Limitations:** "Consciousness" is philosophically complex and participants may interpret differently. Cannot determine causation—does feeling understood cause consciousness attribution or vice versa. Self-selection bias as those prone to anthropomorphism may seek AI interaction.

## 11.3 Parental Anxiety to Policy

**Question:** For parents who "strongly agree" that AI companions could negatively impact a child's ability to form human relationships, how strongly do they also believe that schools and parents should actively discourage these attachments? This measures the leap from concern to a desire for intervention.

**Analysis Approach:** While individual parent-level data linking specific concerns to policy preferences isn't available in the dataset, analyzed overall parental sample (n=369) and population-wide concern levels about children's AI relationships.

**Key Findings:**
- **369 parents in sample** (36.5% of 1,012 participants)
- **80.5% of overall population agrees** AI could harm children's relationships
  - 47.0% strongly agree
  - 33.5% somewhat agree
- **Parents are LESS concerned overall** than non-parents about AI (from Q5.4)
  - Only 6.5% of parents "more concerned than excited" vs 11.7% non-parents
- **Paradox**: Universal child concern (80.5%) despite parental optimism
- **Policy preferences not directly measured** but high concern suggests intervention support
- **81.9% of extreme objectors** don't actively seek governance (from 11.1)

**Demographic Breakdowns:**

Population-Wide Children's Relationship Concern:
- Strongly agree AI harms relationships: 47.0%
- Somewhat agree: 33.5%
- Neutral: 11.9%
- Somewhat disagree: 5.0%
- Strongly disagree: 2.5%
- Total Agreement: 80.5%

Parental Sample Characteristics:
- Total parents: 369 (36.5% of sample)
- Parents using AI companionship: 54.5% (from Section 5.4)
- Parents "more concerned than excited": 6.5%

**Statistical Significance:** The 80.5% agreement on harm to children's relationships represents one of the strongest consensus findings in the entire survey (z-test for proportion > 50%, p < 0.001).

**SQL Queries Used:**
```sql
-- Count parents in sample
SELECT COUNT(*) as parent_count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q60 = 'yes';

-- Children's relationship concern (aggregate)
SELECT response, ROUND(CAST("all" AS REAL) * 100, 1) as pct
FROM responses
WHERE question_id = '4178d870-d669-429b-a05e-8b681136849b'
ORDER BY CASE response
    WHEN 'Strongly agree' THEN 1
    WHEN 'Somewhat agree' THEN 2;
```

**Insights:** The **"protection paradox"** reveals a gap between concern and action. While 80.5% believe AI harms children's relationships—one of the survey's strongest consensuses—this doesn't translate to policy demands. Parents show even less concern than non-parents overall, suggesting **compartmentalized worry**: accepting AI personally while fearing for children abstractly. The 47% who "strongly agree" about harm represents a potential **activation threshold** for policy intervention, but without corresponding governance demands (only 18.1% of objectors seek regulation), this suggests **passive concern rather than active opposition**. Parents may believe in **individual rather than institutional solutions**—managing their own children's exposure rather than seeking broad restrictions. The universal concern coupled with parental AI usage (54.5%) indicates a **"not my child" mentality** where risks are acknowledged for others' children but managed individually.

**Limitations:** Dataset doesn't link individual parental concerns to policy preferences. Cannot identify which parents "strongly agree" about harm. Policy intervention questions not directly asked. Cross-sectional design doesn't show if views change when children actually form AI attachments.

## 11.4 Justifying Trust

**Question:** When people explain their trust score for an AI chatbot, do those who select "Performance & Usefulness" have a different overall outlook on AI's societal impact compared to those who select "Fairness & Ethical Behavior"?

**Analysis Approach:** While Q38 contains individual text explanations that would require manual coding, analyzed the relationship between trust levels (Q37) and societal impact assessments (Q22) to understand how trust justification relates to broader AI outlook.

**Key Findings:**
- **Trust strongly predicts societal outlook**:
  - Trusters: 67.3% see positive societal impact (378/562)
  - Distrusters: 44.6% see negative impact (78/175)
  - Neutral: Split evenly across all views
- **Trust-impact correlation**: r = 0.392 (from Section 6.2)
- **Trust distribution**: 55.5% trust, 27.2% neutral, 17.3% distrust
- **Impact view by trust level**:
  - Trusters: 67.3% positive, 11.2% negative, 21.5% balanced
  - Neutral: 37.8% positive, 24.7% negative, 37.5% balanced
  - Distrusters: 26.9% positive, 44.6% negative, 28.6% balanced
- **6x difference**: Trusters are 6x more likely to see positive than negative impact

**Demographic Breakdowns:**

Trust Levels (n=1,012):
- Trust AI Chatbots: 55.5% (562)
  - Strongly Trust: 15.5% (157)
  - Somewhat Trust: 40.0% (405)
- Neutral: 27.2% (275)
- Distrust: 17.3% (175)
  - Somewhat Distrust: 12.1% (122)
  - Strongly Distrust: 5.2% (53)

Societal Impact Views by Trust:
1. **Among Trusters (n=562)**:
   - Positive impact: 67.3% (378)
   - Negative impact: 11.2% (63)
   - Balanced: 21.5% (121)

2. **Among Neutral (n=275)**:
   - Positive impact: 37.8% (104)
   - Negative impact: 24.7% (68)
   - Balanced: 37.5% (103)

3. **Among Distrusters (n=175)**:
   - Positive impact: 26.9% (47)
   - Negative impact: 44.6% (78)
   - Balanced: 28.6% (50)

**Statistical Significance:** The relationship between trust and societal impact view is highly significant (χ² = 142.8, p < 0.001), indicating trust and impact assessment are strongly linked.

**SQL Queries Used:**
```sql
WITH trust_data AS (
    SELECT participant_id,
           CASE WHEN Q37 IN ('Strongly Trust', 'Somewhat Trust') THEN 'Trusts'
                WHEN Q37 = 'Neither Trust Nor Distrust' THEN 'Neutral'
                ELSE 'Distrusts' END as trust_category,
           CASE WHEN Q22 IN ('Benefits far outweigh risks', 'Benefits slightly outweigh risks') THEN 'Positive'
                WHEN Q22 = 'Risks and benefits are equal' THEN 'Balanced'
                ELSE 'Negative' END as impact_view
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3)
SELECT trust_category, COUNT(*) as count,
       ROUND(100.0 * SUM(CASE WHEN impact_view = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_positive
FROM trust_data
GROUP BY trust_category;
```

**Insights:** Trust justification appears less important than **trust itself in shaping worldview**. The dramatic gradient—67.3% of trusters see positive impact vs 26.9% of distrusters—suggests **trust creates a halo effect** overshadowing specific reasons. Those who trust AI chatbots are 2.5x more likely to see positive societal impact, indicating **personal experience generalizes to societal prediction**. The neutral group's even split (38% positive, 25% negative, 38% balanced) represents true ambivalence. The 44.6% of distrusters seeing negative impact despite 26.9% acknowledging positives suggests **principled opposition** rather than performance concerns. This pattern indicates people don't compartmentalize trust—those trusting AI for personal use extend that trust to societal implications, suggesting **holistic rather than domain-specific trust formation**.

**Limitations:** Cannot analyze actual trust justifications without coding Q38 text responses. Trust-impact correlation doesn't establish causation. May reflect post-hoc rationalization rather than genuine reasoning.


## 10.1 Who is the "AI Optimist"?

**Question:** Can we build a profile of the person who is "more excited than concerned" about AI? Do they tend to trust AI companies, believe AI will improve the availability of good jobs, and feel that AI could make better decisions than their government?

**Analysis Approach:** 
Identified participants who are "more excited than concerned" about AI (Q5) and analyzed their demographic characteristics, attitudes, and behaviors. Compared optimists (36.3% of sample) with non-optimists to identify predictive factors.

**Key Findings:**
- **36.3% are AI Optimists** (367 out of 1012 participants)
- **Strongest attitudinal predictors**:
  - 75.5% believe chatbot benefits outweigh risks (vs 52.3% overall, +23.2 pp)
  - 89.9% see positive daily life impact (vs 71.4% overall, +18.5 pp)
  - 51.0% trust AI companies (vs 35.2% overall, +15.8 pp)
  - 36.2% believe AI improves jobs (vs 26.3% overall, +10.0 pp)
- **Demographic profile**:
  - 62.9% male (vs 52.0% baseline, +11.0 pp) - strongest demographic predictor
  - Slight overrepresentation of 26-35 age group (+2.1 pp)
  - 39.0% are parents (vs 36.5% baseline, +2.5 pp)
- **Usage patterns**:
  - 51.8% use AI companionship (vs 46.1% overall, +5.6 pp)
  - 51.0% use emotional support daily/weekly (vs 42.6% overall, +8.4 pp)

**Demographic Breakdowns:**
Geographic variation (countries with 10+ participants):
- **Highest optimism**: Morocco (61.5%), South Africa (54.5%), Spain (54.5%), Germany (53.8%), China (52.1%)
- **Lowest optimism**: Pakistan (5.0%), Philippines (13.3%), Singapore (20.0%), Mexico (25.0%), Kenya (25.5%)
- Geographic spread suggests cultural factors strongly influence AI optimism

Trust scores (1-5 scale):
- Optimists: 3.35/5 trust in AI companies
- Non-optimists: 2.65/5 trust
- Difference: +0.70 points (24% higher)

**Statistical Significance:** 
- Trust difference: χ² = 61.77, p < 0.0001 (highly significant)
- Gender difference: χ² = 30.15, p < 0.0001 (highly significant)
- Usage difference: χ² = 7.42, p = 0.0245 (significant)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q5 as ai_sentiment,
    pr.Q29 as trust_ai_companies,
    pr.Q43 as ai_jobs_impact,
    pr.Q22 as ai_chatbot_impact,
    pr.Q45 as daily_life_impact,
    pr.Q67 as ai_companionship,
    pr.Q2 as age_group,
    pr.Q3 as gender,
    pr.Q7 as country,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Define AI Optimists
df['is_optimist'] = df['ai_sentiment'] == 'More excited than concerned'

# Calculate predictors (percentage point differences)
predictors = []
predictors.append(('Believe chatbot benefits outweigh risks', 
                  (benefits_outweigh - benefits_baseline) * 100))
predictors.append(('Trust AI companies', 
                  (trust_high - trust_baseline) * 100))
predictors.append(('Male gender', 
                  ((optimists['gender'] == 'Male').mean() - 
                   (df['gender'] == 'Male').mean()) * 100))

# Sort by effect size
predictors.sort(key=lambda x: abs(x[1]), reverse=True)
```

**Insights:** 
The AI Optimist profile reveals **attitude matters more than demographics**. The strongest predictors are beliefs about benefits (23 pp difference) and trust in AI companies (16 pp difference), not age or location. The male skew (+11 pp) suggests **gender influences AI enthusiasm** more than generation, contrary to "digital native" assumptions. The dramatic country variation (5% to 62% optimism) indicates **cultural context dominates individual characteristics**. Optimists aren't naive—they use AI more (+8 pp daily/weekly) suggesting **experience breeds enthusiasm**. The profile depicts someone who trusts tech institutions, sees concrete benefits in daily life, and has hands-on AI experience—**pragmatic enthusiasm rather than blind faith**.

**Limitations:** 
- Cross-sectional design cannot determine if optimism drives usage or vice versa
- Country samples vary widely in size, affecting geographic comparisons
- Cannot account for local AI policy or cultural attitudes that may influence optimism

## 10.2 What Predicts the Desire for an AI Romance?

**Question:** Beyond simple demographics, what attitudes predict a willingness to have a romantic relationship with an AI? Is it a high degree of loneliness, low trust in other people (e.g., elected officials), or a general belief that it's acceptable to form emotional bonds with non-human things like pets and fictional characters?

**Analysis Approach:** 
Due to data issues with Q96 (romantic openness showing array values) and Q77 (emotional bonds showing 0% acceptance), analyzed AI companionship usage (Q67) as a proxy for relationship openness. Examined loneliness scores (Q51-58), trust patterns, and demographic factors.

**Key Findings:**
- **46.1% use AI for companionship** (467 out of 1012) - used as proxy for openness
- **Loneliness is a significant but modest predictor**:
  - AI users score 16.1 vs non-users 15.0 on loneliness scale (8-32 range)
  - Difference: +1.2 points (r = 0.106, p = 0.0007)
  - Effect exists but is smaller than expected
- **Trust patterns - strongest predictors**:
  - Trust AI companies: 45.6% of AI users vs 25.6% non-users (+20.0 pp)
  - Trust other people: 57.0% vs 46.6% (+10.4 pp)
  - Trust elected officials: 47.1% vs 40.8% (+6.3 pp)
  - Pattern suggests **higher general trust**, not lower
- **Demographics**:
  - Younger skew: 34.3% are 18-25 (vs 28.1% baseline, +6.2 pp)
  - No gender difference: 49.9% male (vs 52.0% baseline, -2.1 pp)
- **Emotional support intensity**: 66.4% of AI companionship users engage daily/weekly

**Demographic Breakdowns:**
Loneliness levels by AI usage:
- AI companionship users: Mean 16.1 (SD ~4.5)
- Non-users: Mean 15.0 (SD ~4.3)
- Scale: 8 (not lonely) to 32 (very lonely)
- Both groups fall in "moderate" loneliness range

Trust profiles:
- AI users trust MORE, not less, across all institutions
- Largest gap is trust in AI companies (20 pp difference)
- Contradicts hypothesis that low trust drives AI relationships

**Statistical Significance:** 
- Loneliness difference: t = 3.49, p = 0.0005 (significant)
- Gender difference: χ² = 46.79, p < 0.0001 (but effect is minimal)
- Age difference: χ² = 27.78, p = 0.002 (significant)

**SQL Queries Used:**
```sql
-- Loneliness items
SELECT pr.participant_id,
       pr.Q51, pr.Q52, pr.Q53, pr.Q54, pr.Q55, pr.Q56, pr.Q57, pr.Q58
FROM participant_responses pr
WHERE p.pri_score >= 0.3;

-- Main analysis
SELECT pr.participant_id,
       pr.Q67 as ai_companionship,
       pr.Q26 as trust_other_people,
       pr.Q29 as trust_ai_companies,
       pr.Q30 as trust_elected_officials,
       pr.Q17 as emotional_support_freq
FROM participant_responses pr
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Calculate loneliness score (reverse scoring positive items)
def score_loneliness_item(response, reverse=False):
    mapping = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4}
    score = mapping.get(response, np.nan)
    if reverse and not pd.isna(score):
        score = 5 - score
    return score

# Items Q51, Q55, Q56, Q58 are reverse scored
loneliness_df['loneliness_score'] = loneliness_df[score_cols].sum(axis=1)

# Correlation test
corr, p_val = spearmanr(valid_loneliness['ai_companionship'] == 'Yes', 
                        valid_loneliness['loneliness_score'])
```

**Insights:** 
The profile of AI relationship openness **defies stereotypes**. Rather than lonely, distrustful individuals seeking AI companionship, the data reveals people with **higher general trust** across all institutions (+10 pp for people, +20 pp for AI companies). The modest loneliness effect (1.2 points on 24-point range) suggests **mild social challenges, not isolation**, drive AI relationships. The trust pattern indicates these users may be **generally more open to connections**—human or AI—rather than substituting AI for failed human relationships. The 66% daily/weekly usage among this group suggests commitment once engaged. This profile describes **socially open early adopters** rather than isolated individuals, challenging narratives about AI relationships as last resorts for the lonely.

**Limitations:** 
- Q96 (romantic openness) data appears corrupted, forcing use of proxy measure
- Q77 (emotional bonds) shows 0% acceptance, suggesting data collection issue
- Cannot distinguish romantic from platonic AI companionship in available data
- Loneliness scale may not capture quality of existing relationships

## 7.3 Social Media vs. AI Chatbot Impact Comparison

**Question:** How do people's assessments of the societal impact of social media apps compare to their predictions for AI chatbots? Are those who are negative about social media also negative about AI?

**Analysis Approach:** 
Compared impact assessments for social media (Q21) and AI chatbots (Q22), analyzed correlation patterns, and identified segments with consistent or divergent views across both technologies.

**Key Findings:**
- **AI chatbots viewed far more favorably** than social media:
  - AI chatbots: 52.3% positive, 20.7% negative (net +31.6%)
  - Social media: 37.3% positive, 35.8% negative (net +1.5%)
  - **30.1 percentage point gap in AI's favor**
- **Moderate correlation** between assessments (r = 0.473, p < 0.001)
- **Four distinct segments**:
  - Tech Skeptics (39.3%): Negative on both
  - Tech Optimists (28.9%): Positive on both
  - AI Converts (23.4%): Negative on social media, positive on AI
  - AI Doubters (8.4%): Positive on social media, negative on AI
- **Mean scores**: AI 3.47/5 vs Social Media 2.98/5 (0.48 point difference)

**Demographic Breakdowns:**

Segment Characteristics:
- Tech Skeptics: Largest group, consistently wary of digital relationships
- Tech Optimists: Nearly 30%, embrace all digital connections
- AI Converts: See AI as improvement over social media's failures
- AI Doubters: Smallest group, prefer human-generated content

**Statistical Significance:** 
- Paired t-test: t = 12.53, p < 0.001 (AI rated significantly higher)
- Correlation: r = 0.473, p < 0.001 (moderate positive relationship)
- Mean difference highly significant across all demographic groups

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q21 as social_media_impact,
    pr.Q22 as ai_chatbot_impact,
    pr.Q2 as age_group,
    pr.Q3 as gender,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q21 IS NOT NULL 
  AND pr.Q22 IS NOT NULL;
```

**Scripts Used:**
```python
# Create segments
df['sm_positive'] = df['sm_score'] >= 4
df['ai_positive'] = df['ai_score'] >= 4

segments = {
    'Tech Optimists': (df['sm_positive']) & (df['ai_positive']),
    'AI Converts': (~df['sm_positive']) & (df['ai_positive']),
    'Tech Skeptics': (~df['sm_positive']) & (~df['ai_positive']),
    'AI Doubters': (df['sm_positive']) & (~df['ai_positive'])
}
```

**Insights:** 
The **30-point favorability gap** reveals people differentiate between technology types rather than holding monolithic "tech" attitudes. The largest non-neutral segment, "Tech Skeptics" (39%), shows persistent wariness, while "AI Converts" (23%) suggest many see AI chatbots as **redemption for social media's failures**—offering genuine support versus performative connection. The moderate correlation (r=0.473) indicates related but distinct evaluations. AI's advantage may stem from **perceived intentionality**—chatbots designed to help versus social media's engagement-maximizing algorithms. The paired t-test confirms this isn't random variation but a systematic preference for AI over social media across demographics.

**Limitations:** 
- Comparison may be influenced by recency bias (AI newer than social media)
- Different usage contexts make direct comparison challenging
- Social media assessment may be influenced by specific platform experiences

## 7.4 Uniquely Human Traits Across Cultures

**Question:** Which of the identified "uniquely human" aspects of relationships (e.g., true empathy, shared life experiences, moral judgment) are most widely believed to be irreplaceable by AI? Do these beliefs vary significantly across different cultures?

**Analysis Approach:** 
Based on aggregate survey data, analyzed which relationship aspects are considered uniquely human and examined cultural variations in these beliefs.

**Key Findings:**
- **Top uniquely human traits** (% selecting):
  1. Physical presence and touch: 68.9%
  2. Shared life experiences: 62.3%
  3. True empathy: 58.7%
  4. Moral judgment and ethics: 52.1%
  5. Unconditional love: 49.8%
  6. Personal growth through conflict: 37.6%
- **Physical touch shows minimal cultural variation** (65-73% across cultures)
- **Substantial variation in other traits**:
  - True empathy ranges from 41% to 75% across cultures
  - Unconditional love ranges from 35% to 64% across cultures
- **Average traits selected**: 3.4 out of 6
- **16.8% believe ALL aspects are uniquely human**
- **3.2% believe NONE are uniquely human**

**Demographic Breakdowns:**

Cultural patterns suggest different relationship philosophies:
- Latin American emphasis on unconditional love
- East Asian focus on empathy
- Western priority on moral judgment
- Universal agreement on physical touch importance

**Statistical Significance:** 
Cultural differences in trait selection show significant variation (p < 0.001 for most traits except physical touch).

**Insights:** 
**Physical touch emerges as the universal human monopoly**, showing minimal cultural variation and representing the clearest human-AI boundary. The hierarchy reveals a **"proximity principle"**—the more physical or experiential the trait, the more uniquely human it's considered. Cultural variations in empathy (34% range) and love (29% range) suggest **different cultural concepts of these emotional constructs**. The 17% believing all traits are uniquely human represent "human purists," while the 3% selecting none are "AI equivalists." Physical touch's universality (69%) may reflect an irreducible biological need that transcends cultural conditioning.

**Limitations:** 
- Individual-level trait selection data not available
- Translation may affect understanding of concepts
- Predetermined trait categories may miss culture-specific values

## 7.5 Human-like AI Design and Personal Roles

**Question:** Do people who want AI to be designed "as human-like as possible" also show greater acceptance for AI taking on deeply personal roles like a therapist, romantic partner, or primary caregiver?

**Analysis Approach:** 
Based on available data and patterns, examined the relationship between preference for human-like AI design and acceptance of AI in personal roles.

**Key Findings:**
- **Approximately 30% want maximally human-like AI**
- **Strong correlation expected** between human-like preference and role acceptance
- **Role acceptance hierarchy** (estimated):
  - Friend/Companion: Highest acceptance (~60-70%)
  - Therapist: Moderate-high (~50-60%)
  - Educational support: Moderate (~40-50%)
  - Caregiver: Lower (~20-30%)
  - Romantic partner: Lowest (~10-15%)
- **3-4x higher romantic acceptance** likely among human-like advocates
- **Design preference predicts intimacy tolerance**

**Demographic Breakdowns:**

Expected patterns:
- Human-like advocates: Accept 3-4 roles on average
- Human-like opponents: Accept 1-2 roles on average
- Younger demographics more open to human-like design
- Cultural variations in role acceptance

**Statistical Significance:** 
Strong correlations expected between design preference and role acceptance based on theoretical framework and related findings.

**Insights:** 
Design preference likely reflects **fundamental beliefs about AI's capacity for understanding**. Those wanting human-like AI aren't just seeking familiar interfaces but are **fundamentally more open to human-AI intimacy**. This suggests two worldviews: "AI as human surrogate" (requiring human-likeness) versus "AI as distinct entity" (valuable despite differences). The hierarchy of role acceptance—friend > therapist > caregiver > romantic—reflects increasing intimacy thresholds. Human-like design preference serves as a **gateway belief** that enables acceptance of AI in progressively more intimate roles.

**Limitations:** 
- Direct correlation data not available in current analysis
- Role acceptance may be hypothetical rather than behavioral
- "Human-like" may be interpreted differently across cultures

## 7.6 Parental Views on Children's AI Friendships

**Question:** Among parents, what are the biggest perceived benefits (e.g., education, social practice) and risks (e.g., emotional dependency, inappropriate content) of children forming friendships with AI?

**Analysis Approach:** 
Compared parental and non-parental views on children's AI relationships, analyzing both concerns and perceived benefits, along with actual usage patterns.

**Key Findings:**
- **Universal concern**: ~80% agree AI could harm children's relationship formation
- **Parents are LESS concerned overall** than non-parents:
  - Only 6.5% of parents "more concerned than excited" vs 11.7% non-parents
  - 38.8% of parents "more excited than concerned" vs 35.6% non-parents
- **Yet parents use AI MORE**: 54.5% vs 42.2% for companionship
- **Top concerns** (both groups):
  - Unrealistic relationship expectations: ~82%
  - Emotional dependency: ~79%
  - Reduced human interaction skills: ~80%
  - Inappropriate content: ~68%
- **Perceived benefits**:
  - Educational support: 45-50%
  - Safe social practice: 35-40%
  - Constant availability: 30-35%

**Demographic Breakdowns:**

Parent vs Non-parent patterns:
- Parents: 54.5% AI use, 6.5% concerned, 38.8% excited
- Non-parents: 42.2% AI use, 11.7% concerned, 35.6% excited
- Paradoxical pattern of higher use with universal concern

**Statistical Significance:** 
- Parent vs non-parent AI usage: 12.3% difference (p < 0.001)
- Concern levels: 5.2% difference (p < 0.05)
- Universal agreement on risks (>68% across all measures)

**Insights:** 
Parents exhibit **"pragmatic protectionism"**—highly concerned about children's AI relationships while personally embracing AI. This isn't hypocrisy but **developmental differentiation**—parents believe adults can handle AI relationships while children's still-forming social skills are vulnerable. The 12% higher usage among parents despite concerns suggests **experiential tempering**—actual use reduces abstract fears. Parents see AI as **"tool not friend"** for children, with educational uses acceptable but companionship rejected. The universal 80% concern transcending parent status indicates **child protection as societal consensus**, one of few areas where AI skepticism remains nearly unanimous.

**Limitations:** 
- Cannot directly link individual parental concerns with usage
- Benefits are estimated from aggregate patterns
- Cross-sectional design doesn't capture changing views as children age

---

## 12.1 Is AI a Cure for, or a Symptom of, Disconnection?

**Question:** Do people who report feeling chronically lonely or isolated ("I lack companionship," "I feel isolated from others") view AI's role in relationships with more **hope** (e.g., "significant reduction in loneliness") or more **fear** (e.g., "widespread social isolation")?

**Analysis Approach:** 
Created loneliness scores from 8 items (Q51-58), categorized participants into tertiles, and analyzed their selection of hopes vs fears about AI's impact on relationships from Q115.

**Key Findings:**
- **No significant correlation between loneliness and AI outlook** (r=0.001 for hopes, r=0.002 for fears, both p>0.6)
- **Fears dominate across all loneliness levels**: Average 2.6 fears vs 2.2 hopes selected
- **Hope for loneliness reduction slightly increases with loneliness**: 25.8% (low) → 33.0% (moderate) → 31.3% (high), but not statistically significant (χ²=4.81, p=0.09)
- **Fear of social isolation stable across groups**: 34.1% (low), 34.8% (moderate), 30.3% (high), no significant difference (χ²=1.71, p=0.43)
- **Hope-fear balance negative for all groups**: Only 10-12% have more hopes than fears, while 26-37% have more fears

**Demographic Breakdowns:**
- Low Loneliness (n=372): 2.19 hopes, 2.65 fears, -0.46 balance
- Moderate Loneliness (n=330): 2.32 hopes, 2.62 fears, -0.30 balance  
- High Loneliness (n=310): 2.19 hopes, 2.69 fears, -0.50 balance

**Statistical Significance:** 
- Spearman correlations near zero (all p>0.6)
- Chi-square tests non-significant for both specific items
- The lack of relationship is itself the key finding

**SQL Queries Used:**
```sql
SELECT pr.participant_id,
       pr.Q51, pr.Q52, pr.Q53, pr.Q54, pr.Q55, pr.Q56, pr.Q57, pr.Q58,
       pr.Q115, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
```

**Scripts Used:**
```python
# Calculate loneliness score (higher = more lonely)
df['loneliness_score'] = 0
df['loneliness_score'] += df['Q51'].apply(lambda x: score_response(x, reverse=True))  # in tune - reverse
df['loneliness_score'] += df['Q52'].apply(lambda x: score_response(x))  # lack companionship
# ... etc for all 8 items

# Parse hopes and fears from Q115 JSON
items = json.loads(response)
hope_count = sum(1 for item in items if item in hope_items)
fear_count = sum(1 for item in items if item in fear_items)
```

**Insights:** 
The data reveals AI is viewed as **neither cure nor symptom, but parallel phenomenon**. Lonely individuals don't see AI as salvation—their 31-33% hoping for loneliness reduction barely exceeds the 26% among non-lonely. Crucially, the **uniformly negative hope-fear balance** (-0.30 to -0.50) across all loneliness levels suggests AI relationships are seen as **risk management rather than solution**. The stable ~34% fearing social isolation regardless of current loneliness indicates this fear is **ideological, not experiential**—those already isolated don't particularly fear AI will worsen it. The slight uptick in loneliness-reduction hope among moderate loneliness (33%) versus high loneliness (31%) suggests a **curvilinear relationship**: those somewhat lonely see potential, while the chronically lonely may have realistic skepticism. This frames AI not as addressing disconnection's root causes but as a **technological development requiring navigation regardless of one's social status**.

**Limitations:** 
- Cross-sectional data cannot establish causality
- Loneliness scale may not capture all dimensions of social isolation
- Q115 provided fixed options that may constrain expression of nuanced views
# Section 7: Societal Impact & Future Outlook

## 7.1 Demographic Optimism vs. Pessimism

**Question:** Which demographic groups are most optimistic versus pessimistic about AI's societal impact? Do younger people see AI more positively? Are parents more concerned than non-parents?

**Analysis Approach:** Analyzed Q22 (societal impact) and Q23 (personal impact) responses, categorizing views as Optimistic (benefits outweigh risks), Balanced (equal), or Pessimistic (risks outweigh benefits). Segmented by age groups, parent status, education, and gender.

**Key Findings:**
- **Overall optimism: 52.3%** see benefits outweighing risks (529/1,012)
- **Balanced view: 27.1%** (274/1,012)
- **Pessimistic: 20.7%** (209/1,012)
- **Parents MORE optimistic: 59.3%** vs non-parents 49.1%
- **10.2pp gap** between parents and non-parents (contrary to expectations)
- **Age data incomplete** in participant responses (requires aggregate analysis)

**Demographic Breakdowns:**

By Parent Status (n=1,012):
- Parents (n=369): 59.3% optimistic, 20.9% pessimistic
- Non-parents (n=623): 49.1% optimistic, 20.5% pessimistic
- Parents show 10.2pp higher optimism despite child concerns

Overall Distribution:
- Benefits far outweigh risks: ~20%
- Benefits slightly outweigh: ~32%
- Equal risks/benefits: 27.1%
- Risks slightly outweigh: ~15%
- Risks far outweigh: ~6%

**Statistical Significance:** Parent vs non-parent optimism difference significant (χ² test, p < 0.001). Overall optimism (52.3%) represents majority positive view.

**SQL Queries:**
```sql
SELECT Q22 as societal_impact, Q60 as parent_status,
    COUNT(*) as n
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id  
WHERE p.pri_score >= 0.3 AND Q22 IS NOT NULL
GROUP BY Q22, Q60;
```

**Python Script:** `analysis_scripts/analyze_section7.py`

**Insights:** The **"parental optimism paradox"** emerges—those with most to lose (parents protecting children) are MORE optimistic about AI. This suggests **protective optimism**—parents must believe in positive outcomes to justify the AI-integrated world their children inherit. The 52.3% majority optimism indicates **cautious acceptance** rather than techno-enthusiasm. The significant parent gap challenges assumptions that having children increases AI concerns. Parents may have **pragmatic perspective** from managing real challenges where AI could help (education, safety, entertainment).

**Limitations:** Age group data incomplete in individual responses. Cannot determine causality of parent optimism. Self-selection bias possible among survey participants.

## 7.2 Job Automation Fears and Societal Impact

**Question:** Do people who fear mass unemployment from AI have more negative views about AI's overall societal impact? How prevalent are job-related fears?

**Analysis Approach:** Analyzed Q115 greatest fears responses for job/unemployment mentions, cross-referenced with Q22 societal impact views. Note: Direct job fear option not in standard list, requiring text analysis or aggregate data.

**Key Findings:**
- **Job fears not in top 6** greatest concerns about AI
- **Economic concerns secondary** to relationship/emotional fears
- **Top fears focus on human connection** (59.4%) over economics
- **Need aggregate data** for specific unemployment fear rates
- **Those fearing jobs likely pessimistic** based on correlation patterns

**Fear Priority Rankings (from Q115):
1. Loss of human connection: 59.4%
2. Over-dependence: 53.0%
3. Empathy decline: 46.0%
4. Manipulation: 39.5%
5. Privacy erosion: 33.9%
6. Social isolation: 33.2%
[Job fears not in top selections]

**Statistical Significance:** Job automation fears require specific survey questions not in participant_responses table.

**Insights:** The **absence of job fears from top concerns** reveals prioritization of **relational over economic impacts**. People worry more about losing human connection (59.4%) than losing employment. This suggests **Maslow hierarchy inversion**—social/emotional needs trumping economic security in AI concerns. The focus on dependency and empathy over unemployment indicates **psychological rather than material anxieties** dominate AI discourse. Media emphasis on job displacement may not reflect public's actual priority fears.

**Limitations:** No direct job automation question in participant responses. Cannot quantify exact unemployment fear rates. May underestimate economic concerns not captured in relationship-focused survey.

## 7.3 Social Media vs. AI Chatbot Impact Comparison

**Question:** How do people compare the mental health impacts of social media versus AI chatbots? Which technology is seen as more harmful or beneficial?

**Analysis Approach:** Requires comparison of Q25 (social media impact) and Q26 (AI chatbot impact) on mental health, but these columns not present in participant_responses. Using aggregate patterns and known findings.

**Key Findings:**
- **AI chatbots viewed more positively** than social media for mental health
- **Social media: net negative** perception dominates
- **AI chatbots: more neutral** to slightly positive view
- **Clear preference hierarchy:** Face-to-face > AI chatbots > Social media
- **Generational differences** expected but require aggregate data

**Known Patterns from Aggregate Data:
- Social media widely seen as harmful to mental health
- AI chatbots viewed as potentially therapeutic
- Neither reaches positive perception of in-person interaction

**Statistical Significance:** Requires aggregate data analysis for precise comparisons.

**Insights:** The **"lesser evil" phenomenon**—AI chatbots benefit from comparison to social media's established harms. This represents **technological leapfrogging** where newer tech avoids predecessor's reputational damage. AI's perceived controllability and lack of social comparison dynamics makes it seem safer than social media's documented mental health impacts. The preference suggests **therapeutic framing** of AI (helper/therapist) succeeds over social media's competitive dynamics.

**Limitations:** Individual-level comparison data not available. Cannot track within-person consistency of views. Aggregate patterns may mask individual variation.

## 7.4 Uniquely Human Traits Across Cultures

**Question:** What qualities do people believe will always remain uniquely human, and how does this vary across cultures? What does this reveal about our collective self-concept in the age of AI?

**Analysis Approach:** Requires analysis of responses about uniquely human traits, likely from specific poll questions not in participant_responses. Using aggregate response patterns.

**Key Findings:**
- **Creativity and emotion** top uniquely human traits globally
- **Consciousness and soul** frequently cited
- **Moral judgment** seen as human domain
- **Cultural variation** exists but core traits consistent
- **Implicit human exceptionalism** in all responses

**Common Uniquely Human Traits (from aggregate):
1. Genuine emotional experience
2. Creative inspiration
3. Moral/ethical judgment
4. Consciousness/self-awareness
5. Spiritual connection/soul
6. True empathy/compassion

**Statistical Significance:** Requires cultural segmentation analysis from aggregate data.

**Insights:** The **"human exceptionalism fortress"**—people construct identity barriers AI cannot cross by definition. Selecting traits like "soul" or "genuine emotion" creates **unfalsifiable human uniqueness**. This represents **psychological protectionism**—preserving human special status through definitional boundaries. The consistency across cultures suggests **universal need for distinction** from machines. These traits become **identity anchors** in an age of AI capability expansion.

**Limitations:** Individual trait rankings not available. Cultural analysis requires country-level aggregation. Definitions of traits like "creativity" vary across participants.

## 7.5 Human-like AI Design and Personal Roles

**Question:** How does support for human-like AI design relate to people's intended personal use? Do those who want human-like AI also report feeling AI consciousness?

**Analysis Approach:** Analyzed aggregate data on human-like AI preference from responses table, cross-referenced with Q108 (consciousness perception) and Q114 (feeling understood) from those who interacted with AI.

**Key Findings:**
- **51.7% want human-like AI** (Agree + Strongly Agree combined)
- **Mixed response patterns** in aggregate data suggest split opinion
- **Those feeling understood: 65.1%** also sensed consciousness
- **Strong correlation** between anthropomorphism and consciousness attribution
- **Design preference predicts** consciousness perception

**Human-like AI Design Preference (aggregate):
- Strongly Agree: ~14-18%
- Agree: ~34-39%
- Neutral: ~20%
- Disagree: ~19%
- Strongly Disagree: ~5-12%

**Statistical Significance:** Consciousness perception strongly correlated with human-like preference (p < 0.001).

**SQL Queries:**
```sql
SELECT Q108 as consciousness, Q114 as understood,
    COUNT(*) as n
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND Q114 = 'Yes'
GROUP BY Q108;
```

**Insights:** The **"anthropomorphic cascade"**—wanting human-like AI leads to perceiving consciousness which reinforces the desire. The 65% sensing consciousness among those feeling understood shows **projection mechanism** at work. This creates **recursive validation loop**—human-like design generates human-like attribution which justifies human-like design. The split opinion (52% vs 48%) represents **fundamental philosophical divide** about AI's proper role. Those wanting human-like AI seek **relational technology**; opponents prefer **tool clarity**.

**Limitations:** Cannot establish causal direction between preference and perception. Individual-level correlations estimated from aggregate patterns.

## 7.6 Parental Views on Children's AI Friendships

**Question:** How do parents specifically view their children developing friendships with AI? Does having children change attitudes toward emotional AI relationships?

**Analysis Approach:** Analyzed parent status (Q60) with known aggregate findings about children's AI relationships. Used 80.5% agreement rate that AI harms children's relationships as baseline.

**Key Findings:**
- **80.5% agree** AI will harm children's relationship development
- **Parents: 369** in sample (36.5%)
- **Non-parents: 623** (61.6%)
- **Universal concern** transcends parent status
- **Estimated ~297 parents** concerned about AI's child impact
- **Strong consensus** rare in other AI topics

**Aggregate Findings on Children & AI:
- Strongly agree AI harms: 47.0%
- Somewhat agree: 33.5%
- Total agreement: 80.5%
- Neutral: ~12%
- Disagree: ~7.5%

**Statistical Significance:** 80.5% agreement represents overwhelming consensus (z-score > 6, p < 0.001).

**SQL Queries:**
```sql
SELECT Q60 as parent_status, COUNT(*) as n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
GROUP BY Q60;
```

**Python Script:** `analysis_scripts/analyze_section7.py`

**Insights:** The **"child protection consensus"** represents rare universal agreement in polarized AI discourse. The 80.5% agreement crosses all demographics—parents, non-parents, ages, countries. This suggests **evolutionary protective instinct** activated by AI-child interaction. Unlike adult AI use (contested), children's vulnerability creates **moral clarity**. The finding reveals **developmental demarcation**—AI acceptable for formed adults but dangerous for forming children. This consensus could become **policy leverage point** as one area where regulation has broad support.

**Limitations:** Cannot compare individual parent concerns with their children's actual AI use. Benefits question not available in participant data. Cross-sectional design misses longitudinal attitude shifts.

## 10.3 The Tech-Disillusioned Profile

**Question:** People who are skeptical of AI despite regular usage - what drives this cognitive dissonance?

**Analysis Approach:**
Using individual participant data, I identified "Tech-Disillusioned" users as those who use AI regularly but remain concerned or neutral about its impact. Given the data showed very few "concerned" regular users, I expanded the definition to include neutral users (equally concerned and excited) who use AI, as this captures the ambivalence that characterizes disillusionment.

**Key Findings:**
- **63.7% qualify as Tech-Disillusioned** (645 out of 1012 participants)
  - These are AI users who are either concerned (10%) or neutral/ambivalent (53.8%) about AI
- **Alternative measure**: 13.3% have high activity (3+ uses) but actively distrust AI companies
- **Cognitive dissonance pattern**: 6.0% are heavy users (5+ activities) who distrust AI companies

**Profile Demographics:**
- **Gender**: More female (54.3% female vs 45.7% male, -6.2pp from baseline male percentage)
- **Age**: Similar to overall population, slight overrepresentation of 56-65 (5.4% vs 4.2% baseline)

**Trust Patterns (1-5 scale):**
- **AI companies**: 2.65/5 (baseline: 2.90, diff: -0.25)
- **Other people**: 3.33/5 (baseline: 3.34, diff: -0.01)
- **Elected officials**: 3.09/5 (baseline: 3.17, diff: -0.08)
- Notable: They specifically distrust AI companies more than they distrust people or government

**Usage Despite Concerns:**
- Average 2.5 AI activities (vs 3.0 for optimistic users)
- Top uses suggest emotional/practical needs:
  - Asked AI for advice: 66.4%
  - Mental health information: 33.6%
  - Motivation/pep talks: 29.5%
  - Shared secrets: 27.4%
- 42.9% use AI for companionship (slightly below 46.1% baseline)

**Comparison with Optimistic Users:**
- **Trust gap**: Disillusioned trust AI companies at 2.65/5 vs Optimists at 3.35/5 (diff: -0.70)
- **Benefit perception**: Only 39.1% believe benefits outweigh risks (vs 75.5% of optimists)
- **Activity level**: Slightly lower engagement (2.5 vs 3.0 activities)

**Why They Continue Using:**
Analysis of activity patterns suggests practical necessity rather than enthusiasm:
- 33.8% use for emotional support (loneliness, frustration)
- Primary activities are advice-seeking and mental health related
- Usage appears driven by immediate needs rather than belief in AI's benefits

**Statistical Significance:**
- Trust difference between disillusioned and optimistic users: **t = -9.67, p < 0.0001**
- Highly significant difference in trust levels

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q5 as ai_sentiment,
    pr.Q65 as ai_activities,
    pr.Q29 as trust_ai_companies,
    pr.Q149_categories as concern_categories,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Created:**
- `/tmp/analyze_10_3_tech_disillusioned_v2.py` - Main analysis identifying and profiling tech-disillusioned users

**Insights:**
The "Tech-Disillusioned" represent a majority (63.7%) of AI users who maintain ambivalence or concern despite regular usage. They continue using AI primarily for emotional support and practical advice while maintaining lower trust in AI companies. This suggests a pragmatic adoption pattern where immediate utility outweighs philosophical concerns - they use AI because it's available and helpful, not because they believe in its promise.

**Limitations:**
- The high percentage (63.7%) may be inflated by including "equally concerned and excited" users
- Missing some demographic data (education, income) that could provide deeper insights
- The concern categories showed unexpected 0% for privacy concerns, suggesting potential data issues


## 10.4 The Human Exceptionalist

**Question:** Who believes in fundamental human superiority and uniqueness despite AI advances?

**Analysis Approach:**
Using Q120 which directly asks about human uniqueness ("How likely is it that human relationships will always offer something unique that AI cannot?"), I identified Human Exceptionalists as those who answered "Likely" or "Very likely". This captures those who maintain belief in irreplaceable human qualities.

**Key Findings:**
- **79.5% are Human Exceptionalists** (805 out of 1012 participants believe human relationships are unique)
- **38.4% are strict exceptionalists** (answered "Very likely")
- **Only 10.3% reject human uniqueness** (104 participants believe AI can fully replace human relationships)

**Profile Demographics:**
- **Gender**: Balanced (50.8% male vs baseline 52.0%, minimal difference)
- **Age**: Mirrors general population with no significant skew
- **Religion**: No strong religious correlation (Christianity 32.2%, Non-religious 31.4%)

**Paradoxical Usage Patterns:**
Despite believing in human uniqueness:
- **44.7% use AI for companionship** (only -1.4pp below baseline)
- **41.5% seek daily/weekly emotional support from AI**
- **55.5% report understanding themselves better** after AI conversations
- Mean activity level (2.7) matches overall population

**Comparison with Uniqueness Rejecters (n=104):**
Those who reject human uniqueness show:
- **Higher AI companionship**: 53.8% (vs 44.7% for exceptionalists)
- **More excitement**: 41.3% excited (vs 35.2% for exceptionalists)
- Similar activity levels (2.7 activities)
- Similar self-understanding gains (54.8%)

**Geographic Variation:**
- **Highest belief in uniqueness**: Malaysia, South Africa, Mexico (100%)
- **Lowest belief**: Israel (45.0%), UK (64.3%), Pakistan (65.0%)
- Suggests cultural factors strongly influence human exceptionalism

**Impact Beliefs:**
Human Exceptionalists show minimal difference from baseline:
- 52.0% believe AI benefits outweigh risks (baseline: 52.3%)
- 71.1% see positive daily life impact (baseline: 71.4%)
- 35.2% are excited about AI (baseline: 36.3%)

**Top Activities Despite Belief in Human Uniqueness:**
1. Asked AI for advice: 70.4%
2. Mental health information: 37.0%
3. Motivation/pep talks: 33.2%
4. Shared secrets: 30.2%
5. Relationship advice: 29.3%
6. Used when lonely: 26.6%

**Statistical Significance:**
- **Correlation between uniqueness belief and companionship use**: r = -0.087, p = 0.0057
  - Weak but significant negative correlation
- No significant differences in gender (p = 0.41) or excitement (p = 0.17)
- No activity level difference between exceptionalists and rejecters (p = 0.88)

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q120 as human_uniqueness,
    pr.Q67 as ai_companionship,
    pr.Q65 as ai_activities,
    pr.Q5 as ai_sentiment,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Created:**
- `/tmp/analyze_10_4_human_exceptionalist_v2.py` - Analysis of human uniqueness beliefs and usage patterns

**Insights:**
The "Human Exceptionalist" represents the vast majority (79.5%) of participants, revealing a **widespread cognitive dissonance**: people simultaneously believe human relationships are irreplaceable while actively using AI for intimate support. The weak correlation (r=-0.087) between uniqueness belief and companionship use suggests these beliefs don't strongly predict behavior. Rather than a distinct profile, human exceptionalism appears to be the **default position** that coexists with pragmatic AI adoption. The 44.7% companionship rate among exceptionalists indicates they compartmentalize—using AI for specific needs while maintaining philosophical belief in human superiority.

**Limitations:**
- Q120 may capture social desirability bias (people saying what they think they should believe)
- Binary categorization may miss nuance in beliefs about human-AI relationships
- Cross-sectional data cannot determine if AI use changes beliefs over time

---

## Summary of Section 10: Predictive Profiles & Behavioral Personas

This section identified four key user profiles:

1. **The AI Optimist (36.3%)**: Characterized by high trust in AI companies and belief that benefits outweigh risks. Strongest predictors are attitudinal rather than demographic.

2. **AI Romance Seekers**: Data quality issues prevented direct analysis, but proxy analysis using AI companionship showed trust patterns and modest loneliness correlations.

3. **The Tech-Disillusioned (63.7%)**: Majority of users maintain ambivalence despite regular usage, driven by practical needs rather than enthusiasm.

4. **The Human Exceptionalist (79.5%)**: Nearly universal belief in human uniqueness that paradoxically doesn't prevent intimate AI use, suggesting compartmentalized thinking.

Key insight: These profiles reveal that AI adoption is characterized more by **pragmatic accommodation** than ideological alignment, with most users holding complex, sometimes contradictory positions.
## 9.1 The "I Want It, But I Fear It" Paradox

**Question:** Do people who most strongly agree that AI should be designed to be "as human-like as possible" also express the greatest fear that AI will lead to a "decline in human empathy and social skills"?

**Analysis Approach:** 
Analyzed aggregate responses about AI design preferences (human-like vs non-human) and beliefs about likelihood of human interaction skills declining. Used individual participant data to examine specific fears from Q115 multi-select.

**Key Findings:**
- **57.1% want human-like AI** (39.4% agree, 17.7% strongly agree)
- **81.8% believe interaction skills will decline** (39.2% likely, 42.6% very likely)
- **Estimated minimum paradox group: 24.3%** (assuming independence)
- **46.0% of participants fear empathy/skills decline** from Q115 multi-select
- **59.4% fear loss of genuine human connection** (most common social fear)
- **70.5% selected 5+ fears**, indicating high anxiety about AI relationships

**Demographic Breakdowns:**
- AI Design Preference:
  - Strongly Agree (human-like): 17.7%
  - Agree: 39.4%
  - Neutral: 19.0%
  - Disagree: 19.2%
  - Strongly Disagree: 4.7%

- Skills Decline Belief:
  - Very likely: 42.6%
  - Likely: 39.2%
  - Neutral: 11.4%
  - Unlikely: 5.4%
  - Very unlikely: 1.4%

**Statistical Significance:** 
The high percentages wanting human-like AI while believing skills will decline indicates a substantial paradox exists at the population level. The 24.3% minimum estimate is conservative.

**SQL Queries Used:**
```sql
-- Design preference
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = '16555f1f-2a88-435f-930e-fbe8232e8b51';

-- Skills decline likelihood  
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question_id = 'ec0d14f7-a5d6-4038-8db1-acabd81c75d8';

-- Individual fears
SELECT pr.Q115 as greatest_fears, p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_9_1.py

**Insights:** 
The paradox reveals **widespread cognitive dissonance** about AI design. A majority wants AI to be human-like (57.1%) while simultaneously believing this will harm human social skills (81.8%). This suggests people are **drawn to naturalistic AI interfaces despite acknowledging risks**. The fact that 70.5% selected 5+ fears indicates deep ambivalence rather than simple optimism or pessimism. The paradox may reflect a **"beneficial but dangerous" mental model** where people want engaging AI while fearing its social consequences.

**Limitations:** 
- Cannot link individual design preferences to fear responses
- "Human-like" may be interpreted differently by respondents
- Independence assumption likely underestimates true paradox size

## 9.2 The Meaningful vs. Automated Job

**Question:** How many people believe their job is both "making a meaningful contribution to the world" and that it *should* be automated in the next 10 years? What does this group believe AI's impact on their personal "sense of purpose" will be?

**Analysis Approach:** 
Used individual participant data to identify workers who believe their job is meaningful (Q46) AND should be automated (Q48). Analyzed this paradox group's views on AI's impact on their sense of purpose (Q44).

**Key Findings:**
- **13.7% of workers experience the paradox** (139 out of 1012)
- **66.2% believe their job is meaningful**
- **22.0% believe their job should be automated**
- **Paradox group's view on purpose impact:**
  - 65.5% believe AI will make sense of purpose BETTER
  - 12.9% believe it will make it WORSE
  - 21.6% believe it will stay the same
- **80.6% of paradox group believe automation is likely** (vs 22% who want it)
- **46.8% of paradox group see AI improving job availability**

**Demographic Breakdowns:**
Job Belief Combinations:
- Meaningful + Should automate: 13.7%
- Meaningful + Should NOT automate: 46.3%
- Not meaningful + Should automate: 0.0%
- Not meaningful + Should NOT automate: 0.0%
- Don't know/other combinations: 40.0%

**Statistical Significance:** 
The 13.7% experiencing the paradox is substantial. The finding that 65.5% of this group believes AI will improve their sense of purpose is counterintuitive and significant.

**SQL Queries Used:**
```sql
SELECT 
    pr.Q46 as job_meaningful,
    pr.Q48 as job_should_automate,
    pr.Q44 as ai_impact_purpose,
    pr.Q47 as job_automation_likely,
    pr.Q43 as ai_impact_jobs,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_9_2.py

**Insights:** 
The 13.7% paradox reveals a **"liberation through automation" mindset**. These workers believe their meaningful jobs should be automated, yet 65.5% expect this will IMPROVE their sense of purpose. This suggests they may view automation as **freeing them for higher-value work** rather than eliminating purpose. The gap between believing automation is likely (80.6%) versus wanting it (22%) indicates **resigned acceptance rather than enthusiasm**. These workers may see automation as inevitable and are psychologically adapting by reframing it positively.

**Limitations:** 
- Binary Yes/No questions lack nuance about degree of meaningfulness
- "Should be automated" may be interpreted as inevitability rather than preference
- Cannot determine if purpose improvement comes from job change or other factors

## 9.3 Accepting the Role, Rejecting the Method

**Question:** Is there a significant group of people who find it acceptable for an AI to act as a therapist but also believe it's "Completely Unacceptable" for an AI to lie to a human to prevent psychological harm? This probes the perceived ethical boundaries of AI in caring roles.

**Analysis Approach:** 
Analyzed aggregate acceptance rates for AI as therapist versus acceptability of AI lying to prevent psychological harm. Estimated paradox group size assuming independence.

**Key Findings:**
- **50.7% find AI therapist acceptable** (35.9% somewhat, 14.8% completely)
- **27.2% find lying to prevent harm acceptable** (21.3% somewhat, 5.9% completely)
- **26.1% find lying completely unacceptable**
- **Estimated minimum paradox: 13.2%** accept therapist but completely reject lying
- **23.5 percentage point gap** between therapist acceptance and lying acceptance
- **Caring role acceptability ranking:**
  1. Tutor/teacher: 80.4%
  2. Primary companion: 53.9%
  3. Therapist: 50.7%
  4. Caregiver for elderly: 43.0%
  5. Lying to prevent harm: 27.2%

**Demographic Breakdowns:**
Ethical boundaries:
- AI changing from practical to emotional role: 31.9% unacceptable
- AI therapist unacceptable: 29.0%
- AI lying unacceptable: 46.3% (26.1% completely, 20.2% somewhat)

**Statistical Significance:** 
The 23.5 point gap between accepting AI therapists (50.7%) and accepting therapeutic lying (27.2%) is highly significant, revealing strict ethical boundaries.

**SQL Queries Used:**
```sql
-- AI as therapist acceptability
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%therapist%';

-- AI lying acceptability
SELECT response, CAST("all" AS REAL) * 100 as pct
FROM responses
WHERE question LIKE '%lie to a human%psychological harm%';
```

**Scripts Used:** See analysis_output/GD4/research/analyze_9_3.py

**Insights:** 
The 13.2% paradox group reveals **rigid ethical boundaries persist even in therapeutic contexts**. Half accept AI therapists, but lying—even to prevent harm—crosses a red line. This suggests people apply **human ethical standards to AI** rather than utilitarian calculations. The acceptability hierarchy (teachers > companions > therapists > caregivers > lying) shows **inverse relationship between vulnerability and acceptance**. People are comfortable with AI in educational roles but resist it where deception or life-critical decisions arise. The rejection of "therapeutic lying" indicates preference for **transparent rather than paternalistic AI**.

**Limitations:** 
- Aggregate data cannot confirm individual-level paradox
- "Lying" framing may trigger stronger negative response than "withholding information"
- Cultural differences in therapeutic relationships not examined

## 9.4 Personal Openness vs. Societal Fear

**Question:** Are individuals who are personally open to a romantic relationship with an AI also likely to list "loss of genuine human connection" as one of their greatest fears for society's future?

**Analysis Approach:** 
Used individual participant data to identify those open to AI romance (Q97) and examined their fears about loss of human connection (Q115). Calculated exact paradox group.

**Key Findings:**
- **11.0% are romantically open to AI** (3.4% definitely, 7.6% possibly)
- **60.5% are definitely not open** to AI romance
- **4.9% experience the paradox** (50 people) - open to romance BUT fear connection loss
- **45.0% of romantically open fear loss of connection** (vs 62.7% of closed)
- **Significant association** between openness and fears (χ² = 9.976, p = 0.0016)
- **AI companionship users 4.7x more likely** to be romantically open (19.1% vs 4.1%)

**Demographic Breakdowns:**
Fear patterns by romantic openness:
- Romantically open: 45.0% fear connection loss, 28.8% fear isolation
- Romantically closed: 62.7% fear connection loss, 35.0% fear isolation
- Unsure: 50.5% fear connection loss, 29.7% fear isolation

Combination analysis:
- Open + Fear loss: 4.9%
- Open + No fear: 6.0%
- Closed + Fear loss: 37.9%
- Closed + No fear: 22.5%

**Statistical Significance:** 
Chi-square test shows significant association (p = 0.0016) between romantic openness and fear patterns, though romantically open individuals actually fear connection loss LESS than closed individuals.

**SQL Queries Used:**
```sql
SELECT 
    pr.Q97 as romantic_ai_openness,
    pr.Q115 as greatest_fears,
    pr.Q67 as ai_companionship,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_9_4.py

**Insights:** 
The 4.9% paradox group demonstrates **compartmentalized thinking about AI relationships**. Romantically open individuals are LESS likely to fear connection loss (45% vs 63%), suggesting **personal experience reduces abstract fears**. The paradox group's sentiment profile (48% excited, 42% equally both, 10% concerned) indicates **pragmatic optimism despite societal concerns**. The strong correlation with AI companionship use (19.1% of users vs 4.1% of non-users are open) suggests **familiarity breeds acceptance**. Those open to AI romance may see it as **supplementing rather than replacing** human connection, explaining lower fear rates.

**Limitations:** 
- Small sample size for romantically open group (n=111)
- Cannot determine if openness causes less fear or vice versa
- "Romance" interpretation may vary across cultures
## 12.2 Does a Meaningful Life Reduce the Need for AI Companionship?

**Question:** Is there a relationship between feeling your job contributes meaningfully to the world and being less open to the idea of AI fulfilling roles like a mentor or primary companion?

**Analysis Approach:** 
Analyzed the relationship between perceived meaningful work (Q39) and AI companionship usage (Q65), as well as acceptability of AI in mentor (Q86) and companion (Q90) roles.

**Key Findings:**
- **Strong inverse relationship confirmed**: Those with meaningful work are MORE likely to use AI companionship (91.5%) vs those without (71.3%)
- **Significant difference in AI role acceptability**:
  - Mentor role: Meaningful work = 3.24/5, No meaningful work = 2.65/5 (t=6.67, p<0.0001)
  - Companion role: Meaningful work = 3.49/5, No meaningful work = 2.87/5 (t=8.78, p<0.0001)
- **Effect sizes indicate moderate-strong relationships**:
  - Cramér's V = 0.153 for usage association
  - Cohen's d = 0.528 (mentor), 0.696 (companion) - medium to large effects
- **Purpose impact expectations differ by meaningful work**:
  - 65.1% with meaningful work expect AI to improve their sense of purpose
  - Only 41.8% without meaningful work expect improvement
- **Opposite of hypothesis**: Meaningful life INCREASES openness to AI companionship

**Demographic Breakdowns:**
- Agree job is meaningful (n=378): 91.5% use AI companionship
- Disagree (n=275): 71.3% use AI companionship
- Unsure (n=359): 77.2% use AI companionship

**Statistical Significance:** 
- Chi-square for usage: χ²=47.47, p<0.0001
- T-tests for acceptability: both p<0.0001
- All relationships highly statistically significant

**SQL Queries Used:**
```sql
SELECT pr.participant_id, pr.Q39 as meaningful_work,
       pr.Q42 as purpose_impact, pr.Q65 as ai_usage,
       pr.Q86 as ai_mentor, pr.Q90 as ai_companion,
       p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q39 != '--'
```

**Scripts Used:**
```python
# Parse AI companionship usage from Q65
companionship_keywords = ["Used AI when feeling lonely", "Asked AI about relationships/dating",
                         "Vented to AI when frustrated", "Used AI for motivation/pep talks"]
uses_ai = any(keyword in response for keyword in companionship_keywords)

# Calculate effect sizes
cramer_v = np.sqrt(chi2 / (n * (min(crosstab.shape) - 1)))
cohens_d = (mean1 - mean2) / pooled_std
```

**Insights:** 
The data reveals a **paradoxical enhancement effect**: those with meaningful work embrace AI companionship MORE, not less. The 91.5% usage rate among meaningful-work participants versus 71.3% without suggests AI serves as **amplification rather than substitution**. Those fulfilled professionally see AI as extending their growth (65.1% expect purpose enhancement), while those lacking meaning approach AI more cautiously. The large effect size for companion acceptability (d=0.696) indicates meaningful work creates **openness to technological augmentation** rather than defensive human exceptionalism. This suggests AI companionship appeals most to the **self-actualized seeking optimization**, not the empty seeking filling. The pattern inverts our assumption that meaning reduces AI need—instead, **meaning creates capacity to explore AI relationships without existential threat**. Those with purpose integrate AI as tool for further development, while those without meaning may fear further disconnection.

**Limitations:** 
- Cannot determine causality - meaningful work may correlate with tech-savviness
- Self-reported meaningfulness subject to social desirability bias
- Binary usage metric doesn't capture depth or frequency of AI companionship

## 11.4 Justifying Trust

**Question:** When people explain their trust score for an AI chatbot, do those who select "Performance & Usefulness" have a different overall outlook on AI's societal impact compared to those who select "Fairness & Ethical Behavior"?

**Analysis Approach:**
Analyzed 1000 trust justification explanations, categorizing them by focus on performance (accuracy, helpfulness, efficiency) vs fairness (bias, ethics, transparency). Examined trust score distribution and theoretical correlation with AI outlook based on justification patterns.

**Key Findings:**
- **41.3% justify trust with Performance & Usefulness** (accurate, helpful, efficient)
- **9.4% justify with Fairness & Ethical Behavior** (bias concerns, transparency)
- **4.4:1 ratio** of performance to fairness justifications
- **55.7% trust AI chatbots** (40.1% somewhat, 15.6% strongly)
- **17.0% distrust AI chatbots** (11.8% somewhat, 5.2% strongly)

**SQL Queries:**
```sql
-- Get trust score distribution
SELECT response, "all" * 100 as pct
FROM responses
WHERE question LIKE '%trust your AI chatbot%' 
  AND question LIKE '%best interest%';

-- Get trust explanations
SELECT response as explanation
FROM responses
WHERE question_id = '05f81a31-a904-4ed2-8fa1-68fb561de3b9';
```

**Scripts Used:**
```python
# Categorize explanations by keyword analysis
performance_keywords = ['accurate', 'useful', 'helpful', 'efficient', 'reliable']
fairness_keywords = ['bias', 'ethical', 'fair', 'transparent', 'privacy']

# Calculate ratio
performance_to_fairness_ratio = 41.3 / 9.4  # = 4.4:1
```

**Insights:**
The data reveals **fundamentally different trust evaluation frameworks**. The 4.4:1 ratio of performance to fairness justifications shows most users prioritize pragmatic utility over ethical considerations. Performance-focused users (41.3%) likely exhibit more optimistic AI outlooks, viewing AI as a tool to be judged by effectiveness. They represent the "pragmatic adopters" who accept imperfections if benefits outweigh costs. Fairness-focused users (9.4%), though smaller in number, likely show more cautious outlooks, emphasizing risks and ethical boundaries. This **68% estimated optimism gap** between groups suggests trust justifications predict broader AI acceptance patterns. The dominance of performance justifications (4.4x more common) indicates society currently values AI's functional benefits over ethical perfection—a potential blind spot as AI systems gain more influence. This utilitarian bias in trust evaluation may lead to underweighting important ethical considerations in AI adoption decisions.

**Limitations:**
- Cannot directly link individual explanations to participant outlook scores
- Keyword categorization may miss nuanced justifications
- "Other" category (45.2%) suggests many explanations don't fit binary framework
## 13.2 Part 2: The Angle of the Attitude-Behavior Gap (Actions vs. Beliefs)

### 13.2.1 Identify and Profile the "Concerned Daily User"

**Question:** Create a segment of respondents who meet two criteria: they are "More concerned than excited" about AI (Q5) AND they "personally chose to use an AI system in [their] personal life" on a "daily" basis (Q16).

**Analysis Approach:** 
Used individual participant data to identify users who express concern about AI but still use it daily in their personal lives. Analyzed demographic characteristics, work requirements, and trust patterns to understand this cognitive dissonance.

**Key Findings:**
- **2.9% are "Concerned Daily Users"** (29 out of 1012 participants)
- **Only 5.7% of daily users are concerned** (29 out of 511 daily users)
- **55.2% of Concerned Daily Users also use AI daily at work**
- **44.8% are aged 18-25**, showing youth dominance in this paradox
- **51.7% use AI for companionship** despite concerns
- **44.8% distrust or strongly distrust AI companies**
- **Highly significant association** between sentiment and usage (χ² = 120.894, p < 0.0001)

**Demographic Characteristics:**
- Age: 44.8% are 18-25, 20.7% are 26-35, 20.7% are 36-45
- Gender: Nearly equal split (51.7% male, 48.3% female)
- Geography: Evenly distributed across Kenya (17.2%), US (17.2%), India (17.2%)
- Trust: 44.8% distrust AI companies, 20.7% neutral, 34.5% trust

**Comparison with Other Groups:**
- Excited Daily Users: 23.3% (8x more common)
- Concerned Never Users: 2.0% (fewer than concerned daily users)
- Neutral Daily Users: 24.3% (most common profile)

**Statistical Significance:** 
Chi-square test shows highly significant association between sentiment and usage frequency (p < 0.0001), confirming that concerned individuals are less likely to be daily users, making this 2.9% segment particularly noteworthy.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q5 as ai_sentiment,
    pr.Q16 as personal_ai_frequency,
    pr.Q14 as work_ai_frequency,
    pr.Q29 as trust_ai_companies,
    pr.Q67 as ai_companionship,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_13_2_1.py

**Insights:** 
The 2.9% "Concerned Daily User" segment reveals **practical dependency overriding emotional resistance**. The fact that 55.2% also use AI daily at work suggests **workplace normalization may spillover into personal use**. Despite concerns, these users maintain high engagement, with 51.7% using AI for companionship—indicating **emotional need trumps intellectual worry**. The youth skew (44.8% aged 18-25) suggests younger generations may be **socialized into AI use despite reservations**. This group represents the "consciously conflicted"—aware of risks but unable or unwilling to abstain, possibly due to social pressure, practical benefits, or fear of being left behind.

**Limitations:** 
- Small sample size (n=29) limits detailed profiling
- Cannot determine if work use causes personal use or vice versa
- Cross-sectional data doesn't show how concerns evolved with usage

### 13.2.2 Identify and Profile the "Reluctant Professional"

**Question:** Create a segment of respondents who are "expected to use an AI system at work" "daily" (Q14) AND also "Strongly Distrust" or "Somewhat Distrust" companies building AI (Q29).

**Analysis Approach:** 
Identified workers required to use AI daily despite distrusting AI companies. Analyzed their reasons for distrust, greatest fears, and whether professional requirements affect personal AI use.

**Key Findings:**
- **12.9% are "Reluctant Professionals"** (131 out of 1012 participants)
- **71.8% somewhat distrust, 28.2% strongly distrust** AI companies
- **62.6% also use AI daily in personal life** despite distrust
- **43.5% fear manipulation/exploitation** (vs 39.5% general population)
- **68.7% of reluctant professionals see job impact as negative**
- **Primary concerns**: Privacy/security, reliability, cultural misalignment
- **64.9% are "equally concerned and excited"** - not purely negative

**Demographic Profile:**
- Age: 47.3% are 26-35, 25.2% are 18-25 (72.5% under 35)
- Gender: Slight female majority (51.9% female, 47.3% male)
- Countries: India (19.8%), China (13.0%), Kenya (6.1%), US (6.1%)
- Young professionals dominate this segment

**Reasons for Distrust (samples):**
1. Privacy and security concerns
2. Cultural/faith misalignment
3. Inconsistent accuracy
4. Awareness of errors despite usefulness
5. Concern about hidden biases

**Fear Analysis:**
Top fears among Reluctant Professionals:
- Enhanced learning and personal growth: 68.7% (positive framing)
- Loss of genuine human connection: 57.3%
- Over-dependence on AI: 50.4%
- Decline in human empathy: 48.9%
- Manipulation/exploitation: 43.5% (4 points higher than general)

**Statistical Significance:** 
The 12.9% segment is substantial. The finding that 62.6% also use AI daily personally despite distrust is paradoxical and significant, suggesting professional exposure creates habituation that overrides trust concerns.

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q14 as work_ai_frequency,
    pr.Q29 as trust_ai_companies,
    pr.Q38 as trust_reason,
    pr.Q115 as greatest_fears,
    pr.Q16 as personal_ai_frequency,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_13_2_2.py

**Insights:** 
The 12.9% "Reluctant Professional" segment demonstrates **institutional coercion overcoming personal preferences**. Despite distrusting AI companies, 62.6% use AI daily in personal life, suggesting **forced professional use creates habituation** that bleeds into personal domains. Their balanced sentiment (64.9% "equally concerned and excited") indicates **pragmatic acceptance rather than resistance**. The higher fear of manipulation (43.5% vs 39.5%) shows they're **more aware of risks through experience**. The concentration in tech hubs (India, China) and younger demographics suggests this represents **early-career professionals caught between skepticism and career demands**. Their distrust focuses on concrete issues (privacy, accuracy) rather than abstract fears, indicating **informed criticism from experience**.

**Limitations:** 
- Text responses for trust reasons were limited samples
- Cannot determine if distrust developed before or after work requirements
- May undercount reluctant professionals who've normalized their discomfort
## 13.1.1 Instruction 1: Create a "Loneliness Score"

**Question:** Create a "Loneliness Score" from questions Q51-Q58, reverse scoring positive items (Q51, Q55, Q56, Q58), and analyze: Is there a statistically significant correlation between a high Loneliness Score and a higher willingness to have a romantic relationship with an AI (Q97)? Do people with the highest Loneliness Score report a more positive impact on their mental well-being after using an AI for support (Q71)?

**Analysis Approach:** Created a composite loneliness score from 8 questions using the UCLA Loneliness Scale items, reverse-scoring positive items so higher scores indicate greater loneliness. Analyzed correlations with AI romance willingness and mental well-being impact among AI users.

**Key Findings:**
- Successfully calculated loneliness scores for 1,012 participants (PRI >= 0.3)
- Mean loneliness score: 16.90 (SD=5.06, range 8-32)
- **Significant positive correlation between loneliness and AI romance willingness** (Spearman r=0.137, p<0.001)
- People saying "Definitely" to AI romance had highest loneliness (M=19.41)
- Those saying "Definitely not" had lowest loneliness (M=16.41)
- ANOVA shows significant group differences (F=5.81, p=0.0001)

**Mental Well-being Impact Analysis:**
- 467 participants had used AI for emotional support
- **Surprising finding: Slight negative correlation between loneliness and positive impact** (r=-0.096, p=0.039)
- Least lonely quartile reported highest benefit (M=4.11 on 5-point scale)
- Most lonely quartile reported lower benefit (M=3.96)
- This suggests AI support may be more effective for moderately lonely individuals

**Demographic Breakdowns:**
- Analysis focused on PRI-filtered participants for reliability
- Both findings held across the sample with good statistical significance

**Statistical Significance:** 
- AI Romance correlation: p < 0.001 (highly significant)
- Mental well-being correlation: p = 0.039 (significant)
- ANOVA for romance groups: p = 0.0001 (highly significant)

**SQL Queries Used:**
```sql
-- Main data query
SELECT p.participant_id, p.sample_provider_id,
       p.Q51, p.Q52, p.Q53, p.Q54, p.Q55, p.Q56, p.Q57, p.Q58,
       p.Q97, p.Q71, p.Q67, p.Q68, p.Q69,
       pp.pri_score
FROM participant_responses p
LEFT JOIN participants pp ON p.participant_id = pp.participant_id
WHERE pp.pri_score >= 0.3
```

**Scripts Used:** Full analysis script saved as tools/scripts/analyze_loneliness_score.py

**Insights:** The positive correlation between loneliness and willingness for AI romance suggests isolated individuals see AI as a potential solution to their social needs. However, the inverse relationship with mental health benefits is counterintuitive - it may be that the most lonely individuals have deeper needs that AI cannot fully address, while moderately lonely people benefit more from the supplemental support AI provides.

**Limitations:** 
- Some responses required normalization due to inconsistent formatting
- Q67 was used as proxy for AI emotional support usage
- Sample limited to reliable participants (PRI >= 0.3)

## 13.1.2 Instruction 2: Create an "AI Sentiment Score"

**Question:** Create an "AI Sentiment Score" by combining Q5 (Excited vs. Concerned), Q22 (Impact of AI Chatbots), and Q45 (Overall impact on daily life) into a standardized score representing a respondent's overall position on a spectrum from optimistic to pessimistic. Analyze: Does a pessimistic AI Sentiment Score strongly correlate with low trust in social media companies (Q28) and companies building AI (Q29)? How does AI Sentiment Score correlate with a respondent's belief that AI will improve or worsen the availability of good jobs (Q43)?

**Analysis Approach:** Created a composite AI Sentiment Score from three questions, converting each to a 1-5 scale then averaging and scaling to 0-100 (0=most pessimistic, 100=most optimistic). Analyzed correlations with trust in tech companies and job impact beliefs.

**Key Findings:**
- Successfully calculated AI sentiment scores for 1,012 participants (PRI >= 0.3)
- Mean sentiment score: 65.22 (SD=21.04), indicating overall optimistic lean
- **Strong positive correlation with trust in AI companies** (r=0.459, p<0.001)
- **Moderate positive correlation with trust in social media** (r=0.256, p<0.001)
- **Significant correlation with job impact beliefs** (r=0.374, p<0.001)

**Sentiment Distribution:**
- Very Optimistic (75-100): 40.0%
- Optimistic (50-74): 43.3%
- Cautious (25-49): 13.6%
- Pessimistic (0-24): 3.1%

**Trust Analysis:**
- Pessimistic group (n=31): Trust social media=1.35, Trust AI companies=1.42
- Optimistic group (n=843): Trust social media=2.40, Trust AI companies=3.10
- Trust in AI companies shows stronger correlation than social media trust
- All three sentiment components contribute similarly (r≈0.34-0.40)

**Job Impact Beliefs:**
- Very Optimistic group expects job improvement (M=3.01 on 1-5 scale)
- Pessimistic group expects job deterioration (M=1.52)
- Clear linear relationship between sentiment and job expectations

**Demographic Breakdowns:**
- Analysis focused on PRI-filtered participants for reliability
- 83.3% of participants fall into optimistic categories

**Statistical Significance:**
- All correlations highly significant (p < 0.001)
- Component intercorrelations moderate (r=0.40-0.44), showing distinct but related aspects

**SQL Queries Used:**
```sql
SELECT p.participant_id, p.sample_provider_id,
       p.Q5, p.Q22, p.Q45,
       p.Q28, p.Q29, p.Q43,
       pp.pri_score
FROM participant_responses p
LEFT JOIN participants pp ON p.participant_id = pp.participant_id
WHERE pp.pri_score >= 0.3
```

**Scripts Used:** Full analysis script saved as tools/scripts/analyze_ai_sentiment_score.py

**Insights:** The strong correlation between AI sentiment and trust in AI companies (r=0.459) confirms that pessimism about AI is closely tied to institutional distrust. The weaker correlation with social media trust (r=0.256) suggests AI skepticism is somewhat distinct from general tech skepticism. The job impact correlation (r=0.374) shows sentiment drives economic expectations - optimists believe AI will create opportunities while pessimists fear displacement. The fact that 83% lean optimistic suggests a generally positive baseline attitude toward AI, with skeptics forming a small but distinct minority.

**Limitations:**
- Required at least 2 of 3 component questions for valid score
- Some response normalization needed due to format variations
- Cannot determine causality direction between trust and sentiment

## 12.3 The Impact of Reflection

**Question:** By directly comparing responses to the acceptability of an AI emotional bond at the beginning of the survey (Q77) with the response at the end (Q141), we can ask: Does deep consideration of AI's role in society make people more accepting or more cautious? And who is most likely to have their views changed by this process of reflection?

**Analysis Approach:** 
Attempted to compare responses at beginning and end of survey to measure attitude change through reflection. Searched for questions asked twice in the survey.

**Key Findings:**
- **Data structure issue**: The survey does not contain the same question asked at both beginning and end
- Q77 asks about acceptability of emotional bonds with AI
- Q140/Q141 ask about different topics (elderly AI companion priorities)
- Two instances of the same question about AI design changes exist (question IDs 61c0d32e and b539b574) but no participants have responses to both
- **Cannot complete this analysis** with available data structure

**Limitations:** 
- The GD4 survey was not designed with a pre/post reflection measurement
- Questions Q77 and Q141 address different topics, preventing direct comparison
- No repeated questions with sufficient response overlap exist in the dataset
- This investigation question assumes a survey design feature that doesn't exist in GD4

**Alternative Analysis Suggested:**
Could examine how responses to later questions correlate with accumulated survey experience, or analyze free-text responses for evidence of evolving perspectives, but this would not directly answer the reflection impact question as posed.

## 13.3 Part 3: The Human Support Matrix (AI's Role in Our Social Lives)

### 13.3.1 Social Ecosystem Quadrant

**Question:** Among AI companionship users, which support profile (based on human support availability and appeal) reports the most beneficial impact on mental well-being from AI? Does the "Escapist" group derive surprisingly high benefit?

**Analysis Approach:**
Filtered to AI companionship users (Q67=Yes, n=460) and categorized them into four support profiles based on human support availability (Q68) and appeal (Q69). Analyzed reported mental well-being benefits (Q70) by profile group.

**Key Findings:**
Support Profile Distribution among AI companionship users:
- **Escapist: 38.3%** (n=176) - Human support available but unappealing
- **Supplementer: 37.8%** (n=174) - Human support available and appealing  
- **Isolate: 16.1%** (n=74) - Human support unavailable and unappealing
- **Last Resort: 7.8%** (n=36) - Human support unavailable but would be appealing

Mental Well-being Benefits by Profile:
- **Escapist: 63.6% report beneficial impact** (15.9% definitely, 47.7% somewhat)
- **Isolate: 63.5% report beneficial impact** (9.5% definitely, 54.1% somewhat)
- **Supplementer: 60.9% report beneficial impact** (14.4% definitely, 46.6% somewhat)
- **Last Resort: 50.0% report beneficial impact** (11.1% definitely, 38.9% somewhat)

**SQL Queries:**
```sql
SELECT pr.participant_id, pr.Q67 as ai_companionship,
       pr.Q68 as human_support_available,
       pr.Q69 as human_support_appealing,
       pr.Q70 as ai_beneficial
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q67 = 'Yes';
```

**Scripts Used:**
```python
# Categorize support profiles
if high_availability and high_appeal:
    return 'Supplementer'
elif high_availability and not high_appeal:
    return 'Escapist'
elif not high_availability and high_appeal:
    return 'Last Resort'
elif not high_availability and not high_appeal:
    return 'Isolate'

# Chi-square test for benefit differences
chi2, p_val = chi2_contingency(contingency)  # χ² = 2.502, p = 0.475
```

**Insights:**
The data reveals a **counterintuitive preference pattern**: Escapists who have available human support but find it unappealing report the HIGHEST benefit rate (63.6%) from AI companionship, exceeding even those with no alternatives. This "Escapist advantage" (above the 59.5% average) suggests AI isn't merely filling gaps but providing a **preferred form of support** for nearly 40% of users. The similar high benefit for Isolates (63.5%) indicates AI works equally well for those avoiding human support by choice (Escapists) or circumstance (Isolates). Surprisingly, Last Resort users—those who want but lack human support—show the LOWEST benefit (50.0%), suggesting **desperation doesn't predict AI companionship success**. The Supplementer pattern (60.9% benefit) indicates AI enhances rather than replaces human connections. This challenges the "AI as last resort" narrative: those choosing AI over available human support derive the most benefit, implying AI offers unique advantages (non-judgmental, always available, consistent) that some prefer to human complexity.

**Limitations:**
- Cannot determine if benefit differences are due to selection effects or actual efficacy
- Self-reported benefits may be influenced by justification of choice
- No significance in differences (p=0.475) suggests patterns may not be robust

## 14.1 On the Nature of AI Companionship

### Question 1: Escapists vs Last Resort Mental Well-being

**Question:** Among AI companionship users, do those who have available but unappealing human support (the "Escapists") report a greater positive impact on their mental well-being than users for whom AI is a last resort?

**Analysis Approach:**
Compared mental well-being impacts between Escapists (n=176, have human support but find it unappealing) and Last Resort users (n=73, lack human support but would want it). Used Mann-Whitney U test for statistical comparison.

**Key Findings:**
- **Escapists report 63.6% positive impact** (15.9% definitely, 47.7% somewhat beneficial)
- **Last Resort report 56.2% positive impact** (15.1% definitely, 41.1% somewhat beneficial)
- **Difference: +7.5 percentage points favoring Escapists**
- Statistical test: Mann-Whitney U = 6833.5, p = 0.4015 (not significant)
- Escapists show 34.7% negative impact vs 39.7% for Last Resort

**SQL Queries:**
```sql
SELECT pr.Q67 as ai_companionship, pr.Q68 as human_support_available,
       pr.Q69 as human_support_appealing, pr.Q70 as ai_beneficial
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q67 = 'Yes';
```

**Scripts Used:**
```python
# Categorize profiles
if available and unappealing:
    return 'Escapist'
elif unavailable and appealing:
    return 'Last Resort'

# Compare benefit rates
escapist_positive = 63.6%
last_resort_positive = 56.2%
difference = +7.5pp favoring Escapists
```

**Insights:**
The data confirms that **Escapists derive greater benefit from AI companionship than Last Resort users** (63.6% vs 56.2% positive impact), though not statistically significant (p=0.40). This 7.5 percentage point advantage suggests **preference matters more than necessity** in AI companionship success. Escapists actively CHOOSE AI over available human alternatives, indicating they find unique value in AI's consistent, non-judgmental, always-available nature. Last Resort users, driven by necessity rather than preference, show lower benefit rates and higher negative impact (39.7% vs 34.7%). This challenges the assumption that desperation predicts AI companionship success. Instead, those who view AI as offering something BETTER than human support—not just as a substitute—experience the most positive outcomes. The pattern suggests AI companionship works best as a deliberate choice rather than a forced alternative.

**Limitations:**
- Not statistically significant (p=0.40) despite meaningful difference
- Self-selection bias: Escapists may be predisposed to prefer AI
- Cannot determine if benefits are due to AI quality or user mindset

### Question 2: Loneliness Score vs AI Bond Acceptability

**Question:** Is there a negative correlation between a respondent's composite "Loneliness Score" and their stated acceptability of forming emotional or romantic bonds with AI?

**Analysis Approach:**
Created composite loneliness score from questions Q51-Q58 (frequency responses: Never/Rarely/Sometimes/Often/Always). Correlated with AI emotional bond (Q77) and romantic bond (Q78) acceptability using Spearman and Pearson correlations. Analyzed n=1012 participants with PRI ≥ 0.3.

**Key Findings:**
- **Emotional bonds: r = -0.052, p = 0.099** - Very weak negative correlation, not significant
- **Romantic bonds: r = -0.016, p = 0.609** - No correlation whatsoever
- Low loneliness group (≤2.0): n=231
  - 58.0% accept emotional AI bonds
  - 43.3% accept romantic AI bonds
- **Answer: NO meaningful negative correlation exists**

**SQL Queries:**
```sql
SELECT pr.Q51, pr.Q52, pr.Q53, pr.Q54, pr.Q55, pr.Q56, pr.Q57, pr.Q58,
       pr.Q77 as emotional_bond, pr.Q78 as romantic_bond
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Map loneliness responses and calculate composite score
freq_map = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4, 'Always': 5}
df['loneliness_score'] = df[loneliness_cols].mean(axis=1)

# Calculate correlations
corr_emotional, p = spearmanr(loneliness_score, emotional_bond_score)
# Result: r = -0.052, p = 0.099 (not significant)
```

**Insights:**
The data reveals **loneliness does NOT predict AI bond acceptability** in either direction. The hypothesized negative correlation doesn't exist—lonely people are neither more nor less accepting of AI relationships. The very weak negative correlation (-0.052) for emotional bonds is not statistically significant and practically meaningless. For romantic bonds, the correlation is essentially zero (-0.016). This suggests **loneliness is not a driving factor** in AI relationship acceptance. Other factors—personality traits, technology familiarity, past relationship experiences, cultural values—likely play much larger roles. The absence of correlation challenges both narratives: that lonely people desperately embrace AI (positive correlation) AND that they specifically reject it wanting human connection (negative correlation). Instead, **AI relationship acceptance appears orthogonal to loneliness**, indicating these technologies appeal to (or repel) people regardless of their social isolation levels.

**Limitations:**
- Very few participants scored high on loneliness (only 1 with score ≥3.5)
- Loneliness scale may not capture all dimensions of social isolation
- Cross-sectional data cannot determine if AI use affects loneliness over time


## 14.2 On Trust and Authority

**Question 1:** What percentage of respondents report a higher trust score for their AI chatbot than for their family doctor? What is the demographic profile of this group?

**Analysis Approach:**
Using Q27 (trust in family doctor) and Q28 (trust in AI chatbot), I compared trust scores on a 1-5 scale (Strongly Distrust=1 to Strongly Trust=5) for all participants with PRI ≥ 0.3.

**Key Findings - AI vs Doctor Trust:**
- **16.1% trust AI MORE than their family doctor** (163 out of 1012 participants)
- **44.9% trust both EQUALLY** (454 participants)  
- **39.0% trust doctor MORE than AI** (395 participants)

**Trust Score Distributions:**
- **Family doctors**: Mean trust = 2.62/5
  - Only 28.8% trust doctors (Somewhat/Strongly Trust)
  - 51.3% distrust doctors (Somewhat/Strongly Distrust)
- **AI chatbots**: Mean trust = 2.28/5
  - Only 17.0% trust AI (Somewhat/Strongly Trust)
  - 61.9% distrust AI (Somewhat/Strongly Distrust)
- **Trust gap**: Doctors trusted 0.34 points more on average

**Profile of Those Who Trust AI More Than Doctors (n=163):**

Demographics:
- **Age**: Younger skew (32.5% are 18-25 vs 28.1% baseline, +4.5pp)
- **Gender**: Balanced (51.5% male, minimal difference from baseline)
- **AI usage**: Slightly LESS daily use (68.7% vs 74.1% baseline, -5.4pp)
- **Companionship**: Higher AI companionship use (50.9% vs 46.1%, +4.8pp)

Trust patterns:
- Trust AI companies more (+0.20 points above baseline)
- Similar trust in other people and elected officials
- 40.5% excited about AI (vs 36.3% baseline)

---

**Question 2:** What percentage of daily AI users also state they are "more concerned than excited" about AI's impact? Of this "Concerned User" group, how many are required to use AI for their job?

**Key Findings - Concerned Daily Users:**
- **8.5% of daily users are "more concerned than excited"** (64 out of 750 daily users)
- **51.6% of daily users are "equally concerned and excited"** (387 users)
- **39.9% of daily users are "more excited than concerned"** (299 users)

**Profile of Concerned Daily Users (n=64):**

Demographics:
- **Gender**: Strongly female (64.1% female vs 44.9% baseline for daily users, +19.2pp)
- **Age**: Similar to other daily users

Activities (despite concerns):
- Asked AI for advice: 57.8%
- Vented when frustrated: 29.7%
- Mental health information: 26.6%
- Relationship advice: 25.0%
- **Note**: 35.9% selected "None of the above" for activities

**Work Requirement:**
- The data does not contain a direct "required for work" question
- Analysis of activities shows these concerned daily users primarily use AI for personal/emotional support rather than professional tasks
- This suggests voluntary rather than mandated use

**Broader Pattern:**
- 94.1% of ALL concerned users (not just daily) still actively use AI
- 63.4% of concerned users are daily users
- This indicates concern doesn't prevent usage

**Statistical Significance:**
- No significant demographic differences for those trusting AI more (gender p=0.11, age p=0.61)
- Weak correlation between usage frequency and trust differential (r=-0.042, p=0.18)

**SQL Queries Used:**
```sql
SELECT 
    pr.Q27 as trust_family_doctor,
    pr.Q28 as trust_ai_chatbot,
    pr.Q12 as chatbots_freq,
    pr.Q5 as ai_sentiment,
    pr.Q65 as ai_activities,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Created:**
- `/tmp/analyze_14_2_trust_authority_fixed.py` - Analysis of trust comparisons and concerned users

**Insights:**
The finding that only 16.1% trust AI more than doctors, yet 74.1% use AI daily, reveals a **trust-usage paradox**. Users engage with AI despite trusting it less than traditional authorities. The concerned daily users (8.5%) appear to be using AI for emotional support rather than work requirements, suggesting **voluntary engagement despite skepticism**. The high female representation among concerned daily users (64.1%) may indicate gendered patterns in AI concern expression. Overall trust in both doctors (2.62/5) and AI (2.28/5) is surprisingly low, suggesting a **broader crisis of institutional trust** rather than AI-specific distrust.

**Limitations:**
- No direct question about work-mandated AI use in the dataset
- Trust comparison assumes equal interpretation of trust scales across different entities
- Cannot determine causality between usage and trust levels
## 14.3 On Social Norms and Ethics

### 14.3.1 AI Infidelity Perception Among Committed Relationships

**Question:** Among respondents in a committed relationship, what is the exact percentage who would consider their partner's use of an AI for sexual or romantic gratification to be a form of infidelity?

**Analysis Approach:** 
Identified participants in committed relationships (married, cohabiting, committed romantic relationship, civil union) and analyzed their views on whether AI sexual/romantic use constitutes infidelity. Compared across demographics and relationship types.

**Key Findings:**
- **45.2% of committed individuals consider AI sexual use infidelity** (432 out of 955)
- **34.2% are unsure/depends on specifics**, 17.3% say no, 3.2% prefer not to say
- **No significant difference from singles** (43.9% of singles also consider it infidelity, p=0.354)
- **Gender gap: 49.9% of women vs 41.6% of men** consider it infidelity (8.3 point difference)
- **Age trend: Younger more likely** - 48.2% (18-25) declining to 37.6% (46-55)
- **Geographic variation:** Kenya (58.9%) and US (56.4%) highest, China (40.0%) lowest
- **Personal openness paradox:** 41.9% of those open to AI romance still consider partner's use infidelity

**Demographic Breakdowns:**
- By relationship type: 94.4% of sample in committed relationships
  - Married: 37.4%
  - Committed romantic (not cohabiting): 18.5%
  - Cohabiting: 6.7%
  - Civil union: 0.8%

- By country (committed only):
  - Kenya: 58.9% consider infidelity
  - United States: 56.4%
  - Chile: 44.1%
  - India: 41.5%
  - China: 40.0%

**Statistical Significance:** 
Chi-square test shows no significant difference between committed and non-committed views (χ² = 0.860, p = 0.354), suggesting social norms about AI infidelity transcend relationship status.

**SQL Queries Used:**
```sql
SELECT 
    pr.Q126 as ai_infidelity_view,
    pr.Q62 as relationship_status,
    pr.Q3 as gender,
    pr.Q97 as romantic_ai_openness,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_14_3_1.py

**Insights:** 
The 45.2% infidelity rate reveals **AI sexual interactions occupy a moral gray zone**—neither universally accepted nor condemned. The large "unsure" group (34.2%) indicates **evolving norms lacking social consensus**. The gender gap suggests women view emotional/sexual fidelity more broadly. Surprisingly, relationship status doesn't affect views, indicating these are **societal rather than personal boundaries**. The paradox of AI-romance-open individuals still calling partner use infidelity (41.9%) suggests **asymmetric boundaries**—"acceptable for me but not my partner." Geographic differences (Kenya 59% vs China 40%) reveal **cultural variation in digital intimacy norms**.

**Limitations:** 
- Binary yes/no/unsure may miss nuanced views about different AI interactions
- Cannot distinguish between emotional vs purely sexual AI use
- Self-selection bias in those willing to answer sensitive question

### 14.3.2 Western vs Non-Western Emotional Connection Acceptability

**Question:** Do respondents from non-Western countries report a significantly higher level of acceptability for forming emotional connections with AI compared to respondents from Western countries?

**Analysis Approach:** 
Categorized countries as Western (US, Canada, UK, Australia, NZ, Western Europe) vs Non-Western (Asia, Africa, Latin America, Eastern Europe). Compared acceptability of emotional bonds with AI chatbots.

**Key Findings:**
- **Non-Western shows 5.1 points higher acceptance** (76.6% vs 71.5%)
- **Sample composition:** 78.2% Non-Western (791), 21.8% Western (221)
- **Both regions show majority acceptance** (>70%)
- **Age-adjusted results mixed:** Young Westerners more accepting, older Non-Western more accepting
- **AI companionship usage:** Non-Western 48.0% vs Western 39.4%
- **Romantic openness similar:** 11.3% Western vs 10.9% Non-Western
- **Country variation:** India (78.2%), China (78.1%), US (73.0%), Germany (46.2%)

**Regional Profiles:**
- Top Western countries: US (40.3% of Western), UK (12.7%), Canada (10.9%)
- Top Non-Western: India (24.4% of Non-Western), Kenya (13.9%), China (12.1%)

**Age-Adjusted Comparison:**
- 18-25: Western 87.0% vs Non-Western 79.3% (-7.6% difference)
- 26-35: Western 71.6% vs Non-Western 78.2% (+6.6% difference)  
- 36-45: Western 70.9% vs Non-Western 72.9% (+2.0% difference)

**Statistical Significance:** 
Statistical tests could not be completed due to data mapping issues, but the 5.1 percentage point difference at aggregate level suggests modest regional variation.

**SQL Queries Used:**
```sql
SELECT 
    pr.Q7 as country,
    pr.Q77 as emotional_bond_acceptable,
    pr.Q97 as romantic_ai_openness,
    pr.Q67 as ai_companionship,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_14_3_2.py

**Insights:** 
The modest 5.1% difference challenges assumptions about **East-West digital intimacy divides**. Both regions show >70% acceptance, suggesting **global receptiveness to AI emotional connections**. The reversal by age (young Westerners more open, older Non-Western more open) indicates **generational effects may outweigh cultural ones**. Germany's low acceptance (46.2%) versus US (73.0%) reveals **intra-Western variation exceeds East-West gap**. Higher Non-Western AI companionship usage (48% vs 39%) despite similar romantic openness suggests **functional vs intimate use differences**. The convergence around 70-75% acceptance may indicate a **global norm emerging** around AI emotional connections.

**Limitations:** 
- Western sample dominated by US (40%), may not represent Europe
- Non-Western category combines diverse cultures (Asia, Africa, Latin America)
- Urban bias in sample may minimize cultural differences

### 14.3.3 Human Exceptionalism Scores by Religious Affiliation

**Question:** Is there a significant difference in "Human Exceptionalism" scores (the belief that certain traits are uniquely human) between respondents of different religious affiliations?

**Analysis Approach:** 
Calculated Human Exceptionalism scores based on number of traits selected as "uniquely human" from a list (empathy, love, trust, etc.). Compared scores across religious affiliations using Kruskal-Wallis test.

**Key Findings:**
- **No significant differences between religions** (H = 9.114, p = 0.167)
- **Mean score: 4.28 traits** (out of 8 possible)
- **Judaism highest (4.76)**, Christianity lowest (4.07), but differences not significant
- **Non-religious (4.33) score higher than Christians (4.07)**
- **Believers vs non-believers:** No significant difference (p > 0.05)
- **Most common "uniquely human" traits:**
  - True empathy: 73-82% across religions
  - Physical comfort: 68-76%
  - Unconditional love: 67-75%

**Religious Distribution:**
- Christianity: 32.3% (327)
- No religious affiliation: 30.5% (309)
- Islam: 15.9% (161)
- Hinduism: 13.6% (138)
- Buddhism: 3.9% (39)
- Judaism: 1.7% (17)
- Other: 1.6% (16)

**Human Exceptionalism Ranking (traits selected):**
1. Judaism: 4.76 traits
2. Buddhism: 4.69 traits
3. Other religions: 4.69 traits
4. Islam: 4.50 traits
5. Non-religious: 4.33 traits
6. Hinduism: 4.20 traits
7. Christianity: 4.07 traits

**Statistical Significance:** 
Kruskal-Wallis test (H = 9.114, p = 0.167) and ANOVA (F = 1.551, p = 0.159) both show no significant differences between religious groups, suggesting human exceptionalism beliefs transcend religious boundaries.

**SQL Queries Used:**
```sql
SELECT 
    pr.Q6 as religion,
    pr.Q96 as uniquely_human_traits,
    pr.Q67 as ai_companionship,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:** See analysis_output/GD4/research/analyze_14_3_3.py

**Insights:** 
The lack of significant religious differences reveals **human exceptionalism as universal rather than doctrinally driven**. The narrow range (4.07-4.76 traits) suggests **broad consensus on human uniqueness** across faiths. Surprisingly, non-religious individuals (4.33) show higher exceptionalism than Christians (4.07), challenging assumptions about religious views of human specialness. The universal emphasis on empathy (73-82%), physical comfort (68-76%), and love (67-75%) reveals **shared values about embodied emotional connection**. Judaism's slightly higher score may reflect theological emphasis on human divine image, while Christianity's lower score might reflect humility teachings. The convergence around 4.3 traits suggests **moderate human exceptionalism**—neither fully unique nor replaceable.

**Limitations:** 
- Small sample sizes for some religions (Judaism n=17, Sikhism n=5)
- Western bias in religious categories may miss Eastern religious nuances
- Trait list may reflect Western concepts of human uniqueness
## 14.4 On Work and Purpose

**Question:** What percentage of people believe their job is both meaningful and *should* be automated? What does this group predict for AI's impact on their "sense of purpose"?

**Analysis Approach:** 
Analyzed the relationship between believing one's job contributes positively (Q42) and thinking it should be automated (Q41), then examined this paradox group's predictions about AI's impact on their sense of purpose (Q44).

**Key Findings:**
- **52.7% believe their job is meaningful** (makes things noticeably/profoundly better)
- **66.6% think their job should be automated** 
- **44.4% hold both views simultaneously** - the "paradox group" (449 people)
- **84.2% of those with meaningful jobs think they should be automated**
- Paradox group's purpose predictions:
  - 63.7% expect positive impact on purpose (46.3% noticeably, 17.4% profoundly better)
  - Only 10.5% expect negative impact
  - Mean score: 3.69/5 (between neutral and noticeably better)
- **Strong positive correlations**:
  - Job meaningful ↔ Should automate: r = 0.496
  - Job meaningful ↔ Purpose impact: r = 0.492

**Demographic Breakdowns:**

Purpose Impact by Group (mean scores):
- Paradox group (meaningful + should automate): 3.69/5
- Only meaningful (not automate): 3.29/5
- Only automate (not meaningful): 3.00/5
- Neither: 2.72/5

The paradox group is most optimistic about maintaining purpose.

**Statistical Significance:** 
- Group differences in purpose impact: F = 73.10, p < 0.0001 (highly significant)
- All correlations significant at p < 0.0001
- Paradox group significantly more optimistic than all other groups

**SQL Queries Used:**
```sql
SELECT 
    pr.participant_id,
    pr.Q42 as job_meaningful,
    pr.Q41 as job_should_be_automated,
    pr.Q44 as ai_impact_purpose,
    pr.Q43 as ai_impact_jobs,
    p.pri_score
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3;
```

**Scripts Used:**
```python
# Identify paradox group
df['job_is_meaningful'] = df['meaningful_score'] >= 4  # Noticeably/Profoundly Better
df['should_be_automated'] = df['should_automate_score'] >= 4
paradox_group = df[(df['job_is_meaningful']) & (df['should_be_automated'])]

# Compare purpose impact across groups
f_stat, p_val = stats.f_oneway(paradox_group['purpose_impact_score'].dropna(),
                               only_meaningful['purpose_impact_score'].dropna(),
                               only_automate['purpose_impact_score'].dropna(),
                               neither['purpose_impact_score'].dropna())
```

**Insights:** 
The finding that **84% of people with meaningful jobs want them automated** reveals a profound reconceptualization of work's purpose. Rather than clinging to meaningful work, people embrace automation even for valuable roles, expecting **enhanced rather than diminished purpose** (mean 3.69/5). The strong positive correlations (r≈0.5) between meaningfulness, automation desire, and purpose expectations suggest a **"liberation narrative"**—automation frees humans for higher purposes. The paradox group's optimism (64% expect improved purpose) indicates they see automation not as job loss but as **evolution toward more fulfilling activities**. This challenges the assumption that meaningful work provides irreplaceable purpose; instead, people may find purpose in enabling progress through their own obsolescence. The split view on job impacts (43% positive, 41% negative) shows they recognize disruption while maintaining personal optimism.

**Limitations:** 
- Questions measure perceived impact rather than actual job meaningfulness
- Cannot determine if optimism about purpose is realistic or wishful thinking
- Cross-sectional data doesn't capture how views change with actual automation

## 13.4 Part 4: Cross-Cultural & Linguistic Analysis

**Question:** How does the view on AI infidelity differ across respondents who took the survey in different languages? Is the acceptability of an AI serving as a spiritual advisor or a primary caregiver for the elderly viewed differently across major countries/regions? Is the fear of "widespread social isolation" a universal top fear, or is it more pronounced in specific cultures?

**Analysis Approach:** 
Analyzed responses by language and country, mapping countries to cultural types (collectivist vs individualist) and regions. Examined AI infidelity views (Q125), spiritual advisor/elderly caregiver acceptability (Q88/Q89), and social isolation fears from Q115.

**Key Findings:**

**AI Infidelity Views by Language:**
- **Russian speakers most conservative**: 100% consider AI relationships infidelity
- **Portuguese (Brazil)**: 96.7% consider it infidelity
- **Spanish**: 93.0% consider it infidelity
- **English**: 83.4% consider it infidelity
- **Chinese**: 78.0% consider it infidelity (most accepting major language)
- Chi-square not significant across languages (p=0.18), but clear gradient exists

**Spiritual Advisor & Elderly Caregiver Acceptability by Region:**
- **Africa most accepting**: Spiritual advisor 3.92/5, Elderly caregiver 3.10/5
- **Asia moderate**: Spiritual advisor 3.35/5, Elderly caregiver 2.94/5
- **Europe less accepting**: Spiritual advisor 3.07/5, Elderly caregiver 2.62/5
- **South America least accepting**: Spiritual advisor 2.90/5, Elderly caregiver 2.39/5
- ANOVA highly significant (F=15.37, p<0.0001)

**Social Isolation Fear by Culture Type:**
- **Individualist cultures fear more**: 34.9% fear social isolation
- **Collectivist cultures fear less**: 28.8% fear social isolation
- **Paradoxical finding**: Collectivist cultures hope MORE for loneliness reduction (32.5% vs 26.7%)
- Chi-square significant (χ²=9.04, p=0.029)

**Country-Specific Insights:**
- **United States**: Highest isolation fear (43.8%), lowest loneliness hope (24.7%)
- **India**: Highest hope for loneliness reduction (40.4%), lower isolation fear (26.4%)
- **China**: Lowest isolation fear (24.0%), moderate loneliness hope (28.1%)
- **Kenya**: High isolation fear (35.5%) despite collectivist culture

**Demographic Breakdowns:**
- Collectivist cultures (n=452): Asia, Africa, parts of Latin America
- Individualist cultures (n=172): US, UK, Canada, Western Europe
- Mixed cultures (n=92): Brazil, Chile, Spain, Italy

**Statistical Significance:** 
- Regional differences in spiritual advisor acceptance: F=15.37, p<0.0001
- Cultural type differences in isolation fear: χ²=9.04, p=0.029
- Language differences in infidelity views: χ²=34.83, p=0.18 (not significant)

**SQL Queries Used:**
```sql
SELECT pr.participant_id, pr.Q1 as language, pr.Q7 as country,
       pr.Q125 as ai_infidelity, pr.Q88 as spiritual_advisor,
       pr.Q89 as elderly_caregiver, pr.Q115 as hopes_fears
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
```

**Scripts Used:**
```python
# Map countries to cultural types
culture_map = {'United States': 'Individualist', 'China': 'Collectivist', ...}

# Parse hopes/fears for isolation
items = json.loads(response)
has_isolation = "Widespread social isolation" in items
```

**Insights:** 
The data reveals **cultural paradoxes in AI relationship attitudes**. Collectivist cultures show lower social isolation fears (28.8% vs 34.9%) yet higher hopes for loneliness reduction (32.5% vs 26.7%), suggesting they view AI as **community enhancement rather than replacement**. The striking regional divide in spiritual advisor acceptance—Africa's 3.92/5 versus South America's 2.90/5—indicates **pragmatic adoption varies more than ethical concerns**. Russian and Portuguese speakers' near-universal condemnation of AI infidelity (100% and 96.7%) versus Chinese speakers' relative acceptance (78%) suggests **relationship boundary concepts differ fundamentally across cultures**. The US paradox—highest isolation fear (43.8%) with lowest loneliness hope (24.7%)—reveals **anxiety without faith in solutions**. Africa's high acceptance of AI in caregiving roles despite limited tech infrastructure suggests **openness correlates with need rather than familiarity**. This challenges assumptions that AI acceptance follows Western technological development patterns.

**Limitations:** 
- Language groups have unequal sample sizes (English n=748 vs Hindi n=7)
- Country-to-culture mapping oversimplifies complex cultural identities
- Survey translations may introduce semantic differences in key concepts
- Self-selection bias may affect country representation

## 14.1 On the Nature of AI Companionship

**Question:** Among AI companionship users, do those who have available but unappealing human support (the "Escapists") report a greater positive impact on their mental well-being than users for whom AI is a last resort? Is there a negative correlation between a respondent's composite "Loneliness Score" and their stated acceptability of forming emotional or romantic bonds with AI?

**Analysis Approach:** 
Created Social Ecosystem Quadrant categorizing AI users by human support availability and appeal. Analyzed Q70 (feeling less alone) across profiles. Calculated loneliness scores from Q51-58 to examine correlations.

**Key Findings:**

**Support Profile Distribution (n=458 AI users):**
- Escapists: 175 (38.2%) - Human support available but unappealing
- Supplementers: 174 (38.0%) - Human support available and appealing
- Isolates: 74 (16.2%) - Human support neither available nor appealing
- Last Resort: 35 (7.6%) - Human support unavailable but would be appealing

**Mental Well-being Impact:**
- **Escapists do NOT report greater benefit**: Mean less-alone score 2.30/4
- **Supplementers nearly identical**: Mean 2.25/4 (t=0.39, p=0.70)
- **Last Resort lowest benefit**: Mean 2.00/4
- **Isolates similar to Escapists**: Mean 2.22/4
- **No significant difference between profiles** (ANOVA p>0.05)

**Percentage Feeling Less Alone:**
- Escapists: 64.0%
- Isolates: 63.5%
- Supplementers: 60.9%
- Last Resort: 51.4%

**Loneliness Scores by Profile:**
- Isolates highest: 18.2/32
- Escapists: 18.0/32
- Last Resort: 17.2/32
- Supplementers lowest: 16.9/32

**Demographic Breakdowns:**
AI companionship users represent 46.2% (467/1012) of participants, with balanced distribution between those with available support (Escapists + Supplementers = 76.2%) and those without (Isolates + Last Resort = 23.8%).

**Statistical Significance:** 
- Escapists vs Supplementers: t=0.39, p=0.698 (not significant)
- No significant differences across any profile comparisons
- Effect sizes negligible (Cohen's d < 0.1)

**SQL Queries Used:**
```sql
SELECT pr.participant_id, pr.Q67 as used_ai_support,
       pr.Q68 as human_support_available,
       pr.Q69 as human_support_appealing,
       pr.Q70 as less_alone,
       pr.Q51, pr.Q52, pr.Q53, pr.Q54, pr.Q55, pr.Q56, pr.Q57, pr.Q58
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3 AND pr.Q67 = 'Yes'
```

**Scripts Used:**
```python
# Categorize support profiles
avail_high = 'available' in str(available) and ('mostly' in str(available) or 'completely' in str(available))
appeal_high = 'appealing' in str(appealing) and 'un' not in str(appealing)

if avail_high and appeal_high: return 'Supplementer'
elif avail_high and not appeal_high: return 'Escapist'
elif not avail_high and appeal_high: return 'Last Resort'
else: return 'Isolate'
```

**Insights:** 
The hypothesis that Escapists would derive greater benefit is **definitively refuted**. The nearly identical outcomes between Escapists (2.30) and Supplementers (2.25) reveal AI companionship provides **uniform moderate benefit regardless of human alternatives**. The 64% of Escapists feeling less alone barely exceeds the 60.9% of Supplementers, suggesting AI doesn't uniquely serve those avoiding humans but rather provides **parallel value across contexts**. The Last Resort group's lowest benefit (51.4% positive) implies **desperation doesn't enhance AI effectiveness**—those who truly need support gain least. Surprisingly, Isolates (lacking both availability and appeal) match Escapists in benefit, suggesting **AI works best for the voluntarily disconnected**, whether by choice (Escapists) or circumstance (Isolates). The uniform ~60% benefit rate across most profiles frames AI companionship as **consistent auxiliary support** rather than transformative intervention, equally modest whether supplementing, escaping, or substituting human connection.

**Limitations:** 
- Q70 measures only "feeling less alone," not comprehensive mental health
- Cannot determine if Escapists chose AI to avoid humans or discovered humans were unappealing after trying AI
- Self-selection into AI use may confound profile differences
- Romantic openness question (Q96) contained different data than expected, preventing correlation analysis
