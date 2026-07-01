---
name: primetals-text-style
description: Applies Primetals' official text colors and fonts to ANY deliverable — Word, Excel, PowerPoint, HTML, email, Markdown, anything with text. ALWAYS auto-activate whenever the user asks to produce an HTML file/page/report ("html로 만들어줘", "make/build an HTML", "HTML로 정리", HTML briefing/summary) — HTML output is a hard trigger for this skill, no Primetals/brand keyword required. Also use when producing or styling a Primetals-branded document, when the user asks for Primetals/프리메탈스 brand color or font, corporate styling, brand-compliant text, or whenever writing company-facing content that must match the corporate identity. Not limited to PPT.
---

# Primetals Text Style

Brand standard for **text color and font** in any Primetals deliverable (Word, Excel, PPT, HTML, email, Markdown, etc.). This is the authoritative reference — values are extracted from the official `Primetals full POWERPOINT templates.pptx` theme (theme name "Primetals"). Scope is **text only**: color + font. It does not govern layout, images, shapes, or headline wording.

> **HTML is a hard trigger.** Any request to produce HTML (`html로 만들어줘`, "make an HTML report/page/briefing", "HTML로 정리") auto-activates this skill — apply the brand palette + per-language font stack and mirror the example template at `reference/examples/krakatau_survey_*.html` (dark-blue header banner with orange bottom rule, orange section-number badges, black body, teal links, named status-tag colors). No explicit "Primetals/brand" keyword is needed.

> **ALWAYS produce a self-contained single-file HTML — embed every image inline.** Never reference images by relative path or an `img/` subfolder; the `.html` must be one portable file that displays correctly when moved, copied, or pasted into an email with no sidecar files. Embed each image as a base64 `data:` URI directly in the `<img src>` (e.g. `<img src="data:image/png;base64,iVBORw0KG...">`). (User directive: 앞으로 HTML은 전부 이미지 내장 단일파일.)
> - In PowerShell, generate the data URI with: `$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($path)); "data:image/png;base64,$b64"`. In Python: `import base64; "data:image/png;base64,"+base64.b64encode(open(path,'rb').read()).decode()`.
> - This applies to **all** HTML output (reports, briefings, email digests) — not just email-derived ones.

> **When organizing an email (`.msg`/`.eml`) into HTML, ALWAYS include the email's photos.** Extract the inline images from the message and embed them in the HTML next to the matching passage (with a short caption) — do not produce a text-only digest. (User directive: 메일 정리 시 메일 안의 사진도 추가해서 html에 정리.) Notes:
> - Outlook COM `Attachment.SaveAsFile` often hangs on a security dialog in non-interactive shells. Prefer the Python `extract_msg` library (`pip install extract_msg`) to pull `m.attachments[i].data` directly. Run the script from a **clean working dir** (not `%TEMP%`) so a stray `inspect.py`/`zipfile.py` can't shadow the stdlib.
> - Recover the in-body order of images from `htmlBody` (`src="cid:..."`) and place each photo where its `cid` appears in the text. **Drop tiny decorative images** (spacers/bullets, typ. <~5 KB) and de-duplicate photos that repeat inside a quoted/forwarded original.
> - Embed each kept photo inline as a base64 `data:` URI (per the self-contained rule above) — do **not** write photos to an `img/` subfolder.

## LANGUAGE — DEFAULT 한국어 FOR HTML, DON'T ASK

**For HTML 정리/reports, default to 한국어 — do NOT ask the language.** Just produce the deliverable in Korean using the 한국어 font row below. (User directive: HTML 정리는 기본 한국어, 질문 금지.)

For **non-HTML** deliverables (Word/PPT/Excel/email) where the language is genuinely ambiguous, you may still ask:

> "작성 언어가 무엇인가요? **English / 한국어 / 日本語**"

If the user explicitly states a different language in the request, follow that instead. Then apply the matching font row below.

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

> **This table is the generic role mapping — it applies to HTML / Word / Excel / email.** Native PowerPoint is different: the official `.pptx` master hard-codes its own placeholder colors (**slide title = Orange `E87722`, body = Dark Blue `0C2340`**), so for PPT you do **not** hand-apply these roles — you inherit them from the template. See the **PowerPoint** section below. The two are different house styles per medium; both are brand-valid — do not cross them.

