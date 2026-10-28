# Voices the ad with Google Gemini text-to-speech (the engine behind AI Studio's TTS)
# and mixes it onto youth-ad.mp4 (sound effects only, no music), each line starting on its scene.
# Usage: GEMINI_API_KEY=... python3 ads/gemini-tts.py [--voice Puck] [--sfx 0.5] [--reuse]
#   -> ads/voiceover-gemini.wav and ads/youth-ad-vo.mp4
import argparse, base64, json, os, ssl, subprocess, time, urllib.error, urllib.request, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 24000  # Gemini TTS returns 24 kHz 16-bit mono PCM
# (scene start in seconds, line) — timings match youth-ad.html
LINES = [
    (0.2, "تسع ساعات على الموبايل؟!"),
    (2.9, "طب ما تعمل لعبتك إنت!"),
    (5.7, "من واحد بيلعب… لواحد بيبرمج!"),
    (9.0, "هتعمل لعبتك… تبني موقعك!"),
    (13.5, "يا بابا يا ماما… كورس البرمجة في نادي بهجة المسائي!"),
    (22.1, "الأماكن محدودة… سجّل دلوقتي… ويلا بينا!"),
]

def ssl_ctx():
    for f in (os.environ.get('SSL_CERT_FILE'), os.environ.get('REQUESTS_CA_BUNDLE'), '/root/.ccr/ca-bundle.crt'):
        if f and os.path.exists(f):
            return ssl.create_default_context(cafile=f)
    return ssl.create_default_context()

def tts(text, voice, model, key):
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, context=ssl_ctx(), timeout=120) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors='replace')
            if e.code != 429 or 'PerDay' in detail or attempt == 5:
                raise SystemExit(f'Gemini API error {e.code}: {detail[:500]}')
            time.sleep(20 * (attempt + 1))  # free tier allows only a few requests per minute
    pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    audio = np.frombuffer(pcm, dtype='<i2').astype(np.float32) / 32768
    # trim leading/trailing silence so each line lands exactly on its cue
    loud = np.flatnonzero(np.abs(audio) > 0.02)
    return audio[loud[0]:loud[-1] + 1] if len(loud) else audio

SCRIPT_STYLE = ("Read this ad script in Egyptian Arabic (Cairo dialect), like a young Egyptian guy "
                "in an energetic TikTok ad, natural and friendly, not formal. Make the line to the parents "
                "(يا بابا يا ماما) warmer and calmer. Pause for a full second between lines:\n\n")

def split_on_pauses(audio, n):
    """Cut audio into n pieces at its n-1 longest silences."""
    hop = SR // 100
    frames = np.abs(audio[: len(audio) // hop * hop]).reshape(-1, hop).max(axis=1) < 0.02
    gaps, start = [], None
    for i, quiet in enumerate(np.append(frames, False)):
        if quiet and start is None:
            start = i
        elif not quiet and start is not None:
            if start > 0 and i < len(frames):  # ignore leading/trailing silence
                gaps.append((i - start, start, i))
            start = None
    cuts = sorted((s + e) // 2 * hop for _, s, e in sorted(gaps, reverse=True)[: n - 1])
    pieces = np.split(audio, cuts)
    if len(pieces) != n:
        raise SystemExit(f'Found {len(pieces)} lines in the audio, expected {n}; try again')
    out = []
    for p in pieces:
        loud = np.flatnonzero(np.abs(p) > 0.02)
        out.append(p[loud[0]:loud[-1] + 1] if len(loud) else p)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voice', default='Puck', help='Gemini voice: Puck, Fenrir, Charon, Orus, Kore…')
    # 3.1 and 2.5-flash follow the style instruction; 3.8 reads it aloud and 2.5-pro has no free tier
    ap.add_argument('--model', default='gemini-3.1-flash-tts-preview')
    ap.add_argument('--sfx', type=float, default=0.5, help='sound-effects volume under the voice (0–1)')
    ap.add_argument('--reuse', action='store_true', help='remix the existing voiceover-gemini.wav without calling Gemini')
    args = ap.parse_args()
    vo = os.path.join(HERE, 'voiceover-gemini.wav')
    if not args.reuse:
        make_voice(args, vo)
    mix_video(vo, args.sfx)

def make_voice(args, vo):
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not key:
        raise SystemExit('Set GEMINI_API_KEY (get one free at https://aistudio.google.com/apikey)')

    # One request for the whole script (the free tier allows ~10 a day), then cut it
    # back into lines at its longest pauses.
    whole = tts(SCRIPT_STYLE + '\n\n'.join(line for _, line in LINES), args.voice, args.model, key)
    clips = split_on_pauses(whole, len(LINES))

    track = np.zeros(int(27 * SR), dtype=np.float32)
    cursor = 0.0
    for (start, line), clip in zip(LINES, clips):
        at = max(start, cursor + 0.15)  # never overlap the previous line
        i = min(int(at * SR), len(track))
        clip = clip[: len(track) - i]
        track[i:i + len(clip)] += clip
        cursor = at + len(clip) / SR
        print(f'{at:5.2f}s → {cursor:5.2f}s  {line}')
    track /= max(1e-6, np.abs(track).max()) / 0.95

    with wave.open(vo, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype('<i2').tobytes())

def mix_video(vo, sfx):
    out = os.path.join(HERE, 'youth-ad-vo.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(HERE, 'youth-ad.mp4'), '-i', vo,
                    '-filter_complex',
                    f'[0:a]volume={sfx}[m];[1:a]aresample=44100[v];[m][v]amix=inputs=2:duration=first:normalize=0[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print('wrote', out)

if __name__ == '__main__':
    main()
