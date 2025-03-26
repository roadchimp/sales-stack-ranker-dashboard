"""
Overview tab component for Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Union
from utils.ai_commentary import generate_commentary

def display_overview_tab(metrics: Dict[str, Union[float, int]], filtered_df: pd.DataFrame) -> None:
    """
    Display the overview tab content.
    
    Args:
        metrics (Dict[str, Union[float, int]]): Dictionary of pipeline metrics
        filtered_df (pd.DataFrame): Filtered DataFrame based on user selection
    """
    # Generate and display AI commentary
    st.markdown("### 👑 GenAI Commentary")
    commentary = generate_commentary(metrics)
    st.markdown(commentary)
    
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