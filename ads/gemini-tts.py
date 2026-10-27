# Voices the ad with Google Gemini text-to-speech (the engine behind AI Studio's TTS)
# and mixes it onto youth-ad.mp4, each line starting on its scene.
# Usage: GEMINI_API_KEY=... python3 ads/gemini-tts.py [--voice Puck] [--music 0.25]
#   -> ads/voiceover-gemini.wav and ads/youth-ad-vo.mp4
import argparse, base64, json, os, ssl, subprocess, urllib.request, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 24000  # Gemini TTS returns 24 kHz 16-bit mono PCM
STYLE = ("Read this in Egyptian Arabic (Cairo dialect), like a young Egyptian guy "
         "in an energetic TikTok ad, natural and friendly, not formal: ")
PARENTS_STYLE = ("Read this in Egyptian Arabic (Cairo dialect), warm and reassuring, "
                 "like a respectful young man talking to parents: ")

# (scene start in seconds, style, line) — timings match youth-ad.html
LINES = [
    (0.2, STYLE, "تسع ساعات على الموبايل؟!"),
    (2.9, STYLE, "طب ما تعمل لعبتك إنت!"),
    (5.7, STYLE, "من واحد بيلعب… لواحد بيبرمج!"),
    (9.0, STYLE, "هتعمل لعبتك… تبني موقعك!"),
    (13.5, PARENTS_STYLE, "يا بابا يا ماما… كورس البرمجة في نادي بهجة المسائي!"),
    (22.1, STYLE, "الأماكن محدودة… سجّل دلوقتي… ويلا بينا!"),
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
    with urllib.request.urlopen(req, context=ssl_ctx(), timeout=120) as r:
        data = json.load(r)
    pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    audio = np.frombuffer(pcm, dtype='<i2').astype(np.float32) / 32768
    # trim leading/trailing silence so each line lands exactly on its cue
    loud = np.flatnonzero(np.abs(audio) > 0.02)
    return audio[loud[0]:loud[-1] + 1] if len(loud) else audio

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voice', default='Puck', help='Gemini voice: Puck, Fenrir, Charon, Orus, Kore…')
    ap.add_argument('--model', default='gemini-2.5-flash-preview-tts')
    ap.add_argument('--music', type=float, default=0.25, help='music volume under the voice (0–1)')
    args = ap.parse_args()
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not key:
        raise SystemExit('Set GEMINI_API_KEY (get one free at https://aistudio.google.com/apikey)')

    track = np.zeros(int(27 * SR), dtype=np.float32)
    cursor = 0.0
    for start, style, line in LINES:
        clip = tts(style + line, args.voice, args.model, key)
        at = max(start, cursor + 0.15)  # never overlap the previous line
        i = int(at * SR)
        clip = clip[: len(track) - i]
        track[i:i + len(clip)] += clip
        cursor = at + len(clip) / SR
        print(f'{at:5.2f}s → {cursor:5.2f}s  {line}')
    track /= max(1e-6, np.abs(track).max()) / 0.95

    vo = os.path.join(HERE, 'voiceover-gemini.wav')
    with wave.open(vo, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype('<i2').tobytes())

    out = os.path.join(HERE, 'youth-ad-vo.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(HERE, 'youth-ad.mp4'), '-i', vo,
                    '-filter_complex',
                    f'[0:a]volume={args.music}[m];[1:a]aresample=44100[v];[m][v]amix=inputs=2:duration=first:normalize=0[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print('wrote', vo, 'and', out)

if __name__ == '__main__':
    main()
