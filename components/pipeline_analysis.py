"""
Pipeline analysis component for Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Union

def display_pipeline_analysis_tab(filtered_df: pd.DataFrame, metrics: Dict[str, Union[float, int]]) -> None:
    """
    Display the pipeline analysis tab content.
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame based on user selection
        metrics (Dict[str, Union[float, int]]): Dictionary of pipeline metrics
    """
    st.subheader("📊 Pipeline Stage Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Stage Distribution
        if not filtered_df.empty:
            stage_counts = filtered_df['Stage'].value_counts().sort_index()
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
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            autosize=True
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
            }],
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
            showlegend=False,
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
            fig_age_amount.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=30, b=10),
                autosize=True
            )
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
            fig_age_count.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=30, b=10),
                autosize=True
            )
            st.plotly_chart(fig_age_count, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error calculating Stage 0 metrics: {str(e)}")
        # Display empty metrics if there's an error
        for col in [col1, col2, col3, col4]:
            with col:
                st.metric("No Data", "$0", "Error loading metrics") 