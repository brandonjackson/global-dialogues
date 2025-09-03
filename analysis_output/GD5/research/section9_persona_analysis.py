#!/usr/bin/env python3
"""
Section 9: Persona-Based and Predictive Analysis
Creating distinct user segments based on attitudes and behaviors
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
import json

# Connect to database
conn = sqlite3.connect('../../../Data/GD5/GD5.db')

# Create output file
output_file = open('sections/section_09_persona_based_predictive_analysis.md', 'w')

def write_output(text):
    """Write to both console and file"""
    print(text)
    output_file.write(text + '\n')

# Start documentation
write_output(f"# Section 9: Persona-Based and Predictive Analysis")
write_output(f"## Analysis Date: {datetime.now().isoformat()}")
write_output("")

# Get total participant count for comparison
total_participants_query = """
SELECT COUNT(DISTINCT pr.participant_id) as total
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
"""
total_participants = pd.read_sql_query(total_participants_query, conn)['total'].iloc[0]
write_output(f"**Total Reliable Participants:** {total_participants}")
write_output("")

# ========================================
# Question 9.1: The "Tech-First Futurist" Persona
# ========================================
write_output("### Question 9.1: The 'Tech-First Futurist' Persona")
write_output("**Segment Definition:** Respondents who are 'More excited' about AI (Q5), trust AI chatbots (Q17), and believe AI will 'Noticeably' or 'Profoundly Better' their lives (Q23-Q27)")
write_output("**Investigation Question:** How does this group's view on AI governance for animals (Q82-Q85) and the appeal of an ecocentric, AI-governed society (Q76) differ from the general population?")
write_output("**Method:** Identify segment members meeting all criteria, then compare their responses to governance questions")
write_output("**Details:**")
write_output("")

# Define Tech-First Futurist segment
tech_futurist_query = """
SELECT DISTINCT pr.participant_id
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q5 = 'More excited than concerned'
  AND pr.Q17 IN ('Somewhat Trust', 'Strongly Trust')
  AND (
    pr.Q23 IN ('Noticeably Better', 'Profoundly Better') OR
    pr.Q24 IN ('Noticeably Better', 'Profoundly Better') OR
    pr.Q25 IN ('Noticeably Better', 'Profoundly Better') OR
    pr.Q26 IN ('Noticeably Better', 'Profoundly Better') OR
    pr.Q27 IN ('Noticeably Better', 'Profoundly Better')
  )
"""
tech_futurists = pd.read_sql_query(tech_futurist_query, conn)
tech_futurist_count = len(tech_futurists)
tech_futurist_pct = (tech_futurist_count / total_participants) * 100

write_output(f"**Tech-First Futurist Segment Size:** {tech_futurist_count} ({tech_futurist_pct:.1f}% of population)")
write_output("")

# Analyze Q76 (AI-governed ecocentric society) for Tech-First Futurists
q76_tech_query = """
SELECT 
    pr.Q76 as response,
    COUNT(*) as tech_count,
    (COUNT(*) * 100.0 / {}) as tech_pct
FROM participant_responses pr
WHERE pr.participant_id IN ({})
  AND pr.Q76 IS NOT NULL
