import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def validate_headers(df):
    """Validate that all required headers are present in the DataFrame."""
    required_columns = {
        'OpportunityID': str,
        'Owner': str,
        'Region': str,
        'CreatedDate': str,
        'CloseDate': str,
        'Stage': (int, float),
        'Amount': (int, float),
        'Source': str
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
        
        # Clean Owner and Region (remove extra spaces, ensure string)
        df['Owner'] = df['Owner'].astype(str).str.strip()
        df['Region'] = df['Region'].astype(str).str.strip()
        
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
        
        # Clean and validate Amount (must be positive number)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        if df['Amount'].isna().any():
            bad_amounts = df[df['Amount'].isna()].index.tolist()
            raise ValueError(f"Invalid Amount values at rows: {bad_amounts}")
        if (df['Amount'] < 0).any():
            negative_amounts = df[df['Amount'] < 0].index.tolist()
            raise ValueError(f"Negative Amount values found at rows: {negative_amounts}")
        
        # Clean Source (remove extra spaces, ensure string)
        df['Source'] = df['Source'].astype(str).str.strip()
        
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
        rep_rankings = df.groupby('Owner').agg({
            'Amount': ['sum', 'count'],
            'Stage': lambda x: (x >= 2).mean() * 100 if len(x) > 0 else 0
        }).round(2)
        rep_rankings.columns = ['Total Pipeline', 'Opportunity Count', 'Qualification Rate']
        rep_rankings = rep_rankings.sort_values('Total Pipeline', ascending=False)
    else:
        rep_rankings = pd.DataFrame({
            'Total Pipeline': [],
            'Opportunity Count': [],
            'Qualification Rate': []
        })
    
    metrics['rep_rankings'] = rep_rankings
    
    return metrics 