"""
Q4: Optimization Strategy for Outbound Calls
=============================================

Analyzes patient segmentation and screening-specific performance to identify 
optimal strategies for maximizing screening compliance through targeted outreach.
Provides actionable recommendations for resource allocation and campaign optimization.

Business Question:
    "Based on the data, how should we optimize our outbound calls to maximize 
    compliance?"

Input:
    - data/processed/cleaned_screening_data.csv

Outputs:
    - visualizations/q4_optimization/Q4_Graph1_Priority_Matrix.png
    - visualizations/q4_optimization/Q4_Graph2_Screening_Impact.png

Key Metrics:
    - Patient distribution by reach status and screening eligibility
    - Impact differential by screening type (reached vs not reached)
    - High-priority patient segments for targeted outreach
    - Screening types with highest intervention impact

Methodology:
    1. Create patient-level aggregation (reach status + eligibility count)
    2. Build priority matrix (heatmap) showing patient volumes by segment
    3. Analyze screening-specific completion rates by reach status
    4. Calculate impact differential (reached - not reached) per screening type
    5. Identify optimization opportunities and priority actions

Author: Isaac C.
Date: January 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

# File paths
PROCESSED_DATA_PATH = '../data/processed/cleaned_screening_data.csv'
OUTPUT_DIR = '../visualizations/q4_optimization/'

# Professional color palette
COLORS = {
    'primary': '#1F3A93',      # Dark blue
    'secondary': '#3A66B7',    # Medium blue
    'accent': '#A7C7F2',       # Light blue
    'dark': '#4A4A4A',         # Dark gray
    'light': '#D9D9D9'         # Light gray
}

# Matplotlib configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# ==========================================
# 1. LOAD CLEANED DATA
# ==========================================

print("=" * 70)
print("Q4: OPTIMIZATION STRATEGY ANALYSIS")
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
# 2. IDENTIFY PRIORITY PATIENT SEGMENTS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 2: BUILDING PRIORITY MATRIX")
print(f"{'─' * 70}")

# Filter eligible screenings
df_eligible = df[df['screening_completed_ind'] != 'not eligible'].copy()

# Create patient-level dataset
patient_analysis = df_eligible.groupby('patient_id').agg(
    total_eligible_screenings=('screening_type', 'count'),
    completed_screenings=('screening_completed_ind', lambda x: (x == 'completed').sum()),
    reached_status=('reached_ind', lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0])
).reset_index()

# Calculate compliance rate
patient_analysis['compliance_rate'] = (
    patient_analysis['completed_screenings'] / 
    patient_analysis['total_eligible_screenings'] * 100
).round(2)

print(f"Patient-level records created: {len(patient_analysis):,}")

# Create priority matrix (patient counts by segment)
priority_matrix = patient_analysis.groupby(['reached_status', 'total_eligible_screenings']).agg(
    patient_count=('patient_id', 'count')
).reset_index()

print(f"\nPriority Matrix (Patient Distribution):")
print(priority_matrix.to_string(index=False))

# Calculate high-priority segment (3+ screenings, not called/not reached)
high_priority = priority_matrix[
    (priority_matrix['reached_status'].isin(['not called', 'not reached'])) &
    (priority_matrix['total_eligible_screenings'] >= 3)
]['patient_count'].sum()

not_called_total = len(patient_analysis[patient_analysis['reached_status'] == 'not called'])
not_reached_total = len(patient_analysis[patient_analysis['reached_status'] == 'not reached'])

print(f"\nKey Segment Metrics:")
print(f"  • High-Priority Patients (3+ screenings, not called/not reached): {high_priority:,}")
print(f"  • Total Not Reached: {not_reached_total:,}")
print(f"  • Total Not Called: {not_called_total:,}")

# ==========================================
# 3. ANALYZE SCREENING TYPE PERFORMANCE
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 3: ANALYZING SCREENING-SPECIFIC IMPACT")
print(f"{'─' * 70}")

# Calculate performance by screening type and reach status
screening_performance = df_eligible.groupby(['screening_type', 'reached_ind']).agg(
    total_screenings=('screening_type', 'count'),
    completed=('screening_completed_ind', lambda x: (x == 'completed').sum())
).reset_index()

# Calculate completion rate
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

# Calculate impact of reaching patients
screening_pivot['impact_of_reaching'] = (
    screening_pivot['reached'] - screening_pivot['not reached']
).round(1)

# Sort by impact (ascending for horizontal bar chart)
screening_pivot = screening_pivot.sort_values('impact_of_reaching', ascending=True)

print("\nScreening Type Impact Analysis:")
print(screening_pivot[['reached', 'not reached', 'impact_of_reaching']].to_string())

# Identify top impact screenings
top_impact_screenings = screening_pivot.nlargest(3, 'impact_of_reaching')

print(f"\nTop 3 Screening Types by Impact:")
for screening_type in top_impact_screenings.index:
    impact = screening_pivot.loc[screening_type, 'impact_of_reaching']
    reached_rate = screening_pivot.loc[screening_type, 'reached']
    print(f"  • {screening_type}: +{impact:.1f}pp impact ({reached_rate:.1f}% completion when reached)")

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

# --- GRAPH 1: HEATMAP - PRIORITY MATRIX ---

fig, ax = plt.subplots(figsize=(10, 8))

# Pivot for heatmap
pivot_counts = priority_matrix.pivot(
    index='total_eligible_screenings',
    columns='reached_status',
    values='patient_count'
).fillna(0)

# Reorder columns for logical flow
column_order = ['not called', 'not reached', 'reached']
pivot_counts = pivot_counts[[col for col in column_order if col in pivot_counts.columns]]

# Create heatmap
sns.heatmap(
    pivot_counts, 
    annot=True, 
    fmt='.0f', 
    cmap=sns.light_palette(COLORS['secondary'], as_cmap=True),
    cbar_kws={'label': 'Patient Count'},
    linewidths=2, 
    linecolor='white',
    annot_kws={'fontsize': 12, 'weight': 'bold'},
    ax=ax
)

# Styling
ax.set_title(
    'Priority Matrix: Patient Distribution\nby Reach Status & Screening Eligibility', 
    fontsize=18, 
    weight='bold', 
    pad=20, 
    color=COLORS['dark']
)
ax.set_xlabel('Reach Status', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_ylabel('Number of Eligible Screenings', fontsize=13, weight='bold', color=COLORS['dark'])

# Clean axis labels
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=11, color=COLORS['dark'])
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=11, color=COLORS['dark'])

plt.tight_layout()
graph1_path = os.path.join(OUTPUT_DIR, 'Q4_Graph1_Priority_Matrix.png')
plt.savefig(graph1_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  ✓ Graph 1 saved: {graph1_path}")
plt.close()

# --- GRAPH 2: HORIZONTAL BAR - SCREENING TYPE IMPACT ---

fig, ax = plt.subplots(figsize=(10, 7))

# Get impact data
screening_impact_data = screening_pivot['impact_of_reaching'].sort_values(ascending=True)

# Color based on impact value (positive = dark blue, negative/zero = gray)
colors_impact = [
    COLORS['primary'] if x > 0 else COLORS['light'] 
    for x in screening_impact_data.values
]

bars = ax.barh(
    screening_impact_data.index, 
    screening_impact_data.values,
    color=colors_impact, 
    edgecolor=COLORS['dark'], 
    linewidth=1.5
)

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    label_x = width + (0.5 if width > 0 else -0.5)
    ha = 'left' if width > 0 else 'right'
    ax.text(
        label_x, 
        bar.get_y() + bar.get_height()/2,
        f'{width:.1f}pp',
        ha=ha, 
        va='center', 
        fontsize=11, 
        weight='bold',
        color=COLORS['dark']
    )

# Add zero line
ax.axvline(x=0, color=COLORS['dark'], linestyle='-', linewidth=2)

# Styling
ax.set_xlabel('Impact of Reaching Patients (Percentage Points)', fontsize=13, weight='bold', color=COLORS['dark'])
ax.set_title(
    'Impact of Reaching Patients by Screening Type', 
    fontsize=18, 
    weight='bold', 
    pad=20, 
    color=COLORS['dark']
)

# Grid
ax.grid(axis='x', alpha=0.2, linestyle='-', linewidth=0.5, color=COLORS['light'])
ax.set_axisbelow(True)

# Axis formatting
ax.tick_params(axis='both', labelsize=11, colors=COLORS['dark'])

plt.tight_layout()
graph2_path = os.path.join(OUTPUT_DIR, 'Q4_Graph2_Screening_Impact.png')
plt.savefig(graph2_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  ✓ Graph 2 saved: {graph2_path}")
plt.close()

# ==========================================
# 5. SUMMARY & KEY INSIGHTS
# ==========================================

print(f"\n{'─' * 70}")
print("STEP 5: OPTIMIZATION RECOMMENDATIONS")
print(f"{'─' * 70}")

print(f"""
ANSWER: Implement a 4-pillar optimization strategy

