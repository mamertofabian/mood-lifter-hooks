#!/usr/bin/env python3
"""
JW Daily Text integration for Mood Lifter Hooks.
Fetches daily text from JW.org and creates developer-focused encouragement.
"""

import random
import subprocess
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.api_integrations import APIClient


class JWDailyTextClient:
    """Client for fetching and processing JW daily texts."""
    
    BASE_URL = "https://wol.jw.org/wol/dt/r1/lp-e"
    
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize JW Daily Text client.
        
        Args:
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.api_client = APIClient(
            base_url=None,
            cache_ttl_minutes=cache_ttl_hours * 60
        )
    
    def _build_url(self, date: Optional[datetime] = None) -> str:
        """
        Build the URL for a specific date.
        
        Args:
            date: Date to fetch (defaults to today)
            
        Returns:
            Full URL for the daily text endpoint
        """
        if date is None:
            date = datetime.now()
        
        year = date.year
        month = date.month
        day = date.day
        
        return f"{self.BASE_URL}/{year}/{month}/{day}"
    
    def fetch_daily_text(self, date: Optional[datetime] = None) -> Optional[Dict]:
        """
        Fetch the daily text for a specific date.
        
        Args:
            date: Date to fetch (defaults to today)
            
        Returns:
            Parsed daily text data or None on error
        """
        url = self._build_url(date)
        
        # Fetch the JSON data
        data = self.api_client.get(url)
        
        if not data or not isinstance(data, dict):
            return None
        
        # Extract the relevant daily text entry
        items = data.get("items", [])
        
        # Look for the specific publication based on user's criteria
        for item in items:
            # Check for "Examining the Scriptures Daily" publication
            if (item.get("englishSymbol", "").startswith("es") and 
                "Examining the Scriptures Daily" in item.get("publicationTitle", "")):
                
                # Extract the daily text content
                content = item.get("content", "")
                title = item.get("title", "")
                reference = item.get("reference", "")
                
                # Parse the content to extract scripture and commentary
                scripture_text = ""
                commentary = ""
                
                # The content typically contains scripture reference and commentary
                if content:
                    # Try to extract scripture and commentary
                    # This is a simplified extraction - actual format may vary
                    lines = content.strip().split('\n')
                    if lines:
                        scripture_text = lines[0] if lines else ""
                        commentary = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                
                return {
                    "date": date if date else datetime.now(),
                    "title": title,
                    "reference": reference,
                    "scripture": scripture_text,
                    "commentary": commentary,
                    "full_content": content,
                    "publication": item.get("publicationTitle", "")
                }
        
        # If no matching entry found, try to use the first item as fallback
        if items:
            item = items[0]
            return {
                "date": date if date else datetime.now(),
                "title": item.get("title", ""),
                "reference": item.get("reference", ""),
                "scripture": "",
                "commentary": item.get("content", ""),
                "full_content": item.get("content", ""),
                "publication": item.get("publicationTitle", "")
            }
        
        return None
    
    def get_random_past_date(self, days_back: int = 30) -> datetime:
        """
        Get a random date from the past N days.
        
        Args:
            days_back: Maximum number of days to go back
            
        Returns:
            Random past date
        """
        days = random.randint(1, days_back)
        return datetime.now() - timedelta(days=days)
    
    def fetch_for_time_period(self, time_period: str = "morning") -> Optional[Dict]:
        """
        Fetch daily text based on time period.
        
        Args:
            time_period: "morning", "afternoon", or "evening"
            
        Returns:
            Daily text data
        """
        if time_period == "morning":
            # Always use today's text for morning
            return self.fetch_daily_text()
        elif time_period in ["afternoon", "evening"]:
            # Sometimes use a random past date for variety
            if random.random() < 0.3:  # 30% chance to use past date
                past_date = self.get_random_past_date(days_back=14)
                return self.fetch_daily_text(past_date)
            else:
                return self.fetch_daily_text()
        else:
            return self.fetch_daily_text()


