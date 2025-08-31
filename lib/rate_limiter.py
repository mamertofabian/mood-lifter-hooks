#!/usr/bin/env python3
"""
Rate limiting for content display in Mood Lifter Hooks.
Tracks when specific content types were last shown to avoid repetition.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# Add parent directory to path for imports when run directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.constants import CacheDuration, Defaults


class RateLimiter:
    """Manages rate limiting for different content types."""
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize the rate limiter.
        
        Args:
            state_file: Path to file storing last shown timestamps
        """
        if state_file is None:
            # Use default location in user's home directory
            state_file = os.path.expanduser(Defaults.LAST_SHOWN_FILE)
        
        self.state_file = state_file
        self._ensure_directory()
        self._state = self._load_state()
    
    def _ensure_directory(self):
        """Ensure the directory for the state file exists."""
        state_path = Path(self.state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict[str, Any]:
        """Load the state from file or return empty state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime objects
                    for key in data:
                        if isinstance(data[key], str):
                            try:
                                data[key] = datetime.fromisoformat(data[key])
                            except (ValueError, TypeError):
                                pass
                    return data
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_state(self):
        """Save the current state to file."""
        try:
            # Convert datetime objects to ISO format strings for JSON
            save_data = {}
            for key, value in self._state.items():
                if isinstance(value, datetime):
                    save_data[key] = value.isoformat()
                else:
                    save_data[key] = value
            
            with open(self.state_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except IOError:
            # Fail silently - rate limiting is not critical
            pass
    
    def should_show(self, content_type: str, cooldown_minutes: int = 30) -> bool:
        """
        Check if content of given type should be shown.
        
        Args:
            content_type: Type of content (e.g., 'jw_daily_text')
            cooldown_minutes: Minimum minutes between showing this content
            
        Returns:
            True if content should be shown, False if still in cooldown
        """
        last_shown_key = f"last_shown_{content_type}"
        
        if last_shown_key not in self._state:
            # Never shown before
            return True
        
        last_shown = self._state[last_shown_key]
        if not isinstance(last_shown, datetime):
            # Invalid timestamp, allow showing
            return True
        
        # Check if enough time has passed
        cooldown_delta = timedelta(minutes=cooldown_minutes)
        if datetime.now() - last_shown >= cooldown_delta:
            return True
        
        return False
    
    def mark_shown(self, content_type: str):
        """
        Mark content as shown now.
        
        Args:
            content_type: Type of content that was shown
        """
        last_shown_key = f"last_shown_{content_type}"
        self._state[last_shown_key] = datetime.now()
        self._save_state()
    
    def get_time_until_available(self, content_type: str, cooldown_minutes: int = 30) -> Optional[int]:
        """
        Get minutes until content can be shown again.
        
        Args:
            content_type: Type of content
            cooldown_minutes: Cooldown period in minutes
            
        Returns:
            Minutes until available, or None if available now
        """
        last_shown_key = f"last_shown_{content_type}"
        
        if last_shown_key not in self._state:
            return None
        
        last_shown = self._state[last_shown_key]
        if not isinstance(last_shown, datetime):
            return None
        
        elapsed = datetime.now() - last_shown
        cooldown_delta = timedelta(minutes=cooldown_minutes)
        
        if elapsed >= cooldown_delta:
            return None
        
        remaining = cooldown_delta - elapsed
        return int(remaining.total_seconds() / 60)
    
    def reset(self, content_type: Optional[str] = None):
        """
        Reset rate limiting for specific content or all content.
        
        Args:
            content_type: Specific content type to reset, or None for all
        """
        if content_type:
            last_shown_key = f"last_shown_{content_type}"
            if last_shown_key in self._state:
                del self._state[last_shown_key]
        else:
            # Reset all
            self._state = {}
        
        self._save_state()


# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def should_show_jw_content(cooldown_minutes: Optional[int] = None) -> bool:
    """
    Check if JW daily text content should be shown.
    
    Args:
        cooldown_minutes: Override cooldown period (default from config or constants)
        
    Returns:
        True if JW content should be shown
    """
    if cooldown_minutes is None:
        # Try to get from config first
        try:
            from lib.config import get_config
            config = get_config()
            cooldown_minutes = config.get_jw_rate_limit_minutes()
        except ImportError:
            # Fallback to constant if config not available
            cooldown_minutes = CacheDuration.JW_RATE_LIMIT
    
    limiter = get_rate_limiter()
    return limiter.should_show("jw_daily_text", cooldown_minutes)


def mark_jw_content_shown():
    """Mark that JW content was just shown."""
    limiter = get_rate_limiter()
    limiter.mark_shown("jw_daily_text")


if __name__ == "__main__":
    # Test the rate limiter
    print("Testing Rate Limiter")
    print("=" * 50)
    
    limiter = RateLimiter("/tmp/test_rate_limiter.json")
    
    # Test showing content
    content_type = "test_content"
    cooldown = 1  # 1 minute for testing
    
    print(f"\nShould show '{content_type}'? {limiter.should_show(content_type, cooldown)}")
    
    if limiter.should_show(content_type, cooldown):
        print(f"Marking '{content_type}' as shown...")
        limiter.mark_shown(content_type)
    
    print(f"Should show '{content_type}' again? {limiter.should_show(content_type, cooldown)}")
    
    remaining = limiter.get_time_until_available(content_type, cooldown)
    if remaining:
        print(f"Time until available: {remaining} minutes")
    
    # Test JW content functions
    print("\n\nTesting JW content rate limiting:")
    print(f"Should show JW content? {should_show_jw_content()}")
    
    if should_show_jw_content():
        print("Marking JW content as shown...")
        mark_jw_content_shown()
        print(f"Should show JW content again? {should_show_jw_content()}")
    
    # Clean up test file
    os.remove("/tmp/test_rate_limiter.json")