#!/usr/bin/env python3
"""
Base API integration module for Mood Lifter Hooks.
Provides HTTP client with error handling, retries, and caching.
"""

import json
import time
import hashlib
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class CacheEntry:
    """Represents a cached API response."""
    
    def __init__(self, data: Any, expires_at: datetime):
        self.data = data
        self.expires_at = expires_at
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.expires_at


class APIClient:
    """Base API client with caching, retries, and error handling."""
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
        cache_ttl_minutes: int = 15
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Optional base URL for all requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache_ttl_minutes: Cache time-to-live in minutes
        """
        self.base_url = base_url
        self.timeout = timeout
        self.cache_ttl_minutes = cache_ttl_minutes
        self._cache: Dict[str, CacheEntry] = {}
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "User-Agent": "MoodLifterHooks/1.0 (https://github.com/your-org/mood-lifter-hooks)"
        })
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate a cache key for a URL and parameters."""
        cache_str = url
        if params:
            cache_str += json.dumps(params, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if available and not expired."""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired():
                return entry.data
            else:
                del self._cache[cache_key]
        return None
    
    def _add_to_cache(self, cache_key: str, data: Any):
        """Add data to cache with expiration."""
        expires_at = datetime.now() + timedelta(minutes=self.cache_ttl_minutes)
        self._cache[cache_key] = CacheEntry(data, expires_at)
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
    
    def get(
        self, 
        url: str, 
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Optional[Union[Dict, str]]:
        """
        Make a GET request with caching and error handling.
        
        Args:
            url: URL to request (will be joined with base_url if relative)
            params: Query parameters
            headers: Additional headers
            use_cache: Whether to use caching
            
        Returns:
            Response data (JSON dict or text) or None on error
        """
        # Build full URL
        if self.base_url and not url.startswith(('http://', 'https://')):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(full_url, params)
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            response = self.session.get(
                full_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Try to parse as JSON, otherwise return text
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text
            
            # Cache the response
            if use_cache:
                self._add_to_cache(cache_key, data)
            
            return data
            
        except requests.exceptions.Timeout:
            print(f"Request timeout for {full_url}")
        except requests.exceptions.ConnectionError:
            print(f"Connection error for {full_url}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error {e.response.status_code} for {full_url}")
        except Exception as e:
            print(f"Unexpected error for {full_url}: {e}")
        
        return None
    
    def post(
        self,
        url: str,
        json_data: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Union[Dict, str]]:
        """
        Make a POST request with error handling.
        
        Args:
            url: URL to request
            json_data: JSON data to send
            data: Form data to send
            headers: Additional headers
            
        Returns:
            Response data or None on error
        """
        # Build full URL
        if self.base_url and not url.startswith(('http://', 'https://')):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
        
        try:
            response = self.session.post(
                full_url,
                json=json_data,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Try to parse as JSON, otherwise return text
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
                
        except requests.exceptions.Timeout:
            print(f"Request timeout for {full_url}")
        except requests.exceptions.ConnectionError:
            print(f"Connection error for {full_url}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error {e.response.status_code} for {full_url}")
        except Exception as e:
            print(f"Unexpected error for {full_url}: {e}")
        
        return None


def test_api_client():
    """Test the API client with a sample request."""
    client = APIClient()
    
    # Test with a simple API endpoint
    print("Testing API client with httpbin.org...")
    result = client.get("https://httpbin.org/json")
    if result:
        print(f"Success! Got response with {len(result)} keys")
    else:
        print("Failed to get response")
    
    # Test caching
    print("\nTesting cache...")
    start = time.time()
    client.get("https://httpbin.org/delay/1")
    first_time = time.time() - start
    print(f"First request took {first_time:.2f} seconds")
    
    start = time.time()
    client.get("https://httpbin.org/delay/1")
    second_time = time.time() - start
    print(f"Second request (cached) took {second_time:.2f} seconds")
    
    if second_time < first_time / 2:
        print("Cache is working!")


if __name__ == "__main__":
    test_api_client()