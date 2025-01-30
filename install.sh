#!/bin/bash

# Exit on error
set -e

echo "Starting AI Chat App installation..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install Python if not present
if ! command_exists python3; then
    echo "Installing Python..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install python3
    else
        # Linux
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    fi
fi

# Check and install Git if not present
if ! command_exists git; then
    echo "Installing Git..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install git
    else
        sudo apt-get install -y git
    fi
fi

# Check and install Ollama if not present
if ! command_exists ollama; then
    echo "Installing Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ollama
    else
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
fi

# Clone repository
echo "Cloning AI Chat App repository..."
REPO_PATH="$HOME/AI-Chat-App"
rm -rf "$REPO_PATH"
git clone https://github.com/coff33ninja/AI-Chat-App.git "$REPO_PATH"
cd "$REPO_PATH"

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Pull Ollama models
echo "Pulling AI models..."
ollama pull deepseek-coder
ollama pull deepseek-r1
ollama pull mistral

echo "Installation complete! Starting AI Chat App..."
python3 main.py