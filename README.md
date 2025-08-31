# Mood Lifter Hooks 🌟

A collection of Claude Code Hooks designed to add encouraging and uplifting messages during your coding sessions. These hooks provide positive reinforcement at key moments without cluttering your conversation context.

## ✨ What are Mood Lifter Hooks?

Mood Lifter Hooks are specialized Claude Code Hooks that automatically display encouraging messages during three important events:

- **SessionStart** - Kick off your coding session with motivation
- **Stop** - Get encouragement when wrapping up your work
- **Notification** - Receive uplifting messages during your session

## 🎯 Key Features

- **Non-intrusive**: Messages are displayed to users without cluttering Claude's conversation context
- **Contextual**: Different encouraging messages for different session events
- **Customizable**: Easy to modify messages and add your own encouragement
- **Lightweight**: Minimal performance impact on your coding workflow

## 🚀 Getting Started

### Prerequisites

- Claude Code Hooks enabled in your environment
- Basic understanding of Claude Code Hooks configuration

### Installation

1. Clone or download this repository
2. Configure the hooks in your Claude Code Hooks setup
3. Customize the messages to match your preferences

## 📖 Usage

### SessionStart Hook

Triggers when you begin a new coding session. The hook script generates encouraging messages using ollama and returns them without adding to Claude's context:

```python
# Example output from SessionStart hook
{
  "suppressOutput": true,
  "systemMessage": "🚀 Ready to code something amazing! You've got this!"
}
```

### Stop Hook

Activates when Claude finishes responding. The hook displays an encouraging message that appears in transcript mode without affecting the conversation:

```python
# Hook simply outputs to stdout
print("🎉 Great work today! Your code is looking fantastic!")
```

### Notification Hook

Provides encouragement when Claude sends notifications. Messages are shown to the user but not added to Claude's context:

```python
# Hook outputs encouraging message
print("💪 Keep going! Every line of code brings you closer to your goal!")
```

## 🔧 Customization

### Adding Your Own Messages

You can easily customize the encouraging messages by editing the hook configurations. Consider:

- **Personal motivation**: What keeps you inspired?
- **Project-specific**: Tailor messages to your current work
- **Time-based**: Different encouragement for morning vs. evening sessions

### Message Examples

- "🌟 Your creativity is limitless!"
- "💡 Every bug you fix makes you a better developer"
- "🚀 Innovation happens one commit at a time"
- "🎯 Focus on progress, not perfection"
- "✨ You're building something amazing"

## 🎨 Hook Configuration

Each hook follows the standard Claude Code Hooks format:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python /path/to/mood-lifter/hooks/sessionstart.py"
          }
        ]
      }
    ]
  }
}
```

The hooks use JSON output with `suppressOutput: true` for SessionStart and standard output for Stop/Notification events to ensure messages are shown to users without cluttering Claude's conversation context.

## 🤝 Contributing

We welcome contributions to make Mood Lifter Hooks even better!

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Add your encouraging messages or improvements
4. Submit a pull request

### Ideas for Contributions

- New encouraging message categories
- Multi-language support
- Integration with productivity tools
- Custom message scheduling
- User preference management

## 📚 Resources

- [Claude Code Hooks Documentation](https://docs.anthropic.com/claude/docs/code-hooks)
- [Claude Code Hooks Guide](https://docs.anthropic.com/claude/docs/code-hooks-guide)
- [Community Examples](https://github.com/your-org/mood-lifter-hooks/discussions)

## 🎯 Why Mood Lifter Hooks?

Coding can be challenging, and sometimes we all need a little boost of encouragement. These hooks are designed to:

- **Boost motivation** during long coding sessions
- **Celebrate progress** and achievements
- **Maintain positive mindset** when debugging
- **Create a supportive environment** for learning and development

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Inspired by the Claude Code Hooks community
- Built with positivity and encouragement in mind
- Special thanks to all contributors and users

---

**Ready to lift your coding mood?** 🚀

Start using Mood Lifter Hooks today and transform your coding sessions into uplifting experiences!
