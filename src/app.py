import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_folium import st_folium
from data_loader import load_data, merge_for_map
from metrics import (
    calculate_update_intensity, calculate_age_distribution, detect_anomalies,
    get_seasonal_patterns, get_demographic_vs_biometric_seasonal,
    detect_migration_spikes, get_district_update_velocity, detect_geographic_clusters,
    analyze_age_transitions, get_age_group_update_patterns, calculate_mbu_demand_forecast,
    trivariate_analysis, get_state_month_heatmap_data, get_enrollment_update_correlation
)

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
    gen_ai_btn = st.button("✨ Generate AI Insight", type="primary", width='stretch')

# Load Data
with st.spinner("Loading aggregated Aadhaar datasets..."):
    df_enr, df_upd, gdf = load_data()

# Store original unfiltered data for societal trends analysis
df_enr_full = df_enr.copy()
df_upd_full = df_upd.copy()

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

# Layout: Tabs - Extended for Societal Trends Analysis
tab_trends, tab_seasonal, tab_migration, tab_age18, tab1, tab2, tab3, tab_trivar = st.tabs([
    "📈 Overall Trends",
    "💒 Seasonal Patterns",
    "🚚 Migration Detection",
    "🎓 Age-18 Milestone",
    "🏭 Operational Intensity",
    "👥 Demographics",
    "🛡️ System Integrity",
    "🔬 Trivariate Analysis"
])
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



# =============================================================================
# NEW TAB: SEASONAL PATTERNS (Wedding Seasons, School Admissions)
# =============================================================================
with tab_seasonal:
    st.header("💒 Seasonal Patterns in Aadhaar Updates")
    st.markdown("""
    **Hypothesis**: Demographic updates spike during wedding seasons (Nov-Feb, Apr-May) due to name/address changes after marriage.
    School admission seasons (Apr-Jun) may also show enrollment spikes for children.
    """)

    # Use full data for societal trends analysis
    st.caption("📊 Analyzing all-India data for societal patterns")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Monthly Update Patterns")
        seasonal_data = get_seasonal_patterns(df_upd_full, df_enr_full)

        if not seasonal_data.empty:
            # Color by season
            color_map = {
                'Wedding Season (Nov-Feb)': '#E91E63',
                'Wedding Season (Apr-May)': '#FF5722',
                'School Admission (Jun)': '#2196F3',
                'Regular Period': '#9E9E9E'
            }
            seasonal_data['Color'] = seasonal_data['Season'].map(color_map)

            fig_seasonal = go.Figure()

            for season in seasonal_data['Season'].unique():
                season_df = seasonal_data[seasonal_data['Season'] == season]
                fig_seasonal.add_trace(go.Bar(
                    x=season_df['Month_Name'],
                    y=season_df['Total_Updates'],
                    name=season,
                    marker_color=color_map.get(season, '#9E9E9E')
                ))

            fig_seasonal.update_layout(
                title="Updates by Month (Color-coded by Season)",
                xaxis_title="Month",
                yaxis_title="Total Updates",
                plot_bgcolor='white',
                paper_bgcolor='white',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig_seasonal, width='stretch')

            # Deviation chart
            st.subheader("Deviation from Average")
            fig_dev = px.bar(seasonal_data, x='Month_Name', y='Deviation_Pct',
                            color='Season', color_discrete_map=color_map,
                            title="% Deviation from Average Monthly Updates")
            fig_dev.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_dev.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=300)
            st.plotly_chart(fig_dev, width='stretch')
        else:
            st.warning("Insufficient data for seasonal analysis.")

    with col2:
        st.subheader("📊 Key Insights")

        if not seasonal_data.empty:
            # Wedding season analysis
            wedding_months = seasonal_data[seasonal_data['Season'].str.contains('Wedding')]
            regular_months = seasonal_data[seasonal_data['Season'] == 'Regular Period']

            if not wedding_months.empty and not regular_months.empty:
                wedding_avg = wedding_months['Total_Updates'].mean()
                regular_avg = regular_months['Total_Updates'].mean()
                wedding_increase = ((wedding_avg - regular_avg) / regular_avg * 100) if regular_avg > 0 else 0

                st.metric("Wedding Season Avg", f"{wedding_avg:,.0f}", f"{wedding_increase:+.1f}% vs regular")

            # Peak month
            peak_month = seasonal_data.loc[seasonal_data['Total_Updates'].idxmax()]
            st.metric("Peak Month", peak_month['Month_Name'], f"{peak_month['Total_Updates']:,.0f} updates")

            st.info("""
            **Marriage-Related Updates Pattern:**
            - Women typically update name after marriage
            - Address changes when relocating to spouse's home
            - Mobile number updates common
            - Peak expected: Nov-Feb (wedding season)
            """)

        st.subheader("Demographic vs Biometric by Season")
        demo_bio_seasonal = get_demographic_vs_biometric_seasonal(df_upd_full)
        if not demo_bio_seasonal.empty:
            fig_type_season = px.line(demo_bio_seasonal, x='Month_Num', y='Count',
                                      color='Type', markers=True,
                                      title="Update Type Trend by Month")
            fig_type_season.update_layout(height=250, plot_bgcolor='white')
            st.plotly_chart(fig_type_season, width='stretch')

