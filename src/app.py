import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_folium import st_folium
from data_loader import load_data, merge_for_map
from metrics import calculate_migration_velocity, calculate_dggi, detect_anomalies

# Page Config
st.set_page_config(page_title="Aadhaar-Drishti", layout="wide", page_icon="🇮🇳")

# Custom CSS for Dashboard Styling
st.markdown("""
<style>
    .main-header {
        background-color: #1E3D59; /* darker blue */
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: left;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-card {
        background-color: white;
        padding: 0px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        overflow: hidden; /* for header radius */
    }
    .kpi-title {
        font-size: 18px;
        font-weight: 600;
        color: white;
        padding: 15px;
        margin-bottom: 15px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .kpi-sub {
        font-size: 14px;
        color: #7f8c8d;
        padding-bottom: 20px;
    }
    .enrol-bg { background-color: #5DADE2; }
    .update-bg { background-color: #F1948A; }
    .auth-bg { background-color: #58D68D; }
    .ekyc-bg { background-color: #F5B041; }
    
    /* Chart Card Styling */
    .chart-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
</style>

<div class="main-header">
    <div>
        <div style="font-size: 28px; font-weight: bold;">Welcome to AADHAAR Dashboard</div>
        <div style="font-size: 14px; opacity: 0.9;">Unique Identification Authority of India | Government of India</div>
    </div>
    <div style="font-size: 40px;">🇮🇳</div> 
</div>
""", unsafe_allow_html=True)

# Load Data
with st.spinner("Loading aggregated Aadhaar datasets..."):
    df_enr, df_upd, df_sat, gdf = load_data()

# Custom KPI Cards Section
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



# AI Analyst Section
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Analyst")
if st.sidebar.button("Generate Smart Insight"):
    with st.sidebar.chat_message("assistant"):
        st.write("Analyzing patterns...")
        # ... (AI Logic matches previous)
        insight_text = []
        avg_sat = df_sat['Saturation_Percentage'].mean()
        if avg_sat > 100:
            insight_text.append(f"⚠️ **Action Req**: Saturation > 100% ({avg_sat:.1f}%). **Rec**: Initiate deduplication audit & verify floating population.")
        elif avg_sat > 90:
            insight_text.append(f"✅ **High Coverage**: ({avg_sat:.1f}%) achieved. **Rec**: Shift focus to biometric updates & mobile number linkage.")
            
        # 2. Gender Gap
        male_upd = df_upd[df_upd['Gender']=='Male']['Count'].sum()
        female_upd = df_upd[df_upd['Gender']=='Female']['Count'].sum()
        gap = abs(male_upd - female_upd) / (male_upd + female_upd)
        if gap > 0.2:
            insight_text.append(f"📉 **Gender Gap Alert**: High disparity ({gap:.1%}). **Rec**: Launch targeted 'Aadhaar for Her' camps in this district.")
        else:
            insight_text.append(f"⚖️ **Gender Parity**: Balanced access. **Rec**: Maintain current outreach levels.")
            
        # 3. Migration
        addr_upd = df_upd[df_upd['Update_Type']=='Address']['Count'].sum()
        if addr_upd > 5000: # Arbitrary threshold for mock data
            insight_text.append(f"🚀 **Migration Surge**: {addr_upd:,} address updates. **Rec**: Allocate temporary enrolment centers to manage inflow.")

# Tabs
tab_trends, tab1, tab2, tab3 = st.tabs(["📊 Trends View", "🚀 Migration Monitor", "📱 Inclusion Tracker", "🔍 Anomaly Detection"])

with tab_trends:
    # Use standard headers but we will wrap charts to look 'contained'
    # Streamlit doesn't support wrapping plots in arbitrary HTML divs easily, 
    # so we rely on Plotly's native white background we set below.
    
    col1, col2 = st.columns([2, 1])
    
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
        st.markdown("#### State Saturation Hierarchy")
        
        # Prepare data for Exploded Pie
        pie_data = df_sat.sort_values(by='Projected_Pop_2025', ascending=False)
        pull_config = [0.1] + [0.0] * (len(pie_data) - 1)
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_data['State'], 
            values=pie_data['Projected_Pop_2025'],
            pull=pull_config, 
            hole=0.0, 
            textinfo='percent+label',
            rotation=45, 
            marker=dict(colors=px.colors.qualitative.Pastel, line=dict(color='#FFFFFF', width=2))
        )])
        
        fig_pie.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            showlegend=True,
            legend=dict(orientation="v", y=0.5, x=1.1),
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_pie, width="stretch")

# Sidebar Controls
st.sidebar.header("Filter Controls")
selected_state = st.sidebar.selectbox("Select State", ["All"] + list(df_sat['State'].unique()))

# Filter logic
if selected_state != "All":
    df_enr = df_enr[df_enr['State'] == selected_state]
    df_upd = df_upd[df_upd['State'] == selected_state]
    df_sat = df_sat[df_sat['State'] == selected_state]
    gdf = gdf[gdf['state'] == selected_state]

