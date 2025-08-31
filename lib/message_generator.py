#!/usr/bin/env python3
"""
Message generator module for Mood Lifter Hooks.
Generates encouraging messages using ollama with fallback options.
Now with external API integration and JW daily text support.
"""

import subprocess
import random
import json
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports when run directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API integrations (these will be available once installed)
try:
    from lib.jw_daily_text import generate_jw_message
    from lib.external_apis import generate_external_message, get_fallback_external_message
    from lib.ollama_models import OllamaModelManager, generate_with_model
    from lib.config import get_config
    API_FEATURES_AVAILABLE = True
except ImportError:
    API_FEATURES_AVAILABLE = False
    # Minimal config fallback
    class DummyConfig:
        def is_enabled(self): return True
        def is_ollama_enabled(self): return True
        def use_ollama_variety(self): return False
        def get_preferred_models(self): return ["phi3.5:3.8b"]
        def get_ollama_timeout(self): return 5
        def get_message_source_weights(self): return {"default": 100}
        def is_jw_enabled(self): return False
        def is_external_apis_enabled(self): return False
        def should_show_message(self, event_type): return True
        def get_preferred_sources_for_time(self): return ["default"]
        def get_max_message_length(self): return 120
        def include_emojis(self): return True
        def suppress_errors(self): return True
    
    def get_config():
        return DummyConfig()

# Global model manager instance
_model_manager = None

def get_model_manager():
    """Get or create the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = OllamaModelManager()
    return _model_manager

# Fallback messages for when ollama is unavailable
FALLBACK_MESSAGES = {
    "SessionStart": [
        "🚀 Ready to create something amazing today!",
        "💻 Your code journey begins - let's make it great!",
        "✨ Every expert was once a beginner. Keep coding!",
        "🌟 Time to turn ideas into reality through code!",
        "💪 You've got this! Let's write some awesome code!",
        "🎯 Focus, create, and enjoy the process!",
        "🔥 Another day, another opportunity to level up!",
        "🌈 Your creativity + code = endless possibilities!",
    ],
    "Stop": [
        "🎉 Great work! Your efforts today matter!",
        "✅ Progress made! Every line counts!",
        "🌟 Well done! Rest and come back stronger!",
        "💯 You crushed it! Be proud of what you built!",
        "🚀 Mission accomplished! Your code looks great!",
        "🎯 Target hit! You're getting better every day!",
        "✨ Fantastic session! Your dedication shows!",
        "💪 Strong finish! Your future self will thank you!",
    ],
    "Notification": [
        "💡 Keep going! You're on the right track!",
        "🌟 Your persistence is your superpower!",
        "🚀 Every bug fixed is a lesson learned!",
        "💪 Challenge accepted, solution incoming!",
        "✨ You're doing great! Keep up the momentum!",
        "🎯 Stay focused - breakthrough is near!",
        "🔥 Your code is taking shape beautifully!",
        "🌈 Remember: progress, not perfection!",
    ]
}

# Ollama prompts for different events
OLLAMA_PROMPTS = {
    "SessionStart": {
        "morning": "Generate a brief, encouraging morning message for a developer starting their coding session. Include one emoji. Maximum 15 words. Be positive and energizing.",
        "afternoon": "Generate a brief, encouraging afternoon message for a developer continuing their work. Include one emoji. Maximum 15 words. Be motivating and focused.",
        "evening": "Generate a brief, encouraging evening message for a developer working late. Include one emoji. Maximum 15 words. Be supportive and appreciative.",
    },
    "Stop": {
        "default": "Generate a brief, congratulatory message for a developer finishing their coding work. Include one emoji. Maximum 15 words. Celebrate their effort and progress.",
    },
    "Notification": {
        "default": "Generate a brief, encouraging message for a developer in the middle of coding. Include one emoji. Maximum 15 words. Be supportive and motivating.",
    }
}


def get_time_period() -> str:
    """Determine the current time period for context-aware messages."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    else:
        return "evening"


