#!/bin/bash

# Mood Lifter Hooks Installation Script
# Installs encouraging hooks and commands for Claude Code

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_CLAUDE_DIR="$HOME/.claude"
USER_COMMANDS_DIR="$USER_CLAUDE_DIR/commands"
USER_SETTINGS_FILE="$USER_CLAUDE_DIR/settings.json"

# Default options
INSTALL_HOOKS=true
INSTALL_COMMANDS=true
INSTALL_LOCATION="user"  # user or project
PROJECT_DIR=""

# Display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -p, --project DIR    Install to specific project directory (default: user-level)"
    echo "  --hooks-only         Install only hooks (no slash commands)"
    echo "  --commands-only      Install only slash commands (no hooks)"
    echo "  --no-ollama          Skip ollama availability check"
    echo ""
    echo "Examples:"
    echo "  $0                           # Install everything at user level"
    echo "  $0 --project /path/to/proj   # Install to specific project"
    echo "  $0 --commands-only           # Install only slash commands"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -p|--project)
            INSTALL_LOCATION="project"
            PROJECT_DIR="$2"
            shift 2
            ;;
        --hooks-only)
            INSTALL_COMMANDS=false
            shift
            ;;
        --commands-only)
            INSTALL_HOOKS=false
            shift
            ;;
        --no-ollama)
            SKIP_OLLAMA=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Header
echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}   Mood Lifter Hooks Installation${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Determine installation directory
if [ "$INSTALL_LOCATION" = "project" ]; then
    if [ -z "$PROJECT_DIR" ]; then
        PROJECT_DIR="$(pwd)"
    fi
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}Error: Project directory does not exist: $PROJECT_DIR${NC}"
        exit 1
    fi
    CLAUDE_DIR="$PROJECT_DIR/.claude"
    COMMANDS_DIR="$CLAUDE_DIR/commands"
    SETTINGS_FILE="$CLAUDE_DIR/settings.json"
    echo -e "${GREEN}Installing to project: $PROJECT_DIR${NC}"
else
    CLAUDE_DIR="$USER_CLAUDE_DIR"
    COMMANDS_DIR="$USER_COMMANDS_DIR"
    SETTINGS_FILE="$USER_SETTINGS_FILE"
    echo -e "${GREEN}Installing to user directory: $HOME/.claude${NC}"
fi

# Create directories if they don't exist
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p "$CLAUDE_DIR"
mkdir -p "$COMMANDS_DIR"

# Check for ollama (optional)
if [ "$SKIP_OLLAMA" != true ]; then
    echo -e "${YELLOW}Checking for ollama...${NC}"
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✓ ollama is installed${NC}"
        ollama list &> /dev/null && echo -e "${GREEN}✓ ollama is running${NC}" || echo -e "${YELLOW}⚠ ollama is installed but not running${NC}"
    else
        echo -e "${YELLOW}⚠ ollama not found - hooks will use fallback messages${NC}"
    fi
fi

