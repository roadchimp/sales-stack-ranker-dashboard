# Sales Stack Ranker Dashboard

A Streamlit-based dashboard for visualizing and analyzing sales pipeline data. This dashboard provides real-time insights into your sales pipeline performance, including key metrics, rep rankings, and pipeline health indicators.

## Features

- 📊 Real-time pipeline metrics and KPIs
- 👥 Rep performance rankings
- 📈 Pipeline trend visualization
- 🔍 Interactive filters by region and date
- 📊 Pipeline distribution by source and stage
- 📱 Responsive design

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `data_loader.py`: Data loading and processing functions
- `data/sales_pipeline.csv`: Sample data file (generated automatically)
- `requirements.txt`: Project dependencies

## Data Structure

The dashboard expects data in the following format:
- OpportunityID: Unique identifier
- Owner: Sales representative name
- Region: Sales region
- CreatedDate: Opportunity creation date
- CloseDate: Expected close date
- Stage: Sales stage (0-4)
- Amount: Opportunity value
- Source: Lead source

## Future Enhancements

- 🔄 Real-time Salesforce integration
- 📧 Automated email digests
- 🔍 Advanced filtering and search
- 📱 Mobile-optimized view
- 📈 Custom KPI tracking

## Contributing

Feel free to submit issues and enhancement requests! 