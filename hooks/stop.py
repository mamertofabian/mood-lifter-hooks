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
    
    # Generate and display message using JSON format
    try:
        message = generate_message('Stop')
        if not message:
            message = "🎉 Great work! Your efforts today matter!"
    except:
        # Simple fallback if message generation fails
        message = "✨ Session complete! Keep up the great work!"
    
    # Use JSON output format for proper display in Claude Code
    output = {
        "systemMessage": message
    }
    print(json.dumps(output), flush=True)
    
except Exception as e:
    # Print a fallback message even on error
    fallback_output = {
        "systemMessage": "🌟 Well done! Your coding session is complete!"
    }
    print(json.dumps(fallback_output), flush=True)