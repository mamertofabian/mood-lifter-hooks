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

## Project Structure

```
mood-lifter-hooks/
├── hooks/             # Hook scripts for Claude Code events
├── lib/              # Core message generation module
├── .claude/          # Local Claude Code settings (gitignored)
├── pyproject.toml    # uv/pip package configuration
└── install.sh        # Installation helper script
```

## Development Setup

- Use `uv` for package management (faster than pip)
- Run tests with `pytest`
- Format code with `black` and `ruff`
- No external dependencies required for basic functionality

## Future Features (TODO)

The following features have been planned but not yet implemented:

### 1. Multiple Ollama Model Support
- **Goal**: Randomly use different ollama models (mistral, phi3.5, etc.) for variety
- **Implementation Notes**:
  - Add model rotation logic in `message_generator.py`
  - Keep efficiency in mind - use lightweight models
  - Consider caching model list to avoid repeated `ollama list` calls
  - Suggested models: llama3.2:latest, mistral:7b-instruct

### 2. External API Integration
- **Goal**: Fetch content from external sources and enhance with ollama
- **Implementation Notes**:
  - Add `requests` dependency for API calls
  - Create new module for API integrations
  - Sources to integrate:
    - Dad jokes API
    - Developer quotes/jokes APIs
    - Programming wisdom APIs
  - Process: Fetch → Summarize/enhance with ollama → Display

### 3. JW Daily Text Integration
- **Primary Resource**: https://wol.jw.org/wol/dt/r1/lp-e/YYYY/MM/DD
  - Replace YYYY/MM/DD with current date (e.g., 2025/8/31)
  - Parse daily text and scripture
  - Use ollama to create developer-focused encouragement based on the text
- **Implementation Notes**:
  - Add `beautifulsoup4` for HTML parsing
  - Cache daily texts to avoid repeated fetches
  - For afternoon/evening hooks, optionally use random past dates
  - Ensure wholesome, uplifting integration

### 4. Configuration System
- **Goal**: Allow users to configure preferences
- **Features to add**:
  - Enable/disable ollama
  - Select preferred models
  - Choose message sources (pure encouragement, jokes, daily text)
  - Set message frequency/probability
  - Time-based preferences

### 5. Testing Suite
- **Goal**: Comprehensive test coverage
- **Tests needed**:
  - Unit tests for message_generator.py
  - Integration tests for hook scripts
  - Mock ollama responses for consistent testing
  - Test fallback behavior when ollama unavailable