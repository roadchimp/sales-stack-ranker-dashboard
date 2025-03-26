import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_pipeline_metrics, load_csv_data, get_required_columns
import pandas as pd
from datetime import datetime
import openai

# Set page config (must be called before any other Streamlit command)
st.set_page_config(
    page_title="Sales Stack Ranker",
    page_icon="📊",
    layout="wide"
)

# Initialize OpenAI client with just the API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_commentary(summary_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an insightful sales analytics expert providing concise commentary on sales data.Please provide a clear, concise analysis of these metrics, focusing on key insights and potential areas for attention. Format the response in clear paragraphs with proper spacing using consistent fonts and avoiding italics."},
                {"role": "user", "content": f"Provide insightful commentary on this sales data summary: {summary_text}"}
            ],
            max_tokens=200,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating commentary: {str(e)}")
        return "Unable to generate commentary at this time."

# Initialize session state for data
if 'df' not in st.session_state:
    try:
        st.session_state.df = load_data()
        if st.session_state.df.empty:
            st.error("Error: Unable to load or generate data. Please check the logs for details.")
    except Exception as e:
        st.error(f"Error initializing data: {str(e)}")
        st.session_state.df = pd.DataFrame(columns=get_required_columns().keys())

# Use the session state DataFrame
df = st.session_state.df

# Calculate metrics (with error handling)
try:
    metrics = get_pipeline_metrics(df)
except Exception as e:
    st.error(f"Error calculating metrics: {str(e)}")
    metrics = get_pipeline_metrics(pd.DataFrame(columns=get_required_columns().keys()))

# Generate AI commentary
try:
    summary = f"""The total sales pipeline is currently valued at ${metrics['total_pipeline']:,.0f}, which indicates the total potential revenue from all opportunities in the pipeline.

The Qualified Pipeline for the quarter to date (QTD) is ${metrics['qualified_pipeline']:,.0f}. This is the amount of potential revenue from opportunities that have been qualified and are likely to close. This figure is less than the total pipeline, indicating that there's a considerable number of opportunities in the early stages of the sales process that have not yet been qualified.

The Late Stage Pipeline, which stands at ${metrics['late_stage_pipeline']:,.0f}, represents opportunities that are in the final stages of the sales process. These are deals that are likely to close soon, contributing significantly to the company's revenue. This figure is {metrics['late_stage_pipeline']/metrics['qualified_pipeline']:.1f} times the value of the qualified pipeline, suggesting that the sales team is doing a good job of moving opportunities through the pipeline.

The Average Stage 0 Age is {metrics['avg_stage_0_age']:.1f} days, which indicates the average time opportunities spend in the initial prospecting stage. This metric helps track the efficiency of early-stage pipeline management and qualification process."""
except Exception as e:
    st.error(f"Error generating commentary: {str(e)}")
    summary = "Unable to generate commentary at this time."

