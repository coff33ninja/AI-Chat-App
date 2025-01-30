# AI Chat App

A desktop application for interacting with various AI models, featuring text-to-speech, speech-to-text, and multi-session support.

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

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama (for AI model support)
- Qt6 (installed automatically with requirements)

### Optional Dependencies

- pyttsx3 (for basic TTS)
- Coqui TTS (for enhanced TTS)
- OpenAI Whisper (for STT)
- sounddevice (for STT)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AI-Chat-App.git
cd AI-Chat-App
```

2. Install dependencies:

On Windows:
```bash
.\install.ps1
```

On Linux/Mac:
```bash
./install.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. **Starting a Chat**
   - Select an AI model from the dropdown
   - Click "New Chat" or use Ctrl+N
   - Type your message and press Enter or click Send

2. **Using Voice Features**
   - Enable TTS by checking "Enable TTS"
   - Click the microphone button for voice input (if available)

3. **Managing Sessions**
   - Save current session: Ctrl+S
   - Clear chat: Ctrl+L
   - Switch between tabs for different conversations

4. **Customization**
   - Toggle theme: Ctrl+T
   - Configure shortcuts: Settings → Keyboard Shortcuts
   - Adjust model settings: Settings → Model Settings

## Contributing

This project is open for contributions. Please feel free to submit issues, fork the repository and create pull requests for any improvements.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors and users
- Built with PyQt6
- Uses Ollama for AI model integration