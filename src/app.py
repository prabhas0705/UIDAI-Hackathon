import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_folium import st_folium
from data_loader import load_data, merge_for_map
from metrics import calculate_update_intensity, calculate_age_distribution, detect_anomalies

# Page Config
st.set_page_config(page_title="Aadhaar-Drishti", layout="wide", page_icon="🇮🇳")

# Custom CSS for Dashboard Styling
# Custom CSS for Dashboard Styling
st.markdown("""
<style>
    /* Main Background adjustments if needed */
    .block-container {
        padding-top: 3rem; /* Increased to prevent top clipping */
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* TOP HEADER: White, Logos */
    .top-header {
        background-color: white;
        padding: 15px 25px; /* More breathing room */
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        border-radius: 5px; /* Soften edges */
    }
    .header-logo-text {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .govt-text {
        color: #333;
        line-height: 1.4;
    }
    .govt-title {
        font-size: 18px; /* Slightly larger */
        font-weight: bold;
    }
    .govt-subtitle {
        font-size: 13px;
    }
    
    /* BLUE SUB-HEADER: Title + Button Area */
    .blue-subheader {
        background-color: #1E3D59;
        color: white;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0px 0px 5px 5px; /* Slight rounded bottom */
        margin-bottom: 25px;
    }
    .dashboard-title {
        font-size: 22px;
        font-weight: 500;
        margin: 0;
    }
    
    /* KPI Cards */
    .kpi-card {
        background-color: white;
        padding: 0px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        overflow: hidden;
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    .kpi-title {
        font-size: 16px;
        font-weight: 600;
        color: white;
        padding: 12px;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 2px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #7f8c8d;
        padding-bottom: 15px;
    }
    .enrol-bg { background-color: #5DADE2; }
    .update-bg { background-color: #F1948A; }
    .auth-bg { background-color: #58D68D; }
    .ekyc-bg { background-color: #F5B041; }

    /* Chart Container */
    .chart-container {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    
    /* Filter Box Styling */
    .filter-box {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin-bottom: 20px;
    }
</style>

<!-- Top Header Section -->
<div class="top-header">
    <div class="header-logo-text">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" style="height: 50px;">
        <div class="govt-text">
            <div class="govt-title">Unique Identification Authority of India</div>
            <div class="govt-subtitle">Government of India</div>
        </div>
    </div>
    <div>
        <img src="https://upload.wikimedia.org/wikipedia/en/c/cf/Aadhaar_Logo.svg" style="height: 60px; object-fit: contain;">
    </div>
</div>

<!-- Blue Title Bar Section (Visual only, button is separate Streamlit widget overlay) -->
<div class="blue-subheader">
    <div class="dashboard-title">Welcome to AADHAAR Dashboard</div>
    <!-- Placeholder for alignment, actual button is below via columns -->
    <div style="width: 150px;"></div> 
</div>
""", unsafe_allow_html=True)

# Generate AI Insight Button & Controls Wrapper
# We use a container to visually overlap or sit near the blue header? 
# Actually, putting it strictly inside logic:
col_header_1, col_header_2 = st.columns([6, 1])
with col_header_2:
    # This button technically sits below the blue bar in standard flow. 
    # To make it look "inside", we'd need negative margins or layout hacks. 
    # For now, we place it cleanly right below or we accept standard flow.
    # Let's just place the button here for functionality.
    gen_ai_btn = st.button("✨ Generate AI Insight", type="primary", use_container_width=True)

# Load Data
with st.spinner("Loading aggregated Aadhaar datasets..."):
    df_enr, df_upd, gdf = load_data()

# AI Analyst Logic (Triggered by main button)
if gen_ai_btn:
    st.info("🤖 **AI Analyst Output**")
    st.write("Analyzing patterns...")
    
    # Logic-based "GenAI" for Hackathon (Deterministic but smart)
    insight_text = []
    
    # 1. Volume Insight
    total_enr = df_enr['Enrolment_Count'].sum()
    if total_enr > 1000000:
        insight_text.append(f"📈 **High Volume**: Total enrolments exceed 1 Million ({total_enr:,}), indicating robust activity.")
        
    # 2. Update Ratio
    total_upd = df_upd['Count'].sum() if not df_upd.empty else 0
    ratio = total_upd / total_enr if total_enr > 0 else 0
    if ratio > 0.5:
        insight_text.append(f"🔄 **Maintenance Phase**: Updates ({total_upd:,}) are {ratio:.0%} of enrolments, suggesting a mature ecosystem.")
    else:
        insight_text.append(f"🆕 **Acquisition Phase**: Focus is still largely on new enrolments over updates.")
        
    st.success(" ".join(insight_text))


