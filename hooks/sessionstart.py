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

# Try to import config
try:
    from lib.config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


def main():
    """Main function for SessionStart hook."""
    try:
        # Read input from stdin (Claude Code provides session info)
        input_data = json.load(sys.stdin)
        
        # Verify this is a SessionStart event
        if input_data.get("hook_event_name") != "SessionStart":
            sys.exit(1)
        
        # Check configuration if available
        if CONFIG_AVAILABLE:
            config = get_config()
            if not config.is_enabled():
                sys.exit(0)  # Exit silently if disabled
        
        # Generate encouraging message using configuration
        message = generate_message("SessionStart", use_config=CONFIG_AVAILABLE)
        
        # If message is empty (due to probability settings), exit silently
        if not message:
            sys.exit(0)
        
        # Format output for SessionStart (JSON with suppressOutput)
        output = format_hook_output(message, "SessionStart")
        
        # Output JSON to stdout
        print(json.dumps(output))
        
        # Success
        sys.exit(0)
        
    except Exception as e:
        # Check if errors should be suppressed
        if CONFIG_AVAILABLE:
            config = get_config()
            if not config.suppress_errors():
                print(f"Error in SessionStart hook: {e}", file=sys.stderr)
        # Exit quietly to not disrupt the user's session
        sys.exit(0)


if __name__ == "__main__":
    main()