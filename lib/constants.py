#!/usr/bin/env python3
"""
Constants and configuration values for Mood Lifter Hooks.
Centralizes magic numbers and timeout values for easy configuration.
"""

# API Timeout Values (in seconds)
class Timeouts:
    """Timeout constants for various API calls and operations."""
    
    # External API timeouts
    JW_API = 20  # JW.org API needs longer timeout for reliability
    EXTERNAL_APIS = 10  # Jokes, quotes APIs - fast fail preferred
    
    # Ollama model timeouts
    OLLAMA_QUICK = 10  # Quick responses for hook messages
    OLLAMA_NORMAL = 20  # Normal ollama generation
    OLLAMA_DOWNLOAD = 300  # Model download timeout (5 minutes)
    
    # API client defaults
    DEFAULT_API = 10  # Default API client timeout
    
    # Retry settings
    MAX_RETRIES = 1  # Fail fast to avoid blocking hooks
    RETRY_BACKOFF = 0.3  # Backoff factor for retries


# Cache Duration Values (in minutes)
class CacheDuration:
    """Cache duration constants for API responses."""
    
    JW_DAILY_TEXT = 1440  # 24 hours for daily text
    EXTERNAL_CONTENT = 60  # 1 hour for jokes/quotes
    DEFAULT = 30  # Default cache duration
    JW_RATE_LIMIT = 30  # Show JW content at most once per 30 minutes


# Message Length Limits
class MessageLimits:
    """Message length constraints."""
    
    MAX_LENGTH = 120  # Maximum message length (configurable)
    OLLAMA_WORD_LIMIT = 20  # Word limit for ollama prompts
    

# File Paths and Defaults
class Defaults:
    """Default values for configuration."""
    
    CONFIG_FILE = "~/.claude-code/mood-lifter/config.json"
    LAST_SHOWN_FILE = "~/.claude-code/mood-lifter/last_shown.json"
    OLLAMA_MODELS = [
        "llama3.2:latest",
        "mistral:7b-instruct",
        "llama3.2:1b",
        "gemma2:2b",
        "qwen2.5:0.5b"
    ]
    FALLBACK_MODEL = "llama3.2:latest"