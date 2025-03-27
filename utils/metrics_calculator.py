"""
Metrics calculation utilities for Sales Stack Ranker dashboard.
"""
import pandas as pd
from typing import Dict, Union, Any
from datetime import datetime, timedelta

def get_pipeline_metrics(df: pd.DataFrame) -> Dict[str, Union[float, int]]:
    """
    Calculate key pipeline metrics.
    
    Args:
        df (pd.DataFrame): Input DataFrame with pipeline data
        
    Returns:
        Dict[str, Union[float, int]]: Dictionary of calculated metrics
    """
    if df.empty:
        return {
            'total_pipeline': 0,
            'qualified_pipeline': 0,
            'late_stage_amount': 0,
            'win_rate': 0,
            'avg_deal_size': 0,
            'pipeline_velocity': 0
        }
    
    try:
        # Calculate total pipeline
        total_pipeline = df['Amount'].sum()
        
        # Calculate qualified pipeline (stages 2-4)
        qualified_pipeline = df[df['Stage'] >= 2]['Amount'].sum()
        
        # Calculate late stage amount (stages 3-4)
        late_stage_amount = df[df['Stage'] >= 3]['Amount'].sum()
        
        # Calculate win rate (stage 4 deals / total deals)
        total_deals = len(df)
        won_deals = len(df[df['Stage'] == 4])
        win_rate = won_deals / total_deals if total_deals > 0 else 0
        
        # Calculate average deal size
        avg_deal_size = df['Amount'].mean() if not df.empty else 0
        
        # Calculate pipeline velocity (average days in pipeline)
        pipeline_velocity = df['AvgAge'].mean() if not df.empty else 0
        
        # Calculate late stage percentage
        late_stage_percentage = (
            (late_stage_amount / total_pipeline * 100)
            if total_pipeline > 0 else 0.0
        )
        
        # Calculate Stage 0 metrics
        stage_0_df = df[df['Stage'] == 0]
        if not stage_0_df.empty:
            avg_stage_0_age = stage_0_df['Stage0Age'].mean()
        
        # Calculate pipeline by source
        pipeline_by_source = (
            df.groupby('Source')['Amount']
            .sum()
            .round(2)
            .to_dict()
        )
        
        # Round all numeric metrics for consistency
        for key in [total_pipeline, qualified_pipeline, late_stage_amount, win_rate, avg_deal_size, pipeline_velocity, late_stage_percentage, avg_stage_0_age]:
            if isinstance(key, (float, int)):
                key = round(float(key), 2)
        
        return {
            'total_pipeline': total_pipeline,
            'qualified_pipeline': qualified_pipeline,
            'late_stage_amount': late_stage_amount,
            'win_rate': win_rate,
            'avg_deal_size': avg_deal_size,
            'pipeline_velocity': pipeline_velocity,
            'late_stage_percentage': late_stage_percentage,
            'avg_stage_0_age': avg_stage_0_age,
            'pipeline_by_source': pipeline_by_source
        }
        
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return {
            'total_pipeline': 0,
            'qualified_pipeline': 0,
            'late_stage_amount': 0,
            'win_rate': 0,
            'avg_deal_size': 0,
            'pipeline_velocity': 0
        } 