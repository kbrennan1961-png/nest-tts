#!/usr/bin/env python3
"""CLI for nest-tts."""
import argparse
import sys

from nest_tts import speak, list_speakers


def main():
    p = argparse.ArgumentParser(description="TTS playback on a Google Nest/Chromecast speaker")
    p.add_argument("text", nargs="*", help="text to speak (or read from stdin)")
    p.add_argument("--speaker", default=None, help="device name (default: first Nest/Speaker found)")
    p.add_argument("--list", action="store_true", help="list discovered speakers and exit")
    p.add_argument("--lang", default="en")
    p.add_argument("--volume", type=float, default=0.4)
    p.add_argument("--host-ip", default=None)
    p.add_argument("--port", type=int, default=8788)
    p.add_argument("--serve-dir", default=None)
    args = p.parse_args()

    if args.list:
        print("\n".join(list_speakers()))
        return

    text = " ".join(args.text).strip()
    if not text:
        text = sys.stdin.read().strip()
    if not text:
        p.error("no text provided")

    result = speak(
        text,
        speaker=args.speaker,
        host_ip=args.host_ip,
        port=args.port,
        serve_dir=args.serve_dir,
        lang=args.lang,
        volume=args.volume,
    )
    print(result)


if __name__ == "__main__":
    main()