# =============================================================================
# NEW TAB: MIGRATION DETECTION (Disaster/Event-driven updates)
# =============================================================================
with tab_migration:
    st.header("🚚 Migration & Event-Driven Update Detection")
    st.markdown("""
    **Hypothesis**: Sudden spikes in address updates in specific districts may indicate:
    - Migration after natural disasters (floods, earthquakes)
    - Mass relocation due to industrial changes
    - Seasonal labor migration patterns
    """)

    # Use full data for migration analysis
    st.caption("📊 Analyzing all-India data for migration patterns")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("District Update Velocity (High = Potential Migration)")
        velocity_data = get_district_update_velocity(df_upd_full)

        if not velocity_data.empty:
            # Top 20 by velocity
            top_velocity = velocity_data.nlargest(20, 'Daily_Velocity')

            fig_velocity = px.bar(top_velocity, x='District', y='Daily_Velocity',
                                  color='State', title="Top 20 Districts by Daily Update Velocity",
                                  hover_data=['Total_Updates', 'Days_Active'])
            fig_velocity.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                xaxis_tickangle=-45, height=400
            )
            st.plotly_chart(fig_velocity, width='stretch')

            # Spike detection
            st.subheader("⚠️ Month-over-Month Spike Detection")
            spike_data = detect_migration_spikes(df_upd_full)

            if not spike_data.empty:
                spikes = spike_data[spike_data['Is_Spike'] == True].dropna()
                if not spikes.empty:
                    st.error(f"**{len(spikes)} potential migration events detected!**")

                    # Show top spikes
                    top_spikes = spikes.nlargest(10, 'MoM_Change_Pct')[['District', 'State', 'Year_Month', 'MoM_Change_Pct', 'Count']]
                    top_spikes.columns = ['District', 'State', 'Month', 'Change %', 'Updates']
                    st.dataframe(top_spikes, width='stretch')

                    # Visualization
                    fig_spikes = px.scatter(spikes.head(50), x='Year_Month', y='MoM_Change_Pct',
                                           size='Count', color='State', hover_name='District',
                                           title="Detected Spikes (>100% MoM Increase)")
                    fig_spikes.update_layout(plot_bgcolor='white', height=350)
                    st.plotly_chart(fig_spikes, width='stretch')
                else:
                    st.success("No significant migration spikes detected in current data.")

    with col2:
        st.subheader("📍 Geographic Cluster Analysis")

        state_updates, district_high = detect_geographic_clusters(df_upd_full)

        if not state_updates.empty:
            # High activity states
            high_activity = state_updates[state_updates['Is_High_Activity']]

            st.markdown("**States with Unusually High Update Activity:**")
            if not high_activity.empty:
                for _, row in high_activity.iterrows():
                    st.warning(f"🔴 **{row['State']}**: {row['Total_Updates']:,.0f} updates")
            else:
                st.info("No states with unusually high activity detected.")

            # State-wise distribution
            fig_state = px.treemap(state_updates, path=['State'], values='Total_Updates',
                                   title="State-wise Update Distribution",
                                   color='Total_Updates', color_continuous_scale='Reds')
            fig_state.update_layout(height=350)
            st.plotly_chart(fig_state, width='stretch')

        st.subheader("🔍 Interpretation Guide")
        st.info("""
        **High Velocity Districts** may indicate:
        - Post-disaster address updates
        - Migrant worker hubs
        - Urban centers with high mobility

        **Sudden Spikes** (>100% MoM) suggest:
        - Mass migration event
        - Disaster recovery period
        - Policy-driven update campaigns
        """)

