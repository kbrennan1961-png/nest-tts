"""Core logic for nest-tts."""
import http.server
import os
import socket
import threading
import time
import uuid
from pathlib import Path

try:
    import pychromecast
except ImportError as e:
    raise ImportError("pychromecast is required: pip install pychromecast") from e

try:
    from gtts import gTTS
except ImportError as e:
    raise ImportError("gTTS is required: pip install gTTS") from e


def _lan_ip():
    """Best-effort detection of this machine's LAN IP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def list_speakers(timeout=15):
    """Return a list of discovered Chromecast/Nest device names."""
    chromecasts, browser = pychromecast.get_chromecasts(timeout=timeout)
    names = [c.name for c in chromecasts]
    pychromecast.discovery.stop_discovery(browser)
    return names


def speak(
    text,
    speaker=None,
    host_ip=None,
    port=8788,
    serve_dir=None,
    lang="en",
    volume=0.4,
    timeout=15,
    tld="com",
):
    """Generate TTS for `text` and play it on a Nest/Chromecast speaker.

    Returns the path of the generated mp3 file.
    """
    if not text or not text.strip():
        raise ValueError("text must not be empty")

    if serve_dir is None:
        serve_dir = str(Path.home() / ".cache" / "nest-tts")
    serve_dir = os.path.abspath(serve_dir)
    os.makedirs(serve_dir, exist_ok=True)

    if host_ip is None:
        host_ip = _lan_ip()

    # Serve the directory on `port` in a background thread (if not already).
    _ensure_server(serve_dir, port)

    fname = f"tts_{uuid.uuid4().hex[:8]}.mp3"
    fpath = os.path.join(serve_dir, fname)
    gTTS(text=text, lang=lang, tld=tld).save(fpath)

    chromecasts, browser = pychromecast.get_chromecasts(timeout=timeout)
    if speaker is None:
        # default to first device containing "speaker"/"nest" or first available
        target = next(
            (c for c in chromecasts if "speaker" in c.name.lower() or "nest" in c.name.lower()),
            chromecasts[0] if chromecasts else None,
        )
    else:
        target = next((c for c in chromecasts if c.name == speaker), None)

    if target is None:
        pychromecast.discovery.stop_discovery(browser)
        raise RuntimeError(
            f"speaker {speaker!r} not found; available: {[c.name for c in chromecasts]}"
        )

    target.wait()
    try:
        target.quit_app()
        time.sleep(2)
    except Exception:
        pass
    target.set_volume(volume)
    time.sleep(0.5)
    mc = target.media_controller
    url = f"http://{host_ip}:{port}/{fname}"
    mc.play_media(url, "audio/mpeg", title="nest-tts")
    time.sleep(3)
    state = getattr(mc.status, "player_state", None)
    pychromecast.discovery.stop_discovery(browser)
    return {"file": fpath, "url": url, "state": state}


_server_started = set()


def _ensure_server(directory, port):
    """Start a daemon thread serving `directory` on `port` if not already."""
    key = (directory, port)
    if key in _server_started:
        return
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=directory, **kw)
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    _server_started.add(key)
    time.sleep(0.3)