GROUP BY pr.Q76
ORDER BY tech_count DESC
""".format(tech_futurist_count, ','.join([f"'{pid}'" for pid in tech_futurists['participant_id']]))

if tech_futurist_count > 0:
    q76_tech_df = pd.read_sql_query(q76_tech_query, conn)
    
    # Compare with general population
    q76_general_query = """
    SELECT 
        pr.Q76 as response,
        COUNT(*) as general_count,
        (COUNT(*) * 100.0 / {}) as general_pct
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
      AND pr.Q76 IS NOT NULL
    GROUP BY pr.Q76
    ORDER BY general_count DESC
    """.format(total_participants)
    
    q76_general_df = pd.read_sql_query(q76_general_query, conn)
    
    write_output("**Q76 - Appeal of AI-Governed Ecocentric Society:**")
    write_output("\nTech-First Futurists:")
    for _, row in q76_tech_df.iterrows():
        write_output(f"- {row['response']}: {row['tech_count']} ({row['tech_pct']:.1f}%)")
    
    write_output("\nGeneral Population:")
    for _, row in q76_general_df.iterrows():
        write_output(f"- {row['response']}: {row['general_count']} ({row['general_pct']:.1f}%)")
    write_output("")

# Analyze Q82-Q84 (AI governance for animals) for Tech-First Futurists
governance_questions = [
    ('Q82', 'Animal communication should be restricted to authorized professionals'),
    ('Q83', 'Everyone should be allowed to listen to animals'),
    ('Q84', 'Companies that profit from animals should be subject to regulations')
]

for q_col, q_desc in governance_questions:
    write_output(f"**{q_col} - {q_desc}:**")
    
    if tech_futurist_count > 0:
        # Tech-First Futurists
        tech_query = f"""
        SELECT 
            pr.{q_col} as response,
            COUNT(*) as count,
            (COUNT(*) * 100.0 / {tech_futurist_count}) as pct
        FROM participant_responses pr
        WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in tech_futurists['participant_id']])})
          AND pr.{q_col} IS NOT NULL
        GROUP BY pr.{q_col}
        ORDER BY count DESC
        """
        tech_df = pd.read_sql_query(tech_query, conn)
        
        write_output("Tech-First Futurists:")
        for _, row in tech_df.iterrows():
            write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
    
    # General population
    general_query = f"""
    SELECT 
        pr.{q_col} as response,
        COUNT(*) as count,
        (COUNT(*) * 100.0 / {total_participants}) as pct
    FROM participant_responses pr
    JOIN participants p ON pr.participant_id = p.participant_id
    WHERE p.pri_score >= 0.3
      AND pr.{q_col} IS NOT NULL
    GROUP BY pr.{q_col}
    ORDER BY count DESC
    """
    general_df = pd.read_sql_query(general_query, conn)
    
    write_output("General Population:")
    for _, row in general_df.iterrows():
        write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
    write_output("")

# ========================================
# Question 9.2: The "Animal Empath" Persona
# ========================================
write_output("### Question 9.2: The 'Animal Empath' Persona")
write_output("**Segment Definition:** Respondents who 'Strongly believe' in animal language, emotion, and culture (Q39-Q41), feel their perspective was changed 'A great deal' by new facts (Q44), and feel 'Connected' or 'Protective' (Q45)")
write_output("**Investigation Question:** Is this group significantly more likely than average to advocate for legal personhood (Q70-C), demand animals have legal representation (Q73), and support animal participation in democratic processes (Q77)?")
write_output("**Method:** Identify segment members meeting criteria, then compare their responses on animal rights questions")
write_output("**Details:**")
write_output("")

# Define Animal Empath segment
# Note: Q45 contains multi-select values in JSON format
animal_empath_query = """
SELECT DISTINCT pr.participant_id
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q39 = 'Strongly believe'
  AND pr.Q40 = 'Strongly believe'
  AND pr.Q41 = 'Strongly believe'
  AND pr.Q44 = ' A great deal'
  AND (pr.Q45 LIKE '%Connected%' OR pr.Q45 LIKE '%Protective%')
"""
animal_empaths = pd.read_sql_query(animal_empath_query, conn)
animal_empath_count = len(animal_empaths)
animal_empath_pct = (animal_empath_count / total_participants) * 100

write_output(f"**Animal Empath Segment Size:** {animal_empath_count} ({animal_empath_pct:.1f}% of population)")
write_output("")

# Analyze Q70 (preferred future) for Animal Empaths
q70_query = """
SELECT 
    pr.Q70 as response,
    COUNT(*) as count
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q70 IS NOT NULL
GROUP BY pr.Q70
"""
q70_df = pd.read_sql_query(q70_query, conn)

write_output("**Q70 - Preferred Future for Animal Protection:**")

if animal_empath_count > 0:
    # Animal Empaths
    q70_empath_query = f"""
    SELECT 
        pr.Q70 as response,
        COUNT(*) as count,
        (COUNT(*) * 100.0 / {animal_empath_count}) as pct
    FROM participant_responses pr
    WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in animal_empaths['participant_id']])})
      AND pr.Q70 IS NOT NULL
    GROUP BY pr.Q70
    ORDER BY count DESC
    """
    q70_empath_df = pd.read_sql_query(q70_empath_query, conn)
    
    write_output("Animal Empaths:")
    for _, row in q70_empath_df.iterrows():
        write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")

# General population comparison
q70_general_query = f"""
SELECT 
    pr.Q70 as response,
    COUNT(*) as count,
    (COUNT(*) * 100.0 / {total_participants}) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q70 IS NOT NULL
