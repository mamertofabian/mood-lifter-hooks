#!/usr/bin/env python3
"""
Stop hook for Mood Lifter Hooks.
Displays an encouraging message when Claude finishes responding.
"""

import json
import sys
import os

# Add parent directory to path to import message_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.message_generator import generate_message


def main():
    """Main function for Stop hook."""
    try:
        # Read input from stdin (Claude Code provides session info)
        input_data = json.load(sys.stdin)
        
        # Verify this is a Stop event
        if input_data.get("hook_event_name") != "Stop":
            sys.exit(1)
        
        # Check if stop_hook_active to prevent infinite loops
        if input_data.get("stop_hook_active", False):
            # Don't generate messages if we're already in a stop hook
            sys.exit(0)
        
        # Generate encouraging message
        message = generate_message("Stop", use_ollama=True)
        
        # For Stop hooks, output to stdout (not added to context)
        print(message)
        
        # Success
        sys.exit(0)
        
    except Exception as e:
        # On error, just exit quietly
        sys.exit(0)


if __name__ == "__main__":
    main()