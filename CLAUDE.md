# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mood Lifter Hooks is a collection of Claude Code Hooks designed to display encouraging messages during coding sessions. The hooks are non-intrusive by using proper output control (suppressOutput for SessionStart, standard output for Stop/Notification) and trigger on three key events: SessionStart, Stop, and Notification.

## Hook Structure

Claude Code Hooks configuration in settings.json:
```json
{
  "hooks": {
    "EventName": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python /path/to/hook/script.py"
          }
        ]
      }
    ]
  }
}
```

## Key Implementation Notes

- SessionStart hooks: Use JSON output with `"suppressOutput": true` to prevent context addition
- Stop/Notification hooks: Use standard output (naturally not added to Claude's context)
- Messages generated dynamically using ollama for variety and context-awareness
- Three main hook types: SessionStart, Stop, and Notification
- Messages should be encouraging, positive, and non-distracting
- Includes fallback messages if ollama is unavailable

## Development Guidelines

When implementing hook files:
- Create separate files for each hook type (e.g., `sessionstart.hook.json`, `stop.hook.json`)
- Include a variety of messages that can be randomly selected
- Keep messages concise and uplifting
- Use appropriate emojis to enhance visual appeal without overdoing it

## Testing Hooks

To test hooks in Claude Code:
1. Configure the hook files in your Claude Code Hooks setup
2. Trigger the relevant events (start session, stop session, etc.)
3. Verify messages display correctly without affecting conversation context