---
description: Display today's JW daily text with developer encouragement
allowed-tools: Bash(python3:*)
---

## JW Daily Text with Developer Encouragement

!`python3 $CLAUDE_PROJECT_DIR/lib/jw_text_command.py 2>/dev/null || python3 ~/.claude/jw_text_command.py 2>/dev/null || echo "Script not found. Please run the mood-lifter-hooks installer."`

---

*Fetches today's daily text from JW.org and provides developer-focused encouragement based on the scripture. If online fetch fails, it uses inspiring fallback texts.*