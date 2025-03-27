"""
AI commentary component for Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Union
from utils.ai_commentary import generate_commentary

def display_ai_commentary_tab(df: pd.DataFrame, metrics: Dict[str, Union[float, int]]) -> None:
    """
    Display the AI commentary tab content.
    
    Args:
        df (pd.DataFrame): Input DataFrame with pipeline data
        metrics (Dict[str, Union[float, int]]): Dictionary of pipeline metrics
    """
    st.header("AI-Generated Insights")
    
    # Add a refresh button
    if st.button("Refresh Insights"):
        st.session_state['commentary'] = None
    
    # Check if we have commentary in session state
    if 'commentary' not in st.session_state:
        st.session_state['commentary'] = None
    
    if st.session_state['commentary'] is None:
        with st.spinner("Generating insights..."):
            try:
                # Generate commentary
                commentary = generate_commentary(df, metrics)
                st.session_state['commentary'] = commentary
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
                st.session_state['commentary'] = "Unable to generate insights at this time."
    
    # Display the commentary
    st.markdown(st.session_state['commentary']) 