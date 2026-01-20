import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime


# =============================================================================
# EXISTING METRICS
# =============================================================================

def calculate_update_intensity(df_upd, df_enr):
    """
    Calculates Update Intensity.
    Intensity = (Total Updates / Total Enrolments) * 1000
    Higher intensity implies active maintenance of Aadhaar details.
    """
    # Aggregate Updates by District
    upd_agg = df_upd.groupby(['District', 'State'])['Count'].sum().reset_index()
    upd_agg.rename(columns={'Count': 'Total_Updates'}, inplace=True)
    
    # Aggregate Enrolment (Proxy for Population)
    enr_agg = df_enr.groupby(['District'])['Enrolment_Count'].sum().reset_index()
    
    # Merge
    merged = upd_agg.merge(enr_agg, on='District', how='left')
    
    # Handle missing enrolments (avoid div by zero)
    merged['Enrolment_Count'] = merged['Enrolment_Count'].replace(0, 1)
    
    # Calculate Intensity
    merged['Update_Intensity'] = (merged['Total_Updates'] / merged['Enrolment_Count']) * 1000
    
    return merged

def calculate_age_distribution(df_enr):
    """
    Calculates age distribution share.
    """
    total_0_5 = df_enr['age_0_5'].sum()
    total_5_17 = df_enr['age_5_17'].sum()
    total_18_plus = df_enr['age_18_greater'].sum()
    
    return {
        "0-5 Years": total_0_5,
        "5-17 Years": total_5_17,
        "18+ Years": total_18_plus
    }

def detect_anomalies(df_enr):
    """
    Uses Isolation Forest to detect anomalies in Enrolment Volume.
    Detects districts with unusually low or high enrolment activity.
    """
    # Aggregate by District
    df_agg = df_enr.groupby('District').agg({
        'Enrolment_Count': 'sum'
    }).reset_index()
    
    df_agg = df_agg.fillna(0)
    
    # Isolation Forest
    # We use a 2D array for fit (Sample, Feature). Here just 1 feature.
    if len(df_agg) > 5:
        model = IsolationForest(contamination=0.05, random_state=42)
        df_agg['anomaly'] = model.fit_predict(df_agg[['Enrolment_Count']])
        # -1 is anomaly
        anomalies = df_agg[df_agg['anomaly'] == -1]
    else:
        anomalies = pd.DataFrame()

    return anomalies


# =============================================================================
# NEW METRICS: SEASONAL PATTERN ANALYSIS
# =============================================================================

def get_seasonal_patterns(df_upd, df_enr):
    """
    Analyzes seasonal patterns in updates - wedding seasons, school admissions.
    Wedding Season: Nov-Feb, Apr-May (India)
    School Admission: Apr-Jun
    """
    # Parse month from date
    df_upd = df_upd.copy()
    df_upd['Month_Num'] = pd.to_datetime(df_upd['Month'], format='%d-%m-%Y', errors='coerce').dt.month

    # Aggregate by month
    monthly_updates = df_upd.groupby('Month_Num')['Count'].sum().reset_index()
    monthly_updates.columns = ['Month_Num', 'Total_Updates']

    # Calculate average
    avg_updates = monthly_updates['Total_Updates'].mean()
    monthly_updates['Deviation_Pct'] = ((monthly_updates['Total_Updates'] - avg_updates) / avg_updates * 100).round(1)

    # Tag seasons
    def tag_season(month):
        if month in [11, 12, 1, 2]:
            return 'Wedding Season (Nov-Feb)'
        elif month in [4, 5]:
            return 'Wedding Season (Apr-May)'
        elif month in [6]:
            return 'School Admission (Jun)'
        else:
            return 'Regular Period'

    monthly_updates['Season'] = monthly_updates['Month_Num'].apply(tag_season)

    # Month names
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    monthly_updates['Month_Name'] = monthly_updates['Month_Num'].map(month_names)

    return monthly_updates


def get_demographic_vs_biometric_seasonal(df_upd):
    """
    Compares demographic vs biometric updates by season.
    Hypothesis: Demographic updates spike during wedding season (name/address changes).
    """
    df = df_upd.copy()
    df['Month_Num'] = pd.to_datetime(df['Month'], format='%d-%m-%Y', errors='coerce').dt.month

    seasonal_type = df.groupby(['Month_Num', 'Type'])['Count'].sum().reset_index()

    return seasonal_type


# =============================================================================
# NEW METRICS: MIGRATION/DISASTER SPIKE DETECTION
# =============================================================================

