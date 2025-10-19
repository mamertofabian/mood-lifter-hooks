#!/usr/bin/env python3
"""
Tests for API integration modules.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.api_integrations import APIClient, CacheEntry


class TestCacheEntry(unittest.TestCase):
    """Test cases for cache entry."""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        data = {"test": "data"}
        expires_at = datetime.now() + timedelta(minutes=10)
        entry = CacheEntry(data, expires_at)
        
        self.assertEqual(entry.data, data)
        self.assertEqual(entry.expires_at, expires_at)
    
    def test_cache_expiry_check(self):
        """Test cache expiry checking."""
        data = {"test": "data"}
        
        # Create expired entry
        expired_time = datetime.now() - timedelta(minutes=10)
        expired_entry = CacheEntry(data, expired_time)
        self.assertTrue(expired_entry.is_expired())
        
        # Create valid entry
        valid_time = datetime.now() + timedelta(minutes=10)
        valid_entry = CacheEntry(data, valid_time)
        self.assertFalse(valid_entry.is_expired())


class TestAPIClient(unittest.TestCase):
    """Test cases for API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient(cache_ttl_minutes=15)
    
    def test_api_client_initialization(self):
        """Test API client initialization."""
        client = APIClient(base_url="https://api.example.com", timeout=20)
        
        self.assertEqual(client.base_url, "https://api.example.com")
        self.assertEqual(client.timeout, 20)
        self.assertIsNotNone(client.session)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        # Test with URL only
        key1 = self.client._get_cache_key("https://api.example.com/data")
        self.assertIsInstance(key1, str)
        self.assertEqual(len(key1), 32)  # MD5 hash length
        
        # Test with URL and params
        key2 = self.client._get_cache_key(
            "https://api.example.com/data",
            {"param1": "value1", "param2": "value2"}
        )
        self.assertIsInstance(key2, str)
        self.assertNotEqual(key1, key2)
        
        # Same params in different order should produce same key
        key3 = self.client._get_cache_key(
            "https://api.example.com/data",
            {"param2": "value2", "param1": "value1"}
        )
        self.assertEqual(key2, key3)
    
    def test_cache_operations(self):
        """Test cache get and add operations."""
        cache_key = "test_key"
        data = {"result": "success"}
        
        # Test empty cache
        self.assertIsNone(self.client._get_from_cache(cache_key))
        
        # Add to cache
        self.client._add_to_cache(cache_key, data)
        
        # Get from cache
        cached_data = self.client._get_from_cache(cache_key)
        self.assertEqual(cached_data, data)
        
        # Test cache expiry
        # Manually expire the entry
        self.client._cache[cache_key].expires_at = datetime.now() - timedelta(minutes=1)
        self.assertIsNone(self.client._get_from_cache(cache_key))
        
        # Entry should be removed after expiry check
        self.assertNotIn(cache_key, self.client._cache)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        # Add some data to cache
        self.client._add_to_cache("key1", {"data": 1})
        self.client._add_to_cache("key2", {"data": 2})
        
        self.assertEqual(len(self.client._cache), 2)
        
        # Clear cache
        self.client.clear_cache()
        self.assertEqual(len(self.client._cache), 0)
    
    @patch('requests.Session.get')
    def test_get_request_success(self, mock_get):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get("https://api.example.com/test")
        
        self.assertEqual(result, {"status": "ok"})
        mock_get.assert_called_once()
        
        # Second call should use cache
        result2 = self.client.get("https://api.example.com/test")
        self.assertEqual(result2, {"status": "ok"})
        mock_get.assert_called_once()  # Still only called once
    
    @patch('requests.Session.get')
    def test_get_request_with_params(self, mock_get):
        """Test GET request with parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        params = {"key": "value", "limit": 10}
        result = self.client.get("https://api.example.com/search", params=params)
        
        self.assertEqual(result, {"data": "test"})
        
        # Verify params were passed
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"], params)
    
    @patch('requests.Session.get')
    def test_get_request_text_response(self, mock_get):
        """Test GET request with text response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Plain text response"
        mock_response.json.side_effect = json.JSONDecodeError("Not JSON", "", 0)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get("https://api.example.com/text")
        
        self.assertEqual(result, "Plain text response")
    
    @patch('requests.Session.get')
    def test_get_request_without_cache(self, mock_get):
        """Test GET request without caching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"nocache": True}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # First call
        result1 = self.client.get("https://api.example.com/nocache", use_cache=False)
        self.assertEqual(result1, {"nocache": True})
        
        # Second call should not use cache
        result2 = self.client.get("https://api.example.com/nocache", use_cache=False)
        self.assertEqual(result2, {"nocache": True})
        
        # Should be called twice
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.Session.get')
    def test_get_request_timeout(self, mock_get):
        """Test GET request timeout handling."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = self.client.get("https://api.example.com/timeout")
        
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    def test_get_request_connection_error(self, mock_get):
        """Test GET request connection error handling."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = self.client.get("https://api.example.com/error")
        
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    def test_get_request_http_error(self, mock_get):
        """Test GET request HTTP error handling."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        result = self.client.get("https://api.example.com/notfound")
        
        self.assertIsNone(result)
    
    @patch('requests.Session.post')
    def test_post_request_json(self, mock_post):
        """Test POST request with JSON data."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        json_data = {"name": "test", "value": 123}
        result = self.client.post("https://api.example.com/create", json_data=json_data)
        
        self.assertEqual(result, {"created": True})
        
        # Verify JSON data was passed
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["json"], json_data)
    
    @patch('requests.Session.post')
    def test_post_request_form_data(self, mock_post):
        """Test POST request with form data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"submitted": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        form_data = {"field1": "value1", "field2": "value2"}
        result = self.client.post("https://api.example.com/submit", data=form_data)
        
        self.assertEqual(result, {"submitted": True})
        
        # Verify form data was passed
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["data"], form_data)
    
    def test_base_url_joining(self):
        """Test URL joining with base URL."""
        client = APIClient(base_url="https://api.example.com/v1")
        
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": True}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Test relative URL
            client.get("/endpoint")
            call_url = mock_get.call_args[0][0]
            self.assertEqual(call_url, "https://api.example.com/v1/endpoint")
            
            # Test absolute URL (should not use base_url)
            client.get("https://other.api.com/data")
            call_url = mock_get.call_args[0][0]
            self.assertEqual(call_url, "https://other.api.com/data")


if __name__ == "__main__":
    unittest.main()