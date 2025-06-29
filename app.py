import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from alpha_vantage_fetcher import alpha_vantage_fetcher
from investment_parameters import (
    get_sector_specific_weights, calculate_parameter_score,
    generate_investment_recommendation, get_parameter_thresholds
)
from utils import fetch_stock_news
from tabular_evaluator import (
    create_evaluation_table, display_company_header, 
    style_evaluation_table, create_parameter_chart, display_sector_insights
)

# Set page configuration
st.set_page_config(
    page_title="19th Hole Investment Club - Share Evaluator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #6f9bd1; font-weight: bold; }
    .score-average { color: #ffc107; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
    .investment-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .recommendation-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
    .buy-strong { background-color: #d4edda; color: #155724; }
    .buy-moderate { background-color: #d1ecf1; color: #0c5460; }
    .hold { background-color: #fff3cd; color: #856404; }
    .sell { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">19th Hole Investment Club<br>Share Evaluator</h1>', unsafe_allow_html=True)

# Sidebar for company search
st.sidebar.header("📊 Stock Analysis")
st.sidebar.markdown("Enter a ticker symbol or company name:")

search_input = st.sidebar.text_input(
    "Company/Ticker", 
    placeholder="e.g., AAPL, Microsoft, Tesla",
    help="Enter US stock ticker symbols or company names. International stocks may have limited availability."
)

st.sidebar.markdown("""
**Examples:**
- US Stocks: AAPL, MSFT, GOOGL, TSLA
- Company Names: Apple, Microsoft, Tesla
- Note: Focus on US markets for best data coverage
""")

if search_input:
    with st.spinner(f"Fetching data for {search_input}..."):
        stock_data = alpha_vantage_fetcher.fetch_stock_data(search_input)
    
    # Handle multiple company matches
    if stock_data and "company_matches" in stock_data:
        company_matches = stock_data["company_matches"]
        
        st.info("Multiple companies found. Please select the correct one:")
        
        # Create a selection widget for multiple matches
        company_options = list(company_matches.keys())
        selected_company = st.selectbox("Select Company:", company_options)
        
        # Get the ticker for the selected company
        selected_ticker = company_matches[selected_company]
        st.write(f"Selected: {selected_company} → {selected_ticker}")
        
        # Add a button to confirm and analyze the selected company
        if st.button("Analyze Selected Company", type="primary"):
            with st.spinner(f"Fetching data for {selected_ticker}..."):
                # Now fetch the actual stock data for the selected ticker
                stock_data = alpha_vantage_fetcher.fetch_stock_data(selected_ticker)
    
    if stock_data and "error" not in stock_data and "company_matches" not in stock_data:
        # Extract key information with error handling
        try:
            company_name = stock_data.get('name', 'Unknown Company')
            ticker = stock_data.get('ticker', search_input.upper())
            sector = stock_data.get('sector', 'Technology')
            current_price = stock_data.get('current_price', 0)
            parameters = stock_data.get('parameters', {})
            data_confidence = stock_data.get('data_confidence', {})
            
            # Debug information
            st.sidebar.write("Debug: Data structure received")
            st.sidebar.json(stock_data)
            
        except Exception as e:
            st.error(f"Error processing stock data: {str(e)}")
            st.json(stock_data)  # Show the actual data structure
            st.stop()
        
        # Create comprehensive evaluation table
        evaluation_df, nineteen_h_score, total_weighted, total_possible = create_evaluation_table(stock_data)
        
        # Display company header with 19H score
        display_company_header(stock_data, nineteen_h_score)
        
        st.markdown("---")
        
        # Main evaluation table
        st.header("📊 19th Hole Investment Club - Share Evaluation")
        
        st.markdown(f"""
        **Company:** {company_name} ({ticker}) | **Sector:** {sector} | **19H Score:** {nineteen_h_score:.1f}%
        
        This table shows the 10 most important parameters for evaluating {sector} sector stocks:
        - **Importance (d):** Sector-specific weighting (10 = vital, 1 = irrelevant)
        - **Performance (e):** Company performance rating (10 = excellent, 1 = very poor)
        - **Weighted Score:** Performance × Importance
        - **19H Score:** Total weighted score ÷ Maximum possible score × 100
        """)
        
        # Display styled evaluation table
        styled_table = style_evaluation_table(evaluation_df)
        st.dataframe(styled_table, use_container_width=True, height=400)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Weighted Score", f"{total_weighted:.1f}")
        with col2:
            st.metric("Maximum Possible", f"{total_possible:.1f}")
        with col3:
            st.metric("19H Score", f"{nineteen_h_score:.1f}%")
        with col4:
            # Calculate average performance
            avg_performance = evaluation_df['Performance (e)'].astype(float).mean()
            st.metric("Average Performance", f"{avg_performance:.1f}/10")
        
        # Visual analysis chart
        st.header("📈 Parameter Performance vs Importance Analysis")
        performance_chart = create_parameter_chart(evaluation_df, sector)
        st.plotly_chart(performance_chart, use_container_width=True)
        
        # Sector insights
        display_sector_insights(sector, evaluation_df)
        
        # Latest news
        st.header("📰 Latest News")
        try:
            news_data = fetch_stock_news(company_name, ticker, max_articles=3)
            if news_data and not isinstance(news_data, dict):
                for article in news_data[:3]:
                    with st.expander(f"📰 {article['title'][:100]}..."):
                        st.write(f"**Source:** {article['source']['name']}")
                        st.write(f"**Published:** {article['publishedAt'][:10]}")
                        if article.get('description'):
                            st.write(article['description'])
                        if article.get('url'):
                            st.link_button("Read Full Article", article['url'])
            else:
                st.info("No recent news available for this company.")
        except Exception as e:
            st.warning("Unable to fetch news at this time.")
        
        # Parameter explanations
        with st.expander("📚 Parameter Explanations"):
            st.markdown("""
            **P/E Ratio**: Price-to-Earnings ratio - Lower values often indicate better value
            
            **Revenue Growth**: Year-over-year revenue growth percentage - Higher is better
            
            **Return on Equity**: How efficiently the company uses shareholders' equity - Higher is better
            
            **Debt/Equity**: Company's debt relative to equity - Lower is generally safer
            
            **Free Cash Flow Yield**: Cash generation relative to market value - Higher is better
            
            **Dividend Yield**: Annual dividend as percentage of stock price - Important for income investors
            
            **EPS Growth**: Earnings per share growth - Higher indicates improving profitability
            
            **P/B Ratio**: Price-to-Book ratio - Lower values may indicate undervaluation
            
            **Current Ratio**: Ability to pay short-term obligations - Around 1.5-3.0 is ideal
            
            **Operating Margin**: Operational efficiency measure - Higher indicates better management
            """)
        
    elif stock_data and "error" in stock_data:
        st.error(f"Error: {stock_data['error']}")
        st.info("Please verify the ticker symbol is correct or try again later.")
    else:
        st.warning("No data received. Please check your input and try again.")

else:
    # Welcome screen
    st.markdown("""
    ## Welcome to The 19th Hole Investment Club Share Evaluator
    
    This platform evaluates stocks using a refined **10-parameter framework** specifically designed for UK and US markets.
    
    ### 🎯 Key Features:
    - **Sector-specific weightings** for accurate evaluation
    - **Real-time financial data** from Alpha Vantage
    - **Comprehensive scoring** across 10 critical metrics
    - **Investment recommendations** with risk assessment
    - **Latest company news** integration
    
    ### 📊 The 10 Core Parameters:
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
    
    **Get started by entering a ticker symbol or company name in the sidebar.**
    """)
    
    # Display sample analysis
    st.subheader("📈 Sample Analysis")
    st.info("Try entering: AAPL, MSFT, GOOGL, TSLA, or any other US stock ticker")

# Share Evaluation Form
st.header("Share Evaluation Form")

# Form for share input
with st.form(key='ticker_form'):
    # Use a single column layout with a custom-styled button
    ticker = st.text_input("Enter Company Name or Ticker Symbol (e.g., 'Apple', 'AAPL', 'Toyota', '7203.T')")
    
    # Help text
    st.caption("You can enter either a company name like 'Apple' or a ticker symbol like 'AAPL'")
    
    # Center the button with a fixed width
    col1, col2, col3 = st.columns([4, 2, 4])
    
    with col2:
        fetch_button = st.form_submit_button("Analyze Company")

# Process fetch request
if ticker and fetch_button:
    # Save the current ticker
    st.session_state.last_ticker = ticker
    with st.spinner(f"Fetching data for {ticker}..."):
        # First, check if this is a company name that needs to be resolved
        is_likely_ticker = (ticker.isupper() and len(ticker) <= 5) or '.' in ticker
        search_input = ticker
        
        if not is_likely_ticker:
            # Try to find the ticker for the company name
            with st.spinner(f"Finding ticker symbol for '{ticker}'..."):
                company_matches = search_company(ticker)
                
                if company_matches:
                    # If multiple companies match, let the user select one
                    if len(company_matches) > 1:
                        st.info(f"Found {len(company_matches)} possible matches for '{ticker}'. Please select the correct company:")
                        
                        # Create a radio selection of companies
                        company_options = [f"{company} ({ticker})" for company, ticker in company_matches.items()]
                        selected_option = st.radio("Select the correct company:", company_options)
                        
                        # Extract the selected company and ticker
                        selected_company = selected_option.split(" (")[0]
                        selected_ticker = company_matches[selected_company]
                        
                        st.success(f"You selected: {selected_company} (Ticker: {selected_ticker})")
                        search_input = selected_ticker
                    else:
                        # Single match, use it automatically
                        company_name = list(company_matches.keys())[0]
                        ticker_symbol = company_matches[company_name]
                        st.info(f"Found company: {company_name} (Ticker: {ticker_symbol})")
                        # Use the discovered ticker symbol instead of the company name
                        search_input = ticker_symbol
                else:
                    st.error(f"Could not find a matching company for '{ticker}'")
                    st.info("""Tips for finding companies:
                    • Try the full name (e.g., 'Coca-Cola' instead of 'Coke')
                    • Try common abbreviations (e.g., 'IBM' instead of 'International Business Machines')
                    • For UK companies, try both formats (e.g., 'Marks and Spencer' or 'M&S')
                    """)
        
        # Attempt to fetch stock data
        stock_data = alpha_vantage_fetcher.fetch_stock_data(search_input)
        
        # Check if we got multiple company matches
        if stock_data and "company_matches" in stock_data:
            company_matches = stock_data["company_matches"]
            st.info(f"Found {len(company_matches)} possible matches for '{ticker}'. Please select the correct company:")
            
            # Create a radio selection of companies
            company_options = [f"{company} ({ticker})" for company, ticker in company_matches.items()]
            selected_option = st.radio("Select the correct company:", company_options)
            
            # Extract the selected company and ticker
            selected_company = selected_option.split(" (")[0]
            selected_ticker = company_matches[selected_company]
            
            # Show the user their selection
            st.success(f"You selected: {selected_company} (Ticker: {selected_ticker})")
            
            # Add a button to confirm and analyze the selected company
            if st.button("Analyze Selected Company", type="primary"):
                with st.spinner(f"Fetching data for {selected_ticker}..."):
                    # Now fetch the actual stock data for the selected ticker
                    stock_data = alpha_vantage_fetcher.fetch_stock_data(selected_ticker)
        
        if stock_data and "company_matches" not in stock_data:
            # Use standard stock data for now to avoid rate limiting issues
            sector = stock_data['sector']
            parameters = stock_data['parameters']
            data_confidence = stock_data.get('data_confidence', {})
            
            # Get the sector-specific weightings for refined 10-parameter system
            weightings = get_sector_specific_weights(sector)
            
            # Calculate parameter scores using refined evaluation system
            param_scores = {}
            for param, value in parameters.items():
                if pd.isna(value):
                    # For missing data, use a neutral score (5)
                    param_scores[param] = 5.0
                else:
                    try:
                        # Use refined parameter scoring
                        param_scores[param] = calculate_parameter_score(param, value, sector)
                    except:
                        # Fall back to original scoring
                        param_scores[param] = calculate_parameter_score(param, value)
            
            # Check for low-scoring parameters (below 4)
            low_scoring_params = {}
            for param, score in param_scores.items():
                if score < 4.0:
                    low_scoring_params[param] = score
            
            # Calculate investment score using the parameter scores
            weighted_score_sum = sum(param_scores[param] * weightings[param] for param in parameters.keys())
            investment_score = weighted_score_sum
            
            # Generate buy confidence classification
            try:
                buy_confidence = generate_buy_confidence(stock_data, param_scores, investment_score)
                strengths, vulnerabilities = identify_strengths_vulnerabilities(param_scores)
            except:
                buy_confidence = None
                strengths, vulnerabilities = [], []
            
            # Create evaluation result
            evaluation_result = {
                "name": stock_data['name'],
                "ticker": search_input,
                "sector": sector,
                "parameters": parameters,
                "weightings": weightings,
                "param_scores": param_scores,
                "investment_score": investment_score,
                "low_scoring_params": low_scoring_params,
                "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Store in session state
            st.session_state.evaluated_shares.append(evaluation_result)
            
            # Display the results
            st.success(f"Evaluation Complete: {stock_data['name']} ({search_input})")
            
            # Display current price and 52-week range
            price_info = stock_data.get('price_info', {})
            if price_info:
                current_price = price_info.get('current_price')
                fifty_two_week_high = price_info.get('fifty_two_week_high')
                fifty_two_week_low = price_info.get('fifty_two_week_low')
                currency = price_info.get('currency', 'USD')
                
                # Create a formatted currency symbol
                currency_symbol = "£" if currency in ["GBP", "GBp"] else "$" if currency in ["USD", "CAD"] else "€" if currency == "EUR" else "¥" if currency in ["JPY", "CNY"] else currency
                
                # Create price box
                price_col1, price_col2, price_col3 = st.columns(3)
                
                with price_col1:
                    if current_price is not None:
                        st.metric("Current Price", f"{currency_symbol}{current_price:.2f}")
                
                with price_col2:
                    if fifty_two_week_low is not None:
                        st.metric("52-Week Low", f"{currency_symbol}{fifty_two_week_low:.2f}")
                
                with price_col3:
                    if fifty_two_week_high is not None:
                        st.metric("52-Week High", f"{currency_symbol}{fifty_two_week_high:.2f}")
            
            # Full width layout for main evaluation
            st.header("EVALUATION RESULTS")
            
            # Recommendation box based on total score only
            # Out of a possible 1300 (13 params * 10 weight * 10 score)
            max_possible = 1300
            score_percent = (investment_score / max_possible) * 100
            
            # Create a colorful container for the score
            score_color = "#00cc00"  # Green for good scores
            if score_percent < 60:
                score_color = "#ffaa00"  # Orange for medium scores
            if score_percent < 40:
                score_color = "#ff4444"  # Red for poor scores
                
            # Apply a custom CSS style first
            st.markdown("""
            <style>
            .big-score-container {
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .score-value {
                font-size: 60px;
                font-weight: bold;
                margin: 0;
            }
            .score-label {
                font-size: 24px;
                color: #444;
                margin-top: 5px;
            }
            .max-score {
                font-size: 18px;
                color: #666;
            }
            .score-percentage {
                font-size: 28px;
                margin-top: 5px;
            }
            .recommendation {
                font-size: 32px;
                font-weight: bold;
                margin-top: 10px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Then create the HTML elements separately to avoid formatting issues
            st.markdown(f"""
            <div class="big-score-container">
                <p class="score-label">INVESTMENT SCORE</p>
                <p class="score-value" style="color: {score_color};">{investment_score:.1f}</p>
                <p class="max-score">out of 1300 points (13-parameter system)</p>
                <p class="score-percentage" style="color: {score_color};">({score_percent:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add enhanced buy confidence if available
            if buy_confidence:
                st.markdown(f'<p class="recommendation" style="color: {score_color}; font-size: 28px;">{buy_confidence}</p>', unsafe_allow_html=True)
            else:
                # Fall back to traditional recommendations
                if investment_score >= 975:  # 75% of 1300
                    st.markdown('<p class="recommendation" style="color: #00cc00;">STRONG BUY</p>', unsafe_allow_html=True)
                elif investment_score >= 650:  # 50% of 1300
                    st.markdown('<p class="recommendation" style="color: #00cc00;">BUY</p>', unsafe_allow_html=True)
                elif investment_score >= 390:  # 30% of 1300
                    st.markdown('<p class="recommendation" style="color: #ffaa00;">CAUTIOUS BUY</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="recommendation" style="color: #ff4444;">NOT RECOMMENDED</p>', unsafe_allow_html=True)
            
            # Enhanced strengths and vulnerabilities analysis
            if strengths or vulnerabilities:
                col1, col2 = st.columns(2)
                
                with col1:
                    if strengths:
                        st.subheader("💪 Key Strengths")
                        for strength in strengths[:5]:  # Show top 5
                            st.success(f"✓ {strength}")
                            
                with col2:
                    if vulnerabilities:
                        st.subheader("⚠️ Key Vulnerabilities") 
                        for vulnerability in vulnerabilities[:5]:  # Show top 5
                            st.error(f"⚠ {vulnerability}")
            
            # Low scoring parameters fallback
            if low_scoring_params and not vulnerabilities:
                st.subheader("Low Scoring Parameters")
                st.info(f"The following {len(low_scoring_params)} parameter(s) scored below 4.0/10 - These are highlighted in red in the table below")
            
            # Create a table of all parameters and their scores
            st.subheader("Parameter Evaluation")
            
            # Calculate parameter scores with better handling of missing data
            param_scores = {}
            for param, value in parameters.items():
                if pd.isna(value):
                    # For missing data, use a neutral score (5)
                    param_scores[param] = 5.0
                else:
                    param_scores[param] = calculate_parameter_score(param, value)
            
            # Check if we have data confidence information
            data_confidence = stock_data.get('data_confidence', {})
            
            # Get ticker symbol from stock data
            ticker_symbol = stock_data.get('ticker', '')
            
            # Create a dataframe for the table, with better handling of raw values and missing data
            raw_values = []
            for param, v in parameters.items():
                if pd.isna(v):
                    raw_values.append("Not available")
                elif isinstance(v, (int, float)):
                    # Format based on parameter type
                    if param in ["Yield", "EBIT Growth", "Turnover Growth"]:
                        raw_values.append(f"{v:.2f}%")
                    elif param == "Market Cap":
                        # Check if it's a UK stock (London Stock Exchange)
                        is_uk_stock = ticker_symbol and isinstance(ticker_symbol, str) and ticker_symbol.endswith('.L')
                        raw_values.append(f"£{v:.1f}M" if is_uk_stock else f"${v:.1f}M")
                    elif param == "Debt/Equity":
                        raw_values.append(f"{v:.2f}")
                    else:
                        raw_values.append(f"{v:.2f}")
                else:
                    raw_values.append(str(v))
            
            # Create scores with proper handling of missing data
            score_values = []
            for param in parameters.keys():
                score = param_scores.get(param, None)
                if score is None or pd.isna(score):
                    score_values.append("N/A")
                else:
                    score_values.append(f"{score:.1f}")
            
            # Create weighted scores with proper handling of missing data
            weighted_values = []
            for param in parameters.keys():
                score = param_scores.get(param, None)
                if score is None or pd.isna(score):
                    weighted_values.append("N/A")
                else:
                    weighted_values.append(f"{score * weightings[param]:.1f}")
            
            # Create a dataframe for the table, with fewer columns to fit on one page
            df_params = pd.DataFrame({
                "Parameter": list(parameters.keys()),
                "Raw Value": raw_values,
                "Score (1-10)": score_values,
                "Weight (1-10)": [weightings[param] for param in parameters.keys()],
                "Weighted": weighted_values,
                "Data Quality": [data_confidence.get(param, "N/A") for param in parameters.keys()]
            })
            
            # Create a clean dataframe with minimal styling
            # Only highlight parameters that score below 4
            def style_dataframe(df):
                # Create a stylable dataframe
                styled_df = df.style
                
                # Highlight only low-scoring parameters with red text
                styled_df = styled_df.apply(lambda x: [
                    'color: #cc0000; font-weight: bold;' if param in low_scoring_params else '' 
                    for param in parameters.keys()
                ], axis=0, subset=["Parameter"])
                
                # Format all cells with minimal styling
                styled_df = styled_df.set_properties(**{
                    'text-align': 'center',
                    'font-size': '14px',
                    'padding': '6px'
                })
                
                # Make parameter column bold with left alignment
                styled_df = styled_df.set_properties(
                    subset=['Parameter'],
                    **{'font-weight': 'bold', 'text-align': 'left'}
                )
                
                return styled_df
                
            # Display the styled dataframe with increased height
            st.dataframe(
                style_dataframe(df_params), 
                use_container_width=True,
                height=425  # Increased height for better visibility
            )
            
            # Charts side by side
            charts_col1, charts_col2 = st.columns(2)
            
            with charts_col1:
                # Pie chart for score distribution
                st.subheader("Score Distribution")
                
                # Calculate weighted contribution of each parameter with better handling of missing data
                pie_param_scores = {}
                for param, value in parameters.items():
                    if pd.isna(value):
                        # For missing data, use a neutral score (5)
                        pie_param_scores[param] = 5.0
                    else:
                        pie_param_scores[param] = calculate_parameter_score(param, value)
                        
                weighted_scores = {param: pie_param_scores[param] * weightings[param] for param in parameters.keys()}
                
                # Create a dataframe for the pie chart
                df_contributions = pd.DataFrame({
                    "Parameter": list(weighted_scores.keys()),
                    "Contribution": list(weighted_scores.values())
                })
                
                # Make sure all contributions are positive for pie chart
                df_contributions["Contribution"] = df_contributions["Contribution"].apply(lambda x: max(0.1, x))
                
                fig = px.pie(
                    df_contributions,
                    names="Parameter",
                    values="Contribution",
                    title=f"Score Distribution (Total: {investment_score:.1f}/1300)",
                    height=450,  # Increase chart height
                    color_discrete_sequence=px.colors.qualitative.Set3  # Better colors for 13 parameters
                )
                fig.update_traces(textposition='inside', textinfo='percent', textfont_size=10)
                fig.update_layout(showlegend=True, legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01))
                st.plotly_chart(fig, use_container_width=True)
            
            with charts_col2:
                # Radar chart for parameter scores
                st.subheader("Parameter Performance")
                st.caption("This chart shows each parameter's score on a scale of 0-1 (where 1 is best). The larger the area, the better the overall performance.")
                
                # Use parameter scores for radar chart (normalized to 0-1 scale)
                normalized_values = []
                valid_params = []
                
                for param in parameters.keys():
                    # Check if we have a valid score for this parameter
                    score = param_scores.get(param)
                    
                    # Skip parameters without valid scores
                    if score is None or pd.isna(score):
                        continue
                        
                    # Add to our valid parameters list
                    valid_params.append(param)
                    
                    # Normalize score to 0-1 scale
                    normalized = min(1.0, max(0.0, score / 10))  # Convert 0-10 score to 0-1 scale
                    normalized_values.append(normalized)
                
                # Create radar chart
                fig = go.Figure()
                
                # Only create the chart if we have valid parameters
                if valid_params:
                    fig.add_trace(go.Scatterpolar(
                        r=normalized_values,
                        theta=valid_params,
                        fill='toself',
                        name=stock_data['name']
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1],
                                tickfont=dict(size=12),
                                tickvals=[0.2, 0.4, 0.6, 0.8, 1.0]
                            )
                        ),
                        showlegend=False,
                        height=450,  # Increase chart height
                        title="Parameter Scores (0-10 Scale)",
                        font=dict(size=14)
                    )
                    
                    # Make the radar chart lines thicker with a more vibrant color
                    fig.update_traces(
                        line=dict(width=3, color="#0068c9"),
                        marker=dict(size=8, color="#0068c9"),
                        fillcolor="rgba(0, 104, 201, 0.3)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough valid data to generate radar chart")
            
            # Add enhanced investment summary section
            st.header("Investment Analysis Summary")
            
            # Create summary metrics in columns
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                # Fundamental Score
                fundamental_params = ['Revenue Growth', 'Free Cash Flow Yield', 'ROIC', 'Debt/Equity', 'Dividend Yield', 'EPS Growth', 'P/E Ratio']
                fundamental_scores = [param_scores.get(param, 5.0) for param in fundamental_params if param in param_scores]
                if fundamental_scores:
                    fundamental_avg = sum(fundamental_scores) / len(fundamental_scores)
                    st.metric("Fundamental Score", f"{fundamental_avg:.1f}/10", 
                             delta=f"{fundamental_avg-5:.1f} vs neutral" if fundamental_avg != 5 else None)
                
            with summary_col2:
                # Technical Score  
                technical_params = ['50-day MA', '200-day MA', 'RSI', 'Volume Trend']
                technical_scores = [param_scores.get(param, 5.0) for param in technical_params if param in param_scores]
                if technical_scores:
                    technical_avg = sum(technical_scores) / len(technical_scores)
                    st.metric("Technical Score", f"{technical_avg:.1f}/10",
                             delta=f"{technical_avg-5:.1f} vs neutral" if technical_avg != 5 else None)
                
            with summary_col3:
                # Sentiment Score
                sentiment_params = ['Analyst Ratings', 'Price Target vs Current']
                sentiment_scores = [param_scores.get(param, 5.0) for param in sentiment_params if param in param_scores]
                if sentiment_scores:
                    sentiment_avg = sum(sentiment_scores) / len(sentiment_scores)
                    st.metric("Sentiment Score", f"{sentiment_avg:.1f}/10",
                             delta=f"{sentiment_avg-5:.1f} vs neutral" if sentiment_avg != 5 else None)
                
            with summary_col4:
                # Risk Assessment
                risk_params = ['Debt/Equity', 'RSI']  # Higher debt and extreme RSI indicate risk
                debt_score = param_scores.get('Debt/Equity', 5.0)
                rsi_score = param_scores.get('RSI', 5.0)
                
                # Risk calculation (inverse of debt burden, normalized RSI)
                debt_risk = 10 - debt_score if debt_score <= 10 else 1
                rsi_risk = 10 - abs(rsi_score - 5) if 'RSI' in param_scores else 5
                risk_score = (debt_risk + rsi_risk) / 2
                
                risk_color = "normal"
                if risk_score >= 7:
                    risk_color = "normal"
                elif risk_score >= 5:
                    risk_color = "off"
                else:
                    risk_color = "inverse"
                    
                st.metric("Risk Score", f"{risk_score:.1f}/10", 
                         delta=f"{'Low' if risk_score >= 7 else 'Medium' if risk_score >= 5 else 'High'} Risk")
            
            # Fetch and display news
            st.header(f"Latest News for {stock_data['name']}")
            
            with st.spinner("Fetching latest news..."):
                # Pass both company name and ticker symbol to support fallback to Yahoo Finance
                news_result = fetch_stock_news(stock_data['name'], ticker_symbol=stock_data.get('symbol'), max_articles=5)
                
                # Check if it's an error response
                if isinstance(news_result, dict) and "error" in news_result:
                    if news_result["error"] == "api_key_missing":
                        st.warning("⚠️ NEWS_API_KEY is missing. News cannot be displayed.")
                    else:
                        st.warning(f"⚠️ Error retrieving news: {news_result.get('message', 'Unknown error')}")
                # If it's a list, it contains articles
                elif news_result:
                    for article in news_result:
                        with st.expander(f"{article['title']} - {article['source']['name']}"):
                            st.write(f"**Published**: {article['publishedAt'][:10]}")
                            if article.get('description'):
                                st.write(f"**Description**: {article['description']}")
                            st.write(f"[Read full article]({article['url']})")
                else:
                    st.info(f"No recent news found for {stock_data['name']}")
        # Only show error if no data was found AND we don't have company matches
        elif not stock_data or (stock_data and "company_matches" not in stock_data):
            st.error(f"Could not find data for '{search_input}'. Please check the name or try a different company.")
            st.info("""Tips for finding companies:
            • Try using the company's most common name (e.g., 'Apple' instead of 'Apple Inc.')
            • You can also use ticker symbols directly:
              - US stocks: AAPL, MSFT, AMZN
              - UK stocks: Add .L (e.g., TSCO.L for Tesco)
              - Japanese stocks: Add .T (e.g., 7203.T for Toyota)
              - Hong Kong stocks: Add .HK (e.g., 0700.HK for Tencent)
            """)
