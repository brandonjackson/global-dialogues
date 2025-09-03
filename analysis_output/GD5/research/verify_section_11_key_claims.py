#!/usr/bin/env python3
"""
Verify key claims in Section 11: AI, Trust, and Technology Adoption
"""
import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

print("=== VERIFYING SECTION 11 KEY CLAIMS ===\n")

# === Claim 1: Daily users show 65.2% trust vs 38.4% among non-users ===
print("=== CLAIM 1: DAILY AI USERS TRUST RATES ===")

# Get Q20 and Q57 cross-tabulation
q20_q57_query = """
SELECT Q20, Q57, COUNT(*) as count
FROM participant_responses
WHERE Q20 IS NOT NULL AND Q20 != '--' AND Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q20, Q57
"""
q20_q57_df = pd.read_sql_query(q20_q57_query, conn)
pivot = q20_q57_df.pivot(index='Q20', columns='Q57', values='count').fillna(0)

# Calculate trust percentages (trust = "Strongly trust" + "Somewhat trust")
percentages = pivot.div(pivot.sum(axis=1), axis=0) * 100

trust_cols = [col for col in percentages.columns if 'trust' in col.lower() and 'distrust' not in col.lower()]
if trust_cols:
    trust_by_usage = percentages[trust_cols].sum(axis=1)
    print("Trust percentages by AI usage frequency:")
    for usage, pct in trust_by_usage.items():
        if 'daily' in usage.lower():
            daily_trust = pct
            print(f"  Daily users: {pct:.1f}%")
        elif 'never' in usage.lower():
            never_trust = pct
            print(f"  Never users: {pct:.1f}%")
        else:
            print(f"  {usage}: {pct:.1f}%")
    
    print(f"\nCLAIM: Daily (65.2%) vs Never (38.4%) - difference 26.8%")
    if 'daily_trust' in locals() and 'never_trust' in locals():
        actual_diff = daily_trust - never_trust
        print(f"ACTUAL: Daily ({daily_trust:.1f}%) vs Never ({never_trust:.1f}%) - difference {actual_diff:.1f}%")

# === Claim 2: Those distrusting representatives show 48.3% trust vs 42.1% ===
print("\n\n=== CLAIM 2: REPRESENTATIVE DISTRUST -> AI TRUST ===")

q14_q57_query = """
SELECT Q14, Q57, COUNT(*) as count
FROM participant_responses
WHERE Q14 IS NOT NULL AND Q14 != '--' AND Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q14, Q57
"""
q14_q57_df = pd.read_sql_query(q14_q57_query, conn)
pivot_14 = q14_q57_df.pivot(index='Q14', columns='Q57', values='count').fillna(0)

# Calculate trust percentages by representative trust level
percentages_14 = pivot_14.div(pivot_14.sum(axis=1), axis=0) * 100

trust_by_rep_trust = percentages_14[trust_cols].sum(axis=1) if trust_cols else pd.Series()
print("AI translation trust by representative trust level:")
distrust_groups = []
trust_groups = []

for rep_trust, ai_trust_pct in trust_by_rep_trust.items():
    print(f"  {rep_trust}: {ai_trust_pct:.1f}%")
    if 'distrust' in rep_trust.lower():
        distrust_groups.append(ai_trust_pct)
    elif 'trust' in rep_trust.lower() and 'distrust' not in rep_trust.lower():
        trust_groups.append(ai_trust_pct)

if distrust_groups and trust_groups:
    avg_distrust_ai = np.mean(distrust_groups)
    avg_trust_ai = np.mean(trust_groups)
    print(f"\nCLAIM: Distrust reps -> 48.3% AI trust vs Trust reps -> 42.1%")
    print(f"ACTUAL: Distrust reps -> {avg_distrust_ai:.1f}% vs Trust reps -> {avg_trust_ai:.1f}%")

# === Claim 3: 123 respondents (12.2% of interested) are conflicted ===
print("\n\n=== CLAIM 3: CONFLICTED RESPONDENTS ===")

# Total "Very interested"
total_interested_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q55 = 'Very interested'
"""
total_interested = pd.read_sql_query(total_interested_query, conn)['count'].iloc[0]

# Very interested but distrust (Strongly + Somewhat)
conflicted_query = """
SELECT COUNT(*) as count
FROM participant_responses
WHERE Q55 = 'Very interested'
  AND (Q57 = 'Strongly distrust' OR Q57 = 'Somewhat distrust')
"""
conflicted_count = pd.read_sql_query(conflicted_query, conn)['count'].iloc[0]

conflicted_pct = (conflicted_count / total_interested * 100) if total_interested > 0 else 0

print(f"Total 'Very interested': {total_interested}")
print(f"Conflicted (interested but distrust): {conflicted_count}")
print(f"Percentage: {conflicted_pct:.1f}%")
print(f"\nCLAIM: 123 respondents (12.2% of interested)")
print(f"ACTUAL: {conflicted_count} respondents ({conflicted_pct:.1f}% of interested)")

# === General Q57 distribution check ===
print("\n\n=== Q57 DISTRIBUTION VERIFICATION ===")
q57_query = """
SELECT Q57, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM participant_responses WHERE Q57 IS NOT NULL AND Q57 != '--'), 1) as percentage
FROM participant_responses 
WHERE Q57 IS NOT NULL AND Q57 != '--'
GROUP BY Q57
ORDER BY count DESC
"""
q57_results = pd.read_sql_query(q57_query, conn)
print("Q57 Translation Trust Distribution:")
for _, row in q57_results.iterrows():
    print(f"  {row['Q57']}: {row['count']} ({row['percentage']}%)")

conn.close()