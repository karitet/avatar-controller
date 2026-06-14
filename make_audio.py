#!/usr/bin/env python3
"""
make_audio.py — generate the 7 command cues as audio files.

Two engines:
  elevenlabs  (default) — high-quality, the voice for the finished work
  espeak      — offline robotic placeholder (no network, no key)

Output: audio/<lang>/<command>.mp3   (forward, backward, left, right, stop, shoot, pickup)

Examples
--------
# Offline placeholder set (needs espeak-ng + ffmpeg installed):
python3 make_audio.py --engine espeak --langs da en

# Final voice via ElevenLabs (needs: pip install requests, and an API key):
export ELEVENLABS_API_KEY=sk_...
python3 make_audio.py --engine elevenlabs --voice <VOICE_ID> --langs da

To re-voice or add a language, edit WORDS below and re-run. Nothing else changes —
index.html reads audio/<lang>/<command>.mp3 by filename.
"""
import argparse, json, os, subprocess, sys, urllib.request

# command -> spoken phrase per language. Add a language by adding a block.
WORDS = {
    "da": {"forward": "frem", "backward": "tilbage", "left": "venstre",
           "right": "højre", "stop": "stop", "shoot": "skyd", "pickup": "saml op"},
    "en": {"forward": "forward", "backward": "backward", "left": "left",
           "right": "right", "stop": "stop", "shoot": "shoot", "pickup": "pick up"},
}
ESPEAK_VOICE = {"da": "da", "en": "en-us"}  # espeak-ng voice ids


def out_path(lang, cmd):
    d = os.path.join("audio", lang)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, cmd + ".mp3")


def gen_espeak(lang, cmd, text):
    voice = ESPEAK_VOICE.get(lang, lang)
    mp3 = out_path(lang, cmd)
    wav = mp3[:-4] + ".wav"
    subprocess.run(["espeak-ng", "-v", voice, "-s", "150", "-w", wav, text], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-ac", "1", "-ar", "44100", "-b:a", "96k", mp3], check=True)
    os.remove(wav)


def gen_elevenlabs(lang, cmd, text, voice_id, api_key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg",
    })
    with urllib.request.urlopen(req) as r:
        data = r.read()
    with open(out_path(lang, cmd), "wb") as f:
        f.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["elevenlabs", "espeak"], default="elevenlabs")
    ap.add_argument("--langs", nargs="+", default=["da", "en"])
    ap.add_argument("--voice", help="ElevenLabs voice id")
    args = ap.parse_args()

    if args.engine == "elevenlabs":
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key or not args.voice:
            sys.exit("Set ELEVENLABS_API_KEY and pass --voice <VOICE_ID>.")

    for lang in args.langs:
        if lang not in WORDS:
            print(f"skip {lang}: no words defined", file=sys.stderr); continue
        for cmd, text in WORDS[lang].items():
            if args.engine == "espeak":
                gen_espeak(lang, cmd, text)
            else:
                gen_elevenlabs(lang, cmd, text, args.voice, key)
            print(f"  {lang}/{cmd}.mp3  ←  “{text}”")
    print("done.")


if __name__ == "__main__":
    main()
