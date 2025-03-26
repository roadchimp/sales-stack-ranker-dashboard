"""
AI commentary generation utilities for Sales Stack Ranker dashboard.
"""
import streamlit as st
import openai
from typing import Dict, Union
import os
from dotenv import load_dotenv

def get_openai_api_key() -> str:
    """
    Get OpenAI API key from environment variables or Streamlit secrets.
    Returns:
        str: OpenAI API key
    """
    # Try to load from .env file first
    load_dotenv()
    
    # Check for API key in environment variables (from .env)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found in environment, try Streamlit secrets
    if not api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set it either in:\n"
            "1. A .env file in the root directory (for local development)\n"
            "2. Streamlit secrets (for deployment)"
        )
    
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
        openai.api_key = get_openai_api_key()
        
        # Create summary text from metrics
        summary = f"""The total sales pipeline is currently valued at ${metrics['total_pipeline']:,.0f}, which indicates the total potential revenue from all opportunities in the pipeline.

The Qualified Pipeline for the quarter to date (QTD) is ${metrics['qualified_pipeline']:,.0f}. This represents opportunities that have been qualified and are likely to close.

The Late Stage Pipeline, which stands at ${metrics['late_stage_pipeline']:,.0f}, represents opportunities in the final stages of the sales process. This figure is {metrics['late_stage_pipeline']/metrics['qualified_pipeline']:.1f} times the value of the qualified pipeline.

The Average Stage 0 Age is {metrics['avg_stage_0_age']:.1f} days, which indicates the average time opportunities spend in the initial prospecting stage."""
        
        # Generate AI commentary
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an insightful sales analytics expert providing concise commentary on sales data.
Your task is to analyze the metrics and provide clear, actionable insights.

Guidelines:
1. Use plain text only - NO markdown, NO formatting, NO italics
2. Write in clear, direct sentences
3. Focus on key insights and trends
4. Suggest specific actions when relevant
5. Keep paragraphs short and focused
6. Use proper spacing between paragraphs"""
                },
                {
                    "role": "user",
                    "content": f"Analyze these sales metrics and provide clear insights: {summary}"
                }
            ],
            max_tokens=200,
            temperature=0.5,
        )
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error generating commentary: {str(e)}")
        return "Unable to generate commentary at this time." 