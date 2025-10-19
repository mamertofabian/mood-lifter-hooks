#!/usr/bin/env python3
"""
External API integrations for jokes and quotes.
Provides general jokes and inspirational quotes.
"""

import random
import subprocess
import sys
import os
from typing import Optional, List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.api_integrations import APIClient
from lib.constants import Timeouts, CacheDuration


class JokeQuoteClient:
    """Client for fetching jokes and quotes from various APIs."""
    
    def __init__(self):
        """Initialize the joke/quote client."""
        self.api_client = APIClient(
            cache_ttl_minutes=CacheDuration.EXTERNAL_CONTENT,
            timeout=Timeouts.EXTERNAL_APIS
        )
        
        # Public APIs that don't require authentication
        self.dad_joke_api = "https://icanhazdadjoke.com/"
        # Reliable quote APIs
        self.zenquotes_api = "https://zenquotes.io/api/random"
        self.quotegarden_api = "https://quote-garden.herokuapp.com/api/v3/quotes/random"
        # General joke APIs
        self.general_joke_api = "https://v2.jokeapi.dev/joke/Miscellaneous,Pun"
        self.official_joke_api = "https://official-joke-api.appspot.com/jokes/random"
    
    def get_dad_joke(self) -> Optional[str]:
        """
        Fetch a dad joke from icanhazdadjoke API.
        
        Returns:
            Dad joke text or None on error
        """
        headers = {"Accept": "application/json"}
        data = self.api_client.get(self.dad_joke_api, headers=headers)
        
        if data and isinstance(data, dict):
            return data.get("joke", "")
        
        return None
    
    def get_general_joke(self) -> Optional[str]:
        """
        Fetch a general joke from multiple sources.

        Returns:
            Joke text or None on error
        """
        # Try JokeAPI first (best quality) - miscellaneous and puns only
        data = self.api_client.get(self.general_joke_api + "?safe-mode")
        if data and isinstance(data, dict):
            if data.get("type") == "single":
                return data.get("joke", "")
            elif data.get("type") == "twopart":
                setup = data.get("setup", "")
                delivery = data.get("delivery", "")
                if setup and delivery:
                    return f"{setup} {delivery}"

        # Fallback to Official Joke API (random jokes)
        data = self.api_client.get(self.official_joke_api)
        if isinstance(data, dict):
            setup = data.get("setup", "")
            punchline = data.get("punchline", "")
            if setup and punchline:
                return f"{setup} {punchline}"

        return None
    
    def get_inspirational_quote(self) -> Optional[Dict[str, str]]:
        """
        Fetch an inspirational quote with fallback.
        
        Returns:
            Dictionary with 'text' and 'author' or None on error
        """
        # Try Zen Quotes API first
        data = self.api_client.get(self.zenquotes_api)
        if data and isinstance(data, list) and len(data) > 0:
            quote_data = data[0]
            if isinstance(quote_data, dict):
                return {
                    "text": quote_data.get("q", ""),
                    "author": quote_data.get("a", "Unknown")
                }
        
        # Fallback to Quote Garden API
        data = self.api_client.get(self.quotegarden_api)
        if data and isinstance(data, dict):
            quote_data = data.get("data", [])
            if isinstance(quote_data, list) and len(quote_data) > 0:
                quote = quote_data[0]
                if isinstance(quote, dict):
                    return {
                        "text": quote.get("quoteText", ""),
                        "author": quote.get("quoteAuthor", "Unknown")
                    }
        
        return None
    
    def get_chuck_norris_joke(self) -> Optional[str]:
        """
        Fetch a general Chuck Norris joke.

        Returns:
            Joke text or None on error
        """
        url = "https://api.chucknorris.io/jokes/random?category=dev"
        data = self.api_client.get(url)
        
        if data and isinstance(data, dict):
            return data.get("value", "")
        
        return None
    
    def get_random_content(self, content_type: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Get random content from available APIs.
        
        Args:
            content_type: Optional type filter ('joke', 'quote', or None for any)
            
        Returns:
            Dictionary with 'content', 'type', and optionally 'author'
        """
        if content_type == "joke":
            sources = ["dad_joke", "general_joke"]
        elif content_type == "quote":
            sources = ["inspirational_quote"]
        else:
            sources = ["dad_joke", "general_joke", "inspirational_quote"]
        
        # Try sources in random order
        random.shuffle(sources)
        
        for source in sources:
            try:
                if source == "dad_joke":
                    joke = self.get_dad_joke()
                    if joke:
                        return {"content": joke, "type": "joke", "source": "Dad Joke"}
                
                elif source == "general_joke":
                    joke = self.get_general_joke()
                    if joke:
                        return {"content": joke, "type": "joke", "source": "Programming Joke"}
                
                elif source == "chuck_norris":
                    joke = self.get_chuck_norris_joke()
                    if joke:
                        return {"content": joke, "type": "joke", "source": "Chuck Norris"}
                
                elif source == "inspirational_quote":
                    quote = self.get_inspirational_quote()
                    if quote and quote["text"]:
                        return {
                            "content": quote["text"],
                            "author": quote["author"],
                            "type": "quote",
                            "source": "Inspirational Quote"
                        }
            except Exception:
                # Try next source if this one fails
                continue
        
        return None


def enhance_with_ollama(
    content: Dict[str, str],
    event_type: str = "SessionStart",
    model: str = "llama3.2:latest"
) -> str:
    """
    Present joke or quote in clean format - no enhancement needed.
    Just return the content as-is.

    Args:
        content: Content dictionary from API
        event_type: Type of event (not used, kept for compatibility)
        model: Ollama model to use (not used, kept for compatibility)

    Returns:
        Formatted content
    """
    if not content:
        return "💫 Keep your enthusiasm!"

    content_text = content.get("content", "")
    content_type = content.get("type", "")
    author = content.get("author", "")

    # Return content as-is with appropriate emoji
    if content_type == "joke":
        return f"😄 {content_text}"
    else:  # quote
        if author:
            return f"💭 \"{content_text}\" - {author}"
        else:
            return f"💭 {content_text}"


def generate_external_message(
    event_type: str = "SessionStart",
    content_type: Optional[str] = None,
    use_ollama: bool = True
) -> Optional[str]:
    """
    Generate a message from external APIs.
    
    Args:
        event_type: Type of event
        content_type: Type of content to fetch ('joke', 'quote', or None)
        use_ollama: Whether to enhance with ollama
        
    Returns:
        Message or None on error
    """
    client = JokeQuoteClient()
    
    # Get random content
    content = client.get_random_content(content_type)
    
    if not content:
        return None
    
    if use_ollama:
        return enhance_with_ollama(content, event_type)
    else:
        # Return formatted content without ollama
        if content.get("type") == "joke":
            return f"😄 {content['content'][:100]}"
        else:
            author = content.get("author", "Unknown")
            return f"💭 \"{content['content'][:80]}\" - {author}"


# Fallback messages if APIs are unavailable - general humor
FALLBACK_JOKES = [
    "Why don't scientists trust atoms? Because they make up everything! 🔬",
    "What do you call a fake noodle? An impasta! 🍝",
    "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
    "What do you call a bear with no teeth? A gummy bear! 🐻",
    "Why did the bicycle fall over? It was two tired! 🚲",
    "What do you call a fish wearing a bowtie? Sofishticated! 🐟",
    "Why did the math book look sad? Because it had too many problems! 📚",
    "What's the best thing about Switzerland? The flag is a big plus! 🇨🇭",
]

FALLBACK_QUOTES = [
    '"The only way to do great work is to love what you do." - Steve Jobs',
    '"Experience is the name everyone gives to their mistakes." - Oscar Wilde',
    '"The best way to predict the future is to create it." - Peter Drucker',
    '"Believe you can and you\'re halfway there." - Theodore Roosevelt',
    '"In the middle of difficulty lies opportunity." - Albert Einstein',
]


def get_fallback_external_message(content_type: Optional[str] = None) -> str:
    """Get a fallback message when APIs are unavailable."""
    if content_type == "joke":
        return random.choice(FALLBACK_JOKES)
    elif content_type == "quote":
        return random.choice(FALLBACK_QUOTES)
    else:
        all_messages = FALLBACK_JOKES + FALLBACK_QUOTES
        return random.choice(all_messages)


def test_external_apis():
    """Test the external API integrations."""
    print("Testing External API Integrations")
    print("=" * 50)
    
    client = JokeQuoteClient()
    
    # Test dad joke
    print("\n1. Dad Joke API:")
    joke = client.get_dad_joke()
    if joke:
        print(f"   ✓ {joke[:80]}...")
    else:
        print("   ✗ Failed to fetch dad joke")
    
    # Test inspirational quote
    print("\n2. Inspirational Quote API:")
    quote = client.get_inspirational_quote()
    if quote:
        print(f"   ✓ \"{quote['text'][:60]}...\" - {quote['author']}")
    else:
        print("   ✗ Failed to fetch inspirational quote")
    
    # Test Chuck Norris joke
    print("\n3. Chuck Norris Joke API:")
    joke = client.get_chuck_norris_joke()
    if joke:
        print(f"   ✓ {joke[:80]}...")
    else:
        print("   ✗ Failed to fetch Chuck Norris joke")
    
    # Test random content
    print("\n4. Random Content:")
    for _ in range(3):
        content = client.get_random_content()
        if content:
            if content.get("type") == "joke":
                print(f"   • Joke: {content['content'][:60]}...")
            else:
                print(f"   • Quote: \"{content['content'][:50]}...\" - {content.get('author', 'Unknown')}")
    
    # Test message generation
    print("\n5. Message Generation:")
    print("   Without ollama:")
    msg = generate_external_message(use_ollama=False)
    print(f"   {msg}")
    
    print("\n   With ollama:")
    msg = generate_external_message(use_ollama=True)
    print(f"   {msg}")


if __name__ == "__main__":
    test_external_apis()