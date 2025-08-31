#!/usr/bin/env python3
"""
Configuration management for Mood Lifter Hooks.
Loads configuration from defaults and user overrides.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


class Config:
    """Configuration manager for Mood Lifter Hooks."""
    
    # Default paths
    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "defaults.json"
    USER_CONFIG_DIR = Path.home() / ".mood-lifter-hooks"
    USER_CONFIG_PATHS = [
        USER_CONFIG_DIR / "config.json",
        USER_CONFIG_DIR / "config.yaml",
        USER_CONFIG_DIR / "config.yml",
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to user configuration file
        """
        self.config: Dict[str, Any] = {}
        self._load_defaults()
        
        if config_path:
            self._load_user_config(config_path)
        else:
            self._load_user_config_auto()
    
    def _load_defaults(self):
        """Load default configuration."""
        if self.DEFAULT_CONFIG_PATH.exists():
            try:
                with open(self.DEFAULT_CONFIG_PATH, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load default config: {e}")
                self.config = self._get_fallback_config()
        else:
            self.config = self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get minimal fallback configuration."""
        return {
            "mood_lifter_hooks": {
                "enabled": True,
                "ollama": {
                    "enabled": True,
                    "use_variety": False,
                    "preferred_models": ["phi3.5:3.8b"],
                    "timeout": 5
                },
                "message_sources": {
                    "weights": {
                        "default": 100
                    }
                },
                "events": {
                    "SessionStart": {"enabled": True, "probability": 1.0},
                    "Stop": {"enabled": True, "probability": 1.0},
                    "Notification": {"enabled": True, "probability": 1.0}
                },
                "display": {
                    "max_length": 120,
                    "include_emojis": True,
                    "suppress_errors": True
                }
            }
        }
    
    def _load_user_config_auto(self):
        """Automatically find and load user configuration."""
        for path in self.USER_CONFIG_PATHS:
            if path.exists():
                self._load_user_config(path)
                break
    
    def _load_user_config(self, path: Path):
        """
        Load user configuration and merge with defaults.
        
        Args:
            path: Path to user configuration file
        """
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)
            
            # Merge user config with defaults
            self.config = self._merge_configs(self.config, user_config)
            
        except Exception as e:
            print(f"Warning: Failed to load user config from {path}: {e}")
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Recursively merge configuration dictionaries.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated configuration key (e.g., "ollama.enabled")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config.get("mood_lifter_hooks", {})
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def is_enabled(self) -> bool:
        """Check if mood lifter hooks are enabled."""
        return self.get("enabled", True)
    
    def is_ollama_enabled(self) -> bool:
        """Check if ollama is enabled."""
        return self.get("ollama.enabled", True)
    
    def use_ollama_variety(self) -> bool:
        """Check if ollama model variety is enabled."""
        return self.get("ollama.use_variety", True)
    
    def get_preferred_models(self) -> List[str]:
        """Get list of preferred ollama models."""
        return self.get("ollama.preferred_models", ["phi3.5:3.8b"])
    
    def get_ollama_timeout(self) -> int:
        """Get ollama timeout in seconds."""
        return self.get("ollama.timeout", 5)
    
    def get_message_source_weights(self) -> Dict[str, int]:
        """Get message source weights for random selection."""
        return self.get("message_sources.weights", {"default": 100})
    
    def is_jw_enabled(self) -> bool:
        """Check if JW daily text is enabled."""
        return self.get("message_sources.jw.enabled", True)
    
    def get_jw_rate_limit_minutes(self) -> int:
        """Get JW content rate limit cooldown in minutes."""
        return self.get("message_sources.jw.rate_limit_minutes", 30)
    
    def is_external_apis_enabled(self) -> bool:
        """Check if external APIs are enabled."""
        return self.get("message_sources.external_apis.enabled", True)
    
    def get_event_config(self, event_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific event type.
        
        Args:
            event_type: Event type (SessionStart, Stop, Notification)
            
        Returns:
            Event configuration dictionary
        """
        return self.get(f"events.{event_type}", {})
    
    def should_show_message(self, event_type: str) -> bool:
        """
        Check if a message should be shown for an event based on probability.
        
        Args:
            event_type: Event type
            
        Returns:
            True if message should be shown
        """
        import random
        event_config = self.get_event_config(event_type)
        
        if not event_config.get("enabled", True):
            return False
        
        probability = event_config.get("probability", 1.0)
        return random.random() < probability
    
    def get_time_preferences(self) -> Dict[str, Any]:
        """Get time-based preferences."""
        return self.get("time_preferences", {})
    
    def get_current_time_period(self) -> str:
        """Get current time period based on configuration."""
        from datetime import datetime
        hour = datetime.now().hour
        
        time_prefs = self.get_time_preferences()
        
        for period, config in time_prefs.items():
            hours = config.get("hours", [])
            if len(hours) >= 2:
                start, end = hours[0], hours[1]
                if start <= hour < end:
                    return period
        
        # Default fallback
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    def get_preferred_sources_for_time(self) -> List[str]:
        """Get preferred message sources for current time."""
        period = self.get_current_time_period()
        time_prefs = self.get_time_preferences()
        
        if period in time_prefs:
            return time_prefs[period].get("prefer_sources", ["default"])
        
        return ["default"]
    
    def get_max_message_length(self) -> int:
        """Get maximum message length."""
        return self.get("display.max_length", 120)
    
    def include_emojis(self) -> bool:
        """Check if emojis should be included."""
        return self.get("display.include_emojis", True)
    
    def suppress_errors(self) -> bool:
        """Check if errors should be suppressed."""
        return self.get("display.suppress_errors", True)
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("debug.enabled", False)
    
    def save_user_config(self, config_dict: Dict[str, Any], path: Optional[Path] = None):
        """
        Save user configuration.
        
        Args:
            config_dict: Configuration dictionary to save
            path: Optional path to save to (defaults to first user config path)
        """
        if path is None:
            path = self.USER_CONFIG_PATHS[0]
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, 'w') as f:
                if path.suffix in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            print(f"Configuration saved to {path}")
            
        except Exception as e:
            print(f"Error saving configuration: {e}")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config(config_path: Optional[Path] = None):
    """
    Reload configuration from files.
    
    Args:
        config_path: Optional path to user configuration
    """
    global _config
    _config = Config(config_path)
    return _config


