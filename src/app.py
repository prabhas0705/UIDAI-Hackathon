import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import random
import plotly.graph_objects as go
from streamlit_folium import st_folium
from data_loader import load_data, merge_for_map
from metrics import calculate_migration_velocity, calculate_dggi, detect_anomalies

# Page Config
st.set_page_config(page_title="Aadhaar-Drishti", layout="wide", page_icon="🇮🇳")

# Title and Context
st.title("🇮🇳 Aadhaar-Drishti: Strategic Intelligence Dashboard")
st.markdown("""
> **Theme**: Unlocking Societal Trends in Aadhaar Enrolment and Updates  
> **Mission**: Transforming administrative metadata into actionable governance insights.
""")

# Load Data
with st.spinner("Loading aggregated Aadhaar datasets..."):
    df_enr, df_upd, df_sat, gdf = load_data()

# KPI Section
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total Enrolments (2023-25)", f"{df_enr['Enrolment_Count'].sum():,}")
with kpi2:
    st.metric("Total Updates", f"{df_upd['Count'].sum():,}")
with kpi3:
    st.metric("Avg. Saturation", f"{df_sat['Saturation_Percentage'].mean():.1f}%")
with kpi4:
    st.metric("Avg. Rejection Rate", f"{(df_enr['Rejection_Count'].sum()/df_enr['Enrolment_Count'].sum())*100:.2f}%")
st.markdown("---")

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
        st.subheader("Aadhaar Generation Trend (2023-2025)")
        # Group by Month for Bar Chart
        enr_trend = df_enr.groupby('Month')['Enrolment_Count'].sum().reset_index()
        enr_trend['Month'] = enr_trend['Month'].astype(str)
        fig_enr = px.bar(enr_trend, x='Month', y='Enrolment_Count', 
                         color_discrete_sequence=['#0083B8'], text_auto='.2s')
        st.plotly_chart(fig_enr, width="stretch")
        
        st.subheader("Update Transaction Trend")
        upd_trend = df_upd.groupby('Month')['Count'].sum().reset_index()
        upd_trend['Month'] = upd_trend['Month'].astype(str)
        fig_upd = px.bar(upd_trend, x='Month', y='Count', 
                         color_discrete_sequence=['#ff6c6c'], text_auto='.2s')
        st.plotly_chart(fig_upd, width="stretch")

    with col2:
        st.subheader("State Saturation Hierarchy")
        
        # Prepare data for Exploded Pie
        pie_data = df_sat.sort_values(by='Projected_Pop_2025', ascending=False)
        # Create a 'pull' list: 0.2 for the first item (largest), 0 for others
        pull_config = [0.2] + [0.0] * (len(pie_data) - 1)
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_data['State'], 
            values=pie_data['Projected_Pop_2025'],
            pull=pull_config, # Explode the largest slice to give that "3D pop" look
            hole=0.0, # Full pie (not donut) to match reference
            textinfo='percent+label',
            marker=dict(colors=px.colors.qualitative.Prism, line=dict(color='#000000', width=1))
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05) # Legend on right like reference
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