## Applying per format

- **Word / Excel** (via OOXML or generator libs): set the run/cell font and the font color hex per the tables above.
- **PowerPoint (native `.pptx`)**: do **not** paint colors by hand — start from the bundled brand template and let its master/layouts style everything. See the dedicated **PowerPoint** section below.
- **HTML / CSS**: per-language font stack — EN `font-family: Arial, sans-serif;` · KO `font-family: Arial, "Malgun Gothic", sans-serif;` · JP `font-family: Arial, "Meiryo UI", "Meiryo", sans-serif;` (Arial first so Latin/numbers stay Arial, CJK falls through). Colors: `color:#0C2340` / `#000000` / `#E87722` etc.
- **Markdown / plain text**: structure only (no color/font control) — keep the role mapping in mind for any place that does render (e.g. an HTML export).

## PowerPoint (native `.pptx`) — template-first

**When the deliverable is a PowerPoint, never build slides from a blank deck and hand-color them.** Start from the bundled brand template so the corporate master (logo, orange rule, footer, copyright) and the real placeholder styles are inherited automatically. This is how a genuine Primetals deck is authored.

**Bundled template:** `assets/Primetals_template_blank.pptx` — the official `POWERPOINT templates.pptx` with all 49 sample slides stripped, keeping **1 master + 36 layouts + Primetals theme + the top-right Primetals logo** (vector EMF). 16:9, `12192000 × 6858000` EMU (13.33″ × 7.5″). ~350 KB.

