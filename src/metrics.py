import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

def calculate_migration_velocity(df_upd, df_sat):
    """
    Calculates Migration Velocity ($M_v$).
    M_v = (Address Updates / Projected Population) * 1000
    """
    # Filter for Address updates
    addr_upd = df_upd[df_upd['Update_Type'] == 'Address'].groupby(['District', 'State'])['Count'].sum().reset_index()
    addr_upd.rename(columns={'Count': 'Address_Updates'}, inplace=True)
    
    # Merge with population
    merged = addr_upd.merge(df_sat[['District', 'Projected_Pop_2025']], on='District', how='left')
    
    # Calculate M_v
    merged['Migration_Velocity'] = (merged['Address_Updates'] / merged['Projected_Pop_2025']) * 1000
    
    return merged

def calculate_dggi(df_upd, df_sat):
    """
    Calculates Digital Gender Gap Index (DGGI).
    Ratio of Female Mobile Updates per 100k Female Pop vs Male per 100k Male Pop.
    (Simplified here to just raw ratio of updates for hackathon demo)
    DGGI = (Female Mobile Updates / Total Female) / (Male Mobile Updates / Total Male)
    """
    # Filter Mobile Updates
    mob_upd = df_upd[df_upd['Update_Type'] == 'Mobile']
    
    pivot = mob_upd.groupby(['District', 'Gender'])['Count'].sum().unstack(fill_value=0).reset_index()
    
    if 'Female' not in pivot.columns:
        pivot['Female'] = 0
    if 'Male' not in pivot.columns:
        pivot['Male'] = 0
        
    # Simplified DGGI for visualization (Female Share of Total)
    pivot['Female_Share'] = pivot['Female'] / (pivot['Female'] + pivot['Male'])
    
    # DGGI: < 0.5 means gap against women.
    return pivot

def detect_anomalies(df_enr):
    """
    Uses Isolation Forest to detect anomalies in Enrolment Rejection Rates.
    """
    # Aggregate by District
    df_agg = df_enr.groupby('District').agg({
        'Enrolment_Count': 'sum',
        'Rejection_Count': 'sum'
    }).reset_index()
    
    df_agg['Rejection_Rate'] = df_agg['Rejection_Count'] / df_agg['Enrolment_Count']
    df_agg = df_agg.fillna(0)
    
    # Isolation Forest
    model = IsolationForest(contamination=0.1, random_state=42)
    df_agg['anomaly'] = model.fit_predict(df_agg[['Enrolment_Count', 'Rejection_Rate']])
    
    # -1 is anomaly
    anomalies = df_agg[df_agg['anomaly'] == -1]
    
    return anomalies
