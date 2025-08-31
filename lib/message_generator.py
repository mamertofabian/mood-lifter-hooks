#!/usr/bin/env python3
"""
Message generator module for Mood Lifter Hooks.
Generates encouraging messages using ollama with fallback options.
"""

import subprocess
import random
import json
import sys
from datetime import datetime
from typing import Optional, Dict

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


def generate_with_ollama(event_type: str, model: str = "phi3.5:3.8b") -> Optional[str]:
    """
    Generate an encouraging message using ollama.
    
    Args:
        event_type: Type of event (SessionStart, Stop, Notification)
        model: Ollama model to use
        
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
        
        # Call ollama with timeout
        result = subprocess.run(
            ["ollama", "run", model, "--verbose=false"],
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


def generate_message(event_type: str, use_ollama: bool = True, model: str = "phi3.5:3.8b") -> str:
    """
    Generate an encouraging message for the given event type.
    
    Args:
        event_type: Type of event (SessionStart, Stop, Notification)
        use_ollama: Whether to try using ollama first
        model: Ollama model to use
        
    Returns:
        An encouraging message
    """
    if use_ollama:
        message = generate_with_ollama(event_type, model)
        if message:
            return message
    
    # Fall back to pre-written messages
    return get_fallback_message(event_type)


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
    print("Testing Message Generator")
    print("=" * 50)
    
    for event in ["SessionStart", "Stop", "Notification"]:
        print(f"\n{event}:")
        print(f"  With ollama: {generate_message(event, use_ollama=True)}")
        print(f"  Fallback: {generate_message(event, use_ollama=False)}")