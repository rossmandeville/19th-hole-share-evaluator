# Deployment Guide

## GitHub Repository Setup

### 1. Create Repository
```bash
git init
git add .
git commit -m "Initial commit: 19th Hole Investment Club Share Evaluator"
git branch -M main
git remote add origin https://github.com/yourusername/19th-hole-share-evaluator.git
git push -u origin main
```

### 2. Environment Variables Setup
Create a `.env` file (not included in repository):
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
```

### 3. Streamlit Cloud Deployment
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file: `app.py`
4. Add secrets in Streamlit Cloud:
   - ALPHA_VANTAGE_API_KEY
   - NEWS_API_KEY

### 4. Local Development
```bash
# Install dependencies
pip install -r project_requirements.txt

# Run locally
streamlit run app.py
```

## Project Files Ready for GitHub

### Core Application Files
- `app.py` - Main Streamlit application
- `alpha_vantage_fetcher.py` - API integration
- `investment_parameters.py` - Parameter framework
- `tabular_evaluator.py` - Evaluation system
- `utils.py` - Utility functions
- `api_cache.py` - Caching system

### Documentation
- `README.md` - Project overview and setup
- `DEPLOYMENT.md` - This deployment guide
- `replit.md` - Development documentation

### Configuration
- `project_requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

## Features Implemented
- 10-parameter evaluation framework
- Sector-specific weightings
- 19H proprietary scoring system
- Real-time Alpha Vantage data integration
- Comprehensive evaluation tables
- Visual performance analysis
- Investment recommendations

## Ready for Production
All files are prepared and the application is fully functional with authentic data sources.