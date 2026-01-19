import pandas as pd
import geopandas as gpd
import streamlit as st
import os

@st.cache_data
def load_data():
    """
    Loads Enrolment, Update, Saturation, and Geospatial data.
    """
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    enrolment_path = os.path.join(data_dir, 'enrolment_data.csv')
    update_path = os.path.join(data_dir, 'update_data.csv')
    saturation_path = os.path.join(data_dir, 'saturation_data.csv')
    geojson_path = os.path.join(data_dir, 'india_districts.geojson')
    
    # Load CSVs
    df_enr = pd.read_csv(enrolment_path)
    df_upd = pd.read_csv(update_path)
    df_sat = pd.read_csv(saturation_path)
    
    # Load GeoJSON
    gdf = gpd.read_file(geojson_path)
    
    return df_enr, df_upd, df_sat, gdf

def merge_for_map(gdf, df_metrics, metric_col):
    """
    Merges metric dataframe with GeoDataFrame for plotting.
    """
    # Ensure district names match or use ID
    # In our mock data, names match perfectly.
    merged = gdf.merge(df_metrics, left_on='district', right_on='District', how='left')
    return merged