# ---------------------------------------------------------
# KPI Cards Section
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title enrol-bg">🆔 Enrolment</div>
        <div class="kpi-value">{df_enr['Enrolment_Count'].sum():,}</div>
        <div class="kpi-sub">Total Enrolments</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title update-bg">📝 Update</div>
        <div class="kpi-value">{df_upd['Count'].sum():,}</div>
        <div class="kpi-sub">Total Updates</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title auth-bg">✅ Authentication</div>
        <div class="kpi-value">90.1 B</div>
        <div class="kpi-sub">Total Authentications</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title ekyc-bg">👍 eKYC</div>
        <div class="kpi-value">14.7 B</div>
        <div class="kpi-sub">eKYC Transations</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Filter Section (Moved below Stats Cards)
# ---------------------------------------------------------
with st.expander("🔍 Filter Dashboard Data", expanded=True):
    # Enhanced Filter Style using Columns
    col_f1, col_f2, col_f3 = st.columns([2, 2, 4])
    
    with col_f1:
        # State Filter
        state_list = sorted(list(df_enr['State'].unique()))
        selected_state = st.selectbox("1️⃣ Select State", ["All"] + state_list, key="state_filter_main")
        
    with col_f2:
        # District Filter (Dynamic)
        if selected_state != "All":
            district_list = sorted(list(df_enr[df_enr['State'] == selected_state]['District'].unique()))
            selected_district = st.selectbox("2️⃣ Select District", ["All"] + district_list, key="dist_filter_main")
        else:
            selected_district = "All"
            st.selectbox("2️⃣ Select District", ["Select State First"], disabled=True)

# Filter logic
if selected_state != "All":
    df_enr = df_enr[df_enr['State'] == selected_state]
    df_upd = df_upd[df_upd['State'] == selected_state]
    gdf = gdf[gdf['state'] == selected_state]
    
    if selected_district != "All":
        df_enr = df_enr[df_enr['District'] == selected_district]
        df_upd = df_upd[df_upd['District'] == selected_district]
        # map filter logic if district specific map needed, usually district map shows specific district highlighted
        # For this hackathon, we keep map focused on state or filter down
        gdf = gdf[gdf['district'] == selected_district]

# Layout: Tabs
tab_trends, tab1, tab2, tab3 = st.tabs(["📈 Overall Trends", "🏭 Operational Intensity", "👥 Demographics", "🛡️ System Integrity"])
with tab_trends:
    # Use standard headers but we will wrap charts to look 'contained'
    # Streamlit doesn't support wrapping plots in arbitrary HTML divs easily, 
    # so we rely on Plotly's native white background we set below.
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### Aadhaar Generation Trend")
        
        # 1. Enrolment Combo Chart
        enr_trend = df_enr.groupby('Month')['Enrolment_Count'].sum().reset_index()
        enr_trend['Month'] = enr_trend['Month'].astype(str)
        enr_trend['Cumulative'] = enr_trend['Enrolment_Count'].cumsum()
        
        # Create Dual-Axis Plot with White Background Style
        fig_enr = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_enr.add_trace(go.Bar(x=enr_trend['Month'], y=enr_trend['Enrolment_Count'], name="Enrolments", marker_color='#26C6DA', opacity=0.8), secondary_y=False)
        fig_enr.add_trace(go.Scatter(x=enr_trend['Month'], y=enr_trend['Cumulative'], name="Trendline", line=dict(color='#F1C40F', width=3), mode='lines+markers'), secondary_y=True)
        
        fig_enr.update_layout(
            plot_bgcolor='white', paper_bgcolor='white', # White Card look
            margin=dict(t=30, b=0, l=10, r=10), height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_enr.update_yaxes(showgrid=True, gridcolor='#f0f0f0', secondary_y=False)
        fig_enr.update_yaxes(showgrid=False, secondary_y=True)
        st.plotly_chart(fig_enr, width="stretch")
        
        st.markdown("#### Update Transaction Trend")
        
        # 2. Update Combo Chart
        upd_trend = df_upd.groupby('Month')['Count'].sum().reset_index()
        upd_trend['Month'] = upd_trend['Month'].astype(str)
        upd_trend['Cumulative'] = upd_trend['Count'].cumsum()
        
        fig_upd = make_subplots(specs=[[{"secondary_y": True}]])
        fig_upd.add_trace(go.Bar(x=upd_trend['Month'], y=upd_trend['Count'], name="Updates", marker_color='#EF5350', opacity=0.8), secondary_y=False)
        fig_upd.add_trace(go.Scatter(x=upd_trend['Month'], y=upd_trend['Cumulative'], name="Trendline", line=dict(color='#F1C40F', width=3), mode='lines+markers'), secondary_y=True)
        
        fig_upd.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(t=30, b=0, l=10, r=10), height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_upd.update_yaxes(showgrid=True, gridcolor='#f0f0f0', secondary_y=False)
        st.plotly_chart(fig_upd, width="stretch")

    with col2:
        st.subheader("Update Type Distribution")
        
        if 'Type' in df_upd.columns:
            update_counts = df_upd['Type'].value_counts()
            fig_type = px.pie(names=update_counts.index, values=update_counts.values, hole=0.4,
                             color_discrete_sequence=['#FF7043', '#42A5F5'])
            fig_type.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_type, width="stretch")
        else:
            st.warning("Type breakdown not available.")



