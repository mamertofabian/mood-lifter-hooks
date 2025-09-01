#!/usr/bin/env python3
"""
Stop hook for Mood Lifter Hooks.
Displays an encouraging message when Claude finishes responding.
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
    
    # Verify this is a Stop event
    if input_data.get("hook_event_name") != "Stop":
        sys.exit(1)
    
    # Check if stop_hook_active to prevent infinite loops
    if input_data.get("stop_hook_active", False):
        sys.exit(0)
    
    # Generate and display message
    message = generate_message('Stop')
    if message:
        print("\n" + message)
    
except Exception:
    # Exit quietly on error
    pass