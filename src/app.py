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
        background-color: #2c3e50;
        padding: 15px;
        border-radius: 5px;
        color: white;
        text-align: left;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .kpi-title {
        font-size: 16px;
        font-weight: bold;
        color: white;
        padding: 10px;
        border-radius: 5px 5px 0 0;
        margin: -20px -20px 15px -20px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #333;
    }
    .enrol-bg { background-color: #5DADE2; } /* Blue */
    .update-bg { background-color: #F1948A; } /* Red */
    .auth-bg { background-color: #58D68D; }   /* Green */
    .ekyc-bg { background-color: #F5B041; }   /* Orange */
</style>

<div class="main-header">
    <div style="font-size: 24px; font-weight: bold;">Welcome to AADHAAR Dashboard</div>
    <div style="font-size: 12px;">Unique Identification Authority of India</div>
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
        <div class="kpi-title enrol-bg">Enrolment</div>
        <div class="kpi-value">{df_enr['Enrolment_Count'].sum():,}</div>
        <div style="font-size: 12px; color: #777;">Total Enrolments</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title update-bg">Update</div>
        <div class="kpi-value">{df_upd['Count'].sum():,}</div>
        <div style="font-size: 12px; color: #777;">Total Updates</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title auth-bg">Authentication</div>
        <div class="kpi-value">90,096,849,046</div>
        <div style="font-size: 12px; color: #777;">Total Authentications (Mock)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title ekyc-bg">eKYC</div>
        <div class="kpi-value">14,774,500,494</div>
        <div style="font-size: 12px; color: #777;">eKYC Done (Mock)</div>
    </div>
    """, unsafe_allow_html=True)

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
if st.sidebar.button("Generate Smart Insight"):
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

# Tabs
tab_trends, tab1, tab2, tab3 = st.tabs(["📊 Trends View", "🚀 Migration Monitor", "📱 Inclusion Tracker", "🔍 Anomaly Detection"])

with tab_trends:
    st.header("National Trends (Executive View)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Aadhaar Generation Trend")
        
        # 1. Enrolment Combo Chart
        enr_trend = df_enr.groupby('Month')['Enrolment_Count'].sum().reset_index()
        enr_trend['Month'] = enr_trend['Month'].astype(str)
        enr_trend['Cumulative'] = enr_trend['Enrolment_Count'].cumsum()
        
        # Create Dual-Axis Plot
        fig_enr = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Bar Trace (Monthly)
        fig_enr.add_trace(
            go.Bar(x=enr_trend['Month'], y=enr_trend['Enrolment_Count'], name="Monthly Enrolment",
                   marker_color='#26C6DA', opacity=0.8), # Teal color
            secondary_y=False
        )
        
        # Line Trace (Cumulative/Trend)
        fig_enr.add_trace(
            go.Scatter(x=enr_trend['Month'], y=enr_trend['Cumulative'], name="Cumulative Trend",
                       line=dict(color='#FFCA28', width=3), mode='lines+markers'), # Yellow Line
            secondary_y=True
        )
        
        fig_enr.update_layout(title_text="", showlegend=True, height=350, margin=dict(t=10, b=0, l=0, r=0))
        fig_enr.update_yaxes(title_text="Monthly Count", secondary_y=False, showgrid=False)
        fig_enr.update_yaxes(title_text="Cumulative", secondary_y=True, showgrid=False)
        st.plotly_chart(fig_enr, width="stretch")
        
        st.subheader("Update Transaction Trend")
        
        # 2. Update Combo Chart
        upd_trend = df_upd.groupby('Month')['Count'].sum().reset_index()
        upd_trend['Month'] = upd_trend['Month'].astype(str)
        upd_trend['Cumulative'] = upd_trend['Count'].cumsum()
        
        fig_upd = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_upd.add_trace(
            go.Bar(x=upd_trend['Month'], y=upd_trend['Count'], name="Monthly Updates",
                   marker_color='#EF5350', opacity=0.8), # Red/Pink color
            secondary_y=False
        )
        
        fig_upd.add_trace(
            go.Scatter(x=upd_trend['Month'], y=upd_trend['Cumulative'], name="Cumulative Trend",
                       line=dict(color='#FFCA28', width=3), mode='lines+markers'), # Yellow Line
            secondary_y=True
        )
        
        fig_upd.update_layout(title_text="", showlegend=True, height=350, margin=dict(t=10, b=0, l=0, r=0))
        fig_upd.update_yaxes(title_text="Monthly Count", secondary_y=False, showgrid=False)
        fig_upd.update_yaxes(title_text="Cumulative", secondary_y=True, showgrid=False)
        st.plotly_chart(fig_upd, width="stretch")

    with col2:
        st.subheader("State Saturation Hierarchy")
        
        # Prepare data for Exploded Pie
        pie_data = df_sat.sort_values(by='Projected_Pop_2025', ascending=False)
        
        # Create a 'pull' list: 0.2 for the first item (largest)
        pull_config = [0.2] + [0.0] * (len(pie_data) - 1)
        
        # Custom Colors to match the reference (Yellow-Green, Blue, Orange, etc.)
        custom_colors = ['#A2D9CE', '#AED6F1', '#F9E79F', '#F5B7B1', '#D2B4DE', '#FAD7A0'] * 3
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_data['State'], 
            values=pie_data['Projected_Pop_2025'],
            pull=pull_config, 
            hole=0.0, 
            textinfo='percent+label',
            rotation=45, # Rotate to position the exploded slice nicely
            marker=dict(colors=px.colors.qualitative.Pastel, line=dict(color='#FFFFFF', width=2))
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05),
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_pie, width="stretch")

with tab1:
    st.header("Migration Velocity ($M_v$)")
    st.info("Tracking 'Address Updates' as a proxy for internal migration pressure.")
    
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
    st.header("Digital Gender Gap Index (DGGI)")
    st.info("Ratio of Female-to-Male Mobile Updates. A clearer path to 0.5 indicates parity.")
    
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
    st.header("Anomaly Detection & Forecasting")
    
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
