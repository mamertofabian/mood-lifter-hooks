#!/bin/bash

# Mood Lifter Hooks Installation Script
# This script helps set up the hooks in your Claude Code configuration

set -e

echo "🚀 Mood Lifter Hooks Installation"
echo "=================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama detected - will use for dynamic message generation"
    echo "   Available models:"
    ollama list 2>/dev/null | grep -E "^(phi3.5|mistral|llama)" | head -5 || echo "   No suitable models found"
else
    echo "ℹ️  Ollama not found - will use fallback messages"
    echo "   To enable dynamic messages, install ollama: https://ollama.ai"
fi
echo ""

# Make scripts executable
echo "Setting up hook scripts..."
chmod +x "$SCRIPT_DIR"/hooks/*.py
chmod +x "$SCRIPT_DIR"/lib/*.py
echo "✅ Scripts are now executable"
echo ""

# Show configuration instructions
echo "📝 Configuration Instructions:"
echo "------------------------------"
echo ""
echo "Add the following to your Claude Code settings file:"
echo "(~/.claude/settings.json or .claude/settings.json in your project)"
echo ""
cat << EOF
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $SCRIPT_DIR/hooks/sessionstart.py",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $SCRIPT_DIR/hooks/stop.py",
            "timeout": 10
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $SCRIPT_DIR/hooks/notification.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
EOF

echo ""
echo "💡 Tips:"
echo "  - Project settings (.claude/settings.json) override user settings"
echo "  - Use .claude/settings.local.json for local-only configuration"
echo "  - Restart Claude Code after changing settings"
echo "  - Messages won't clutter your conversation context"
echo ""
echo "🎉 Installation complete!"
echo "   Your next coding session will be more uplifting! 🌟"