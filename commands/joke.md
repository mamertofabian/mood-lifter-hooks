---
description: Generate a random developer joke
allowed-tools: Bash(python3:*)
---

## Generate Random Developer Joke

!`python3 $CLAUDE_PROJECT_DIR/lib/joke_command.py 2>/dev/null || python3 ~/.claude/joke_command.py 2>/dev/null || echo "Script not found. Please run the mood-lifter-hooks installer."`

---

*Displays a random programming joke to brighten your coding session! Uses ollama for creative jokes when available, with quality fallbacks.*