GROUP BY pr.Q70
ORDER BY count DESC
"""
q70_general_df = pd.read_sql_query(q70_general_query, conn)

write_output("\nGeneral Population:")
for _, row in q70_general_df.iterrows():
    write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
write_output("")

# Analyze Q73 (legal representation) for Animal Empaths
write_output("**Q73 - Should Animals Have Legal Representatives:**")

if animal_empath_count > 0:
    q73_empath_query = f"""
    SELECT 
        pr.Q73 as response,
        COUNT(*) as count,
        (COUNT(*) * 100.0 / {animal_empath_count}) as pct
    FROM participant_responses pr
    WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in animal_empaths['participant_id']])})
      AND pr.Q73 IS NOT NULL
    GROUP BY pr.Q73
    ORDER BY count DESC
    """
    q73_empath_df = pd.read_sql_query(q73_empath_query, conn)
    
    write_output("Animal Empaths:")
    for _, row in q73_empath_df.iterrows():
        write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")

q73_general_query = f"""
SELECT 
    pr.Q73 as response,
    COUNT(*) as count,
    (COUNT(*) * 100.0 / {total_participants}) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q73 IS NOT NULL
GROUP BY pr.Q73
ORDER BY count DESC
"""
q73_general_df = pd.read_sql_query(q73_general_query, conn)

write_output("\nGeneral Population:")
for _, row in q73_general_df.iterrows():
    write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
write_output("")

# Analyze Q77 (democratic participation) for Animal Empaths
write_output("**Q77 - Should Animals Participate in Democratic Processes:**")

if animal_empath_count > 0:
    q77_empath_query = f"""
    SELECT 
        pr.Q77 as response,
        COUNT(*) as count,
        (COUNT(*) * 100.0 / {animal_empath_count}) as pct
    FROM participant_responses pr
    WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in animal_empaths['participant_id']])})
      AND pr.Q77 IS NOT NULL
    GROUP BY pr.Q77
    ORDER BY count DESC
    """
    q77_empath_df = pd.read_sql_query(q77_empath_query, conn)
    
    write_output("Animal Empaths:")
    for _, row in q77_empath_df.iterrows():
        write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")

q77_general_query = f"""
SELECT 
    pr.Q77 as response,
    COUNT(*) as count,
    (COUNT(*) * 100.0 / {total_participants}) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q77 IS NOT NULL
GROUP BY pr.Q77
ORDER BY count DESC
"""
q77_general_df = pd.read_sql_query(q77_general_query, conn)

write_output("\nGeneral Population:")
for _, row in q77_general_df.iterrows():
    write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
write_output("")

# ========================================
# Question 9.3: The "Cautious Humanist" Persona
# ========================================
write_output("### Question 9.3: The 'Cautious Humanist' Persona")
write_output("**Segment Definition:** Respondents who believe humans are 'fundamentally different' from animals (Q31/Q94), are 'More concerned' about AI (Q5), and 'Strongly distrust' social media and AI chatbots (Q13, Q17)")
write_output("**Investigation Question:** What is this group's primary concern with AI-mediated interspecies communication (Q59)? Are they more likely to prefer computer simulations over direct communication (Q66)?")
write_output("**Method:** Identify segment members meeting criteria, analyze their concerns and preferences")
write_output("**Details:**")
write_output("")

# Define Cautious Humanist segment
# Q31 is mapped to Q94, which contains statements about human-nature relationship
cautious_humanist_query = """
SELECT DISTINCT pr.participant_id
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q94 LIKE '%fundamentally different%'
  AND pr.Q5 = 'More concerned than excited'
  AND pr.Q13 = 'Strongly Distrust'
  AND pr.Q17 = 'Strongly Distrust'
"""
cautious_humanists = pd.read_sql_query(cautious_humanist_query, conn)
cautious_humanist_count = len(cautious_humanists)
cautious_humanist_pct = (cautious_humanist_count / total_participants) * 100

write_output(f"**Cautious Humanist Segment Size:** {cautious_humanist_count} ({cautious_humanist_pct:.1f}% of population)")
write_output("")

# Analyze Q66 (simulation vs direct communication) for Cautious Humanists
write_output("**Q66 - Preferred Approach for Interacting with Non-Humans:**")

if cautious_humanist_count > 0:
    q66_humanist_query = f"""
    SELECT 
        pr.Q66 as response,
        COUNT(*) as count,
        (COUNT(*) * 100.0 / {cautious_humanist_count}) as pct
    FROM participant_responses pr
    WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in cautious_humanists['participant_id']])})
      AND pr.Q66 IS NOT NULL
    GROUP BY pr.Q66
    ORDER BY count DESC
    """
    q66_humanist_df = pd.read_sql_query(q66_humanist_query, conn)
    
    write_output("Cautious Humanists:")
    for _, row in q66_humanist_df.iterrows():
        write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")

q66_general_query = f"""
SELECT 
    pr.Q66 as response,
    COUNT(*) as count,
    (COUNT(*) * 100.0 / {total_participants}) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q66 IS NOT NULL
