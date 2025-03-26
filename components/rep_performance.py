"""
Rep performance component for Sales Stack Ranker dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

def display_rep_performance_tab(filtered_df: pd.DataFrame) -> None:
    """
    Display the rep performance tab content.
    
    Args:
        filtered_df (pd.DataFrame): Filtered DataFrame based on user selection
    """
    st.subheader("🎯 Percent-to-Plan and Rankings")
    
    try:
        # Calculate qualified pipeline per rep (opportunities Stage 2 or higher)
        qualified_pipeline = filtered_df[filtered_df['Stage'] >= 2].groupby('Owner')['Amount'].sum().reset_index()
        qualified_pipeline.columns = ['Owner', 'QualifiedPipeline']
        
        # Calculate actual attainment (Closed Won deals)
        actual_attainment = filtered_df[filtered_df['Stage'] == 4].groupby('Owner')['Amount'].sum().reset_index()
        actual_attainment.columns = ['Owner', 'Attainment']
        
        # Get unique owners and their targets
        owner_targets = filtered_df.groupby('Owner')['PipelineTargetQTD'].first().reset_index()
        owner_targets.columns = ['Owner', 'Target']
        
        # Merge qualified pipeline, attainment, and targets
        rankings_df = pd.merge(qualified_pipeline, owner_targets, on='Owner', how='left')
        rankings_df = pd.merge(rankings_df, actual_attainment, on='Owner', how='left')
        rankings_df['Attainment'] = rankings_df['Attainment'].fillna(0)
        
        # Calculate percent to plan based on actual attainment
        # Convert to numeric first to ensure proper calculation
        rankings_df['Target'] = pd.to_numeric(rankings_df['Target'])
        rankings_df['Attainment'] = pd.to_numeric(rankings_df['Attainment'])
        rankings_df['PercentToPlan'] = (rankings_df['Attainment'] / rankings_df['Target']) * 100
        
        # Sort by percent to plan descending
        rankings_df = rankings_df.sort_values('PercentToPlan', ascending=False)
        
        # Create a copy for metrics calculation before formatting
        metrics_df = rankings_df.copy()
        
        # Format the numeric columns
        rankings_df['QualifiedPipeline'] = rankings_df['QualifiedPipeline'].apply(lambda x: f"${x:,.0f}")
        rankings_df['Target'] = rankings_df['Target'].apply(lambda x: f"${x:,.0f}")
        rankings_df['Attainment'] = rankings_df['Attainment'].apply(lambda x: f"${x:,.0f}")
        rankings_df['PercentToPlan'] = rankings_df['PercentToPlan'].apply(lambda x: f"{x:.1f}")
        
        # Add rank column
        rankings_df.insert(0, 'Rank', range(1, len(rankings_df) + 1))
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            above_plan = (metrics_df['PercentToPlan'] >= 100).sum()
            st.metric("Reps Above Plan", f"{above_plan}", f"{(above_plan/len(rankings_df))*100:.1f}% of team")
        
        with col2:
            avg_attainment = metrics_df['PercentToPlan'].mean()
            st.metric("Average Attainment", f"{avg_attainment:.1f}%", "of target")
        
        with col3:
            median_attainment = metrics_df['PercentToPlan'].median()
            st.metric("Median Attainment", f"{median_attainment:.1f}%", "of target")
        
        # Rename columns for display
        rankings_df.columns = ['Rank', 'Sales Rep', 'Qualified Pipeline', 'Target', 'Attainment', 'Percent to Plan']
        
        # Display the rankings table
        st.dataframe(
            rankings_df,
            column_config={
                "Rank": st.column_config.NumberColumn(
                    "🏆 Rank",
                    help="Sales rep ranking based on percent to plan",
                    format="%d"
                ),
                "Sales Rep": st.column_config.TextColumn(
                    "👤 Sales Rep",
                    help="Name of the sales representative"
                ),
                "Qualified Pipeline": st.column_config.TextColumn(
                    "💰 Qualified Pipeline",
                    help="Sum of opportunity amounts in Stage 2 or higher"
                ),
                "Target": st.column_config.TextColumn(
                    "🎯 Target",
                    help="Pipeline creation target for the quarter"
                ),
                "Attainment": st.column_config.TextColumn(
                    "✅ Attainment",
                    help="Total closed/won business"
                ),
                "Percent to Plan": st.column_config.ProgressColumn(
                    "📊 Percent to Plan",
                    help="Percentage of target achieved (Attainment / Target)",
                    format="%.1f%%",
                    min_value=0,
                    max_value=200
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Add a download button for the rankings
        csv = rankings_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Rankings",
            data=csv,
            file_name="sales_rankings.csv",
            mime="text/csv"
        )
        
        # Top Performers Highlight
        st.subheader("🌟 Top Performers")
        top_3_df = rankings_df.head(3)
        
        cols = st.columns(3)
        for idx, (_, row) in enumerate(top_3_df.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                #### {['🥇', '🥈', '🥉'][idx]} {row['Sales Rep']}
                - Qualified Pipeline: {row['Qualified Pipeline']}
                - Target: {row['Target']}
                - Attainment: {row['Attainment']}
                - Percent to Plan: {row['Percent to Plan']}%
                """)
        
        # Create a histogram of percent to plan distribution
        percent_to_plan_values = metrics_df['PercentToPlan']
        
        fig = px.histogram(
            percent_to_plan_values,
            nbins=10,
            title='Distribution of Percent to Plan',
            labels={'value': 'Percent to Plan', 'count': 'Number of Reps'},
        )
        fig.update_layout(
            xaxis_title="Percent to Plan",
            yaxis_title="Number of Reps",
            showlegend=False,
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            autosize=True
        )
        fig.update_traces(
            hovertemplate="Percent to Plan: %{x:.1f}%<br>Number of Reps: %{y}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error calculating rankings: {str(e)}")
        st.write("Unable to display rankings. Please check your data and try again.") 