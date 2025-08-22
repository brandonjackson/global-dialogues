# Q14.2 On Trust and Authority - Standalone Analysis

## Question 1: Trust in AI vs Family Doctor

**Question:** What percentage of respondents report a higher trust score for their AI chatbot than for their family doctor? What is the demographic profile of this group?

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

## Question 2: Concerned Daily Users

**Question:** What percentage of daily AI users also state they are "more concerned than excited" about AI's impact? Of this "Concerned User" group, how many are required to use AI for their job?

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