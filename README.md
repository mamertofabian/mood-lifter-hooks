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

### 🧘 Message Sources
- **Default** - General encouraging messages
- **JW Daily Text** - Scripture-based encouragement
- **Developer Jokes** - Programming humor
- **Stoic Quotes** - Ancient wisdom for calm coding (NEW!)
- **Inspirational Quotes** - General motivational quotes

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
| `--no-lms` | Skip LM Studio availability check |

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
- Uses **LM Studio** for AI-generated encouragement when available
- Falls back to curated messages if LM Studio is unavailable
- Supports multiple lightweight models (phi3.5, mistral, llama3.2)

## 🎮 Using the Commands

### Developer Jokes
```
/joke
```
Displays a random programming joke using LM Studio or fallback jokes.

### JW Daily Text
```
/jwtext
```
Shows today's scripture with developer-focused encouragement.

### Stoic Wisdom (NEW!)
The system now includes **stoic quotes** for calm, focused coding:
- **Ancient wisdom** from Marcus Aurelius, Epictetus, and Seneca
- **Developer-specific** stoic principles for coding challenges
- **Pure LLM generation** creating original stoic wisdom (40% pure, 60% quote-based)
- **Theme filtering** for anger management, self-control, peace, and obstacles
- **Weighted distribution**: Stoic 32%, Default 30%, JW 20%, Jokes 15%, Quotes 3%

Perfect for maintaining composure during debugging sessions! 🧘

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

### Configure LM Studio Models
Edit `config/defaults.json` to prefer different models:
```json
{
  "mood_lifter_hooks": {
    "ollama": {
      "preferred_models": [
        "llama-3.2-1b-instruct",
        "qwen2.5-7b-instruct",
        "your-model-name"
      ]
    }
  }
}
```

## 🚦 Prerequisites

### Required
- Python 3.6+
- Claude Code with hooks support

### Optional but Recommended
- [LM Studio](https://lmstudio.ai) - For dynamic message generation
  ```bash
  # 1. Download and install LM Studio from https://lmstudio.ai

  # 2. Load a lightweight model in LM Studio GUI
  #    Recommended: llama-3.2-1b-instruct or llama-3.2-3b-instruct

  # 3. Start the server (should run on http://localhost:1234 by default)
  #    This is usually automatic when you load a model

  # The hooks will use LM Studio's OpenAI-compatible API automatically
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

### LM Studio Issues?
1. Ensure LM Studio server is running (check the app)
2. Verify server is accessible: `curl http://localhost:1234/v1/models`
3. Check that a model is loaded in LM Studio GUI
4. Verify port 1234 is not blocked by firewall
5. Scripts will automatically use fallback messages if LM Studio is unavailable

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
- Support for more LLM backends
- Theme-based messages

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Claude Code Hooks community
- LM Studio for AI message generation
- All contributors and users

---

**Ready to brighten your coding sessions?** 🚀

Install Mood Lifter Hooks today and code with encouragement!