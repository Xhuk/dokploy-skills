#!/usr/bin/env python3
"""
Dokploy Skills - AI Environment Detector
Detects which AI assistant is running and adapts accordingly
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


AI_ENVIRONMENTS = {
    'claude': {
        'name': 'Claude Code',
        'check': ['CLAUDE_CODE', 'ANTHROPIC_API_KEY'],
        'dirs': ['.claude'],
        'install_cmd': '/plugin marketplace add {repo}',
        'docs_url': 'https://docs.anthropic.com/claude/docs',
        'config_file': 'CLAUDE.md',
    },
    'kimi': {
        'name': 'Kimi Code',
        'check': ['KIMI_CLI'],
        'dirs': ['.kimi'],
        'install_cmd': '/skill install {repo}',
        'docs_url': 'https://kimi.moonshot.cn',
        'config_file': 'SKILLS.md',
    },
    'codex': {
        'name': 'OpenAI Codex',
        'check': ['CODEX_CLI'],
        'dirs': ['.codex'],
        'install_cmd': 'git clone https://github.com/{repo}.git',
        'docs_url': 'https://platform.openai.com/docs',
        'config_file': '.codex/config',
    },
    'cursor': {
        'name': 'Cursor',
        'check': ['CURSOR'],
        'dirs': ['.cursor'],
        'install_cmd': 'git clone https://github.com/{repo}.git',
        'docs_url': 'https://cursor.sh/docs',
        'config_file': '.cursor/rules/dokploy.md',
    },
    'windsurf': {
        'name': 'Windsurf',
        'check': ['WINDSURF'],
        'dirs': ['.windsurf'],
        'install_cmd': 'git clone https://github.com/{repo}.git',
        'docs_url': 'https://windsurf.com/docs',
        'config_file': '.windsurf/rules/dokploy.md',
    },
    'qoder': {
        'name': 'Qoder',
        'check': ['QODER'],
        'dirs': ['.qoder'],
        'install_cmd': '/plugin install {repo}',
        'docs_url': 'https://qoder.ai/docs',
        'config_file': '.qoder/skills.md',
    },
    'copilot': {
        'name': 'GitHub Copilot',
        'check': ['COPILOT', 'GITHUB_COPILOT'],
        'dirs': ['.github/copilot'],
        'install_cmd': 'Use Copilot Workspace to import {repo}',
        'docs_url': 'https://docs.github.com/copilot',
        'config_file': '.github/copilot/skills.md',
    },
}


def detect_ai_environment() -> Tuple[str, Dict]:
    """
    Detect which AI assistant environment is running.
    
    Returns:
        Tuple of (env_key, env_config)
    """
    for env_key, config in AI_ENVIRONMENTS.items():
        # Check environment variables
        for var in config['check']:
            if os.environ.get(var):
                return env_key, config
        
        # Check directory markers
        for dir_name in config['dirs']:
            if Path(dir_name).exists():
                return env_key, config
    
    return 'unknown', {
        'name': 'Unknown',
        'install_cmd': 'pip install git+https://github.com/{repo}.git',
        'docs_url': '',
        'config_file': '',
    }


def get_install_command(repo: str = 'Xhuk/dokploy-skills') -> str:
    """Get the install command for the detected environment."""
    env_key, config = detect_ai_environment()
    return config['install_cmd'].format(repo=repo)


def get_config_instructions() -> str:
    """Get configuration instructions for the detected environment."""
    env_key, config = detect_ai_environment()
    
    if env_key == 'unknown':
        return """
No specific AI environment detected.

Generic installation:
  pip install git+https://github.com/Xhuk/dokploy-skills.git

Or clone manually:
  git clone https://github.com/Xhuk/dokploy-skills.git
  cd dokploy-skills
  pip install -e .
"""
    
    instructions = f"""
Detected: {config['name']}

Install command:
  {config['install_cmd'].format(repo='Xhuk/dokploy-skills')}

Configuration file: {config['config_file']}
Documentation: {config['docs_url']}
"""
    
    # Add specific instructions per environment
    if env_key == 'claude':
        instructions += """
CLAUDE.md template:
  ---
  # Dokploy Skills
  
  Use this skill for managing Dokploy deployments.
  
  ## Commands
  - dokploy init --name <app> --type <template>
  - dokploy security scan
  - dokploy deploy --env production
  
  ## Security Rules
  - Always run security scan before deploying
  - Use non-root containers
  - Store secrets in environment variables
  ---
"""
    elif env_key == 'kimi':
        instructions += """
SKILLS.md entry:
  ---
  ## Dokploy Skills
  Repository: Xhuk/dokploy-skills
  Description: Advanced toolkit for Dokploy deployments
  Commands:
    - dokploy init
    - dokploy security scan
    - dokploy deploy
  ---
"""
    elif env_key in ['cursor', 'windsurf']:
        instructions += f"""
Project rules ({config['config_file']}):
  ---
  # Dokploy Skills
  
  When working with deployments:
  
  1. Always use `dokploy security scan` before deploying
  2. Use templates from dokploy-skills/templates/
  3. Follow security best practices:
     - Non-root containers
     - Read-only filesystems
     - Internal networks for databases
  ---
"""
    
    return instructions


def print_environment_info():
    """Print detected environment information."""
    env_key, config = detect_ai_environment()
    
    print("=" * 50)
    print("AI Environment Detection")
    print("=" * 50)
    print(f"Detected: {config['name']}")
    print(f"Key: {env_key}")
    print("")
    print(f"Install: {get_install_command()}")
    print("")
    print(get_config_instructions())


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detect AI assistant environment'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'env'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--install-cmd',
        action='store_true',
        help='Print only install command'
    )
    
    args = parser.parse_args()
    
    env_key, config = detect_ai_environment()
    
    if args.install_cmd:
        print(get_install_command())
        return
    
    if args.format == 'json':
        import json
        print(json.dumps({
            'environment': env_key,
            'name': config['name'],
            'install_command': get_install_command(),
            'config_file': config.get('config_file', ''),
            'docs_url': config.get('docs_url', ''),
        }, indent=2))
    elif args.format == 'env':
        print(f"DOKPLOY_AI_ENV={env_key}")
        print(f"DOKPLOY_AI_NAME={config['name']}")
    else:
        print_environment_info()


if __name__ == '__main__':
    main()
