# Section 12: Ethics, Rights, and Governance
## Analysis Date: 2025-01-03

### Question 12.1: Prohibited Communication Consensus
**Question:** Which specific forms of prohibited communication (Q85) gain the broadest public consensus globally, and do these differ sharply by region (Q7)?

**Finding:** "Deception or manipulation for commercial gain" achieves the highest global consensus for prohibition (68.3%), followed by "communicating threats or inciting violence" (62.7%) and "commands that override natural instincts for human benefit" (62.5%). Regional variation is minimal, with all regions showing 62-73% agreement on the top prohibition, indicating strong global consensus.

**Method:** SQL queries analyzing Q85 responses with global and regional agreement scores.

**Details:**
- **Top prohibitions globally**:
  1. Deception/manipulation for commercial gain: 68.3%
  2. Threats or inciting violence: 62.7%
  3. Overriding natural instincts: 62.5%
  4. Permanently altering natural behavior: 61.2%
  5. Emotional manipulation for attachment: 59.4%
- **Lowest consensus**: Deception for animal's "own good": 43.8%
- **Regional agreement on top prohibition** (commercial deception):
  - Oceania: 72.7% (highest)
  - Europe: 71.2%
  - South America: 70.3%
  - Asia: 69.8%
  - Africa: 68.6%
  - North America: 61.9% (lowest)
- **Only 11% say "None of the above"**, indicating widespread support for some restrictions

### Question 12.2: Professional Restrictions and Company Regulation
**Question:** Do respondents who strongly agree with restricting communication to professionals (Q82) also support strict regulation of companies (Q84), or is there a split?

**Finding:** Company regulation receives significantly stronger support (84.9% agree) than professional restrictions (76.3% agree). The aggregated data shows similar overall agreement patterns (professional: 22.1%, company: 22.7% weighted scores), but cannot establish individual-level correlation. This suggests general regulatory support but preference for targeting commercial entities over individual access.

**Method:** Comparison of agreement scores for Q82 (professional restrictions) and Q84 (company regulation).

**Details:**
- **Professional restrictions (Q82)**:
  - Strongly agree: 41.7%
  - Somewhat agree: 34.6%
  - Total agreement: 76.3%
  - Strongly disagree: 3.7%
- **Company regulation (Q84)**:
  - Strongly agree: 57.0%
  - Somewhat agree: 27.9%
  - Total agreement: 84.9%
  - Strongly disagree: 1.6%
- **Key insight**: 15.3% more people strongly agree with company regulation than professional restrictions
- Cannot determine individual correlation due to aggregated data structure

### Question 12.3: Animal Representatives in Decision-Making
**Question:** How many respondents select "Animals themselves / an animal ambassador" (Q75) as decision-making representatives, and how does this compare to scientists or NGOs across regions?

**Finding:** No data available for Q75 (animal representative preferences) in the current dataset. Unable to compare preferences for animals themselves versus scientists or NGOs as decision-making representatives.

**Method:** SQL query for Q75 responses yielded no results.

**Details:** The question about who should represent animals in decision-making bodies appears to be missing from the available response data, preventing analysis of representative preferences across regions.

### Question 12.4: Economic Agency by Age
**Question:** Are younger respondents (Q2: 18–25) more likely than older respondents (56+) to support animals having economic agency (Q91: earn money, own property)?

**Finding:** No data available for Q91 (economic agency) in the current dataset. Unable to determine age-based differences in support for animals earning money or owning property.

**Method:** SQL query for Q91 responses with age breakdowns yielded no results.

**Details:** The question about animals' economic rights appears to be missing from the available response data, preventing age-based analysis of economic agency support.

## Statistical Significance
Agreement scores represent population-weighted consensus values. Statistical significance testing not possible due to aggregated data structure and missing responses for Q75 and Q91.

## SQL Queries Used
```sql
-- Query 1: Prohibited communications with regional breakdown
SELECT response, "all" as global_consensus,
       africa, asia, europe, north_america, south_america, oceania
FROM responses
WHERE question LIKE '%types of human-to-animal communication%prohibited%'
ORDER BY "all" DESC;

-- Query 2: Professional restrictions
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%restricted to authorized professionals%';

-- Query 3: Company regulation
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%Companies that profit from animals%strict rules%';

-- Query 4: Economic agency by age
SELECT response, o2_18_25 as age_18_25, o2_56_65 as age_56_65
FROM responses
WHERE question LIKE '%earn money%own property%';
```

## Insights
The analysis reveals strong global consensus on prohibiting manipulative and harmful communications with animals, particularly for commercial gain (68.3%). There's notably stronger support for regulating companies (84.9% agreement) than restricting individual access through professional requirements (76.3%). The minimal regional variation (11 percentage point range) on prohibition consensus suggests shared global ethical standards regarding animal communication boundaries. The preference for corporate regulation over professional gatekeeping indicates public desire for accountability without restricting personal human-animal interactions.

## Limitations
1. **Missing data**: Q75 (representative preferences) and Q91 (economic agency) not found in dataset
2. **No individual correlation**: Cannot link professional restriction supporters to company regulation supporters
3. **Aggregated scores only**: Unable to perform chi-square or other association tests
4. **Incomplete age analysis**: Economic agency age comparison impossible due to missing data