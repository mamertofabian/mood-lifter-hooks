#!/usr/bin/env python3
"""
Notification hook for Mood Lifter Hooks.
Displays an encouraging message when Claude sends notifications.
"""

import json
import sys
import os

# Add ~/.claude to path to import message_generator (where install.sh copies it)
sys.path.insert(0, os.path.expanduser('~/.claude'))
from message_generator import generate_message

try:
    # Read input from stdin (Claude Code provides session info)
    input_data = json.load(sys.stdin)
    
    # Verify this is a Notification event
    if input_data.get("hook_event_name") != "Notification":
        sys.exit(1)
    
    # Generate and display message
    message = generate_message('Notification')
    if message:
        print("\n" + message)
    
except Exception:
    # Exit quietly on error
    pass