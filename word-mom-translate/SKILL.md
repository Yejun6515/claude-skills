---
name: word-mom-translate
description: Translate a Japanese Word meeting-minutes/MOM (.docx) into Korean by keeping the original text intact and appending a Korean translation directly beneath each Japanese passage (blue, parenthesized, inside the same table cell). Use when the user asks to translate a 회의록/MOM/Minutes of Meeting Word file from Japanese to Korean, add Korean under Japanese in a .docx, or produce a JP_KR bilingual meeting-minutes document.
---

# Word 회의록(MOM) 일→한 번역

Produce a bilingual (Japanese + Korean) Word meeting-minutes document. **The original is never modified** — for every Japanese passage, the Korean translation is **appended right below it** (a new paragraph inside the same table cell), styled blue and wrapped in parentheses. This mirrors the house style of POSCO K3C Revamping MOM documents.

## When to use
The user gives a Japanese MOM `.docx` (often named `JP_<contract>.docx`) and wants a Korean bilingual version (`MOM(<contract>)_<date>(JP_KR).docx`).

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

### 3. Inject under the originals
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skillDir>\scripts\inject-translations.ps1" -Source "<JP .docx>" -Translations "<work>\translations.json" -Out "<output .docx>"
```
For each id it appends one new paragraph after the original in that cell: blue `0000CC`, font `맑은 고딕` (eastAsia) + majorHAnsi theme, size 9pt (`sz=18`), `ko-KR`, the text wrapped in `( … )`, with `\n` rendered as `<w:br/>`. Everything else in the file is byte‑preserved (only `word/document.xml` is rewritten). It prints `Applied N translations`.

### 4. Name and place the output
Same folder as the source. Filename convention:
```
MOM(<contractNo>)_<YYYY.MM.DD>(JP_KR).docx
```
- `<contractNo>` = source filename with the leading `JP_` and `.docx` removed (e.g. `JP_0324R086-2001043-ME014.docx` → `0324R086-2001043-ME014`).
- `<YYYY.MM.DD>` = the meeting **Date** from the document header (e.g. `Date: June 1, 2026` → `2026.06.01`).

If either is ambiguous, confirm with the user before writing.

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
- **Run on a Japanese-only source.** Re-running on an already-bilingual file would double up, because the original Japanese is still present and would be re-extracted.
- Never edit the source file in place; always write a new `(JP_KR)` output.
- If `extract` returns body-paragraph (`pN`) units, those are Japanese passages outside the table — translate them too; inject puts their Korean in a new paragraph immediately after the original.
- The scripts need no internet and no extra modules (built-in `System.IO.Compression`).
