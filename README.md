# Avatar Controller

A peer-to-peer pilot/avatar controller for *Avatar Controller Maze* (Jakob la Cour Studio).
One phone (the **pilot**) sends movement and action commands to another phone (the **avatar**),
which speaks them into the wearer's earphones. Built on plain web standards so it rots as slowly
as possible, and documented so it can be rebuilt from this file.

**Live:** https://karitet.github.io/avatar-controller/

## What's in this version (overview)

- **Pairing by a 6-digit code + QR.** The pilot shows a short numeric code and a QR. The avatar
  scans the QR with the phone camera (or types the code) and connects. Auto-retries if a code is taken.
- **Peer-to-peer commands.** Once paired, commands travel device-to-device over WebRTC (via PeerJS).
- **Voice cues from recorded files** with a speech-synthesis fallback. The wearer hears each command.
- **English only** right now (kept simple). The structure stays multilingual — easy to re-add languages.
- **Works in portrait and landscape.** The controller reflows: stacked upright, wide gamepad on its side.
  Nothing is force-locked or cropped. An optional **Fuldskærm** button is on the controller.
- **Installable PWA** with offline app + audio caching.

## The voice

The command cues were generated with **espeak-ng** (eSpeak NG) — a free, open-source, *offline*
text-to-speech engine (version 1.51), English voice `en-us`, then encoded to MP3 with ffmpeg.
Its slightly synthetic, machine-like character suits a piece about being remote-controlled, and
because it runs locally there's no account, API key, or external service to depend on.

Regenerate or extend the voice with one command:

```bash
# offline, same espeak voice (needs espeak-ng + ffmpeg):
python3 make_audio.py --engine espeak --langs en

# or a produced voice via ElevenLabs (needs an API key):
export ELEVENLABS_API_KEY=sk_...
python3 make_audio.py --engine elevenlabs --voice <VOICE_ID> --langs en
```

Add a language: add a row to `WORDS` in `make_audio.py`, run it, and add the language back to
`LANGS` in `index.html`. Nothing else changes.

## Durable vs perishable

- **Durable** (belongs on paper / in the publication): the concept, rules, mask, costume, and the
  command vocabulary below. If the code dies, the work rebuilds from this.
- **Perishable**: this code — one implementation, documented so a technical partner can replace it.

## Architecture

```
   PILOT device                                   AVATAR device
   (phone/tablet)                                 (phone in pocket + earphones)
   ┌──────────────┐      WebRTC data (P2P)         ┌──────────────┐
   │  joypad UI   │  ───── commands ──────────▶    │ speaks the    │
   │  + QR / code │                                │ instruction   │
   └──────────────┘                                └──────────────┘
          │                                               │
          └──── avatar scans the pilot's QR (or types the code) ───┘
                (a broker introduces them; commands stay P2P)
```

The only external dependency is the rendezvous broker that introduces the two devices
(PeerJS' public `0.peerjs.com` by default). It's replaceable: run your own one-line `peerjs-server`
and point `new Peer()` at it. Once connected, commands flow directly between the two phones.

## Command protocol

Pilot → avatar, JSON over the data channel:

```json
{ "t": "cmd", "c": "<command>", "ts": 1718323200000 }
```

`c` ∈ `forward, backward, left, right, stop, shoot, pickup`. `ts` = sender epoch-ms.
The pilot also sends `{ "t": "lang", "l": "en" }` on connect so the avatar speaks the right language.

On receipt the avatar plays `audio/<lang>/<command>.mp3` (falling back to speech synthesis) and buzzes.

## Run / test locally

WebRTC, the camera, and service workers need a secure context (`https://` or `localhost`).

```bash
cd avatar-controller
python3 -m http.server 8000
# open http://localhost:8000 in two tabs/devices
```

Quick desktop check: open as **Pilot**, note the code, open a second tab as **Avatar**, enter the
code → **Forbind** → **Tryk når du er klar** → press a button in the pilot tab; the avatar tab speaks it.
Phone-to-phone QR scanning needs the `https` deploy below.

## Deploy

Static-host the folder (GitHub Pages, Netlify, …) — files never change, hosting is near-eternal.
Put a QR to the URL in the publication. Anyone can fork and self-host their own instance.

## Harden before live performance

- **TURN server** for restrictive Wi-Fi where direct P2P fails (e.g. coturn).
- **Self-host the PeerJS broker** so pairing doesn't depend on a public service.
- **Reconnect logic** if a device drops mid-game.
- **Live voice** option: a WebRTC audio track so the pilot can speak directly to the earpiece.

## Files

| file                    | role                                              |
|-------------------------|---------------------------------------------------|
| `index.html`            | the whole app — pilot + avatar, UI, WebRTC, QR    |
| `vendor/peerjs.min.js`  | WebRTC signaling + data channel (MIT)             |
| `vendor/qrcode.js`      | QR generation (MIT)                               |
| `audio/<lang>/*.mp3`    | command cues (espeak-ng voice — replaceable)      |
| `make_audio.py`         | regenerate cues (espeak or ElevenLabs)            |
| `manifest.webmanifest`  | installable as a PWA                              |
| `sw.js`                 | offline cache of app + audio                      |
| `icon.svg`              | the green aperture-cube mark                      |