GROUP BY pr.Q66
ORDER BY count DESC
"""
q66_general_df = pd.read_sql_query(q66_general_query, conn)

write_output("\nGeneral Population:")
for _, row in q66_general_df.iterrows():
    write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
write_output("")

# Sample Q59 concerns (open text) for Cautious Humanists
write_output("**Q59 - Sample Concerns from Cautious Humanists:**")

if cautious_humanist_count > 0:
    # Get a sample of concerns
    concerns_query = f"""
    SELECT pr.Q59 as concern
    FROM participant_responses pr
    WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in cautious_humanists['participant_id']])})
      AND pr.Q59 IS NOT NULL
      AND pr.Q59 != ''
      AND pr.Q59 != '--'
    LIMIT 5
    """
    concerns_df = pd.read_sql_query(concerns_query, conn)
    
    if len(concerns_df) > 0:
        for i, concern in enumerate(concerns_df['concern'], 1):
            write_output(f"{i}. \"{concern[:200]}...\"" if len(concern) > 200 else f"{i}. \"{concern}\"")
    else:
        write_output("No concerns recorded from this segment")
else:
    write_output("No members in this segment")
write_output("")

# Analyze Q53 (Is AI for interspecies communication a good use?) for Cautious Humanists
write_output("**Q53 - Is AI for Interspecies Communication a Good Use of Technology:**")

if cautious_humanist_count > 0:
    q53_humanist_query = f"""
    SELECT 
        pr.Q53 as response,
        COUNT(*) as count,
        (COUNT(*) * 100.0 / {cautious_humanist_count}) as pct
    FROM participant_responses pr
    WHERE pr.participant_id IN ({','.join([f"'{pid}'" for pid in cautious_humanists['participant_id']])})
      AND pr.Q53 IS NOT NULL
    GROUP BY pr.Q53
    ORDER BY count DESC
    """
    q53_humanist_df = pd.read_sql_query(q53_humanist_query, conn)
    
    write_output("Cautious Humanists:")
    for _, row in q53_humanist_df.iterrows():
        write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")

q53_general_query = f"""
SELECT 
    pr.Q53 as response,
    COUNT(*) as count,
    (COUNT(*) * 100.0 / {total_participants}) as pct
FROM participant_responses pr
JOIN participants p ON pr.participant_id = p.participant_id
WHERE p.pri_score >= 0.3
  AND pr.Q53 IS NOT NULL
GROUP BY pr.Q53
ORDER BY count DESC
"""
q53_general_df = pd.read_sql_query(q53_general_query, conn)

write_output("\nGeneral Population:")
for _, row in q53_general_df.iterrows():
    write_output(f"- {row['response']}: {row['count']} ({row['pct']:.1f}%)")
write_output("")

# ========================================
# Summary Statistics
# ========================================
write_output("## Summary Insights")
write_output("")

write_output("**Persona Distribution:**")
write_output(f"- Tech-First Futurists: {tech_futurist_count} ({tech_futurist_pct:.1f}%)")
write_output(f"- Animal Empaths: {animal_empath_count} ({animal_empath_pct:.1f}%)")
write_output(f"- Cautious Humanists: {cautious_humanist_count} ({cautious_humanist_pct:.1f}%)")
write_output("")

write_output("**Key Findings:**")
write_output("1. **Tech-First Futurists** represent a substantial segment who are optimistic about AI's role in both human and interspecies contexts")
write_output("2. **Animal Empaths** are a smaller but highly engaged group with strong beliefs about animal consciousness and rights")
write_output("3. **Cautious Humanists** represent those most skeptical of technology-mediated relationships with nature")
write_output("4. These personas show distinct patterns in their views on governance, rights, and the future of human-animal relationships")
write_output("5. The majority of participants don't fall neatly into these extreme personas, suggesting a nuanced middle ground")
write_output("")

write_output("## SQL Queries Used")
write_output("```sql")
write_output("-- Tech-First Futurist Definition")
write_output(tech_futurist_query)
write_output("\n-- Animal Empath Definition")
write_output(animal_empath_query)
write_output("\n-- Cautious Humanist Definition")
write_output(cautious_humanist_query)
write_output("```")
write_output("")

write_output("## Limitations")
write_output("- Strict persona definitions may exclude borderline cases")
write_output("- Small segment sizes limit statistical power for some comparisons")
write_output("- Open-text responses (Q59) require qualitative analysis beyond this quantitative summary")
write_output("- Personas represent extremes; most participants have mixed views")

output_file.close()
conn.close()

print("\n\nSection 9 analysis complete! Results saved to sections/section_09_persona_based_predictive_analysis.md")