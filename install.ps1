# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    Break
}

# Function to check if a command exists
function Test-Command($CommandName) {
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

# Set up error handling
$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "Starting AI Chat App installation..." -ForegroundColor Green

# Check and install Python if not present
if (-not (Test-Command python)) {
    Write-Host "Installing Python..." -ForegroundColor Yellow
    winget install Python.Python.3.10
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Check and install Git if not present
if (-not (Test-Command git)) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    winget install Git.Git
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Check and install Ollama if not present
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Ollama..." -ForegroundColor Yellow
    $ollamaInstaller = "$env:TEMP\ollama-installer.exe"

    # Download the installer
    Invoke-WebRequest -Uri "https://ollama.ai/download/OllamaSetup.exe" -OutFile $ollamaInstaller

    # Install silently
    Start-Process -FilePath $ollamaInstaller -ArgumentList "/S" -Wait

    # Remove installer after installation
    Remove-Item $ollamaInstaller -Force

    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")

    Write-Host "Ollama installation complete. Restart your terminal or run 'refreshenv' (if using Chocolatey)." -ForegroundColor Green
} else {
    Write-Host "Ollama is already installed." -ForegroundColor Cyan
}

# Clone repository
Write-Host "Cloning AI Chat App repository..." -ForegroundColor Yellow
$repoPath = "$env:USERPROFILE\AI-Chat-App"
if (Test-Path $repoPath) {
    Remove-Item -Path $repoPath -Recurse -Force
}
git clone https://github.com/coff33ninja/AI-Chat-App.git $repoPath
Set-Location $repoPath

# Create and activate virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Pull Ollama models
Write-Host "Pulling AI models..." -ForegroundColor Yellow
ollama pull deepseek-coder
ollama pull deepseek-r1
ollama pull mistral

Write-Host "Installation complete! Starting AI Chat App..." -ForegroundColor Green
python main.py
