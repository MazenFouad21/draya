# Dirayah design system: "Bookcloth & gold"

Dirayah is a teacher-led Quran lesson deck for kids' classes, filled with lesson data by n8n.
It runs on a classroom projector first, and must also work on tablets and phones.

## Idea
The deep emerald cloth and gold foil of a Mushaf binding form the frame: top bar, sidebar and the
cover slide. The lesson stage stays bright so it projects well in a lit room. The colors of Mushaf
tajweed coding mark the lesson's parts and the quiz answers.

## Color (tokens on `:root` in `dirayah-template.html`)
| Role | Token | Value |
|---|---|---|
| Binding (chrome, cover) | `--bind` / `--bind-2` / `--bind-3` | `#0F3D2E` / `#164B39` / `#1E5C47` |
| Gold foil (rewards, current item, focus) | `--gold` / `--gold-2` | `#C9973A` / `#E2B962` |
| Stage ground / card | `--paper` / `--card` | `#F3F6F3` / `#FFFFFF` |
| Ink / muted / faint | `--ink` / `--muted` / `--faint` | `#12231C` / `#53665C` / `#8A9B92` |
| Primary action, emphasis | `--em` / `--em-700` | `#127A55` / `#0C5E41` |
| Part and answer accents | `--crimson` `--blue` `--amber` `--violet` `--cyan` | tajweed-coded |

The older names (`--teal`, `--lime`, `--purple`, and so on) are aliases so that inline styles and n8n content keep working.
Gold text sits only on the binding. On the stage, gold is used for fills and rules.

## Type
- Display (slide titles, numbers, the timer): **Reem Kufi** 500–700, a Kufic voice from early Mushaf script.
- UI and body: **Readex Pro** 300–700, with tabular numerals for scores.
- Quran text: **Amiri Quran**. Never substitute another face.
- English helper lines (`.eng`) are quiet LTR text, with no box or border.

## Motifs
- An 8-point star (two squares rotated 45°) for the logo, the cover medallion, objective numbers and timeline dots.
- Ayah numbers use the gold `﴿١﴾` end mark.
- No eyebrow or kicker labels above headings. Ayah ranges for each part appear as a colored seal (`.seal`).

## Components
- Buttons: `.btn` is emerald, `.btn.green` is the gold call to action, `.btn.ghost` is outlined. Radius 14px, soft blurred shadow, no hard offset shadow.
- Cards: white, 1px `--line` border, radius 20px, two-layer blurred shadow.
- Icons: the inline SVG sprite at the top of `<body>`, rendered with `ic(name)` in JS (1.9 stroke). No emoji in controls.
  Emoji supplied by n8n lesson content are kept as content.
- Focus ring: 2px gold outline. Selection and scrollbars are themed.

## Layout
- Desktop: a 60px top bar, a 288px timeline sidebar on the right, and the slide stage.
- 900px and below: the sidebar becomes an overlay, grids collapse, and nav and counter move to a fixed 68px bottom bar.
- 560px and below: tighter gutters (16px), and labels on the points button are hidden.
- `prefers-reduced-motion` turns off animation.

## Preview
`npm run preview` injects `preview/sample-lesson.json` (Surah Al-Ikhlas; tafsir lines are marked as sample text) the way n8n does.
Then `npm run slides` screenshots every slide to `shots/slides/`.
