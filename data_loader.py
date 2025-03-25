import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def validate_headers(df):
    """Validate that all required headers are present in the DataFrame."""
    required_columns = {
        'OpportunityID': str,
        'Owner': str,
        'Role': str,
        'Region': str,
        'CreatedDate': str,
        'CloseDate': str,
        'Stage': (int, float),
        'Amount': (int, float),
        'Source': str,
        'LeadSourceCategory': str,
        'QualifiedPipeQTD': (int, float),
        'LateStageAmount': (int, float),
        'AvgAge': (int, float),
        'Stage0Age': (int, float),
        'Stage0Count': (int, float)
    }
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    return required_columns

def clean_and_validate_data(df):
    """Clean and validate data types and formats."""
    if df.empty:
        raise ValueError("CSV file is empty or contains only headers")
    
    # Get required columns and their types
    required_columns = validate_headers(df)
    
    # Make a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Clean and validate each column
    try:
        # Clean OpportunityID (remove any spaces, convert to string)
        df['OpportunityID'] = df['OpportunityID'].astype(str).str.strip()
        
        # Clean text fields
        for text_col in ['Owner', 'Role', 'Region', 'Source', 'LeadSourceCategory']:
            df[text_col] = df[text_col].astype(str).str.strip()
        
        # Clean and validate dates
        for date_col in ['CreatedDate', 'CloseDate']:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            if df[date_col].isna().any():
                bad_dates = df[df[date_col].isna()][date_col].index.tolist()
                raise ValueError(f"Invalid date format in {date_col} at rows: {bad_dates}")
        
        # Clean and validate Stage (must be integer 0-4)
        df['Stage'] = pd.to_numeric(df['Stage'], errors='coerce')
        invalid_stages = df[~df['Stage'].isin([0, 1, 2, 3, 4])].index.tolist()
        if invalid_stages:
            raise ValueError(f"Invalid Stage values at rows {invalid_stages}. Stage must be between 0 and 4.")
        
        # Clean and validate numeric columns
        numeric_cols = ['Amount', 'QualifiedPipeQTD', 'LateStageAmount', 'AvgAge', 'Stage0Age', 'Stage0Count']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isna().any():
                bad_values = df[df[col].isna()].index.tolist()
                raise ValueError(f"Invalid numeric values in {col} at rows: {bad_values}")
            if col != 'Stage0Count' and (df[col] < 0).any():
                negative_values = df[df[col] < 0].index.tolist()
                raise ValueError(f"Negative values found in {col} at rows: {negative_values}")
        
        # Remove any rows with all NaN values
        df = df.dropna(how='all')
        
    except Exception as e:
        raise ValueError(f"Data validation error: {str(e)}")
    
    return df

def generate_synthetic_data(n_records=100):
    """Generate synthetic sales pipeline data for testing."""
    np.random.seed(42)
    
    # Define possible values
    owners = ['Alice Smith', 'Bob Jones', 'Carol White', 'David Brown', 'Emma Wilson']
    roles = ['Account Executive', 'Senior AE', 'Enterprise AE', 'SMB AE']
    regions = ['West', 'Midwest', 'East', 'South']
    stages = [0, 1, 2, 3, 4]  # 0: Prospecting, 1: Qualification, 2: Proposal, 3: Negotiation, 4: Closed Won
    sources = ['Rep', 'Marketing', 'Partner', 'Website']
    lead_categories = ['Inbound', 'Outbound', 'Partner', 'Event', 'Referral']
    
    # Generate base data
    created_dates = [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_records)]
    stages_data = np.random.choice(stages, n_records)
    amounts = np.random.randint(10000, 500000, n_records)
    
    # Calculate derived fields
    qualified_pipe_qtd = [amt if stage >= 2 and (datetime.now() - created).days <= 90 else 0 
                         for amt, stage, created in zip(amounts, stages_data, created_dates)]
    late_stage_amount = [amt if stage >= 3 else 0 for amt, stage in zip(amounts, stages_data)]
    stage0_counts = [1 if stage == 0 else 0 for stage in stages_data]
    stage0_ages = [
        (datetime.now() - created).days if stage == 0 else 0 
        for stage, created in zip(stages_data, created_dates)
    ]
    avg_ages = [(datetime.now() - created).days for created in created_dates]
    
    data = {
        'OpportunityID': [f'OPP{i+1:04d}' for i in range(n_records)],
        'Owner': np.random.choice(owners, n_records),
        'Role': np.random.choice(roles, n_records),
        'Region': np.random.choice(regions, n_records),
        'CreatedDate': [d.strftime('%Y-%m-%d') for d in created_dates],
        'CloseDate': [(d + timedelta(days=np.random.randint(30, 180))).strftime('%Y-%m-%d') 
                     for d in created_dates],
        'Stage': stages_data,
        'Amount': amounts,
        'Source': np.random.choice(sources, n_records),
        'LeadSourceCategory': np.random.choice(lead_categories, n_records),
        'QualifiedPipeQTD': qualified_pipe_qtd,
        'LateStageAmount': late_stage_amount,
        'AvgAge': avg_ages,
        'Stage0Age': stage0_ages,
        'Stage0Count': stage0_counts
    }
    
    return pd.DataFrame(data)

