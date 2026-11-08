# nest-tts

Text-to-speech playback on Google Nest / Chromecast speakers from Python.

Self-contained: generates an MP3 with gTTS, serves it over HTTP from this
machine, and casts it to a Nest/Chromecast device via pychromecast.

## Install
```
pip install -r requirements.txt
```
(Requires Python 3.9+ and a LAN connection to the speaker.)

## CLI
```
nest-tts "Hello from the mini PC"
nest-tts --list                       # discover speakers
nest-tts --speaker "Kitchen Speaker" "dinner is ready"
echo "hi" | nest-tts
```

## Library
```python
from nest_tts import speak, list_speakers
print(list_speakers())
speak("Hello world", speaker="Kitchen Speaker", volume=0.4)
```

## Configuration
- `--host-ip` / `host_ip=` — LAN IP of this machine (auto-detected)
- `--port` / `port=` — HTTP port (default 8788)
- `--serve-dir` / `serve_dir=` — where MP3s are stored/served
- `--lang`, `--volume`

## Notes
The Cast device fetches the audio over HTTP from this machine, so the
machine must be reachable on the LAN and a free port must be available.
The HTTP server is started in a background thread automatically.
