# Unlocking Societal Trends in Aadhaar Data
## UIDAI Data Hackathon 2026 | Team Arya

**Live Dashboard:** [uidai-insights.streamlit.app](https://uidai-insights.streamlit.app)
**GitHub:** [github.com/prabhas0705/UIDAI-Hackathon](https://github.com/prabhas0705/UIDAI-Hackathon)

---

## Executive Summary

We analyzed **4.9 million Aadhaar records** to identify three societal trends:

| Trend | Finding | Actionable Insight |
|-------|---------|-------------------|
| **Marriage Patterns** | March shows 47% spike in updates | Increase capacity during wedding seasons |
| **Migration Events** | 1,045 districts with >100% monthly spikes | Early warning system for disaster response |
| **Age-18 Transitions** | 898K projected MBU demand | Youth outreach at schools/colleges |

---

## Data Analyzed

| Dataset | Records | Key Columns |
|---------|---------|-------------|
| Enrolment | 1.0M | age_0_5, age_5_17, age_18_greater |
| Demographic Updates | 2.1M | demo_age_5_17, demo_age_17_ |
| Biometric Updates | 1.9M | bio_age_5_17, bio_age_17_ |

**Coverage:** 55 States/UTs, 1,097 Districts, 7 months (Mar-Nov 2025)

---

## Key Analyses & Findings

### 1. Seasonal Patterns (Wedding Season Hypothesis)

**Method:** Monthly aggregation with seasonal tagging

```
Wedding Seasons: Nov-Feb (primary), Apr-May (secondary)
```

**Result:**
- March: **+47.2%** above average (post-wedding name changes)
- April-May: **-25%** below average
- Strong correlation with Indian wedding calendar

**Recommendation:** Pre-schedule 40% capacity increase for Nov-Mar

---

### 2. Migration Detection (Disaster/Event Response)

**Method:** Month-over-Month spike detection per district

```python
Spike Threshold: MoM Change > 100%
```

**Result:**
- **1,045 spike events** detected across districts
- Top velocity: 3,435 updates/day (urban centers)
- Geographic clustering in specific states

**Recommendation:** Integrate with NDMA for disaster-triggered alerts

---

### 3. Age-18 Lifecycle Milestone

**Method:** Age-group transition analysis + MBU demand forecasting

| Age Milestone | Projected Demand |
|---------------|------------------|
| Age 5 (MBU) | ~180K immediate |
| Age 15 (MBU) | ~90K short-term |
| Age 18+ (Adult) | ~630K long-term |

**Recommendation:** School partnerships for MBU campaigns

---

### 4. Operational Intensity Map

**Method:** Update Intensity = (Updates / Enrolments) × 1000

**Result:** 619 districts mapped with intensity scores

**Recommendation:** Deploy mobile vans to high-intensity districts

---

## Technical Approach

**Stack:** Python, Streamlit, Pandas, Plotly, Scikit-learn, GeoPandas

**Key Metrics:**
```
Update Intensity = (Total Updates / Enrolments) × 1000
MoM Spike = ((Current - Previous) / Previous) × 100
Anomaly Score = Isolation Forest (contamination=5%)
```

**Analysis Types:**
- Univariate: Monthly trends, age distribution
- Bivariate: State × Updates, District × Velocity
- Trivariate: Age × Geography × Time (Heatmap)

---

## Impact & Applicability

| Application | Benefit |
|-------------|---------|
| **Capacity Planning** | Predict seasonal demand surges |
| **Disaster Response** | Early migration detection |
| **Youth Outreach** | Targeted MBU campaigns |
| **Resource Allocation** | Data-driven van deployment |

---

## Limitations & Future Work

- No gender field (marriage hypothesis is indirect)
- No update-type breakdown (name vs address)
- Future: Integrate with marriage registry, NDMA data

---

## Dashboard Screenshots

The interactive dashboard includes 8 analysis tabs:
1. Overall Trends
2. Seasonal Patterns
3. Migration Detection
4. Age-18 Milestone
5. Operational Intensity (India Map)
6. Demographics
7. System Integrity (Anomaly Detection)
8. Trivariate Analysis

---

**Team Arya** | UIDAI Data Hackathon 2026

*Code available in GitHub repository*
