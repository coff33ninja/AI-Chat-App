# AI Chat App

A sophisticated chat application that leverages AI models through Ollama integration, featuring a modern PyQt6 interface with support for text-to-speech and speech-to-text capabilities.

## 🚧 Work in Progress

This project is actively under development. Current features and upcoming plans are outlined below.

### Current Features

- **Multi-Model Support**: Compatible with various AI models through Ollama
- **Text-to-Speech (TTS)**: Multiple TTS options including:
  - pyttsx3
  - Coqui TTS (when available)
- **Speech-to-Text (STT)**: Voice input capability (when dependencies are installed)
- **Multi-Tab Interface**: Multiple chat sessions in a single window
- **Session Management**: Save and load chat sessions
- **Theme Support**: Light and dark mode
- **Keyboard Shortcuts**: Customizable shortcuts for common actions
- **Chat History**: Persistent chat history with export options

### Upcoming Features

1. **Model Management**
   - Model download interface
   - Model fine-tuning capabilities
   - Custom model configuration

2. **UI Enhancements**
   - Improved chat visualization
   - Better mobile responsiveness
   - Enhanced accessibility features
   - Custom themes support

3. **Advanced Features**
   - Context length management
   - Prompt templates
   - Chat session sharing
   - Advanced export options

## Installation Scripts

The application provides robust installation scripts for both Windows and Unix-like systems (Linux/macOS):

### Windows Installation (install.ps1)

The PowerShell installation script provides:

1. **Package Management**
   - Installs Chocolatey if not present
   - Uses Chocolatey to install winget-cli
   - Fallback mechanisms: winget → Chocolatey for package installations
   - Automatic environment variable updates

2. **Core Components Installation**
   - Python 3.11
   - Git
   - FFmpeg
   - Ollama

3. **Environment Setup**
   - Creates isolated virtual environment
   - Handles environment variables
   - Manages dependencies in a separate terminal
   - Automatic post-install configuration

4. **Error Handling**
   - Administrator privilege checks
   - Package installation verification
   - Fallback mechanisms for failed installations
   - Detailed error logging

### Linux/macOS Installation (install.sh)

The shell installation script provides:

1. **Package Management**
   - Debian/Ubuntu: Installs and uses nala (with apt fallback)
   - macOS: Uses Homebrew
   - Intelligent package manager detection and selection
   - Automatic dependency resolution

2. **Core Components Installation**
   - Python 3.10 (with version checking)
   - Git
   - FFmpeg
   - Ollama

3. **Environment Setup**
   - Creates Python virtual environment
   - Handles terminal-specific launching
   - OS-specific package management
   - Permission handling

Both scripts feature:
- Automatic dependency resolution
- Error handling and fallback mechanisms
- Separate post-install environment setup
- Automatic Ollama model pulling (deepseek-coder, deepseek-r1, mistral)
- Comprehensive logging
- Platform-specific optimizations

## Project Structure

### Core Components

1. **User Interface (PyQt6)**
   - `modules/tab_manager.py`: Manages chat tabs and sessions
   - `modules/chat_interface.py`: Main chat interface implementation
   - `modules/settings_dialog.py`: Application settings management

2. **AI Integration**
   - `modules/ai_handler.py`: Manages AI model interactions
   - `modules/model_config.py`: AI model configuration
   - `modules/ollama_interface.py`: Ollama API integration

3. **Speech Features**
   - `modules/tts_manager.py`: Text-to-speech functionality
   - `modules/stt_manager.py`: Speech-to-text processing
   - `modules/audio_utils.py`: Audio processing utilities

4. **System Components**
   - `run_app.py`: Main application entry point
   - `dependency_manager.py`: Dependency management system
   - `utils/logger.py`: Logging system implementation

### Features

1. **Chat Management**
   - Multiple chat sessions
   - Session persistence
   - Chat history management
   - Context handling

2. **AI Capabilities**
   - Multiple model support
   - Context-aware responses
   - Model switching
   - Parameter customization

3. **Speech Processing**
   - Text-to-speech output
   - Speech-to-text input
   - Voice command support
   - Multiple TTS engine support

4. **User Interface**
   - Dark/Light theme support
   - Customizable shortcuts
   - Responsive design
   - Tab-based interface

## Dependencies

### Core Requirements
- Python 3.10 or higher
- PyQt6
- Ollama
- FFmpeg

### Additional Features
- pyttsx3 (basic TTS)
- Coqui TTS (enhanced TTS)
- OpenAI Whisper (STT)
- sounddevice (audio I/O)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/coff33ninja/AI-Chat-App.git
cd AI-Chat-App
```

2. Run the installation script:

Windows:
```powershell
.\install.ps1
```

Linux/macOS:
```bash
chmod +x install.sh
./install.sh
```

The installation scripts will:
- Install required package managers
- Set up necessary dependencies
- Create a Python virtual environment
- Pull required Ollama models
- Launch the application

## Development

### Logging System

The application includes comprehensive logging:

1. **Categories**
   - Model operations
   - User interactions
   - System events
   - Error tracking

2. **Log Levels**
   - DEBUG: Development details
   - INFO: General operations
   - WARNING: Non-critical issues
   - ERROR: Critical problems

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with PyQt6
- Uses Ollama for AI integration
- Inspired by modern chat applications
