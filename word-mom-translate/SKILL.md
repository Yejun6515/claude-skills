---
name: word-mom-translate
description: Translate a Japanese Word document (.docx) into Korean. Two modes — (A) bilingual append for MOMs (JP_<contract>.docx): original kept intact, Korean appended in blue parentheses under each Japanese passage; (B) replace for non-MOM docs (질의회신, 기술문서 등): Japanese deleted, Korean-only output with matching pagination. Use when the user asks to translate a 회의록/MOM/질의회답/Word file from Japanese to Korean, add Korean under Japanese in a .docx, produce a JP_KR bilingual document, or 일본어 없애고 한글만.
---

# Word 문서 일→한 번역 (MOM 병기 / 일반문서 교체)

Translate a Japanese Word document to Korean. **The source file is never modified** — output is always a new file. Two modes:

- **Mode A — bilingual append (MOM 전용):** for every Japanese passage, the Korean translation is **appended right below it** (a new paragraph inside the same table cell), styled blue and wrapped in parentheses. This mirrors the house style of POSCO K3C Revamping MOM documents.
- **Mode B — replace (기본, MOM이 아닌 문서):** the Japanese text is **deleted and replaced in place** by the Korean translation, keeping the original run formatting and table layout. Output is Korean-only.

## When to use / mode selection
- Source is a MOM (`JP_<contract>.docx`, POINTS DISCUSSED/RESULT table) and the user wants a bilingual version → **Mode A**.
- Anything else (질의회신/ご質問への回答, 기술문서, 일반 문서) or the user says "일본어 없애고 한글만", "한글로 바꿔줘" → **Mode B**. When in doubt for non-MOM docs, default to Mode B (2026-07-17 결정).

## What gets translated
- **Only passages containing Japanese kana/kanji.** In these MOMs that is the `POINTS DISCUSSED` and `RESULT` columns of the main discussion table.
- **Left untouched:** the header block (Subject/Date/Place/Participants), the `Distribution` table, and all code/English-only cells (`No.`, `BY` = POS/PTJ, `*` = D/P, `Remarks` = Attachment-1, etc.). The extract script auto-skips these because they contain no Japanese.

## Workflow

All scripts live in `scripts/` next to this file. Run them with Windows PowerShell. They are saved UTF‑8 **with BOM** (required so PS 5.1 reads the Japanese/Korean inside correctly) — do not re-save them without a BOM.

### 1. Extract the Japanese units
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skillDir>\scripts\extract-cells.ps1" -Source "<JP .docx>" -Out "<work>\cells.json"
```
`cells.json` is a list of `{ "id": "t1.r2.c1", "kind": "cell", "text": "..." }`. The `id` encodes table/row/cell (or `pN` for a body paragraph). `text` uses `\n` for line breaks and in‑cell paragraph breaks. The script copies the docx to temp first, so it works even while the file is open in Word.

### 2. Translate each unit to Korean
Read `cells.json`. For **every** unit, translate `text` → Korean following the **Translation rules** below. **Preserve the `\n` structure** (same number of lines). Build a JSON object mapping each `id` to its Korean string and write it with the Write tool as `translations.json` (UTF‑8):
```json
{ "t1.r1.c1": "PTJ Scope표 확인(5/28의 이어서)",
  "t1.r2.c1": "1-23 1) l  Centrifugal pump with base, coupling, cover에 scope 기재가 없음.\n본 기기는 Reuse이므로, Reuse를 기재할 것",
  "t1.r2.c3": "잘 알겠습니다" }
```
Do **not** add the surrounding parentheses or the blue color — the inject script adds those. Just provide the Korean text. Translate the whole file; don't skip cells.

### 3-A. Mode A — inject under the originals
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skillDir>\scripts\inject-translations.ps1" -Source "<JP .docx>" -Translations "<work>\translations.json" -Out "<output .docx>"
```
For each id it appends one new paragraph after the original in that cell: blue `0000CC`, font `맑은 고딕` (eastAsia) + majorHAnsi theme, size 9pt (`sz=18`), `ko-KR`, the text wrapped in `( … )`, with `\n` rendered as `<w:br/>`. Everything else in the file is byte‑preserved (only `word/document.xml` is rewritten). It prints `Applied N translations`.

### 3-B. Mode B — replace the originals
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skillDir>\scripts\replace-translations.ps1" -Source "<JP .docx>" -Translations "<work>\translations.json" -Out "<output .docx>"
```
Same `translations.json` format. For each id it removes the Japanese runs and writes the Korean text in the same paragraph/cell, cloning the original run formatting (only the eastAsia font is switched to `맑은 고딕` + `ko-KR`). `\t` in a value renders as `<w:tab/>`, `\n` as `<w:br/>` (extra in-cell paragraphs are merged into the first). It prints `Replaced N units`. Afterwards, re-run `extract-cells.ps1` on the output — it must return `[]` (no Japanese left).

**Page matching (Mode B):** the Korean output should keep the SAME page count as the Japanese original — 예준님 reads them side by side. Matching pages wins over font size (2026-07-17 결정). 맑은 고딕 has taller line metrics than Japanese fonts, so the KR file often gains a page even at the same pt. Fix loop:
1. Compare page counts (Word COM, read-only): `$d.ComputeStatistics(2)` on both files.
2. If KR has more pages, shrink all Korean runs by 1pt and re-check:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "<skillDir>\scripts\shrink-korean-runs.ps1" -Path "<KR .docx>" -Step 2
   ```
   (`-Step` is in half-points; targets only runs with eastAsia=맑은 고딕, i.e. the injected Korean. Floor 5pt.) Repeat until counts match — the 2026-07-17 질의회신 doc needed 2 passes (−2pt total).
