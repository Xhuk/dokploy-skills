# Dokploy Skills - Universal Installer for Windows
# Detects environment and installs with appropriate method
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

# Colors
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Cyan = "Cyan"
    Blue = "Blue"
}

function Write-ColorText {
    param($Text, $Color)
    Write-Host $Text -ForegroundColor $Color
}

# ASCII Art Banner
Write-ColorText "" $Colors.Cyan
Write-ColorText "██████╗  ██████╗ ██╗  ██╗██████╗ ██╗      ██████╗ ██╗   ██╗" $Colors.Cyan
Write-ColorText "██╔══██╗██╔═══██╗██║ ██╔╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝" $Colors.Cyan
Write-ColorText "██║  ██║██║   ██║█████╔╝ ██████╔╝██║     ██║   ██║ ╚████╔╝" $Colors.Cyan
Write-ColorText "██║  ██║██║   ██║██╔═██╗ ██╔═══╝ ██║     ██║   ██║  ╚██╔╝" $Colors.Cyan
Write-ColorText "██████╔╝╚██████╔╝██║  ██╗██║     ███████╗╚██████╔╝   ██║" $Colors.Cyan
Write-ColorText "╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝" $Colors.Cyan
Write-ColorText "" $Colors.Cyan
Write-ColorText "Advanced Toolkit for Dokploy Deployments" $Colors.Green
Write-ColorText ""

# Detect AI Environment
function Detect-AIEnvironment {
    $envVars = @{
        Claude = $env:CLAUDE_CODE -or $env:ANTHROPIC_API_KEY -or (Test-Path ".claude")
        Kimi = $env:KIMI_CLI -or (Test-Path ".kimi") -or (Test-Path ".kimi/config")
        Codex = $env:CODEX_CLI -or (Test-Path ".codex")
        Cursor = $env:CURSOR -or (Test-Path ".cursor")
        Windsurf = $env:WINDSURF -or (Test-Path ".windsurf")
        Qoder = $env:QODER -or (Test-Path ".qoder")
        Copilot = $env:COPILOT -or (Test-Path ".github/copilot")
    }
    
    foreach ($ai in $envVars.Keys) {
        if ($envVars[$ai]) {
            return $ai.ToLower()
        }
    }
    return "unknown"
}

# Get install command for AI environment
function Get-InstallCommand {
    param($AIEnv)
    $repo = "Xhuk/dokploy-skills"
    
    switch ($AIEnv) {
        "claude" { return "/plugin marketplace add $repo" }
        "kimi" { return "/skill install $repo" }
        "codex" { return "git clone https://github.com/$repo.git" }
        "cursor" { return "git clone https://github.com/$repo.git" }
        "windsurf" { return "git clone https://github.com/$repo.git" }
        "qoder" { return "/plugin install $repo" }
        "copilot" { return "Use Copilot Workspace to import $repo" }
        default { return "pip install git+https://github.com/$repo.git" }
    }
}

