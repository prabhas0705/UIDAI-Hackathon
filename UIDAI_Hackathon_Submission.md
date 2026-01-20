# Unlocking Societal Trends in Aadhaar Data
## UIDAI Data Hackathon 2026 | Team Arya

**Dashboard:** [uidai-insights.streamlit.app](https://uidai-insights.streamlit.app)
**GitHub:** [github.com/prabhas0705/UIDAI-Hackathon](https://github.com/prabhas0705/UIDAI-Hackathon)

---

## 1. Problem Statement and Approach

### Problem
Aadhaar data contains signals of **societal trends** - marriage patterns, migration events, and lifecycle transitions - that can inform UIDAI's operational planning and resource allocation.

### Hypotheses Tested
| # | Hypothesis | Rationale |
|---|------------|-----------|
| 1 | Wedding seasons cause update spikes | Women update name/address post-marriage |
| 2 | Disasters trigger regional migration | Address updates surge in affected areas |
| 3 | Age milestones drive predictable demand | MBU at 5, 15; adult needs at 18 |

### Analytical Approach
- **Univariate:** Monthly trends, age distributions
- **Bivariate:** State × Updates, District × Velocity
- **Trivariate:** Age × Geography × Time heatmaps

---

## 2. Datasets Used

### Primary Datasets (Provided by UIDAI)

| Dataset | Records | Files |
|---------|---------|-------|
| Aadhaar Enrolment | 1,006,029 | 3 CSVs |
| Demographic Updates | 2,071,700 | 5 CSVs |
| Biometric Updates | 1,861,108 | 4 CSVs |
| **Total** | **4,938,837** | 12 CSVs |

### Column Descriptions

**Enrolment Dataset:**
| Column | Type | Description |
|--------|------|-------------|
| date | string | Enrolment date (DD-MM-YYYY) |
| state | string | State/UT name |
| district | string | District name |
| pincode | int | 6-digit postal code |
| age_0_5 | int | Enrolments for ages 0-5 |
| age_5_17 | int | Enrolments for ages 5-17 |
| age_18_greater | int | Enrolments for ages 18+ |

**Demographic Update Dataset:**
| Column | Type | Description |
|--------|------|-------------|
| date | string | Update date (DD-MM-YYYY) |
| state | string | State/UT name |
| district | string | District name |
| pincode | int | 6-digit postal code |
| demo_age_5_17 | int | Demographic updates for ages 5-17 |
| demo_age_17_ | int | Demographic updates for ages 17+ |

**Biometric Update Dataset:**
| Column | Type | Description |
|--------|------|-------------|
| date | string | Update date (DD-MM-YYYY) |
| state | string | State/UT name |
| district | string | District name |
| pincode | int | 6-digit postal code |
| bio_age_5_17 | int | Biometric updates for ages 5-17 |
| bio_age_17_ | int | Biometric updates for ages 17+ |

**Coverage:** 55 States/UTs, 1,097 Districts, Mar-Nov 2025

---

## 3. Methodology

### 3.1 Data Loading & Merging
```python
# Load multiple CSV files per dataset
import pandas as pd
import glob

enr_files = glob.glob('api_data_aadhar_enrolment/*.csv')
df_enr = pd.concat([pd.read_csv(f) for f in enr_files], ignore_index=True)

demo_files = glob.glob('api_data_aadhar_demographic/*.csv')
df_demo = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)

bio_files = glob.glob('api_data_aadhar_biometric/*.csv')
df_bio = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)
```

### 3.2 Data Cleaning & Preprocessing
```python
# Handle missing values
df_enr.fillna(0, inplace=True)
df_demo.fillna(0, inplace=True)
df_bio.fillna(0, inplace=True)

# Create derived columns
df_enr['Enrolment_Count'] = df_enr['age_0_5'] + df_enr['age_5_17'] + df_enr['age_18_greater']
df_demo['Count'] = df_demo['demo_age_5_17'] + df_demo['demo_age_17_']
df_bio['Count'] = df_bio['bio_age_5_17'] + df_bio['bio_age_17_']

# Standardize column names
df_enr.rename(columns={'state': 'State', 'district': 'District', 'date': 'Month'}, inplace=True)

# Combine demographic and biometric into unified update dataset
df_demo['Type'] = 'Demographic'
df_bio['Type'] = 'Biometric'
df_upd = pd.concat([df_demo, df_bio], ignore_index=True)
```

### 3.3 Date Transformations
```python
# Parse dates for temporal analysis
df['Date'] = pd.to_datetime(df['Month'], format='%d-%m-%Y', errors='coerce')
df['Month_Num'] = df['Date'].dt.month
df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')
```

### 3.4 Key Metrics Computed

| Metric | Formula | Purpose |
|--------|---------|---------|
| Update Intensity | `(Updates / Enrolments) × 1000` | District maintenance load |
| MoM Change % | `((Curr - Prev) / Prev) × 100` | Spike detection |
| Daily Velocity | `Updates / Days_Active` | Update rate |
| Anomaly Score | Isolation Forest | Outlier detection |

---

## 4. Data Analysis and Visualisation

### 4.1 Seasonal Pattern Analysis (Marriage Hypothesis)

**Method:** Tag months by wedding season, compare to baseline
```python
def tag_season(month):
    if month in [11, 12, 1, 2]: return 'Wedding Season (Nov-Feb)'
    elif month in [4, 5]: return 'Wedding Season (Apr-May)'
    elif month == 6: return 'School Admission (Jun)'
    else: return 'Regular Period'

monthly['Season'] = monthly['Month_Num'].apply(tag_season)
monthly['Deviation_Pct'] = ((monthly['Count'] - avg) / avg * 100)
```

**Finding:** March shows **+47.2%** above average updates
**Visualization:** Bar chart color-coded by season + deviation chart

---

### 4.2 Migration Spike Detection

**Method:** Month-over-Month change per district, flag >100% spikes
```python
def detect_migration_spikes(df_upd):
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')
    district_monthly = df.groupby(['District', 'State', 'Year_Month'])['Count'].sum()

    district_monthly['Prev_Count'] = district_monthly.groupby('District')['Count'].shift(1)
    district_monthly['MoM_Change_Pct'] = (
        (district_monthly['Count'] - district_monthly['Prev_Count'])
        / district_monthly['Prev_Count'] * 100
    )
    district_monthly['Is_Spike'] = district_monthly['MoM_Change_Pct'] > 100
    return district_monthly
```

**Finding:** **1,045 spike events** detected
**Visualization:** Scatter plot of spikes + treemap of state distribution

---

### 4.3 Age-18 Milestone Analysis

**Method:** MBU demand forecasting by age cohort
```python
def calculate_mbu_demand_forecast(df_enr):
    forecast = df_enr.groupby('State').agg({
        'age_0_5': 'sum', 'age_5_17': 'sum', 'age_18_greater': 'sum'
    })
    forecast['MBU_Immediate'] = forecast['age_0_5'] * 0.2   # Near age 5
    forecast['MBU_ShortTerm'] = forecast['age_5_17'] * 0.1  # Near age 15
    forecast['MBU_LongTerm'] = forecast['age_18_greater'] * 0.1
    return forecast
```

**Finding:** **898,268** projected MBU demand
**Visualization:** Stacked bar chart by state

---

### 4.4 Operational Intensity Map

**Method:** Merge with India districts GeoJSON for choropleth
```python
def calculate_update_intensity(df_upd, df_enr):
    upd_agg = df_upd.groupby(['District', 'State'])['Count'].sum()
    enr_agg = df_enr.groupby('District')['Enrolment_Count'].sum()
    merged = upd_agg.merge(enr_agg, on='District')
    merged['Update_Intensity'] = (merged['Count'] / merged['Enrolment_Count']) * 1000
    return merged
```

**Finding:** 619 districts mapped with intensity scores
**Visualization:** India choropleth map (Folium)

---

### 4.5 Anomaly Detection

**Method:** Isolation Forest algorithm
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.05, random_state=42)
df['anomaly'] = model.fit_predict(df[['Enrolment_Count']])
anomalies = df[df['anomaly'] == -1]  # -1 indicates outlier
```

**Finding:** Districts flagged for audit
**Visualization:** Scatter plot with anomaly markers

---

### 4.6 Trivariate Analysis

**Method:** State × Month heatmap + correlation analysis
```python
heatmap = df.groupby(['State', 'Month_Num'])['Count'].sum()
heatmap_pivot = heatmap.pivot(index='State', columns='Month_Num', values='Count')

correlation = df_enr['Enrolment_Count'].corr(df_upd['Count'])  # r = 0.936
```

**Finding:** Strong lifecycle correlation (r=0.936)
**Visualization:** Heatmap + scatter with trendline

---

## 5. Key Insights & Recommendations

| Finding | Recommendation |
|---------|----------------|
| March +47% spike | Increase capacity Nov-Mar (wedding season) |
| 1,045 migration spikes | Integrate with NDMA for early alerts |
| 898K MBU demand | School partnerships for age-5/15 drives |
| High-intensity districts | Deploy mobile update vans |

---

## 6. Code Repository

**Full code available at:** [github.com/prabhas0705/UIDAI-Hackathon](https://github.com/prabhas0705/UIDAI-Hackathon)

```
Repository Structure:
├── src/
│   ├── app.py           # Streamlit dashboard (main)
│   ├── data_loader.py   # Data loading utilities
│   └── metrics.py       # All analysis functions
├── data/
│   └── india_districts.geojson
├── api_data_aadhar_*/   # UIDAI datasets (12 CSV files)
└── requirements.txt
```

---

**Team Arya** | UIDAI Data Hackathon 2026