**What the master paints on every slide automatically** (don't recreate these by hand):
- **Primetals logo**, top-right (vector EMF).
- **Orange full-width bottom rule** (`E87722`, ~0.075″ tall).
- **Copyright**, bottom-left: `Restricted © Primetals Technologies 2021-2026. All rights reserved.` (grey `63666A`, 10 pt).
- **Footer** `YeJun Kim / SM JP INT`, page number, date — grey `63666A`, 10 pt.
- (A Concast India co-brand logo is embedded but hidden — off by default.)

**Real placeholder text styles baked into the master** (inherited — do not override unless asked):

| Placeholder | Color | Size | Notes |
|---|---|---|---|
| **Slide title** | **Orange `E87722`** | 24 pt | Arial, left-aligned |
| Body level 1 | Dark Blue `0C2340` | 18 pt | orange `•` bullet |
| Body level 2 | Dark Blue `0C2340` | 18 pt | `–` dash bullet |
| Body level 3 | Dark Blue `0C2340` | 12 pt | `–` dash bullet |
| Body level 4 | Grey `63666A` | 12 pt | |
| Body level 5 | Grey `97999B` | 12 pt | |

> Note the medium difference: in native PPT the **title is Orange and body is Dark Blue** (theme `accent1` / `tx1`). This is deliberately different from the HTML/Word role table (title Dark Blue, body Black). Follow whichever medium you're producing.

**Layout catalog** (select by `layout.name` — indices can shift if the template is edited):
- Covers: `Cover with image`, `Cover without image`
- Chapter dividers: `Chapter title with image`, `Chapter title without image`
- Content: `Content - blank`, `Content - one element`, `Content - two elements`, `Content - three elements`, `Content - one image`, `Content - element and image #1…#3`, `Content - element and two images #1…#2`, `Content - two images and two elements`
- Special: `Challenge - Solution - Features - Benefits`, `Highlighted statement #1…#3`, `Highlighted content #1…#2`, `Circular images - one…six items`, `References - one…six projects`, `Image full`
- Closing: `Contact`, `Contact_PTCN`, `Contact_Concast`

**python-pptx pattern** — open the template, pick a layout by name, fill placeholders:

```python
from pptx import Presentation
prs = Presentation(r"<skill>/assets/Primetals_template_blank.pptx")

def layout(name):
    return next(l for l in prs.slide_layouts if l.name == name)

# Cover
s = prs.slides.add_slide(layout("Cover without image"))
s.shapes.title.text = "K3CX Cold Mill Capacity Increase"

# Content — title + bullets (colors/bullets come from the master; don't set them)
s = prs.slides.add_slide(layout("Content - one element"))
s.shapes.title.text = "Scope of Supply"
body = s.placeholders[<idx>].text_frame        # inspect .placeholder_format.idx to find the body
body.text = "Mechanical equipment"
p = body.add_paragraph(); p.text = "Electrical & automation"; p.level = 1

prs.save(out_path)
```

- **Let the master do the styling.** Only set a run color/font explicitly when the user asks for a deliberate accent (e.g. a key figure in Orange) — then pull the hex from the palette.
- **Fonts** still follow the language rows above (EN Arial / KO 맑은 고딕 / JP Meiryo UI) for any run where you set the font at all.
- Images aren't required (user directive: 로고만 있으면 됨, 그림 불필요) — the logo already ships in the master, so a text-only deck is fully brand-compliant.

### Cover photo, special layouts & closing (verified recipes)

- **Cover with a photo** — use the `Cover with image` layout and drop the picture into its **PICTURE placeholder** (idx 14); it auto-clips to the diagonal. A ready brand cover photo is bundled: `assets/Primetals_cover_people.jpg` (official Primetals team shot).
  ```python
  from pptx.enum.shapes import PP_PLACEHOLDER as PH
  s = prs.slides.add_slide(layout("Cover with image"))
  s.shapes.title.text = "…"
  pic = next(p for p in s.placeholders if p.placeholder_format.type == PH.PICTURE)
  pic.insert_picture(r"<skill>/assets/Primetals_cover_people.jpg")
  ```
- **Special "statement" layouts** (`Highlighted statement …`, `Chapter title …`) — the headline/statement goes in the **TITLE** (it fills the orange circle / chapter band), **not** the body. The body placeholder on these is a small caption.
- **Closing "THANK YOU"** — the brand's closing is `Content - blank` + a plain textbox with **60 pt Orange `E87722`, all-caps "THANK YOU"** (logo + orange rule come from the master):
  ```python
  from pptx.util import Emu, Pt
  from pptx.dml.color import RGBColor
  from pptx.oxml.ns import qn
  s = prs.slides.add_slide(layout("Content - blank"))
  tb = s.shapes.add_textbox(Emu(360359), Emu(1798638), Emu(5588000), Emu(1800000))
  p = tb.text_frame.paragraphs[0]
  p._p.get_or_add_pPr().append(p._p.get_or_add_pPr().makeelement(qn('a:buNone'), {}))  # kill inherited bullet
  r = p.add_run(); r.text = "THANK YOU"
  r.font.size = Pt(60); r.font.name = "Arial"; r.font.color.rgb = RGBColor(0xE8,0x77,0x22)
  ```
- **Gotcha:** a plain `add_textbox` paragraph inherits the theme's default bullet (`•`). Add `<a:buNone/>` to the paragraph's `pPr` (as above) or a stray dot appears.

## Common mistakes

- Producing content before asking the language → wrong font.
- Using Orange for whole paragraphs (it's an accent, not body).
- Making body text Dark Blue (headers are Dark Blue; **body is Black**).
- Inventing a hex (e.g. a "nicer" orange) instead of using `E87722` / the named palette.
- Treating this as PPT-only — it applies to every text deliverable.
- Building a PPT from a blank deck and hand-coloring it → off-brand (no logo, wrong title/body colors). Start from `assets/Primetals_template_blank.pptx` and inherit the master styles.
- Applying the HTML role colors to native PPT placeholders (title Dark Blue / body Black) → wrong: PPT master is **title Orange / body Dark Blue**.
- Referencing images by relative path / `img/` folder instead of embedding them as base64 → broken images when the HTML is moved or emailed. Always emit a self-contained single file.

## Worked examples

Reference outputs — the same POSCO Krakatau equipment survey rendered in all three languages, sharing one brand palette and differing only by language font (the skill's core pattern). Open these to confirm correct styling:

- `reference/examples/krakatau_survey_KO.html` — 한국어, body `Arial, "Malgun Gothic"`
- `reference/examples/krakatau_survey_EN.html` — English, body `Arial`
- `reference/examples/krakatau_survey_JP.html` — 日本語, body `Arial, "Meiryo UI"`

Each uses the dark-blue header banner with an orange bottom rule, orange section-number badges, black body, teal links, and the named status-tag colors — a good template to mirror for HTML deliverables.

## Full palette

All 22 named brand colors (greys, accents, signals) → `reference/palette.md`.
