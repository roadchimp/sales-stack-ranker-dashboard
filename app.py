import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_pipeline_metrics
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Sales Stack Ranker",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📊 Sales Stack Ranker")
st.markdown("""
    This dashboard provides real-time insights into your sales pipeline performance.
    Track key metrics, rep performance, and pipeline health at a glance.
""")

# Load data
df = load_data()
metrics = get_pipeline_metrics(df)

# Sidebar filters
st.sidebar.header("Filters")
selected_region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(df['CreatedDate'].min(), df['CreatedDate'].max()),
    min_value=df['CreatedDate'].min(),
    max_value=df['CreatedDate'].max()
)

# Apply filters
filtered_df = df[
    (df['Region'].isin(selected_region)) &
    (df['CreatedDate'].dt.date >= date_range[0]) &
    (df['CreatedDate'].dt.date <= date_range[1])
]

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Pipeline",
        f"${metrics['total_pipeline']:,.0f}",
        f"{metrics['late_stage_percentage']:.1f}% Late Stage"
    )

with col2:
    st.metric(
        "Qualified Pipeline",
        f"${metrics['qualified_pipeline']:,.0f}",
        f"{(metrics['qualified_pipeline']/metrics['total_pipeline']*100):.1f}% of Total"
    )

with col3:
    st.metric(
        "Stage 0 Pipeline",
        f"${metrics['stage_0_pipeline']:,.0f}",
        f"{metrics['stage_0_count']} Opportunities"
    )

with col4:
    st.metric(
        "Avg Stage 0 Age",
        f"{metrics['avg_stage_0_age']:.0f} days",
        "Time in Prospecting"
    )

# Pipeline by Source and Stage Distribution
col1, col2 = st.columns(2)

with col1:
    # Pipeline by Source
    source_data = pd.DataFrame(
        list(metrics['pipeline_by_source'].items()),
        columns=['Source', 'Amount']
    )
    fig_source = px.pie(
        source_data,
        values='Amount',
        names='Source',
        title='Pipeline by Source'
    )
    st.plotly_chart(fig_source, use_container_width=True)

with col2:
    # Stage Distribution
    stage_counts = df['Stage'].value_counts().sort_index()
    fig_stage = px.bar(
        x=stage_counts.index,
        y=stage_counts.values,
        title='Opportunities by Stage',
        labels={'x': 'Stage', 'y': 'Count'}
    )
    st.plotly_chart(fig_stage, use_container_width=True)

# Rep Rankings Table
st.subheader("Rep Rankings")
st.dataframe(
    metrics['rep_rankings'],
    use_container_width=True,
    hide_index=True
)

# Pipeline Trend
st.subheader("Pipeline Trend")
pipeline_trend = df.groupby(df['CreatedDate'].dt.date)['Amount'].sum().reset_index()
fig_trend = px.line(
    pipeline_trend,
    x='CreatedDate',
    y='Amount',
    title='Pipeline Growth Over Time'
)
st.plotly_chart(fig_trend, use_container_width=True)

# Footer with future enhancements
st.markdown("---")
st.markdown("""
    ### Future Enhancements
    - 🔄 Real-time Salesforce integration
    - 📧 Automated email digests
    - 🔍 Advanced filtering and search
    - 📱 Mobile-optimized view
    - 📈 Custom KPI tracking
""") 