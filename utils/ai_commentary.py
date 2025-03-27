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
        prompt = f"""Analyze the following sales pipeline data and provide a concise executive summary:

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

Please provide a brief executive summary (3-4 bullet points) that highlights:
1. The most important pipeline metrics and their implications
2. Key areas of concern or risks
3. Notable trends in the pipeline

Use bullet points (•) and keep the tone professional and concise. Focus on actionable insights.
Do not include separate sections or headings."""

        # Generate commentary using OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a sales analytics expert providing clear, concise insights. Keep the format simple and consistent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
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