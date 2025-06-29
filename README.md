# 19th Hole Investment Club - Share Evaluator

A comprehensive stock evaluation platform that analyzes shares using a refined 10-parameter framework specifically designed for UK and US markets.

## Features

- **10-Parameter Evaluation System**: Comprehensive analysis using the most important financial metrics
- **Sector-Specific Weightings**: Dynamic importance scoring based on industry characteristics
- **Real-Time Data**: Authentic financial data from Alpha Vantage API
- **19H Score**: Proprietary scoring system (Total weighted score ÷ Maximum possible × 100)
- **Visual Analysis**: Interactive charts showing parameter performance vs importance
- **Investment Recommendations**: AI-powered buy/hold/sell recommendations with risk assessment

## The 10 Core Parameters

1. **P/E Ratio** - Primary valuation metric
2. **Revenue Growth** - Business expansion indicator
3. **Return on Equity** - Management efficiency
4. **Debt/Equity** - Financial risk assessment
5. **Free Cash Flow Yield** - Cash generation capability
6. **Dividend Yield** - Income generation potential
7. **EPS Growth** - Earnings trajectory
8. **P/B Ratio** - Value identification
9. **Current Ratio** - Liquidity safety measure
10. **Operating Margin** - Operational efficiency

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/19th-hole-share-evaluator.git
cd 19th-hole-share-evaluator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
NEWS_API_KEY=your_news_api_key
```

4. Run the application:
```bash
streamlit run app.py
```

## API Keys Required

- **Alpha Vantage API**: Get your free key at [alphavantage.co](https://www.alphavantage.co/support/#api-key)
- **News API**: Get your free key at [newsapi.org](https://newsapi.org/register)

## Usage

1. Enter a US stock ticker symbol (e.g., AAPL, MSFT, GOOGL) in the sidebar
2. View the comprehensive evaluation table with:
   - Parameter importance weights for the sector
   - Company performance scores (1-10)
   - Weighted scores and 19H overall score
3. Analyze the visual performance vs importance chart
4. Review investment recommendation and sector insights

## Project Structure

```
├── app.py                      # Main Streamlit application
├── alpha_vantage_fetcher.py    # Alpha Vantage API integration
├── investment_parameters.py    # Parameter definitions and scoring
├── tabular_evaluator.py       # Evaluation table generation
├── utils.py                    # Utility functions
├── api_cache.py               # API caching and rate limiting
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Technology Stack

- **Frontend**: Streamlit
- **Data Source**: Alpha Vantage API
- **Charts**: Plotly
- **Data Processing**: Pandas, NumPy
- **News Integration**: News API

## Contributing

This project is developed for The 19th Hole Investment Club. For contributions or suggestions, please contact the development team.

## License

This project is proprietary software developed for The 19th Hole Investment Club.

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Always consult with qualified financial professionals before making investment decisions.