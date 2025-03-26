import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_pipeline_metrics, load_csv_data, get_required_columns
import pandas as pd
from datetime import datetime
import openai

# Initialize OpenAI client with just the API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_commentary(summary_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an insightful sales analytics expert providing concise commentary on sales data."},
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
        st.session_state.df = df
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
        st.sidebar.error(f"⚠️ Error in uploaded CSV: {str(e)}")
        if st.session_state.df.empty:
            st.session_state.df = load_data()
    except Exception as e:
        st.sidebar.error(f"⚠️ Unexpected error: {str(e)}")
        if st.session_state.df.empty:
            st.session_state.df = load_data()

# Use the session state DataFrame
df = st.session_state.df

# Calculate metrics (with error handling)
try:
    metrics = get_pipeline_metrics(df)
except Exception as e:
    st.error(f"Error calculating metrics: {str(e)}")
    metrics = get_pipeline_metrics(pd.DataFrame(columns=get_required_columns().keys()))

# Generate Summary for Commentary
summary_text = f"""
Pipeline Summary:
- Total Pipeline: ${df['Amount'].sum():,.0f}
- Qualified Pipeline QTD: ${df['QualifiedPipeQTD'].sum():,.0f}
- Late Stage Pipeline: ${df['LateStageAmount'].sum():,.0f}
- Average Stage 0 Age: {df['Stage0Age'].mean():.2f} days
- Pipeline Created QTD: ${df['PipelineCreatedQTD'].sum():,.0f}
- Pipeline Target QTD: ${df['PipelineTargetQTD'].sum():,.0f}
- Pipeline Attainment: {(df['PipelineCreatedQTD'].sum() / df['PipelineTargetQTD'].sum() * 100 if df['PipelineTargetQTD'].sum() > 0 else 0):.1f}%

Please provide a clear, concise analysis of these metrics, focusing on key insights and potential areas for attention. Format the response in clear paragraphs with proper spacing using consistent fonts and avoiding italics.
"""

if st.button("✨ Generate AI Commentary"):
    try:
        commentary = generate_commentary(summary_text)
        st.markdown("""
        **🤖 GenAI Commentary:**
        
        {}
        """.format(commentary))
    except Exception as e:
        st.error(f"Error generating commentary: {str(e)}")

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
        # Calculate daily run rate needed
        days_left_in_quarter = 90 - (datetime.now() - datetime.now().replace(day=1, month=((datetime.now().month-1)//3)*3+1)).days
        daily_target = gap_to_target / days_left_in_quarter if days_left_in_quarter > 0 else 0
        st.metric(
            "Daily Target to Goal",
            f"${daily_target:,.0f}",
            f"{days_left_in_quarter} days left"
        )

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

except Exception as e:
    st.error(f"Error calculating pipeline attainment metrics: {str(e)}")
    # Display empty metrics if there's an error
    for col in [col1, col2, col3]:
        with col:
            st.metric("No Data", "$0", "Error loading metrics")

# Pipeline by Source and Stage Distribution
col1, col2, col3 = st.columns(3)

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

with col3:
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
    st.plotly_chart(fig_late_stage, use_container_width=True)

# Qualified Pipeline by Source
st.subheader("📊 Qualified Pipeline by Source")
col1, col2 = st.columns(2)

with col1:
    # Calculate qualified pipeline by source
    qualified_by_source = filtered_df.groupby('Source')['QualifiedPipeQTD'].sum().reset_index()
    qualified_by_source = qualified_by_source.sort_values('QualifiedPipeQTD', ascending=True)  # Sort for better visualization
    
    fig_qualified_source = px.bar(
        qualified_by_source,
        x='QualifiedPipeQTD',
        y='Source',
        orientation='h',  # Horizontal bars
        title='Qualified Pipeline by Source',
        labels={'QualifiedPipeQTD': 'Qualified Pipeline ($)', 'Source': 'Source'},
    )
    
    # Customize the layout
    fig_qualified_source.update_traces(
        texttemplate='$%{x:,.0f}',
        textposition='outside'
    )
    fig_qualified_source.update_layout(
        xaxis_title="Qualified Pipeline ($)",
        yaxis_title="Source",
        showlegend=False
    )
    st.plotly_chart(fig_qualified_source, use_container_width=True)

with col2:
    # Create a summary table with percentages
    total_qualified = qualified_by_source['QualifiedPipeQTD'].sum()
    qualified_summary = qualified_by_source.copy()
    qualified_summary['Percentage'] = (qualified_summary['QualifiedPipeQTD'] / total_qualified * 100)
    qualified_summary['QualifiedPipeQTD'] = qualified_summary['QualifiedPipeQTD'].apply(lambda x: f"${x:,.0f}")
    qualified_summary['Percentage'] = qualified_summary['Percentage'].apply(lambda x: f"{x:.1f}%")
    qualified_summary.columns = ['Source', 'Qualified Pipeline', 'Percentage of Total']
    
    st.markdown("### Source Breakdown")
    st.dataframe(
        qualified_summary,
        column_config={
            "Source": st.column_config.TextColumn("Source"),
            "Qualified Pipeline": st.column_config.TextColumn("Qualified Pipeline"),
            "Percentage of Total": st.column_config.TextColumn("% of Total")
        },
        use_container_width=True
    )

# Pipe Health & Stage 0 Detail Table
st.header("🚦 Pipe Health and Stage 0 Detail")
pipe_health_cols = ['Owner', 'Role', 'Amount', 'LateStageAmount', 'AvgAge', 'Stage0Count', 'Stage0Age']
pipe_health_df = df[pipe_health_cols].groupby(['Owner', 'Role']).agg({
    'Amount': 'sum',
    'LateStageAmount': 'sum',
    'AvgAge': 'mean',
    'Stage0Count': 'sum',
    'Stage0Age': 'mean'
}).round(2).reset_index()
pipe_health_df = pipe_health_df.sort_values('Amount', ascending=False)
st.dataframe(pipe_health_df, use_container_width=True)

# Rep Rankings (Qualified Pipe This Quarter)
st.subheader("Rep Rankings (Qualified Pipe This Quarter)")
rep_ranking = df.groupby(['Owner', 'Role'])['QualifiedPipeQTD'].sum().reset_index()
rep_ranking = rep_ranking.sort_values('QualifiedPipeQTD', ascending=False).reset_index(drop=True)
rep_ranking.index += 1  # Start rank from 1
st.dataframe(rep_ranking.rename_axis('Rank').reset_index(), use_container_width=True)

# QTD Pipe Qualification By Lead Source
st.header("📈 QTD Pipe Qualification By Lead Source")
pipe_by_leadsource = df.groupby('LeadSourceCategory')['QualifiedPipeQTD'].sum().reset_index()
fig_leadsource = px.bar(
    pipe_by_leadsource,
    x='LeadSourceCategory',
    y='QualifiedPipeQTD',
    title='Qualified Pipeline by Lead Source Category',
    labels={'LeadSourceCategory': 'Lead Source', 'QualifiedPipeQTD': 'Qualified Pipeline'}
)
st.plotly_chart(fig_leadsource, use_container_width=True)

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