# Custom CSS
st.markdown("""
    <style>
    /* Base styles */
    .main {
        padding: 1rem;
    }
    
    /* Dark mode styles */
    [data-theme="dark"] .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
    }
    
    [data-theme="dark"] .stMetric label {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    [data-theme="dark"] .stMetric [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    [data-theme="dark"] .stMetric [data-testid="stMetricDelta"] {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Light mode styles */
    [data-theme="light"] .stMetric {
        background-color: #f0f2f6;
        color: #0e1117 !important;
    }
    
    [data-theme="light"] .stMetric label {
        color: #0e1117 !important;
    }
    
    [data-theme="light"] .stMetric [data-testid="stMetricValue"] {
        color: #0e1117 !important;
    }
    
    [data-theme="light"] .stMetric [data-testid="stMetricDelta"] {
        color: #0e1117 !important;
    }
    
    /* Common metric styles */
    .stMetric {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        width: 100%;
        box-sizing: border-box;
    }
    
    .stMetric > div[data-testid="metric-container"] {
        width: 100%;
    }
    
    .stMetric label {
        font-size: clamp(0.8rem, 2vw, 1rem);
        white-space: normal !important;
    }
    
    .stMetric .css-1xarl3l {
        font-size: clamp(1.2rem, 4vw, 1.8rem);
    }
    
    /* Responsive metrics styling */
    .stMetric {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        width: 100%;
        box-sizing: border-box;
    }
    /* Make metric text responsive */
    .stMetric > div[data-testid="metric-container"] {
        width: 100%;
    }
    .stMetric label {
        font-size: clamp(0.8rem, 2vw, 1rem);
        white-space: normal !important;
    }
    .stMetric .css-1xarl3l {
        font-size: clamp(1.2rem, 4vw, 1.8rem);
    }
    /* Responsive table styling */
    [data-testid="stDataFrame"] {
        width: 100%;
        overflow-x: auto;
    }
    /* Responsive chart styling */
    [data-testid="stPlotlyChart"] > div {
        width: 100%;
        min-height: 200px;
    }
    /* Improve tab navigation on mobile */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        white-space: nowrap;
        font-size: clamp(0.8rem, 2vw, 1rem);
    }
    /* Make columns stack on mobile */
    @media (max-width: 640px) {
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
    /* Mobile-friendly sidebar */
    .css-1d391kg {
        width: auto;
    }
    @media (max-width: 640px) {
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
        .css-1d391kg .block-container {
            padding: 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📊 Sales Stack Ranker")
st.markdown("""
    This dashboard provides real-time insights into your sales pipeline performance.
    Track key metrics, rep performance, and pipeline health at a glance.
""")

# Update the metrics display code to use custom classes
if "dark" in st.config.get_option("theme.base"):
    metrics_bg_color = "rgba(255, 255, 255, 0.1)"
    text_color = "white"
else:
    metrics_bg_color = "#f0f2f6"
    text_color = "#0e1117"

# Key Metrics Row with explicit styling
for metric in [
    {
        "label": "Total Pipeline",
        "value": f"${metrics['total_pipeline']:,.0f}",
        "delta": f"{metrics['late_stage_percentage']:.1f}% Late Stage",
        "delta_color": "normal"
    },
    {
        "label": "Qualified Pipeline",
        "value": f"${metrics['qualified_pipeline']:,.0f}",
        "delta": f"{(metrics['qualified_pipeline']/metrics['total_pipeline']*100 if metrics['total_pipeline'] > 0 else 0):.1f}% of Total",
        "delta_color": "normal"
    },
    {
        "label": "Average Deal Size",
        "value": f"${filtered_df['Amount'].mean() if not filtered_df.empty else 0:,.0f}",
        "delta": "Per Opportunity",
        "delta_color": "off"
    },
    {
        "label": "Late Stage Win Rate",
        "value": f"{(len(won_deals) / len(late_stage_deals) * 100 if len(late_stage_deals) > 0 else 0):.1f}%",
        "delta": "Stage 3+ Opportunities",
        "delta_color": "off"
    }
]:
    st.metric(
        label=metric["label"],
        value=metric["value"],
        delta=metric["delta"],
        delta_color=metric.get("delta_color", "normal")
    )

# Create tabs with shorter names for mobile
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "👥 Reps",
    "🔍 Pipeline",
    "📊 Sources"
])

with tab1:
    # Overview Tab
    st.markdown("### 👑 GenAI Commentary")
    st.markdown(summary)
    
    # Pipeline Attainment Metrics
    st.subheader("📈 Pipeline Creation & Attainment (QTD)")
    col1, col2, col3 = st.columns(3)
    
    try:
        # Calculate QTD metrics using filtered data
        pipeline_created_qtd = filtered_df['PipelineCreatedQTD'].sum()
        pipeline_target_qtd = filtered_df['PipelineTargetQTD'].sum()
        attainment_percentage = (pipeline_created_qtd / pipeline_target_qtd * 100) if pipeline_target_qtd > 0 else 0
        gap_to_target = pipeline_target_qtd - pipeline_created_qtd

        with col1:
            st.metric(
                "Pipeline Created QTD",
                f"${pipeline_created_qtd:,.0f}",
                f"vs Target: ${pipeline_target_qtd:,.0f}"
            )

        with col2:
            st.metric(
                "Attainment",
                f"{attainment_percentage:.1f}%",
                f"Gap: ${gap_to_target:,.0f}"
            )

        with col3:
            days_left_in_quarter = 90 - (datetime.now() - datetime.now().replace(day=1, month=((datetime.now().month-1)//3)*3+1)).days
            daily_target = gap_to_target / days_left_in_quarter if days_left_in_quarter > 0 else 0
            st.metric(
                "Daily Target to Goal",
                f"${daily_target:,.0f}",
                f"{days_left_in_quarter} days left"
            )
    except Exception as e:
        st.error(f"Error calculating pipeline attainment metrics: {str(e)}")
        for col in [col1, col2, col3]:
            with col:
                st.metric("No Data", "$0", "Error loading metrics")

with tab2:
    # Rep Performance Tab
    st.subheader("🎯 Percent-to-Plan and Rankings")
    
    try:
        # Calculate qualified pipeline per rep
        qualified_pipeline = filtered_df[filtered_df['Stage'] >= 3].groupby('Owner')['Amount'].sum().reset_index()
        qualified_pipeline.columns = ['Owner', 'QualifiedPipeQTD']
        
        # Get unique owners and their targets
        owner_targets = filtered_df.groupby('Owner')['PipelineTargetQTD'].first().reset_index()
        owner_targets.columns = ['Owner', 'Target']
        
        # Merge qualified pipeline with targets
        rankings_df = pd.merge(qualified_pipeline, owner_targets, on='Owner', how='left')
        
        # Calculate percent to plan
        rankings_df['PercentToPlan'] = (rankings_df['QualifiedPipeQTD'] / rankings_df['Target'] * 100).fillna(0)
        
        # Sort by percent to plan descending
        rankings_df = rankings_df.sort_values('PercentToPlan', ascending=False)
        
        # Format the columns
        rankings_df['QualifiedPipeQTD'] = rankings_df['QualifiedPipeQTD'].apply(lambda x: f"${x:,.0f}")
        rankings_df['Target'] = rankings_df['Target'].apply(lambda x: f"${x:,.0f}")
        rankings_df['PercentToPlan'] = rankings_df['PercentToPlan'].apply(lambda x: f"{x:.1f}%")
        
        # Add rank column
        rankings_df.insert(0, 'Rank', range(1, len(rankings_df) + 1))
        
        # Rename columns for display
        rankings_df.columns = ['Rank', 'Sales Rep', 'Qualified Pipeline', 'Target', 'Percent to Plan']
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            above_plan = (pd.to_numeric(rankings_df['Percent to Plan'].str.rstrip('%')) >= 100).sum()
            st.metric("Reps Above Plan", f"{above_plan}", f"{(above_plan/len(rankings_df))*100:.1f}% of team")
        
        with col2:
            avg_attainment = pd.to_numeric(rankings_df['Percent to Plan'].str.rstrip('%')).mean()
            st.metric("Average Attainment", f"{avg_attainment:.1f}%", "of target")
        
        with col3:
            median_attainment = pd.to_numeric(rankings_df['Percent to Plan'].str.rstrip('%')).median()
            st.metric("Median Attainment", f"{median_attainment:.1f}%", "of target")

        # Add conditional formatting styles
        def style_percent_to_plan(val):
            try:
                percent = float(val.rstrip('%'))
                if percent >= 100:
                    return 'background-color: #d4edda; color: #155724'
                elif percent >= 75:
                    return 'background-color: #fff3cd; color: #856404'
                else:
                    return 'background-color: #f8d7da; color: #721c24'
            except:
                return ''

        # Apply styling to the DataFrame
        styled_df = rankings_df.style.applymap(style_percent_to_plan, subset=['Percent to Plan'])

        # Display the rankings table
        st.dataframe(
            rankings_df,
            column_config={
                "Rank": st.column_config.NumberColumn(
                    "🏆 Rank",
                    help="Sales rep ranking based on percent to plan",
                    format="%d"
                ),
                "Sales Rep": st.column_config.TextColumn(
                    "👤 Sales Rep",
                    help="Name of the sales representative"
                ),
                "Qualified Pipeline": st.column_config.TextColumn(
                    "💰 Qualified Pipeline",
                    help="Total qualified pipeline (Stage 3+)"
                ),
                "Target": st.column_config.TextColumn(
                    "🎯 Target",
                    help="Sales target for the period"
                ),
                "Percent to Plan": st.column_config.ProgressColumn(
                    "📊 Percent to Plan",
                    help="Percentage of target achieved",
                    format="%.1f%%",
                    min_value=0,
                    max_value=200
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Add a download button for the rankings
        csv = rankings_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Rankings",
            data=csv,
            file_name="sales_rankings.csv",
            mime="text/csv"
        )

        # Top Performers Highlight
        st.subheader("🌟 Top Performers")
        top_3_df = rankings_df.head(3)
        
        cols = st.columns(3)
        for idx, (_, row) in enumerate(top_3_df.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                #### {['🥇', '🥈', '🥉'][idx]} {row['Sales Rep']}
                - Pipeline: {row['Qualified Pipeline']}
                - Target: {row['Target']}
                - Attainment: {row['Percent to Plan']}
                """)

        # Create a histogram of percent to plan distribution
        percent_to_plan_values = pd.to_numeric(rankings_df['Percent to Plan'].str.rstrip('%'))
        
        fig = px.histogram(
            percent_to_plan_values,
            nbins=10,
            title='Distribution of Percent to Plan',
            labels={'value': 'Percent to Plan', 'count': 'Number of Reps'},
        )
        fig.update_layout(
            xaxis_title="Percent to Plan",
            yaxis_title="Number of Reps",
            showlegend=False
        )
        fig.update_traces(
            hovertemplate="Percent to Plan: %{x:.1f}%<br>Number of Reps: %{y}"
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error calculating rankings: {str(e)}")
        st.write("Unable to display rankings. Please check your data and try again.")

with tab3:
    # Pipeline Analysis Tab
    st.subheader("📊 Pipeline Stage Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
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
        fig_stage.update_layout(
            height=300,  # Smaller height for mobile
            margin=dict(l=10, r=10, t=30, b=10),  # Reduced margins
            autosize=True  # Enable autosizing
        )
        st.plotly_chart(fig_stage, use_container_width=True)

    with col2:
        # Late Stage Pipeline Distribution
        late_stage_data = pd.DataFrame([
            {'Category': 'Late Stage', 'Amount': metrics['late_stage_pipeline']},
            {'Category': 'Early Stage', 'Amount': metrics['total_pipeline'] - metrics['late_stage_pipeline']}
        ])
        fig_late_stage = go.Figure(data=[go.Pie(
            labels=late_stage_data['Category'],
            values=late_stage_data['Amount'],
            hole=0.7,
            marker_colors=['#2ecc71', '#e74c3c']
        )])
        fig_late_stage.update_layout(
            title=f"Late Stage Pipeline: {metrics['late_stage_percentage']:.1f}%",
            annotations=[{
                'text': f"${metrics['late_stage_pipeline']:,.0f}",
                'x': 0.5,
                'y': 0.5,
                'font_size': 14,
                'showarrow': False
            }]
        )
        fig_late_stage.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            autosize=True
        )
        st.plotly_chart(fig_late_stage, use_container_width=True)
    
    # Stage 0 Pipeline Health
    st.subheader("🔍 Stage 0 Pipeline Health")
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Filter for Stage 0 opportunities
        stage0_df = filtered_df[filtered_df['Stage'] == 0]
        total_stage0 = stage0_df['Amount'].sum()
        avg_stage0_age = stage0_df['Stage0Age'].mean()
        aging_threshold = 51  # Days threshold for aging opportunities
        aging_stage0_count = stage0_df[stage0_df['Stage0Age'] > aging_threshold].shape[0]
        total_stage0_count = stage0_df.shape[0]
        
        with col1:
            st.metric(
                "Stage 0 Pipeline",
                f"${total_stage0:,.0f}",
                f"{total_stage0_count} Opportunities"
            )
        
        with col2:
            st.metric(
                "Average Age",
                f"{avg_stage0_age:.1f} days",
                "Time in Stage 0"
            )
        
        with col3:
            aging_percentage = (aging_stage0_count / total_stage0_count * 100) if total_stage0_count > 0 else 0
            st.metric(
                f"Aging (>{aging_threshold} days)",
                f"{aging_stage0_count}",
                f"{aging_percentage:.1f}% of Stage 0"
            )
        
        with col4:
            # Calculate the weekly trend
            stage0_weekly = stage0_df.groupby(pd.Grouper(key='CreatedDate', freq='W'))['Amount'].sum().reset_index()
            weekly_change = stage0_weekly['Amount'].pct_change().iloc[-1] if len(stage0_weekly) > 1 else 0
            st.metric(
                "Weekly Trend",
                f"${stage0_weekly['Amount'].iloc[-1]:,.0f}" if len(stage0_weekly) > 0 else "$0",
                f"{weekly_change*100:.1f}% WoW" if weekly_change != 0 else "No Change"
            )

        # Stage 0 Trend Over Time
        st.subheader("Stage 0 Pipeline Trend")
        stage0_trend = stage0_df.groupby('CreatedDate')['Amount'].sum().reset_index()
        fig_stage0_trend = px.line(
            stage0_trend,
            x='CreatedDate',
            y='Amount',
            title='Stage 0 Pipeline Over Time',
            labels={'Amount': 'Pipeline Amount ($)', 'CreatedDate': 'Date'}
        )
        fig_stage0_trend.update_layout(
            xaxis_title="Date",
            yaxis_title="Pipeline Amount ($)",
            showlegend=False
        )
        fig_stage0_trend.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            autosize=True
        )
        st.plotly_chart(fig_stage0_trend, use_container_width=True)

        # Stage 0 Age Distribution
        age_bins = [0, 15, 30, 45, 60, float('inf')]
        age_labels = ['0-15 days', '16-30 days', '31-45 days', '46-60 days', '60+ days']
        stage0_df['AgeGroup'] = pd.cut(stage0_df['Stage0Age'], bins=age_bins, labels=age_labels, right=False)
        age_distribution = stage0_df.groupby('AgeGroup')['Amount'].agg(['sum', 'count']).reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            # Age Distribution by Amount
            fig_age_amount = px.bar(
                age_distribution,
                x='AgeGroup',
                y='sum',
                title='Stage 0 Pipeline by Age Group',
                labels={'sum': 'Amount ($)', 'AgeGroup': 'Age Group'}
            )
            fig_age_amount.update_traces(texttemplate='$%{y:,.0f}', textposition='outside')
            st.plotly_chart(fig_age_amount, use_container_width=True)
        
        with col2:
            # Age Distribution by Count
            fig_age_count = px.bar(
                age_distribution,
                x='AgeGroup',
                y='count',
                title='Stage 0 Opportunity Count by Age Group',
                labels={'count': 'Number of Opportunities', 'AgeGroup': 'Age Group'}
            )
            fig_age_count.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig_age_count, use_container_width=True)

    except Exception as e:
        st.error(f"Error calculating Stage 0 metrics: {str(e)}")
        # Display empty metrics if there's an error
        for col in [col1, col2, col3, col4]:
            with col:
                st.metric("No Data", "$0", "Error loading metrics")

