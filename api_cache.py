"""
API Cache and Rate Limiting Module
Handles Yahoo Finance API rate limits and caches responses
"""

import time
import json
import os
from datetime import datetime, timedelta
import hashlib

class APICache:
    def __init__(self, cache_dir="cache", cache_duration_minutes=30):
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.last_request_time = 0
        self.min_request_interval = 1.5  # Minimum seconds between requests
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, ticker_symbol, data_type="stock_info"):
        """Generate a unique cache key for the ticker and data type"""
        key_string = f"{ticker_symbol}_{data_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key):
        """Get the full path to the cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get_cached_data(self, ticker_symbol, data_type="stock_info"):
        """Retrieve cached data if it exists and is still valid"""
        cache_key = self._get_cache_key(ticker_symbol, data_type)
        cache_file = self._get_cache_file_path(cache_key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < self.cache_duration:
                print(f"Using cached data for {ticker_symbol}")
                return cached_data['data']
            else:
                # Cache expired, remove file
                os.remove(cache_file)
                return None
                
        except Exception as e:
            print(f"Error reading cache for {ticker_symbol}: {str(e)}")
            return None
    
    def cache_data(self, ticker_symbol, data, data_type="stock_info"):
        """Store data in cache with timestamp"""
        cache_key = self._get_cache_key(ticker_symbol, data_type)
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'ticker': ticker_symbol,
                'data_type': data_type,
                'data': data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, default=str)
                
        except Exception as e:
            print(f"Error caching data for {ticker_symbol}: {str(e)}")
    
    def enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

# Global cache instance
api_cache = APICache()