def load_data():
    """Load data from CSV if exists, otherwise generate synthetic data."""
    if os.path.exists('data/sales_pipeline.csv'):
        df = pd.read_csv('data/sales_pipeline.csv')
        df = clean_and_validate_data(df)  # Validate loaded data
    else:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        df = generate_synthetic_data()
        df.to_csv('data/sales_pipeline.csv', index=False)
    
    # Convert date columns to datetime
    df['CreatedDate'] = pd.to_datetime(df['CreatedDate'])
    df['CloseDate'] = pd.to_datetime(df['CloseDate'])
    
    return df

def load_csv_data(uploaded_file):
    """Load and validate data from uploaded CSV file."""
    try:
        # First, try to read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate and clean the data
        df = clean_and_validate_data(df)
        
        return df
        
    except pd.errors.EmptyDataError:
        raise ValueError("The uploaded CSV file is empty")
    except pd.errors.ParserError:
        raise ValueError("Unable to parse the CSV file. Please ensure it's a valid CSV format.")
    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")

def get_pipeline_metrics(df):
    """Calculate key pipeline metrics with proper handling of empty DataFrames."""
    # Handle empty DataFrame
    if df.empty:
        return {
            'total_pipeline': 0,
            'late_stage_pipeline': 0,
            'late_stage_percentage': 0,
            'qualified_pipeline': 0,
            'stage_0_pipeline': 0,
            'stage_0_count': 0,
            'avg_stage_0_age': 0,
            'pipeline_by_source': {'No Data': 0},
            'rep_rankings': pd.DataFrame({
                'Total Pipeline': [],
                'Opportunity Count': [],
                'Qualification Rate': []
            })
        }

    # Calculate metrics with safe division
    total_pipeline = df['Amount'].sum()
    late_stage_pipeline = df[df['Stage'].isin([3, 4])]['Amount'].sum()
    
    metrics = {
        'total_pipeline': total_pipeline,
        'late_stage_pipeline': late_stage_pipeline,
        'late_stage_percentage': (late_stage_pipeline / total_pipeline * 100) if total_pipeline > 0 else 0,
        'qualified_pipeline': df[df['Stage'].isin([2, 3, 4])]['Amount'].sum(),
        'stage_0_pipeline': df[df['Stage'] == 0]['Amount'].sum(),
        'stage_0_count': len(df[df['Stage'] == 0]),
    }
    
    # Safe calculation of average stage 0 age
    stage_0_df = df[df['Stage'] == 0]
    if not stage_0_df.empty:
        metrics['avg_stage_0_age'] = (datetime.now() - stage_0_df['CreatedDate']).mean().days
    else:
        metrics['avg_stage_0_age'] = 0
    
    # Calculate pipeline by source
    pipeline_by_source = df.groupby('Source')['Amount'].sum().to_dict()
    metrics['pipeline_by_source'] = pipeline_by_source if pipeline_by_source else {'No Data': 0}
    
    # Calculate rep rankings with safe calculations
    if not df.empty:
        rep_rankings = df.groupby(['Owner', 'Role']).agg({
            'Amount': ['sum', 'count'],
            'Stage': lambda x: (x >= 2).mean() * 100 if len(x) > 0 else 0,
            'QualifiedPipeQTD': 'sum',
            'LateStageAmount': 'sum',
            'Stage0Count': 'sum',
            'Stage0Age': 'mean'
        }).round(2)
        
        # Flatten column names
        rep_rankings.columns = ['Total Pipeline', 'Opportunity Count', 'Qualification Rate', 
                              'Qualified Pipeline QTD', 'Late Stage Amount', 'Stage 0 Count', 'Stage 0 Age']
        rep_rankings = rep_rankings.sort_values('Total Pipeline', ascending=False)
    else:
        rep_rankings = pd.DataFrame(columns=['Total Pipeline', 'Opportunity Count', 'Qualification Rate',
                                           'Qualified Pipeline QTD', 'Late Stage Amount', 'Stage 0 Count', 'Stage 0 Age'])
    
    metrics['rep_rankings'] = rep_rankings
    
    return metrics 