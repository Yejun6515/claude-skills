---
name: primetals-text-style
description: Applies Primetals' official text colors and fonts to ANY deliverable — Word, Excel, PowerPoint, HTML, email, Markdown, anything with text. ALWAYS auto-activate whenever the user asks to produce an HTML file/page/report ("html로 만들어줘", "make/build an HTML", "HTML로 정리", HTML briefing/summary) — HTML output is a hard trigger for this skill, no Primetals/brand keyword required. Also use when producing or styling a Primetals-branded document, when the user asks for Primetals/프리메탈스 brand color or font, corporate styling, brand-compliant text, or whenever writing company-facing content that must match the corporate identity. Not limited to PPT.
---

# Primetals Text Style

Brand standard for **text color and font** in any Primetals deliverable (Word, Excel, PPT, HTML, email, Markdown, etc.). This is the authoritative reference — values are extracted from the official `Primetals full POWERPOINT templates.pptx` theme (theme name "Primetals"). Scope is **text only**: color + font. It does not govern layout, images, shapes, or headline wording.

> **HTML is a hard trigger.** Any request to produce HTML (`html로 만들어줘`, "make an HTML report/page/briefing", "HTML로 정리") auto-activates this skill — apply the brand palette + per-language font stack and mirror the example template at `reference/examples/krakatau_survey_*.html` (dark-blue header banner with orange bottom rule, orange section-number badges, black body, teal links, named status-tag colors). No explicit "Primetals/brand" keyword is needed.

## ALWAYS ASK LANGUAGE FIRST

**Before producing any styled content, ask the working language.** The brand defines the Latin font (Arial) but leaves the East-Asian font unset, so the font cannot be chosen until the language is known.

> "작성 언어가 무엇인가요? **English / 한국어 / 日本語**"

Do not assume — even if the request is written in Korean, the deliverable may be English. Ask, then apply the matching font row below. (If the user already stated the language in this turn, skip the question.)

## Font rules

| Language | Body font | Notes |
|---|---|---|
| English | **Arial** | Brand official (majorFont = minorFont = Arial) |
| 한국어 | **맑은 고딕 (Malgun Gothic)** | Use Arial for embedded numbers/Latin runs |
| 日本語 | **Meiryo UI** | Use Arial for embedded numbers/Latin runs |

- Headings and body share the same font family (no separate display font).
- Emphasis = **bold/size**, never a decorative font.
- Where a tool can't set fonts (plain Markdown, plain-text email), skip font and apply color/structure only.

## Color rules (role → color)

| Role | Color name | HEX |
|---|---|---|
| Title / header (bold) | Dark Blue (PT) | `0C2340` |
| Body default | Black | `000000` |
| Emphasis / key figures / bullets | **Orange (PT)** | `E87722` |
| Link | Teal (PT) | `00587C` |
| Secondary / muted text | Dark Grey (PT) | `97999B` |
| Positive signal | Green (PT) | `7A9A01` |
| Negative / warning signal | Red (PT) | `CE0037` |

- **Orange `E87722` is the signature Primetals accent** — use it deliberately for emphasis, not as body text.
- Dark Blue `0C2340` is the brand's primary dark; use it for titles/headers. Body text is Black `000000`.
- Need a color not listed (chart series, table banding, a second accent)? Pull only from the named brand palette in `reference/palette.md` — never invent an off-brand hex.

## Applying per format

- **Word / PPT / Excel** (via OOXML or generator libs): set the run/cell font and the font color hex per the tables above.
- **HTML / CSS**: per-language font stack — EN `font-family: Arial, sans-serif;` · KO `font-family: Arial, "Malgun Gothic", sans-serif;` · JP `font-family: Arial, "Meiryo UI", "Meiryo", sans-serif;` (Arial first so Latin/numbers stay Arial, CJK falls through). Colors: `color:#0C2340` / `#000000` / `#E87722` etc.
- **Markdown / plain text**: structure only (no color/font control) — keep the role mapping in mind for any place that does render (e.g. an HTML export).

## Common mistakes

- Producing content before asking the language → wrong font.
- Using Orange for whole paragraphs (it's an accent, not body).
- Making body text Dark Blue (headers are Dark Blue; **body is Black**).
- Inventing a hex (e.g. a "nicer" orange) instead of using `E87722` / the named palette.
- Treating this as PPT-only — it applies to every text deliverable.

## Worked examples

Reference outputs — the same POSCO Krakatau equipment survey rendered in all three languages, sharing one brand palette and differing only by language font (the skill's core pattern). Open these to confirm correct styling:

- `reference/examples/krakatau_survey_KO.html` — 한국어, body `Arial, "Malgun Gothic"`
- `reference/examples/krakatau_survey_EN.html` — English, body `Arial`
- `reference/examples/krakatau_survey_JP.html` — 日本語, body `Arial, "Meiryo UI"`

Each uses the dark-blue header banner with an orange bottom rule, orange section-number badges, black body, teal links, and the named status-tag colors — a good template to mirror for HTML deliverables.

## Full palette

All 22 named brand colors (greys, accents, signals) → `reference/palette.md`.
