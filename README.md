# DeepSeek AI Assistant

A desktop application that combines AI chat capabilities with speech features, built with PyQt6.

## Features

- AI Chat Interface using Ollama models
- Text-to-Speech (TTS) for AI responses
- Speech-to-Text (STT) for voice input
- Multiple TTS engine support
  - System TTS (pyttsx3)
  - Coqui TTS (optional)
- Intuitive UI with keyboard shortcuts

## Requirements

- Python 3.8+
- Ollama installed and in PATH
- Required Python packages (see requirements.txt)

## AI Setup

1. Install Ollama:
   - Visit [Ollama's official website](https://ollama.ai)
   - Follow installation instructions for your operating system
   - Make sure it's added to your system PATH

2. Pull required models:
```bash
git clone <repository-url>
cd deepseek-assistant
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install Ollama:
   - Follow instructions at [Ollama's official website](https://ollama.ai)
   - Make sure it's added to your system PATH

## Usage

1. Start the application:
```bash
python Deepseek-ai.py
```

2. Select an AI model from the dropdown
3. Type your query or use the voice input button
4. Toggle TTS to have AI responses read aloud

## Keyboard Shortcuts

- `Enter`: Send message
- `Shift + Enter`: New line in input field

## TTS Rules

1. TTS Activation
   - Only activates when explicitly enabled via toggle
   - Only reads AI responses
   - Manual stop option available

2. AI Speech Monitoring
   - Visual indicator shows when AI is speaking
   - Optional auditory cues

3. Input Handling & Interruptions
   - Enter sends query
   - Shift+Enter creates new line
   - New queries during speech are queued

4. Conversational Flow
   - Waits for complete AI response
   - Natural pauses between responses
   - Queue system for multiple responses

## Dependencies

Core dependencies:
- PyQt6: UI framework
- pyttsx3: System TTS
- openai-whisper: Speech recognition
- sounddevice: Audio recording
- numpy: Numerical operations

Optional:
- Coqui TTS: Enhanced TTS capabilities

## License

[MIT License](LICENSE)