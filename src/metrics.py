import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np



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
