# Data Dictionary
## Healthcare Screening Outreach Dataset

**Last Updated:** January 29, 2026  
**Dataset:** DA_outbound_call_nursing_team.csv  
**Records:** 1,982 (after cleaning)  
**Unique Patients:** 165

---

## 📋 Overview

This dataset contains records of preventive healthcare screening eligibility, completion status, and outbound call center contact attempts for patients at Universal Healthy Humans Company (UHHC). Each row represents a **patient-screening combination**, meaning individual patients may appear multiple times (once per eligible screening type).

**Data Structure:** Long format (one row per patient-screening pair)

---

## 📊 Variables

### 1. `patient_id`

**Description:** Unique identifier for each patient

**Data Type:** Numeric (Integer)  
**Format:** 22-digit number  
**Example:** `1234567890123456789012`

**Characteristics:**
- ✅ No missing values
- ✅ Unique per patient
- ✅ Used as primary key for patient-level aggregations

**Notes:**
- One patient can appear in multiple rows (one per eligible screening)
- Total unique patients in dataset: **165**

---

### 2. `screening_type`

**Description:** Abbreviation code for the type of preventive healthcare screening

**Data Type:** Character (String)  
**Format:** 3-character uppercase code  
**Possible Values:**

| Code | Full Name | Target Population |
|------|-----------|------------------|
| **BCS** | Bowel Cancer Screening | Adults 50+ |
| **CBP** | Controlling High Blood Pressure | Adults with hypertension risk |
| **COL** | Colorectal Cancer Screening | Adults 45-75 |
| **EED** | Early Elective Delivery Prevention | Pregnant women |
| **OMW** | Osteoporosis Management in Women | Women 65+ or high-risk |

**Distribution in Dataset:**
```
COL: 588 records (29.7%)
BCS: 279 records (14.1%)
CBP: 269 records (13.6%)
EED: 219 records (11.0%)
OMW:  19 records (1.0%)
Other screening combinations: 608 records (30.6%)
```

**Validation Rules:**
- ✅ Must be one of the 5 approved codes
- ❌ Invalid values (e.g., 'A1C') removed during data cleaning (6 records)

**Notes:**
- Not all screenings apply to all patients (eligibility determined by age, gender, health history)
- Patients may be eligible for 1-64 screenings (median: 8 screenings per patient)

---

### 3. `screening_completed_ind`

**Description:** Indicator of whether the patient completed the screening

**Data Type:** Categorical (String)  
**Format:** Descriptive text  
**Possible Values:**

| Value | Meaning | Interpretation |
|-------|---------|----------------|
| `'completed'` | Screening was completed | Patient fulfilled this screening requirement |
| `'not completed'` | Screening eligible but not done | Patient has not yet completed this screening |
| `'not eligible'` | Patient not eligible for this screening | Screening doesn't apply to this patient |

**Original Format (Raw Data):**
- Numeric/text inconsistencies: `'0'`, `'1'`, `'s'`, `'S'`, `0`, `1`
- Cleaned to standardized descriptive text during data processing

**Distribution in Clean Dataset:**
```
completed:      1,125 records (56.8%)
not completed:    249 records (12.6%)
not eligible:     608 records (30.7%)
```

**Business Logic:**
- **Eligible Screenings** = `completed` + `not completed` (1,374 records)
- **Compliance Rate** = `completed` / `eligible` = 81.9% (overall)

**Notes:**
- `'not eligible'` records are **excluded** from compliance calculations
- Used to calculate patient-level compliance: (completed screenings / eligible screenings)

---

### 4. `screening_date`

**Description:** Date when the screening was completed

**Data Type:** DateTime  
**Format:** `YYYY-MM-DD` (ISO 8601)  
**Example:** `2024-03-15`

**Characteristics:**
- ✅ Valid datetime format after cleaning
- ⚠️ Missing values expected (screenings not completed have no date)

**Date Range (Completed Screenings):**
- Earliest: 2024-01-04
- Latest: 2025-01-13

**Missing Values:**
- **Expected:** Rows where `screening_completed_ind = 'not completed'` or `'not eligible'`
- **Unexpected:** None after cleaning

**Analysis Use Cases:**
- Calculate time between call and screening completion
- Identify seasonal patterns in screening behavior
- Measure intervention lag (days from call to completion)

**Notes:**
- All dates converted from text to datetime during cleaning
- Used in temporal analysis (e.g., average 85.8 days from call to screening)

---

### 5. `latest_call_date`

**Description:** Date of the most recent outbound call attempt by the call center

**Data Type:** DateTime  
**Format:** `YYYY-MM-DD` (ISO 8601)  
**Example:** `2024-02-10`

**Characteristics:**
- ✅ Valid datetime format after cleaning
- ⚠️ Missing values expected for patients not called

**Date Range (Called Patients):**
- Earliest: 2024-01-01
- Latest: 2024-12-16

**Missing Values:**
- **Expected:** Rows where `reached_ind = 'not called'`
- **Validation:** Enforced consistency during cleaning (not called → no call date)

**Relationship to Other Variables:**
- If `reached_ind = 'not called'` → `latest_call_date = null`
- If `reached_ind = 'reached'` or `'not reached'` → `latest_call_date` should have valid date

**Analysis Use Cases:**
- Calculate call-to-screening interval
- Identify optimal call timing
- Track campaign timeline and duration

**Notes:**
- Represents **latest** attempt, not first attempt
- Multiple call attempts to same patient may have occurred (only latest recorded)
- Patient-level variable (same date across all screenings for one patient)

---

### 6. `reached_ind`

**Description:** Indicator of whether the patient was successfully reached during outbound calling

**Data Type:** Categorical (String)  
**Format:** Descriptive text  
**Possible Values:**

| Value | Meaning | Call Attempt Made? | Contact Successful? |
|-------|---------|-------------------|---------------------|
| `'reached'` | Patient successfully contacted | ✅ Yes | ✅ Yes |
| `'not reached'` | Call attempted but patient not contacted | ✅ Yes | ❌ No |
| `'not called'` | No call attempt made to this patient | ❌ No | N/A |

**Original Format (Raw Data):**
- Numeric/text inconsistencies: `'0'`, `'1'`, `'1 and reached'`, `0`, `1`
- Cleaned to standardized descriptive text

**Distribution in Dataset:**
```
reached:     776 records (39.1%) - 66 unique patients
not reached: 418 records (21.1%) - 26 unique patients
not called:  180 records (9.1%)  - 73 unique patients
not eligible: 608 records (30.7%) - excluded from reach analysis
```

**Business Metrics:**
- **Call Coverage:** (reached + not reached) / total = 56%
- **Reach Success Rate:** reached / (reached + not reached) = 71.7%

**Key Analysis Finding:**
- `'not called'` patients show **93.3% compliance** (self-selected high-engagement)
- `'reached'` patients show **79.9% compliance** (intervention-requiring population)
- `'not reached'` patients show **80.6% compliance** (similar to reached)

**Validation Rules:**
- ✅ Logical consistency enforced: `not called` → no `latest_call_date`
- ✅ Patient-level variable (same status across all screenings for one patient)

**Notes:**
- This is a **patient-level attribute** that appears on all screening rows for that patient
- Used to segment patients into engagement tiers for targeted interventions

---

## 🔗 Relationships Between Variables

### Patient-Level vs. Screening-Level

**Patient-Level Variables** (same value for all rows of one patient):
- `patient_id` - Unique identifier
- `reached_ind` - Contact status
- `latest_call_date` - Most recent call attempt

**Screening-Level Variables** (vary by screening type for same patient):
- `screening_type` - Specific screening
- `screening_completed_ind` - Completion status for that screening
- `screening_date` - When that specific screening was done

### Logical Dependencies
```
IF reached_ind = 'not called'
  THEN latest_call_date = null

IF screening_completed_ind = 'not eligible'
  THEN screening_date = null
  AND excluded from compliance calculations

IF screening_completed_ind = 'completed'
  THEN screening_date should have valid value
  (though some edge cases may exist)
```

---

## 📈 Derived Metrics (Not in Raw Data)

These metrics are calculated during analysis:

### Patient-Level Aggregations

1. **Total Eligible Screenings per Patient**
   - `COUNT(screening_type WHERE screening_completed_ind != 'not eligible')`
   - Range: 1-64 screenings
   - Median: 8 screenings

2. **Completed Screenings per Patient**
   - `COUNT(screening_type WHERE screening_completed_ind = 'completed')`

3. **Patient Compliance Rate**
   - `(Completed Screenings / Total Eligible Screenings) × 100`
   - Used in Q2 analysis (compliance by eligibility)

