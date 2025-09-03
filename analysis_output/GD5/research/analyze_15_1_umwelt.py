#!/usr/bin/env python3
"""
Section 15.1: Umwelt Imagination and Representation
Analyzing Q48 (imagine umwelt) -> Q50 (importance) -> Q73-77 (representation)
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, spearmanr

conn = sqlite3.connect('file:/Users/evan/Documents/GitHub/project-gd5-insights/Data/GD5/GD5.db?mode=ro', uri=True)

# Get relevant data
df = pd.read_sql_query("""
SELECT 
    participant_id,
    Q48 as imagine_umwelt,
    Q50 as importance_understanding,
    Q73 as legal_representation,
    Q74 as legal_rep_all_animals,
    Q75 as who_represents,
    Q76 as ecocentric_society,
    Q77 as democratic_participation
FROM participant_responses
""", conn)

print("=== Q48: HOW OFTEN IMAGINE ANIMAL UMWELT ===")
print(df['imagine_umwelt'].value_counts())

print("\n=== Q50: IMPORTANCE OF UNDERSTANDING ===")
print(df['importance_understanding'].value_counts())

# Convert to numeric scales
def freq_to_numeric(val):
    if pd.isna(val) or val == '--':
        return np.nan
    val_lower = str(val).lower()
    if 'very often' in val_lower or 'all the time' in val_lower:
        return 5
    elif 'often' in val_lower:
        return 4
    elif 'sometimes' in val_lower:
        return 3
    elif 'rarely' in val_lower:
        return 2
    elif 'never' in val_lower:
        return 1
    return np.nan

def importance_to_numeric(val):
    if pd.isna(val) or val == '--':
        return np.nan
    val_lower = str(val).lower()
    if 'very important' in val_lower:
        return 5
    elif 'somewhat important' in val_lower:
        return 4
    elif 'neutral' in val_lower:
        return 3
    elif 'not very important' in val_lower:
        return 2
    elif 'not important at all' in val_lower:
        return 1
    return np.nan

df['imagine_numeric'] = df['imagine_umwelt'].apply(freq_to_numeric)
df['importance_numeric'] = df['importance_understanding'].apply(importance_to_numeric)

# Correlation between imagination frequency and importance rating
valid_data = df[['imagine_numeric', 'importance_numeric']].dropna()
if len(valid_data) > 2:
    corr, p_value = spearmanr(valid_data['imagine_numeric'], valid_data['importance_numeric'])
    print(f"\n=== CORRELATION: IMAGINATION FREQUENCY vs IMPORTANCE ===")
    print(f"Spearman correlation: {corr:.3f}")
    print(f"P-value: {p_value:.6f}")
    print(f"Significant: {'YES' if p_value < 0.05 else 'NO'}")

# Analyze by imagination frequency groups
df['frequent_imaginer'] = df['imagine_numeric'] >= 4  # Often or Very Often

print(f"\n=== FREQUENT IMAGINERS vs OTHERS ===")
print(f"Frequent imaginers: {df['frequent_imaginer'].sum()} ({df['frequent_imaginer'].mean()*100:.1f}%)")

# Compare importance ratings
freq_importance = df[df['frequent_imaginer']]['importance_numeric'].dropna()
other_importance = df[~df['frequent_imaginer']]['importance_numeric'].dropna()

print(f"\nImportance ratings (mean):")
print(f"  Frequent imaginers: {freq_importance.mean():.2f}")
print(f"  Others: {other_importance.mean():.2f}")

# Very Important percentage
freq_very_imp = (df[df['frequent_imaginer']]['importance_understanding'] == 'Very important').mean() * 100
other_very_imp = (df[~df['frequent_imaginer']]['importance_understanding'] == 'Very important').mean() * 100

print(f"\n'Very Important' percentage:")
print(f"  Frequent imaginers: {freq_very_imp:.1f}%")
print(f"  Others: {other_very_imp:.1f}%")

# Analyze support for representation (Q73-77)
print(f"\n=== REPRESENTATION SUPPORT BY IMAGINATION FREQUENCY ===")

# Q73: Legal representation support
def support_representation(val):
    if pd.isna(val) or val == '--':
        return False
    return 'agree' in str(val).lower()

freq_legal_support = df[df['frequent_imaginer']]['legal_representation'].apply(support_representation).mean() * 100
other_legal_support = df[~df['frequent_imaginer']]['legal_representation'].apply(support_representation).mean() * 100

print(f"\nQ73 - Legal representation support:")
print(f"  Frequent imaginers: {freq_legal_support:.1f}%")
print(f"  Others: {other_legal_support:.1f}%")

# Q77: Democratic participation
freq_demo = df[df['frequent_imaginer']]['democratic_participation'].value_counts(normalize=True).head(3) * 100
other_demo = df[~df['frequent_imaginer']]['democratic_participation'].value_counts(normalize=True).head(3) * 100

print(f"\nQ77 - Democratic participation (top responses):")
print("Frequent imaginers:")
for val, pct in freq_demo.items():
    if pd.notna(val) and val != '--':
        print(f"  {str(val)[:50]}...: {pct:.1f}%")

print("\nOthers:")
for val, pct in other_demo.items():
    if pd.notna(val) and val != '--':
        print(f"  {str(val)[:50]}...: {pct:.1f}%")

# Statistical test for Q77
contingency = pd.crosstab(df['frequent_imaginer'], df['democratic_participation'])
if contingency.shape[0] > 1 and contingency.shape[1] > 1:
    chi2, p_value, dof, expected = chi2_contingency(contingency)
    print(f"\nStatistical test for democratic participation:")
    print(f"  Chi-square: {chi2:.2f}, p-value: {p_value:.6f}")

conn.close()