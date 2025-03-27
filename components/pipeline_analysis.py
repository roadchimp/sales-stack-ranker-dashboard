"""
Pipeline analysis component for the Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

def display_pipeline_analysis_tab(df: pd.DataFrame, metrics: Dict[str, Any]) -> None:
    """
    Display the pipeline analysis tab with charts and metrics.
    
    Args:
        df: DataFrame containing pipeline data
        metrics: Dictionary containing calculated metrics
    """
    if df.empty:
        st.warning("No data available for pipeline analysis.")
        return
    
    # Pipeline Health Section
    st.subheader("Pipeline Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Qualified Pipeline",
            f"${metrics['qualified_pipeline']:,.2f}"
        )
    
    with col2:
        st.metric(
            "Win Rate",
            f"{metrics['win_rate']:.1%}"
        )
    
    with col3:
        st.metric(
            "Pipeline Velocity",
            f"{metrics['pipeline_velocity']:.1f} days"
        )
    
    # Stage Distribution Chart
    st.subheader("Pipeline Distribution by Stage")
    
    # Create stage distribution DataFrame
    stage_df = pd.DataFrame({
        'Stage': list(metrics['stage_distribution'].keys()),
        'Amount': list(metrics['stage_distribution'].values())
    })
    
    # Calculate percentages
    total_amount = stage_df['Amount'].sum()
    stage_df['Percentage'] = (stage_df['Amount'] / total_amount * 100).round(1)
    
    # Create bar chart with percentages
    fig = px.bar(
        stage_df,
        x='Stage',
        y=['Amount', 'Percentage'],
        barmode='group',
        title='Pipeline Distribution by Stage'
    )
    
    fig.update_layout(
        yaxis_title='Amount ($)',
        yaxis2_title='Percentage (%)',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Source Distribution Chart
    st.subheader("Pipeline Distribution by Source")
    
    # Create source distribution DataFrame
    source_df = pd.DataFrame({
        'Source': list(metrics['source_distribution'].keys()),
        'Amount': list(metrics['source_distribution'].values())
    })
    
    # Calculate percentages
    total_amount = source_df['Amount'].sum()
    source_df['Percentage'] = (source_df['Amount'] / total_amount * 100).round(1)
    
    # Create pie chart
    fig = px.pie(
        source_df,
        values='Amount',
        names='Source',
        title='Pipeline Distribution by Source'
    )
    
    fig.update_traces(textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Pipeline Aging Analysis
    st.subheader("Pipeline Aging Analysis")
    
    # Calculate days in pipeline
    df['DaysInPipeline'] = (pd.Timestamp.now() - df['CreatedDate']).dt.days
    
    # Create aging distribution chart
    fig = px.histogram(
        df,
        x='DaysInPipeline',
        nbins=30,
        title='Pipeline Aging Distribution'
    )
    
    fig.update_layout(
        xaxis_title='Days in Pipeline',
        yaxis_title='Number of Opportunities'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display aging statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Average Age",
            f"{df['DaysInPipeline'].mean():.1f} days"
        )
    
    with col2:
        st.metric(
            "Median Age",
            f"{df['DaysInPipeline'].median():.1f} days"
        ) 