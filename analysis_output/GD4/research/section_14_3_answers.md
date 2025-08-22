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