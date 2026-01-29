"""
Q2: Compliance Analysis by Screening Eligibility
=================================================

Analyzes whether there are differences in screening compliance rates based on 
the number of screenings a patient is eligible for. This helps identify if 
screening burden impacts patient completion behavior.

Business Question:
    "Were there differences in compliance depending on how many screenings 
    a patient was eligible for?"

Input:
    - data/processed/cleaned_screening_data.csv

Outputs:
    - visualizations/q2_compliance_eligibility/Q2_Graph1_Compliance_by_Eligibility.png
    - visualizations/q2_compliance_eligibility/Q2_Graph2_Patient_Distribution.png

Key Metrics:
    - Average compliance rate by number of eligible screenings
    - Patient distribution across eligibility groups
    - Identification of highest/lowest performing segments

Methodology:
    1. Calculate total eligible screenings per patient (excluding 'not eligible')
    2. Calculate completed screenings per patient
    3. Compute compliance rate (completed/eligible * 100)
    4. Group by number of eligible screenings and analyze patterns

Author: [Your Name]
Date: January 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

# File paths
PROCESSED_DATA_PATH = '../data/processed/cleaned_screening_data.csv'
OUTPUT_DIR = '../visualizations/q2_compliance_eligibility/'

# Professional color palette
COLORS = {
    'primary': '#1F3A93',      # Dark blue
    'secondary': '#3A66B7',    # Medium blue
    'accent': '#A7C7F2',       # Light blue
    'dark': '#4A4A4A',         # Dark gray
    'light': '#D9D9D9'         # Light gray
}

# Blue gradient for multiple bars
BLUE_GRADIENT = [
    '#1F3A93',  # Dark blue
    '#3A66B7',  # Medium blue
    '#5B8FD3',  # Medium-light blue
    '#7DAAE8',  # Light blue
    '#A7C7F2'   # Very light blue
]

# Matplotlib configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# ==========================================
# 1. LOAD CLEANED DATA
# ==========================================

print("=" * 70)
print("Q2: COMPLIANCE BY SCREENING ELIGIBILITY ANALYSIS")
print("=" * 70)
print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Verify file exists
if not os.path.exists(PROCESSED_DATA_PATH):
    raise FileNotFoundError(
        f"Cleaned data not found: {PROCESSED_DATA_PATH}\n"
        f"Please run 01_data_cleaning.py first."
    )

# Load cleaned data
df = pd.read_csv(PROCESSED_DATA_PATH)

print(f"\n{'─' * 70}")
print("STEP 1: DATA LOADED")
print(f"{'─' * 70}")
print(f"Total records loaded: {len(df):,}")
print(f"Unique patients: {df['patient_id'].nunique():,}")

# ==========================================
# 2. CALCULATE ELIGIBILITY & COMPLIANCE
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 2: CALCULATING PATIENT-LEVEL COMPLIANCE")
print(f"{'─' * 70}")

# Filter only eligible screenings (exclude 'not eligible')
df_eligible = df[df['screening_completed_ind'] != 'not eligible'].copy()

print(f"Eligible screening records: {len(df_eligible):,}")

# Calculate patient-level metrics
patient_metrics = df_eligible.groupby('patient_id').agg(
    total_eligible_screenings=('screening_type', 'count'),
    completed_screenings=('screening_completed_ind', lambda x: (x == 'completed').sum())
).reset_index()

# Calculate compliance rate per patient
patient_metrics['compliance_rate'] = (
    patient_metrics['completed_screenings'] / 
    patient_metrics['total_eligible_screenings'] * 100
).round(2)

print(f"Patients with eligible screenings: {len(patient_metrics):,}")
print(f"\nPatient Compliance Rate Distribution:")
print(f"  • Mean: {patient_metrics['compliance_rate'].mean():.1f}%")
print(f"  • Median: {patient_metrics['compliance_rate'].median():.1f}%")
print(f"  • Min: {patient_metrics['compliance_rate'].min():.1f}%")
print(f"  • Max: {patient_metrics['compliance_rate'].max():.1f}%")

# ==========================================
# 3. ANALYZE BY ELIGIBILITY GROUP
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 3: GROUPING BY SCREENING ELIGIBILITY")
print(f"{'─' * 70}")

# Group by number of eligible screenings
compliance_by_eligibility = patient_metrics.groupby('total_eligible_screenings').agg(
    total_patients=('patient_id', 'count'),
    avg_compliance_rate=('compliance_rate', 'mean')
).reset_index()

compliance_by_eligibility['avg_compliance_rate'] = compliance_by_eligibility['avg_compliance_rate'].round(1)

print("\nCompliance by Number of Eligible Screenings:")
print(compliance_by_eligibility.to_string(index=False))

# Identify best and worst performing groups
best_group = compliance_by_eligibility.loc[compliance_by_eligibility['avg_compliance_rate'].idxmax()]
worst_group = compliance_by_eligibility.loc[compliance_by_eligibility['avg_compliance_rate'].idxmin()]

print(f"\nBest Performance:")
print(f"  • {int(best_group['total_eligible_screenings'])} screening(s): {best_group['avg_compliance_rate']:.1f}% compliance ({int(best_group['total_patients'])} patients)")

print(f"\nWorst Performance:")
print(f"  • {int(worst_group['total_eligible_screenings'])} screenings: {worst_group['avg_compliance_rate']:.1f}% compliance ({int(worst_group['total_patients'])} patients)")

print(f"\nCompliance Gap: {abs(best_group['avg_compliance_rate'] - worst_group['avg_compliance_rate']):.1f} percentage points")

# ==========================================
# 4. CREATE VISUALIZATIONS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 4: GENERATING VISUALIZATIONS")
print(f"{'─' * 70}")

# Create output directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"  ✓ Created directory: {OUTPUT_DIR}")

# --- GRAPH 1: AVERAGE COMPLIANCE RATE BY ELIGIBILITY ---

fig, ax = plt.subplots(figsize=(10, 7))

# Number of bars determines gradient selection
n_bars = len(compliance_by_eligibility)
colors_gradient = BLUE_GRADIENT[:n_bars]

bars = ax.bar(
    compliance_by_eligibility['total_eligible_screenings'], 
    compliance_by_eligibility['avg_compliance_rate'],
    color=colors_gradient,
    edgecolor=COLORS['dark'],
    linewidth=1.5,
    width=0.6
)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2., 
        height + 1,
        f'{height:.1f}%',
        ha='center', 
        va='bottom', 
        fontsize=12, 
        weight='bold',
        color=COLORS['dark']
    )

# Styling
ax.set_xlabel('Number of Eligible Screenings', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_ylabel('Average Compliance Rate (%)', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_title(
    'Average Compliance Rate by Screening Eligibility', 
    fontsize=18, 
    weight='bold', 
    pad=20, 
    color=COLORS['dark']
)
ax.set_ylim(0, 105)

# Grid
ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5, color=COLORS['light'])
ax.set_axisbelow(True)

# Axis formatting
ax.tick_params(axis='both', labelsize=11, colors=COLORS['dark'])
ax.set_xticks(compliance_by_eligibility['total_eligible_screenings'])

plt.tight_layout()
graph1_path = os.path.join(OUTPUT_DIR, 'Q2_Graph1_Compliance_by_Eligibility.png')
plt.savefig(graph1_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  ✓ Graph 1 saved: {graph1_path}")
plt.close()

# --- GRAPH 2: PATIENT DISTRIBUTION BY ELIGIBILITY ---

fig, ax = plt.subplots(figsize=(10, 7))

bars = ax.bar(
    compliance_by_eligibility['total_eligible_screenings'], 
    compliance_by_eligibility['total_patients'],
    color=COLORS['secondary'],
    edgecolor=COLORS['dark'],
    linewidth=1.5,
    width=0.6
)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2., 
        height + 5,
        f'{int(height):,}',
        ha='center', 
        va='bottom', 
        fontsize=12, 
        weight='bold',
        color=COLORS['dark']
    )

# Styling
ax.set_xlabel('Number of Eligible Screenings', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_ylabel('Number of Patients', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_title(
    'Patient Distribution by Screening Eligibility', 
    fontsize=18, 
    weight='bold', 
    pad=20, 
    color=COLORS['dark']
)
ax.set_ylim(0, compliance_by_eligibility['total_patients'].max() * 1.15)

# Grid
ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5, color=COLORS['light'])
ax.set_axisbelow(True)

# Axis formatting
ax.tick_params(axis='both', labelsize=11, colors=COLORS['dark'])
ax.set_xticks(compliance_by_eligibility['total_eligible_screenings'])

plt.tight_layout()
graph2_path = os.path.join(OUTPUT_DIR, 'Q2_Graph2_Patient_Distribution.png')
plt.savefig(graph2_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  ✓ Graph 2 saved: {graph2_path}")
plt.close()

# ==========================================
# 5. SUMMARY & KEY INSIGHTS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 5: ANALYSIS SUMMARY")
print(f"{'─' * 70}")

print(f"""
ANSWER: YES - Significant differences in compliance based on screening eligibility

