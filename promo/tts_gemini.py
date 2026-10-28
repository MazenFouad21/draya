"""Generate the Dirayah promo voice-over with Google AI Studio (Gemini TTS).

Voice only: no music, no effects. One clip per line, so the video can sync each scene to it.

    export GEMINI_API_KEY=...        # from https://aistudio.google.com/apikey
    python3 tts_gemini.py            # writes audio/b1.wav … audio/b12.wav
    node render.js                   # renders out/dirayah-promo.mp4 with the VO

Optional: VOICE=Charon python3 tts_gemini.py  /  MODEL=gemini-2.5-pro-preview-tts python3 tts_gemini.py
"""
import base64, json, os, sys, time, urllib.request, wave

DIR = os.path.dirname(os.path.abspath(__file__))
script = json.load(open(os.path.join(DIR, "script.json"), encoding="utf-8"))
KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
MODEL = os.environ.get("MODEL", script["model"])
VOICE = os.environ.get("VOICE", script["voice"])
if not KEY:
    sys.exit("Set GEMINI_API_KEY (Google AI Studio → Get API key).")

os.makedirs(os.path.join(DIR, "audio"), exist_ok=True)
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def tts(text):
    body = {
        "contents": [{"parts": [{"text": f"{script['style']}\n\nقول الجملة دي بس:\n{text}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
            return base64.b64decode(part["data"])  # 16-bit PCM, 24 kHz, mono
        except Exception as e:  # rate limits / transient errors
            if attempt == 3:
                raise
            print("  retry:", e)
            time.sleep(2 ** (attempt + 1))

for b in script["beats"]:
    out = os.path.join(DIR, "audio", b["id"] + ".wav")
    if os.path.exists(out) and "--force" not in sys.argv:
        print("skip", b["id"]); continue
    print(b["id"], b["text"])
    pcm = tts(b["text"])
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)

print("Done → audio/. Now run: node render.js")