def detect_migration_spikes(df_upd):
    """
    Detects unusual spikes in updates by district - potential migration indicators.
    Uses month-over-month change detection.
    """
    df = df_upd.copy()
    df['Date'] = pd.to_datetime(df['Month'], format='%d-%m-%Y', errors='coerce')
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')  # String format for JSON serialization

    # Aggregate by district and month
    district_monthly = df.groupby(['District', 'State', 'Year_Month'])['Count'].sum().reset_index()

    # Calculate month-over-month change per district
    district_monthly = district_monthly.sort_values(['District', 'Year_Month'])
    district_monthly['Prev_Count'] = district_monthly.groupby('District')['Count'].shift(1)
    district_monthly['MoM_Change'] = district_monthly['Count'] - district_monthly['Prev_Count']
    district_monthly['MoM_Change_Pct'] = (district_monthly['MoM_Change'] / district_monthly['Prev_Count'] * 100).round(1)

    # Flag significant spikes (>100% increase)
    district_monthly['Is_Spike'] = district_monthly['MoM_Change_Pct'] > 100

    return district_monthly


def get_district_update_velocity(df_upd):
    """
    Calculates update velocity (rate of change) by district.
    High velocity indicates potential migration or event-driven updates.
    """
    df = df_upd.copy()
    df['Date'] = pd.to_datetime(df['Month'], format='%d-%m-%Y', errors='coerce')

    # Get date range per district
    velocity = df.groupby(['District', 'State']).agg({
        'Count': 'sum',
        'Date': ['min', 'max']
    }).reset_index()
    velocity.columns = ['District', 'State', 'Total_Updates', 'First_Date', 'Last_Date']

    # Calculate days active
    velocity['Days_Active'] = (velocity['Last_Date'] - velocity['First_Date']).dt.days + 1
    velocity['Daily_Velocity'] = (velocity['Total_Updates'] / velocity['Days_Active']).round(2)

    # Rank by velocity
    velocity['Velocity_Rank'] = velocity['Daily_Velocity'].rank(ascending=False, method='dense')

    return velocity


def detect_geographic_clusters(df_upd, threshold_percentile=90):
    """
    Identifies geographic clusters with unusually high update activity.
    Could indicate mass migration events or disaster recovery.
    """
    df = df_upd.copy()

    # State-level aggregation
    state_updates = df.groupby('State')['Count'].sum().reset_index()
    state_updates.columns = ['State', 'Total_Updates']

    # Calculate threshold
    threshold = state_updates['Total_Updates'].quantile(threshold_percentile / 100)
    state_updates['Is_High_Activity'] = state_updates['Total_Updates'] > threshold

    # District-level within high-activity states
    high_states = state_updates[state_updates['Is_High_Activity']]['State'].tolist()
    district_in_high = df[df['State'].isin(high_states)].groupby(['State', 'District'])['Count'].sum().reset_index()

    return state_updates, district_in_high


# =============================================================================
# NEW METRICS: AGE-18 MILESTONE TRACKING
# =============================================================================

def analyze_age_transitions(df_enr, df_upd):
    """
    Analyzes transition patterns from enrollment to updates by age group.
    Key insight: Age 17+ updates should correlate with age 5-17 enrollments from years prior.
    """
    # Enrollment by age group and state
    enr_by_age = df_enr.groupby('State').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'Enrolment_Count': 'sum'
    }).reset_index()

    # Updates by age group (17+ as proxy for 18+)
    upd_demo = df_upd[df_upd['Type'] == 'Demographic'].copy()
    upd_bio = df_upd[df_upd['Type'] == 'Biometric'].copy()

    # Demographic updates by state
    if 'demo_age_5_17' in df_upd.columns:
        demo_age = df_upd.groupby('State').agg({
            'Count': 'sum'
        }).reset_index()
    else:
        demo_age = df_upd[df_upd['Type'] == 'Demographic'].groupby('State')['Count'].sum().reset_index()

    # Merge for transition analysis
    transition = enr_by_age.merge(demo_age, on='State', how='left', suffixes=('', '_upd'))
    transition['Count'] = transition['Count'].fillna(0)

    # Calculate update rate (updates per enrollment)
    transition['Update_Rate'] = (transition['Count'] / transition['Enrolment_Count'] * 100).round(2)

    # Age 18 specific: ratio of 18+ enrollments to total
    transition['Adult_Enrollment_Share'] = (transition['age_18_greater'] / transition['Enrolment_Count'] * 100).round(2)

    return transition


