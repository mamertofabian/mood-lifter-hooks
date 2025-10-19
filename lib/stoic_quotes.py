#!/usr/bin/env python3
"""
Stoic quotes and wisdom for calmness, self-control, and peace of mind.
Provides quotes from ancient Stoics and modern interpretations for developers.
"""

import random
import subprocess
import sys
import os
from typing import Optional, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.constants import Timeouts


# Curated stoic quotes focused on calmness, self-control, peace of mind, and managing anger
STOIC_QUOTES = [
    # Marcus Aurelius - Meditations
    {
        "text": "You have power over your mind - not outside events. Realize this, and you will find strength.",
        "author": "Marcus Aurelius",
        "theme": "control"
    },
    {
        "text": "The best revenge is not to be like your enemy.",
        "author": "Marcus Aurelius",
        "theme": "anger"
    },
    {
        "text": "How much more harmful are the consequences of anger than the causes of it.",
        "author": "Marcus Aurelius",
        "theme": "anger"
    },
    {
        "text": "The happiness of your life depends upon the quality of your thoughts.",
        "author": "Marcus Aurelius",
        "theme": "peace"
    },
    {
        "text": "If you are distressed by anything external, the pain is not due to the thing itself, but to your estimate of it.",
        "author": "Marcus Aurelius",
        "theme": "peace"
    },
    {
        "text": "The impediment to action advances action. What stands in the way becomes the way.",
        "author": "Marcus Aurelius",
        "theme": "obstacles"
    },
    {
        "text": "Very little is needed to make a happy life; it is all within yourself, in your way of thinking.",
        "author": "Marcus Aurelius",
        "theme": "peace"
    },
    {
        "text": "Confine yourself to the present.",
        "author": "Marcus Aurelius",
        "theme": "focus"
    },

    # Epictetus - Discourses and Enchiridion
    {
        "text": "It's not what happens to you, but how you react to it that matters.",
        "author": "Epictetus",
        "theme": "control"
    },
    {
        "text": "Any person capable of angering you becomes your master.",
        "author": "Epictetus",
        "theme": "anger"
    },
    {
        "text": "He is a wise man who does not grieve for the things which he has not, but rejoices for those which he has.",
        "author": "Epictetus",
        "theme": "peace"
    },
    {
        "text": "First say to yourself what you would be; and then do what you have to do.",
        "author": "Epictetus",
        "theme": "discipline"
    },
    {
        "text": "If anyone tells you that a certain person speaks ill of you, do not make excuses, but answer: 'He does not know my other faults, or he would not have mentioned only these.'",
        "author": "Epictetus",
        "theme": "criticism"
    },
    {
        "text": "Don't seek for everything to happen as you wish it would, but rather wish that everything happens as it actually will—then your life will flow well.",
        "author": "Epictetus",
        "theme": "acceptance"
    },
    {
        "text": "No person is free who is not master of himself.",
        "author": "Epictetus",
        "theme": "control"
    },

    # Seneca - Letters and Essays
    {
        "text": "The greatest remedy for anger is delay.",
        "author": "Seneca",
        "theme": "anger"
    },
    {
        "text": "We suffer more often in imagination than in reality.",
        "author": "Seneca",
        "theme": "worry"
    },
    {
        "text": "Difficulties strengthen the mind, as labor does the body.",
        "author": "Seneca",
        "theme": "obstacles"
    },
    {
        "text": "True happiness is to enjoy the present, without anxious dependence upon the future.",
        "author": "Seneca",
        "theme": "peace"
    },
    {
        "text": "The mind that is anxious about future events is miserable.",
        "author": "Seneca",
        "theme": "worry"
    },
    {
        "text": "If a person doesn't know to which port they sail, no wind is favorable.",
        "author": "Seneca",
        "theme": "purpose"
    },
    {
        "text": "Hang on to your youthful enthusiasms — you'll be able to use them better when you're older.",
        "author": "Seneca",
        "theme": "enthusiasm"
    },
    {
        "text": "Every new beginning comes from some other beginning's end.",
        "author": "Seneca",
        "theme": "change"
    },

    # Additional Stoic Wisdom
    {
        "text": "The obstacle is the way.",
        "author": "Ryan Holiday",
        "theme": "obstacles"
    },
    {
        "text": "Waste no more time arguing about what a good person should be. Be one.",
        "author": "Marcus Aurelius",
        "theme": "action"
    },
    {
        "text": "When another person makes you suffer, it is because they suffer deeply within themselves.",
        "author": "Thich Nhat Hanh (Stoic-aligned)",
        "theme": "compassion"
    },
    {
        "text": "Between stimulus and response there is a space. In that space is our power to choose our response.",
        "author": "Viktor Frankl (Stoic-aligned)",
        "theme": "control"
    },
    {
        "text": "The tranquility that comes when you stop caring what they say. Or think, or do. Only what you do.",
        "author": "Marcus Aurelius",
        "theme": "peace"
    },
    {
        "text": "Choose not to be harmed — and you won't feel harmed. Don't feel harmed — and you haven't been.",
        "author": "Marcus Aurelius",
        "theme": "resilience"
    },
    {
        "text": "Anger is an acid that can do more harm to the vessel in which it is stored than to anything on which it is poured.",
        "author": "Mark Twain (Stoic-aligned)",
        "theme": "anger"
    },
    {
        "text": "For every minute you remain angry, you give up sixty seconds of peace of mind.",
        "author": "Ralph Waldo Emerson (Stoic-aligned)",
        "theme": "anger"
    },
]


