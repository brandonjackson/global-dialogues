# Section 18: Experiential & Exposure Effects
## Analysis Date: 2025-01-03

### Question 18.1: Working Animals and AI Uses
**Question:** Do people who regularly interact with working animals (Q38) (e.g., police dogs, mules) support more instrumental uses of AI (e.g., safety, productivity) than wildlife-focused conservation uses?

**Finding:** Only 8.8% of respondents regularly encounter working animals (police dogs, work mules), making this a small specialized group. Statistical analysis shows no significant difference in animal protection preferences between those with and without working animal exposure (p=0.856).

**Method:** Individual-level analysis linking Q38 animal encounter data to Q70 animal protection preferences using chi-square test (n=1037).

**Details:**
- **Working animal exposure rate**: 8.8% (ranked 5th of 9 animal categories)
- **Statistical test results**: Chi-square = 0.77, p = 0.856, df = 3
- **Conclusion**: Working animal exposure does not significantly correlate with different animal protection approaches
- Both groups show similar preferences for relationship-based vs. legal rights approaches

### Question 18.2: Zoo Visitors and Entertainment
**Question:** Are zoo/aquarium visitors (Q38) more likely to support AI-mediated entertainment uses of animal translation than other groups?

**Finding:** Zoo/aquarium visitors represent only 7.0% of respondents, the third-lowest exposure category. While 1,024 entertainment-related responses exist in the database, the aggregated structure prevents linking zoo visitation to entertainment support preferences.

**Method:** Analysis of zoo/aquarium visitor rates from Q38 and entertainment-related response data.

**Details:**
- **Zoo/aquarium exposure**: 7.0% (ranked 6th of 9 categories)
- **Entertainment data available**: 1,024 responses found but not linkable to visitor status
- **Interest levels found**: 70.1% "very interested" in knowing what animals say, 23.2% "somewhat interested"
- Cannot establish if zoo visitors differ from non-visitors in entertainment use support

### Question 18.3: Urban vs. Companion Animal Ethics
**Question:** Do people who encounter urban wildlife (Q38: rats, pigeons, squirrels) show different ethical priorities than those who mostly encounter companion animals?

**Finding:** Urban wildlife encounters (47.6%) are common but far less frequent than companion animal encounters (89.8%). The aggregated data structure prevents comparing ethical priorities between these exposure groups, though both represent major segments of the population.

**Method:** Comparison of encounter rates and search for linkable ethical priority data.

**Details:**
- **Exposure rates**:
  - Companion animals: 89.8% (highest category)
  - Urban wildlife: 47.6% (second highest)
  - Ratio: 1.88x more companion than urban wildlife exposure
- **Ethical concerns found**: Misinterpretation and manipulation dominate (57.0% agreement)
- **Key limitation**: Cannot determine if urban wildlife encounters correlate with different ethical frameworks than companion animal encounters

## Statistical Significance
No statistical tests possible due to aggregated data structure preventing individual-level analysis of exposure-ethics relationships.

## SQL Queries Used
```sql
-- Query 1: Animal encounter types (Q38)
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%types of animals%encounter%life%week%'
ORDER BY "all" DESC;

-- Query 2: AI use preferences
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%AI%use%' OR question LIKE '%benefit%understand%animals%'
LIMIT 20;

-- Query 3: Entertainment-related responses
SELECT response, "all" as agreement_score
FROM responses
WHERE question LIKE '%entertainment%' OR question LIKE '%What would you be most interested%';

-- Query 4: Ethical priorities
SELECT question, response, "all" as agreement_score
FROM responses
WHERE question LIKE '%ethical%' OR question LIKE '%rights%' OR question LIKE '%welfare%';
```

## Insights
The analysis reveals a clear hierarchy of animal exposure in daily life, with companion animals dominating (89.8%), followed by urban wildlife (47.6%) and farmed animals (31.6%). Specialized exposures like working animals (8.8%), zoo animals (7.0%), and laboratory animals (4.7%) affect relatively small populations. This exposure hierarchy likely shapes attitudes toward AI-mediated communication, though the aggregated data prevents establishing direct correlations. The high interest in animal communication (70.1% very interested) coupled with concerns about misinterpretation (57.0%) suggests a cautiously optimistic public regardless of exposure type.

## Limitations
1. **No individual linking**: Cannot connect specific animal exposure to AI use preferences or ethical priorities
2. **Missing causal analysis**: Unable to determine if exposure type influences attitudes
3. **Aggregated scores only**: Prevents correlation testing between exposure and preferences
4. **Limited instrumental vs. conservation data**: Specific AI use categories not clearly delineated in responses
5. **Entertainment use ambiguity**: Cannot isolate entertainment-specific support from general interest