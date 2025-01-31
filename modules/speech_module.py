from PyQt6.QtCore import QTimer
import re
import os
import subprocess
import wave
import numpy as np
import logging
import unicodedata
import string
import weakref

# Get logger for speech module
logger = logging.getLogger("main.speech")

# Define valid characters (ASCII printable characters)
VALID_CHARS = set(string.printable)

# Character replacement map for common problematic Unicode characters
CHAR_REPLACEMENTS = {
    # Vowels
    '\u0254': 'o',  # Open O
    '\u028a': 'u',  # Upsilon
    '\u0259': 'e',  # Schwa
    '\u025b': 'e',  # Open E
    '\u0251': 'a',  # Script A
    '\u0252': 'a',  # Turned Alpha
    '\u026a': 'i',  # Small Capital I
    '\u0268': 'i',  # Small Capital I
    '\u0289': 'u',  # U bar
    '\u028c': 'v',  # Turned V
    '\u0275': 'o',  # Barred O
    '\u0264': 'g',  # Small Capital G

    # Consonants
    '\u0283': 'sh',  # Esh
    '\u027e': 'r',   # R with Fishhook
    '\u0292': 'zh',  # Ezh
    '\u03b8': 'th',  # Theta
    '\u00f0': 'th',  # Eth
    '\u014b': 'ng',  # Eng
    '\u0279': 'r',   # Turned R
    '\u0288': 't',   # Turned T
    '\u0256': 'd',   # Turned D
    '\u0273': 'n',   # N with retroflex hook
    '\u0272': 'n',   # N with left hook

    # Additional common characters
    '\u2019': "'",   # Right single quotation mark
    '\u2018': "'",   # Left single quotation mark
    '\u201c': '"',   # Left double quotation mark
    '\u201d': '"',   # Right double quotation mark
    '\u2013': '-',   # En dash
    '\u2014': '--',  # Em dash
    '\u00a0': ' ',   # Non-breaking space
}

# Optional imports with fallbacks
try:
    from TTS.api import TTS
    import pkg_resources
    tts_version = pkg_resources.get_distribution('TTS').version
    COQUI_TTS_AVAILABLE = True
    logger.info(f"Coqui TTS available (version {tts_version})")
