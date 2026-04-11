#!/bin/bash
# Dokploy Skills - Universal Installer
# Detects environment and installs with appropriate method
# Usage: curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# ASCII Art Banner
echo -e "${CYAN}"
echo "██████╗  ██████╗ ██╗  ██╗██████╗ ██╗      ██████╗ ██╗   ██╗"
echo "██╔══██╗██╔═══██╗██║ ██╔╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝"
echo "██║  ██║██║   ██║█████╔╝ ██████╔╝██║     ██║   ██║ ╚████╔╝"
echo "██║  ██║██║   ██║██╔═██╗ ██╔═══╝ ██║     ██║   ██║  ╚██╔╝"
echo "██████╔╝╚██████╔╝██║  ██╗██║     ███████╗╚██████╔╝   ██║"
echo "╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝"
echo -e "${NC}"
echo -e "${GREEN}Advanced Toolkit for Dokploy Deployments${NC}"
echo ""

# Detect AI Environment
detect_ai_environment() {
    if [ -n "$CLAUDE_CODE" ] || [ -n "$ANTHROPIC_API_KEY" ] || [ -d ".claude" ]; then
        echo "claude"
    elif [ -n "$KIMI_CLI" ] || [ -d ".kimi" ] || [ -f ".kimi/config" ]; then
        echo "kimi"
    elif [ -n "$CODEX_CLI" ] || [ -d ".codex" ]; then
        echo "codex"
    elif [ -n "$CURSOR" ] || [ -d ".cursor" ]; then
        echo "cursor"
    elif [ -n "$WINDSURF" ] || [ -d ".windsurf" ]; then
        echo "windsurf"
    elif [ -n "$QODER" ] || [ -d ".qoder" ]; then
        echo "qoder"
    elif [ -n "$COPILOT" ] || [ -d ".github/copilot" ]; then
        echo "copilot"
    else
        echo "unknown"
    fi
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        elif [ -f /etc/arch-release ]; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Get install command for AI environment
get_install_command() {
    local ai_env=$1
    local repo="Xhuk/dokploy-skills"
    
    case $ai_env in
        claude)
            echo "/plugin marketplace add ${repo}"
            ;;
        kimi)
            echo "/skill install ${repo}"
            ;;
        codex|cursor|windsurf|qoder)
            echo "git clone https://github.com/${repo}.git && cd dokploy-skills && pip install -e ."
            ;;
        copilot)
            echo "Use Copilot Workspace to import ${repo}"
            ;;
        *)
            echo "pip install git+https://github.com/${repo}.git"
            ;;
    esac
}

# Main installation
main() {
    AI_ENV=$(detect_ai_environment)
    OS=$(detect_os)
    
    echo -e "${YELLOW}Environment Detection:${NC}"
    echo -e "  OS: ${CYAN}${OS}${NC}"
    echo -e "  AI Environment: ${CYAN}${AI_ENV}${NC}"
    echo ""
    
    # Check Python
    echo -e "${YELLOW}Checking Python...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        echo -e "${RED}ERROR: Python not found. Please install Python 3.8+${NC}"
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    echo -e "${GREEN}  Found: $PYTHON_VERSION${NC}"
    
    # Check pip
    echo ""
    echo -e "${YELLOW}Checking pip...${NC}"
    if command -v pip3 &> /dev/null; then
        PIP=pip3
    elif command -v pip &> /dev/null; then
        PIP=pip
    else
        echo -e "${RED}ERROR: pip not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}  Found: pip${NC}"
    
    # Installation directory
    INSTALL_DIR="$HOME/.dokploy-skills"
    
    # Clone or update
    echo ""
    echo -e "${YELLOW}Installing Dokploy Skills...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "  Directory exists, updating...${NC}"
        cd "$INSTALL_DIR"
        git pull --quiet 2>/dev/null || true
    else
        echo -e "  Cloning repository...${NC}"
        git clone https://github.com/Xhuk/dokploy-skills.git "$INSTALL_DIR" --quiet
        cd "$INSTALL_DIR"
    fi
    
    # Install package
    echo ""
    echo -e "${YELLOW}Installing package...${NC}"
    $PIP install -e . --quiet --user
    
    # Add to PATH
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    fi
    
    if [ -n "$SHELL_RC" ] && ! grep -q "\.local/bin" "$SHELL_RC" 2>/dev/null; then
        echo -e "${YELLOW}Adding to PATH in ${SHELL_RC}...${NC}"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo -e "${YELLOW}Note: Run 'source $SHELL_RC' after installation${NC}"
    fi
    
    # Installation complete
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Show AI-specific integration
    if [ "$AI_ENV" != "unknown" ]; then
        echo -e "${CYAN}AI Integration:${NC}"
        echo -e "  Detected: ${YELLOW}${AI_ENV}${NC}"
        echo -e "  Install command: ${BLUE}$(get_install_command $AI_ENV)${NC}"
        echo ""
    fi
    
    echo -e "${CYAN}Quick Start:${NC}"
    echo "  dokploy init --name myapp --type nodejs-postgres"
    echo "  cd myapp"
    echo "  dokploy security scan"
    echo "  dokploy deploy --env production"
    echo ""
    
    echo -e "${CYAN}Available Commands:${NC}"
    echo "  dokploy template list          # List templates"
    echo "  dokploy init                   # Create new project"
    echo "  dokploy security scan          # Security check"
    echo "  dokploy deploy                 # Deploy to Dokploy"
    echo "  dokploy logs                   # View logs"
    echo "  dokploy backup                 # Backup data"
    echo ""
    
    echo -e "${CYAN}Documentation:${NC}"
    echo "  $INSTALL_DIR/docs/security-best-practices.md"
    echo "  https://github.com/Xhuk/dokploy-skills"
    echo ""
    
    # Post-install for AI environments
    case $AI_ENV in
        claude)
            echo -e "${YELLOW}Claude Code Integration:${NC}"
            echo "  Add to CLAUDE.md or use: /plugin marketplace add Xhuk/dokploy-skills"
            ;;
        kimi)
            echo -e "${YELLOW}Kimi Integration:${NC}"
            echo "  Add to SKILLS.md or use: /skill install Xhuk/dokploy-skills"
            ;;
        cursor|windsurf|qoder)
            echo -e "${YELLOW}IDE Integration:${NC}"
            echo "  Add project rules to .cursor/rules/ or equivalent"
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}Happy Deploying!${NC}"
}

# Run main
main "$@"
