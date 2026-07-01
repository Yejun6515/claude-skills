---
name: note-description
description: Organize Obsidian note frontmatter — write/refresh the `description:` field, fill empty `tags:` from a controlled entity/·topic/ vocabulary, and normalize frontmatter to the standard Event template. Follows the `file:///` source links inside a note (network-drive attachments/folders) and skims them to enrich the description. Use when the user asks to add/write/update descriptions, fill in tags, tidy/normalize frontmatter, or "organize/정리" a note or project folder in their Obsidian vault.
---

# Note Organizer (description + tags + frontmatter)

You organize Obsidian note frontmatter so notes are identifiable in AI search and well-connected via tags. You do three jobs, in this order, on each in-scope note:

1. **Description** — write/refresh the `description:` field.
2. **Tags** — fill an empty `tags:` field from the controlled vocabulary below.
3. **Frontmatter normalization** — conform to the standard Event template.

When pointed at a folder, process **every in-scope note** in it (and nested subfolders).

**Default: edit frontmatter only.** Two body exceptions: (a) when following linked source materials, add a brief `## 핵심요약` summary under the note's `# Claude Code` section (see "Following linked source materials"); (b) if normalization would drop a non-standard field that holds real data, move it into the body rather than deleting it (see Normalization). In all cases Claude writes **only inside `# Claude Code`** and never touches `# Yejun's memo` (or 회의록 notes' `# Tiro`).

## Vault location

The vault root **differs per PC** — read the `vault_root:` value from `%USERPROFILE%\.claude\skills\_config\local-paths.md` (if the file/key is missing, ask the user and save it there; see `_config\README.md`). `{vault}` below means that value. Note projects live under `{vault}\01. Projects` (e.g. `01.01 HSC\HSC_DJ _CM_PGL MP Scale`). Work **one project folder at a time**.

## Scope — which notes get processed

