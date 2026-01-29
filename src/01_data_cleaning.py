"""
Healthcare Screening Data Cleaning & Validation
===============================================

This script performs comprehensive data cleaning and validation on the UHHC 
outbound call center dataset for preventive healthcare screening analysis.

Input:
    - data/raw/DA_outbound_call_nursing_team.csv (1,988 raw records)

Output:
    - data/processed/cleaned_screening_data.csv (validated dataset)

Transformations:
    - Validates screening types against approved list
    - Standardizes boolean indicators to descriptive text
    - Converts date fields to datetime format
    - Enforces logical consistency (e.g., not_called → no call date)
    - Removes invalid records (screening type 'A1C')

Author: Isaac C.
Date: January 2026
"""

import pandas as pd
import os
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

# File paths
RAW_DATA_PATH = '../data/raw/DA_outbound_call_nursing_team.csv'
PROCESSED_DATA_PATH = '../data/processed/cleaned_screening_data.csv'

# Valid screening types per specification
VALID_SCREENING_TYPES = ['BCS', 'COL', 'EED', 'CBP', 'OMW']

# Display configuration
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# ==========================================
# 1. LOAD RAW DATA
# ==========================================

print("=" * 70)
print("UHHC SCREENING DATA CLEANING & VALIDATION")
print("=" * 70)
print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Verify file exists
if not os.path.exists(RAW_DATA_PATH):
    raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_PATH}")

df = pd.read_csv(RAW_DATA_PATH)

print(f"\n{'─' * 70}")
print("STEP 1: RAW DATA LOADED")
print(f"{'─' * 70}")
print(f"Records loaded: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")
print(f"\nColumn names: {list(df.columns)}")

# ==========================================
# 2. DATA CLEANING & VALIDATION
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 2: DATA CLEANING & VALIDATION")
print(f"{'─' * 70}")

# 2.1 Patient ID Validation
print("\n[1/6] Validating patient_id...")
initial_nulls = df['patient_id'].isnull().sum()
print(f"  ✓ Missing values: {initial_nulls}")
print(f"  ✓ Unique patients: {df['patient_id'].nunique():,}")

# 2.2 Screening Type Validation
print("\n[2/6] Cleaning screening_type...")
df['screening_type'] = df['screening_type'].str.strip().str.upper()

# Identify invalid types
invalid_types = df[~df['screening_type'].isin(VALID_SCREENING_TYPES)]['screening_type'].unique()
if len(invalid_types) > 0:
    print(f"  ⚠ Invalid types found: {list(invalid_types)}")

# Remove invalid records
records_before = len(df)
df = df[df['screening_type'].isin(VALID_SCREENING_TYPES)]
records_removed = records_before - len(df)

print(f"  ✓ Records removed: {records_removed}")
print(f"  ✓ Valid types retained: {sorted(df['screening_type'].unique())}")

# 2.3 Screening Completion Indicator
print("\n[3/6] Standardizing screening_completed_ind...")

# Mapping for boolean values
completion_mapping = {
    '0': 0, '0.0': 0, 0: 0, 0.0: 0,
    '1': 1, '1.0': 1, 1: 1, 1.0: 1,
    's': 1, 'S': 1  # Handle inconsistent 's' values
}

df['screening_completed_ind'] = df['screening_completed_ind'].replace(completion_mapping)
df['screening_completed_ind'] = pd.to_numeric(df['screening_completed_ind'], errors='coerce')

# Convert to descriptive text
df['screening_completed_ind'] = df['screening_completed_ind'].map({
    0: 'not completed',
    1: 'completed'
})
df['screening_completed_ind'] = df['screening_completed_ind'].fillna('not eligible')

# Distribution
completion_dist = df['screening_completed_ind'].value_counts()
print(f"  ✓ Distribution:")
for status, count in completion_dist.items():
    print(f"      {status}: {count:,} ({count/len(df)*100:.1f}%)")

# 2.4 Screening Date
print("\n[4/6] Converting screening_date to datetime...")
df['screening_date'] = pd.to_datetime(df['screening_date'], errors='coerce', format='%Y-%m-%d')

valid_dates = df['screening_date'].notna().sum()
print(f"  ✓ Valid dates: {valid_dates:,}")
if valid_dates > 0:
    print(f"  ✓ Date range: {df['screening_date'].min()} to {df['screening_date'].max()}")

# 2.5 Latest Call Date
print("\n[5/6] Converting latest_call_date to datetime...")
df['latest_call_date'] = pd.to_datetime(df['latest_call_date'], errors='coerce', format='%Y-%m-%d')

valid_call_dates = df['latest_call_date'].notna().sum()
print(f"  ✓ Valid call dates: {valid_call_dates:,}")
if valid_call_dates > 0:
    print(f"  ✓ Call date range: {df['latest_call_date'].min()} to {df['latest_call_date'].max()}")

# 2.6 Reached Indicator
print("\n[6/6] Standardizing reached_ind...")

# Mapping for reach status
reach_mapping = {
    '0': 0, '0.0': 0, 0: 0, 0.0: 0,
    '1': 1, '1.0': 1, 1: 1, 1.0: 1,
    '1 and reached': 1
}

df['reached_ind'] = df['reached_ind'].replace(reach_mapping)
df['reached_ind'] = pd.to_numeric(df['reached_ind'], errors='coerce')

