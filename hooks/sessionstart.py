#!/usr/bin/env python3
"""
SessionStart hook for Mood Lifter Hooks.
Displays an encouraging message when a Claude Code session starts.
"""

import json
import sys
import os

# Add parent directory to path to import message_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.message_generator import generate_message, format_hook_output


def main():
    """Main function for SessionStart hook."""
    try:
        # Read input from stdin (Claude Code provides session info)
        input_data = json.load(sys.stdin)
        
        # Verify this is a SessionStart event
        if input_data.get("hook_event_name") != "SessionStart":
            sys.exit(1)
        
        # Generate encouraging message
        message = generate_message("SessionStart", use_ollama=True)
        
        # Format output for SessionStart (JSON with suppressOutput)
        output = format_hook_output(message, "SessionStart")
        
        # Output JSON to stdout
        print(json.dumps(output))
        
        # Success
        sys.exit(0)
        
    except Exception as e:
        # On error, just exit quietly
        # We don't want to disrupt the user's session with errors
        sys.exit(0)


if __name__ == "__main__":
    main()