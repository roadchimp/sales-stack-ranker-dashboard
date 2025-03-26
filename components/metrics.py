"""
Key metrics component for displaying important dashboard metrics.
"""
import streamlit as st
import pandas as pd

def display_key_metrics(metrics: dict, filtered_df: pd.DataFrame, late_stage_deals: pd.DataFrame, won_deals: pd.DataFrame):
    """
    Display the key metrics section of the dashboard.
    
    Args:
        metrics (dict): Dictionary containing calculated metrics
        filtered_df (pd.DataFrame): Filtered dataframe based on user selection
        late_stage_deals (pd.DataFrame): Deals in late stages
        won_deals (pd.DataFrame): Won deals
    """
    # Create columns for metrics
    cols = st.columns(4)
    
    # Define metrics with consistent styling
    metrics_data = [
        {
            "label": "Total Pipeline",
            "value": f"${metrics['total_pipeline']:,.0f}",
            "delta": f"{metrics['late_stage_percentage']:.1f}% Late Stage",
            "delta_color": "normal",
            "help": "Total value of all opportunities in the pipeline"
        },
        {
            "label": "Qualified Pipeline",
            "value": f"${metrics['qualified_pipeline']:,.0f}",
            "delta": f"{(metrics['qualified_pipeline']/metrics['total_pipeline']*100 if metrics['total_pipeline'] > 0 else 0):.1f}% of Total",
            "delta_color": "normal",
            "help": "Value of opportunities that have been qualified"
        },
        {
            "label": "Average Deal Size",
            "value": f"${filtered_df['Amount'].mean() if not filtered_df.empty else 0:,.0f}",
            "delta": "Per Opportunity",
            "delta_color": "off",
            "help": "Average value per opportunity in the pipeline"
        },
        {
            "label": "Late Stage Win Rate",
            "value": f"{(len(won_deals) / len(late_stage_deals) * 100 if len(late_stage_deals) > 0 else 0):.1f}%",
            "delta": "Stage 3+ Opportunities",
            "delta_color": "off",
            "help": "Percentage of late-stage opportunities that are won"
        }
    ]
    
    # Display metrics in columns
    for col, metric in zip(cols, metrics_data):
        with col:
            st.metric(
                label=metric["label"],
                value=metric["value"],
                delta=metric["delta"],
                delta_color=metric["delta_color"],
                help=metric["help"]
            ) 