# General stoic principles for daily life
GENERAL_STOIC_WISDOM = [
    "The obstacle is not against you; it simply is. Your reaction determines your growth.",
    "Control your emotions, not others' opinions.",
    "Difficulties are inevitable. Your calm response is optional.",
    "The challenge doesn't care about your frustration. Handle it with clarity.",
    "Master your anxiety, and you master your life.",
    "Failure reveals truth. Your anger at it reveals weakness.",
    "Your circumstances do not control your inner peace. Your discipline does.",
    "The situation is what it is. Your approach to it defines you.",
    "Others' words don't create your reality. Your interpretation does.",
    "Life's lessons are teachers, not enemies. Learn without anger.",
]


def get_stoic_quote(theme: Optional[str] = None) -> Dict[str, str]:
    """
    Get a random stoic quote, optionally filtered by theme.

    Args:
        theme: Optional theme filter ('anger', 'control', 'peace', 'obstacles', etc.)

    Returns:
        Dictionary with 'text' and 'author' keys
    """
    if theme:
        filtered_quotes = [q for q in STOIC_QUOTES if q.get("theme") == theme]
        if filtered_quotes:
            quote = random.choice(filtered_quotes)
        else:
            # Fallback to any quote if theme not found
            quote = random.choice(STOIC_QUOTES)
    else:
        quote = random.choice(STOIC_QUOTES)

    return {
        "text": quote["text"],
        "author": quote["author"]
    }


def get_general_stoic_wisdom() -> str:
    """
    Get a random general stoic wisdom statement.

    Returns:
        A stoic principle for daily life
    """
    return random.choice(GENERAL_STOIC_WISDOM)


def enhance_stoic_quote_with_ollama(
    quote: Dict[str, str],
    event_type: str = "SessionStart",
    model: str = "llama3.2:latest"
) -> str:
    """
    Present stoic quote in a clean, readable format.
    No developer-specific adjustments - just the raw wisdom.

    Args:
        quote: Quote dictionary with 'text' and 'author'
        event_type: Type of event
        model: Ollama model to use (not used, kept for compatibility)

    Returns:
        Formatted quote
    """
    if not quote:
        return "🧘 Stay calm and carry on."

    quote_text = quote.get("text", "")
    author = quote.get("author", "")

    # Return the quote as-is with a simple emoji
    if len(quote_text) > 100:
        return f"🧘 \"{quote_text[:97]}...\" - {author}"
    else:
        return f"🧘 \"{quote_text}\" - {author}"


