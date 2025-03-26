"""
Source analysis component for Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Literal

def display_source_analysis_tab(filtered_df: pd.DataFrame) -> None:
    """
    Display the source analysis tab content.
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame based on user selection
    """
    st.subheader("📈 Pipeline Sources Analysis")
    
    try:
        # Add toggle for pipeline type
        pipeline_type: Literal["Qualified Pipeline", "Total Pipeline"] = st.radio(
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
                showlegend=False,
                height=300,
                margin=dict(l=10, r=10, t=30, b=10),
                autosize=True
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
    
    except Exception as e:
        st.error(f"Error analyzing pipeline sources: {str(e)}")
        st.write("Unable to display source analysis. Please check your data and try again.") 