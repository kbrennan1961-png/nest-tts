# nest-tts

Text-to-speech playback on Google Nest / Chromecast speakers from Python.

Self-contained: generates an MP3 with gTTS, serves it over HTTP from this
machine, and casts it to a Nest/Chromecast device via pychromecast.

Originally built to let an AI agent (Hermes) speak aloud on a Kitchen Nest Mini
via a small HTTP server; packaged here so anyone can reuse it.

## Install
```bash
pip install -r requirements.txt
# or
pip install .
```
Requires Python 3.9+, gTTS, pychromecast, and a LAN connection to the speaker.

## Discover speakers
```bash
nest-tts --list
```

## CLI
```bash
nest-tts "Hello from the mini PC"
nest-tts --speaker "Kitchen Speaker" "dinner is ready"
nest-tts --volume 0.3 --lang en "quiet message"
echo "hi" | nest-tts
```

## Library
```python
from nest_tts import speak, list_speakers

print(list_speakers())
result = speak("Hello world", speaker="Kitchen Speaker", volume=0.4)
print(result)  # {"file": ..., "url": ..., "state": ...}
```

## Configuration
| Option | Default | Notes |
|---|---|---|
| `speaker` | first Nest/Speaker found | exact device name from `--list` |
| `host_ip` | auto-detected LAN IP | must be reachable by the Cast device |
| `port` | 8788 | HTTP port serving the MP3 |
| `serve_dir` | `~/.cache/nest-tts` | where MP3s are stored/served |
| `lang` | `en` | gTTS language code |
| `volume` | 0.4 | 0.0–1.0 |
| `tld` | `com` | gTTS TLD for accent variant |

## How it works
1. gTTS synthesizes the text to an MP3 in `serve_dir`.
2. A background `ThreadingHTTPServer` serves `serve_dir` on `port`.
3. pychromecast discovers the target device, quits any running app, sets
   volume, and plays the MP3 URL.

The Cast device fetches the audio over HTTP from this machine, so the
machine must be on the same LAN and the port must be free/reachable.

## Run as a service (optional)
If you prefer a persistent server (e.g. systemd) instead of the built-in
thread, point it at `serve_dir` on `port` and pass `serve_dir`/`port` to
`speak()`.

## Troubleshooting
- "speaker not found": run `nest-tts --list`; names must match exactly.
- No audio: check firewall allows inbound on `port`; verify `host_ip` is the
  LAN IP, not 127.0.0.1.
- `pychromecast` import errors: install into the same Python you run with.

## License
MIT
