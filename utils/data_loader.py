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
        'Stage': object,  # Changed from int to object to support both numeric and string values
        'Amount': float,
        'Source': str,
        'LeadSourceCategory': str
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
        if col == 'Stage':  # Special handling for Stage column
            continue  # Skip standard conversion, we'll handle Stage specially below
        try:
            if expected_type == 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(expected_type)
        except Exception as e:
            raise ValueError(f"Error converting column {col} to type {expected_type}: {str(e)}")
    
    # Normalize Stage column to handle both numeric and string values
    def normalize_stage(s):
        # Try to convert to integer first
        try:
            return int(s)
        except (ValueError, TypeError):
            # If not convertible to int, keep as string
            return str(s)
    
    df['Stage'] = df['Stage'].apply(normalize_stage)
    
    # Validate Amount (must be positive)
    if (df['Amount'] < 0).any():
        raise ValueError("Amount must be positive")

def recalc_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recalculate derived fields for each opportunity based on Owner.

    Derived Fields:
    - QualifiedPipeQTD: Sum of Amount for opportunities where stage is numeric and > 3 or stage is 'closed won'
    - LateStageAmount: Sum of Amount for opportunities where stage is numeric and >= 3 or stage is 'closed lost' (excluding 'closed won')
    - AvgAge: Average of (CloseDate - CreatedDate) in days, excluding opportunities with stage 'closed lost'
    - Stage0Count: Count of opportunities where stage is 0 (numeric 0 or string '0')
    - Stage0Age: Average age (in days) for opportunities with stage = 0
    - PipelineCreatedQTD: Sum of Amount for opportunities created in the current quarter
    - PipelineTargetQTD: 120% of PipelineCreatedQTD

    Returns:
        pd.DataFrame: DataFrame with new derived columns merged in
    """
    df = df.copy()
    # Compute age in days
    df['AgeDays'] = (df['CloseDate'] - df['CreatedDate']).dt.days

    # Normalize Stage: if convertible to float, use numeric; otherwise, use lower-case string
    def normalize_stage(s):
        try:
            return float(s)
        except Exception:
            return str(s).strip().lower()

    df['stage_norm'] = df['Stage'].apply(normalize_stage)

    # Determine current quarter start date
    now = pd.Timestamp.now()
    quarter = now.quarter
    year = now.year
    quarter_start = pd.Timestamp(year=year, month=3*(quarter-1)+1, day=1)

    # QualifiedPipeQTD: include if (numeric and > 3) OR (string equals 'closed won')
    qualified_mask = df['stage_norm'].apply(lambda x: (isinstance(x, float) and x > 3) or (isinstance(x, str) and x == 'closed won'))
    qpipe = df[qualified_mask].groupby('Owner')['Amount'].sum()

    # LateStageAmount: include if (numeric and >= 3) OR (string equals 'closed lost')
    late_mask = df['stage_norm'].apply(lambda x: (isinstance(x, float) and x >= 3) or (isinstance(x, str) and x == 'closed lost'))
    lstage = df[late_mask].groupby('Owner')['Amount'].sum()

    # AvgAge: average AgeDays excluding 'closed lost'
    age_mask = df['stage_norm'].apply(lambda x: not (isinstance(x, str) and x == 'closed lost'))
    avg_age = df[age_mask].groupby('Owner')['AgeDays'].mean()

    # Stage0Count and Stage0Age: count and average for rows where stage_norm equals 0 (numeric or string '0')
    stage0_mask = df['stage_norm'].apply(lambda x: (isinstance(x, float) and x == 0) or (isinstance(x, str) and x == '0'))
    stage0_count = df[stage0_mask].groupby('Owner').size()
    stage0_age = df[stage0_mask].groupby('Owner')['AgeDays'].mean()

    # PipelineCreatedQTD: sum Amount for opportunities with CreatedDate in the current quarter
    pipeline_created = df[df['CreatedDate'] >= quarter_start].groupby('Owner')['Amount'].sum()
    # PipelineTargetQTD: 120% of PipelineCreatedQTD
    pipeline_target = pipeline_created * 1.2

    # Combine aggregated values into a DataFrame
    agg_df = pd.DataFrame({
        'QualifiedPipeQTD': qpipe,
        'LateStageAmount': lstage,
        'AvgAge': avg_age,
        'Stage0Count': stage0_count,
        'Stage0Age': stage0_age,
        'PipelineCreatedQTD': pipeline_created
    }).fillna(0)
    agg_df['PipelineTargetQTD'] = agg_df['PipelineCreatedQTD'] * 1.2

    # Merge aggregated values back into original DataFrame
    df = df.merge(agg_df, how='left', left_on='Owner', right_index=True)

    # Drop temporary columns
    df = df.drop(columns=['AgeDays', 'stage_norm'])
    return df

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
        # Recalculate derived fields
        df = recalc_derived_fields(df)
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
        
        # Generate synthetic data without derived columns; they will be recalculated
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
        
        print(f"Generated {n_records} total deals, {len(df[df['Stage'] == 4])} closed won")
        print(f"Average deal size: ${df['Amount'].mean():,.0f}")
        
        # Recalculate derived fields
        df = recalc_derived_fields(df)
        return df 