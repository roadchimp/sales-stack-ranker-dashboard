"""
Data loading and validation utilities for Sales Stack Ranker dashboard.
"""
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, Any

def get_required_columns() -> Dict[str, Any]:
    """
    Get the required columns and their types for the dashboard.
    
    Returns:
        Dict[str, Any]: Dictionary of column names and their expected types
    """
    return {
        'OpportunityID': str,
        'Owner': str,
        'Role': str,
        'Region': str,
        'CreatedDate': 'datetime64[ns]',
        'CloseDate': 'datetime64[ns]',
        'Stage': int,
        'Amount': float,
        'Source': str,
        'LeadSourceCategory': str,
        'QualifiedPipeQTD': float,
        'LateStageAmount': float,
        'AvgAge': float,
        'Stage0Age': float,
        'Stage0Count': int,
        'PipelineCreatedQTD': float,
        'PipelineTargetQTD': float
    }

def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate the DataFrame against required columns and types.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        
    Raises:
        ValueError: If validation fails
    """
    required_columns = get_required_columns()
    
    # Check for missing columns
    missing_cols = set(required_columns.keys()) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Validate data types
    for col, expected_type in required_columns.items():
        try:
            if expected_type == 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(expected_type)
        except Exception as e:
            raise ValueError(f"Error converting column {col} to type {expected_type}: {str(e)}")
    
    # Validate value ranges
    if (df['Stage'] < 0).any() or (df['Stage'] > 4).any():
        raise ValueError("Stage must be between 0 and 4")
    
    if (df['Amount'] < 0).any():
        raise ValueError("Amount must be positive")

def load_csv_data(file) -> pd.DataFrame:
    """
    Load and validate data from a CSV file.
    
    Args:
        file: File-like object containing CSV data
        
    Returns:
        pd.DataFrame: Validated DataFrame
        
    Raises:
        ValueError: If data validation fails
    """
    try:
        df = pd.read_csv(file)
        validate_dataframe(df)
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV data: {str(e)}")

def load_data() -> pd.DataFrame:
    """
    Load sales data from CSV or generate synthetic data if file not found.
    
    Returns:
        pd.DataFrame: Sales data with required columns
    """
    try:
        df = pd.read_csv('data/sales_data.csv')
        return df
    except FileNotFoundError:
        # Generate synthetic data
        n_records = 100  # Increased to get better distribution
        
        # Generate random dates within current quarter
        quarter_start = pd.Timestamp(datetime.now()).to_period('Q').start_time
        dates = [quarter_start + timedelta(days=np.random.randint(0, 90)) for _ in range(n_records)]
        
        # List of sales reps
        sales_reps = [
            'Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Kim',
            'Rachel Thompson', 'James Wilson', 'Lisa Garcia', 'John Smith'
        ]
        
        # Generate stages with weighted distribution to ensure some closed won deals
        stage_weights = [0.2, 0.2, 0.3, 0.2, 0.1]  # 10% Closed Won
        stages = np.random.choice([0, 1, 2, 3, 4], size=n_records, p=stage_weights)
        
        # Generate amounts using log-normal distribution - higher mean for larger deals
        amounts = np.random.lognormal(mean=12.5, sigma=0.6, size=n_records)
        amounts = np.round(amounts, -3)  # Round to nearest thousand
        
        # Generate targets that are challenging but achievable
        # Base target should be achievable with about 8-10 closed deals
        base_target = 1000000  # $1M base target
        rep_targets = {rep: base_target * (0.8 + 0.4 * np.random.random()) for rep in sales_reps}
        
        # Create the DataFrame
        df = pd.DataFrame({
            'OpportunityID': [f'OPP-{i:04d}' for i in range(n_records)],
            'Owner': np.random.choice(sales_reps, size=n_records),
            'Role': 'Sales Representative',
            'Region': np.random.choice(['North', 'South', 'East', 'West'], size=n_records),
            'CreatedDate': dates,
            'CloseDate': [d + timedelta(days=np.random.randint(30, 120)) for d in dates],
            'Stage': stages,
            'Amount': amounts,
            'Source': np.random.choice(['Inbound', 'Outbound', 'Partner', 'Referral'], size=n_records),
            'LeadSourceCategory': np.random.choice(['Marketing', 'Sales', 'Partner'], size=n_records)
        })
        
        # Add derived columns
        df['QualifiedPipeQTD'] = df[df['Stage'] >= 2]['Amount']
        df['LateStageAmount'] = df[df['Stage'] >= 3]['Amount']
        df['AvgAge'] = np.random.randint(15, 60, size=n_records)
        df['Stage0Age'] = np.where(df['Stage'] == 0, df['AvgAge'], 0)
        df['Stage0Count'] = (df['Stage'] == 0).astype(int)
        df['PipelineCreatedQTD'] = df['Amount']
        
        # Add target amount for each rep
        df['PipelineTargetQTD'] = df['Owner'].map(rep_targets)
        
        # Validate the data
        total_deals = len(df)
        closed_won_deals = len(df[df['Stage'] == 4])
        avg_deal_size = df['Amount'].mean()
        print(f"Generated {total_deals} total deals, {closed_won_deals} closed won")
        print(f"Average deal size: ${avg_deal_size:,.0f}")
        
        return df 