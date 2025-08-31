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

# Try to import config
try:
    from lib.config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


def main():
    """Main function for Notification hook."""
    try:
        # Read input from stdin (Claude Code provides session info)
        input_data = json.load(sys.stdin)
        
        # Verify this is a Notification event
        if input_data.get("hook_event_name") != "Notification":
            sys.exit(1)
        
        # Check configuration if available
        if CONFIG_AVAILABLE:
            config = get_config()
            if not config.is_enabled():
                sys.exit(0)  # Exit silently if disabled
        
        # Check what type of notification this is
        notification_message = input_data.get("message", "")
        
        # Only show encouragement for certain notifications
        # (e.g., when Claude is waiting for input or needs permission)
        if "waiting" in notification_message.lower() or "permission" in notification_message.lower():
            # Generate encouraging message using configuration
            message = generate_message("Notification", use_config=CONFIG_AVAILABLE)
            
            # If message is empty (due to probability settings), exit silently
            if not message:
                sys.exit(0)
            
            # For Notification hooks, output to stdout (not added to context)
            print(message)
        
        # Success
        sys.exit(0)
        
    except Exception as e:
        # Check if errors should be suppressed
        if CONFIG_AVAILABLE:
            config = get_config()
            if not config.suppress_errors():
                print(f"Error in Notification hook: {e}", file=sys.stderr)
        # Exit quietly
        sys.exit(0)


if __name__ == "__main__":
    main()