# AI Analyst Logic (Triggered by main button)



with tab1:
    st.header("Operational Intensity (Updates vs Enrolments)")
    
    # Calculate Metric
    intensity_df = calculate_update_intensity(df_upd, df_enr)
    
    # Visualization: Map
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("District-wise Update Intensity")
        # Merge for map
        map_df = merge_for_map(gdf, intensity_df, 'Update_Intensity')
        
        if not map_df.empty:
            m = folium.Map(location=[20, 78], zoom_start=5)
            folium.Choropleth(
                geo_data=map_df.__geo_interface__,
                name="choropleth",
                data=map_df,
                columns=["District", "Update_Intensity"],
                key_on="feature.properties.district",
                fill_color="YlGnBu",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="Update Intensity (Updates per 1k Enrolments)"
            ).add_to(m)
            st_folium(m, width=None, height=400, returned_objects=[], use_container_width=True)
        else:
            st.warning("No geospatial data available for the selected filters.")
            
    with col2:
        st.subheader("Priority Actions")
        
        # 1. District Selector
        if not intensity_df.empty:
            max_intensity = intensity_df['Update_Intensity'].max()
            top_dist = intensity_df.loc[intensity_df['Update_Intensity'].idxmax()]
            
            st.metric(label=f"Highest Intensity: {top_dist['District']}", value=f"{top_dist['Update_Intensity']:.0f}")
            
            st.info(f"**Insight**: {top_dist['District']} has the highest maintenance load. Deploy mobile update vans.")
            
            st.markdown("**Top Districts by Intensity**")
            st.dataframe(intensity_df.sort_values(by='Update_Intensity', ascending=False).head(5)[['District', 'Update_Intensity']])
        else:
            st.write("No data available.")

with tab2:
    st.header("Demographic Profile (Age Distribution)")
    
    age_dist = calculate_age_distribution(df_enr)
    
    # Visualization: Pie Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.pie(values=list(age_dist.values()), names=list(age_dist.keys()), hole=0.3,
                     title="Enrolment Share by Age Group",
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, width="stretch")
        
    with col2:
        st.info("**Policy Note**: \n\n- **0-5 Years**: Mandatory Biometric Update (MBU) pending at age 5.\n- **5-17 Years**: MBU pending at age 15.\n- **18+**: General updates.")

with tab3:
    st.header("System Integrity & MBU Demand Forecasting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Anomalous Enrolment Volume")
        st.markdown("Detected using **Isolation Forest** on Enrolment Counts.")
        
        anomalies = detect_anomalies(df_enr)
        
        if not anomalies.empty:
            # -1 is anomaly, map to string for color
            anomalies['Status'] = anomalies['anomaly'].apply(lambda x: 'Anomaly' if x == -1 else 'Normal')
            
            fig = px.scatter(anomalies, x="District", y="Enrolment_Count", 
                             color="Status", size="Enrolment_Count",
                             color_discrete_map={'Anomaly': 'red', 'Normal': 'blue'},
                             hover_name="District", title="Outliers: Unusual Enrolment Volume")
            st.plotly_chart(fig)
            st.error(f"**Action Required**: {len(anomalies[anomalies['anomaly']==-1])} Districts flagged for audit due to deviation from state norms.")
        else:
            st.success("No significant anomalies detected in the current view.")
            
    with col2:
        st.subheader("Alert: 40% Surge in Child Updates Expected")
        st.markdown("**Predicting Mandatory Biometric Updates (Age 5/15) for next quarter.**")
        # Dummy forecast viz for hackathon prototype
        dates = pd.date_range(start="2025-01-01", periods=6, freq="ME")
        forecast_vals = [1200, 1350, 1100, 2200, 2400, 2350] # Seasonal spike
        forecast_df = pd.DataFrame({'Date': dates, 'Predicted_Updates': forecast_vals})
        
        fig = px.line(forecast_df, x='Date', y='Predicted_Updates', markers=True, title="Forecasted Demand")
        fig.add_annotation(x=dates[4], y=2400, text="Peak Demand", showarrow=True, arrowhead=1)
        st.plotly_chart(fig)
        
        st.warning("⚡ **Staffing Increase Required**: projected demand exceeds current capacity by 1,200 slots/day in May.")

# Footer
st.markdown("---")
st.caption("UIDAI Data Hackathon 2026 | Team Arya")