with tab4:
    # Source Analysis Tab
    st.subheader("📈 Pipeline Sources Analysis")
    
    # Add toggle for pipeline type
    pipeline_type = st.radio(
        "Select Pipeline Type",
        ["Qualified Pipeline", "Total Pipeline"],
        horizontal=True
    )

    col1, col2 = st.columns(2)

    with col1:
        # Calculate pipeline by source based on selection
        if pipeline_type == "Qualified Pipeline":
            source_pipeline = filtered_df.groupby('Source')['QualifiedPipeQTD'].sum().reset_index()
            value_col = 'QualifiedPipeQTD'
            title = 'Qualified Pipeline by Source'
        else:
            source_pipeline = filtered_df.groupby('Source')['Amount'].sum().reset_index()
            value_col = 'Amount'
            title = 'Total Pipeline by Source'
        
        source_pipeline = source_pipeline.sort_values(value_col, ascending=True)
        
        fig_source = px.bar(
            source_pipeline,
            x=value_col,
            y='Source',
            orientation='h',
            title=title,
            labels={value_col: 'Pipeline Amount ($)', 'Source': 'Source'},
        )
        
        fig_source.update_traces(
            texttemplate='$%{x:,.0f}',
            textposition='outside'
        )
        fig_source.update_layout(
            xaxis_title="Pipeline Amount ($)",
            yaxis_title="Source",
            showlegend=False
        )
        st.plotly_chart(fig_source, use_container_width=True)

    with col2:
        # Create a summary table with percentages
        total_amount = source_pipeline[value_col].sum()
        source_summary = source_pipeline.copy()
        source_summary['Percentage'] = (source_summary[value_col] / total_amount * 100)
        source_summary[value_col] = source_summary[value_col].apply(lambda x: f"${x:,.0f}")
        source_summary['Percentage'] = source_summary['Percentage'].apply(lambda x: f"{x:.1f}%")
        source_summary.columns = ['Source', 'Pipeline Amount', 'Percentage of Total']
        
        st.markdown("### Source Breakdown")
        st.dataframe(
            source_summary,
            column_config={
                "Source": st.column_config.TextColumn("Source"),
                "Pipeline Amount": st.column_config.TextColumn("Pipeline Amount"),
                "Percentage of Total": st.column_config.TextColumn("% of Total")
            },
            use_container_width=True
        )

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

# Sidebar with collapsible sections
st.sidebar.header("📊 Dashboard Controls")

# Collapsible filter section
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
        ]
    else:
        filtered_df = df

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