"""
Q1: Patient Reach Analysis
===========================

Analyzes how many patients were successfully reached through the outbound 
calling campaign and examines the distribution of reach status across the 
patient population.

Business Question:
    "How many patients were reached successfully?"

Input:
    - data/processed/cleaned_screening_data.csv

Outputs:
    - visualizations/q1_reach_analysis/Q1_Graph1_Reach_Distribution.png
    - visualizations/q1_reach_analysis/Q1_Graph2_Reach_Counts.png

Key Metrics:
    - Total unique patients
    - Patients reached (count and percentage)
    - Patients not reached (count and percentage)
    - Patients not called (count and percentage)
    - Success rate among patients who were called

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
OUTPUT_DIR = '../visualizations/q1_reach_analysis/'

# Professional color palette
COLORS = {
    'primary': '#1F3A93',      # Dark blue
    'secondary': '#3A66B7',    # Medium blue
    'accent': '#A7C7F2',       # Light blue
    'dark': '#4A4A4A',         # Dark gray
    'light': '#D9D9D9'         # Light gray
}

# Matplotlib configuration for professional plots
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# ==========================================
# 1. LOAD CLEANED DATA
# ==========================================

print("=" * 70)
print("Q1: PATIENT REACH ANALYSIS")
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
print(f"Records loaded: {len(df):,}")
print(f"Unique patients: {df['patient_id'].nunique():,}")

# ==========================================
# 2. CALCULATE REACH METRICS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 2: CALCULATING REACH METRICS")
print(f"{'─' * 70}")

# Calculate unique patients by reach status
reach_summary = df.groupby('reached_ind')['patient_id'].nunique().reset_index()
reach_summary.columns = ['reach_status', 'unique_patients']

# Calculate total patients
total_patients = df['patient_id'].nunique()
reach_summary['percentage'] = (reach_summary['unique_patients'] / total_patients * 100).round(1)

# Extract key metrics
patients_reached = reach_summary[reach_summary['reach_status'] == 'reached']['unique_patients'].values[0]
patients_not_reached = reach_summary[reach_summary['reach_status'] == 'not reached']['unique_patients'].values[0]
patients_not_called = reach_summary[reach_summary['reach_status'] == 'not called']['unique_patients'].values[0]

# Calculate success rate (among patients who were called)
patients_called = patients_reached + patients_not_reached
success_rate = (patients_reached / patients_called * 100) if patients_called > 0 else 0

print(f"\nReach Status Summary:")
print(f"  • Total Patients: {total_patients:,}")
print(f"  • Patients Reached: {patients_reached:,} ({patients_reached/total_patients*100:.1f}%)")
print(f"  • Patients Not Reached: {patients_not_reached:,} ({patients_not_reached/total_patients*100:.1f}%)")
print(f"  • Patients Not Called: {patients_not_called:,} ({patients_not_called/total_patients*100:.1f}%)")
print(f"  • Success Rate (among called): {success_rate:.1f}%")

# ==========================================
# 3. CREATE VISUALIZATIONS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 3: GENERATING VISUALIZATIONS")
print(f"{'─' * 70}")

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"  ✓ Created directory: {OUTPUT_DIR}")

# --- GRAPH 1: PIE CHART - REACH STATUS DISTRIBUTION ---

fig, ax = plt.subplots(figsize=(10, 6))

# Color mapping for each reach status
colors_pie = [COLORS['secondary'], COLORS['accent'], COLORS['light']]
explode = (0.05, 0, 0)  # Slightly separate 'reached' segment

wedges, texts, autotexts = ax.pie(
    reach_summary['unique_patients'], 
    labels=None,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors_pie,
    explode=explode,
    textprops={'fontsize': 14, 'weight': 'bold', 'color': 'white'}
)

# Title
ax.set_title(
    'Patient Reach Status Distribution', 
    fontsize=18, 
    weight='bold', 
    pad=20, 
    color=COLORS['dark']
)

# Legend with patient counts
legend_labels = [
    f"{row['reach_status'].title()}: {row['unique_patients']:,}" 
    for _, row in reach_summary.iterrows()
]
ax.legend(
    legend_labels, 
    loc='upper left', 
    bbox_to_anchor=(0.85, 1), 
    frameon=False, 
    fontsize=11
)

plt.tight_layout()
graph1_path = os.path.join(OUTPUT_DIR, 'Q1_Graph1_Reach_Distribution.png')
plt.savefig(graph1_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  ✓ Graph 1 saved: {graph1_path}")
plt.close()

# --- GRAPH 2: BAR CHART - REACH STATUS COUNTS ---

fig, ax = plt.subplots(figsize=(10, 6))

# Create bars
bars = ax.bar(
    reach_summary['reach_status'], 
    reach_summary['unique_patients'],
    color=[COLORS['secondary'], COLORS['accent'], COLORS['light']],
    edgecolor=COLORS['dark'],
    linewidth=1.5,
    width=0.6
)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2., 
        height,
        f'{int(height):,}',
        ha='center', 
        va='bottom', 
        fontsize=13, 
        weight='bold',
        color=COLORS['dark']
    )

# Styling
ax.set_ylabel('Number of Patients', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_title(
    'Patients by Reach Status', 
    fontsize=18, 
    weight='bold', 
    pad=20, 
    color=COLORS['dark']
)
ax.set_ylim(0, reach_summary['unique_patients'].max() * 1.15)

# Grid
ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5, color=COLORS['light'])
ax.set_axisbelow(True)

# Axis formatting
ax.set_xticklabels(reach_summary['reach_status'], fontsize=11, color=COLORS['dark'])
ax.tick_params(axis='y', labelsize=10, colors=COLORS['dark'])

plt.tight_layout()
graph2_path = os.path.join(OUTPUT_DIR, 'Q1_Graph2_Reach_Counts.png')
plt.savefig(graph2_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  ✓ Graph 2 saved: {graph2_path}")
plt.close()

# ==========================================
# 4. SUMMARY & KEY INSIGHTS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 4: ANALYSIS SUMMARY")
print(f"{'─' * 70}")

print(f"""
ANSWER: {patients_reached:,} patients were reached successfully

