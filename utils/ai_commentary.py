"""
AI commentary utilities for generating insights using OpenAI.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Union
from openai import OpenAI
from datetime import datetime

def get_openai_client():
    """Get OpenAI client with API key from Streamlit secrets."""
    if 'openai' not in st.secrets:
        raise ValueError("OpenAI API key not found in Streamlit secrets")
    
    api_key = st.secrets['openai']['OPENAI_API_KEY']
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("Please configure your OpenAI API key in Streamlit secrets")
    
    return OpenAI(api_key=api_key)

def generate_commentary(df: pd.DataFrame, metrics: Dict[str, Union[float, int]]) -> str:
    """
    Generate AI commentary on pipeline metrics and trends.
    
    Args:
        df (pd.DataFrame): Input DataFrame with pipeline data
        metrics (Dict[str, Union[float, int]]): Dictionary of pipeline metrics
        
    Returns:
        str: Generated commentary in markdown format
    """
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Prepare data for analysis
        stage_distribution = df.groupby('Stage')['Amount'].sum().to_dict()
        source_distribution = metrics['source_distribution']
        
        # Create prompt for OpenAI
        prompt = f"""Analyze the following sales pipeline data and provide insights in a clear, bullet-point format:

Key Metrics:
- Total Pipeline: ${metrics['total_pipeline']:,.2f}
- Qualified Pipeline: ${metrics['qualified_pipeline']:,.2f}
- Win Rate: {metrics['win_rate']:.1%}
- Average Deal Size: ${metrics['avg_deal_size']:,.2f}
- Pipeline Velocity: {metrics['pipeline_velocity']:.1f} days

Stage Distribution:
{stage_distribution}

Source Distribution:
{source_distribution}

Please provide insights in the following format:

### Key Observations
• [Observation 1]
• [Observation 2]
• [Observation 3]

### Areas of Concern
• [Concern 1]
• [Concern 2]
• [Concern 3]

### Opportunities
• [Opportunity 1]
• [Opportunity 2]
• [Opportunity 3]

### Recommendations
• [Recommendation 1]
• [Recommendation 2]
• [Recommendation 3]

Use bullet points (•) for all items and maintain a consistent, professional tone."""

        # Generate commentary using OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a sales analytics expert providing clear, concise insights in a consistent bullet-point format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and format the commentary
        commentary = response.choices[0].message.content
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commentary = f"*Generated on {timestamp}*\n\n{commentary}"
        
        return commentary
        
    except Exception as e:
        print(f"Error generating commentary: {str(e)}")
        return "Unable to generate insights at this time. Please check your OpenAI API configuration." 