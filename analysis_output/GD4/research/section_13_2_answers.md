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