# Main installation
function Install-DokploySkills {
    # Detect environment
    $AIEnv = Detect-AIEnvironment
    
    Write-ColorText "Environment Detection:" $Colors.Yellow
    Write-ColorText "  OS: Windows" $Colors.Cyan
    Write-ColorText "  AI Environment: $AIEnv" $Colors.Cyan
    Write-ColorText ""
    
    # Check Python
    Write-ColorText "Checking Python..." $Colors.Yellow
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    
    if (-not $python) {
        Write-ColorText "ERROR: Python not found. Please install Python 3.8+" $Colors.Red
        Write-ColorText "Visit: https://www.python.org/downloads/windows/" $Colors.Yellow
        exit 1
    }
    
    $pythonVersion = & $python.Source --version 2>&1
    Write-ColorText "  Found: $pythonVersion" $Colors.Green
    
    # Check pip
    Write-ColorText ""
    Write-ColorText "Checking pip..." $Colors.Yellow
    $pip = Get-Command pip -ErrorAction SilentlyContinue
    if (-not $pip) {
        Write-ColorText "ERROR: pip not found" $Colors.Red
        exit 1
    }
    Write-ColorText "  Found: pip" $Colors.Green
    
    # Check Git
    Write-ColorText ""
    Write-ColorText "Checking Git..." $Colors.Yellow
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        Write-ColorText "ERROR: Git not found. Please install Git" $Colors.Red
        Write-ColorText "Visit: https://git-scm.com/download/win" $Colors.Yellow
        exit 1
    }
    Write-ColorText "  Found: git" $Colors.Green
    
    # Installation directory
    $installDir = "$env:USERPROFILE\dokploy-skills"
    
    # Clone or update
    Write-ColorText ""
    Write-ColorText "Installing Dokploy Skills..." $Colors.Yellow
    
    if (Test-Path $installDir) {
        Write-ColorText "  Directory exists, updating..." $Colors.Yellow
        Set-Location $installDir
        git pull --quiet 2>$null
    } else {
        Write-ColorText "  Cloning repository..." $Colors.Yellow
        git clone https://github.com/Xhuk/dokploy-skills.git $installDir --quiet
        Set-Location $installDir
    }
    
    # Install package
    Write-ColorText ""
    Write-ColorText "Installing package..." $Colors.Yellow
    & pip install -e . --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "ERROR: Installation failed" $Colors.Red
        exit 1
    }
    
    # Add to PATH
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$installDir*") {
        Write-ColorText ""
        Write-ColorText "Adding to PATH..." $Colors.Yellow
        [Environment]::SetEnvironmentVariable("PATH", "$userPath;$installDir", "User")
        Write-ColorText "  Added to User PATH (restart terminal to apply)" $Colors.Green
    }
    
    # Installation complete
    Write-ColorText ""
    Write-ColorText "========================================" $Colors.Green
    Write-ColorText "   Installation Complete!" $Colors.Green
    Write-ColorText "========================================" $Colors.Green
    Write-ColorText ""
    
    # Show AI-specific integration
    if ($AIEnv -ne "unknown") {
        Write-ColorText "AI Integration:" $Colors.Cyan
        Write-ColorText "  Detected: $AIEnv" $Colors.Yellow
        Write-ColorText "  Install command: $(Get-InstallCommand $AIEnv)" $Colors.Blue
        Write-ColorText ""
    }
    
    Write-ColorText "Quick Start:" $Colors.Cyan
    Write-ColorText "  dokploy init --name myapp --type nodejs-postgres"
    Write-ColorText "  cd myapp"
    Write-ColorText "  dokploy security scan"
    Write-ColorText "  dokploy deploy --env production"
    Write-ColorText ""
    
    Write-ColorText "Available Commands:" $Colors.Cyan
    Write-ColorText "  dokploy template list          # List templates"
    Write-ColorText "  dokploy init                   # Create new project"
    Write-ColorText "  dokploy security scan          # Security check"
    Write-ColorText "  dokploy deploy                 # Deploy to Dokploy"
    Write-ColorText "  dokploy logs                   # View logs"
    Write-ColorText "  dokploy backup                 # Backup data"
    Write-ColorText ""
    
    Write-ColorText "Documentation:" $Colors.Cyan
    Write-ColorText "  $installDir\docs\security-best-practices.md"
    Write-ColorText "  https://github.com/Xhuk/dokploy-skills"
    Write-ColorText ""
    
    # Post-install for AI environments
    switch ($AIEnv) {
        "Claude" {
            Write-ColorText "Claude Code Integration:" $Colors.Yellow
            Write-ColorText "  Add to CLAUDE.md or use: /plugin marketplace add Xhuk/dokploy-skills"
        }
        "Kimi" {
            Write-ColorText "Kimi Integration:" $Colors.Yellow
            Write-ColorText "  Add to SKILLS.md or use: /skill install Xhuk/dokploy-skills"
        }
        "Cursor" {
            Write-ColorText "Cursor Integration:" $Colors.Yellow
            Write-ColorText "  Add project rules to .cursor/rules/"
        }
        "Windsurf" {
            Write-ColorText "Windsurf Integration:" $Colors.Yellow
            Write-ColorText "  Add project rules to .windsurf/rules/"
        }
    }
    
    Write-ColorText ""
    Write-ColorText "Happy Deploying!" $Colors.Green
}

# Run installation
Install-DokploySkills