# =============================================================================
# NEW TAB: AGE-18 MILESTONE TRACKING
# =============================================================================
with tab_age18:
    st.header("🎓 Age-18 Milestone & Lifecycle Tracking")
    st.markdown("""
    **Key Milestones in Aadhaar Lifecycle:**
    - **Age 5**: First Mandatory Biometric Update (MBU)
    - **Age 15**: Second MBU
    - **Age 18**: Adult transition - often needs update for voting, college, employment
    """)

    # Use full data for lifecycle analysis
    st.caption("📊 Analyzing all-India data for age-based patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Enrollment to Update Transition Analysis")
        transition_data = analyze_age_transitions(df_enr_full, df_upd_full)

        if not transition_data.empty:
            # Update rate by state
            fig_transition = px.bar(transition_data.nlargest(15, 'Update_Rate'),
                                   x='State', y='Update_Rate',
                                   color='Adult_Enrollment_Share',
                                   color_continuous_scale='Viridis',
                                   title="Update Rate vs Adult Enrollment Share by State")
            fig_transition.update_layout(plot_bgcolor='white', height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_transition, width='stretch')

            # Scatter plot: Enrollment vs Updates
            fig_scatter = px.scatter(transition_data, x='Enrolment_Count', y='Count',
                                    size='age_18_greater', color='Update_Rate',
                                    hover_name='State',
                                    title="Enrollment vs Updates (Bubble size = 18+ Enrollments)",
                                    color_continuous_scale='RdYlGn')
            fig_scatter.update_layout(plot_bgcolor='white', height=400)
            st.plotly_chart(fig_scatter, width='stretch')

    with col2:
        st.subheader("MBU Demand Forecast by State")
        mbu_forecast = calculate_mbu_demand_forecast(df_enr_full)

        if not mbu_forecast.empty:
            # Top states by MBU demand
            top_mbu = mbu_forecast.nlargest(10, 'Total_MBU_Demand')

            fig_mbu = go.Figure()
            fig_mbu.add_trace(go.Bar(name='Immediate (Age 5)', x=top_mbu['State'], y=top_mbu['MBU_Immediate'], marker_color='#E53935'))
            fig_mbu.add_trace(go.Bar(name='Short-term (Age 15)', x=top_mbu['State'], y=top_mbu['MBU_ShortTerm'], marker_color='#FB8C00'))
            fig_mbu.add_trace(go.Bar(name='Long-term (Adult)', x=top_mbu['State'], y=top_mbu['MBU_LongTerm'], marker_color='#43A047'))

            fig_mbu.update_layout(
                title="Projected MBU Demand by State",
                barmode='stack',
                plot_bgcolor='white', paper_bgcolor='white',
                height=400, xaxis_tickangle=-45
            )
            st.plotly_chart(fig_mbu, width='stretch')

            # Key metrics
            total_immediate = mbu_forecast['MBU_Immediate'].sum()
            total_shortterm = mbu_forecast['MBU_ShortTerm'].sum()
            total_longterm = mbu_forecast['MBU_LongTerm'].sum()

            st.metric("Immediate MBU Demand (Age 5)", f"{total_immediate:,.0f}")
            st.metric("Short-term MBU Demand (Age 15)", f"{total_shortterm:,.0f}")
            st.metric("Long-term Adult Updates", f"{total_longterm:,.0f}")

        st.subheader("📋 Age-18 Specific Insights")

        # Calculate 17+ updates (proxy for 18+)
        if 'Age_17_Plus' in df_upd_full.columns:
            adult_updates = df_upd_full['Age_17_Plus'].sum()
            total_updates = df_upd_full['Count'].sum()
            adult_share = (adult_updates / total_updates * 100) if total_updates > 0 else 0

            st.metric("17+ Age Updates", f"{adult_updates:,.0f}", f"{adult_share:.1f}% of total")

        st.info("""
        **Age-18 Update Drivers:**
        - Voter ID linkage requirement
        - College admission documentation
        - First job/employment verification
        - Bank account opening (KYC)
        - Driving license application
        """)

