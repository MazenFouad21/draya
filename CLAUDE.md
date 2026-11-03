# Draya: design workflow

Main file: `dirayah-template.html`, a teacher-led Quran lesson deck sold as a product. n8n replaces `/*__LESSON_JSON__*/null` and `/*__AYAT_JSON__*/null` with lesson data. Keep that data contract and every element ID the script uses.

## Design system
- `DESIGN.md` is the source of truth for the look ("Bookcloth & gold"): tokens, type, motifs, components.
- `design/stripe-DESIGN.md` is a craft reference only (precision of spacing, type scale, shadows). Don't apply its palette.

## Skills (`.claude/skills/`)
| Skill | Use for |
|---|---|
| `impeccable` (pbakaus/impeccable, Apache-2.0) | Craft, critique, audit, polish, animate, colorize, harden, and similar commands. Read its `reference/` files as needed. |
| `taste-skill` (Leonxlnx/taste-skill, MIT) | Art direction and an anti-generic house style. Its inspector is `scripts/inspect.mjs`. |
| `web-design-guidelines` (vercel-labs/agent-skills) | Reviewing UI against the Vercel Web Interface Guidelines. If the guidelines can't be fetched, use the bundled copy in `guidelines.md`. |

## Playwright
- MCP server: `.mcp.json` registers `@playwright/mcp` (headless) for browsing and interacting with pages.
- `npm run preview` builds `shots/preview.html` with sample data, and `npm run slides` screenshots every slide.
- `npm run shots` saves screenshots of the preview at widths 1440, 768 and 390 to `shots/`, and reports JS errors and horizontal overflow.
- `npm run taste` runs the taste-skill inspector. In the cloud, set
  `CHROME_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome` first.

## Loop for every UI change
1. Edit using the DESIGN.md tokens.
2. Run `npm run preview && npm run shots` and look at all three widths.
3. Check the result against web-design-guidelines and the impeccable audit.