def get_age_group_update_patterns(df_upd):
    """
    Breaks down update patterns by age group over time.
    Identifies when 17+ updates spike (potential age-18 milestone updates).
    """
    df = df_upd.copy()
    df['Date'] = pd.to_datetime(df['Month'], format='%d-%m-%Y', errors='coerce')
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')  # String format for JSON serialization

    # We need to get the original age columns before aggregation
    # For now, work with Type as proxy
    age_pattern = df.groupby(['Year_Month', 'Type'])['Count'].sum().reset_index()

    return age_pattern


def calculate_mbu_demand_forecast(df_enr):
    """
    Forecasts Mandatory Biometric Update (MBU) demand based on enrollment age distribution.
    - Age 0-5 enrolled → MBU needed at age 5 (in 0-5 years)
    - Age 5-17 enrolled → MBU needed at age 15 (in 0-10 years)
    - Adult first-time enrollees need update at 10-year intervals
    """
    forecast = df_enr.groupby('State').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()

    # Immediate MBU demand (0-5 approaching age 5)
    forecast['MBU_Immediate'] = (forecast['age_0_5'] * 0.2).round(0)  # ~20% near age 5

    # Short-term MBU demand (5-17 approaching age 15)
    forecast['MBU_ShortTerm'] = (forecast['age_5_17'] * 0.1).round(0)  # ~10% near age 15

    # Long-term adult updates (10-year cycle)
    forecast['MBU_LongTerm'] = (forecast['age_18_greater'] * 0.1).round(0)

    # Total projected demand
    forecast['Total_MBU_Demand'] = forecast['MBU_Immediate'] + forecast['MBU_ShortTerm'] + forecast['MBU_LongTerm']

    return forecast


# =============================================================================
# NEW METRICS: TRIVARIATE ANALYSIS (Age × Geography × Time)
# =============================================================================

def trivariate_analysis(df_enr, df_upd):
    """
    Combines Age, Geography, and Time for multi-dimensional analysis.
    Returns data suitable for 3D visualization or heatmaps.
    """
    # Enrollment: State × Month × Age Groups
    df_enr_copy = df_enr.copy()
    df_enr_copy['Date'] = pd.to_datetime(df_enr_copy['Month'], format='%d-%m-%Y', errors='coerce')
    df_enr_copy['Year_Month'] = df_enr_copy['Date'].dt.strftime('%Y-%m')  # String format

    trivar_enr = df_enr_copy.groupby(['State', 'Year_Month']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'Enrolment_Count': 'sum'
    }).reset_index()

    # Updates: State × Month × Type
    df_upd_copy = df_upd.copy()
    df_upd_copy['Date'] = pd.to_datetime(df_upd_copy['Month'], format='%d-%m-%Y', errors='coerce')
    df_upd_copy['Year_Month'] = df_upd_copy['Date'].dt.strftime('%Y-%m')  # String format

    trivar_upd = df_upd_copy.groupby(['State', 'Year_Month', 'Type'])['Count'].sum().reset_index()

    return trivar_enr, trivar_upd


def get_state_month_heatmap_data(df_upd):
    """
    Prepares data for State × Month heatmap visualization.
    Useful for identifying regional seasonal patterns.
    """
    df = df_upd.copy()
    df['Date'] = pd.to_datetime(df['Month'], format='%d-%m-%Y', errors='coerce')
    df['Month_Num'] = df['Date'].dt.month

    heatmap_data = df.groupby(['State', 'Month_Num'])['Count'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='State', columns='Month_Num', values='Count').fillna(0)

    return heatmap_pivot


def get_enrollment_update_correlation(df_enr, df_upd):
    """
    Calculates correlation between enrollment patterns and update patterns.
    High correlation might indicate systematic lifecycle updates.
    Low correlation might indicate event-driven updates (migration, disasters).
    """
    # Aggregate by state
    enr_state = df_enr.groupby('State')['Enrolment_Count'].sum().reset_index()
    upd_state = df_upd.groupby('State')['Count'].sum().reset_index()

    merged = enr_state.merge(upd_state, on='State', how='outer').fillna(0)
    merged.columns = ['State', 'Enrollments', 'Updates']

    # Calculate ratio
    merged['Update_to_Enrollment_Ratio'] = (merged['Updates'] / merged['Enrollments']).round(3)

    # Correlation coefficient
    correlation = merged['Enrollments'].corr(merged['Updates'])

    return merged, correlation
