import io
import pyaudio
import requests
import threading
import wave


class TtsServerAudio():
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()
        self.thread = threading.Thread()
    
    def play(self, wav_bytes: bytearray) -> None:
        with wave.open(io.BytesIO(wav_bytes), 'rb') as f:
            rate = f.getframerate()
            width = f.getsampwidth()
            channels = f.getnchannels()
        
        stream = self.audio.open(
            rate=rate,
            channels=channels,
            format=pyaudio.get_format_from_width(width),
            output=True,
            frames_per_buffer=2048)
        
        stream.write(wav_bytes)

    def async_play(self, wav_bytes: bytearray) -> None:
        self.thread = threading.Thread(target=self.play, args=(wav_bytes,))
        self.thread.start()
