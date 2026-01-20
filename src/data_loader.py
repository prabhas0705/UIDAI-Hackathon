import pandas as pd
import geopandas as gpd
import streamlit as st
import os

@st.cache_data
def load_data():
    """
    Loads Enrolment, Demographic, and Biometric data from split CSVs.
    """
    import glob
    
    # Base Path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Load Enrolment Data
    enr_path = os.path.join(base_dir, 'api_data_aadhar_enrolment', '*.csv')
    enr_files = glob.glob(enr_path)
    if enr_files:
        df_enr = pd.concat((pd.read_csv(f) for f in enr_files), ignore_index=True)
        # Calculate Total Enrolment
        # Fill NaNs with 0 just in case
        df_enr.fillna(0, inplace=True)
        df_enr['Enrolment_Count'] = df_enr['age_0_5'] + df_enr['age_5_17'] + df_enr['age_18_greater']
        
        # Standardize columns for merging/plotting
        # Rename 'date' -> 'Month' or ensure format if needed. 
        # The CSV has 'date' like '09-03-2025'.
        # For uniformity with app logic, let's keep 'State' and 'District' proper case if needed.
        # Column names in CSV: 'state', 'district'. App uses 'State'.
        df_enr.rename(columns={'state': 'State', 'district': 'District', 'date': 'Month'}, inplace=True)
    else:
        st.error("No Enrolment Data Found!")
        df_enr = pd.DataFrame()

    # 2. Load Demographic Update Data
    demo_path = os.path.join(base_dir, 'api_data_aadhar_demographic', '*.csv')
    demo_files = glob.glob(demo_path)
    if demo_files:
        df_demo = pd.concat((pd.read_csv(f) for f in demo_files), ignore_index=True)
        df_demo.fillna(0, inplace=True)
        df_demo['Count'] = df_demo['demo_age_5_17'] + df_demo['demo_age_17_']
        df_demo.rename(columns={'state': 'State', 'district': 'District', 'date': 'Month'}, inplace=True)
        df_demo['Type'] = 'Demographic'
        # Preserve age columns for detailed analysis
        df_demo.rename(columns={'demo_age_5_17': 'Age_5_17', 'demo_age_17_': 'Age_17_Plus'}, inplace=True)
    else:
        df_demo = pd.DataFrame()

    # 3. Load Biometric Update Data
    bio_path = os.path.join(base_dir, 'api_data_aadhar_biometric', '*.csv')
    bio_files = glob.glob(bio_path)
    if bio_files:
        df_bio = pd.concat((pd.read_csv(f) for f in bio_files), ignore_index=True)
        df_bio.fillna(0, inplace=True)
        df_bio['Count'] = df_bio['bio_age_5_17'] + df_bio['bio_age_17_']
        df_bio.rename(columns={'state': 'State', 'district': 'District', 'date': 'Month'}, inplace=True)
        df_bio['Type'] = 'Biometric'
        # Preserve age columns for detailed analysis
        df_bio.rename(columns={'bio_age_5_17': 'Age_5_17', 'bio_age_17_': 'Age_17_Plus'}, inplace=True)
    else:
        df_bio = pd.DataFrame()

    # Combine Updates into one DataFrame (similar to original df_upd)
    df_upd = pd.concat([df_demo, df_bio], ignore_index=True)

    # 4. Load GeoJSON
    geojson_path = os.path.join(base_dir, 'data', 'india_districts.geojson')
    if os.path.exists(geojson_path):
        gdf = gpd.read_file(geojson_path)
    else:
        gdf = gpd.GeoDataFrame()
    
    return df_enr, df_upd, gdf

def merge_for_map(gdf, df_metrics, metric_col):
    """
    Merges metric dataframe with GeoDataFrame for plotting.
    """
    # Handle empty GeoDataFrame (no GeoJSON file)
    if gdf.empty or 'district' not in gdf.columns:
        return gpd.GeoDataFrame()

    # Ensure district names match or use ID
    # In our mock data, names match perfectly.
    merged = gdf.merge(df_metrics, left_on='district', right_on='District', how='left')
    return merged
