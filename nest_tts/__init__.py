"""nest-tts: Text-to-speech playback on Google Nest / Chromecast speakers."""

from .core import speak, list_speakers

__all__ = ["speak", "list_speakers"]
__version__ = "0.1.0"