# Install Python scripts to user directory (always, for global access)
if [ "$INSTALL_COMMANDS" = true ] || [ "$INSTALL_HOOKS" = true ]; then
    echo -e "${YELLOW}Installing Python scripts...${NC}"
    
    # Copy core library files and lib folder for API features
    cp "$SCRIPT_DIR/lib/message_generator.py" "$USER_CLAUDE_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/lib/joke_command.py" "$USER_CLAUDE_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/lib/jw_text_command.py" "$USER_CLAUDE_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/lib/stoic_quotes.py" "$USER_CLAUDE_DIR/" 2>/dev/null || true
    
    # Copy entire lib folder to ensure all modules are available
    echo -e "${YELLOW}Installing lib modules for API features...${NC}"
    cp -r "$SCRIPT_DIR/lib" "$USER_CLAUDE_DIR/" 2>/dev/null && \
        echo -e "${GREEN}✓ Lib modules installed (enables JW text, jokes, quotes)${NC}" || \
        echo -e "${YELLOW}⚠ Could not install lib modules${NC}"

    # Copy config folder for defaults
    echo -e "${YELLOW}Installing configuration files...${NC}"
    cp -r "$SCRIPT_DIR/config" "$USER_CLAUDE_DIR/" 2>/dev/null && \
        echo -e "${GREEN}✓ Configuration files installed${NC}" || \
        echo -e "${YELLOW}⚠ Could not install config files${NC}"
    
    # Make scripts executable
    chmod +x "$USER_CLAUDE_DIR"/*.py 2>/dev/null || true
    
    echo -e "${GREEN}✓ Python scripts installed${NC}"
fi

# Install slash commands
if [ "$INSTALL_COMMANDS" = true ]; then
    echo -e "${YELLOW}Installing slash commands...${NC}"
    
    # Copy command files from repository
    if [ -d "$SCRIPT_DIR/commands" ]; then
        cp "$SCRIPT_DIR/commands/joke.md" "$COMMANDS_DIR/" 2>/dev/null && \
            echo -e "${GREEN}✓ Installed /joke command${NC}" || \
            echo -e "${RED}✗ Failed to install /joke command${NC}"
        
        cp "$SCRIPT_DIR/commands/jwtext.md" "$COMMANDS_DIR/" 2>/dev/null && \
            echo -e "${GREEN}✓ Installed /jwtext command${NC}" || \
            echo -e "${RED}✗ Failed to install /jwtext command${NC}"
    else
        echo -e "${RED}✗ Commands directory not found in repository${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Slash commands installed (/joke, /jwtext)${NC}"
fi

# Install hooks
if [ "$INSTALL_HOOKS" = true ]; then
    echo -e "${YELLOW}Installing hooks configuration...${NC}"
    
    # Create hook scripts directory
    HOOKS_DIR="$CLAUDE_DIR/hooks"
    mkdir -p "$HOOKS_DIR"
    
    # Copy hook scripts from repository
    echo -e "${YELLOW}Copying hook scripts from repository...${NC}"
    if [ -d "$SCRIPT_DIR/hooks" ]; then
        cp "$SCRIPT_DIR/hooks/sessionstart.py" "$HOOKS_DIR/" 2>/dev/null && \
            echo -e "${GREEN}✓ Copied sessionstart.py${NC}" || \
            echo -e "${RED}✗ Failed to copy sessionstart.py${NC}"
        
        cp "$SCRIPT_DIR/hooks/stop.py" "$HOOKS_DIR/" 2>/dev/null && \
            echo -e "${GREEN}✓ Copied stop.py${NC}" || \
            echo -e "${RED}✗ Failed to copy stop.py${NC}"
        
        cp "$SCRIPT_DIR/hooks/notification.py" "$HOOKS_DIR/" 2>/dev/null && \
            echo -e "${GREEN}✓ Copied notification.py${NC}" || \
            echo -e "${RED}✗ Failed to copy notification.py${NC}"
        
        # Make hook scripts executable
        chmod +x "$HOOKS_DIR"/*.py
        echo -e "${GREEN}✓ Hook scripts installed from repository${NC}"
    else
        echo -e "${RED}✗ Hooks directory not found in repository${NC}"
        exit 1
    fi
    
    # Update settings.json
    if [ -f "$SETTINGS_FILE" ]; then
        echo -e "${YELLOW}Backing up existing settings.json...${NC}"
        cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create or update settings.json with Python for proper JSON handling
    python3 << EOF
import json
import os

settings_file = "$SETTINGS_FILE"
hooks_dir = "$HOOKS_DIR"

# Load existing settings or create new
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        settings = json.load(f)
else:
    settings = {}

# Ensure hooks section exists
if 'hooks' not in settings:
    settings['hooks'] = {}

# Add our hooks (preserve existing ones)
mood_lifter_hooks = {
    "SessionStart": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {hooks_dir}/sessionstart.py"
                }
            ]
        }
    ],
    "Stop": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {hooks_dir}/stop.py"
                }
            ]
        }
    ],
    "Notification": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {hooks_dir}/notification.py"
                }
            ]
        }
    ]
}

# Merge hooks (add if not exists, skip if exists)
for event, hooks in mood_lifter_hooks.items():
    if event not in settings['hooks']:
        settings['hooks'][event] = hooks
    else:
        # Check if our hook already exists
        our_command = hooks[0]['hooks'][0]['command']
        exists = False
        for existing_hook in settings['hooks'][event]:
            if 'hooks' in existing_hook:
                for h in existing_hook['hooks']:
                    if h.get('command') == our_command:
                        exists = True
                        break
        if not exists:
            settings['hooks'][event].extend(hooks)

# Save settings
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print("✓ Hooks configuration updated")
EOF
    
    echo -e "${GREEN}✓ Hooks installed (SessionStart, Stop, Notification)${NC}"
fi

# Copy message_generator.py if hooks were installed
if [ "$INSTALL_HOOKS" = true ]; then
    if [ ! -f "$USER_CLAUDE_DIR/message_generator.py" ]; then
        echo -e "${YELLOW}Installing message generator...${NC}"
        cp "$SCRIPT_DIR/lib/message_generator.py" "$USER_CLAUDE_DIR/"
        cp "$SCRIPT_DIR/lib/joke_command.py" "$USER_CLAUDE_DIR/"
        cp "$SCRIPT_DIR/lib/jw_text_command.py" "$USER_CLAUDE_DIR/"
        cp "$SCRIPT_DIR/lib/stoic_quotes.py" "$USER_CLAUDE_DIR/"
        echo -e "${GREEN}✓ Message generator installed${NC}"
    fi
fi

# Success message
echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}   Installation Complete! 🎉${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""

if [ "$INSTALL_COMMANDS" = true ]; then
    echo -e "${BLUE}Slash commands available:${NC}"
    echo "  • /joke    - Display a random developer joke"
    echo "  • /jwtext  - Show today's JW daily text with encouragement"
    echo ""
fi

if [ "$INSTALL_HOOKS" = true ]; then
    echo -e "${BLUE}Hooks installed:${NC}"
    echo "  • SessionStart - Encouraging message when starting Claude Code"
    echo "  • Stop - Uplifting message when Claude finishes a task"
    echo "  • Notification - Motivational message during notifications"
    echo ""
fi

echo -e "${YELLOW}Note: Restart Claude Code for hooks to take effect${NC}"
echo ""
echo -e "${GREEN}Enjoy your mood-lifted coding sessions! 😊${NC}"