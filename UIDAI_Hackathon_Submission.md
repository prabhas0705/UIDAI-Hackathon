# UIDAI Data Hackathon 2026 - Team Arya

## Unlocking Societal Trends in Aadhaar Enrolment and Updates

**Dashboard:** [uidai-insights.streamlit.app](https://uidai-insights.streamlit.app)
**GitHub:** [github.com/prabhas0705/UIDAI-Hackathon](https://github.com/prabhas0705/UIDAI-Hackathon)

---

## 1. Problem Statement and Approach

### 1.1 Problem Statement

Aadhaar, with over 1.4 billion enrolments, generates massive amounts of data on demographic updates, biometric captures, and enrolment patterns. This data, when analyzed effectively, can reveal **societal trends** that support:

- **Policy Planning**: Understanding population mobility and demographic shifts
- **Resource Allocation**: Predicting demand for Aadhaar services
- **Anomaly Detection**: Identifying unusual patterns requiring investigation

### 1.2 Key Hypotheses Explored

| # | Hypothesis | Rationale |
|---|------------|-----------|
| 1 | **Marriage-related updates spike during wedding seasons** | Women typically update name/address after marriage. Indian wedding seasons (Nov-Feb, Apr-May) should show demographic update spikes |
| 2 | **Natural disasters/migration cause regional update spikes** | Mass migration after floods, earthquakes, or industrial changes leads to sudden address update surges in specific districts |
| 3 | **Age-based enrollment follows lifecycle milestones** | MBU (Mandatory Biometric Update) at ages 5, 15, and adult transitions at age 18 create predictable demand patterns |

### 1.3 Analytical Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYTICAL FRAMEWORK                         │
├─────────────────────────────────────────────────────────────────┤
│  UNIVARIATE          BIVARIATE           TRIVARIATE            │
│  ─────────          ─────────           ──────────             │
│  • Monthly trends   • State × Updates   • Age × State × Time   │
│  • Age distribution • District velocity • Update type × Region │
│  • Update volumes   • Enrol vs Update     × Season             │
│                     • Seasonal patterns                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Datasets Used

### 2.1 Primary Datasets (Provided by UIDAI)

| Dataset | Records | Columns | Description |
|---------|---------|---------|-------------|
| **Aadhaar Enrolment** | 1,006,029 | 7 | New Aadhaar registrations by age group |
| **Demographic Updates** | 2,071,700 | 6 | Name, address, mobile, DOB updates |
| **Biometric Updates** | 1,861,108 | 6 | Fingerprint, iris, photo updates |

**Total Records Analyzed: ~4.9 Million**

### 2.2 Column Descriptions

#### Enrolment Dataset
```
date          : Date of enrolment (DD-MM-YYYY)
state         : State name
district      : District name
pincode       : 6-digit postal code
age_0_5       : Enrolments for ages 0-5 years
age_5_17      : Enrolments for ages 5-17 years
age_18_greater: Enrolments for ages 18+ years
```

#### Demographic Update Dataset
```
date          : Date of update (DD-MM-YYYY)
state         : State name
district      : District name
pincode       : 6-digit postal code
demo_age_5_17 : Demographic updates for ages 5-17
demo_age_17_  : Demographic updates for ages 17+
```

#### Biometric Update Dataset
```
date          : Date of update (DD-MM-YYYY)
state         : State name
district      : District name
pincode       : 6-digit postal code
bio_age_5_17  : Biometric updates for ages 5-17
bio_age_17_   : Biometric updates for ages 17+
```

### 2.3 Supplementary Data

| Data | Source | Purpose |
|------|--------|---------|
| India Districts GeoJSON | DataMeet/GitHub | Choropleth map visualization |
| India States GeoJSON | DataMeet/GitHub | State-level aggregation |

---

## 3. Methodology

### 3.1 Data Pipeline Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Raw CSV    │───►│   Pandas     │───►│   Metrics    │
│   Files      │    │   Loading    │    │   Engine     │
│  (12 files)  │    │   & Merge    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐    ┌──────────────┐
                    │   GeoJSON    │    │   Streamlit  │
                    │   Mapping    │    │   Dashboard  │
                    └──────────────┘    └──────────────┘
```

### 3.2 Data Cleaning & Preprocessing

```python
# 1. Loading and concatenating multiple CSV files
df_enr = pd.concat([pd.read_csv(f) for f in enrolment_files])
df_demo = pd.concat([pd.read_csv(f) for f in demographic_files])
df_bio = pd.concat([pd.read_csv(f) for f in biometric_files])

# 2. Handling missing values
df.fillna(0, inplace=True)

# 3. Creating derived columns
df_enr['Enrolment_Count'] = df_enr['age_0_5'] + df_enr['age_5_17'] + df_enr['age_18_greater']
df_demo['Count'] = df_demo['demo_age_5_17'] + df_demo['demo_age_17_']

# 4. Date parsing for temporal analysis
df['Date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
df['Month_Num'] = df['Date'].dt.month
df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')

# 5. Standardizing column names
df.rename(columns={'state': 'State', 'district': 'District'}, inplace=True)
```

### 3.3 Key Metrics Computed

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Update Intensity** | `(Total Updates / Total Enrolments) × 1000` | Maintenance load per district |
| **MoM Change %** | `((Current - Previous) / Previous) × 100` | Migration spike detection |
| **Daily Velocity** | `Total Updates / Days Active` | Update rate measurement |
| **MBU Demand** | Age-group weighted projections | Capacity planning |

### 3.4 Anomaly Detection Algorithm

```python
# Isolation Forest for outlier detection
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.05, random_state=42)
df['anomaly'] = model.fit_predict(df[['Enrolment_Count']])
# -1 indicates anomaly
```

---

## 4. Data Analysis and Visualisation

### 4.1 Tab 1: Overall Trends

**Visualizations:**
- Aadhaar Generation Trend (Bar + Cumulative Line)
- Update Transaction Trend (Bar + Cumulative Line)
- Update Type Distribution (Demographic vs Biometric Pie Chart)

**Key Finding:** Updates are 3.9x the volume of new enrolments, indicating a **mature ecosystem** in maintenance phase.

### 4.2 Tab 2: Seasonal Patterns (Marriage Hypothesis)

**Analysis:** Monthly update volumes color-coded by wedding season

```
SEASONAL CLASSIFICATION:
├── Wedding Season (Nov-Feb): Primary marriage period
├── Wedding Season (Apr-May): Secondary marriage period
├── School Admission (Jun): Child enrollment surge
└── Regular Period: Baseline comparison
```

**Visualization:**
- Monthly bar chart with seasonal color coding
- Deviation from average (% above/below mean)
- Demographic vs Biometric comparison by month

**Key Finding:** March shows **47.2% above average** updates, potentially indicating post-wedding season name changes.

### 4.3 Tab 3: Migration Detection

**Analysis:** District-level spike detection for potential migration events

**Metrics:**
- **Daily Update Velocity**: Updates per day per district
- **Month-over-Month Change %**: Spike detection threshold >100%
- **Geographic Clusters**: States with 90th percentile activity

**Visualization:**
- Top 20 Districts by Update Velocity (Bar Chart)
- Spike Detection Scatter Plot (MoM Change %)
- State Treemap (Update Distribution)

**Key Finding:** **1,045 potential migration events detected** (districts with >100% MoM increase)

### 4.4 Tab 4: Age-18 Milestone Tracking

**Analysis:** Lifecycle-based enrollment and update patterns

**Milestones Tracked:**
| Age | Event | Aadhaar Action |
|-----|-------|----------------|
| 0-5 | Birth | Initial enrollment |
| 5 | School entry | First MBU |
| 15 | Adolescence | Second MBU |
| 18 | Adulthood | Voter ID, college, employment |

**Visualization:**
- Update Rate by State (Bar Chart)
- Enrollment vs Updates Scatter
- MBU Demand Stacked Bar (Immediate/Short-term/Long-term)

**Key Finding:** Total projected MBU demand: **898,268 updates** across all states

### 4.5 Tab 5: Operational Intensity

**Analysis:** Updates per 1,000 enrollments by district

**Visualization:**
- India Choropleth Map (594 districts)
- Top Districts Table
- Priority Actions Panel

**Key Finding:** High-intensity districts indicate areas needing **mobile update van deployment**

### 4.6 Tab 6: Demographics

**Analysis:** Age distribution of enrollments

**Visualization:** Pie chart showing:
- 0-5 Years: Child enrollments
- 5-17 Years: School-age population
- 18+ Years: Adult population

### 4.7 Tab 7: System Integrity

**Analysis:** Anomaly detection using Isolation Forest

**Visualization:**
- Outlier Scatter Plot (Anomaly vs Normal)
- MBU Demand Forecast (6-month projection)

**Key Finding:** Districts flagged for audit due to deviation from state norms

### 4.8 Tab 8: Trivariate Analysis

**Analysis:** Age × Geography × Time combined analysis

**Visualizations:**
- State × Month Heatmap
- Enrollment-Update Correlation Scatter
- Age Group Trends Over Time
- Update Type Over Time

**Key Finding:** Correlation coefficient **0.936** indicates strong lifecycle-driven update patterns

---

## 5. Key Findings and Insights

### 5.1 Summary of Findings

| Finding | Evidence | Impact |
|---------|----------|--------|
| **Wedding Season Effect** | 47.2% spike in March updates | Schedule capacity increases Nov-Mar |
| **Migration Patterns** | 1,045 spike events detected | Early warning system for disaster response |
| **Age-18 Transition** | 898K projected MBU demand | Youth outreach programs needed |
| **Urban Hotspots** | Top districts have 3,435 daily velocity | Deploy mobile update centers |
| **Strong Lifecycle Correlation** | r=0.936 enrollment-update | Predictable demand forecasting |

### 5.2 Actionable Recommendations

1. **Capacity Planning**
   - Increase staffing during wedding seasons (Nov-Feb, Apr-May)
   - Pre-position resources in high-velocity districts

2. **Disaster Response**
   - Monitor MoM spike alerts for early migration detection
   - Coordinate with NDMA for affected area coverage

3. **Youth Outreach**
   - Partner with schools for age-5 MBU campaigns
   - College enrollment drives for age-18 updates

4. **Anomaly Investigation**
   - Audit districts with >2σ deviation from state mean
   - Investigate unusual enrollment volumes

### 5.3 Limitations

- **No Gender Data**: Cannot directly verify marriage-related hypothesis
- **No Update Type Breakdown**: Cannot distinguish name vs address changes
- **Historical Baseline**: Limited to 7 months of data (Mar-Nov 2025)

---

## 6. Technical Implementation

### 6.1 Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit 1.53 |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Folium |
| **ML/Analytics** | Scikit-learn (Isolation Forest) |
| **Geospatial** | GeoPandas |
| **Deployment** | Streamlit Cloud |

### 6.2 Repository Structure

```
UIDAI-Hackathon/
├── src/
│   ├── app.py           # Main Streamlit dashboard
│   ├── data_loader.py   # Data loading utilities
│   └── metrics.py       # Analysis functions
├── data/
│   ├── india_districts.geojson
│   └── india_states.geojson
├── api_data_aadhar_enrolment/
│   └── *.csv (3 files)
├── api_data_aadhar_demographic/
│   └── *.csv (5 files)
├── api_data_aadhar_biometric/
│   └── *.csv (4 files)
├── requirements.txt
└── README.md
```

### 6.3 Key Code Snippets

#### Seasonal Pattern Detection
```python
def get_seasonal_patterns(df_upd, df_enr):
    df = df_upd.copy()
    df['Month_Num'] = pd.to_datetime(df['Month'], format='%d-%m-%Y').dt.month

    monthly = df.groupby('Month_Num')['Count'].sum().reset_index()
    avg = monthly['Count'].mean()
    monthly['Deviation_Pct'] = ((monthly['Count'] - avg) / avg * 100).round(1)

    def tag_season(month):
        if month in [11, 12, 1, 2]: return 'Wedding Season (Nov-Feb)'
        elif month in [4, 5]: return 'Wedding Season (Apr-May)'
        elif month == 6: return 'School Admission (Jun)'
        else: return 'Regular Period'

    monthly['Season'] = monthly['Month_Num'].apply(tag_season)
    return monthly
```

#### Migration Spike Detection
```python
def detect_migration_spikes(df_upd):
    df = df_upd.copy()
    df['Date'] = pd.to_datetime(df['Month'], format='%d-%m-%Y')
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')

    district_monthly = df.groupby(['District', 'State', 'Year_Month'])['Count'].sum()
    district_monthly = district_monthly.reset_index().sort_values(['District', 'Year_Month'])

    district_monthly['Prev'] = district_monthly.groupby('District')['Count'].shift(1)
    district_monthly['MoM_Pct'] = ((district_monthly['Count'] - district_monthly['Prev'])
                                    / district_monthly['Prev'] * 100)
    district_monthly['Is_Spike'] = district_monthly['MoM_Pct'] > 100

    return district_monthly
```

#### Update Intensity Calculation
```python
def calculate_update_intensity(df_upd, df_enr):
    upd_agg = df_upd.groupby(['District', 'State'])['Count'].sum().reset_index()
    enr_agg = df_enr.groupby('District')['Enrolment_Count'].sum().reset_index()

    merged = upd_agg.merge(enr_agg, on='District', how='left')
    merged['Update_Intensity'] = (merged['Count'] / merged['Enrolment_Count']) * 1000

    return merged
```

---

## 7. Conclusion

This analysis demonstrates that Aadhaar data can reveal significant **societal trends** including:

1. **Seasonal patterns** correlating with marriage seasons
2. **Geographic mobility** detectable through update spikes
3. **Lifecycle transitions** predictable through age-based analysis

The insights can support UIDAI in:
- **Proactive capacity planning** based on seasonal demand
- **Early warning systems** for migration events
- **Targeted outreach** for age-milestone updates
- **Anomaly detection** for system integrity

---

## Team Arya

**UIDAI Data Hackathon 2026**

*Built with Streamlit, Pandas, Plotly, and GeoPandas*
