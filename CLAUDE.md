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
- Messages generated dynamically using LM Studio (via `lms` CLI) for variety and context-awareness
- Three main hook types: SessionStart, Stop, and Notification
- Messages should be encouraging, positive, and non-distracting
- Includes fallback messages if LM Studio is unavailable

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

## Implemented Features

### 1. ✅ Multiple LLM Model Support
- Model rotation logic implemented in `lm_studio.py`
- Uses lightweight models for efficiency
- Caches model list to avoid repeated `lms ls` calls
- Supported models: llama-3.2-1b-instruct, llama-3.2-3b-instruct, qwen2.5-7b-instruct, etc.

### 2. ✅ External API Integration
- `requests` dependency added
- API integrations module created
- Integrated sources:
  - Dad jokes API
  - Developer quotes/jokes APIs
  - Programming wisdom APIs
- Process: Fetch → Optionally enhance with LM Studio → Display

### 3. ✅ JW Daily Text Integration
- Primary Resource: https://wol.jw.org/wol/dt/r1/lp-e/YYYY/MM/DD
- Parses daily text and scripture
- Uses LM Studio to create developer-focused encouragement
- `beautifulsoup4` for HTML parsing
- Caches daily texts to avoid repeated fetches
- Supports random past dates for variety

### 4. ✅ Configuration System
- User configuration system implemented
- Features:
  - Enable/disable LM Studio
  - Select preferred models
  - Choose message sources (pure encouragement, jokes, daily text, stoic quotes)
  - Set message frequency/probability
  - Time-based preferences

### 5. Testing Suite
- **Status**: Partially implemented
- **Tests needed**:
  - Add integration tests for LM Studio API
  - Test fallback behavior when LM Studio unavailable