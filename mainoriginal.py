from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
)
import subprocess
import sys
import re
import os

# Optional imports with fallbacks
try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import whisper
    WHISPER_MODEL = None  # We'll load it only when needed
    import sounddevice as sd
    import numpy as np
    import wave
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False


class Worker(QThread):
    """Worker thread for running AI models in a separate thread to avoid blocking the GUI."""

    result_ready = pyqtSignal(str)

    def __init__(self, query: str, model_name: str):
        super().__init__()
        self.query = query
        self.model_name = model_name

    def run(self):
        """Run the subprocess for the specified AI model and emit the result."""
        try:
            # First check if ollama is available
            try:
                subprocess.run(["ollama", "list"], capture_output=True, text=True)
            except FileNotFoundError:
                self.result_ready.emit("Error: Ollama is not installed or not in PATH. Please install Ollama first.")
                return
            
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=self.query,
                text=True,
                capture_output=True,
                encoding="utf-8",
            )
            
            if result.returncode != 0:
                self.result_ready.emit(f"Error: {result.stderr}")
                return
                
            response = result.stdout.strip()
            if not response:
                self.result_ready.emit("Error: No response from the model.")
                return
                
            self.result_ready.emit(response)
            
        except Exception as e:
            self.result_ready.emit(f"Error: {str(e)}")


class DeepSeekApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepSeek AI with Speech")
        self.setGeometry(100, 100, 700, 500)

        # TTS State Variables
        self.tts_enabled = False
        self.is_speaking = False
        self.speech_queue = []
        
        # Check available TTS methods
        tts_methods = []
        if PYTTSX3_AVAILABLE:
            tts_methods.append("pyttsx3 (System)")
        if COQUI_TTS_AVAILABLE:
            tts_methods.append("Coqui TTS (Local AI)")
        
        # Initialize UI
        self.setup_ui(tts_methods)
        
    def setup_ui(self, tts_methods):
        """Setup the UI components"""
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Model Selection
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["deepseek-r1", "deepseek-coder", "mistral"])
        self.layout.addWidget(self.model_dropdown)

        # Output Display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.layout.addWidget(self.output_display)

        # Speaking Status Indicator
        self.speaking_indicator = QLabel("")
        self.speaking_indicator.setStyleSheet("color: gray;")
        self.layout.addWidget(self.speaking_indicator)

        # Input & Buttons Layout
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your query here...")
        self.input_field.returnPressed.connect(self.handle_query)
        input_layout.addWidget(self.input_field)

        self.submit_button = QPushButton("Send")
        self.submit_button.clicked.connect(self.handle_query)
        input_layout.addWidget(self.submit_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.output_display.clear)
        input_layout.addWidget(self.clear_button)

        self.layout.addLayout(input_layout)

        # Speech Controls Layout
        speech_layout = QHBoxLayout()

        if tts_methods:  # Only show TTS controls if methods are available
            # TTS Enable Toggle
            self.tts_toggle = QCheckBox("Enable TTS")
            self.tts_toggle.stateChanged.connect(self.toggle_tts)
            speech_layout.addWidget(self.tts_toggle)

            # TTS Dropdown
            self.tts_dropdown = QComboBox()
            self.tts_dropdown.addItems(tts_methods)
            speech_layout.addWidget(self.tts_dropdown)

            # Stop Button
            self.stop_button = QPushButton("Stop Speaking")
            self.stop_button.clicked.connect(self.stop_speaking)
            self.stop_button.setEnabled(False)
            speech_layout.addWidget(self.stop_button)
        else:
            # Show message if no TTS methods are available
            tts_label = QLabel("TTS not available. Install TTS or pyttsx3.")
            tts_label.setStyleSheet("color: gray;")
            speech_layout.addWidget(tts_label)

        # Add a spacer to separate TTS and STT controls
        speech_layout.addStretch()

        # STT Section
        stt_section = QHBoxLayout()
        if STT_AVAILABLE:
            # STT Status Label
            self.stt_status = QLabel("")
            self.stt_status.setStyleSheet("color: gray;")
            stt_section.addWidget(self.stt_status)
            
            # STT Button
            self.stt_button = QPushButton("🎤 Listen (STT)")
            self.stt_button.clicked.connect(self.start_listening)
            stt_section.addWidget(self.stt_button)
        else:
            # Show message if STT is not available
            stt_label = QLabel("STT not available. Install whisper and sounddevice.")
            stt_label.setStyleSheet("color: gray;")
            stt_section.addWidget(stt_label)

        speech_layout.addLayout(stt_section)
        self.layout.addLayout(speech_layout)

        self.current_worker = None

        if STT_AVAILABLE:
            # STT Button
            self.stt_button = QPushButton("🎤 Listen (STT)")
            self.stt_button.clicked.connect(self.start_listening)
            speech_layout.addWidget(self.stt_button)
        else:
            # Show message if STT is not available
            stt_label = QLabel("STT not available. Install whisper and sounddevice.")
            stt_label.setStyleSheet("color: gray;")
            speech_layout.addWidget(stt_label)

        self.layout.addLayout(speech_layout)

        self.current_worker = None

    def toggle_tts(self, state):
        """Toggle TTS functionality"""
        self.tts_enabled = bool(state)
        self.stop_button.setEnabled(self.tts_enabled)
        status = "enabled" if self.tts_enabled else "disabled"
        self.output_display.append(f"Text-to-Speech {status}")

    def stop_speaking(self):
        """Stop current TTS output"""
        self.is_speaking = False
        self.speech_queue.clear()
        self.speaking_indicator.setText("")
        self.stop_button.setEnabled(False)
        # Stop the current TTS engine
        if hasattr(self, 'engine'):
            try:
                self.engine.stop()
            except:
                pass

    def handle_query(self):
        """Handles the submission of the query and starts the worker thread."""
        query = self.input_field.text().strip()
        if not query:
            return

        model_name = self.model_dropdown.currentText()
        self.output_display.append(f"Query: {query}")

        self.current_worker = Worker(query, model_name)
        self.current_worker.result_ready.connect(self.display_result)
        self.current_worker.start()

    def display_result(self, response: str):
        """Processes and displays the AI response in the output display."""
        # Remove any unwanted tags or non-text elements
        response = re.sub(r"<.*?>", "", response).strip()

        if not response:
            self.output_display.append("AI response is empty or invalid.")
            return

        if len(response) < 5:
            self.output_display.append("AI response is too short or not meaningful.")
            return

        # Display the result
        self.output_display.append(f"AI: {response}")

        # Handle TTS if enabled
        if self.tts_enabled and not self.is_speaking:
            self.text_to_speech(response)
        elif self.tts_enabled:
            self.speech_queue.append(response)

    def text_to_speech(self, text):
        """Enhanced TTS function with visual feedback"""
        if not self.tts_enabled or not text or len(text.strip()) < 5:
            return

        self.is_speaking = True
        self.speaking_indicator.setText("🔊 AI is speaking...")
        self.stop_button.setEnabled(True)

        # Clean the text
        text = re.sub(r"<.*?>", "", text).strip()

        try:
            method = self.tts_dropdown.currentText()
            if method == "pyttsx3 (System)" and PYTTSX3_AVAILABLE:
                self.engine = pyttsx3.init()
                self.engine.say(text)
                self.engine.runAndWait()
            elif method == "Coqui TTS (Local AI)" and COQUI_TTS_AVAILABLE:
                self.coqui_tts(text)
            else:
                raise Exception("Selected TTS method is not available")

            # Process next in queue if any
            if self.speech_queue and self.tts_enabled:
                next_text = self.speech_queue.pop(0)
                QTimer.singleShot(500, lambda: self.text_to_speech(next_text))
            else:
                self.is_speaking = False
                self.speaking_indicator.setText("")
                self.stop_button.setEnabled(False)

        except Exception as e:
            self.output_display.append(f"TTS Error: {str(e)}")
            self.is_speaking = False
            self.speaking_indicator.setText("")
            self.stop_button.setEnabled(False)

    def start_listening(self):
        """Records audio and converts it to text using the Whisper model."""
        if not STT_AVAILABLE:
            self.output_display.append("Error: Speech-to-Text is not available. Please install whisper and sounddevice.")
            return

        try:
            samplerate = 16000
            duration = 5  # seconds
            filename = "stt_record.wav"

            self.output_display.append("Listening...")
            self.stt_button.setEnabled(False)  # Disable button while recording
            QApplication.processEvents()  # Update UI

            # Record audio
            audio_data = sd.rec(
                int(samplerate * duration),
                samplerate=samplerate,
                channels=1,
                dtype=np.int16,
            )
            sd.wait()

            # Save to WAV file
            with wave.open(filename, "wb") as wavefile:
                wavefile.setnchannels(1)
                wavefile.setsampwidth(2)
                wavefile.setframerate(samplerate)
                wavefile.writeframes(audio_data.tobytes())

            self.output_display.append("Processing speech...")
            QApplication.processEvents()  # Update UI

            # Load model only when needed
            global WHISPER_MODEL
            if WHISPER_MODEL is None:
                self.output_display.append("Loading Whisper model (first time only)...")
                QApplication.processEvents()
                WHISPER_MODEL = whisper.load_model("base")

            # Transcribe
            result = WHISPER_MODEL.transcribe(filename)
            transcribed_text = result["text"].strip()

            if transcribed_text:
                self.input_field.setText(transcribed_text)
                self.output_display.append(f"Transcribed: {transcribed_text}")
            else:
                self.output_display.append("No speech detected.")

        except Exception as e:
            self.output_display.append(f"Error during speech recognition: {str(e)}")
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
            self.stt_button.setEnabled(True)
            self.output_display.append("Ready.")

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Return:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter: New line
                cursor = self.input_field.textCursor()
                cursor.insertText('\n')
            else:
                # Enter: Send message
                self.handle_query()
        else:
            super().keyPressEvent(event)

    def text_to_speech(self, text=None):
        """Converts text to speech using the selected method in the dropdown."""
        # If text is None, get it from the input field (human input)
        if text is None:
            text = self.input_field.text().strip()  # Get text from the input field

        print(f"Debug: Text to convert: '{text}'")  # Debug statement
        method = self.tts_dropdown.currentText()  # Ensure method is defined
        print(f"Debug: Selected TTS method: {method}")  # Debug statement
        if not text or len(text.strip()) < 5 or getattr(self, 'tts_running', False):
            self.output_display.append("No valid text to convert.")
            print(f"Debug: No valid text to convert. Text: '{text}'")
            return

        # Remove any unwanted tags or non-text elements
        text = re.sub(r"<.*?>", "", text).strip()

        if not text:
            self.output_display.append("No text to convert.")
            print(f"Debug: No text after cleaning. Text: '{text}'")
            return

        # Check if the text is too short for TTS
        if len(text.strip()) < 5:  # Adjust length threshold as necessary
            self.output_display.append("Text is too short for TTS.")
            return

        method = self.tts_dropdown.currentText()

        try:
            if method == "pyttsx3 (System)":
                engine = pyttsx3.init()
                engine.say(text)
                print("Debug: TTS engine initialized, speaking...")  # Debug statement
                engine.runAndWait()
                print("Debug: TTS finished speaking.")  # Debug statement

            elif method == "Coqui TTS (Local AI)":
                print("Debug: Triggering Coqui TTS method.")
                self.coqui_tts(text)

        except Exception as e:
            self.output_display.append(f"Failed to use TTS: {str(e)}")

    def coqui_tts(self, text):
        try:
            model = TTS("tts_models/en/ljspeech/glow-tts").to("cpu")
            file_path = "output.wav"
            print(
                f"Debug: Length of input text: {len(text)}"
            )  # Log the length of the input text
            if len(text) < 5:  # Ensure the text is long enough for TTS
                raise ValueError("Input text is too short for TTS.")
            model.tts_to_file(text, file_path=file_path)
            print(f"Debug: TTS output saved to {file_path}.")
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print("Debug: Audio file created successfully and is not empty.")
            else:
                print("Debug: Audio file was not created or is empty.")
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "output.wav"])
            os.remove("output.wav")
        except Exception as e:
            self.output_display.append(f"Failed to use Coqui TTS: {str(e)}")

    def closeEvent(self, event):
        """Override closeEvent to handle thread cleanup properly."""
        if self.current_worker and self.current_worker.isRunning():
            print("Waiting for worker thread to finish...")
            self.current_worker.quit()  # Ask the worker to finish
            self.current_worker.wait()  # Ensure the worker finishes before closing the window
            print("Worker thread finished.")

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeepSeekApp()
    window.show()
    sys.exit(app.exec())