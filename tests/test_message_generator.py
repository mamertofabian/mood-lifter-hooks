#!/usr/bin/env python3
"""
Tests for the message generator module.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.message_generator import (
    get_time_period,
    get_fallback_message,
    generate_message,
    format_hook_output,
    _apply_config_formatting
)


class TestMessageGenerator(unittest.TestCase):
    """Test cases for message generator functions."""
    
    def test_get_time_period(self):
        """Test time period detection."""
        with patch('lib.message_generator.datetime') as mock_datetime:
            # Test morning
            mock_datetime.now.return_value.hour = 8
            self.assertEqual(get_time_period(), "morning")
            
            # Test afternoon
            mock_datetime.now.return_value.hour = 14
            self.assertEqual(get_time_period(), "afternoon")
            
            # Test evening
            mock_datetime.now.return_value.hour = 20
            self.assertEqual(get_time_period(), "evening")
    
    def test_get_fallback_message(self):
        """Test fallback message retrieval."""
        # Test SessionStart
        message = get_fallback_message("SessionStart")
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        
        # Test Stop
        message = get_fallback_message("Stop")
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        
        # Test Notification
        message = get_fallback_message("Notification")
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        
        # Test unknown event type (should fallback to Notification)
        message = get_fallback_message("UnknownEvent")
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
    
    def test_generate_message_without_ollama(self):
        """Test message generation without ollama."""
        # Generate message without ollama
        message = generate_message("SessionStart", use_ollama=False)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
    
    @patch('subprocess.run')
    def test_generate_message_with_ollama(self, mock_run):
        """Test message generation with ollama (mocked)."""
        # Mock successful ollama response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Keep coding, you're doing great! 🚀"
        mock_run.return_value = mock_result
        
        message = generate_message("SessionStart", use_ollama=True)
        self.assertIsInstance(message, str)
        self.assertIn("Keep coding", message)
    
    def test_format_hook_output(self):
        """Test hook output formatting."""
        # Test SessionStart (should return JSON with suppressOutput)
        result = format_hook_output("Test message", "SessionStart")
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("suppressOutput"))
        self.assertEqual(result.get("systemMessage"), "Test message")
        
        # Test Stop (should return None for stdout)
        result = format_hook_output("Test message", "Stop")
        self.assertIsNone(result)
        
        # Test Notification (should return None for stdout)
        result = format_hook_output("Test message", "Notification")
        self.assertIsNone(result)
    
    def test_apply_config_formatting(self):
        """Test configuration-based formatting."""
        # Test without config
        message = _apply_config_formatting("Test message 🚀", None)
        self.assertEqual(message, "Test message 🚀")
        
        # Test with emoji removal
        mock_config = MagicMock()
        mock_config.get_max_message_length.return_value = 10
        mock_config.include_emojis.return_value = False
        
        message = _apply_config_formatting("Test message 🚀 with emoji 😊", mock_config)
        self.assertNotIn("🚀", message)
        self.assertNotIn("😊", message)
        self.assertIn("Test message", message)
        
        # Test with emojis enabled
        mock_config.include_emojis.return_value = True
        message = _apply_config_formatting("Test message 🚀 with emoji 😊", mock_config)
        self.assertIn("🚀", message)
        self.assertIn("😊", message)
    
    @patch('lib.message_generator.get_config')
    def test_message_probability(self, mock_get_config):
        """Test message probability based on config."""
        mock_config = MagicMock()
        mock_config.should_show_message.return_value = False
        mock_get_config.return_value = mock_config
        
        # Should return empty string when probability check fails
        message = generate_message("Notification", use_config=True)
        self.assertEqual(message, "")
        
        # Should return message when probability check passes
        mock_config.should_show_message.return_value = True
        mock_config.is_ollama_enabled.return_value = False
        mock_config.use_ollama_variety.return_value = False
        mock_config.get_message_source_weights.return_value = {"default": 100}
        mock_config.get_preferred_sources_for_time.return_value = ["default"]
        mock_config.get_max_message_length.return_value = 120
        mock_config.include_emojis.return_value = True
        
        message = generate_message("SessionStart", use_config=True)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)


class TestMessageSources(unittest.TestCase):
    """Test cases for different message sources."""
    
    @patch('lib.message_generator.API_FEATURES_AVAILABLE', True)
    @patch('lib.message_generator.generate_jw_message')
    def test_jw_message_source(self, mock_jw):
        """Test JW daily text message source."""
        mock_jw.return_value = "Daily wisdom for developers"
        
        message = generate_message("SessionStart", message_source="jw", use_ollama=False)
        self.assertEqual(message, "Daily wisdom for developers")
        mock_jw.assert_called_once()
    
    @patch('lib.message_generator.API_FEATURES_AVAILABLE', True)
    @patch('lib.message_generator.generate_external_message')
    def test_joke_message_source(self, mock_external):
        """Test joke message source."""
        mock_external.return_value = "Why do programmers prefer dark mode? Light attracts bugs!"
        
        message = generate_message("SessionStart", message_source="joke", use_ollama=False)
        self.assertIn("bugs", message)
        mock_external.assert_called_once_with("SessionStart", content_type="joke", use_ollama=False)
    
    @patch('lib.message_generator.API_FEATURES_AVAILABLE', True)
    @patch('lib.message_generator.generate_external_message')
    def test_quote_message_source(self, mock_external):
        """Test quote message source."""
        mock_external.return_value = '"Code is poetry" - Someone'
        
        message = generate_message("SessionStart", message_source="quote", use_ollama=False)
        self.assertIn("poetry", message)
        mock_external.assert_called_once_with("SessionStart", content_type="quote", use_ollama=False)
    
    @patch('lib.message_generator.API_FEATURES_AVAILABLE', True)
    @patch('lib.message_generator.generate_stoic_message')
    def test_stoic_message_source(self, mock_stoic):
        """Test stoic quotes message source."""
        mock_stoic.return_value = "🧘 Control what you can: your code, your response, your calm."
        
        message = generate_message("SessionStart", message_source="stoic", use_ollama=False)
        self.assertIn("🧘", message)
        self.assertIn("calm", message)
        mock_stoic.assert_called_once_with("SessionStart", use_ollama=False)


if __name__ == "__main__":
    unittest.main()