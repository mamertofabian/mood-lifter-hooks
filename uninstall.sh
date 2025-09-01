#!/bin/bash

# Mood Lifter Hooks Uninstaller
# Removes mood-lifter hooks and commands from Claude Code

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
REMOVE_HOOKS=true
REMOVE_COMMANDS=true
REMOVE_SCRIPTS=false
REMOVE_LOCATION="user"  # user or project
PROJECT_DIR=""

# Display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -p, --project DIR    Uninstall from specific project directory (default: user-level)"
    echo "  --hooks-only         Remove only hooks (keep slash commands)"
    echo "  --commands-only      Remove only slash commands (keep hooks)"
    echo "  --complete           Remove everything including Python scripts"
    echo ""
    echo "Examples:"
    echo "  $0                           # Remove user-level installation"
    echo "  $0 --project /path/to/proj   # Remove from specific project"
    echo "  $0 --complete                # Complete removal including scripts"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -p|--project)
            REMOVE_LOCATION="project"
            PROJECT_DIR="$2"
            shift 2
            ;;
        --hooks-only)
            REMOVE_COMMANDS=false
            shift
            ;;
        --commands-only)
            REMOVE_HOOKS=false
            shift
            ;;
        --complete)
            REMOVE_SCRIPTS=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Header
echo -e "${RED}=======================================${NC}"
echo -e "${RED}   Mood Lifter Hooks Uninstaller${NC}"
echo -e "${RED}=======================================${NC}"
echo ""

# Determine target directory
if [ "$REMOVE_LOCATION" = "project" ]; then
    if [ -z "$PROJECT_DIR" ]; then
        PROJECT_DIR="$(pwd)"
    fi
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}Error: Project directory does not exist: $PROJECT_DIR${NC}"
        exit 1
    fi
    CLAUDE_DIR="$PROJECT_DIR/.claude"
    echo -e "${YELLOW}Removing from project: $PROJECT_DIR${NC}"
else
    CLAUDE_DIR="$HOME/.claude"
    echo -e "${YELLOW}Removing from user directory: $HOME/.claude${NC}"
fi

COMMANDS_DIR="$CLAUDE_DIR/commands"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
HOOKS_DIR="$CLAUDE_DIR/hooks"

# Remove slash commands
if [ "$REMOVE_COMMANDS" = true ]; then
    echo -e "${YELLOW}Removing slash commands...${NC}"
    
    if [ -f "$COMMANDS_DIR/joke.md" ]; then
        rm "$COMMANDS_DIR/joke.md"
        echo -e "${GREEN}✓ Removed /joke command${NC}"
    fi
    
    if [ -f "$COMMANDS_DIR/jwtext.md" ]; then
        rm "$COMMANDS_DIR/jwtext.md"
        echo -e "${GREEN}✓ Removed /jwtext command${NC}"
    fi
fi

# Remove hooks from settings.json
if [ "$REMOVE_HOOKS" = true ] && [ -f "$SETTINGS_FILE" ]; then
    echo -e "${YELLOW}Removing hooks from settings.json...${NC}"
    
    # Back up settings before modification
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${BLUE}Created backup: $SETTINGS_FILE.backup.*${NC}"
    
    # Remove hooks using Python for proper JSON handling
    python3 << EOF
import json
import os

settings_file = "$SETTINGS_FILE"
hooks_dir = "$HOOKS_DIR"

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    
    if 'hooks' not in settings:
        print("No hooks section found")
        exit(0)
    
    # Patterns to identify our hooks
    mood_lifter_patterns = [
        "sessionstart.py",
        "stop.py",
        "notification.py",
        f"{hooks_dir}/sessionstart.py",
        f"{hooks_dir}/stop.py",
        f"{hooks_dir}/notification.py"
    ]
    
    # Remove our hooks from each event type
    for event in ['SessionStart', 'Stop', 'Notification']:
        if event in settings['hooks']:
            original_count = len(settings['hooks'][event])
            settings['hooks'][event] = [
                hook_group for hook_group in settings['hooks'][event]
                if not any(
                    pattern in hook.get('command', '')
                    for hook in hook_group.get('hooks', [])
                    for pattern in mood_lifter_patterns
                )
            ]
            
            # Clean up empty event arrays
            if not settings['hooks'][event]:
                del settings['hooks'][event]
            
            removed = original_count - len(settings['hooks'].get(event, []))
            if removed > 0:
                print(f"✓ Removed {removed} {event} hook(s)")
    
    # Clean up empty hooks section
    if not settings['hooks']:
        del settings['hooks']
    
    # Save modified settings
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("✓ Settings updated")
    
