#!/usr/bin/env python3
"""
JW Daily Text integration for Mood Lifter Hooks.
Fetches daily text from JW.org and creates developer-focused encouragement.
"""

import random
import subprocess
import sys
import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.api_integrations import APIClient
from lib.constants import Timeouts, CacheDuration


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
            cache_ttl_minutes=cache_ttl_hours * 60,
            timeout=Timeouts.JW_API,
            persistent_cache=True,  # Enable persistent caching for JW content
            cache_dir=os.path.expanduser("~/.claude-code/mood-lifter/jw_cache")
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
                
                # Parse the HTML content to extract scripture and commentary
                scripture_text = ""
                commentary = ""
                
                if content:
                    # Extract the daily text scripture from the themeScrp paragraph
                    # Pattern to find the scripture text and reference
                    scripture_pattern = r'<p[^>]*class="themeScrp"[^>]*>.*?<em>(.*?)</em>.*?<em>(.*?)</em>.*?</p>'
                    scripture_match = re.search(scripture_pattern, content, re.DOTALL)
                    
                    if scripture_match:
                        # Combine the text and reference
                        text_part = re.sub(r'<[^>]+>', '', scripture_match.group(1)).strip()
                        ref_part = re.sub(r'<[^>]+>', '', scripture_match.group(2)).strip()
                        scripture_text = f"{text_part}{ref_part}"
                    
                    # Extract the commentary from bodyTxt div
                    bodytext_pattern = r'<div class="bodyTxt">(.*?)</div>'
                    bodytext_match = re.search(bodytext_pattern, content, re.DOTALL)
                    
                    if bodytext_match:
                        # Remove HTML tags from commentary
                        commentary_html = bodytext_match.group(1)
                        # Remove all HTML tags but keep the text
                        commentary = re.sub(r'<[^>]+>', ' ', commentary_html)
                        # Clean up extra whitespace
                        commentary = ' '.join(commentary.split()).strip()
                
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
    Create spiritual encouragement from daily text.
    
    Args:
        daily_text: Daily text data
        use_ollama: Whether to use ollama for enhancement
        model: Ollama model to use
        
    Returns:
        Encouraging message
    """
    if not daily_text:
        return "💫 Keep coding with purpose and dedication!"
    
    scripture = daily_text.get("scripture", "").strip()
    commentary = daily_text.get("commentary", "").strip()
    title = daily_text.get("title", "").strip()
    
    # Format the scripture text for display
    scripture_display = scripture if scripture else ""
    
    if use_ollama:
        # Create a prompt for ollama to summarize the daily text
        # Keep it pure - just summarize the spiritual message without programming context
        # Include both scripture and commentary for full context
        full_text = f"{scripture_display} {commentary}" if scripture_display and commentary else (commentary or scripture_display or 'N/A')
        
        prompt = f"""Daily text to summarize:
{full_text}

Summarize the main spiritual message in one to three concise, encouraging sentences. 
Keep the original spiritual essence."""
        
        try:
            result = subprocess.run(
                ["ollama", "run", model, "--verbose=false"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=Timeouts.OLLAMA_NORMAL
            )
            
            if result.returncode == 0 and result.stdout:
                summary = result.stdout.strip()
                # Include the scripture text followed by the summary
                if scripture_display:
                    return f"📖 {scripture_display}\n{summary}"
                else:
                    return f"📖 Today's spiritual encouragement:\n{summary}"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Fallback messages that include the scripture text
    if scripture_display:
        return f"📖 {scripture_display}\n💡 Reflect on this spiritual encouragement for your day."
    else:
        # If no scripture extracted, use simpler fallback
        return f"📖 Today's text: {title[:50] if title else 'Daily wisdom'}\n🌟 Draw strength from today's spiritual message."


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