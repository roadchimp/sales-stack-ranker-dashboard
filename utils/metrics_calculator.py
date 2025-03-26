"""
Metrics calculation utilities for Sales Stack Ranker dashboard.
"""
import pandas as pd
from typing import Dict, Union, Any

def get_pipeline_metrics(df: pd.DataFrame) -> Dict[str, Union[float, int]]:
    """
    Calculate key pipeline metrics.
    
    Args:
        df (pd.DataFrame): Input DataFrame with pipeline data
        
    Returns:
        Dict[str, Union[float, int]]: Dictionary of calculated metrics
    """
    metrics = {
        'total_pipeline': 0.0,
        'qualified_pipeline': 0.0,
        'late_stage_pipeline': 0.0,
        'late_stage_percentage': 0.0,
        'avg_stage_0_age': 0.0,
        'pipeline_by_source': {}
    }
    
    if df.empty:
        return metrics
    
    try:
        # Calculate total pipeline
        metrics['total_pipeline'] = df['Amount'].sum()
        
        # Calculate qualified pipeline (Stage 2+)
        qualified_df = df[df['Stage'] >= 2]
        metrics['qualified_pipeline'] = qualified_df['Amount'].sum()
        
        # Calculate late stage pipeline (Stage 3+)
        late_stage_df = df[df['Stage'] >= 3]
        metrics['late_stage_pipeline'] = late_stage_df['Amount'].sum()
        
        # Calculate late stage percentage
        metrics['late_stage_percentage'] = (
            (metrics['late_stage_pipeline'] / metrics['total_pipeline'] * 100)
            if metrics['total_pipeline'] > 0 else 0.0
        )
        
        # Calculate Stage 0 metrics
        stage_0_df = df[df['Stage'] == 0]
        if not stage_0_df.empty:
            metrics['avg_stage_0_age'] = stage_0_df['Stage0Age'].mean()
        
        # Calculate pipeline by source
        metrics['pipeline_by_source'] = (
            df.groupby('Source')['Amount']
            .sum()
            .round(2)
            .to_dict()
        )
        
        # Round all numeric metrics for consistency
        for key in metrics:
            if isinstance(metrics[key], (float, int)):
                metrics[key] = round(float(metrics[key]), 2)
        
        return metrics
        
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return metrics 