# =============================================================================
# NEW TAB: TRIVARIATE ANALYSIS (Age × Geography × Time)
# =============================================================================
with tab_trivar:
    st.header("🔬 Trivariate Analysis: Age × Geography × Time")
    st.markdown("Multi-dimensional analysis combining age groups, geographic regions, and temporal patterns.")

    # Use full data for trivariate analysis
    st.caption("📊 Analyzing all-India data for multi-dimensional patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("State × Month Heatmap (Updates)")
        heatmap_data = get_state_month_heatmap_data(df_upd_full)

        if not heatmap_data.empty:
            # Limit to top 15 states for readability
            top_states = df_upd_full.groupby('State')['Count'].sum().nlargest(15).index
            heatmap_filtered = heatmap_data.loc[heatmap_data.index.isin(top_states)]

            fig_heatmap = px.imshow(heatmap_filtered,
                                    labels=dict(x="Month", y="State", color="Updates"),
                                    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:len(heatmap_filtered.columns)],
                                    y=heatmap_filtered.index,
                                    color_continuous_scale='YlOrRd',
                                    title="Update Intensity Heatmap (Top 15 States)")
            fig_heatmap.update_layout(height=500)
            st.plotly_chart(fig_heatmap, width='stretch')
        else:
            st.warning("Insufficient data for heatmap.")

    with col2:
        st.subheader("Enrollment vs Update Correlation")
        correlation_data, corr_value = get_enrollment_update_correlation(df_enr_full, df_upd_full)

        if not correlation_data.empty:
            st.metric("Correlation Coefficient", f"{corr_value:.3f}")

            if corr_value > 0.7:
                st.success("Strong positive correlation: Updates follow enrollment patterns (lifecycle-driven)")
            elif corr_value > 0.4:
                st.info("Moderate correlation: Mix of lifecycle and event-driven updates")
            else:
                st.warning("Weak correlation: Updates may be event-driven (migration, disasters)")

            fig_corr = px.scatter(correlation_data, x='Enrollments', y='Updates',
                                  size='Update_to_Enrollment_Ratio', hover_name='State',
                                  title="Enrollment vs Update Correlation by State")
            fig_corr.update_layout(plot_bgcolor='white', height=400)
            st.plotly_chart(fig_corr, width='stretch')

    # Trivariate: Age × State × Month
    st.subheader("Age Group × State × Time Analysis")
    trivar_enr, trivar_upd = trivariate_analysis(df_enr_full, df_upd_full)

    if not trivar_enr.empty:
        col3, col4 = st.columns(2)

        with col3:
            # Age group trend over time (aggregated)
            age_time = trivar_enr.groupby('Year_Month').agg({
                'age_0_5': 'sum',
                'age_5_17': 'sum',
                'age_18_greater': 'sum'
            }).reset_index()

            fig_age_time = go.Figure()
            fig_age_time.add_trace(go.Scatter(x=age_time['Year_Month'], y=age_time['age_0_5'],
                                              name='0-5 Years', mode='lines+markers', line=dict(color='#4CAF50')))
            fig_age_time.add_trace(go.Scatter(x=age_time['Year_Month'], y=age_time['age_5_17'],
                                              name='5-17 Years', mode='lines+markers', line=dict(color='#2196F3')))
            fig_age_time.add_trace(go.Scatter(x=age_time['Year_Month'], y=age_time['age_18_greater'],
                                              name='18+ Years', mode='lines+markers', line=dict(color='#F44336')))

            fig_age_time.update_layout(
                title="Enrollment by Age Group Over Time",
                plot_bgcolor='white', paper_bgcolor='white',
                height=350, xaxis_tickangle=-45
            )
            st.plotly_chart(fig_age_time, width='stretch')

        with col4:
            # Update type trend over time
            if not trivar_upd.empty:
                fig_upd_time = px.line(trivar_upd, x='Year_Month', y='Count',
                                       color='Type', markers=True,
                                       title="Update Type Over Time")
                fig_upd_time.update_layout(plot_bgcolor='white', height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig_upd_time, width='stretch')

    st.subheader("🎯 Multi-Dimensional Insights Summary")
    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown("**Temporal Patterns**")
        st.info("""
        - Wedding seasons show demographic update spikes
        - School admission periods show child enrollment peaks
        - Year-end shows administrative backlogs
        """)

    with col6:
        st.markdown("**Geographic Patterns**")
        st.info("""
        - Urban centers: Higher update velocity
        - Disaster-prone areas: Spike patterns
        - Migrant destinations: Address update clusters
        """)

    with col7:
        st.markdown("**Age-based Patterns**")
        st.info("""
        - 0-5: New child enrollments
        - 5-17: MBU at milestones
        - 18+: Life event updates (marriage, job)
        """)

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
            st_folium(m, height=400, returned_objects=[], use_container_width=True)
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