except Exception as e:
    print(f"Warning: Could not update settings.json: {e}")
EOF
fi

# Remove hook scripts
if [ "$REMOVE_HOOKS" = true ] && [ -d "$HOOKS_DIR" ]; then
    echo -e "${YELLOW}Removing hook scripts...${NC}"
    
    for script in sessionstart.py stop.py notification.py; do
        if [ -f "$HOOKS_DIR/$script" ]; then
            rm "$HOOKS_DIR/$script"
            echo -e "${GREEN}✓ Removed $script${NC}"
        fi
    done
    
    # Remove hooks directory if empty
    if [ -z "$(ls -A "$HOOKS_DIR" 2>/dev/null)" ]; then
        rmdir "$HOOKS_DIR"
        echo -e "${GREEN}✓ Removed empty hooks directory${NC}"
    fi
fi

# Remove Python scripts and lib modules (optional)
if [ "$REMOVE_SCRIPTS" = true ]; then
    echo -e "${YELLOW}Removing Python scripts and lib modules...${NC}"
    
    # Remove main scripts from ~/.claude
    SCRIPTS=("message_generator.py" "joke_command.py" "jw_text_command.py")
    
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$HOME/.claude/$script" ]; then
            rm "$HOME/.claude/$script"
            echo -e "${GREEN}✓ Removed $script${NC}"
        fi
    done
    
    # Remove only our specific lib files (not the entire folder!)
    if [ -d "$HOME/.claude/lib" ]; then
        echo -e "${YELLOW}Removing mood-lifter lib modules...${NC}"
        
        # List of our lib files to remove
        LIB_FILES=(
            "api_integrations.py"
            "config.py"
            "constants.py"
            "external_apis.py"
            "joke_command.py"
            "jw_daily_text.py"
            "jw_text_command.py"
            "message_generator.py"
            "ollama_models.py"
            "rate_limiter.py"
        )
        
        for lib_file in "${LIB_FILES[@]}"; do
            if [ -f "$HOME/.claude/lib/$lib_file" ]; then
                rm "$HOME/.claude/lib/$lib_file"
                echo -e "${GREEN}  ✓ Removed lib/$lib_file${NC}"
            fi
        done
        
        # Also remove __pycache__ if it exists
        if [ -d "$HOME/.claude/lib/__pycache__" ]; then
            rm -rf "$HOME/.claude/lib/__pycache__"
            echo -e "${GREEN}  ✓ Removed lib/__pycache__${NC}"
        fi
        
        # Only remove the lib folder if it's now empty
        if [ -z "$(ls -A "$HOME/.claude/lib" 2>/dev/null)" ]; then
            rmdir "$HOME/.claude/lib"
            echo -e "${GREEN}✓ Removed empty lib folder${NC}"
        else
            echo -e "${YELLOW}⚠ lib folder not removed (contains other files)${NC}"
        fi
    fi
    
    # Remove our cache directories if they exist
    if [ -d "$HOME/.claude-code/mood-lifter" ]; then
        rm -rf "$HOME/.claude-code/mood-lifter"
        echo -e "${GREEN}✓ Removed mood-lifter cache directory${NC}"
    fi
fi

# Success message
echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}   Uninstallation Complete${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""

if [ "$REMOVE_COMMANDS" = true ]; then
    echo -e "${BLUE}Removed:${NC}"
    echo "  • /joke command"
    echo "  • /jwtext command"
fi

if [ "$REMOVE_HOOKS" = true ]; then
    echo -e "${BLUE}Removed:${NC}"
    echo "  • SessionStart hooks"
    echo "  • Stop hooks"
    echo "  • Notification hooks"
fi

if [ "$REMOVE_SCRIPTS" = true ]; then
    echo -e "${BLUE}Removed:${NC}"
    echo "  • Python support scripts"
    echo "  • Lib modules (JW text, jokes, quotes APIs)"
    echo "  • Cache directories"
fi

echo ""
echo -e "${YELLOW}Note: Restart Claude Code for changes to take effect${NC}"
echo -e "${BLUE}Backups of settings.json were created if modified${NC}"
echo ""
echo -e "${GREEN}Thank you for using Mood Lifter Hooks! 👋${NC}"