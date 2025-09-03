# GD5 Analysis Review Instructions

You are peer-reviewing GD5 analysis sections to ensure accuracy and completeness.

## Review Process

1. **Find sections to review**:
   - Navigate to: `cd analysis_output/GD5/research`
   - Run: `python section_manager.py status` to see what needs review
   - Look for completed sections with `review_status='pending'`

2. **Select a section**: Choose a completed but unreviewed section

3. **Open the analysis file**: `sections/section_XX_*.md`

4. **Verify each finding**:
   - Re-run SQL queries to verify numerical results
   - Check that the analysis actually answers the question
   - Verify calculations and statistical claims
   - Look for logical errors or misinterpretations
   - Ensure the finding directly addresses what was asked

## When to Make Edits

**ONLY edit if you find**:
- Factual errors in the data (wrong numbers, incorrect queries)
- Queries that don't match what's claimed
- Questions left unanswered or partially answered
- Logical or statistical errors
- Misinterpretation of the question

**DO NOT edit for**:
- Style preferences
- Minor wording changes
- Adding unnecessary detail
- Personal interpretation differences (unless factually wrong)

## Completing Review

1. If corrections were needed:
   - Make the minimum necessary edits
   - Run: `python section_manager.py complete_review [section_number]`
   - Commit: "Review Section X - corrections made: [brief description]"

2. If no corrections needed:
   - Run: `python section_manager.py complete_review [section_number]`
   - Commit: "Review Section X - verified correct"

3. Return to step 1 for next section

## Review Priorities
- Accuracy of data and calculations
- Completeness of answers
- Clarity of findings
- Logical consistency