except ImportError:
    COQUI_TTS_AVAILABLE = False
    logger.warning("Coqui TTS not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    logger.info("System TTS (pyttsx3) available")
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("System TTS (pyttsx3) not available")

try:
    import whisper  # Using the openai-whisper package
    import sounddevice as sd
    WHISPER_MODEL = None
    STT_AVAILABLE = True
    logger.info("Speech-to-Text (Whisper) available")
except ImportError:
    STT_AVAILABLE = False
    logger.warning("Speech-to-Text (Whisper) not available")


class SpeechHandler:
    def __init__(self, parent=None):
        logger.debug("Initializing SpeechHandler")
        self.parent = weakref.proxy(parent) if parent else None  # Use weakref to prevent circular reference
        self.is_speaking = False
        self.speech_queue = []
        self.engine = None
        self.tts_model = None
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.debug(f"Created temporary directory: {self.output_dir}")

    def _init_tts_model(self):
        """Lazy initialization of TTS model"""
        if not self.tts_model and COQUI_TTS_AVAILABLE:
            try:
                logger.info("Initializing Coqui TTS model...")
                self.tts_model = TTS("tts_models/en/ljspeech/glow-tts")
                self.tts_model.to("cpu")
                logger.info("Coqui TTS model initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Coqui TTS model: {str(e)}")
                return False
        return True

    def get_available_tts_methods(self):
        """Returns a list of available TTS methods"""
        methods = []
        if PYTTSX3_AVAILABLE:
            methods.append("pyttsx3 (System)")
        if COQUI_TTS_AVAILABLE:
            methods.append("Coqui TTS (Local AI)")
        logger.debug(f"Available TTS methods: {methods}")
        return methods

    def is_tts_working(self):
        """Check if TTS is currently working and return status"""
        if self.is_speaking:
            return "TTS is currently speaking"
        return "TTS is ready"

    def _sanitize_text(self, text):
        """Enhanced text sanitization for TTS processing"""
        try:
            # Store original text for logging
            original_text = text

            # Step 1: Replace known problematic characters
            for char, replacement in CHAR_REPLACEMENTS.items():
                if char in text:
                    text = text.replace(char, replacement)
                    logger.debug(f"Replaced character {repr(char)} with {repr(replacement)}")

            # Step 2: Normalize Unicode characters
            text = unicodedata.normalize('NFKD', text)

            # Step 3: Build sanitized text using only valid characters
            sanitized = ''.join(c for c in text if c in VALID_CHARS)

            # Log changes if any were made
            if sanitized != original_text:
                # Find and log all characters that were removed
                removed_chars = set()
                for i, char in enumerate(original_text):
                    if char not in VALID_CHARS and char not in CHAR_REPLACEMENTS:
                        removed_chars.add(repr(char))

                if removed_chars:
                    logger.debug(f"Removed unsupported characters: {', '.join(removed_chars)}")
                logger.debug(f"Text sanitized from: {repr(original_text[:50])}... to: {repr(sanitized[:50])}...")

            return sanitized

        except Exception as e:
            logger.error(f"Error during text sanitization: {str(e)}")
            # Return original text if sanitization fails
            return text

    def text_to_speech(self, text, method, callback=None):
        """Enhanced TTS function with visual feedback and character encoding handling"""
        if not text or len(text.strip()) < 5:
            logger.warning("Text too short or empty for TTS")
            return False

        self.is_speaking = True
        logger.info(f"Starting TTS using method: {method}")

        try:
            # Update UI indicator if parent exists
            if self.parent:
                try:
                    self.parent.speaking_indicator.setText("Speaking...")
                    self.parent.stop_button.setEnabled(True)
                except (ReferenceError, RuntimeError):
                    pass  # Parent widget has been deleted

            # Clean and sanitize the text
            text = re.sub(r"<.*?>", "", text).strip()
            original_text = text
            text = self._sanitize_text(text)

            if method == "pyttsx3 (System)" and PYTTSX3_AVAILABLE:
                logger.debug("Using pyttsx3 for TTS")
                self.engine = pyttsx3.init()
                self.engine.say(text)
                self.engine.runAndWait()
            elif method == "Coqui TTS (Local AI)" and COQUI_TTS_AVAILABLE:
                logger.debug("Using Coqui TTS")
                if not self._init_tts_model():
                    raise Exception("Failed to initialize TTS model")
                self._coqui_tts(text)
            else:
                logger.error(f"Selected TTS method '{method}' is not available")
                raise Exception("Selected TTS method is not available")

            # Process next in queue if any
            if self.speech_queue and callback:
                next_text = self.speech_queue.pop(0)
                logger.debug("Processing next item in speech queue")
                QTimer.singleShot(500, lambda: self.text_to_speech(next_text, method, callback))
            else:
                self.is_speaking = False
                # Update UI indicator
                if self.parent:
                    try:
                        self.parent.speaking_indicator.setText("TTS Ready")
                        self.parent.stop_button.setEnabled(False)
                    except (ReferenceError, RuntimeError):
                        pass
                if callback:
                    callback()
                logger.info("TTS completed successfully")

            return True

        except Exception as e:
            self.is_speaking = False
            # Update UI indicator on error
            if self.parent:
                try:
                    self.parent.speaking_indicator.setText("TTS Error")
                    self.parent.stop_button.setEnabled(False)
                except (ReferenceError, RuntimeError):
                    pass

            # Enhanced error logging for character encoding issues
            if "charmap" in str(e):
                logger.error(f"Character encoding error in TTS.")
                logger.error(f"Original text: {repr(original_text)}")
                logger.error(f"Sanitized text: {repr(text)}")
                logger.error(f"Error details: {str(e)}")
            else:
                logger.error(f"TTS error: {str(e)}")

            if callback:
                callback(error=str(e))
            return False

    def _coqui_tts(self, text):
        """Internal method to handle Coqui TTS"""
        file_path = os.path.join(self.output_dir, "output.wav")
        logger.debug(f"Generating TTS audio file: {file_path}")
        try:
            if self.tts_model is None:
                logger.error("TTS model not initialized")
                raise Exception("TTS model not initialized")

            self.tts_model.tts_to_file(text, file_path=file_path)
            logger.debug("Audio file generated, playing...")
            subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path],
                         check=True,
                         stderr=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error("Failed to play audio file")
            raise Exception("Failed to play audio file")
        except Exception as e:
            logger.error(f"Failed to use Coqui TTS: {str(e)}")
            raise Exception(f"Failed to use Coqui TTS: {str(e)}")
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug("Cleaned up temporary audio file")
                except:
                    logger.warning(f"Failed to remove temporary file: {file_path}")
                    pass

    def stop_speaking(self):
        """Stop current TTS output"""
        logger.info("Stopping TTS output")
        self.is_speaking = False
        self.speech_queue.clear()

        # Update UI indicator if parent exists
        if self.parent:
            try:
                self.parent.speaking_indicator.setText("TTS Stopped")
                self.parent.stop_button.setEnabled(False)
            except (ReferenceError, RuntimeError):
                pass  # Parent widget has been deleted

        if hasattr(self, "engine") and self.engine:
            try:
                self.engine.stop()
                logger.debug("TTS engine stopped")
            except:
                logger.warning("Failed to stop TTS engine")
                pass

    def __del__(self):
        """Cleanup resources"""
        logger.debug("Cleaning up SpeechHandler resources")
        try:
            self.stop_speaking()
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    try:
                        os.remove(os.path.join(self.output_dir, file))
                    except:
                        pass
                try:
                    os.rmdir(self.output_dir)
                    logger.debug(f"Removed temporary directory: {self.output_dir}")
                except:
                    logger.warning(f"Failed to remove temporary directory: {self.output_dir}")
        except:
            pass

    def start_listening(self, duration=5, callback=None):
        """Records audio and converts it to text using the Whisper model"""
        if not STT_AVAILABLE:
            logger.error("Speech-to-Text is not available")
            if callback:
                callback(error="Speech-to-Text is not available. Please install whisper and sounddevice.")
            return False

        try:
            samplerate = 16000
            filename = "stt_record.wav"
            logger.info(f"Starting audio recording (duration: {duration}s)")

            if callback:
                callback(status="Listening...")

            # Record audio
            logger.debug("Recording audio...")
            audio_data = sd.rec(
                int(samplerate * duration),
                samplerate=samplerate,
                channels=1,
                dtype=np.int16,
            )
            sd.wait()

            # Save to WAV file
            logger.debug(f"Saving audio to {filename}")
            with wave.open(filename, "wb") as wavefile:
                wavefile.setnchannels(1)
                wavefile.setsampwidth(2)
                wavefile.setframerate(samplerate)
                wavefile.writeframes(audio_data.tobytes())

            if callback:
                callback(status="Processing speech...")

            # Load model only when needed
            global WHISPER_MODEL
            if WHISPER_MODEL is None:
                if callback:
                    callback(status="Loading Whisper model (first time only)...")
                logger.info("Loading Whisper model (first time)")
                WHISPER_MODEL = whisper.load_model("base")
                logger.info("Whisper model loaded successfully")

            # Transcribe
            logger.debug("Transcribing audio...")
            result = WHISPER_MODEL.transcribe(filename)
            transcribed_text = result["text"].strip()

            if transcribed_text:
                logger.info("Speech transcription successful")
                logger.debug(f"Transcribed text: {transcribed_text}")
                if callback:
                    callback(text=transcribed_text)
            else:
                logger.warning("No speech detected in audio")
                if callback:
                    callback(error="No speech detected.")

            return True

        except Exception as e:
            logger.error(f"Error during speech recognition: {str(e)}")
            if callback:
                callback(error=f"Error during speech recognition: {str(e)}")
            return False
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    logger.debug(f"Removed temporary file: {filename}")
                except:
                    logger.warning(f"Failed to remove temporary file: {filename}")
                    pass
