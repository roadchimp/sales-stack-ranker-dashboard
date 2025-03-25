import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_synthetic_data(n_records=100):
    """Generate synthetic sales pipeline data for testing."""
    np.random.seed(42)
    
    # Define possible values
    owners = ['Alice Smith', 'Bob Jones', 'Carol White', 'David Brown', 'Emma Wilson']
    regions = ['West', 'Midwest', 'East', 'South']
    stages = [0, 1, 2, 3, 4]  # 0: Prospecting, 1: Qualification, 2: Proposal, 3: Negotiation, 4: Closed Won
    sources = ['Rep', 'Marketing', 'Partner', 'Website']
    
    # Generate data
    data = {
        'OpportunityID': range(1, n_records + 1),
        'Owner': np.random.choice(owners, n_records),
        'Region': np.random.choice(regions, n_records),
        'CreatedDate': [(datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d') 
                       for _ in range(n_records)],
        'CloseDate': [(datetime.now() + timedelta(days=np.random.randint(30, 365))).strftime('%Y-%m-%d') 
                     for _ in range(n_records)],
        'Stage': np.random.choice(stages, n_records),
        'Amount': np.random.randint(10000, 500000, n_records),
        'Source': np.random.choice(sources, n_records)
    }
    
    return pd.DataFrame(data)

def load_data():
    """Load data from CSV if exists, otherwise generate synthetic data."""
    if os.path.exists('data/sales_pipeline.csv'):
        df = pd.read_csv('data/sales_pipeline.csv')
    else:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        df = generate_synthetic_data()
        df.to_csv('data/sales_pipeline.csv', index=False)
    
    # Convert date columns to datetime
    df['CreatedDate'] = pd.to_datetime(df['CreatedDate'])
    df['CloseDate'] = pd.to_datetime(df['CloseDate'])
    
    return df

def get_pipeline_metrics(df):
    """Calculate key pipeline metrics."""
    metrics = {
        'total_pipeline': df['Amount'].sum(),
        'late_stage_pipeline': df[df['Stage'].isin([3, 4])]['Amount'].sum(),
        'late_stage_percentage': (df[df['Stage'].isin([3, 4])]['Amount'].sum() / df['Amount'].sum()) * 100,
        'qualified_pipeline': df[df['Stage'].isin([2, 3, 4])]['Amount'].sum(),
        'stage_0_pipeline': df[df['Stage'] == 0]['Amount'].sum(),
        'stage_0_count': len(df[df['Stage'] == 0]),
        'avg_stage_0_age': (datetime.now() - df[df['Stage'] == 0]['CreatedDate']).mean().days
    }
    
    # Calculate pipeline by source
    pipeline_by_source = df.groupby('Source')['Amount'].sum().to_dict()
    metrics['pipeline_by_source'] = pipeline_by_source
    
    # Calculate rep rankings
    rep_rankings = df.groupby('Owner').agg({
        'Amount': ['sum', 'count'],
        'Stage': lambda x: (x >= 2).mean() * 100  # Percentage of qualified opportunities
    }).round(2)
    rep_rankings.columns = ['Total Pipeline', 'Opportunity Count', 'Qualification Rate']
    rep_rankings = rep_rankings.sort_values('Total Pipeline', ascending=False)
    metrics['rep_rankings'] = rep_rankings
    
    return metrics 