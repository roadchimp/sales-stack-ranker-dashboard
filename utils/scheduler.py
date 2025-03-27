"""
Scheduler module for automated email tasks in Sales Stack Ranker dashboard.
"""
import schedule
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Union
from utils.email_utils import send_digest, send_alert
from utils.data_loader import load_data
from utils.metrics_calculator import get_pipeline_metrics

def check_pipeline_drop(df: pd.DataFrame, threshold: float = 1000000) -> Dict[str, Union[float, int]]:
    """
    Check if pipeline has dropped below threshold.
    
    Args:
        df (pd.DataFrame): Pipeline data
        threshold (float): Minimum pipeline value threshold
        
    Returns:
        Dict[str, Union[float, int]]: Alert data if threshold is breached
    """
    metrics = get_pipeline_metrics(df)
    if metrics['total_pipeline'] < threshold:
        return {
            'current_value': metrics['total_pipeline'],
            'previous_value': metrics.get('previous_total_pipeline', 0),
            'drop_percentage': ((metrics['total_pipeline'] - metrics.get('previous_total_pipeline', 0)) 
                              / metrics.get('previous_total_pipeline', 1) * 100)
        }
    return None

def check_aging_opportunities(df: pd.DataFrame, threshold: int = 30) -> Dict[str, Union[float, int]]:
    """
    Check for opportunities aging beyond threshold.
    
    Args:
        df (pd.DataFrame): Pipeline data
        threshold (int): Age threshold in days
        
    Returns:
        Dict[str, Union[float, int]]: Alert data if threshold is breached
    """
    stage0_df = df[df['Stage'] == 0].copy()
    aging_count = len(stage0_df[stage0_df['Stage0Age'] > threshold])
    
    if aging_count > 0:
        return {
            'count': aging_count,
            'total_stage0': len(stage0_df),
            'avg_age': stage0_df['Stage0Age'].mean()
        }
    return None

def check_rep_performance(df: pd.DataFrame, threshold: float = 0.7) -> Dict[str, Union[float, int]]:
    """
    Check for reps below performance threshold.
    
    Args:
        df (pd.DataFrame): Pipeline data
        threshold (float): Minimum performance threshold (0-1)
        
    Returns:
        Dict[str, Union[float, int]]: Alert data if threshold is breached
    """
    rep_metrics = df.groupby('Owner').agg({
        'QualifiedPipeQTD': 'sum',
        'PipelineTargetQTD': 'first'
    }).reset_index()
    
    rep_metrics['PercentToPlan'] = rep_metrics['QualifiedPipeQTD'] / rep_metrics['PipelineTargetQTD']
    underperforming = rep_metrics[rep_metrics['PercentToPlan'] < threshold]
    
    if not underperforming.empty:
        return {
            'count': len(underperforming),
            'reps': underperforming['Owner'].tolist(),
            'min_performance': underperforming['PercentToPlan'].min()
        }
    return None

def send_daily_digest():
    """Send daily pipeline digest email."""
    try:
        # Load data
        df = load_data()
        
        # Calculate date range
        today = datetime.now()
        start_date = today - timedelta(days=7)
        
        # Filter data for the last 7 days
        filtered_df = df[df['CreatedDate'].dt.date >= start_date.date()].copy()
        
        # Calculate metrics
        metrics = get_pipeline_metrics(filtered_df)
        
        # Get rep performance
        rep_performance = filtered_df.groupby('Owner').agg({
            'QualifiedPipeQTD': 'sum',
            'PipelineTargetQTD': 'first'
        }).reset_index()
        
        rep_performance['PercentToPlan'] = (
            rep_performance['QualifiedPipeQTD'] / rep_performance['PipelineTargetQTD'] * 100
        )
        
        # Get pipeline health metrics
        pipeline_health = {
            'avg_stage_0_age': filtered_df[filtered_df['Stage'] == 0]['Stage0Age'].mean(),
            'stage_0_count': len(filtered_df[filtered_df['Stage'] == 0])
        }
        
        # Send digest
        send_digest(
            metrics=metrics,
            rep_performance=rep_performance,
            pipeline_health=pipeline_health,
            date_range=(start_date.date(), today.date())
        )
        
    except Exception as e:
        print(f"Error sending daily digest: {str(e)}")

def check_alerts():
    """Check and send alerts for various conditions."""
    try:
        # Load data
        df = load_data()
        
        # Check pipeline drop
        pipeline_drop = check_pipeline_drop(df)
        if pipeline_drop:
            send_alert(
                alert_type='pipeline_drop',
                alert_data=pipeline_drop,
                threshold=1000000
            )
        
        # Check aging opportunities
        aging_opps = check_aging_opportunities(df)
        if aging_opps:
            send_alert(
                alert_type='aging_opportunities',
                alert_data=aging_opps,
                threshold=30
            )
        
        # Check rep performance
        rep_perf = check_rep_performance(df)
        if rep_perf:
            send_alert(
                alert_type='rep_performance',
                alert_data=rep_perf,
                threshold=0.7
            )
            
    except Exception as e:
        print(f"Error checking alerts: {str(e)}")

def start_scheduler():
    """Start the email scheduler."""
    # Schedule daily digest at 9 AM
    schedule.every().day.at("09:00").do(send_daily_digest)
    
    # Schedule alert checks every 4 hours
    schedule.every(4).hours.do(check_alerts)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler() 