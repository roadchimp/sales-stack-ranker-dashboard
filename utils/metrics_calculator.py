"""
Utility functions for calculating pipeline metrics.
"""
import pandas as pd
from typing import Dict, Any

def get_pipeline_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate key pipeline metrics from the DataFrame.
    
    Args:
        df: DataFrame containing pipeline data
        
    Returns:
        Dictionary containing calculated metrics
    """
    if df.empty:
        return {
            'total_pipeline': 0,
            'qualified_pipeline': 0,
            'win_rate': 0,
            'avg_deal_size': 0,
            'pipeline_velocity': 0,
            'late_stage_amount': 0,
            'stage_distribution': {},
            'source_distribution': {}
        }
    
    # Calculate total pipeline
    total_pipeline = df['Amount'].sum()
    
    # Calculate qualified pipeline (stages 3 and 4)
    qualified_pipeline = df[df['Stage'] >= 3]['Amount'].sum()
    
    # Calculate win rate (stage 4 deals / total deals)
    total_deals = len(df)
    won_deals = len(df[df['Stage'] == 4])
    win_rate = won_deals / total_deals if total_deals > 0 else 0
    
    # Calculate average deal size
    avg_deal_size = df['Amount'].mean() if not df.empty else 0
    
    # Calculate pipeline velocity (average days in pipeline)
    df['DaysInPipeline'] = (pd.Timestamp.now() - df['CreatedDate']).dt.days
    pipeline_velocity = df['DaysInPipeline'].mean() if not df.empty else 0
    
    # Calculate late stage amount (stages 3 and 4)
    late_stage_amount = df[df['Stage'] >= 3]['Amount'].sum()
    
    # Calculate stage distribution
    stage_distribution = df.groupby('Stage')['Amount'].sum().to_dict()
    
    # Calculate source distribution
    source_distribution = df.groupby('Source')['Amount'].sum().to_dict()
    
    return {
        'total_pipeline': total_pipeline,
        'qualified_pipeline': qualified_pipeline,
        'win_rate': win_rate,
        'avg_deal_size': avg_deal_size,
        'pipeline_velocity': pipeline_velocity,
        'late_stage_amount': late_stage_amount,
        'stage_distribution': stage_distribution,
        'source_distribution': source_distribution
    } 