# Convert to descriptive text
df['reached_ind'] = df['reached_ind'].map({
    0: 'not reached',
    1: 'reached'
})
df['reached_ind'] = df['reached_ind'].fillna('not called')

# Distribution
reach_dist = df['reached_ind'].value_counts()
print(f"  ✓ Distribution:")
for status, count in reach_dist.items():
    print(f"      {status}: {count:,} ({count/len(df)*100:.1f}%)")

# Enforce logical consistency
inconsistencies = (df['reached_ind'] == 'not called') & (df['latest_call_date'].notna())
if inconsistencies.sum() > 0:
    print(f"  ⚠ Fixing {inconsistencies.sum()} logical inconsistencies (not called but has call date)")
    df.loc[df['reached_ind'] == 'not called', 'latest_call_date'] = pd.NaT

# ==========================================
# 3. SAVE CLEANED DATA
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 3: SAVING CLEANED DATA")
print(f"{'─' * 70}")

# Ensure output directory exists
output_dir = os.path.dirname(PROCESSED_DATA_PATH)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"  ✓ Created directory: {output_dir}")

# Save cleaned dataset
df.to_csv(PROCESSED_DATA_PATH, index=False)
file_size = os.path.getsize(PROCESSED_DATA_PATH) / 1024  # KB

print(f"  ✓ File saved: {PROCESSED_DATA_PATH}")
print(f"  ✓ File size: {file_size:.1f} KB")
print(f"  ✓ Final records: {len(df):,}")
print(f"  ✓ Final columns: {len(df.columns)}")

# ==========================================
# 4. DATA QUALITY SUMMARY
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 4: DATA QUALITY SUMMARY")
print(f"{'─' * 70}")

print(f"\nRecords Summary:")
print(f"  • Original records: 1,988")
print(f"  • Invalid records removed: {records_removed} (screening type 'A1C')")
print(f"  • Final clean records: {len(df):,}")
print(f"  • Unique patients: {df['patient_id'].nunique():,}")

print(f"\nData Types:")
for col in df.columns:
    print(f"  • {col}: {df[col].dtype}")

print(f"\nMissing Values:")
null_counts = df.isnull().sum()
if null_counts.sum() == 0:
    print(f"  ✓ No unexpected missing values")
else:
    for col, count in null_counts[null_counts > 0].items():
        print(f"  • {col}: {count:,} ({count/len(df)*100:.1f}%)")

print(f"\nScreening Type Distribution:")
for screening, count in df['screening_type'].value_counts().sort_index().items():
    print(f"  • {screening}: {count:,} ({count/len(df)*100:.1f}%)")

# ==========================================
# 5. VALIDATION CHECKS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 5: VALIDATION CHECKS")
print(f"{'─' * 70}")

checks_passed = True

# Check 1: All screening types valid
invalid_screening_types = df[~df['screening_type'].isin(VALID_SCREENING_TYPES)]
if len(invalid_screening_types) == 0:
    print("  ✓ All screening types are valid")
else:
    print(f"  ✗ Found {len(invalid_screening_types)} invalid screening types")
    checks_passed = False

# Check 2: Boolean indicators have correct values
valid_completion = df['screening_completed_ind'].isin(['completed', 'not completed', 'not eligible']).all()
valid_reach = df['reached_ind'].isin(['reached', 'not reached', 'not called']).all()

if valid_completion and valid_reach:
    print("  ✓ All boolean indicators properly formatted")
else:
    print("  ✗ Invalid boolean indicator values found")
    checks_passed = False

# Check 3: Logical consistency
consistency_check = ((df['reached_ind'] == 'not called') & (df['latest_call_date'].notna())).sum()
if consistency_check == 0:
    print("  ✓ Logical consistency maintained (not called = no call date)")
else:
    print(f"  ✗ Found {consistency_check} logical inconsistencies")
    checks_passed = False

# Check 4: Date formats
if df['screening_date'].dtype == 'datetime64[ns]' and df['latest_call_date'].dtype == 'datetime64[ns]':
    print("  ✓ Date fields properly formatted")
else:
    print("  ✗ Date formatting issues detected")
    checks_passed = False

# Final validation status
print(f"\n{'=' * 70}")
if checks_passed:
    print("✅ DATA CLEANING COMPLETE - ALL VALIDATION CHECKS PASSED")
else:
    print("⚠️  DATA CLEANING COMPLETE - SOME VALIDATION CHECKS FAILED")
print(f"{'=' * 70}\n")

"""
KEY INSIGHTS FROM DATA CLEANING
================================

Data Quality:
- Successfully cleaned 1,982 records (99.7% of original data)
- Removed 6 records with invalid screening type 'A1C'
- Standardized all boolean indicators to human-readable format
- Enforced logical consistency across related fields

Screening Distribution:
- 5 screening types validated: BCS, COL, EED, CBP, OMW
- Patient eligibility varies by screening type
- Significant portion of patients eligible for multiple screenings

Call Center Activity:
- Three distinct patient states: reached, not reached, not called
- Latest call dates range from [DATE_RANGE]
- Opportunity exists to expand outreach to uncalled patients

Next Steps:
- Proceed to exploratory data analysis (EDA)
- Analyze reach effectiveness by patient segments
- Examine compliance patterns by screening type and reach status
"""