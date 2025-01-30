# Quick Start Guide

## 1. System Requirements

- Windows, macOS, or Linux
- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- GPU recommended but not required
- Microphone (for voice input)
- Speakers (for TTS output)

## 2. Install Ollama

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

## 3. Setup AI Models

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

## 4. Install Python Dependencies

1. Create virtual environment (recommended):
   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## 5. Start the Application

1. Run:
   ```bash
   python Deepseek-ai.py
   ```

2. First-time setup:
   - Select your preferred model from the dropdown
   - Enable TTS if desired
   - Test voice input if needed

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

For more detailed information, see [README.md](README.md).