def test_config():
    """Test the configuration system."""
    print("Testing Configuration System")
    print("=" * 50)
    
    config = get_config()
    
    print("\n1. Basic Settings:")
    print(f"   Enabled: {config.is_enabled()}")
    print(f"   Ollama enabled: {config.is_ollama_enabled()}")
    print(f"   Use variety: {config.use_ollama_variety()}")
    
    print("\n2. Preferred Models:")
    for model in config.get_preferred_models():
        print(f"   • {model}")
    
    print("\n3. Message Source Weights:")
    weights = config.get_message_source_weights()
    for source, weight in weights.items():
        print(f"   • {source}: {weight}%")
    
    print("\n4. Event Configuration:")
    for event in ["SessionStart", "Stop", "Notification"]:
        event_config = config.get_event_config(event)
        print(f"   {event}:")
        print(f"     Enabled: {event_config.get('enabled', True)}")
        print(f"     Probability: {event_config.get('probability', 1.0)}")
    
    print("\n5. Time Preferences:")
    print(f"   Current period: {config.get_current_time_period()}")
    print(f"   Preferred sources: {config.get_preferred_sources_for_time()}")
    
    print("\n6. Display Settings:")
    print(f"   Max length: {config.get_max_message_length()}")
    print(f"   Include emojis: {config.include_emojis()}")
    print(f"   Suppress errors: {config.suppress_errors()}")
    
    # Test user config creation
    print("\n7. Creating Sample User Config:")
    sample_config = {
        "mood_lifter_hooks": {
            "ollama": {
                "use_variety": False,
                "preferred_models": ["phi3.5:3.8b"]
            },
            "message_sources": {
                "weights": {
                    "default": 60,
                    "jw": 40
                }
            }
        }
    }
    
    user_config_path = Config.USER_CONFIG_DIR / "config.json.example"
    config.save_user_config(sample_config, user_config_path)
    print(f"   Sample saved to: {user_config_path}")


if __name__ == "__main__":
    test_config()