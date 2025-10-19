#!/usr/bin/env python3
"""
Stop hook for Mood Lifter Hooks.
Displays an encouraging message when Claude finishes responding.
"""

import json
import sys
import os
from datetime import datetime

# Add ~/.claude to path to import message_generator (where install.sh copies it)
sys.path.insert(0, os.path.expanduser('~/.claude'))
from message_generator import generate_message

# Debug logging
DEBUG_LOG = os.path.expanduser('~/.claude/debug/stop_hook_debug.log')

def debug_log(message, data=None):
    """Log debug information to file."""
    try:
        os.makedirs(os.path.dirname(DEBUG_LOG), exist_ok=True)
        with open(DEBUG_LOG, 'a') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"\n{'='*60}\n")
            f.write(f"[{timestamp}] {message}\n")
            if data:
                f.write(json.dumps(data, indent=2))
                f.write("\n")
    except:
        pass

try:
    # Read input from stdin (Claude Code provides session info)
    input_data = json.load(sys.stdin)

    # Log all invocations
    debug_log("Stop hook triggered", input_data)

    # Verify this is a Stop event
    if input_data.get("hook_event_name") != "Stop":
        debug_log("Not a Stop event, exiting")
        sys.exit(1)

    # Check if stop_hook_active to prevent infinite loops
    if input_data.get("stop_hook_active", False):
        debug_log("stop_hook_active is True, skipping to prevent loop")
        sys.exit(0)

    # Time-based filtering: Only show message if >3 seconds since last invocation
    # This prevents rapid-fire messages during tool usage
    TIMESTAMP_FILE = os.path.expanduser('~/.claude/debug/stop_hook_last_run')
    MIN_INTERVAL_SECONDS = 3

    current_time = datetime.now().timestamp()
    should_show = True

    try:
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as f:
                last_time = float(f.read().strip())
                time_diff = current_time - last_time
                debug_log(f"Time since last SHOWN message: {time_diff:.2f} seconds")

                if time_diff < MIN_INTERVAL_SECONDS:
                    debug_log(f"Skipping message (too soon: {time_diff:.2f}s < {MIN_INTERVAL_SECONDS}s)")
                    should_show = False
    except Exception as e:
        debug_log(f"Error checking timestamp: {e}")

    # Skip message if too soon (don't update timestamp!)
    if not should_show:
        debug_log("Exiting without showing message or updating timestamp")
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

    # Update timestamp file ONLY after successfully showing a message
    try:
        os.makedirs(os.path.dirname(TIMESTAMP_FILE), exist_ok=True)
        with open(TIMESTAMP_FILE, 'w') as f:
            f.write(str(current_time))
        debug_log(f"Message shown successfully, timestamp updated")
    except Exception as e:
        debug_log(f"Error updating timestamp: {e}")

except Exception as e:
    # Print a fallback message even on error
    fallback_output = {
        "systemMessage": "🌟 Well done! Your coding session is complete!"
    }
    print(json.dumps(fallback_output), flush=True)