3. If shrinking looks excessive (>3pt), shorten the Korean wording instead.

### 4. Name and place the output
Same folder as the source.

**Mode A (MOM):**
```
MOM(<contractNo>)_<YYYY.MM.DD>(JP_KR).docx
```
- `<contractNo>` = source filename with the leading `JP_` and `.docx` removed (e.g. `JP_0324R086-2001043-ME014.docx` → `0324R086-2001043-ME014`).
- `<YYYY.MM.DD>` = the meeting **Date** from the document header (e.g. `Date: June 1, 2026` → `2026.06.01`).

If either is ambiguous, confirm with the user before writing.

**Mode B (replace):** translate the source filename itself into Korean and append `(KR)` — e.g. `POSCO殿K3C改造_20260709ご質問への回答.docx` → `POSCO K3C 개조_20260709 질의사항 회신(KR).docx`. Keep dates/codes verbatim.

### 5. Report
Tell the user the output path and the applied count, and that the original is unchanged. Recommend a quick visual review in Word (translations appear in blue).

## Translation rules

Tone: **개조식 (nominal-ending meeting-minutes style)** — this is the most important rule. Korean MOMs use clipped nominal endings, **not** full conversational sentences. Avoid `～한다` and `～합니다` endings: they read as machine-translated / AI-written. Convert statements to a noun-ending form instead.

- Imperative `～する事 / ～すること` → `～할 것`
- Plain statement verbs → nominalize with `～함 / ～됨`: `回答する` → **회신함** (NOT 회신한다/회신합니다); `協議する` → **협의함**; `依頼する` → **의뢰함**; `送付します` → **송부함**; `変更します` → **변경함**; `削除します` → **삭제함**; `計画しています` → **계획 중임**.
- Requests `～ください / ～お願いします` → `～바람` (e.g. 連絡ください → **연락 바람**, 送付をお願いします → **송부 바람**).
- Set replies stay fixed: `拝承 / ご了解` → `잘 알겠습니다`.
- It is fine for a noun-ended clause to keep a trailing period (`…함.`). Keep sentences short and factual; do not add connective filler.

**Keep in English / verbatim (do NOT translate):**
- Equipment & scope terms used as-is in the source: `scope`, `new`, `remove`, `Reuse`, `Coolant System`, `Oil mist`, `Pressure transducer`, `Back wash filter`, `Pedestal`, `Mill Area`, `Grease piping`, `Stainless`, `Drum Can`, `standby`, `maker`, `I/L`, etc.
- Item codes and section numbers exactly: `1-23 2) d-1`, `2-1 a`, `K-2`, `m-2`…
- Dimensions/figures: `2m^3`, `70m3`, `5/28`, `6/2`…
- Proper nouns & maker names: `POSCO`, `PTJ`, `WNC`, `HTC`, `Rosemount`, `Yokogawa`, tank/line names like `S1 clean & dirty tank`.

**Standard glossary (JP → KR):**
| 日本語 | 한국어 |
|---|---|
| 拝承 / ご了解 | 잘 알겠습니다 |
| ～する事 / ～すること | ～할 것 |
| ～ください | ～ 바랍니다 |
| ～について(は) | ～에 대해(서는) |
| POSCO殿 / ～殿 | POSCO 측 / ～ 측 |
| 既設 | 기존(설비) |
| 新設 / 新規 | 신설 / 신규 |
| 流用 | Reuse(문맥상 영어 유지) / 유용 |
| 撤去 | 철거 |
| 設置 | 설치 |
| 記載 | 기재 |
| 訂正 / 誤記 | 정정 / 오기 |
| 見積(もり) / 改訂見積 | 견적 / 개정 견적 |
| 重量 | 중량 |
| 仕様 / 型式 | 사양 / 형식 |
| 図面 / 系統図 / 配置 | 도면 / 계통도 / 배치 |
| 連絡する / 送付する | 연락함 / 송부함 (NOT 연락한다) |
| 確認 / 検討 / 協議 | 확인 / 검토 / 협의 |
| 方針 / 反映 | 방침 / 반영 |
| 回答する | 회신함 (NOT 회신한다) |
| 容量アップ | 용량 up |

Normalize spacing lightly (e.g. `base,coupling,cover` → `base, coupling, cover`) as the reference does, but don't otherwise rewrite the source's technical phrasing.

## Notes & guardrails
- **Run on a Japanese-only source.** Re-running Mode A on an already-bilingual file would double up, because the original Japanese is still present and would be re-extracted.
- Never edit the source file in place; always write a new `(JP_KR)` / `(KR)` output.
- If `extract` returns body-paragraph (`pN`) units, those are Japanese passages outside the table — translate them too; inject puts their Korean in a new paragraph immediately after the original (Mode A) or replaces it in place (Mode B).
- The scripts need no internet and no extra modules (built-in `System.IO.Compression`).
