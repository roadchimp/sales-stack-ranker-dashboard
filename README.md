# Sales Stack Ranker Dashboard

A comprehensive sales pipeline analytics dashboard built with Streamlit, providing real-time insights into sales performance, pipeline health, and team metrics.

## Features

- **Key Metrics Overview**: Track total pipeline, qualified pipeline, average deal size, and win rates
- **AI-Powered Commentary**: Get intelligent insights about your pipeline metrics
- **Rep Performance Analysis**: View rankings, attainment, and performance distribution
- **Pipeline Analysis**: Analyze stage distribution, aging, and pipeline health
- **Source Analysis**: Understand pipeline sources and their effectiveness

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- OpenAI API key (for AI-powered commentary)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sales-stack-ranker.git
cd sales-stack-ranker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up OpenAI API key:

For local development:
- Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

For Streamlit Cloud deployment:
- Go to your Streamlit Cloud dashboard
- Navigate to your app's settings
- Add the following to your secrets:
```toml
OPENAI_API_KEY = "your_openai_api_key_here"
```

Note: Never commit your `.env` file or expose your API key in public repositories.

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Upload your sales data CSV file or use the sample data provided

## Data Format

Your CSV file should include the following columns:
- OpportunityID (text)
- Owner (text)
- Role (text)
- Region (text)
- CreatedDate (YYYY-MM-DD)
- CloseDate (YYYY-MM-DD)
- Stage (0-4)
- Amount (positive number)
- Source (text)
- LeadSourceCategory (text)
- QualifiedPipeQTD (number)
- LateStageAmount (number)
- AvgAge (number)
- Stage0Age (number)
- Stage0Count (number)
- PipelineCreatedQTD (number)
- PipelineTargetQTD (number)

## Project Structure

```
sales_stack_ranker/
├── app.py                    # Main application entry point
├── requirements.txt          # Dependencies
├── README.md                # Documentation
├── components/              # UI Components
│   ├── __init__.py
│   ├── metrics.py          # Key metrics display
│   ├── overview_tab.py     # Overview & Attainment tab
│   ├── rep_performance.py  # Rep Performance tab
│   ├── pipeline_analysis.py # Pipeline Analysis tab
│   └── source_analysis.py  # Source Analysis tab
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── data_loader.py     # Data loading and processing
│   ├── metrics_calculator.py # Metrics calculations
│   └── ai_commentary.py   # AI commentary generation
├── styles/                # Styling
│   └── custom.css        # CSS styles
└── config/               # Configuration
    └── settings.py       # App settings and constants
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 