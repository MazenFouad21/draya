# Draya: design workflow

Main file: `dirayah-template.html`, a single-page shop template (look reference: https://infinity-5d5.pages.dev/#shop).

## Design system
- `design/stripe-DESIGN.md` is the visual language to follow: colors, type, radii, spacing, gradients and components. It comes from VoltAgent/awesome-design-md (MIT).
  Use its tokens as CSS custom properties on `:root`. Don't copy Stripe's brand name or logo.

## Skills (`.claude/skills/`)
| Skill | Use for |
|---|---|
| `impeccable` (pbakaus/impeccable, Apache-2.0) | Craft, critique, audit, polish, animate, colorize, harden, and similar commands. Read its `reference/` files as needed. |
| `taste-skill` (Leonxlnx/taste-skill, MIT) | Art direction and an anti-generic house style. Its inspector is `scripts/inspect.mjs`. |
| `web-design-guidelines` (vercel-labs/agent-skills) | Reviewing UI against the Vercel Web Interface Guidelines. If the guidelines can't be fetched, use the bundled copy in `guidelines.md`. |

## Playwright
- MCP server: `.mcp.json` registers `@playwright/mcp` (headless) for browsing and interacting with pages.
- `npm run shots` saves screenshots at widths 1440, 768 and 390 to `shots/`, and reports JS errors and horizontal overflow.
- `npm run taste` runs the taste-skill inspector. In the cloud, set
  `CHROME_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome` first.

## Loop for every UI change
1. Edit using the DESIGN.md tokens.
2. Run `npm run shots` and look at all three widths.
3. Check the result against web-design-guidelines and the impeccable audit.