# AI Analyst Section
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Analyst")
if st.sidebar.button("Generate Smart Insight", key="ai_analyst_btn"):
    with st.sidebar.chat_message("assistant"):
        st.write("Analyzing patterns...")
        
        # Logic-based "GenAI" for Hackathon (Deterministic but smart)
        insight_text = []
        
        # 1. Saturation Insight
        avg_sat = df_sat['Saturation_Percentage'].mean()
        if avg_sat > 100:
            insight_text.append(f"⚠️ **Anomaly Detected**: Saturation is at {avg_sat:.1f}%, indicating extensive floating population or potential duplication in this region.")
        elif avg_sat > 90:
            insight_text.append(f"✅ **High Saturation**: This region has achieved {avg_sat:.1f}% coverage, suggesting a shift to 'Update-Correction' phase is priority.")
            
        # 2. Gender Gap
        male_upd = df_upd[df_upd['Gender']=='Male']['Count'].sum()
        female_upd = df_upd[df_upd['Gender']=='Female']['Count'].sum()
        gap = abs(male_upd - female_upd) / (male_upd + female_upd)
        if gap > 0.2:
            insight_text.append(f"📉 **Gender Gap Alert**: High disparity ({gap:.1%}) in updates between genders. Targeted camps for women are recommended.")
        else:
            insight_text.append(f"⚖️ **Gender Parity**: Excellent balance in digital access between genders.")
            
        # 3. Migration
        addr_upd = df_upd[df_upd['Update_Type']=='Address']['Count'].sum()
        if addr_upd > 5000: # Arbitrary threshold for mock data
            insight_text.append(f"🚀 **High Migration Flow**: {addr_upd:,} address updates detected. Infrastructure planning required for new residents.")
            
        st.write(" ".join(insight_text))



with tab1:
    st.header("Migration Pressure & Infrastructure Planning")
    st.info("Policy Insight: High address updates often precede resource strain. Use $M_v$ to allocate new centers.")
    
    # Calculate Metric
    mv_df = calculate_migration_velocity(df_upd, df_sat)
    
    # Visualization: Map
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Geospatial Hotspots")
        # Merge for map
        map_df = merge_for_map(gdf, mv_df, 'Migration_Velocity')
        
        if not map_df.empty:
            m = folium.Map(location=[20, 78], zoom_start=5)
            folium.Choropleth(
                geo_data=map_df.__geo_interface__,
                name="choropleth",
                data=map_df,
                columns=["District", "Migration_Velocity"],
                key_on="feature.properties.district",
                fill_color="YlOrRd",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="Migration Velocity (Updates per 1k Pop)"
            ).add_to(m)
            st_folium(m, width=None, height=400, returned_objects=[], use_container_width=True)
        else:
            st.warning("No geospatial data available for the selected filters.")
            
    with col2:
        st.subheader("Top Districts by Inflow")
        top_districts = mv_df.sort_values(by='Migration_Velocity', ascending=False).head(10)
        st.dataframe(top_districts[['District', 'State', 'Migration_Velocity']].style.format({"Migration_Velocity": "{:.2f}"}))

with tab2:
    st.header("Digital Inclusion Targets (Gender Parity)")
    st.info("Policy Insight: Districts with < 0.4 Female Share require targeted enrolment camps.")
    
    dggi_df = calculate_dggi(df_upd, df_sat)
    
    # Visualization: Dumbbell or Bar chart
    # Here we show Female Share of Total Updates by District
    
    fig = px.scatter(dggi_df.sort_values(by='Female_Share'), 
                     x="Female_Share", y="District", color="Female_Share",
                     color_continuous_scale="RdBu",
                     title="Female Share of Mobile Updates (Proxy for Digital Autonomy)")
    
    # Add vertical line at 0.5 (Parity)
    fig.add_vline(x=0.5, line_dash="dash", annotation_text="Parity")
    
    st.plotly_chart(fig, width="stretch")

with tab3:
    st.header("System Integrity & Demand Forecasting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Anomalous Enrolment Centers")
        st.markdown("Detected using **Isolation Forest** on Rejection Rates.")
        
        anomalies = detect_anomalies(df_enr)
        
        if not anomalies.empty:
            fig = px.scatter(anomalies, x="Enrolment_Count", y="Rejection_Rate", 
                             color="Rejection_Rate", size="Enrolment_Count",
                             hover_name="District", title="Outliers: High Rejection Clusters")
            st.plotly_chart(fig)
            st.dataframe(anomalies[['Rejection_Rate', 'Enrolment_Count']].sort_values(by='Rejection_Rate', ascending=False))
        else:
            st.success("No significant anomalies detected in the current view.")
            
    with col2:
        st.subheader("📈 MBU Demand Forecast")
        st.markdown("Predicting Mandatory Biometric Updates (Age 5/15) for next quarter.")
        # Dummy forecast viz for hackathon prototype
        dates = pd.date_range(start="2025-01-01", periods=6, freq="ME")
        forecast_vals = [1200, 1350, 1100, 1600, 1800, 1750] # Seasonal spike
        forecast_df = pd.DataFrame({'Date': dates, 'Predicted_Updates': forecast_vals})
        
        fig = px.line(forecast_df, x='Date', y='Predicted_Updates', markers=True, title="Forecasted Demand")
        st.plotly_chart(fig)

# Footer
st.markdown("---")
st.caption("UIDAI Data Hackathon 2026 | Team Arya")