def generate_with_ollama(event_type: str, model: Optional[str] = None, use_variety: bool = True) -> Optional[str]:
    """
    Generate an encouraging message using ollama.
    
    Args:
        event_type: Type of event (SessionStart, Stop, Notification)
        model: Specific ollama model to use (None for auto-selection)
        use_variety: Whether to use model rotation for variety
        
    Returns:
        Generated message or None if failed
    """
    try:
        # Get appropriate prompt based on event type and time
        prompts = OLLAMA_PROMPTS.get(event_type, {})
        
        if event_type == "SessionStart":
            time_period = get_time_period()
            prompt = prompts.get(time_period, prompts.get("default", ""))
        else:
            prompt = prompts.get("default", "")
        
        if not prompt:
            return None
        
        # Use model manager for selection if API features available
        if API_FEATURES_AVAILABLE and use_variety and model is None:
            manager = get_model_manager()
            selected_model = manager.select_model()
        else:
            selected_model = model or "phi3.5:3.8b"
        
        # Call ollama with timeout
        result = subprocess.run(
            ["ollama", "run", selected_model, "--verbose=false"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=5  # 5 second timeout
        )
        
        if result.returncode == 0 and result.stdout:
            # Clean up the output - take first line, trim whitespace
            message = result.stdout.strip().split('\n')[0].strip()
            # Ensure it's not too long
            if len(message) > 100:
                message = message[:97] + "..."
            return message
            
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Ollama not available or failed
        pass
    
    return None


def get_fallback_message(event_type: str) -> str:
    """Get a random fallback message for the given event type."""
    messages = FALLBACK_MESSAGES.get(event_type, FALLBACK_MESSAGES["Notification"])
    return random.choice(messages)


def generate_message(
    event_type: str, 
    use_ollama: Optional[bool] = None, 
    model: Optional[str] = None,
    message_source: Optional[str] = None,
    use_variety: Optional[bool] = None,
    use_config: bool = True
) -> str:
    """
    Generate an encouraging message for the given event type.
    
    Args:
        event_type: Type of event (SessionStart, Stop, Notification)
        use_ollama: Whether to try using ollama first (None to use config)
        model: Specific ollama model to use (None for auto-selection)
        message_source: Optional source preference ('default', 'jw', 'joke', 'quote', None for random)
        use_variety: Whether to use model rotation for variety (None to use config)
        use_config: Whether to use configuration settings
        
    Returns:
        An encouraging message
    """
    # Load configuration if enabled
    config = get_config() if use_config else None
    
    # Check if we should show a message based on probability
    if config and not config.should_show_message(event_type):
        return ""  # Return empty string if message should be skipped
    
    # Apply configuration defaults if not specified
    if use_ollama is None:
        use_ollama = config.is_ollama_enabled() if config else True
    if use_variety is None:
        use_variety = config.use_ollama_variety() if config else True
    
    # If API features are available and source is specified or randomly selected
    if API_FEATURES_AVAILABLE:
        # Determine message source
        if message_source is None and config:
            # Use configuration-based weighted selection
            weights = config.get_message_source_weights()
            sources = []
            for source, weight in weights.items():
                sources.extend([source] * weight)
            
            # Apply time preferences if configured
            if event_type == "SessionStart":
                preferred = config.get_preferred_sources_for_time()
                # Boost preferred sources
                for source in preferred:
                    if source in weights:
                        sources.extend([source] * 10)
            
            message_source = random.choice(sources) if sources else 'default'
        elif message_source is None:
            # Fallback to default weighted selection
            sources = ['default'] * 4  # 40% chance
            if API_FEATURES_AVAILABLE:
                sources.extend(['jw'] * 2)  # 20% chance
                sources.extend(['joke'] * 2)  # 20% chance
                sources.extend(['quote'] * 2)  # 20% chance
            message_source = random.choice(sources)
        
        # Try to generate from selected source
        if message_source == 'jw' and (not config or config.is_jw_enabled()):
            message = generate_jw_message(event_type, use_ollama=use_ollama)
            if message:
                return _apply_config_formatting(message, config)
        elif message_source == 'joke' and (not config or config.is_external_apis_enabled()):
            message = generate_external_message(event_type, content_type='joke', use_ollama=use_ollama)
            if message:
                return _apply_config_formatting(message, config)
        elif message_source == 'quote' and (not config or config.is_external_apis_enabled()):
            message = generate_external_message(event_type, content_type='quote', use_ollama=use_ollama)
            if message:
                return _apply_config_formatting(message, config)
        # If source is 'default' or previous attempts failed, continue to default behavior
    
    # Default behavior: use ollama or fallback messages
    if use_ollama:
        message = generate_with_ollama(event_type, model, use_variety)
        if message:
            return _apply_config_formatting(message, config)
    
    # Fall back to pre-written messages or external fallbacks
    if API_FEATURES_AVAILABLE and message_source in ['joke', 'quote']:
        message = get_fallback_external_message(message_source)
    else:
        message = get_fallback_message(event_type)
    
    return _apply_config_formatting(message, config)


def _apply_config_formatting(message: str, config: Optional[Any]) -> str:
    """
    Apply configuration-based formatting to a message.
    
    Args:
        message: The message to format
        config: Configuration object
        
    Returns:
        Formatted message
    """
    if not config:
        return message
    
    # Apply max length
    max_length = config.get_max_message_length()
    if len(message) > max_length:
        message = message[:max_length-3] + "..."
    
    # Remove emojis if configured
    if not config.include_emojis():
        # Simple emoji removal (keeps text)
        import re
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        message = emoji_pattern.sub('', message).strip()
    
    return message


def format_hook_output(message: str, event_type: str) -> Dict:
    """
    Format the message for proper hook output based on event type.
    
    Args:
        message: The encouragement message
        event_type: Type of event
        
    Returns:
        Dictionary for JSON output (SessionStart) or None for stdout
    """
    if event_type == "SessionStart":
        # For SessionStart, return JSON with suppressOutput
        return {
            "suppressOutput": True,
            "systemMessage": message
        }
    else:
        # For Stop and Notification, just return the message for stdout
        return None


if __name__ == "__main__":
    # Test the message generator
    print("Testing Enhanced Message Generator")
    print("=" * 50)
    
    # Test basic functionality
    for event in ["SessionStart", "Stop", "Notification"]:
        print(f"\n{event}:")
        print(f"  Default (with ollama): {generate_message(event, use_ollama=True)}")
        print(f"  Default (fallback): {generate_message(event, use_ollama=False)}")
    
    # Test new API features if available
    if API_FEATURES_AVAILABLE:
        print("\n\nTesting API Integrations:")
        print("-" * 30)
        
        # Test JW daily text
        print("\nJW Daily Text:")
        msg = generate_message("SessionStart", message_source="jw", use_ollama=False)
        print(f"  Without ollama: {msg}")
        msg = generate_message("SessionStart", message_source="jw", use_ollama=True)
        print(f"  With ollama: {msg}")
        
        # Test jokes
        print("\nJokes:")
        msg = generate_message("SessionStart", message_source="joke", use_ollama=False)
        print(f"  Without ollama: {msg}")
        msg = generate_message("SessionStart", message_source="joke", use_ollama=True)
        print(f"  With ollama: {msg}")
        
        # Test quotes
        print("\nQuotes:")
        msg = generate_message("SessionStart", message_source="quote", use_ollama=False)
        print(f"  Without ollama: {msg}")
        msg = generate_message("SessionStart", message_source="quote", use_ollama=True)
        print(f"  With ollama: {msg}")
        
        # Test random selection
        print("\n\nRandom source selection (5 samples):")
        for i in range(5):
            msg = generate_message("SessionStart")
            print(f"  {i+1}. {msg}")
    else:
        print("\n\nAPI features not available (dependencies may not be installed)")