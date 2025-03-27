"""
Email control component for Sales Stack Ranker dashboard.
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from utils.email_utils import send_digest, send_alert, test_email_connection
from utils.data_loader import load_data
from utils.metrics_calculator import get_pipeline_metrics

def validate_email_config():
    """Validate email configuration in Streamlit secrets."""
    if 'email' not in st.secrets:
        return False, "Email configuration not found in Streamlit secrets"
    
    config = st.secrets['email']
    required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'email_from', 'email_to']
    
    missing_fields = [field for field in required_fields if field not in config]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    if not config['email_to']:
        return False, "No email recipients configured"
    
    return True, "Email configuration is valid"

def display_email_controls():
    """Display email control panel in Streamlit."""
    st.header("Email Controls")
    
    # Email Configuration Section
    with st.expander("Email Configuration", expanded=True):
        st.info("Configure email settings in Streamlit Cloud Secrets")
        st.code("""
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your_email@gmail.com"
smtp_password = "your_app_specific_password"
email_from = "your_email@gmail.com"
email_to = ["recipient1@example.com", "recipient2@example.com"]
        """)
        
        # Validate configuration
        is_valid, validation_message = validate_email_config()
        if not is_valid:
            st.error(f"⚠️ {validation_message}")
        else:
            st.success("✅ Email configuration is valid")
            
            # Display current configuration (without password)
            email_config = st.secrets['email']
            st.markdown("**Current Configuration:**")
            st.json({
                "SMTP Server": email_config.get('smtp_server', 'Not set'),
                "SMTP Port": email_config.get('smtp_port', 'Not set'),
                "SMTP Username": email_config.get('smtp_username', 'Not set'),
                "Email From": email_config.get('email_from', 'Not set'),
                "Email To": email_config.get('email_to', 'Not set')
            })
            
            # Test Connection Button
            if st.button("Test Email Connection"):
                with st.spinner("Testing email connection..."):
                    success, message = test_email_connection()
                    if success:
                        st.success("✅ Email connection successful!")
                    else:
                        st.error(f"❌ Email connection failed: {message}")
    
    # Test Email Section
    with st.expander("Send Test Email", expanded=True):
        if not is_valid:
            st.warning("Please configure email settings before sending test emails")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                email_type = st.selectbox(
                    "Email Type",
                    ["Daily Digest", "Pipeline Drop Alert", "Aging Opportunities Alert", "Rep Performance Alert"]
                )
            
            with col2:
                test_recipients = st.text_input(
                    "Test Recipients (comma-separated)",
                    value=st.session_state.get("test_recipients", ""),
                    key="test_recipients"
                )
            
            if st.button("Send Test Email"):
                try:
                    # Load data
                    df = load_data()
                    
                    if email_type == "Daily Digest":
                        # Calculate date range
                        today = datetime.now()
                        start_date = today - timedelta(days=7)
                        
                        # Filter data for the last 7 days
                        filtered_df = df[df['CreatedDate'].dt.date >= start_date.date()].copy()
                        
                        # Calculate metrics
                        metrics = get_pipeline_metrics(filtered_df)
                        
                        # Get rep performance
                        rep_performance = filtered_df.groupby('Owner').agg({
                            'QualifiedPipeQTD': 'sum',
                            'PipelineTargetQTD': 'first'
                        }).reset_index()
                        
                        rep_performance['PercentToPlan'] = (
                            rep_performance['QualifiedPipeQTD'] / rep_performance['PipelineTargetQTD'] * 100
                        )
                        
                        # Get pipeline health metrics
                        pipeline_health = {
                            'avg_stage_0_age': filtered_df[filtered_df['Stage'] == 0]['Stage0Age'].mean(),
                            'stage_0_count': len(filtered_df[filtered_df['Stage'] == 0])
                        }
                        
                        # Send digest
                        success = send_digest(
                            metrics=metrics,
                            rep_performance=rep_performance,
                            pipeline_health=pipeline_health,
                            date_range=(start_date.date(), today.date()),
                            recipients=test_recipients.split(",") if test_recipients else None
                        )
                        
                    elif email_type == "Pipeline Drop Alert":
                        metrics = get_pipeline_metrics(df)
                        alert_data = {
                            'current_value': metrics['total_pipeline'],
                            'previous_value': metrics.get('previous_total_pipeline', 0),
                            'drop_percentage': ((metrics['total_pipeline'] - metrics.get('previous_total_pipeline', 0)) 
                                              / metrics.get('previous_total_pipeline', 1) * 100)
                        }
                        success = send_alert(
                            alert_type='pipeline_drop',
                            alert_data=alert_data,
                            threshold=1000000,
                            recipients=test_recipients.split(",") if test_recipients else None
                        )
                        
                    elif email_type == "Aging Opportunities Alert":
                        stage0_df = df[df['Stage'] == 0].copy()
                        alert_data = {
                            'count': len(stage0_df[stage0_df['Stage0Age'] > 30]),
                            'total_stage0': len(stage0_df),
                            'avg_age': stage0_df['Stage0Age'].mean()
                        }
                        success = send_alert(
                            alert_type='aging_opportunities',
                            alert_data=alert_data,
                            threshold=30,
                            recipients=test_recipients.split(",") if test_recipients else None
                        )
                        
                    else:  # Rep Performance Alert
                        rep_metrics = df.groupby('Owner').agg({
                            'QualifiedPipeQTD': 'sum',
                            'PipelineTargetQTD': 'first'
                        }).reset_index()
                        
                        rep_metrics['PercentToPlan'] = rep_metrics['QualifiedPipeQTD'] / rep_metrics['PipelineTargetQTD']
                        underperforming = rep_metrics[rep_metrics['PercentToPlan'] < 0.7]
                        
                        alert_data = {
                            'count': len(underperforming),
                            'reps': underperforming['Owner'].tolist(),
                            'min_performance': underperforming['PercentToPlan'].min()
                        }
                        success = send_alert(
                            alert_type='rep_performance',
                            alert_data=alert_data,
                            threshold=0.7,
                            recipients=test_recipients.split(",") if test_recipients else None
                        )
                    
                    if success:
                        st.success("Test email sent successfully!")
                    else:
                        st.error("Failed to send test email. Check the console for details.")
                        
                except Exception as e:
                    st.error(f"Error sending test email: {str(e)}")
    
    # Scheduler Control Section
    with st.expander("Scheduler Control", expanded=True):
        st.warning("⚠️ Scheduler is currently disabled for testing")
        st.info("To enable the scheduler, run: `python -m utils.scheduler`") 