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

# Create log directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
}

# Install Chocolatey if not present
if (-not (Test-Command choco)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}

# Install winget using Chocolatey if not present
if (-not (Test-Command winget)) {
    Write-Host "Installing winget using Chocolatey..." -ForegroundColor Yellow
    choco install -y winget-cli
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    
    # Verify winget installation
    if (-not (Test-Command winget)) {
        Write-Error "Failed to install winget. Please install manually from the Microsoft Store."
        exit 1
    }
}

# Create post-install script for environment-dependent installations
$postInstallScript = @'
# Function to install with winget, falling back to chocolatey
function Install-Package {
    param (
        [string]$WingetId,
        [string]$ChocoId,
        [string]$Name
    )
    Write-Host "Installing $Name..." -ForegroundColor Yellow
    try {
        winget install $WingetId
        if ($LASTEXITCODE -ne 0) { throw "Winget installation failed" }
    }
    catch {
        Write-Host "Winget installation failed, trying Chocolatey..." -ForegroundColor Yellow
        choco install $ChocoId -y
    }
}

# Install Python and FFmpeg with fallback
Install-Package -WingetId "Python.Python.3.10" -ChocoId "python310" -Name "Python"
Install-Package -WingetId "Gyan.FFmpeg" -ChocoId "ffmpeg" -Name "FFmpeg"

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

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

# Pull Ollama models
Write-Host "Pulling AI models..." -ForegroundColor Yellow
ollama pull deepseek-coder
ollama pull deepseek-r1
ollama pull mistral

Write-Host "Installation complete! Starting AI Chat App..." -ForegroundColor Green

# Run the application with dependency checking
try {
    python run_app.py
}
catch {
    Write-Error "Failed to start the application. Please check the logs for details."
    exit 1
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'@

# Save post-install script
$postInstallPath = "$env:TEMP\post_install.ps1"
$postInstallScript | Out-File -FilePath $postInstallPath -Encoding UTF8

# Check and install Git if not present
if (-not (Test-Command git)) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    try {
        winget install Git.Git
    }
    catch {
        Write-Host "Winget installation failed, trying Chocolatey..." -ForegroundColor Yellow
        choco install git -y
    }
}

# Check and install Ollama if not present
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Ollama..." -ForegroundColor Yellow
    $ollamaInstaller = "$env:TEMP\ollama-installer.exe"
    Invoke-WebRequest -Uri "https://ollama.ai/download/OllamaSetup.exe" -OutFile $ollamaInstaller
    Start-Process -FilePath $ollamaInstaller -ArgumentList "/S" -Wait
    Remove-Item $ollamaInstaller -Force
}

# Launch post-install script in a new window
Write-Host "Launching environment setup in a new window..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$postInstallPath`"" -Wait

Write-Host "Setup complete! The application should now be running in a new window." -ForegroundColor Green
