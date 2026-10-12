# كيفن للكوكيز · Kevin Cookie Company

A 90‑second motion‑graphics film in Egyptian Arabic, written for parents. Open `index.html` in a browser.

## Files
- `index.html`: the film and its player, in one self-contained page.
- `narration.ar.srt`: the narration script with timestamps. Use it to record a voice-over or to add subtitles in a video editor.

## How it works
Every visual is driven by one clock, so the scenes always match the subtitle timestamps when you play, pause or scrub.

| Time | Scene | Technique |
|---|---|---|
| 0:00 | المقدمة | Title fade + 2 s rise, falling chocolate chips, title shadow, slow zoom |
| 0:07 | ولادكم أولاً | Animated typography |
| 0:14 | المكونات | Self-drawing icons |
| 0:23 | من غير إضافات | Product callouts |
| 0:31 | رحلة الخَبز | Process diagram |
| 0:41 | سكر أقل | Bar chart |
| 0:48 | طاقة الفُسحة | Infographic |
| 0:56 | حكايتنا | Timeline |
| 1:06 | النكهات | Product visuals |
| 1:14 | رأي الأهالي | Pictogram + counter |
| 1:21 | الختام | Title, tagline, call to action |

## Narration
- **Your own recording:** record the lines in `narration.ar.srt` at those times, then load the file with «ملف التعليق». The film then follows the audio's clock.
- **Rough preview voice:** «صوت تجريبي» reads each line with the device's Arabic text-to-speech voice, if one is installed.

## Exporting to video
The page exposes `kevinFilm.pause()` and `kevinFilm.seek(seconds)`. You can step through it frame by frame with a headless browser (for example, Playwright at 30 fps) and join the frames with ffmpeg.

> The figures in the film (sugar −30%, 50,000 homes, 98% survey, nutrition values) are placeholders for the story. Replace them with the company's real numbers before publishing.