def create_developer_encouragement(
    daily_text: Dict, 
    use_ollama: bool = True,
    model: str = "phi3.5:3.8b"
) -> str:
    """
    Create developer-focused encouragement from daily text.
    
    Args:
        daily_text: Daily text data
        use_ollama: Whether to use ollama for enhancement
        model: Ollama model to use
        
    Returns:
        Encouraging message for developers
    """
    if not daily_text:
        return "💫 Keep coding with purpose and dedication!"
    
    scripture = daily_text.get("scripture", "").strip()
    commentary = daily_text.get("commentary", "").strip()
    title = daily_text.get("title", "").strip()
    
    if use_ollama:
        # Create a prompt for ollama
        prompt = f"""Based on this daily text: "{scripture if scripture else title}"
        
Commentary: {commentary[:200] if commentary else 'N/A'}

Create a brief, encouraging message for a software developer that relates this wisdom to their coding journey. 
Maximum 20 words. Include one appropriate emoji. Focus on practical encouragement."""
        
        try:
            result = subprocess.run(
                ["ollama", "run", model, "--verbose=false"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=8  # Slightly longer timeout for more complex generation
            )
            
            if result.returncode == 0 and result.stdout:
                message = result.stdout.strip().split('\n')[0].strip()
                if len(message) > 120:
                    message = message[:117] + "..."
                return message
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Fallback messages inspired by daily text themes
    fallback_messages = [
        f"📖 Today's wisdom: {title[:50]}... Apply it in your code!",
        f"💡 Like today's text teaches, persevere in your coding journey!",
        f"🌟 Reflect on: {scripture[:40]}... while you create!",
        f"💪 Draw strength from today's text as you tackle challenges!",
        f"🎯 Apply today's lesson: Code with purpose and integrity!",
    ]
    
    return random.choice(fallback_messages)


def generate_jw_message(
    event_type: str = "SessionStart",
    time_period: Optional[str] = None,
    use_ollama: bool = True
) -> Optional[str]:
    """
    Generate a message based on JW daily text.
    
    Args:
        event_type: Type of event (SessionStart, Stop, Notification)
        time_period: Time period (morning, afternoon, evening)
        use_ollama: Whether to use ollama
        
    Returns:
        Encouraging message or None on error
    """
    client = JWDailyTextClient()
    
    # Determine time period if not provided
    if time_period is None:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 17:
            time_period = "afternoon"
        else:
            time_period = "evening"
    
    # Fetch daily text
    daily_text = client.fetch_for_time_period(time_period)
    
    if not daily_text:
        return None
    
    # Create developer encouragement
    return create_developer_encouragement(daily_text, use_ollama)


def test_jw_client():
    """Test the JW Daily Text client."""
    print("Testing JW Daily Text Client")
    print("=" * 50)
    
    client = JWDailyTextClient()
    
    # Test fetching today's text
    print("\nFetching today's daily text...")
    today_text = client.fetch_daily_text()
    
    if today_text:
        print(f"Date: {today_text['date'].strftime('%Y-%m-%d')}")
        print(f"Title: {today_text['title'][:60]}...")
        print(f"Reference: {today_text['reference']}")
        print(f"Scripture: {today_text['scripture'][:100]}...")
        
        # Test message generation
        print("\nGenerating developer encouragement...")
        
        # Without ollama
        message = create_developer_encouragement(today_text, use_ollama=False)
        print(f"Without ollama: {message}")
        
        # With ollama (if available)
        message = create_developer_encouragement(today_text, use_ollama=True)
        print(f"With ollama: {message}")
    else:
        print("Failed to fetch daily text")
    
    # Test random past date
    print("\n\nFetching random past daily text...")
    past_date = client.get_random_past_date(days_back=7)
    past_text = client.fetch_daily_text(past_date)
    
    if past_text:
        print(f"Date: {past_text['date'].strftime('%Y-%m-%d')}")
        print(f"Title: {past_text['title'][:60]}...")
    else:
        print("Failed to fetch past daily text")


if __name__ == "__main__":
    test_jw_client()