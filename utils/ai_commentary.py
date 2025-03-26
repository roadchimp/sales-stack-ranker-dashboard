"""
AI commentary generation utilities for Sales Stack Ranker dashboard.
"""
import os
from openai import OpenAI
from typing import Dict, Union

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment variable."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    return api_key

def generate_commentary(metrics: Dict[str, Union[float, int]]) -> str:
    """
    Generate AI commentary based on pipeline metrics.
    
    Args:
        metrics (Dict[str, Union[float, int]]): Dictionary of pipeline metrics
        
    Returns:
        str: Generated commentary
    """
    try:
        # Initialize OpenAI client with API key
        client = OpenAI(api_key=get_openai_api_key())
        
        # Create summary text from metrics
        summary = f"""The total sales pipeline is currently valued at ${metrics['total_pipeline']:,.0f}, which indicates the total potential revenue from all opportunities in the pipeline.

The Qualified Pipeline for the quarter to date (QTD) is ${metrics['qualified_pipeline']:,.0f}. This represents opportunities that have been qualified and are likely to close.

The Late Stage Pipeline, which stands at ${metrics['late_stage_pipeline']:,.0f}, represents opportunities in the final stages of the sales process. This figure is {metrics['late_stage_pipeline']/metrics['qualified_pipeline']:.1f} times the value of the qualified pipeline.

The Average Stage 0 Age is {metrics['avg_stage_0_age']:.1f} days, which indicates the average time opportunities spend in the initial prospecting stage."""
        
        # Generate commentary using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sales analytics expert. Analyze the pipeline metrics and provide insights in a clear, professional manner."},
                {"role": "user", "content": f"Please analyze these sales pipeline metrics and provide key insights:\n\n{summary}"}
            ],
            max_tokens=250,
            temperature=0.7
        )
        
        # Extract and return the generated commentary
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating commentary: {str(e)}" 