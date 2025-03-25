import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_pipeline_metrics, load_csv_data
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
    .error-message {
        color: #ff4b4b;
        padding: 1rem;
        background-color: #ffe5e5;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-message {
        padding: 1rem;
        background-color: #e5f6ff;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📊 Sales Stack Ranker")
st.markdown("""
    This dashboard provides real-time insights into your sales pipeline performance.
    Track key metrics, rep performance, and pipeline health at a glance.
""")

# CSV Data Loader in Sidebar with Template Download
st.sidebar.header("Data Source")

# Add CSV template download button
st.sidebar.markdown("""
### CSV Template Format
Your CSV should include these columns:
- OpportunityID (text)
- Owner (text)
- Region (text)
- CreatedDate (YYYY-MM-DD)
- CloseDate (YYYY-MM-DD)
- Stage (0-4)
- Amount (positive number)
- Source (text)
""")

# Generate sample data for template
sample_df = pd.DataFrame({
    'OpportunityID': ['OPP001', 'OPP002'],
    'Owner': ['John Doe', 'Jane Smith'],
    'Region': ['West', 'East'],
    'CreatedDate': ['2024-01-01', '2024-01-02'],
    'CloseDate': ['2024-03-01', '2024-03-02'],
    'Stage': [0, 1],
    'Amount': [50000, 75000],
    'Source': ['Rep', 'Marketing']
})

# Convert sample DataFrame to CSV
csv_template = sample_df.to_csv(index=False)
st.sidebar.download_button(
    label="📥 Download CSV Template",
    data=csv_template,
    file_name="sales_pipeline_template.csv",
    mime="text/csv"
)

uploaded_file = st.sidebar.file_uploader("Upload your own CSV file (optional)", type=["csv"])

# Load and process data
if uploaded_file is not None:
    try:
        df = load_csv_data(uploaded_file)
        st.sidebar.success("✅ Custom data loaded successfully!")
        
        # Show data preview with validation message
        if st.sidebar.checkbox("Show Data Preview"):
            st.sidebar.markdown("""
            <div class="info-message">
            ✓ All data validated successfully:
            - Required columns present
            - Date formats valid
            - Numeric values valid
            - No missing required data
            </div>
            """, unsafe_allow_html=True)
            st.sidebar.dataframe(df.head(), use_container_width=True)
            
    except ValueError as e:
        st.sidebar.markdown(f"""
        <div class="error-message">
        ⚠️ Error in uploaded CSV:
        {str(e)}
        <br><br>
        Using synthetic data instead.
        </div>
        """, unsafe_allow_html=True)
        df = load_data()
    except Exception as e:
        st.sidebar.markdown(f"""
        <div class="error-message">
        ⚠️ Unexpected error:
        {str(e)}
        <br><br>
        Using synthetic data instead.
        </div>
        """, unsafe_allow_html=True)
        df = load_data()
else:
    df = load_data()  # Use synthetic data by default
    st.sidebar.info("ℹ️ Using synthetic data. Upload your CSV file to use custom data.")

# Calculate metrics
metrics = get_pipeline_metrics(df)

# Sidebar filters (only show if we have data)
if not df.empty:
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
else:
    filtered_df = df

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
        f"{(metrics['qualified_pipeline']/metrics['total_pipeline']*100 if metrics['total_pipeline'] > 0 else 0):.1f}% of Total"
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
    if not df.empty:
        stage_counts = df['Stage'].value_counts().sort_index()
        fig_stage = px.bar(
            x=stage_counts.index,
            y=stage_counts.values,
            title='Opportunities by Stage',
            labels={'x': 'Stage', 'y': 'Count'}
        )
    else:
        fig_stage = px.bar(
            x=[],
            y=[],
            title='Opportunities by Stage (No Data)',
            labels={'x': 'Stage', 'y': 'Count'}
        )
    st.plotly_chart(fig_stage, use_container_width=True)

# Rep Rankings Table
st.subheader("Rep Rankings")
if not metrics['rep_rankings'].empty:
    st.dataframe(
        metrics['rep_rankings'],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No rep data available.")

# Pipeline Trend
st.subheader("Pipeline Trend")
if not df.empty:
    pipeline_trend = df.groupby(df['CreatedDate'].dt.date)['Amount'].sum().reset_index()
    fig_trend = px.line(
        pipeline_trend,
        x='CreatedDate',
        y='Amount',
        title='Pipeline Growth Over Time'
    )
else:
    fig_trend = px.line(
        pd.DataFrame({'CreatedDate': [], 'Amount': []}),
        x='CreatedDate',
        y='Amount',
        title='Pipeline Growth Over Time (No Data)'
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