- **Dated event/log notes** (filename has a `YYMMDD_` prefix or an explicit date in the title) get the full treatment: description + tags + normalization.
- **Skip `0_`-prefixed notes** (index/MOC notes, `.base` files) entirely — they are not tagged or described. User instruction.
- **Near-empty stub notes**: hold (don't force tags/description); mention them to the user.
- A note whose **title lacks a date but has substantive content and a `Date:` frontmatter field** (e.g. a `인수인계`/handover note) may be processed — confirm with the user if unsure, since the legacy rule was date-in-title only.
- If the user names a **single note**, do that one. If they point at a **folder** or say "fill in missing ones", enumerate it, then process the in-scope notes (grep `^tags:` / `^description:` to find empty/missing ones).

## Job 1 — Description

1. **Read the full note body** (this skill is the deep-read exception to the usual description-first scan).
2. **Follow linked source materials** referenced in the body (see "Following linked source materials" below) and fold their key facts into the description — this is the main way to enrich an otherwise thin note.
3. Compose **1–2 English sentences** (~25–45 words): *what it contains + (if useful) when to reference it*.
3. **Distinctiveness first** — include proper nouns (HSC, PTJ, POSCO, PTKR, NSD…) and key figures (costs, dates, quantities, grades). Never generic ("Meeting note", "Project summary"). Never invent facts not in the body.
4. If the value contains a colon, quote, or special char, **wrap the whole value in double quotes** so the YAML stays valid:
   ```
   description: "..."
   ```
5. Only replace empty/missing/generic descriptions; leave good existing ones unless asked to refresh.

❌ `description: "Notes about a POSCO project."`
✅ `description: "POSCO P2H hot strip mill revamp feasibility study — quotation (~33 MJPY) submitted, executive briefing Mar 2026. Covers cost basis and schedule coordination."`

## Job 2 — Tags (fill empty `tags:`)

Goal: raise vault connectivity. **Two nested axes**, both optional per note — assign what genuinely applies, don't pad. Write as a YAML list:

```
tags:
  - topic/quotation
  - entity/PTKR
```

**`entity/<외부 주체>`** — external parties that cut across projects (customers' contractors, manufacturers, affiliates, competitors, consultants, insurers). Established vocabulary (extend when a genuinely new party appears, matching existing casing):
`entity/SEJAL` `entity/TEXTECH` `entity/Uenotex` `entity/PTCN` `entity/PTDE` `entity/PTKR` `entity/Andritz`(competitor) `entity/Danieli`(Danieli-Fröhling — 압연기 competitor) `entity/Kato`(consultant) `entity/Ikuta`(生田産機) `entity/Moog` `entity/Hitachi` `entity/EMG` `entity/Nireco` `entity/NSD`(Absocoder maker) `entity/JMC`(trade insurance) `entity/DHTG`(China equipment maker) `entity/WNC`(우노상사/Woono Corp — POSCO 거래 trading agent) `entity/Zhengrui`(正瑞 — TEX 납품 동박압연 고객) `entity/Hengtong`(亨通 — 중국 케이블·동박 메이커) `entity/ShanxiChangda`(山西长达精密金属 — 동박 신규 고객) `entity/OBOT`(奥博特 — 중국 압연기 메이커) `entity/TMEIC`(東芝三菱電機産業システム — POSCO servo-valve 시스템 메인 컨트랙터) `entity/DMS`(auto roll-changing robot competitor — POSCO K2ZRM 납입 실적) `entity/MHI`(三菱重工 — push plate·판금 제작 파트너) `entity/KYOWA`(共和電業 — Pressure Cell/load-cell maker) `entity/Nucor`(US steelmaker — HSC Pair Cross reference-visit plant, Decatur) `entity/Ternium`(중남미 철강사 — POSCO 멕시코 전기강판 JV 상대)

**`topic/<주제·업무>`** — work theme:
`topic/quotation` `topic/logistics` `topic/site-visit` `topic/spare-parts` `topic/installation` `topic/equipment-spec` `topic/tech-spec` `topic/layout` `topic/packing` `topic/rust` `topic/unpacking-inspection` `topic/claim` `topic/expense` `topic/company-info` `topic/customs` `topic/contract` `topic/bond` `topic/payment` `topic/insurance` `topic/training` `topic/drawing` `topic/negotiation` `topic/meeting` `topic/PO` `topic/internal-process` `topic/tax`

Rules:
- The **customer is the folder** (e.g. HSC/Hyundai Steel) and **PTJ is the user's own company** → never tag these as `entity/`.
- `customer/` and `equip/` axes are **out of scope** (folder already encodes customer & project).
- Derive `entity/` tags from the **body** (subcontractors/makers/affiliates named there), not just the description.
- If nothing genuinely applies, leave `tags:` empty rather than inventing.
- The controlled vocabulary is **shared vault-wide** — reuse exact spellings so tags actually link notes together.
- **This list is the single master vocabulary for the whole vault.** Every skill that tags notes (note-digest, tiro-meeting-note, wiki-ingest, meeting-folder-brief…) follows it; when a genuinely new `entity/` or `topic/` tag is introduced anywhere, add it **here (this SKILL.md)** so the vocabulary cannot drift.

## Job 2c — mentions (people ↔ Contacts: propose → confirm → apply)

Connect the **people** named in a note to their contact notes under `20. Contacts`, recorded in `mentions:`. **Apply only after the user confirms — never auto-fill.**

1. **Extract names** — for 회의록, from `# Tiro` transcript / `# Yejun's memo` / 참석자; for Event/email notes, from sender·recipients·body. Include the user (Kim Yejun) when they attended.
2. **Match against Contacts** — match each name to a contact **filename** under `{vault}\20. Contacts\**`, tolerant of name-order / spacing / comma / romanization·Korean·Kanji variants (e.g. "Yang yohan"=양요한, "Doho, Haruka"=道法 春香). Use the **exact contact filename** so the wikilink resolves.
3. **Split the proposal** — (a) **has a contact** → `- "[[filename]]"` candidates; (b) **no contact (new person)** → report separately; don't silently add — ask whether to create a contact stub or skip.
4. **Confirm (required)** — show the proposed list and write **only the approved names**. Even an obvious match is not written without confirmation.
5. **Preserve & merge** — keep existing `mentions:` entries, dedupe. Format is a YAML list with double quotes `- "[[Name]]"` (inline `[[A]] [[B]]` breaks the frontmatter).

## Two note templates — Event vs 회의록 (meeting)

There are **two** templates. Pick by note type. **Both now carry body sections** — Claude writes only inside `# Claude Code` and never touches `# Yejun's memo` (or 회의록 notes' `# Tiro`).

- **Event template** (default, non-meeting log notes). Reference: `{vault}\50. Template\Event template.md`.
  - Frontmatter: `Date / Catetory / mentions / Google Drive / description / tags`.
  - Body sections (standard order): **`# Yejun's memo`** → **`# Claude Code`**. The user's own content (the source `file:///` link, free notes) lives under `# Yejun's memo`; Claude's `## 핵심요약`/organized summary goes under `# Claude Code`.
  - **Migrating legacy notes**: older Event notes have a `## Event` heading holding the source link. When processing one, **rename `## Event` → `# Yejun's memo`** (keep its link/content untouched), add a `# Claude Code` section below it, and write the summary there. Never leave the summary under the old `## Event`.
- **회의록 / meeting template** — use this whenever the note records a **meeting (미팅/회의)** (filename or content says 미팅·meeting·회의, or it's minutes of a customer/internal call). Do **not** force these onto the Event template. Fields:
  ```
  Date:
  Catetory:
    - customer meeting        # or: Online meeting (online이면 추가)
  Venue:                      # online / 장소 (모르면 비움)
  mentions:                   # 참석자 [[wikilink]] — Contacts 대조해 제안, 확인 후 반영 (Job 2c)
  Tiro Address:               # Tiro 전사 URL (있으면)
  Tiro Edited:                # raw 등
  description:
  tags:
  ```
  Body sections (standard order): **`# Yejun's memo`** → **`# Claude Code`** → **`# Tiro`**. Claude's organized summary/안건 정리는 **`# Claude Code`에만** 작성하고 `# Yejun's memo`·`# Tiro`는 손대지 않음(비어 있으면 빈 헤더만 유지). Tiro 전사 본문은 `# Tiro` 아래에 들어감.
  - Meetings often cover **multiple 안건(cases)** — number them and organize each one's 관련메일·배경·진척·결론 separately under `# Claude Code`. Write `description`/`tags` **last**, after all 안건 are organized.

## Job 3b — Title (filename) when missing

If a note's **filename has no descriptive title** — just a bare date like `260612.md` — give it one. Look at sibling notes in the same folder for the convention (`YYMMDD_설명`, e.g. `260604_K3CX sales factor.md`), derive 설명 from the note's link label / the linked source content, and **rename the file** to match (`260612_<설명>.md`). Keep the date prefix. If the link label already reads as a title, use it.

## Job 3 — Frontmatter normalization (standard Event template)

Standard field order: `Date / Catetory / mentions / Google Drive / description / tags`.

- Keep `Catetory` as-is including the original misspelling **`Catetory`** (template original; it's the note-type classifier, role-separate from tags).
- **`Catetory: submission`** when the note records a deliverable/document **submitted to the customer** (견적서·자료·제안 등 고객사 제출물). Otherwise keep the note's existing classifier (e.g. `information`, `meeting`). Internal-only correspondence/discussion is **not** a submission → leave as `information`.
- **`mentions:` — propose from Contacts, apply only after confirmation (see Job 2c).** Never auto-fill; never overwrite existing entries (merge/dedupe).
- Non-standard fields (Participants/Status/Transcription Accuracy, etc.): remove — **but if a removed field holds real data** (e.g. a Notebook LM link), move that data into the body, don't delete it.
- Match each note's existing indentation/quoting style; only touch frontmatter.

## Following linked source materials ("연결된 자료")

Notes often link out to the real source files on the network drive, e.g. `[Absocode breakdown.xlsx](<file:///U:\...\250912_Breakdown>)`. When a note's own body is thin (just links), **open those linked files/folders to understand the note and enrich its description**.

- Resolve `file:///` links to their Windows path (`file:///U:\...` → `U:\...`); `Test-Path` then list the folder. `.xlsx` → read via Excel COM (`New-Object -ComObject Excel.Application`, open read-only).
- **`.msg` email — read it when it's the only file.** If a linked folder contains **only a single `.msg`** (or a handful where one email is clearly the substance), that email **is** the note's content and is important — **open and read it** (Outlook COM, below) and base the description + `## 핵심요약` on its actual thread content, not just the filename. The full thread (the lower quoted replies) usually carries the key context. Only when many other files are present is a `.msg`/`.pdf` safely skippable.
  ```powershell
  $ol = New-Object -ComObject Outlook.Application
  $msg = $ol.Session.OpenSharedItem($path)   # $path = full .msg path
  $msg.Subject; $msg.SenderName; $msg.To; $msg.ReceivedTime; $msg.Body
  $msg.Close(1)
  ```
- **Don't exhaust tokens on complex/large files.** If a workbook is big or has many sheets, **skim for a rough summary, don't extract everything**: list sheet names, read only the header rows + a capped sample (e.g. first ~30–50 rows of the key sheet, ≤15 cols), and stop once you grasp the gist. A rough, correct summary beats a complete dump. If a dump is unavoidably large, save it to a temp file and read just the head.
- Pull the **distinctive facts** (totals, price/cost figures, scenarios, key spec/qty changes, delivery terms) into the description, **and also add a concise `## 핵심요약` block under the note's `# Claude Code` section** summarizing the linked sources. Bullets in Korean `~함/~임` style, matching the vault's existing 핵심요약 sections. Skip row-by-row detail. **Always write inside `# Claude Code` only** — for legacy notes, first migrate `## Event` → `# Yejun's memo` and add `# Claude Code` (see "Two note templates"). Never touch `# Yejun's memo` / `# Tiro` content.
- If a linked source is unreachable (drive not mounted), note that and describe from the note text alone.

## Folder handling

When the target is a folder, enumerate it (including nested subfolders) and process every in-scope note. Report results grouped by folder.

## Operating notes

- When processing multiple notes, **briefly list each note with the tags (and any new/updated description) you wrote** so the user can review.
- Note any skipped notes (`0_` indexes, stubs) and any **new `entity/` tags** you introduced so the vocabulary stays consistent.
- Both templates use body section headers (`# Yejun's memo` / `# Claude Code`, plus `# Tiro` for 회의록). Claude writes the `## 핵심요약`/summary **only under `# Claude Code`** and leaves `# Yejun's memo` / `# Tiro` content untouched.