def generate_pure_stoic_wisdom(
    event_type: str = "SessionStart",
    theme: Optional[str] = None,
    model: str = "llama3.2:latest"
) -> Optional[str]:
    """
    Generate original stoic wisdom from scratch using ollama.
    Raw philosophical wisdom - not developer-specific.

    Args:
        event_type: Type of event
        theme: Optional theme to focus on (anger, control, peace, etc.)
        model: Ollama model to use

    Returns:
        Generated stoic wisdom or None if failed
    """
    # Build theme-specific context
    theme_context = ""
    if theme == "anger":
        theme_context = "Focus on managing anger and maintaining composure."
    elif theme == "control":
        theme_context = "Focus on what we can control versus what we cannot."
    elif theme == "peace":
        theme_context = "Focus on finding inner peace and tranquility."
    elif theme == "obstacles":
        theme_context = "Focus on viewing obstacles as opportunities for growth."
    else:
        theme_context = "Focus on timeless stoic wisdom."

    prompt = f"""Generate original stoic wisdom. {theme_context}

Write a brief, practical stoic principle for daily life.
Maximum 20 words. Include one zen/calm emoji (🧘, 💭, 🌊, ⚖️, or 🎯).
Make it sound like wisdom from Marcus Aurelius, Epictetus, or Seneca.
Do not quote existing stoics - create new wisdom in their style.
Only output the wisdom statement, no metadata or attribution."""

    try:
        result = subprocess.run(
            ["ollama", "run", model, "--verbose=false"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=Timeouts.OLLAMA_QUICK
        )

        if result.returncode == 0 and result.stdout:
            message = result.stdout.strip().split('\n')[0].strip()
            return message
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return None


def generate_stoic_message(
    event_type: str = "SessionStart",
    use_ollama: bool = True,
    theme: Optional[str] = None,
    use_general_wisdom: bool = False,
    pure_generation_ratio: float = 0.4
) -> str:
    """
    Generate a stoic wisdom message.

    Args:
        event_type: Type of event
        use_ollama: Whether to use ollama (for enhancement or pure generation)
        theme: Optional theme filter
        use_general_wisdom: If True, use general stoic wisdom statements
        pure_generation_ratio: Ratio of pure LLM generation vs quote-based (0.0-1.0)

    Returns:
        Stoic wisdom message
    """
    if use_general_wisdom:
        # Use general wisdom directly (doesn't need ollama)
        wisdom = get_general_stoic_wisdom()
        return f"🧘 {wisdom}"

    # Decide whether to use pure LLM generation or quote-based approach
    if use_ollama and random.random() < pure_generation_ratio:
        # Generate from scratch using ollama
        pure_wisdom = generate_pure_stoic_wisdom(event_type, theme)
        if pure_wisdom:
            return pure_wisdom
        # Fall through to quote-based if pure generation fails

    # Get a stoic quote
    quote = get_stoic_quote(theme)

    if use_ollama:
        return enhance_stoic_quote_with_ollama(quote, event_type)
    else:
        # Return formatted quote without ollama
        return f"🧘 \"{quote['text']}\" - {quote['author']}"


def get_fallback_stoic_message() -> str:
    """Get a fallback stoic message when generation fails."""
    return random.choice([
        "🧘 Control what you can: your code, your response, your calm.",
        "💭 The bug will pass. Your composure is permanent.",
        "🌊 Like water around a rock, flow around obstacles in your code.",
        "⚖️ Balance your ambition with acceptance of what is.",
        "🎯 Focus on the present line of code, not yesterday's bugs or tomorrow's deadlines.",
    ])


def test_stoic_quotes():
    """Test the stoic quotes module."""
    print("Testing Stoic Quotes Module")
    print("=" * 60)

    # Test getting quotes by theme
    print("\n1. Quotes by Theme:")
    for theme in ["anger", "control", "peace", "obstacles"]:
        quote = get_stoic_quote(theme=theme)
        print(f"\n   {theme.upper()}:")
        print(f"   \"{quote['text']}\"")
        print(f"   - {quote['author']}")

    # Test random quotes
    print("\n\n2. Random Quotes (5 samples):")
    for i in range(5):
        quote = get_stoic_quote()
        print(f"\n   {i+1}. \"{quote['text'][:60]}...\"")
        print(f"      - {quote['author']}")

    # Test developer wisdom
    print("\n\n3. Developer-Specific Stoic Wisdom (5 samples):")
    for i in range(5):
        wisdom = get_developer_stoic_wisdom()
        print(f"   {i+1}. {wisdom}")

    # Test message generation
    print("\n\n4. Message Generation:")
    print("\n   Without ollama:")
    msg = generate_stoic_message(use_ollama=False)
    print(f"   {msg}")

    print("\n   With developer wisdom:")
    msg = generate_stoic_message(use_developer_wisdom=True)
    print(f"   {msg}")

    print("\n   With ollama (quote-based, may take a moment):")
    msg = generate_stoic_message(use_ollama=True, pure_generation_ratio=0.0)
    print(f"   {msg}")

    print("\n   Pure LLM generation (from scratch):")
    msg = generate_pure_stoic_wisdom()
    if msg:
        print(f"   {msg}")
    else:
        print("   Failed to generate")

    print("\n   Mixed approach (40% pure, 60% quote-based) - 5 samples:")
    for i in range(5):
        msg = generate_stoic_message(use_ollama=True, pure_generation_ratio=0.4)
        prefix = "[PURE]" if not any(name in msg for name in ['Marcus', 'Epictetus', 'Seneca', 'Ryan', '"']) else "[QUOTE]"
        print(f"   {i+1}. {prefix} {msg[:65]}...")

    # Test fallback
    print("\n\n5. Fallback Messages (3 samples):")
    for i in range(3):
        msg = get_fallback_stoic_message()
        print(f"   {i+1}. {msg}")


if __name__ == "__main__":
    test_stoic_quotes()