PRIORITY SEGMENTS:
  • High Priority: {high_priority:,} patients with 3+ screenings (not called/not reached)
  • Medium Priority: {not_reached_total:,} patients who were called but not reached
  • Expansion Opportunity: {not_called_total:,} patients who haven't been called yet

TOP SCREENING TYPES BY IMPACT:""")

for screening_type in screening_pivot.index[-3:]:
    impact = screening_pivot.loc[screening_type, 'impact_of_reaching']
    reached_rate = screening_pivot.loc[screening_type, 'reached']
    print(f"  • {screening_type}: +{impact:.1f}pp improvement when reached ({reached_rate:.1f}% completion)")

print(f"""
OPTIMIZATION STRATEGIES:

1. PRIORITIZE HIGH-IMPACT SEGMENTS
   → Focus on {high_priority:,} patients with 3+ eligible screenings
   → These patients have lowest baseline compliance but highest volume

2. IMPROVE REACH RATE
   → Implement multi-touch strategy for {not_reached_total:,} "not reached" patients
   → Test different call times, days, and frequencies
   → Train staff on effective engagement techniques

3. EXPAND CALL COVERAGE
   → Systematically call all {not_called_total:,} uncalled patients
   → Achieve 95%+ coverage of eligible patient population
   → Eliminate "not called" category through systematic outreach

