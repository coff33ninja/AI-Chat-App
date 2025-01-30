# AI Chat App

A desktop application that provides an interface to interact with various AI models through Ollama, featuring text-to-speech and speech-to-text capabilities.

## Quick Installation

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/coff33ninja/AI-Chat-App/main/install.ps1 | iex
```

### Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/coff33ninja/AI-Chat-App/main/install.sh | bash
```

The one-line installers will:
1. Install Ollama if not present
2. Clone the repository
3. Set up Python virtual environment
4. Install required dependencies
5. Pull necessary AI models
6. Launch the application

## Manual Installation Guide

### 1. System Requirements

- Windows, macOS, or Linux
- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- GPU recommended but not required
- Microphone (for voice input)
- Speakers (for TTS output)

### 2. Install Ollama

1. Download Ollama:
   - Windows: [Ollama for Windows](https://ollama.ai/download/windows)
   - macOS: [Ollama for macOS](https://ollama.ai/download/mac)
   - Linux:
     ```bash
     curl -fsSL https://ollama.ai/install.sh | sh
     ```

2. Verify installation:
   ```bash
   ollama --version
   ```

### 3. Setup AI Models

1. Pull required models:
   ```bash
   # Main model for code-related queries
   ollama pull deepseek-coder

   # General purpose models (optional)
   ollama pull deepseek-r1
   ollama pull mistral
   ```

2. Test model:
   ```bash
   ollama run deepseek-coder "Hello, are you working?"
   ```

### 4. Install Python Dependencies

1. Clone the repository:
   ```bash
   git clone https://github.com/coff33ninja/AI-Chat-App.git
   cd AI-Chat-App
   ```

2. Create virtual environment (recommended):
   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### 5. Start the Application

1. Run:
   ```bash
   python main.py
   ```

2. First-time setup:
   - Select your preferred model from the dropdown
   - Enable TTS if desired
   - Test voice input if needed

## Features

- Interactive chat interface with various AI models through Ollama
- Text-to-Speech (TTS) support with multiple engines:
  - System TTS (pyttsx3)
  - Coqui TTS (optional)
- Speech-to-Text (STT) using OpenAI's Whisper
- Configurable model selection
- Queue system for TTS responses
- Visual feedback for AI speech status

## TTS Rules and Behavior

1. TTS Activation
   - TTS only activates when explicitly enabled via toggle
   - Only AI responses are read aloud
   - Manual stop option available

2. AI Speech Monitoring
   - Visual indicator shows when AI is speaking
   - Optional auditory cues for feedback

3. Input Handling & Interruptions
   - Enter sends the query
   - Shift+Enter creates a new line
   - New queries during speech are queued

4. Conversational Flow
   - Waits for complete AI response before speaking
   - Natural pauses between responses
   - Seamless transitions between spoken input/output

## Common Issues

1. "Ollama not found":
   - Make sure Ollama is installed
   - Add Ollama to system PATH
   - Restart your terminal/computer

2. "Model not found":
   - Run `ollama pull deepseek-coder` again
   - Check internet connection
   - Verify model name in dropdown matches pulled model

3. "TTS not working":
   - Check if speakers are connected and working
   - Try switching TTS engine in dropdown
   - Install additional TTS dependencies if needed

4. "Voice input not working":
   - Check if microphone is connected and set as default
   - Allow microphone access in system settings
   - Install additional STT dependencies if needed

## Next Steps

1. Explore different models:
   - Try different models for different tasks
   - Compare response quality and speed

2. Customize TTS:
   - Try different TTS engines
   - Adjust speech rate and volume

3. Use keyboard shortcuts:
   - Enter to send
   - Shift+Enter for new line
   - Stop button to halt speech

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Visit our [GitHub repository](https://github.com/coff33ninja/AI-Chat-App) for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.