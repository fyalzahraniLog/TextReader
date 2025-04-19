import pygame
import edge_tts
import asyncio
import tempfile
import os
from threading import Thread

class TextToSpeech:
    def __init__(self):
        pygame.mixer.init()
        self.active_file = None
        self.voice = "en-US-ChristopherNeural"
        self.speed = 1.0
        self.volume = 50  # 0-100, 50 = Edge TTS +0%
        self.playing = False

    def _speed_to_rate(self, speed):
        speed = max(0.5, min(2.0, speed))
        rate = int((speed - 1.0) * 100)
        rate = max(-90, min(100, rate))
        return f"+{rate}%" if rate >= 0 else f"{rate}%"

    def _volume_to_edge(self, volume):
        edge_volume = int((volume - 50) * 2)
        edge_volume = max(-100, min(100, edge_volume))
        return f"+{edge_volume}%" if edge_volume >= 0 else f"{edge_volume}%"

    async def _edge_tts(self, text):
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self._speed_to_rate(self.speed),
            volume=self._volume_to_edge(self.volume)
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
            return f.name

    def _play_audio(self, file_path):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.playing = True
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            self.playing = False
            self._cleanup()

    def convert(self, text, lang='en'):
        if self.playing:
            self.stop()
        if not text.strip():
            return

        def run_tts():
            try:
                self.voice = "ar-SA-HamedNeural" if lang == 'ar' else "en-US-ChristopherNeural"
                file_path = asyncio.run(self._edge_tts(text))
                self.active_file = file_path
                self._play_audio(file_path)
            except Exception as e:
                print(f"[TTS Error] {e}")
                self._cleanup()

        Thread(target=run_tts, daemon=True).start()

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
