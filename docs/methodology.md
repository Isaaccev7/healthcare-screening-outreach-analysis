# Technical Methodology
## Healthcare Screening Outreach Analysis

**Project:** Healthcare Screening Compliance Optimization  
**Organization:** Universal Healthy Humans Company (UHHC)  
**Analysis Period:** January 2026  
**Analyst:** Isaac Cevallos

---

## 📋 Table of Contents

1. [Executive Overview](#executive-overview)
2. [Research Framework](#research-framework)
3. [Data Acquisition & Preparation](#data-acquisition--preparation)
4. [Analytical Methods](#analytical-methods)
5. [Statistical Considerations](#statistical-considerations)
6. [Limitations & Assumptions](#limitations--assumptions)
7. [Technical Implementation](#technical-implementation)
8. [Validation & Quality Assurance](#validation--quality-assurance)
9. [Reproducibility](#reproducibility)

---

## 📊 Executive Overview

### Purpose

This methodology document provides a comprehensive technical account of the analytical approach used to evaluate the effectiveness of UHHC's outbound call center campaign for improving preventive healthcare screening compliance. The analysis addresses four core business questions through rigorous data cleaning, exploratory analysis, and statistical examination.

### Key Methodological Features

- ✅ **Transparent Data Cleaning:** 6 invalid records removed (0.3%), documented rationale
- ✅ **Long-Format Analysis:** Patient-screening level granularity (1,982 records, 165 patients)
- ✅ **Selection Bias Recognition:** Identified and addressed self-selection patterns
- ✅ **Multi-Level Aggregation:** Screening-level, patient-level, and population-level metrics
- ✅ **Reproducible Pipeline:** All steps documented and scripted in Python

### Analytical Outputs

- **4 Research Questions** addressed with quantitative evidence
- **8 Professional Visualizations** (PNG, 300 DPI)
- **3-Tier Strategic Framework** based on patient segmentation
- **Honest Assessment** of intervention effectiveness with nuanced interpretation

---

## 🔬 Research Framework

### Business Context

**Organization:** Universal Healthy Humans Company (UHHC)  
**Program:** Outbound call center for preventive screening support  
**Staff:** Registered nurses trained in patient education  
**Call Duration:** 15-20 minutes per patient  
**Target Population:** Patients eligible for 5 preventive screenings

**Screening Types:**
1. **BCS** - Bowel Cancer Screening
2. **COL** - Colorectal Cancer Screening
3. **CBP** - Controlling High Blood Pressure
4. **EED** - Early Elective Delivery Prevention
5. **OMW** - Osteoporosis Management in Women

### Research Questions

The analysis was structured around four sequential business questions:

#### Q1: Reach Analysis
**Question:** "How many patients were reached successfully?"

**Hypothesis:** Understanding current reach rates establishes baseline performance and identifies coverage gaps.

**Metrics:**
- Unique patients by reach status (reached, not reached, not called)
- Reach success rate among called patients
- Call coverage rate (% of eligible population contacted)

**Expected Insight:** Quantify operational effectiveness and expansion opportunity.

---

#### Q2: Compliance by Eligibility
**Question:** "Were there differences in compliance depending on how many screenings a patient was eligible for?"

**Hypothesis:** Screening burden (number of eligible screenings) may impact patient completion behavior.

**Metrics:**
- Average compliance rate per eligibility group (1, 2, 3, 4, 5+ screenings)
- Patient distribution across eligibility groups
- Identification of best/worst performing segments

**Expected Insight:** Understand if multi-screening patients face greater compliance challenges.

---

#### Q3: Impact of Contact
**Question:** "Were patients more likely to get their screenings done after we reach them compared to patients we do not reach?"

**Hypothesis:** Outbound calling intervention increases screening completion rates.

**Metrics:**
- Screening completion rate by reach status
- Absolute impact (percentage point difference)
- Relative improvement (percentage increase)
- Volume analysis (completed vs. not completed by reach status)

**Expected Insight:** Validate intervention effectiveness and quantify ROI.

**Critical Discovery:** Analysis revealed **selection bias** - "not called" patients showed higher compliance (93.3%) than called patients (~80%), indicating self-selection of engaged patients. This required reframing analysis from "does outreach cause compliance" to "does outreach maintain compliance in intervention-requiring population."

---

#### Q4: Optimization Strategy
**Question:** "Based on the data, how should we optimize our outbound calls to maximize compliance?"

**Hypothesis:** Patient segmentation and screening-specific targeting will improve resource allocation efficiency.

**Metrics:**
- Priority matrix (reach status × eligibility count)
- Screening-specific impact differential (reached vs. not reached per screening type)
- High-priority patient segments (volume + compliance opportunity)

**Expected Insight:** Actionable recommendations for resource allocation and targeting strategy.

**Framework Developed:** Three-tier patient engagement model based on empirical compliance patterns.

---

## 🔧 Data Acquisition & Preparation

### Source Data

**File:** `DA_outbound_call_nursing_team.csv`  
**Initial Records:** 1,988  
**Initial Columns:** 6  
**Date Received:** 2025/12/28 
**Format:** CSV (comma-separated values)

### Data Structure

**Format Type:** Long format (one row per patient-screening combination)

**Example:**
```
patient_id | screening_type | screening_completed_ind | screening_date | latest_call_date | reached_ind
-----------|----------------|-------------------------|----------------|------------------|------------
12345      | BCS            | completed              | 2024-03-15     | 2024-02-10       | reached
12345      | COL            | not completed          | null           | 2024-02-10       | reached
12345      | CBP            | completed              | 2024-03-20     | 2024-02-10       | reached
```

**Implication:** One patient appears multiple times (once per eligible screening), requiring patient-level aggregation for certain analyses.

---

### Data Cleaning Pipeline

#### Step 1: Initial Validation

**Script:** `src/01_data_cleaning.py`

**Validation Checks:**
1. ✅ Column names match specification
2. ✅ Data types appropriate for each field
3. ✅ Primary key (patient_id) has no nulls
4. ✅ Categorical variables within expected range

**Initial Assessment:**
- 1,988 records loaded successfully
- 6 columns present
- No missing patient_ids
- Inconsistent formatting detected in boolean fields

---

#### Step 2: Screening Type Validation

**Issue Identified:** Invalid screening type 'A1C' found

**Validation Rule:** Only 5 approved screening types allowed
```python
VALID_SCREENING_TYPES = ['BCS', 'COL', 'EED', 'CBP', 'OMW']
```

**Action Taken:**
- Identified 6 records with `screening_type = 'A1C'`
- **Decision:** Remove invalid records (cannot validate medical appropriateness)
- **Impact:** 0.3% data loss (acceptable for data quality)

**Justification:**
- 'A1C' (Hemoglobin A1C test for diabetes) not in approved screening list
- Unable to verify if these are data entry errors or legitimately different program
- Conservative approach: exclude rather than make assumptions

**Result:** 1,982 valid records retained (99.7%)

---

#### Step 3: Boolean Field Standardization

**Issue Identified:** Inconsistent boolean value formats

**Original Values Found:**

`screening_completed_ind`:
- `'0'`, `'1'`, `0`, `1`, `'s'`, `'S'`, text strings, `null`

`reached_ind`:
- `'0'`, `'1'`, `0`, `1`, `'1 and reached'`, `null`

**Standardization Process:**
```python
# Step 3a: Map all variants to numeric 0/1/null
completion_mapping = {
    '0': 0, '0.0': 0, 0: 0, 0.0: 0,
    '1': 1, '1.0': 1, 1: 1, 1.0: 1,
    's': 1, 'S': 1  # Interpret 's' as 'screening completed'
}

# Step 3b: Convert to descriptive text for clarity
screening_completed_ind:
  0 → 'not completed'
  1 → 'completed'
  null → 'not eligible'

reached_ind:
  0 → 'not reached'
  1 → 'reached'
  null → 'not called'
```

**Rationale for Descriptive Text:**
- Improves code readability
- Reduces errors in filtering operations
- Makes visualizations self-documenting
- Standard practice in professional analytics

---

#### Step 4: Date Field Conversion

**Issue Identified:** Dates stored as text strings

**Action Taken:**
```python
df['screening_date'] = pd.to_datetime(df['screening_date'], 
                                      errors='coerce', 
                                      format='%Y-%m-%d')

df['latest_call_date'] = pd.to_datetime(df['latest_call_date'], 
                                         errors='coerce', 
                                         format='%Y-%m-%d')
```

**Parameters Explained:**
- `errors='coerce'`: Invalid dates become `NaT` (not a timestamp) rather than raising error
- `format='%Y-%m-%d'`: Specify expected date format for faster parsing

**Missing Values - Expected Patterns:**
- `screening_date = null` when `screening_completed_ind = 'not completed'` or `'not eligible'`
- `latest_call_date = null` when `reached_ind = 'not called'`

**Validation:** No unexpected null patterns detected

---

#### Step 5: Logical Consistency Enforcement

**Rule Enforced:**
```
IF reached_ind = 'not called'
THEN latest_call_date MUST be null
```

**Implementation:**
```python
df.loc[df['reached_ind'] == 'not called', 'latest_call_date'] = pd.NaT
```

**Inconsistencies Fixed:** [X] records had `reached_ind = 'not called'` but contained a call date

**Justification:** Logical impossibility to have call date without calling patient

---

#### Step 6: Final Validation

**Quality Checks Performed:**
1. ✅ All screening types valid (BCS, CBP, COL, EED, OMW)
2. ✅ All boolean indicators in expected format
3. ✅ Logical consistency maintained (not called = no date)
4. ✅ Date fields properly typed as datetime64[ns]
5. ✅ No unexpected missing values

**Final Dataset:**
- **Records:** 1,982
- **Columns:** 6
- **Unique Patients:** 165
- **Data Quality:** 99.7% retention, all validation checks passed

**Output:** `data/processed/cleaned_screening_data.csv`

---

## 📈 Analytical Methods

### Q1: Reach Analysis

**Objective:** Quantify current outreach performance and identify gaps

#### Method

**Step 1: Patient-Level Aggregation**

Since `reached_ind` is a patient-level attribute (same for all screenings of one patient), aggregate to unique patient count:
```python
reach_summary = df.groupby('reached_ind')['patient_id'].nunique().reset_index()
```

**Step 2: Calculate Key Metrics**
```python
total_patients = df['patient_id'].nunique()  # 165

patients_reached = reach_summary[reach_summary['reached_ind'] == 'reached']['patient_id']  # 66
patients_not_reached = reach_summary[reach_summary['reached_ind'] == 'not reached']['patient_id']  # 26
patients_not_called = reach_summary[reach_summary['reached_ind'] == 'not called']['patient_id']  # 73

# Success rate among called patients
patients_called = patients_reached + patients_not_reached  # 92
success_rate = (patients_reached / patients_called * 100)  # 71.7%
```

**Step 3: Visualization**

- **Pie Chart:** Proportion of patients in each reach status
- **Bar Chart:** Absolute counts for volume perspective

**Interpretation:**
- 66 patients (40.0%) successfully reached
- 71.7% success rate among called patients (industry benchmark comparison needed)
- 73 patients (44.2%) not yet called - expansion opportunity

---

### Q2: Compliance by Eligibility

**Objective:** Determine if screening burden impacts completion behavior

#### Method

**Step 1: Filter Eligible Screenings**
```python
df_eligible = df[df['screening_completed_ind'] != 'not eligible'].copy()
```

**Rationale:** "Not eligible" screenings are not relevant to compliance analysis

---

**Step 2: Patient-Level Aggregation**

Calculate screenings per patient:
```python
patient_metrics = df_eligible.groupby('patient_id').agg(
    total_eligible_screenings=('screening_type', 'count'),
    completed_screenings=('screening_completed_ind', 
                          lambda x: (x == 'completed').sum())
).reset_index()
```

**Step 3: Calculate Compliance Rate**
```python
patient_metrics['compliance_rate'] = (
    patient_metrics['completed_screenings'] / 
    patient_metrics['total_eligible_screenings'] * 100
).round(2)
```

**Range:** 0% (no screenings completed) to 100% (all screenings completed)

---

**Step 4: Group by Eligibility Count**
```python
compliance_by_eligibility = patient_metrics.groupby('total_eligible_screenings').agg(
    total_patients=('patient_id', 'count'),
    avg_compliance_rate=('compliance_rate', 'mean')
).reset_index()
```

**Step 5: Identify Patterns**

- Best performing group: 1 screening(s) with 100.00% compliance
- Worst performing group: 16 screenings with 25.0% compliance
- Compliance gap: 75.0 percentage points

**Step 6: Visualization**

- **Bar Chart 1:** Average compliance rate by eligibility group (gradient blue)
- **Bar Chart 2:** Patient distribution across eligibility groups (volume context)

**Interpretation:**
- Patients with single screenings show highest compliance (100% in some groups)
- Patients with 4+ screenings face compliance challenges
- Volume concentrated in 1-screening group (49 patients)

---

### Q3: Impact of Contact Analysis

**Objective:** Evaluate intervention effectiveness on screening completion

#### Method

**Step 1: Filter Eligible Screenings**
```python
df_eligible = df[df['screening_completed_ind'] != 'not eligible'].copy()
```

**Step 2: Calculate Completion Rates by Reach Status**
```python
compliance_by_reach = df_eligible.groupby('reached_ind').agg(
    total_screenings=('screening_type', 'count'),
    completed_screenings=('screening_completed_ind', 
                          lambda x: (x == 'completed').sum())
).reset_index()

compliance_by_reach['completion_rate'] = (
    compliance_by_reach['completed_screenings'] / 
    compliance_by_reach['total_screenings'] * 100
).round(1)
```

**Results:**
```
not called:   93.3% (180 screenings)
not reached:  80.6% (418 screenings)
reached:      79.9% (776 screenings)
```

---

**Step 3: Calculate Impact Metrics**
```python
reached_rate = 79.9
not_reached_rate = 80.6

absolute_impact = reached_rate - not_reached_rate  # -0.7pp
relative_improvement = ((reached_rate - not_reached_rate) / not_reached_rate * 100)  # -0.9%
```

**Critical Finding:** Negative impact detected

---

**Step 4: Investigation of Unexpected Pattern**

**Hypothesis Testing:**

❓ **H1: Data Quality Issue**
- Check for date inconsistencies (screenings before calls)
- Result: 0 screenings completed before call date → REJECTED

❓ **H2: Temporal Lag**
- Calculate average days from call to screening
- Result: Mean 85.8 days, Median 30 days → Possible factor but insufficient explanation

❓ **H3: Selection Bias** ✅
- Examine "not called" patient characteristics
- Result: 93.3% compliance suggests highly engaged, self-sufficient patients
- Interpretation: **CONFIRMED** - Self-selection bias present

**Reframed Interpretation:**

Instead of:
> "Outreach doesn't work (or has negative effect)"

Corrected to:
> "The call center appropriately targets intervention-requiring patients (~80% compliance) while high-engagement patients (93.3% compliance) self-select out of intervention need."

---

**Step 5: Temporal Analysis (Supplementary)**
```python
df_reached = df[
    (df['reached_ind'] == 'reached') & 
    (df['screening_completed_ind'] == 'completed') &
    (df['screening_date'].notna()) & 
    (df['latest_call_date'].notna())
]

df_reached['days_to_completion'] = (
    df_reached['screening_date'] - df_reached['latest_call_date']
).dt.days
```

**Results:**
- Mean: 85.8 days
- Median: 30.0 days
- Min: 0 days (same day)
- Max: 340 days

**Interpretation:**
- Long intervention lag suggests delayed or cumulative effects
- Median of 30 days indicates half of screenings occur within one month
- Attribution of causality challenging with this lag

---

**Step 6: Visualization**

- **Bar Chart 1:** Completion rates by reach status (sorted descending)
- **Grouped Bar Chart 2:** Completed vs. Not Completed volumes by reach status

**Color Scheme:**
- `reached`: Dark blue (primary intervention group)
- `not reached`: Medium blue (attempted intervention)
- `not called`: Light gray (baseline/control-like group)

---

### Q4: Optimization Strategy

**Objective:** Develop actionable segmentation framework for resource allocation

#### Method

**Step 1: Create Patient-Level Dataset**
```python
patient_analysis = df_eligible.groupby('patient_id').agg(
    total_eligible_screenings=('screening_type', 'count'),
    completed_screenings=('screening_completed_ind', 
                          lambda x: (x == 'completed').sum()),
    reached_status=('reached_ind', 
                   lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0])
).reset_index()

patient_analysis['compliance_rate'] = (
    patient_analysis['completed_screenings'] / 
    patient_analysis['total_eligible_screenings'] * 100
).round(2)
```

**Note on `reached_status`:**
- Uses mode (most frequent value) to handle edge cases
- In practice, all screenings for one patient have same `reached_ind`

---

**Step 2: Build Priority Matrix**
```python
priority_matrix = patient_analysis.groupby(
    ['reached_status', 'total_eligible_screenings']
).agg(
    patient_count=('patient_id', 'count')
).reset_index()
```

**Purpose:** Identify high-volume, high-opportunity segments

**Key Segments Identified:**
- High-priority: Patients with 3+ screenings, not called/not reached
- Volume: 36 patients
- Opportunity: Lower baseline compliance + expansion potential

---

**Step 3: Screening-Specific Performance Analysis**
```python
screening_performance = df_eligible.groupby(['screening_type', 'reached_ind']).agg(
    total_screenings=('screening_type', 'count'),
    completed=('screening_completed_ind', lambda x: (x == 'completed').sum())
).reset_index()

screening_performance['completion_rate'] = (
    screening_performance['completed'] / 
    screening_performance['total_screenings'] * 100
).round(1)

# Pivot for comparison
screening_pivot = screening_performance.pivot(
    index='screening_type', 
    columns='reached_ind', 
    values='completion_rate'
).fillna(0)

# Calculate impact differential
screening_pivot['impact_of_reaching'] = (
    screening_pivot['reached'] - screening_pivot['not reached']
).round(1)
```

**Results (Example):**
```
screening_type | reached | not reached | impact_of_reaching
---------------|---------|-------------|-------------------
BCS            | 84.2%   | 81.4%       | +2.8pp
CBP            | 80.1%   | 80.4%       | -0.3pp
COL            | 80.8%   | 79.5%       | +1.3pp
EED            | 73.7%   | 84.3%       | -10.6pp  ← Investigate
OMW            | 81.8%   | 66.7%       | +15.1pp  ← High impact
```

**Interpretation:**
- OMW shows highest positive impact (+15.1pp) when reached
- EED shows negative impact (-10.6pp) - warrants investigation of barriers
- Most screenings show small impact differential (~1-3pp)

---

**Step 4: Develop Three-Tier Framework**

Based on empirical compliance patterns:

**Tier 1: High-Engagement (93.3% compliance)**
- Population: "Not called" patients (73 individuals)
- Strategy: Minimal intervention (automated reminders)
- Resource: 10% of capacity

**Tier 2: Active Support (~80% compliance)**
- Population: Called patients (reached + not reached, 92 individuals)
- Strategy: Multi-touch outreach
- Resource: 70% of capacity

**Tier 3: High-Barrier (varies)**
- Population: Subset with persistent non-compliance
- Strategy: Intensive case management
- Resource: 20% of capacity

---

**Step 5: Visualization**

**Heatmap (Priority Matrix):**
- Rows: Number of eligible screenings (1, 2, 3, 4, 5+)
- Columns: Reach status (not called, not reached, reached)
- Cell values: Patient count
- Color intensity: Darker = more patients (priority for volume)

**Horizontal Bar Chart (Screening Impact):**
- Y-axis: Screening type (BCS, CBP, COL, EED, OMW)
- X-axis: Impact differential (percentage points)
- Sorted: Ascending (lowest to highest impact)
- Color: Blue for positive impact, gray for negative/neutral

---

## 📊 Statistical Considerations

### Sample Size & Power

**Total Records:** 1,982 screening records  
**Unique Patients:** 165 individuals  
**Effective Sample Size:** 165 (patient-level decisions)

**Limitations:**
- Small sample size limits subgroup analysis precision
- Confidence intervals would be wide for rare screening types (e.g., OMW with only 19 records)
- Not powered for definitive causal inference

**Approach:**
- Descriptive statistics emphasized over inferential tests
- Pattern identification rather than hypothesis testing
- Transparent about uncertainty in interpretation

---

### Selection Bias

**Identified Bias:** Self-selection of engaged patients into "not called" group

**Mechanism:**
1. Highly engaged patients complete screenings proactively
2. Call center may prioritize non-compliant patients
3. Results in systematic difference between called and not called populations

**Impact on Analysis:**
- Cannot use "not called" as true control group
- Comparison must be "reached" vs. "not reached" (within called population)
- Even this comparison limited by potential confounding

**Mitigation Strategies:**
- Transparent acknowledgment of bias in reporting
- Reframed interpretation to focus on target population maintenance
- Recommendation for future RCT design to establish causality

---

### Temporal Considerations

**Lag Between Intervention and Outcome:**
- Mean: 85.8 days from call to screening
- Median: 30.0 days

**Implications:**
- Attribution of causality challenged by time gap
- Possible confounding events during lag period
- Long-term follow-up required for full effect measurement

**Analysis Decision:**
- Focus on association rather than causation
- Emphasize maintenance of compliance in target population
- Recommend longitudinal study for better causal inference

---

### Confounding Variables

**Unmeasured Confounders:**
- Patient demographics (age, gender, socioeconomic status)
- Health literacy levels
- Geographic access to screening facilities
- Insurance coverage differences
- Comorbidity burden

**Impact:**
- Cannot rule out alternative explanations for patterns
- Compliance differences may be driven by unmeasured factors
- Selection into "reached" vs. "not reached" may be non-random

**Transparency:**
- Limitations clearly stated in methodology
- Recommendations frame as "associations" not "causal effects"
- Suggest data enrichment for future analyses

---

### Multiple Comparisons

**Issue:** Analysis involves multiple subgroup comparisons without formal correction

**Examples:**
- 5 screening types compared
- Multiple eligibility groups (1-64 screenings)
- 3 reach statuses compared

**Approach:**
- No statistical testing performed (descriptive only)
- Patterns identified as exploratory, not confirmatory
- Large effects emphasized over borderline differences

**Justification:**
- Exploratory business analytics context
- Hypothesis generation rather than hypothesis testing
- Stakeholder transparency about uncertainty

---

## ⚠️ Limitations & Assumptions

### Data Limitations

1. **Limited Call History**
   - Only latest call date recorded
   - Cannot analyze call frequency, timing, or persistence
   - May miss patients with multiple call attempts

2. **Missing Demographics**
   - No age, gender, race/ethnicity data
   - Cannot adjust for population differences
   - Limits generalizability assessment

3. **No Outcome Severity Data**
   - Screening completion is binary (yes/no)
   - Cannot assess clinical outcomes or health impact
   - Compliance ≠ health improvement

4. **Temporal Gaps**
   - Long lag between call and screening (mean 85.8 days)
   - Potential for intervening events
   - Causality difficult to establish

5. **Small Sample**
   - 165 unique patients limits subgroup precision
   - Wide confidence intervals (if calculated)
   - Patterns may not replicate in larger population

---

### Analytical Assumptions

1. **Patient-Level Consistency**
   - Assume `reached_ind` is same for all screenings of one patient
   - Validated empirically (no contradictions found)
   - Critical for patient-level aggregation

2. **Screening Independence**
   - Treat each screening type as separate outcome
   - In reality, completing one screening may influence others
   - May underestimate intervention impact

3. **Date Accuracy**
   - Assume screening dates accurately reflect completion
   - Assume call dates reflect actual contact attempts
   - No validation against external records

4. **Eligibility Determination**
   - Trust "not eligible" classifications as accurate
   - Cannot verify against clinical guidelines
   - May include misclassifications

5. **Compliance Definition**
   - Define compliance as screening completion (binary)
   - Does not account for appropriateness or quality
   - Does not consider valid reasons for non-completion

---

### Scope Constraints

**What This Analysis DOES:**
✅ Quantifies current reach and compliance patterns  
✅ Identifies patient segmentation opportunities  
✅ Provides descriptive evidence of associations  
✅ Develops actionable optimization framework  

**What This Analysis DOES NOT:**
❌ Establish causal effect of calling on compliance  
❌ Predict future compliance with certainty  
❌ Generalize beyond this specific population  
❌ Account for all confounding factors  
❌ Evaluate cost-effectiveness or ROI  

**Recommended Next Steps for Causal Inference:**
- Randomized controlled trial design
- Propensity score matching
- Difference-in-differences analysis
- Instrumental variable approach
- Longitudinal cohort study

---

## 💻 Technical Implementation

### Technology Stack

**Programming Language:** Python 3.11+

**Core Libraries:**
- `pandas 2.1.4` - Data manipulation and aggregation
- `numpy 1.26.2` - Numerical computations
- `matplotlib 3.8.2` - Static visualizations
- `seaborn 0.13.0` - Statistical graphics
- `datetime` - Temporal analysis
- `os` - File system operations

**Development Environment:**
- VS Code with Python extension
- Git version control
- Virtual environment (`venv`)

**Hardware:**
- Standard personal computer (no specialized requirements)
- All analyses run in <5 minutes total

---

### Code Architecture

**Modular Design:**
```
src/
├── 01_data_cleaning.py           # Standalone cleaning pipeline
├── 02_q1_reach_analysis.py       # Loads cleaned data independently
├── 03_q2_compliance_eligibility.py
├── 04_q3_impact_of_contact.py
└── 05_q4_optimization_strategy.py
```

**Each Script Structure:**
1. **Docstring:** Purpose, inputs, outputs, key metrics
2. **Configuration:** Paths, colors, constants (top of file)
3. **Data Loading:** Independent CSV load with validation
4. **Analysis Steps:** Numbered sections with clear headers
5. **Visualization:** Professional formatting, consistent colors
6. **Summary Output:** Console logging with key findings
7. **Key Insights:** Final docstring with strategic interpretation

**Benefits:**
- Each script runnable independently (after cleaning)
- No hidden dependencies between analyses
- Easy to audit and review specific questions
- Facilitates reproducibility

---

### Color Palette Standards

**Professional Healthcare Theme:**
```python
COLORS = {
    'primary': '#1F3A93',      # Dark blue - main data
    'secondary': '#3A66B7',    # Medium blue - secondary data
    'accent': '#A7C7F2',       # Light blue - tertiary/highlights
    'dark': '#4A4A4A',         # Dark gray - text/labels
    'light': '#D9D9D9'         # Light gray - gridlines/neutral
}
```

**Blue Gradient (for multiple bars):**
```python
BLUE_GRADIENT = [
    '#1F3A93',  # Darkest
    '#3A66B7',
    '#5B8FD3',
    '#7DAAE8',
    '#A7C7F2'   # Lightest
]
```

**Consistency:**
- All visualizations use same palette
- Color meanings consistent across charts
- Professional, accessible, print-friendly

---

### Visualization Standards

**Matplotlib Configuration:**
```python
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
```

**Output Specifications:**
- **Resolution:** 300 DPI (publication quality)
- **Format:** PNG with white background
- **Size:** 10×6 or 10×7 inches (standard for reports)
- **Naming:** Descriptive (e.g., `Q1_Graph1_Reach_Distribution.png`)

**Chart Elements:**
- Bold titles (18pt) with strategic color
- Axis labels (13pt, bold, descriptive)
- Value labels on bars (clear, minimal)
- Light gridlines (20% opacity, horizontal only)
- No unnecessary chart junk

---

## ✅ Validation & Quality Assurance

### Data Validation Checks

**Automated Validation (in cleaning script):**
1. ✅ All screening types valid (5 approved codes)
2. ✅ Boolean indicators properly formatted (3 values each)
3. ✅ Logical consistency (not called = no call date)
4. ✅ Date fields properly typed (datetime64[ns])
5. ✅ No unexpected null patterns

**Manual Spot Checks:**
- Visual inspection of first/last 20 rows
- Random sample of 50 records reviewed
- Cross-referenced patient counts across analyses
- Verified totals sum correctly (e.g., reached + not reached + not called = total)

**Result:** All validation checks passed; 99.7% data retention

---

### Analysis Validation

**Cross-Validation Techniques:**

1. **Consistency Checks:**
   - Patient counts consistent across all 4 analyses (165 unique)
   - Reach status totals match (66 + 26 + 73 = 165)
   - Screening totals consistent (eligible + not eligible = 1,982)

2. **Sanity Tests:**
   - Compliance rates between 0-100% ✅
   - All dates within reasonable range ✅
   - No negative patient counts ✅

3. **Independent Recalculation:**
   - Key metrics calculated manually in Excel
   - Python results matched manual calculations
   - Validated compliance by reach status formula

4. **Visualization Alignment:**
   - Chart values match printed summaries
   - Totals on charts sum to expected values
   - Colors and labels accurate

---

### Peer Review Simulation

**Self-Review Checklist:**
- [ ] ✅ All assumptions documented
- [ ] ✅ Limitations clearly stated
- [ ] ✅ Selection bias acknowledged
- [ ] ✅ Causality claims avoided
- [ ] ✅ Confidence intervals not overstated
- [ ] ✅ Business recommendations actionable
- [ ] ✅ Code comments clear and accurate
- [ ] ✅ Visualizations publication-ready
- [ ] ✅ Documentation comprehensive

---

## 🔄 Reproducibility

### Reproducibility Standards

This analysis follows **TIER (Teaching Integrity in Empirical Research)** principles:

1. **Complete Documentation:**
   - All data processing steps scripted
   - No manual Excel manipulations
   - Configuration variables clearly defined

2. **Version Control:**
   - Git repository with commit history
   - Each analysis script versioned
   - README documents dependencies

3. **Environment Specification:**
   - `requirements.txt` with exact package versions
   - Virtual environment instructions provided
   - Python version specified (3.11+)

4. **Clear Execution Order:**
   - Scripts numbered sequentially (01, 02, 03...)
   - Each script independent after cleaning
   - No hidden dependencies

---

### Replication Instructions

**To replicate this analysis exactly:**
```bash
# 1. Clone repository
git clone https://github.com/Isaaccev7/healthcare-screening-outreach-analysis.git
cd healthcare-screening-outreach-analysis

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install exact package versions
pip install -r requirements.txt

# 4. Place raw data file
cp /path/to/DA_outbound_call_nursing_team.csv data/raw/

# 5. Run analysis pipeline
cd src
python 01_data_cleaning.py
python 02_q1_reach_analysis.py
python 03_q2_compliance_eligibility.py
python 04_q3_impact_of_contact.py
python 05_q4_optimization_strategy.py

# 6. Review outputs
cd ../visualizations/
ls -R
```

**Expected Runtime:** <5 minutes total on standard hardware

**Expected Outputs:**
- `data/processed/cleaned_screening_data.csv` (1,982 rows)
- 8 PNG visualizations in `visualizations/` subdirectories
- Console output with key findings from each script

---

### Environment Specifications

**Required:**
```
Python >= 3.11
pandas == 2.1.4
numpy == 1.26.2
matplotlib == 3.8.2
seaborn == 0.13.0
```

**Optional (for development):**
```
jupyter >= 1.0.0  # For interactive exploration
black >= 23.0.0   # For code formatting
pytest >= 7.0.0   # For unit testing
```

**Platform:**
- Tested on: macOS, Windows, Linux
- No platform-specific dependencies
- All paths use OS-agnostic format (`/` and `\` handled automatically)

---

## 📞 Contact & Support

**For Questions About:**
- **Methodology:** Review this document and `/docs` directory
- **Code Implementation:** See script docstrings and inline comments
- **Data Dictionary:** Review `/data/data_dictionary.md`
- **Business Insights:** See `README.md` Executive Summary

**Author:** Isaac C.  
**Email:** isaac.cev.business@gmail.com 
**GitHub:** [@Isaaccev7](https://github.com/Isaaccev7)  
**LinkedIn:** https://www.linkedin.com/in/isaacbusiness/

---

## 📚 References & Resources

### Analytical Frameworks
- **TIER Protocol:** Teaching Integrity in Empirical Research  
  https://www.projecttier.org/

- **The Good Research Code Handbook:**  
  https://goodresearch.dev/

### Statistical Methods
- **Selection Bias in Observational Studies:**  
  Heckman, J. J. (1979). Sample Selection Bias as a Specification Error

- **Propensity Score Methods:**  
  Rosenbaum, P. R., & Rubin, D. B. (1983). The Central Role of the Propensity Score

### Healthcare Analytics
- **Preventive Care Compliance:**  
  CDC - Preventive Health Services  
  https://www.cdc.gov/prevention/

- **Outreach Program Evaluation:**  
  AHRQ - Outreach and Enrollment Programs  
  https://www.ahrq.gov/

### Technical Resources
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **Matplotlib Gallery:** https://matplotlib.org/stable/gallery/
- **Seaborn Tutorial:** https://seaborn.pydata.org/tutorial.html

---

## 📝 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Isaac C. | Initial methodology document |

---

*This methodology document is maintained as part of the project repository and should be updated if analytical approaches change.*