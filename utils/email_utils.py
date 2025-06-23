"""
Email utility functions for sending digests and alerts.
"""
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from pathlib import Path
import jinja2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_email_config():
    """Get email configuration from environment variables or Streamlit secrets."""
    config = {}
    
    # First try to get configuration from environment variables (for local development)
    config['smtp_server'] = os.getenv('SMTP_SERVER')
    config['smtp_port'] = int(os.getenv('SMTP_PORT', 587))
    config['smtp_username'] = os.getenv('SMTP_USERNAME')
    config['smtp_password'] = os.getenv('SMTP_PASSWORD')
    config['email_from'] = os.getenv('EMAIL_FROM')
    email_to_str = os.getenv('EMAIL_TO', '')
    config['email_to'] = [email.strip() for email in email_to_str.split(',') if email.strip()]
    
    # If environment variables are not set, try Streamlit secrets (for cloud deployment)
    if not config['smtp_server'] and 'email' in st.secrets:
        secrets_config = st.secrets['email']
        config = {
            'smtp_server': secrets_config.get('smtp_server'),
            'smtp_port': secrets_config.get('smtp_port'),
            'smtp_username': secrets_config.get('smtp_username'),
            'smtp_password': secrets_config.get('smtp_password'),
            'email_from': secrets_config.get('email_from'),
            'email_to': secrets_config.get('email_to', [])
        }
    
    # Validate configuration
    if not config['smtp_server']:
        raise ValueError("Email configuration not found in environment variables or Streamlit secrets")
    
    return config

def test_email_connection():
    """Test the email connection using the configured settings."""
    try:
        # Get email configuration
        config = get_email_config()
        
        # Create a test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Test Email Connection"
        msg['From'] = config['email_from']
        msg['To'] = config['email_from']  # Send to self for testing
        
        # Add test content
        msg.attach(MIMEText("This is a test email to verify the email configuration.", 'plain'))
        
        # Try to connect and send
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['smtp_username'], config['smtp_password'])
            server.send_message(msg)
        
        return True, "Connection successful"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Please check your username and password."
    except smtplib.SMTPConnectError:
        return False, "Could not connect to SMTP server. Please check server and port settings."
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def send_email(subject, html_content, recipients=None):
    """Send an email using SMTP."""
    try:
        # Get email configuration from secrets
        config = get_email_config()
        
        # Use provided recipients or default from config
        recipients = recipients or config['email_to']
        if not recipients:
            raise ValueError("No recipients specified")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['email_from']
        msg['To'] = ', '.join(recipients)
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['smtp_username'], config['smtp_password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def get_template(template_name):
    """Load and return an HTML template."""
    template_dir = Path(__file__).parent.parent / 'templates' / 'email'
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir)
    )
    return env.get_template(template_name)

def send_digest(metrics, rep_performance, pipeline_health, date_range, recipients=None):
    """Send a daily digest email."""
    template = get_template('digest.html')
    
    # Format metrics for display
    formatted_metrics = {
        'total_pipeline': float(metrics.get('total_pipeline') or 0),
        'qualified_pipeline': float(metrics.get('qualified_pipeline') or 0),
        'late_stage_amount': float(metrics.get('late_stage_amount') or 0),
        'win_rate': float(metrics.get('win_rate') or 0),
        'avg_deal_size': float(metrics.get('avg_deal_size') or 0),
        'pipeline_velocity': float(metrics.get('pipeline_velocity') or 0)
    }
    
    # Format rep performance
    rep_performance['PercentToPlan'] = rep_performance['PercentToPlan'].round(1)
    
    # Format pipeline health
    pipeline_health['avg_stage_0_age'] = round(float(pipeline_health.get('avg_stage_0_age') or 0), 1)
    
    # Generate HTML content
    html_content = template.render(
        metrics=formatted_metrics,
        rep_performance=rep_performance.to_dict('records'),
        pipeline_health=pipeline_health,
        date_range=date_range,
        generated_at=datetime.now().strftime("%B %d, %Y")
    )
    
    # Send email
    return send_email(
        subject=f"Sales Pipeline Digest - {datetime.now().strftime('%B %d, %Y')}",
        html_content=html_content,
        recipients=recipients
    )

def send_alert(alert_type, alert_data, threshold, recipients=None):
    """Send an alert email."""
    template = get_template('alert.html')
    
    # Format alert data based on type
    if alert_type == 'pipeline_drop':
        formatted_data = {
            'current_value': float(alert_data.get('current_value') or 0),
            'previous_value': float(alert_data.get('previous_value') or 0),
            'drop_percentage': float(alert_data.get('drop_percentage') or 0)
        }
        subject = "Pipeline Drop Alert"
    elif alert_type == 'aging_opportunities':
        formatted_data = {
            'count': int(alert_data.get('count') or 0),
            'total_stage0': int(alert_data.get('total_stage0') or 0),
            'avg_age': float(alert_data.get('avg_age') or 0)
        }
        subject = "Aging Opportunities Alert"
    else:  # rep_performance
        formatted_data = {
            'count': int(alert_data.get('count') or 0),
            'reps': alert_data.get('reps') if alert_data.get('reps') is not None else [],
            'min_performance': float(alert_data.get('min_performance') or 0)
        }
        subject = "Rep Performance Alert"
    
    threshold = float(threshold or 0)

    # Generate HTML content
    html_content = template.render(
        alert_type=alert_type,
        alert_data=formatted_data,
        threshold=threshold,
        generated_at=datetime.now().strftime("%B %d, %Y")
    )
    
    # Send email
    return send_email(
        subject=subject,
        html_content=html_content,
        recipients=recipients
    ) 