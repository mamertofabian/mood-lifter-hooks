# Mood Lifter Hooks 🌟

Encouraging hooks and commands for Claude Code that brighten your coding sessions with uplifting messages, developer jokes, and daily wisdom.

## ✨ Features

### 🎣 Hooks
- **SessionStart** - Motivational messages when starting Claude Code
- **Stop** - Encouragement when Claude finishes tasks
- **Notification** - Uplifting messages during notifications

### 🎯 Slash Commands
- `/joke` - Display random developer jokes
- `/jwtext` - Show today's JW daily text with developer encouragement

All messages are displayed without cluttering your conversation context!

## 🚀 Quick Install

### Install to Any Repository

```bash
# Clone this repository
git clone https://github.com/your-org/mood-lifter-hooks.git
cd mood-lifter-hooks

# Install globally (user-level)
./install.sh

# Install to specific project
./install.sh --project /path/to/your/project

# Install only commands (no hooks)
./install.sh --commands-only

# Install only hooks (no commands)
./install.sh --hooks-only
```

### Installation Options

| Option | Description |
|--------|------------|
| `--help` | Show help message |
| `--project DIR` | Install to specific project directory |
| `--hooks-only` | Install only hooks (no slash commands) |
| `--commands-only` | Install only slash commands (no hooks) |
| `--no-ollama` | Skip ollama availability check |

## 📦 What Gets Installed

### User-Level Installation (Default)
```
~/.claude/
├── settings.json          # Updated with hook configurations
├── commands/
│   ├── joke.md           # /joke command
│   └── jwtext.md         # /jwtext command
├── hooks/
│   ├── sessionstart.py   # SessionStart hook
│   ├── stop.py          # Stop hook
│   └── notification.py   # Notification hook
├── message_generator.py  # Core message generation
├── joke_command.py      # Joke generator script
└── jw_text_command.py   # JW daily text script
```

### Project-Level Installation
```
/your/project/.claude/
├── settings.json        # Project-specific hook configurations
├── commands/           # Project-specific commands
└── hooks/             # Project-specific hook scripts
```

## 🔄 Uninstall

```bash
# Remove user-level installation
./uninstall.sh

# Remove from specific project
./uninstall.sh --project /path/to/project

# Complete removal (including Python scripts)
./uninstall.sh --complete

# Remove only hooks
./uninstall.sh --hooks-only

# Remove only commands
./uninstall.sh --commands-only
```

## 💡 How It Works

### Context-Free Messages
- **SessionStart hooks** use `suppressOutput: true` to prevent context addition
- **Slash commands** use bash execution (`!`) which doesn't add to context
- **Stop/Notification hooks** output directly without context impact

### Dynamic Message Generation
- Uses **ollama** for AI-generated encouragement when available
- Falls back to curated messages if ollama is unavailable
- Supports multiple lightweight models (phi3.5, mistral, llama3.2)

## 🎮 Using the Commands

### Developer Jokes
```
/joke
```
Displays a random programming joke using ollama or fallback jokes.

### JW Daily Text
```
/jwtext
```
Shows today's scripture with developer-focused encouragement.

## 🔧 Advanced Installation

### Install from GitHub directly
```bash
# One-liner installation
curl -sSL https://raw.githubusercontent.com/your-org/mood-lifter-hooks/main/install.sh | bash
```

### Custom Installation Path
```bash
# Clone to custom location
git clone https://github.com/your-org/mood-lifter-hooks.git ~/my-tools/mood-lifter

# Install from custom location
cd ~/my-tools/mood-lifter
./install.sh
```

### Multiple Project Setup
```bash
# Install to multiple projects
for project in ~/projects/*; do
    ./install.sh --project "$project"
done
```

## 🎨 Customization

### Modify Messages
Edit `lib/message_generator.py` to customize:
- Start messages
- Stop messages
- Notification messages
- Fallback messages

### Add New Commands
Create new commands in `~/.claude/commands/`:
```markdown
---
description: Your custom command
allowed-tools: Bash(python3:*)
---

!`python3 ~/.claude/your_script.py`
```

### Configure Ollama Models
Edit scripts to prefer different models:
```python
preferred_models = ['gemma2:2b', 'phi3.5:3.8b', 'your-model:tag']
```

## 🚦 Prerequisites

### Required
- Python 3.6+
- Claude Code with hooks support

### Optional but Recommended
- [ollama](https://ollama.ai) - For dynamic message generation
  ```bash
  # Install ollama
  curl -sSL https://ollama.ai/install.sh | bash
  
  # Pull lightweight model
  ollama pull phi3.5:3.8b
  ```

## 🐛 Troubleshooting

### Hooks Not Working?
1. Restart Claude Code after installation
2. Check settings.json was updated correctly
3. Verify Python scripts are executable
4. Run with `--debug` flag to see hook execution

### Commands Not Found?
1. Check `~/.claude/commands/` directory exists
2. Verify command files have `.md` extension
3. Restart Claude Code
4. Try `/help` to see available commands

### Ollama Issues?
1. Ensure ollama is running: `ollama serve`
2. Check model is downloaded: `ollama list`
3. Scripts will use fallback messages if ollama fails

## 📝 Manual Configuration

If automatic installation fails, add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/sessionstart.py"
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/stop.py"
      }]
    }],
    "Notification": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/notification.py"
      }]
    }]
  }
}
```

## 🤝 Contributing

We welcome contributions! Ideas:
- New message categories
- Multi-language support
- Additional API integrations
- Custom scheduling
- More ollama models
- Theme-based messages

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Claude Code Hooks community
- Ollama for AI message generation
- All contributors and users

---

**Ready to brighten your coding sessions?** 🚀

Install Mood Lifter Hooks today and code with encouragement!