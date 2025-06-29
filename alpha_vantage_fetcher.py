"""
Alpha Vantage Data Fetcher
Reliable financial data source using Alpha Vantage API
"""

import os
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import json

class AlphaVantageDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = 'https://www.alphavantage.co/query'
        self.last_request_time = 0
        self.request_interval = 12  # Alpha Vantage free tier: 5 requests per minute
        
    def _make_request(self, params):
        """Make rate-limited request to Alpha Vantage API"""
        # Enforce rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API error messages
                if 'Error Message' in data:
                    return {'error': data['Error Message']}
                elif 'Note' in data:
                    return {'error': 'API call frequency limit reached. Please try again later.'}
                else:
                    return data
            else:
                return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout - please try again'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except json.JSONDecodeError:
            return {'error': 'Invalid response format'}
    
    def get_company_overview(self, symbol):
        """Get fundamental company data"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        return self._make_request(params)
    
    def get_daily_prices(self, symbol):
        """Get daily price data"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full'
        }
        return self._make_request(params)
    
    def get_technical_indicators(self, symbol, indicator='RSI'):
        """Get technical indicators"""
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': 'daily',
            'time_period': 14,
            'series_type': 'close'
        }
        return self._make_request(params)
    
    def search_symbol(self, query):
        """Search for stock symbols using company name"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': query
        }
        return self._make_request(params)
    
    def fetch_stock_data(self, input_value):
        """
        Fetch comprehensive stock data using Alpha Vantage API
        Handles both ticker symbols and company names
        """
        input_value = input_value.strip()
        
        # Check if it's likely a ticker symbol (short and mostly uppercase)
        if len(input_value) <= 6 and input_value.replace('.', '').replace('-', '').isalpha():
            ticker_symbol = input_value.upper()
            print(f"Fetching data for ticker {ticker_symbol} using Alpha Vantage...")
            
            # Try direct lookup first
            overview_data = self.get_company_overview(ticker_symbol)
            if 'error' not in overview_data and overview_data.get('Symbol') == ticker_symbol:
                # Direct lookup successful
                price_data = self.get_daily_prices(ticker_symbol)
                if 'error' in price_data:
                    return {"error": f"Unable to fetch price data for {ticker_symbol}: {price_data['error']}"}
                
                try:
                    return self._process_alpha_vantage_data(ticker_symbol, overview_data, price_data)
                except Exception as e:
                    return {"error": f"Error processing data for {ticker_symbol}: {str(e)}"}
            else:
                return {"error": f"No data found for ticker symbol '{ticker_symbol}'. For international stocks, try company name search or verify the correct ticker format."}
        else:
            # Treat as company name - search for symbols
            print(f"Searching for company '{input_value}' using Alpha Vantage...")
            search_results = self.search_symbol(input_value)
            
            if 'error' in search_results:
                return {"error": f"Unable to search for '{input_value}': {search_results['error']}"}
            
            best_matches = search_results.get('bestMatches', [])
            if not best_matches:
                return {"error": f"No companies found matching '{input_value}'. Try using the exact ticker symbol instead."}
            
            # Filter for US/major exchanges and high match scores
            viable_matches = []
            for match in best_matches:
                symbol = match.get('1. symbol', '')
                name = match.get('2. name', '')
                region = match.get('4. region', '')
                match_score = float(match.get('9. matchScore', '0'))
                
                # Prioritize US stocks and high match scores
                if region == 'United States' and match_score >= 0.5:
                    viable_matches.append({
                        'symbol': symbol,
                        'name': name,
                        'region': region,
                        'score': match_score
                    })
            
            if not viable_matches:
                # Show all matches if no US matches found
                viable_matches = []
                for match in best_matches[:5]:
                    symbol = match.get('1. symbol', '')
                    name = match.get('2. name', '')
                    region = match.get('4. region', '')
                    match_score = float(match.get('9. matchScore', '0'))
                    
                    if match_score >= 0.3:
                        viable_matches.append({
                            'symbol': symbol,
                            'name': name,
                            'region': region,
                            'score': match_score
                        })
                
                if not viable_matches:
                    return {"error": f"No suitable matches found for '{input_value}'. Please try a more specific company name or ticker symbol."}
            
            # If single high-confidence US match, fetch directly
            if len(viable_matches) == 1 and viable_matches[0]['region'] == 'United States' and viable_matches[0]['score'] >= 0.8:
                best_symbol = viable_matches[0]['symbol']
                return self.fetch_stock_data(best_symbol)
            
            # Multiple matches - return for user selection
            match_dict = {}
            for match in viable_matches:
                display_name = f"{match['name']} ({match['region']}) - Score: {match['score']:.2f}"
                match_dict[display_name] = match['symbol']
            
            return {"company_matches": match_dict}
    
    def _process_alpha_vantage_data(self, ticker_symbol, overview, price_data):
        """Process Alpha Vantage data into our standard format"""
        try:
            # Basic company information
            company_name = overview.get('Name', ticker_symbol)
            sector = overview.get('Sector', 'TECHNOLOGY')  # Default to TECHNOLOGY if missing
            
            # Normalize sector name
            if sector:
                sector = sector.title()  # Convert "TECHNOLOGY" to "Technology"
            
            # Current price and 52-week range
            current_price = float(overview.get('Price', 0)) if overview.get('Price') else None
            fifty_two_week_high = float(overview.get('52WeekHigh', 0)) if overview.get('52WeekHigh') else None
            fifty_two_week_low = float(overview.get('52WeekLow', 0)) if overview.get('52WeekLow') else None
            
            # Process daily price data for technical analysis
            time_series = price_data.get('Time Series (Daily)', {})
            if not time_series:
                return {"error": f"No price history available for {ticker_symbol}"}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df.index = pd.to_datetime(df.index)
            df = df.astype(float).sort_index()
            
            if df.empty:
                return {"error": f"No valid price data for {ticker_symbol}"}
            
            # Get current price from latest data if not available in overview
            if not current_price:
                current_price = df['Close'].iloc[-1]
            
            # Initialize parameters dictionary for refined 10-parameter system
            parameters = {}
            data_confidence = {}
            
            # 1. P/E Ratio (Primary valuation metric)
            pe_ratio = overview.get('PERatio')
            if pe_ratio and pe_ratio != 'None' and pe_ratio != '-':
                parameters['P/E Ratio'] = float(pe_ratio)
                data_confidence['P/E Ratio'] = "High"
            else:
                parameters['P/E Ratio'] = np.nan
                data_confidence['P/E Ratio'] = "Not available"
            
            # 2. Revenue Growth (YoY)
            revenue_growth = overview.get('QuarterlyRevenueGrowthYOY')
            if revenue_growth and revenue_growth != 'None' and revenue_growth != '-':
                parameters['Revenue Growth'] = float(revenue_growth) * 100
                data_confidence['Revenue Growth'] = "High"
            else:
                parameters['Revenue Growth'] = np.nan
                data_confidence['Revenue Growth'] = "Not available"
            
            # 3. Return on Equity (ROE)
            roe = overview.get('ReturnOnEquityTTM')
            if roe and roe != 'None' and roe != '-':
                parameters['Return on Equity'] = float(roe) * 100
                data_confidence['Return on Equity'] = "High"
            else:
                parameters['Return on Equity'] = np.nan
                data_confidence['Return on Equity'] = "Not available"
            
            # 4. Debt/Equity Ratio
            debt_to_equity = overview.get('DebtToEquityRatio')
            if debt_to_equity and debt_to_equity != 'None' and debt_to_equity != '-':
                parameters['Debt/Equity'] = float(debt_to_equity)
                data_confidence['Debt/Equity'] = "High"
            else:
                parameters['Debt/Equity'] = np.nan
                data_confidence['Debt/Equity'] = "Not available"
            
            # 5. Free Cash Flow Yield (using operating cash flow as proxy)
            operating_cash_flow = overview.get('OperatingCashflowTTM')
            market_cap = overview.get('MarketCapitalization')
            if (operating_cash_flow and market_cap and 
                operating_cash_flow != 'None' and market_cap != 'None' and
                operating_cash_flow != '-' and market_cap != '-'):
                try:
                    ocf = float(operating_cash_flow)
                    mc = float(market_cap)
                    if mc > 0:
                        parameters['Free Cash Flow Yield'] = (ocf / mc) * 100
                        data_confidence['Free Cash Flow Yield'] = "Medium"
                    else:
                        parameters['Free Cash Flow Yield'] = np.nan
                        data_confidence['Free Cash Flow Yield'] = "Not available"
                except (ValueError, TypeError):
                    parameters['Free Cash Flow Yield'] = np.nan
                    data_confidence['Free Cash Flow Yield'] = "Not available"
            else:
                parameters['Free Cash Flow Yield'] = np.nan
                data_confidence['Free Cash Flow Yield'] = "Not available"
            
            # 6. Dividend Yield
            dividend_yield = overview.get('DividendYield')
            if dividend_yield and dividend_yield != 'None' and dividend_yield != '-':
                parameters['Dividend Yield'] = float(dividend_yield) * 100
                data_confidence['Dividend Yield'] = "High"
            else:
                parameters['Dividend Yield'] = 0.0  # No dividend
                data_confidence['Dividend Yield'] = "High"
            
            # 7. EPS Growth
            eps_growth = overview.get('QuarterlyEarningsGrowthYOY')
            if eps_growth and eps_growth != 'None' and eps_growth != '-':
                parameters['EPS Growth'] = float(eps_growth) * 100
                data_confidence['EPS Growth'] = "High"
            else:
                parameters['EPS Growth'] = np.nan
                data_confidence['EPS Growth'] = "Not available"
            
            # 8. P/B Ratio (Price-to-Book)
            pb_ratio = overview.get('PriceToBookRatio')
            if pb_ratio and pb_ratio != 'None' and pb_ratio != '-':
                parameters['P/B Ratio'] = float(pb_ratio)
                data_confidence['P/B Ratio'] = "High"
            else:
                parameters['P/B Ratio'] = np.nan
                data_confidence['P/B Ratio'] = "Not available"
            
            # 9. Current Ratio (Liquidity measure)
            current_ratio = overview.get('CurrentRatio')
            if current_ratio and current_ratio != 'None' and current_ratio != '-':
                parameters['Current Ratio'] = float(current_ratio)
                data_confidence['Current Ratio'] = "High"
            else:
                parameters['Current Ratio'] = np.nan
                data_confidence['Current Ratio'] = "Not available"
            
            # 10. Operating Margin (Profitability measure)
            operating_margin = overview.get('OperatingMarginTTM')
            if operating_margin and operating_margin != 'None' and operating_margin != '-':
                parameters['Operating Margin'] = float(operating_margin) * 100
                data_confidence['Operating Margin'] = "High"
            else:
                parameters['Operating Margin'] = np.nan
                data_confidence['Operating Margin'] = "Not available"
            
            return {
                'name': company_name,
                'ticker': ticker_symbol,
                'sector': sector,
                'current_price': current_price,
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_two_week_low': fifty_two_week_low,
                'parameters': parameters,
                'data_confidence': data_confidence,
                'currency': 'USD'  # Alpha Vantage primarily provides USD data
            }
            
        except Exception as e:
            return {"error": f"Error processing Alpha Vantage data for {ticker_symbol}: {str(e)}"}

# Global instance
alpha_vantage_fetcher = AlphaVantageDataFetcher()