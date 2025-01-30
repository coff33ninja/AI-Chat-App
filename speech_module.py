from PyQt6.QtCore import QTimer
import re
import os
import subprocess
import wave
import numpy as np

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
    import sounddevice as sd
    WHISPER_MODEL = None
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False


class SpeechHandler:
    def __init__(self, parent=None):
        self.parent = parent
        self.is_speaking = False
        self.speech_queue = []
        self.engine = None
        
    def get_available_tts_methods(self):
        """Returns a list of available TTS methods"""
        methods = []
        if PYTTSX3_AVAILABLE:
            methods.append("pyttsx3 (System)")
        if COQUI_TTS_AVAILABLE:
            methods.append("Coqui TTS (Local AI)")
        return methods

    def text_to_speech(self, text, method, callback=None):
        """Enhanced TTS function with visual feedback"""
        if not text or len(text.strip()) < 5:
            return False

        self.is_speaking = True
        
        # Clean the text
        text = re.sub(r"<.*?>", "", text).strip()

        try:
            if method == "pyttsx3 (System)" and PYTTSX3_AVAILABLE:
                self.engine = pyttsx3.init()
                self.engine.say(text)
                self.engine.runAndWait()
            elif method == "Coqui TTS (Local AI)" and COQUI_TTS_AVAILABLE:
                self._coqui_tts(text)
            else:
                raise Exception("Selected TTS method is not available")

            # Process next in queue if any
            if self.speech_queue and callback:
                next_text = self.speech_queue.pop(0)
                QTimer.singleShot(500, lambda: self.text_to_speech(next_text, method, callback))
            else:
                self.is_speaking = False
                if callback:
                    callback()

            return True

        except Exception as e:
            self.is_speaking = False
            if callback:
                callback(error=str(e))
            return False

    def _coqui_tts(self, text):
        """Internal method to handle Coqui TTS"""
        try:
            model = TTS("tts_models/en/ljspeech/glow-tts").to("cpu")
            file_path = "output.wav"
            model.tts_to_file(text, file_path=file_path)
            subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path])
            os.remove(file_path)
        except Exception as e:
            raise Exception(f"Failed to use Coqui TTS: {str(e)}")

    def stop_speaking(self):
        """Stop current TTS output"""
        self.is_speaking = False
        self.speech_queue.clear()
        if hasattr(self, 'engine') and self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def start_listening(self, duration=5, callback=None):
        """Records audio and converts it to text using the Whisper model"""
        if not STT_AVAILABLE:
            if callback:
                callback(error="Speech-to-Text is not available. Please install whisper and sounddevice.")
            return False

        try:
            samplerate = 16000
            filename = "stt_record.wav"

            if callback:
                callback(status="Listening...")

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

            if callback:
                callback(status="Processing speech...")

            # Load model only when needed
            global WHISPER_MODEL
            if WHISPER_MODEL is None:
                if callback:
                    callback(status="Loading Whisper model (first time only)...")
                WHISPER_MODEL = whisper.load_model("base")

            # Transcribe
            result = WHISPER_MODEL.transcribe(filename)
            transcribed_text = result["text"].strip()

            if transcribed_text:
                if callback:
                    callback(text=transcribed_text)
            else:
                if callback:
                    callback(error="No speech detected.")

            return True

        except Exception as e:
            if callback:
                callback(error=f"Error during speech recognition: {str(e)}")
            return False
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass