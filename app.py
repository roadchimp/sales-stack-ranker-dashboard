"""
Sales Stack Ranker Dashboard
"""
import streamlit as st
from pathlib import Path
import pandas as pd

# Import components
from components.pipeline_analysis import display_pipeline_analysis_tab
from components.rep_performance import display_rep_performance_tab
from components.source_analysis import display_source_analysis_tab
from components.email_controls import display_email_controls
from components.ai_commentary import display_ai_commentary_tab

# Import utilities
from utils.data_loader import load_data, load_csv_data, get_required_columns
from utils.metrics_calculator import get_pipeline_metrics
from utils.ai_commentary import generate_commentary

# Set page config (must be called before any other Streamlit command)
st.set_page_config(
    page_title="Sales Stack Ranker",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
with open(Path(__file__).parent / "styles" / "custom.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Initialize session state for data and commentary
if 'df' not in st.session_state:
    try:
        st.session_state.df = load_data()
        if st.session_state.df.empty:
            st.error("Error: Unable to load or generate data. Please check the logs for details.")
    except Exception as e:
        st.error(f"Error initializing data: {str(e)}")
        st.session_state.df = pd.DataFrame(columns=get_required_columns().keys())

if 'commentary' not in st.session_state:
    st.session_state.commentary = None

# Use the session state DataFrame
df = st.session_state.df

# Initialize filtered_df with the full dataset
filtered_df = df

# Sidebar with collapsible sections
st.sidebar.header("📊 Dashboard Controls")

# Filters section
with st.sidebar.expander("🔍 Filters", expanded=False):
    if not df.empty:
        selected_region = st.multiselect(
            "Select Region",
            options=df['Region'].unique(),
            default=df['Region'].unique()
        )

        date_range = st.date_input(
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
        ].copy()  # Create a copy to avoid SettingWithCopyWarning

# Calculate filtered metrics
late_stage_deals = filtered_df[filtered_df['Stage'] >= 3].copy()
won_deals = late_stage_deals[late_stage_deals['Stage'] == 4].copy()

# Title and description
st.title("📊 Sales Stack Ranker")
st.markdown("""
    This dashboard provides real-time insights into your sales pipeline performance.
    Track key metrics, rep performance, and pipeline health at a glance.
""")

# Calculate metrics
try:
    metrics = get_pipeline_metrics(filtered_df)
except Exception as e:
    st.error(f"Error calculating metrics: {str(e)}")
    metrics = get_pipeline_metrics(pd.DataFrame(columns=get_required_columns().keys()))

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "👥 Reps",
    "🔍 Pipeline",
    "📊 Sources",
    "📧 Email Controls"
])

# Overview Tab
with tab1:
    st.header("Sales Pipeline Overview")
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Pipeline",
            f"${metrics['total_pipeline']:,.2f}"
        )
        st.metric(
            "Qualified Pipeline",
            f"${metrics['qualified_pipeline']:,.2f}"
        )
    
    with col2:
        st.metric(
            "Win Rate",
            f"{metrics['win_rate']:.1%}"
        )
        st.metric(
            "Avg Deal Size",
            f"${metrics['avg_deal_size']:,.2f}"
        )
    
    with col3:
        st.metric(
            "Pipeline Velocity",
            f"{metrics['pipeline_velocity']:.1f} days"
        )
        st.metric(
            "Late Stage Amount",
            f"${metrics['late_stage_amount']:,.2f}"
        )
    
    # AI Commentary Section
    st.subheader("AI-Generated Insights")
    
    # Add a refresh button
    if st.button("Refresh Insights"):
        st.session_state.commentary = None
    
    if st.session_state.commentary is None:
        with st.spinner("Generating insights..."):
            try:
                # Generate commentary
                commentary = generate_commentary(filtered_df, metrics)
                st.session_state.commentary = commentary
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
                st.session_state.commentary = "Unable to generate insights at this time."
    
    # Display the commentary with consistent styling
    st.markdown("""
        <style>
        .ai-insights {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .ai-insights h3 {
            color: #1f77b4;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        .ai-insights ul {
            list-style-type: none;
            padding-left: 0;
        }
        .ai-insights li {
            margin-bottom: 0.5em;
            padding-left: 1.5em;
            position: relative;
        }
        .ai-insights li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #1f77b4;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="ai-insights">{st.session_state.commentary}</div>', unsafe_allow_html=True)
    
    # Display pipeline by stage
    st.subheader("Pipeline by Stage")
    stage_pipeline = df.groupby('Stage')['Amount'].sum().reset_index()
    stage_pipeline['Stage'] = stage_pipeline['Stage'].astype(str)
    st.bar_chart(stage_pipeline.set_index('Stage'))

# Rep Performance Tab
with tab2:
    display_rep_performance_tab(df)

# Pipeline Analysis Tab
with tab3:
    display_pipeline_analysis_tab(df, metrics)

# Source Analysis Tab
with tab4:
    display_source_analysis_tab(df)

# Email Controls Tab
with tab5:
    display_email_controls()

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by Roadchimp")

# Collapsible data source section
with st.sidebar.expander("📥 Data Source", expanded=False):
    st.markdown("""
    ### CSV Template Format
    Your CSV should include these columns:
    - OpportunityID (text)
    - Owner (text)
    - Role (text)
    - Region (text)
    - CreatedDate (YYYY-MM-DD)
    - CloseDate (YYYY-MM-DD)
    - Stage (0-4)
    - Amount (positive number)
    - Source (text)
    - LeadSourceCategory (text)
    - QualifiedPipeQTD (number)
    - LateStageAmount (number)
    - AvgAge (number)
    - Stage0Age (number)
    - Stage0Count (number)
    - PipelineCreatedQTD (number)
    - PipelineTargetQTD (number)
    """)

    # Generate sample data for template
    sample_df = pd.DataFrame({
        'OpportunityID': ['OPP001', 'OPP002'],
        'Owner': ['John Doe', 'Jane Smith'],
        'Role': ['Account Executive', 'Senior AE'],
        'Region': ['West', 'East'],
        'CreatedDate': ['2024-01-01', '2024-01-02'],
        'CloseDate': ['2024-03-01', '2024-03-02'],
        'Stage': [0, 1],
        'Amount': [50000, 75000],
        'Source': ['Rep', 'Marketing'],
        'LeadSourceCategory': ['Inbound', 'Outbound'],
        'QualifiedPipeQTD': [0, 75000],
        'LateStageAmount': [0, 0],
        'AvgAge': [30, 45],
        'Stage0Age': [30, 0],
        'Stage0Count': [1, 0],
        'PipelineCreatedQTD': [50000, 75000],
        'PipelineTargetQTD': [60000, 90000]
    })

    # Convert sample DataFrame to CSV
    csv_template = sample_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Template",
        data=csv_template,
        file_name="sales_pipeline_template.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Upload your own CSV file (optional)", type=["csv"])

    # Load and process data
    if uploaded_file is not None:
        try:
            df = load_csv_data(uploaded_file)
            st.session_state.df = df
            st.success("✅ Custom data loaded successfully!")
            
            # Show data preview with validation message
            if st.checkbox("Show Data Preview"):
                st.markdown("""
                ✓ All data validated successfully:
                - Required columns present
                - Date formats valid
                - Numeric values valid
                - No missing required data
                """)
                st.dataframe(df.head(), use_container_width=True)
                
        except ValueError as e:
            st.error(f"⚠️ Error in uploaded CSV: {str(e)}")
            if st.session_state.df.empty:
                st.session_state.df = load_data()
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")
            if st.session_state.df.empty:
                st.session_state.df = load_data() 