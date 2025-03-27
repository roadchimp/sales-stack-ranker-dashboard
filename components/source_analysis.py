"""
Source analysis component for the Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

def display_source_analysis_tab(df: pd.DataFrame) -> None:
    """
    Display the source analysis tab with charts and metrics.
    
    Args:
        df: DataFrame containing pipeline data
    """
    if df.empty:
        st.warning("No data available for source analysis.")
        return
    
    # Source Performance Section
    st.subheader("Source Performance")
    
    # Helper functions for Stage analysis
    def is_qualified(stage):
        if isinstance(stage, (int, float)):
            return stage >= 3
        if isinstance(stage, str):
            return stage.lower() in ['closed won', 'closed lost']
        return False
        
    def is_won(stage):
        if isinstance(stage, (int, float)):
            return stage == 4
        if isinstance(stage, str):
            return stage.lower() == 'closed won'
        return False
    
    # Calculate source metrics
    source_metrics = df.groupby('Source').agg({
        'Amount': ['sum', 'count', 'mean'],
        'Stage': lambda x: x.apply(is_qualified).mean()  # Qualified pipeline percentage
    }).reset_index()
    
    source_metrics.columns = ['Source', 'Total Amount', 'Deal Count', 'Avg Deal Size', 'Qualified %']
    
    # Display source metrics table
    st.markdown("### Source Metrics")
    st.dataframe(
        source_metrics.style.format({
            'Total Amount': '${:,.2f}',
            'Deal Count': '{:,.0f}',
            'Avg Deal Size': '${:,.2f}',
            'Qualified %': '{:.1%}'
        }),
        use_container_width=True
    )
    
    # Source Distribution Chart
    st.subheader("Pipeline Distribution by Source")
    
    # Create source distribution DataFrame
    source_df = pd.DataFrame({
        'Source': source_metrics['Source'],
        'Amount': source_metrics['Total Amount'],
        'Percentage': (source_metrics['Total Amount'] / source_metrics['Total Amount'].sum() * 100).round(1)
    })
    
    # Create bar chart with percentages
    fig = px.bar(
        source_df,
        x='Source',
        y=['Amount', 'Percentage'],
        barmode='group',
        title='Pipeline Distribution by Source'
    )
    
    fig.update_layout(
        yaxis_title='Amount ($)',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Source Performance by Stage
    st.subheader("Source Performance by Stage")
    
    # Create stage distribution by source
    stage_source_df = pd.crosstab(df['Source'], df['Stage'], values=df['Amount'], aggfunc='sum')
    
    # Create stacked bar chart
    fig = px.bar(
        stage_source_df,
        title='Pipeline Distribution by Source and Stage'
    )
    
    fig.update_layout(
        xaxis_title='Source',
        yaxis_title='Amount ($)',
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Source Conversion Analysis
    st.subheader("Source Conversion Analysis")
    
    # Calculate conversion metrics
    conversion_metrics = df.groupby('Source').agg({
        'Stage': lambda x: x.apply(is_won).mean()  # Win rate
    }).reset_index()
    
    conversion_metrics.columns = ['Source', 'Win Rate']
    
    # Create conversion chart
    fig = px.bar(
        conversion_metrics,
        x='Source',
        y='Win Rate',
        title='Win Rate by Source'
    )
    
    fig.update_layout(
        yaxis_title='Win Rate',
        yaxis_tickformat='.1%'
    )
    
    st.plotly_chart(fig, use_container_width=True) 