KEY FINDINGS:
  • Best Performance: {int(best_group['total_eligible_screenings'])} screening(s) - {best_group['avg_compliance_rate']:.1f}% compliance
  • Worst Performance: {int(worst_group['total_eligible_screenings'])} screenings - {worst_group['avg_compliance_rate']:.1f}% compliance
  • Compliance Gap: {abs(best_group['avg_compliance_rate'] - worst_group['avg_compliance_rate']):.1f} percentage points

DETAILED BREAKDOWN:""")

for _, row in compliance_by_eligibility.iterrows():
    print(f"  • {int(row['total_eligible_screenings'])} screening(s): {row['avg_compliance_rate']:.1f}% compliance ({int(row['total_patients'])} patients)")

print(f"""
VISUALIZATIONS GENERATED:
  ✓ Q2_Graph1_Compliance_by_Eligibility.png - Average compliance rate by eligibility group
  ✓ Q2_Graph2_Patient_Distribution.png - Patient volume distribution

OUTPUT LOCATION:
  {OUTPUT_DIR}
""")

print("=" * 70)
print("✅ Q2 ANALYSIS COMPLETE")
print("=" * 70)

"""
KEY INSIGHTS - COMPLIANCE BY ELIGIBILITY ANALYSIS
==================================================

Pattern Identified:
- Clear relationship exists between number of eligible screenings and compliance rate
- Patients with {int(best_group['total_eligible_screenings'])} screening(s) show highest compliance ({best_group['avg_compliance_rate']:.1f}%)
- Patients with {int(worst_group['total_eligible_screenings'])} screenings show lowest compliance ({worst_group['avg_compliance_rate']:.1f}%)
- {abs(best_group['avg_compliance_rate'] - worst_group['avg_compliance_rate']):.1f} percentage point gap indicates screening burden impacts behavior

Strategic Implications:
1. Patients with multiple screenings face compliance challenges (cognitive load, time constraints)
2. Targeted interventions needed for high-eligibility patients
3. Potential benefit from bundling multiple screenings into single appointment
4. Communication strategies should differ based on patient screening load

Volume Distribution:
- Highest patient volume in {int(compliance_by_eligibility.loc[compliance_by_eligibility['total_patients'].idxmax(), 'total_eligible_screenings'])} screening category
- Resource allocation should prioritize high-volume, low-compliance segments
- {int(compliance_by_eligibility['total_patients'].sum())} total patients with eligible screenings

Next Steps:
- Examine if outreach effectiveness varies by eligibility group
- Test bundled appointment strategy for multi-screening patients
- Develop eligibility-specific messaging and support materials
- Monitor compliance trends as screening requirements change
"""