#!/usr/bin/env python3
"""
SessionStart hook for Mood Lifter Hooks.
Displays an encouraging message when a Claude Code session starts.
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
    
    # Verify this is a SessionStart event
    if input_data.get("hook_event_name") != "SessionStart":
        sys.exit(1)
    
    # Generate encouraging message
    message = generate_message('SessionStart')
    
    # For SessionStart, just print the message
    # The hook output is automatically not added to context
    if message:
        print(message)
    
except Exception:
    # Exit quietly on error
    pass