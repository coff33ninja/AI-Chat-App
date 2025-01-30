#!/bin/bash

# Exit on error
set -e

echo "Starting AI Chat App installation..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif command_exists apt-get; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Function to install nala on Debian/Ubuntu systems
install_nala() {
    echo "Installing nala package manager..."
    sudo apt-get update
    sudo apt-get install -y nala
    # Update package lists with nala
    sudo nala update
}

# Function to detect package manager
detect_package_manager() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "brew"
    elif command_exists nala; then
        echo "nala"
    elif command_exists apt-get; then
        echo "apt"
    else
        echo "unknown"
    fi
}

# Function to install packages with fallback
install_package() {
    local package_name="$1"
    local brew_package="${2:-$1}"  # Use $1 if $2 is not provided
    local pkg_manager=$(detect_package_manager)
    
    echo "Installing $package_name..."
    
    case $pkg_manager in
        "brew")
            if ! brew install "$brew_package"; then
                echo "Homebrew installation failed for $package_name"
                return 1
            fi
            ;;
        "nala")
            if ! sudo nala install -y "$package_name"; then
                echo "Nala installation failed for $package_name, falling back to apt..."
                if ! sudo apt-get install -y "$package_name"; then
                    echo "Apt installation failed for $package_name"
                    return 1
                fi
            fi
            ;;
        "apt")
            if ! sudo apt-get install -y "$package_name"; then
                echo "Apt installation failed for $package_name"
                return 1
            fi
            ;;
        *)
            echo "Unsupported package manager"
            return 1
            ;;
    esac
    return 0
}

# Create logs directory
mkdir -p logs

# Install nala if on Debian/Ubuntu and not already installed
if [[ "$(detect_os)" == "debian" ]] && ! command_exists nala; then
    install_nala
fi

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [ "$(printf '%s\n' "3.10" "$version" | sort -V | head -n1)" = "3.10" ]; then
            return 0
        fi
    fi
    return 1
}

# Install or update Python
if ! check_python_version; then
    echo "Installing/Updating Python..."
    if [[ "$(detect_package_manager)" == "brew" ]]; then
        install_package "python@3.10"
    else
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        if command_exists nala; then
            sudo nala update
            install_package "python3.10" 
            install_package "python3.10-venv"
            install_package "python3-pip"
        else
            sudo apt-get update
            install_package "python3.10"
            install_package "python3.10-venv"
            install_package "python3-pip"
        fi
    fi
fi

# Install Git if not present
if ! command_exists git; then
    install_package "git"
fi

# Install FFmpeg if not present
if ! command_exists ffmpeg; then
    install_package "ffmpeg"
fi

# Install Ollama if not present
if ! command_exists ollama; then
    echo "Installing Ollama..."
    if [[ "$(detect_package_manager)" == "brew" ]]; then
        install_package "ollama"
    else
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
fi

# Create and execute post-install script
post_install_script=$(mktemp)
cat << 'EOF' > "$post_install_script"
#!/bin/bash

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

# Pull Ollama models
echo "Pulling AI models..."
ollama pull deepseek-coder
ollama pull deepseek-r1
ollama pull mistral

echo "Installation complete! Starting AI Chat App..."

# Run the application with dependency checking
if ! python3 run_app.py; then
    echo "Error: Failed to start the application. Please check the logs for details."
    exit 1
fi

echo "Press Enter to exit..."
read
EOF

# Make post-install script executable
chmod +x "$post_install_script"

# Launch post-install script in a new terminal
if [[ "$OSTYPE" == "darwin"* ]]; then
    open -a Terminal.app "$post_install_script"
else
    if command_exists gnome-terminal; then
        gnome-terminal -- "$post_install_script"
    elif command_exists xterm; then
        xterm -e "$post_install_script"
    else
        # Fallback to running in current terminal if no GUI terminal is available
        "$post_install_script"
    fi
fi

echo "Setup complete! The application should now be running in a new window."
