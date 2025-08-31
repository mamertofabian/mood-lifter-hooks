#!/usr/bin/env python3
"""
Tests for the configuration system.
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import Config, get_config, reload_config


class TestConfig(unittest.TestCase):
    """Test cases for configuration system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config_path = Path(self.temp_dir) / "test_config.json"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_defaults(self):
        """Test loading default configuration."""
        config = Config()
        
        # Check basic settings exist
        self.assertTrue(config.is_enabled())
        self.assertTrue(config.is_ollama_enabled())
        self.assertIsInstance(config.get_preferred_models(), list)
        self.assertGreater(len(config.get_preferred_models()), 0)
    
    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        config = Config()
        
        # Test valid paths
        self.assertIsNotNone(config.get("ollama.enabled"))
        self.assertIsNotNone(config.get("message_sources.weights"))
        
        # Test invalid path with default
        self.assertEqual(config.get("non.existent.path", "default"), "default")
    
    def test_user_config_override(self):
        """Test user configuration overriding defaults."""
        # Create user config
        user_config = {
            "mood_lifter_hooks": {
                "ollama": {
                    "enabled": False,
                    "use_variety": False
                },
                "message_sources": {
                    "weights": {
                        "default": 80,
                        "jw": 20
                    }
                }
            }
        }
        
        with open(self.temp_config_path, 'w') as f:
            json.dump(user_config, f)
        
        # Load config with user override
        config = Config(self.temp_config_path)
        
        # Check overrides
        self.assertFalse(config.is_ollama_enabled())
        self.assertFalse(config.use_ollama_variety())
        
        weights = config.get_message_source_weights()
        self.assertEqual(weights["default"], 80)
        self.assertEqual(weights["jw"], 20)
    
    def test_merge_configs(self):
        """Test configuration merging."""
        config = Config()
        
        base = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            },
            "e": [1, 2, 3]
        }
        
        override = {
            "a": 10,
            "b": {
                "c": 20
            },
            "f": 4
        }
        
        result = config._merge_configs(base, override)
        
        self.assertEqual(result["a"], 10)  # Overridden
        self.assertEqual(result["b"]["c"], 20)  # Nested override
        self.assertEqual(result["b"]["d"], 3)  # Preserved from base
        self.assertEqual(result["e"], [1, 2, 3])  # Preserved from base
        self.assertEqual(result["f"], 4)  # New from override
    
    def test_event_configuration(self):
        """Test event-specific configuration."""
        config = Config()
        
        # Test getting event config
        session_config = config.get_event_config("SessionStart")
        self.assertIsInstance(session_config, dict)
        self.assertTrue(session_config.get("enabled", False))
        
        stop_config = config.get_event_config("Stop")
        self.assertIsInstance(stop_config, dict)
    
    def test_should_show_message(self):
        """Test message probability logic."""
        config = Config()
        
        # Test with probability 1.0 (should always show)
        with patch('random.random', return_value=0.5):
            # SessionStart has probability 1.0 by default
            self.assertTrue(config.should_show_message("SessionStart"))
        
        # Test with lower probability
        with patch('random.random', return_value=0.9):
            # Notification has probability 0.5 by default
            self.assertFalse(config.should_show_message("Notification"))
        
        with patch('random.random', return_value=0.3):
            self.assertTrue(config.should_show_message("Notification"))
    
    def test_time_preferences(self):
        """Test time-based preferences."""
        config = Config()
        
        from datetime import datetime
        with patch('datetime.datetime') as mock_datetime:
            # Test morning
            mock_now = MagicMock()
            mock_now.hour = 8
            mock_datetime.now.return_value = mock_now
            period = config.get_current_time_period()
            self.assertEqual(period, "morning")
            
            sources = config.get_preferred_sources_for_time()
            self.assertIsInstance(sources, list)
            self.assertIn("default", sources)
            
            # Test afternoon
            mock_now.hour = 14
            period = config.get_current_time_period()
            self.assertEqual(period, "afternoon")
            
            # Test evening
            mock_now.hour = 20
            period = config.get_current_time_period()
            self.assertEqual(period, "evening")
    
    def test_display_settings(self):
        """Test display configuration settings."""
        config = Config()
        
        # Test default display settings
        self.assertIsInstance(config.get_max_message_length(), int)
        self.assertGreater(config.get_max_message_length(), 0)
        self.assertIsInstance(config.include_emojis(), bool)
        self.assertIsInstance(config.suppress_errors(), bool)
    
    def test_api_feature_settings(self):
        """Test API feature configuration."""
        config = Config()
        
        # Test API feature flags
        self.assertIsInstance(config.is_jw_enabled(), bool)
        self.assertIsInstance(config.is_external_apis_enabled(), bool)
    
    def test_save_user_config(self):
        """Test saving user configuration."""
        config = Config()
        
        # Create sample config
        sample_config = {
            "mood_lifter_hooks": {
                "enabled": True,
                "test_value": 123
            }
        }
        
        # Save config
        save_path = Path(self.temp_dir) / "saved_config.json"
        config.save_user_config(sample_config, save_path)
        
        # Verify file exists and contents
        self.assertTrue(save_path.exists())
        
        with open(save_path, 'r') as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded["mood_lifter_hooks"]["test_value"], 123)
    
    def test_fallback_config(self):
        """Test fallback configuration when defaults missing."""
        with patch.object(Path, 'exists', return_value=False):
            config = Config()
            
            # Should still have basic functionality with fallback
            self.assertTrue(config.is_enabled())
            self.assertIsInstance(config.get_preferred_models(), list)
            self.assertGreater(len(config.get_preferred_models()), 0)


class TestGlobalConfig(unittest.TestCase):
    """Test global configuration instance management."""
    
    def test_get_config_singleton(self):
        """Test that get_config returns singleton."""
        config1 = get_config()
        config2 = get_config()
        
        # Should be the same instance
        self.assertIs(config1, config2)
    
    def test_reload_config(self):
        """Test configuration reload."""
        config1 = get_config()
        config2 = reload_config()
        
        # Should be different instances
        self.assertIsNot(config1, config2)
        
        # New get_config should return reloaded instance
        config3 = get_config()
        self.assertIs(config2, config3)


if __name__ == "__main__":
    unittest.main()