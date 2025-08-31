#!/usr/bin/env python3
"""
Notification hook for Mood Lifter Hooks.
Displays an encouraging message when Claude sends notifications.
"""

import json
import sys
import os

# Add parent directory to path to import message_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.message_generator import generate_message


def main():
    """Main function for Notification hook."""
    try:
        # Read input from stdin (Claude Code provides session info)
        input_data = json.load(sys.stdin)
        
        # Verify this is a Notification event
        if input_data.get("hook_event_name") != "Notification":
            sys.exit(1)
        
        # Check what type of notification this is
        notification_message = input_data.get("message", "")
        
        # Only show encouragement for certain notifications
        # (e.g., when Claude is waiting for input or needs permission)
        if "waiting" in notification_message.lower() or "permission" in notification_message.lower():
            # Generate encouraging message
            message = generate_message("Notification", use_ollama=True)
            
            # For Notification hooks, output to stdout (not added to context)
            print(message)
        
        # Success
        sys.exit(0)
        
    except Exception as e:
        # On error, just exit quietly
        sys.exit(0)


if __name__ == "__main__":
    main()