4. FOCUS ON HIGH-IMPACT SCREENING TYPES
   → Prioritize screenings with largest impact differential
   → Develop screening-specific messaging and materials
   → Target resources where intervention is most effective

VISUALIZATIONS GENERATED:
  ✓ Q4_Graph1_Priority_Matrix.png - Heatmap showing resource allocation priorities
  ✓ Q4_Graph2_Screening_Impact.png - Impact differential by screening type

OUTPUT LOCATION:
  {OUTPUT_DIR}
""")

print("=" * 70)
print("✅ Q4 ANALYSIS COMPLETE - ALL ANALYSES FINISHED")
print("=" * 70)

"""
KEY INSIGHTS - OPTIMIZATION STRATEGY
=====================================

Strategic Framework - Segment-Based Approach:
The data reveals a critical segmentation opportunity based on patient engagement levels
rather than a universal outreach strategy.

Three-Tier Population Structure:

TIER 1: High-Engagement (93.3% compliance)
- Current Status: {not_called_total:,} patients "not called"
- Characteristics: Complete screenings proactively without intervention
- Strategy: Minimal touch (automated reminders, annual wellness checks)
- Resource Allocation: 10% of call capacity
- Rationale: Already achieving excellent outcomes; don't over-serve

TIER 2: Active Support (~80% compliance)
- Current Status: Called patients (reached + not reached)
- Characteristics: Need intervention support but respond well
- Strategy: Sustained outreach with multi-touch approach
- Resource Allocation: 70% of call capacity
- Rationale: Maintaining 80% in challenging population is strong performance

TIER 3: High-Barrier (varies)
- Current Status: Subset of called patients with <50% compliance
- Characteristics: Multiple attempts unsuccessful, complex barriers
- Strategy: Intensive case management, barrier identification
- Resource Allocation: 20% of call capacity
- Rationale: Understand root causes to improve intervention

Optimization Priorities (Revised):

Priority 1: IMPROVE REACH RATE (Immediate)
- Target: 71.7% → 85%+ success rate
- Population: {not_reached_total:,} "not reached" patients
- Action: Multi-touch strategy (3-5 attempts at varied times/days)
- Impact: Convert more attempts into successful contacts

Priority 2: SEGMENT IDENTIFICATION (Short-term)
- Target: Classify all patients into engagement tiers
- Population: All 165 patients
- Action: Develop predictive model using:
  * Historical compliance patterns
  * Number of eligible screenings
  * Response to previous outreach
- Impact: Right-size intervention intensity per patient

Priority 3: EXPAND STRATEGICALLY (Medium-term)
- Target: {not_called_total:,} "not called" patients
- Action: Assess engagement level before calling
  * High-engagement indicators → Tier 1 (minimal touch)
  * Intervention-requiring indicators → Tier 2 (active support)
- Impact: Prevent over-calling engaged patients, focus resources appropriately

Priority 4: OPTIMIZE SCREENING-SPECIFIC APPROACH (Long-term)
- Target: Screening types with largest compliance gaps
- Action: Develop tailored messaging per screening type
  * BCS: Highest "not called" compliance (96.9%) - maintain
  * EED: Lowest "reached" compliance (73.7%) - investigate barriers
- Impact: Address screening-specific challenges

Expected Outcomes (6-Month Timeline):

Operational Metrics:
- Call coverage: 56% → 95% (appropriate patients)
- Reach success rate: 71.7% → 85%+
- Tier 2 compliance: Maintain ~80%
- Tier 1 compliance: Maintain >90% with minimal resources

Efficiency Gains:
- Resource reallocation from over-serving Tier 1 to supporting Tier 2
- Reduced cost per completed screening through segmentation
- Improved nurse satisfaction (focusing efforts where most impactful)

Quality Improvements:
- Patient satisfaction increase (right-touch approach)
- Reduced "nuisance calling" of already-compliant patients
- Better support for patients who genuinely need assistance

Critical Learning - Analytical Maturity:
This analysis demonstrates that "more outreach" is not always better. Identifying
self-sufficient patients and focusing resources on those who need support represents
more sophisticated population health management than universal intervention.

Implementation Roadmap:

Weeks 1-4:
- Implement multi-touch strategy for "not reached" patients
- Develop engagement tier classification criteria
- Train staff on segmented approach

Weeks 5-12:
- Roll out tiered intervention model
- Monitor compliance by tier
- Adjust resource allocation based on outcomes

Weeks 13-20:
- Systematically classify and contact "not called" patients
- Refine tier assignment based on observed patterns
- Begin screening-specific optimization

Weeks 21-26:
- Full implementation of three-tier model
- Continuous improvement based on feedback
- Prepare expansion to additional screening types

Next Steps:
- Present findings to executive team with tier-based framework
- Develop patient engagement scoring model
- Allocate resources based on three-tier structure
- Establish monitoring dashboard for tier-specific metrics
"""