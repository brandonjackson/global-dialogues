# GD5 Parallel Analysis Instructions

You are analyzing GD5 survey data. Follow these steps:

## Setup
1. Navigate to the research directory: `cd analysis_output/GD5/research`
2. Run: `python section_manager.py claim` to get your next section
3. If "NO_SECTIONS_AVAILABLE" is returned, all work is complete

## For Each Claimed Section
1. Find your section number in `GD5_investigation_questions.md`
2. Use `@docs/gd_research_guide.md` for methodology guidance
3. Connect to the SQLite database using read-only mode:
   ```python
   import sqlite3
   # Adjust path as needed for GD5
   conn = sqlite3.connect('file:/path/to/gd5.db?mode=ro', uri=True)
   ```

## Analysis Process
For each question in your section:
1. **Understand**: Carefully analyze what's being asked
2. **Query**: Write and execute SQL queries to gather data
3. **Analyze**: Perform additional Python analysis if needed
4. **Document**: Record findings clearly and comprehensively

## Output Format
Save your analysis to: `sections/section_XX_[section_title_snake_case].md`

Use this exact format:
```markdown
# Section X: [Section Title]
## Analysis Date: [ISO timestamp]

### Question X.Y: [Full question text]
**Finding:** [Clear, concise answer - the key takeaway]
**Method:** [SQL query or Python approach used]
**Details:** [Extended analysis, caveats, interesting observations]
```

## Completing Your Work
1. Run: `python section_manager.py complete [section_number]`
2. Commit with message: "Complete Section X analysis"
3. Return to Setup step 2 for the next section

## Important Notes
- If a question depends on another section's findings:
  - Check if that section's file exists in `sections/`
  - If missing, note: "PENDING: Requires Section Y findings"
  - Continue with other questions in your section
- Focus on accuracy over speed
- Include actual numbers and percentages in findings
- Note any data quality issues or limitations