KEY METRICS:
  • Total Patients: {total_patients:,}
  • Patients Reached: {patients_reached:,} ({patients_reached/total_patients*100:.1f}%)
  • Patients Not Reached: {patients_not_reached:,} ({patients_not_reached/total_patients*100:.1f}%)
  • Patients Not Called: {patients_not_called:,} ({patients_not_called/total_patients*100:.1f}%)
  • Success Rate (among called): {success_rate:.1f}%

VISUALIZATIONS GENERATED:
  ✓ Q1_Graph1_Reach_Distribution.png - Pie chart showing reach status distribution
  ✓ Q1_Graph2_Reach_Counts.png - Bar chart displaying absolute patient counts

OUTPUT LOCATION:
  {OUTPUT_DIR}
""")

print("=" * 70)
print("✅ Q1 ANALYSIS COMPLETE")
print("=" * 70)

"""
KEY INSIGHTS - PATIENT REACH ANALYSIS
======================================

Current Performance:
- The outbound call center successfully reached {patients_reached:,} unique patients
- Success rate of {success_rate:.1f}% among patients who were contacted
- {patients_not_reached:,} patients were called but not reached (opportunity for retry strategy)
- {patients_not_called:,} patients have not yet been contacted (expansion opportunity)

Strategic Implications:
1. Immediate Action: Implement multi-touch strategy for "not reached" patients
2. Expansion Opportunity: Systematically call all "not called" patients
3. Capacity Planning: Current call coverage is at {((total_patients - patients_not_called)/total_patients*100):.1f}%

Next Steps:
- Analyze compliance differences between reached vs. not reached patients (Q3)
- Identify optimal patient segments for prioritized outreach (Q4)
- Examine relationship between screening eligibility and reach success
"""