4. **Days from Call to Screening**
   - `screening_date - latest_call_date`
   - Mean: 85.8 days
   - Median: 30.0 days
   - Used in temporal analysis

### Population-Level Metrics

5. **Screening Completion Rate by Reach Status**
   - Q3 analysis primary metric
   - Example: `reached` = 79.9%, `not called` = 93.3%

6. **Reach Success Rate**
   - `reached / (reached + not reached)`
   - Current: 71.7%

7. **Call Coverage Rate**
   - `(reached + not reached) / total_patients`
   - Current: 56%

---

## ⚠️ Data Quality Notes

### Cleaning Actions Taken

1. **Invalid Screening Types Removed**
   - 6 records with `screening_type = 'A1C'` deleted
   - Final dataset: 1,982 records (99.7% retention)

2. **Standardization Applied**
   - Boolean indicators converted to descriptive text
   - Date fields converted to datetime format
   - Logical consistency enforced (e.g., not called → no call date)

3. **Validation Checks Passed**
   - ✅ All screening types valid (BCS, CBP, COL, EED, OMW)
   - ✅ All boolean indicators properly formatted
   - ✅ Logical consistency maintained
   - ✅ Date fields correctly typed

### Known Limitations

1. **Call Attempt History Incomplete**
   - Only **latest** call date recorded (not all attempts)
   - Cannot analyze call frequency or timing patterns

2. **Self-Selection Bias Present**
   - "Not called" patients may be systematically different
   - 93.3% compliance suggests high-engagement self-selection

3. **Temporal Gaps**
   - Long lag between call and screening (mean 85.8 days)
   - Difficult to attribute causality directly

4. **Limited Demographics**
   - No age, gender, or socioeconomic data
   - Cannot control for confounding variables

---

## 📚 Usage Examples

### Example 1: Calculate Patient-Level Compliance
```python
import pandas as pd

df = pd.read_csv('data/processed/cleaned_screening_data.csv')

# Filter eligible screenings only
df_eligible = df[df['screening_completed_ind'] != 'not eligible']

# Calculate compliance per patient
patient_compliance = df_eligible.groupby('patient_id').agg(
    total_eligible=('screening_type', 'count'),
    completed=('screening_completed_ind', lambda x: (x == 'completed').sum())
)

patient_compliance['compliance_rate'] = (
    patient_compliance['completed'] / patient_compliance['total_eligible'] * 100
)
```

### Example 2: Analyze Reach Effectiveness
```python
# Calculate completion rate by reach status
completion_by_reach = df_eligible.groupby('reached_ind').agg(
    total_screenings=('screening_type', 'count'),
    completed=('screening_completed_ind', lambda x: (x == 'completed').sum())
)

completion_by_reach['completion_rate'] = (
    completion_by_reach['completed'] / completion_by_reach['total_screenings'] * 100
)
```

### Example 3: Temporal Analysis
```python
# Convert dates
df['screening_date'] = pd.to_datetime(df['screening_date'])
df['latest_call_date'] = pd.to_datetime(df['latest_call_date'])

# Calculate time to screening for reached patients
df_reached = df[
    (df['reached_ind'] == 'reached') & 
    (df['screening_completed_ind'] == 'completed')
]

df_reached['days_to_completion'] = (
    df_reached['screening_date'] - df_reached['latest_call_date']
).dt.days
```

---

## 🔍 Quick Reference Summary

| Variable | Type | Missing Values | Unique Values | Primary Use |
|----------|------|----------------|---------------|-------------|
| `patient_id` | Numeric | None | 165 | Patient identification |
| `screening_type` | Categorical | None | 5 | Screening classification |
| `screening_completed_ind` | Categorical | None | 3 | Completion tracking |
| `screening_date` | DateTime | 857 (43.2%) | Varies | Temporal analysis |
| `latest_call_date` | DateTime | 788 (39.8%) | Varies | Outreach tracking |
| `reached_ind` | Categorical | None | 3 | Contact effectiveness |

---

## 📞 Questions or Issues?

For questions about this dataset or data dictionary:
- Review analysis scripts in `/src` directory
- See methodology documentation in `/docs/methodology.md`
- Contact: [Your Email]

---

*This data dictionary is maintained alongside the analysis codebase and should be updated when data structure changes.*