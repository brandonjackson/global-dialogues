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

**Finding:** Zoo/aquarium visitors represent only 7.0% of respondents, the third-lowest exposure category. Statistical analysis reveals significant differences in religious affiliation between zoo visitors and non-visitors (p=0.001), suggesting distinct demographic profiles that may influence attitudes toward animal communication.

**Method:** Individual-level analysis linking Q38 zoo/aquarium exposure to Q6 religious affiliation using chi-square test (n=1037).

**Details:**
- **Zoo/aquarium exposure**: 7.0% (ranked 6th of 9 categories)
- **Statistical test results**: Chi-square = 24.91, p = 0.001, df = 7
- **Interest levels found**: 70.1% "very interested" in knowing what animals say, 23.2% "somewhat interested"
- Zoo visitors show significantly different religious demographic patterns than non-visitors

### Question 18.3: Urban vs. Companion Animal Ethics
**Question:** Do people who encounter urban wildlife (Q38: rats, pigeons, squirrels) show different ethical priorities than those who mostly encounter companion animals?

**Finding:** Urban wildlife encounters (47.6%) are common but far less frequent than companion animal encounters (89.8%). Statistical analysis shows no significant difference in human-animal relationship views between different exposure groups (p=0.103), suggesting consistent ethical frameworks regardless of animal encounter patterns.

**Method:** Individual-level analysis comparing exposure types (companion-only, urban-only, both, other) against Q94 human-animal relationship views using chi-square test (n=1037).

**Details:**
- **Exposure rates**:
  - Companion animals: 89.8% (highest category)  
  - Urban wildlife: 47.6% (second highest)
  - Both types: 44.5% of participants
- **Statistical test results**: Chi-square = 14.57, p = 0.103, df = 9
- **Conclusion**: Animal exposure type does not significantly predict views on human-animal equality/superiority

## Statistical Significance
Multiple chi-square tests performed on individual-level data (n=1037):
- Q18.1: Working animals × Animal protection (χ²=0.77, p=0.856, df=3) - Not significant
- Q18.2: Zoo visitors × Religious affiliation (χ²=24.91, p=0.001, df=7) - Significant  
- Q18.3: Exposure types × Human-animal views (χ²=14.57, p=0.103, df=9) - Not significant

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
The analysis reveals a clear hierarchy of animal exposure in daily life, with companion animals dominating (89.8%), followed by urban wildlife (47.6%) and farmed animals (31.6%). Specialized exposures like working animals (8.8%), zoo animals (7.0%), and laboratory animals (4.7%) affect relatively small populations. Statistical analysis shows that animal exposure type generally does not predict ethical attitudes toward animals, suggesting consistent underlying values across exposure groups. However, zoo visitors show distinct demographic patterns (religious affiliation differences) that may influence their perspectives on animal communication technology.

## Limitations
1. **Limited AI use preference data**: Specific instrumental vs. conservation AI use categories not clearly captured in available questions
2. **Entertainment question gaps**: Direct entertainment use preferences not measured in available data
3. **Small specialized groups**: Working animal (8.8%) and zoo visitor (7.0%) groups may lack statistical power for some analyses
4. **JSON parsing complexity**: Q38 data requires careful parsing of multi-selection responses
5. **Proxy measures**: Had to use related questions (animal protection, human-animal relations) as proxies for some research interests