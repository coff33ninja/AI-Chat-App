# DeepSeek AI Assistant

A desktop application that provides an interface to interact with DeepSeek AI models, featuring text-to-speech and speech-to-text capabilities.

## Features

- Interactive chat interface with DeepSeek AI models
- Text-to-Speech (TTS) support with multiple engines:
  - System TTS (pyttsx3)
  - Coqui TTS (optional)
- Speech-to-Text (STT) using OpenAI's Whisper
- Configurable model selection
- Queue system for TTS responses
- Visual feedback for AI speech status

## Requirements

- Python 3.8 or higher
- Ollama (for AI model interaction)
- PyQt6 (for GUI)
- Additional dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deepseek-assistant.git
cd deepseek-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Ollama following instructions at: https://ollama.ai/

## Usage

1. Start the application:
```bash
python Deepseek-ai.py
```

2. Select your preferred AI model from the dropdown
3. Type your query and press Enter or click Send
4. Toggle TTS to enable voice responses
5. Use the microphone button for voice input

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.