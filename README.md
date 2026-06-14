# Avatar Controller — system & protocol

A peer-to-peer pilot/avatar controller for *Avatar Controller Maze* (Jakob la Cour Studio).
A working reference, built on plain web standards so it rots as slowly as possible and can be
rebuilt from the spec below.

## The principle: durable vs perishable

- **Durable** (lives on paper / in the publication): the concept, the rules, the mask and
  costume, and the command vocabulary below. If the code dies, the work rebuilds from this.
- **Perishable** (this code): one implementation. Documented so a technical partner can replace it.

## Architecture

```
   PILOT device                                   AVATAR device
   (phone/tablet)                                 (phone in pocket + earphones)
   ┌──────────────┐      WebRTC data (P2P)         ┌──────────────┐
   │  joypad UI   │  ───── commands ──────────▶    │ speaks / plays│
   │  + QR pair   │                                │ the cue       │
   └──────────────┘                                └──────────────┘
          │                                               │
          └──── pairing: avatar scans pilot's QR ─────────┘
                (broker sets up the call; commands stay P2P)
```

- **Transport:** WebRTC data channel (via PeerJS), device-to-device. Command traffic is not relayed.
- **Pairing:** the pilot shows a QR code that is a deep link (`…/?join=<peerId>`). The avatar
  scans it with the phone camera, the app opens already connecting. Manual code entry is the fallback.
- **No app store, no build step.** Two small vendored libraries (PeerJS, qrcode-generator) ship in `vendor/`.

### The one external dependency, and how to remove it

Pairing needs a rendezvous point. By default PeerJS uses its public broker (`0.peerjs.com`).
That is the only thing here you don't control. It is replaceable: run your own one-line
`peerjs-server` (npm) and point `new Peer(id, {host, port})` at it. The broker only introduces
the two devices — once connected, commands flow directly between them.

## Command protocol

Pilot → avatar, JSON over the data channel:

```json
{ "t": "cmd", "c": "<command>", "ts": 1718323200000 }
```

`c` ∈ `forward, backward, left, right, stop, shoot, pickup`. `ts` = sender epoch-ms.

On receipt the avatar device plays `audio/<lang>/<command>.mp3` (falling back to the browser's
speech synthesis if a file is missing) and buzzes. Spoken words per language:

| command  | da        | en        |
|----------|-----------|-----------|
| forward  | frem      | forward   |
| backward | tilbage   | backward  |
| left     | venstre   | left      |
| right    | højre     | right     |
| stop     | stop      | stop      |
| shoot    | skyd      | shoot     |
| pickup   | saml op   | pick up   |

## Audio

The cues in `audio/da` and `audio/en` are **placeholders** generated offline with espeak-ng —
robotic on purpose. Replace them with a real voice for the finished work; browser TTS quality
(especially Danish on iOS) is inconsistent and not yours to control.

`make_audio.py` regenerates the whole set from one word list:

```bash
# offline placeholders (needs espeak-ng + ffmpeg):
python3 make_audio.py --engine espeak --langs da en

# final voice via ElevenLabs (needs an API key):
export ELEVENLABS_API_KEY=sk_...
python3 make_audio.py --engine elevenlabs --voice <VOICE_ID> --langs da en
```

Add a language or change a word: edit `WORDS` in `make_audio.py`, re-run. The app needs no change.

## Run / test locally

WebRTC, the camera, and service workers need a secure context (`https://` or `localhost`).

```bash
cd avatar-controller
python3 -m http.server 8000
# open http://localhost:8000 on two devices/tabs
```

Pilot on one device shows a QR. Avatar scans it (or enters the code) → hears commands.
For phone-to-phone scanning you need an `https` URL (deploy first, below).

## Deploy (for a release)

Static host the folder — files never change, hosting is near-eternal and free: GitHub Pages,
Netlify, Codeberg Pages, an institution's web space. Put a QR to that URL in the publication.
Anyone can fork and self-host their own instance.

## Harden before live performance

- **TURN server** for restrictive Wi-Fi where direct P2P fails (e.g. coturn).
- **Self-host the PeerJS broker** so pairing doesn't depend on a public service.
- **Reconnect logic** if a device drops mid-game.
- **Live voice** option: a WebRTC audio track so the pilot can speak directly to the earpiece.

## Files

| file                    | role                                                  |
|-------------------------|-------------------------------------------------------|
| `index.html`            | the whole app — pilot + avatar, UI, WebRTC, QR        |
| `vendor/peerjs.min.js`  | WebRTC signaling + data channel (MIT)                 |
| `vendor/qrcode.js`      | QR generation (MIT)                                   |
| `audio/<lang>/*.mp3`    | command cues (placeholder voice — replace)            |
| `make_audio.py`         | regenerate cues (ElevenLabs or espeak)                |
| `manifest.webmanifest`  | installable as a PWA                                  |
| `sw.js`                 | offline cache of app + audio                          |
| `icon.svg`              | the green aperture-cube mark                          |
