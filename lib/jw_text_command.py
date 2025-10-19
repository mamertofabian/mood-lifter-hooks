#!/usr/bin/env python3
"""
On-demand JW Daily Text display for Claude Code slash command
"""

import json
import subprocess
import random
import sys
import re
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional, Tuple

# Fallback encouraging messages
FALLBACK_ENCOURAGEMENT = [
    "💪 Keep coding with wisdom and purpose!",
    "🌟 Your dedication to quality code reflects spiritual values!",
    "🎯 Focus on building with integrity and excellence!",
    "🔧 Every line of code can be an act of love and service!",
    "✨ Let wisdom guide your development today!",
    "🙏 May your work glorify the Creator through excellence!",
    "📖 Apply scriptural principles to create meaningful software!",
    "🌱 Grow in skill while maintaining spiritual balance!"
]

# Fallback daily texts if fetch fails
FALLBACK_TEXTS = [
    {
        "date": "Daily Wisdom",
        "scripture": "Proverbs 2:6 - 'Jehovah himself gives wisdom'",
        "text": "True wisdom comes from above. As developers, we can seek divine guidance in solving complex problems.",
        "message": "💻 Just as we seek divine wisdom, pursue clean, thoughtful code that serves others well!"
    },
    {
        "date": "Daily Encouragement",
        "scripture": "Ecclesiastes 9:10 - 'Whatever your hand finds to do, do with all your might'",
        "text": "Excellence in our work, including coding, brings honor to our Creator.",
        "message": "🚀 Code with excellence and dedication - your work reflects your values!"
    },
    {
        "date": "Daily Motivation",
        "scripture": "Colossians 3:23 - 'Whatever you do, work at it with all your heart'",
        "text": "Wholehearted effort in our programming work can be a form of worship.",
        "message": "✨ Every function you write can be an act of love and service to users!"
    }
]

def fetch_daily_text() -> Tuple[Optional[str], Optional[str]]:
    """Fetch today's daily text from JW.org"""
    try:
        today = datetime.now()
        url = f"https://wol.jw.org/wol/dt/r1/lp-e/{today.year}/{today.month}/{today.day}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            
        # Extract theme scripture
        theme_match = re.search(r'class="themeScrp"[^>]*>(.*?)</p>', html, re.DOTALL)
        if not theme_match:
            theme_match = re.search(r'<p[^>]*>([^<]*<a[^>]*>[^<]*</a>[^<]*)</p>', html)
        
        # Extract daily text
        text_match = re.search(r'class="sb"[^>]*>(.*?)</p>', html, re.DOTALL)
        if not text_match:
            text_match = re.search(r'<div[^>]*class="[^"]*bodyTxt[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        
        if theme_match:
            theme = re.sub(r'<[^>]+>', '', theme_match.group(1)).strip()
            theme = ' '.join(theme.split())
        else:
            theme = None
            
        if text_match:
            text = re.sub(r'<[^>]+>', '', text_match.group(1)).strip()
            text = ' '.join(text.split())[:300]  # Limit to 300 chars
        else:
            text = None
            
        return theme, text
    except Exception as e:
        return None, None

def generate_developer_encouragement(scripture: str, text: str) -> str:
    """Generate developer-focused encouragement using ollama"""
    try:
        # Check if ollama is available
        result = subprocess.run(
            ['ollama', 'list'], 
            capture_output=True, 
            text=True, 
            timeout=2
        )
        
        if result.returncode != 0:
            return random.choice(FALLBACK_ENCOURAGEMENT)
        
        # Parse available models
        models = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if line:
                model_name = line.split()[0]
                models.append(model_name)
        
        if not models:
            return random.choice(FALLBACK_ENCOURAGEMENT)
        
        # Select lightweight model
        preferred_models = ['llama3.2:latest', 'mistral:7b-instruct', 'llama3.2:1b']
        model = next((m for m in preferred_models if any(m.startswith(pm.split(':')[0]) for pm in models)), models[0])
        
        # Generate encouragement
        prompt = f"""Based on this scripture: "{scripture}"
        
Create a very brief (under 30 words) encouraging message for developers that connects this spiritual principle to their coding work. Be practical and uplifting."""
        
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return "💻 " + result.stdout.strip()
        else:
            return random.choice(FALLBACK_ENCOURAGEMENT)
            
    except Exception:
        return random.choice(FALLBACK_ENCOURAGEMENT)

def main():
    """Main function to display daily text"""
    # Get today's date
    today = datetime.now().strftime("%B %d, %Y")
    
    print(f"📅 Daily Text for {today}")
    print("=" * 50)
    
    # Try to fetch real daily text
    scripture, text = fetch_daily_text()
    
    if scripture and text:
        print(f"\n📖 {scripture}\n")
        print(f"💭 {text}\n")
        
        # Generate developer encouragement
        encouragement = generate_developer_encouragement(scripture, text)
        print("=" * 50)
        print(f"\n{encouragement}")
    else:
        # Use fallback
        fallback = random.choice(FALLBACK_TEXTS)
        print(f"\n📖 {fallback['scripture']}\n")
        print(f"💭 {fallback['text']}\n")
        print("=" * 50)
        print(f"\n{fallback['message']}")
    
    print("\n🙏 May your code be blessed with wisdom and purpose today!\n")

if __name__ == "__main__":
    main()