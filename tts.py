import pygame
import tempfile
from gtts import gTTS
import os

class TextToSpeech:
    def __init__(self):
        pygame.mixer.init()
        self.active_file = None

    def convert(self, text, lang='en'):
        self.stop()
        if not text.strip():
            return

        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                self.active_file = f.name
            
            pygame.mixer.music.load(self.active_file)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"TTS Error: {e}")
            self._cleanup()

    def stop(self):
        pygame.mixer.music.stop()
        self._cleanup()

    def _cleanup(self):
        if self.active_file and os.path.exists(self.active_file):
            try:
                os.remove(self.active_file)
            except:
                pass
            self.active_file = None

tts = TextToSpeech()