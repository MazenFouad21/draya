"""Generate the LAT magazine (مجلة العلم والعمل) reel voice-over with Google AI Studio (Gemini TTS).

Voice only: no music, no effects.
By default the whole script is read in ONE request (one consistent take, and it fits the
free tier's ~10 requests/day), then split on the pauses into audio/b1.wav … audio/b11.wav
so every scene can sync to its line. Use --per-line for one request per line instead.

    export GEMINI_API_KEY=...        # from https://aistudio.google.com/apikey
    python3 tts_gemini.py            # writes audio/full.wav + audio/b1.wav … audio/b11.wav
    node render.js                   # renders out/lat-reel.mp4 with the VO

Optional: VOICE=Charon MODEL=gemini-2.5-pro-preview-tts python3 tts_gemini.py
"""
import base64, json, os, re, subprocess, sys, time, urllib.error, urllib.request, wave

DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(DIR, "audio")
script = json.load(open(os.path.join(DIR, "script.json"), encoding="utf-8"))
KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
MODEL = os.environ.get("MODEL", script["model"])
VOICE = os.environ.get("VOICE", script["voice"])
BEATS = script["beats"]
if not KEY:
    sys.exit("Set GEMINI_API_KEY (Google AI Studio → Get API key).")
os.makedirs(AUDIO, exist_ok=True)


def tts(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            return base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])  # PCM s16le 24 kHz mono
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code == 429:
                sys.exit("Quota exceeded for " + MODEL + ":\n" + msg[:600])
            if attempt == 3:
                sys.exit(f"HTTP {e.code}: {msg[:600]}")
        except (KeyError, IndexError):
            if attempt == 3:
                sys.exit("No audio in response: " + json.dumps(data, ensure_ascii=False)[:600])
        print("  retry", attempt + 1)
        time.sleep(2 ** (attempt + 1))


def write_wav(path, pcm):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)


def split_on_pauses(full):
    """Cut full.wav into len(BEATS) clips at the longest pauses between lines."""
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", full, "-af", "silencedetect=n=-40dB:d=0.18", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", full]))
    gaps = [(e - s, s, e) for s, e in zip(starts, ends) if s > 0.05 and e < total - 0.05]  # inner pauses only
    need = len(BEATS) - 1
    if len(gaps) < need:
        sys.exit(f"Found only {len(gaps)} pauses, need {need}. Re-run with --per-line.")
    cuts = sorted(sorted(gaps, reverse=True)[:need], key=lambda g: g[1])
    head = ends[0] if starts and starts[0] <= 0.05 else 0.0
    tail = starts[-1] if starts and ends[-1] >= total - 0.05 else total
    bounds = [head] + [x for _, s, e in cuts for x in (s, e)] + [tail]
    for i, b in enumerate(BEATS):
        s, e = bounds[2 * i], bounds[2 * i + 1]
        out = os.path.join(AUDIO, b["id"] + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, s - 0.04):.3f}", "-to", f"{e + 0.08:.3f}", "-i", full, out], check=True)
        print(f"  {b['id']}  {e - s:5.2f}s  {b['text']}")


if "--per-line" in sys.argv:
    for b in BEATS:
        out = os.path.join(AUDIO, b["id"] + ".wav")
        if os.path.exists(out) and "--force" not in sys.argv:
            print("skip", b["id"]); continue
        print(b["id"], b["text"])
        write_wav(out, tts(f"{script['style']}\n\nقول الجملة دي بس:\n{b['text']}"))
else:
    lines = "\n\n".join(b["text"] for b in BEATS)
    # Director's notes are for the voice, not to be spoken; only the TRANSCRIPT is read aloud.
    prompt = ("### DIRECTOR'S NOTES (do NOT read these aloud)\n"
              f"Style: {script['style']}\n"
              "Pacing: leave a clear pause of about one second between lines.\n\n"
              f"### TRANSCRIPT (read ONLY this, line by line)\n{lines}")
    full = os.path.join(AUDIO, "full.wav")
    print(f"Generating full take with {MODEL} / {VOICE} …")
    write_wav(full, tts(prompt))
    split_on_pauses(full)

print("Done → audio/. Now run: node render.js")
