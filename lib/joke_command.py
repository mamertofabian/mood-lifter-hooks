#!/usr/bin/env python3
"""
On-demand joke generator for Claude Code slash command
"""

import subprocess
import random
import sys

# Extensive collection of developer jokes
FALLBACK_JOKES = [
    "🎭 Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "☕ A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?' 🍻",
    "🔍 Why did the developer go broke? Because he used up all his cache! 💰",
    "🐛 99 little bugs in the code, 99 little bugs. Take one down, patch it around... 127 little bugs in the code! 🎪",
    "🤖 How many programmers does it take to change a light bulb? None. It's a hardware problem! 💡",
    "🎨 CSS is like a good joke - if you have to explain it, it's not that good! 🎭",
    "⚡ Why do Java developers wear glasses? Because they don't C#! 👓",
    "🔧 'It works on my machine' - Famous last words! 💻",
    "🎯 There are only 10 types of people: those who understand binary and those who don't! 🔢",
    "🚀 Programming is like writing a book... except if you miss a semicolon, the whole thing makes no sense! 📚",
    "🎪 A programmer's spouse asks: 'Would you go to the store and pick up a loaf of bread? And if they have eggs, get a dozen.' The programmer returns with 12 loaves of bread. 🍞",
    "🏃 Why did the programmer quit his job? Because he didn't get arrays! 📊",
    "🎯 Algorithm: A word used by programmers when they don't want to explain what they did! 🤫",
    "🐍 Python programmers don't byte, they just nibble a bit! 🍰",
    "🎮 Real programmers count from 0. 💯",
    "🔄 Recursion (n): See 'Recursion' 🔁",
    "☕ I don't have a problem with caffeine. I have a problem without it! ☕",
    "💾 There's no place like 127.0.0.1 🏠",
    "🎯 Programming is 10% writing code and 90% figuring out why it doesn't work! 🔍",
    "🎪 My code doesn't have bugs. It just develops random features! ✨",
    "🚨 A good programmer is someone who always looks both ways before crossing a one-way street! 🚦",
    "📝 Documentation? We don't need documentation. The code is self-documenting! (Famous last words) 📚",
    "🎭 I told my wife I'd be home in a minute. That was before I started debugging... ⏰",
    "🔨 When all you have is a hammer, everything looks like a nail. When all you know is JavaScript, everything looks like a JSON! 🔧",
    "🌟 The best thing about a Boolean is that even if you're wrong, you're only off by a bit! 💡"
]

def generate_joke_with_ollama():
    """Try to generate a joke using ollama"""
    try:
        # Check if ollama is available
        result = subprocess.run(
            ['ollama', 'list'], 
            capture_output=True, 
            text=True, 
            timeout=2
        )
        
        if result.returncode != 0:
            return None
        
        # Parse available models
        models = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if line:
                model_name = line.split()[0]
                models.append(model_name)
        
        if not models:
            return None
        
        # Select lightweight model
        preferred_models = ['phi3.5:3.8b', 'mistral:7b-instruct', 'llama3.2:1b', 'gemma2:2b']
        model = next((m for m in preferred_models if any(m.startswith(pm.split(':')[0]) for pm in models)), models[0])
        
        # Generate joke
        prompts = [
            "Tell me a short, funny programming joke. Keep it under 50 words. Be creative and original. Only output the joke, no metadata.",
            "Share a witty developer joke about debugging, git, or coding. Maximum 50 words. Only output the joke, no metadata.",
            "Create a humorous programming pun or wordplay. Keep it brief and clever. Only output the joke, no metadata.",
            "Tell a funny story about a programmer's daily life in under 50 words. Only output the story, no metadata.",
            "Share a tech joke about JavaScript, Python, or any programming language. Be concise and funny. Only output the joke, no metadata."
        ]
        
        prompt = random.choice(prompts)
        
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            joke = result.stdout.strip()
            # Add a random emoji for fun
            emojis = ['😄', '🎭', '😂', '🤓', '💻', '🐛', '🚀', '☕', '🤖', '🎪', '✨']
            return f"{random.choice(emojis)} {joke}"
        
        return None
            
    except Exception:
        return None

def main():
    """Main function to display a joke"""
    # Try ollama first
    joke = generate_joke_with_ollama()
    
    # Fall back to pre-written jokes if ollama fails
    if not joke:
        joke = random.choice(FALLBACK_JOKES)
    
    print("\n" + "=" * 50)
    print("😄 Developer Joke of the Moment")
    print("=" * 50 + "\n")
    print(joke)
    print("\n" + "=" * 50)
    print("Keep coding with a smile! 😊\n")

if __name__ == "__main__":
    main()