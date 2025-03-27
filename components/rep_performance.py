"""
Rep performance component for the Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

def display_rep_performance_tab(df: pd.DataFrame) -> None:
    """
    Display the rep performance tab with charts and metrics.
    
    Args:
        df: DataFrame containing pipeline data
    """
    if df.empty:
        st.warning("No data available for rep performance analysis.")
        return
    
    try:
        # Rep Performance Section
        st.subheader("Rep Performance")
        
        # Calculate rep metrics
        rep_metrics = df.groupby('Owner').agg({
            'Amount': ['sum', 'count', 'mean'],
            'Stage': lambda x: (x >= 3).mean(),  # Qualified pipeline percentage
            'CreatedDate': lambda x: (pd.Timestamp.now() - x).mean().days  # Average age
        }).reset_index()
        
        rep_metrics.columns = ['Rep', 'Total Amount', 'Deal Count', 'Avg Deal Size', 'Qualified %', 'Avg Age']
        
        # Display rep metrics table
        st.markdown("### Rep Metrics")
        st.dataframe(
            rep_metrics.style.format({
                'Total Amount': '${:,.2f}',
                'Deal Count': '{:,.0f}',
                'Avg Deal Size': '${:,.2f}',
                'Qualified %': '{:.1%}',
                'Avg Age': '{:.1f}'
            }),
            use_container_width=True
        )
        
        # Rep Pipeline Distribution
        st.subheader("Pipeline Distribution by Rep")
        
        # Create rep distribution DataFrame
        rep_df = pd.DataFrame({
            'Rep': rep_metrics['Rep'],
            'Amount': rep_metrics['Total Amount'],
            'Percentage': (rep_metrics['Total Amount'] / rep_metrics['Total Amount'].sum() * 100).round(1)
        })
        
        # Create bar chart with percentages
        fig = px.bar(
            rep_df,
            x='Rep',
            y=['Amount', 'Percentage'],
            barmode='group',
            title='Pipeline Distribution by Rep'
        )
        
        fig.update_layout(
            yaxis_title='Amount ($)',
            yaxis2=dict(title='Percentage (%)'),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Rep Performance by Stage
        st.subheader("Rep Performance by Stage")
        
        # Create stage distribution by rep
        stage_rep_df = pd.crosstab(df['Owner'], df['Stage'], values=df['Amount'], aggfunc='sum')
        
        # Create stacked bar chart
        fig = px.bar(
            stage_rep_df,
            title='Pipeline Distribution by Rep and Stage',
            barmode='stack'
        )
        
        fig.update_layout(
            xaxis_title='Rep',
            yaxis_title='Amount ($)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Rep Conversion Analysis
        st.subheader("Rep Conversion Analysis")
        
        # Calculate conversion metrics
        conversion_metrics = df.groupby('Owner').agg({
            'Stage': lambda x: (x == 4).mean()  # Win rate
        }).reset_index()
        
        conversion_metrics.columns = ['Rep', 'Win Rate']
        
        # Create conversion chart
        fig = px.bar(
            conversion_metrics,
            x='Rep',
            y='Win Rate',
            title='Win Rate by Rep'
        )
        
        fig.update_layout(
            yaxis_title='Win Rate',
            yaxis_tickformat='.1%',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Rep Pipeline Aging
        st.subheader("Rep Pipeline Aging")
        
        # Calculate aging metrics
        aging_metrics = df.groupby('Owner').agg({
            'CreatedDate': lambda x: (pd.Timestamp.now() - x).mean().days
        }).reset_index()
        
        aging_metrics.columns = ['Rep', 'Avg Age']
        
        # Create aging chart
        fig = px.bar(
            aging_metrics,
            x='Rep',
            y='Avg Age',
            title='Average Pipeline Age by Rep'
        )
        
        fig.update_layout(
            yaxis_title='Average Age (days)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error displaying rep performance: {str(e)}")
        st.write("Unable to display rep performance metrics. Please check your data and try again.") 