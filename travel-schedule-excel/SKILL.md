---
name: travel-schedule-excel
description: 출장 스케줄 Excel 작성. 출장 일정을 글(prose)로 주면 Business_trip 양식 그대로 영어 일정표(.xlsx)를 생성. 하루=AM/PM 2행, 날짜·요일 자동 계산, 단일 항목 Agenda 병합, 저녁 일정은 Notes. 빈 마스터 복사·채우기 방식이라 테두리·폰트·병합 서식이 그대로 보존됨. 일정표와 함께 출장 승인요청 영어 메일 초안(.txt)도 같은 폴더에 자동 생성(Dear Kazuyuki/Kurata 앞, Main Projects 불릿+일정). 사용자가 출장 스케줄 만들어줘, 출장 일정표, business trip schedule, travel schedule excel, 출장 엑셀, 출장 메일 초안, 출장 승인 메일 등을 요청할 때 사용.
---

# Travel Schedule Excel

Turn a free-form trip description into **two deliverables**, both saved to the
`business_trip_output_root` folder:

1. An English `Business_trip` schedule **workbook (.xlsx)** — matching the
   company template exactly: Yu Gothic header, Arial body, horizontal hair grid,
   AM/PM two-row day blocks, no gridlines.
2. An English **approval-request e-mail draft (.txt)** — the mail Yejun sends to
   his manager to get the trip approved, built from the same itinerary so the two
   always agree. See **Approval mail draft (.txt)** below.

Given a rough itinerary, produce both by default.

## Output is always ENGLISH

The deliverable must be English regardless of input language. If the user
writes the itinerary in Korean/Japanese, **translate each agenda/venue into
concise English** (e.g. "포항으로 이동" → "Move to Pohang", "전략기획팀 미팅"
→ "Strategy & Planning Team Meeting").

## Workflow

1. **Read the user's itinerary prose** and extract (a) per day: the date, the
   AM item, the PM item, the venue, and any notes; and (b) for the mail:
   the destinations, the departing date, the approver (salutation), the section
   grouping label, and each activity's one-liner (+ purpose/PTJ if given). When a
   project is mentioned, **check its Obsidian overview note** for agenda detail
   and contract status — see **Referencing Obsidian project notes**.
2. **Resolve the year.** If the prose has no year, infer it from context
   (e.g. a folder name like `260615_Korea` → 2026); if still ambiguous, ask.
3. **Resolve the trip folder + countries.** Read the root from
   `business_trip_output_root:` in `%USERPROFILE%\.claude\skills\_config\local-paths.md`
   (PC마다 다름; 파일/키 없으면 사용자에게 물어 거기 저장 — `_config\README.md`). Both
   deliverables go into a **per-trip subfolder** under that root, named to match
   the existing folders — see **Trip folder naming** below. **List the existing
   folders first** and mirror their style; if one already fits this trip (same
   departing date), reuse it instead of making a new one. Create the folder if
   needed. Filenames inside: `Business_trip_<MonYYYY>(<countries>).xlsx` and
   `Business_trip_<MonYYYY>(<countries>)_approval.txt`. Ask only for the
   countries if not derivable from the itinerary.
4. **Write `schedule_data.json`** (shape below) next to the output file.
5. **Run** `scripts/generate_schedule.py <data.json> <output.xlsx>`.
6. **Write the approval-mail draft** to
   `<folder>\Business_trip_<MonYYYY>(<countries>)_approval.txt` per the
   **Approval mail draft (.txt)** section. Reuse the same day data so the mail's
   schedule matches the workbook.
7. **Review**: show the parsed table (Date / AM / PM / Venue / Notes), the mail
   draft body, and the judgment calls you made (inferred destinations, year,
   dinner→Notes, approver, section label, etc.) so the user can correct
   anything. Re-run if needed.

## Trip folder naming

Each trip is one subfolder under `business_trip_output_root`, holding the
schedule, the approval mail, and later the receipts/itineraries. Match the
existing convention — **always `Get-ChildItem <root> -Directory` first** and copy
the prevailing style, because it drifts over time.

    <YYMMDD>_<label>

- `YYMMDD` — the **departing date**, 6 digits, no separators (e.g. `260520`).
- `label` — destination or customer, following what's already there. Observed
  styles (all valid): country/city (`Korea`, `Tokyo`), customer (`POSCO`),
  multi-country (`KR, CN trip`), or `Trip to <place>` (`Trip to Korea`,
  `Trip to taiwan`). Generic fallbacks also exist: `Business trip`, `Home trip`.

Pick the label style that best fits the trip and looks like its neighbors — e.g.
a single-country Japan trip departing 2026-05-11 → `260511_Tokyo` or
`260511_Japan`; a two-country trip → `260415_Trip to taiwan`-style or
`260309_KR, CN trip`-style. If a folder for this departing date already exists,
reuse it. When the label is ambiguous, show the chosen name in the review step so
the user can rename.

## Data format (`schedule_data.json`)

```json
{
  "days": [
    {"iso": "2026-06-15", "venue": "Seoul", "notes": "",
     "am": "Move to Korea", "pm": "PTKR Monthly Meeting"},
    {"iso": "2026-06-19", "venue": "", "notes": "", "fullday": "Return to Japan"}
  ]
}
```

- `iso` — date as `YYYY-MM-DD`; the script computes the `Mon/D(DDD)` label and
  weekday automatically. **Don't compute weekdays yourself.**
- `am` / `pm` — agenda text for each half-day (either may be empty `""`).
- `fullday` — use instead of am/pm when one item spans the whole day.
- `venue`, `notes` — optional; leave `""` if absent.

## Approval mail draft (.txt)

Write an English **business-trip approval e-mail** to
`{business_trip_output_root}\Business_trip_<MonYYYY>(<countries>)_approval.txt`.
Learned from real examples in `reference/mail_example_1..4.txt` (examples 3 & 4
are transcriptions of screenshots the user sent). Fixed skeleton:

    <Salutation>,

    I am writing to seek approval for a business trip to <destinations>, departing <Mon/DD>, covering the following activities:

    <Section header>:

    •    <activity one-liner>      (repeat per activity)

    <schedule>

    Best regards,
    Yejun Kim

Rules:
- **Salutation** = the approver. Recent approvers: `Kazuyuki`, `Kurata`. Default
  `Dear Kazuyuki,`; keep whatever name the user gives.
- **destinations** — country/city list, e.g. `Japan (Tokyo)`, `Taiwan and Korea`,
  `Korea and China`. **departing** — the first day as `Mon/DD` (`May/11`,
  `Apr/15`, or spelled `March 9`).
- **Section header** — `Main Projects:` for contracted work, `Pre-Projects:`
  for before-contract pursuits. **`Pre-Projects` already means before contract —
  do NOT append `(before contract)`.** Split into both groups when the trip mixes
  them. Decide each activity's group from the Obsidian project note — see
  **Referencing Obsidian project notes**. Keep the user's own label if given.
- **Routine internal meetings are NOT projects.** A standing/internal meeting
  (e.g. PTKR Monthly Meeting) is **not** listed as a project bullet at all — omit
  it from the Main/Pre-Projects lists. It still appears in the day-by-day
  schedule, just not as a project line.
- **Activity bullets** — one line each, `•` prefix; put the counterpart engineer
  inline when known: `(with PTJ Kamoshita)`, `(with PTJ 4~5 engineers)`.

Two body styles — pick by how much detail the user gives:

**A. Bulleted + schedule** (default; matches examples 3 & 4) — one-line bullets,
then the full day-by-day schedule mirroring the workbook:

    Main Projects:

    •    POSCO P2H online meeting at POSCO's facility
    •    Poogsang F12 post-FAC meeting (work handover from Kobayashi)

    Schedule (see attached Business_trip_Mar2026(Korea, China).xlsx):
    Mar/9(Mon)  AM : Move to Korea   PM : P2H Online Meeting – Revamp concept sharing & Q&A
    Mar/10(Tue) AM : Move to Ulsan (Poongsan)   PM : Meeting with PSC
    ...

**B. Per-project detail** (when the user gives purpose/PTJ per project; matches
examples 1 & 2) — each project carries its own sub-bullets:

    Projects:

    •    Zhengrui Foil 2 – Project execution follow-up meeting with TEX and SEJAL
    o    Visit purpose : To discuss and align on pending execution items with TEX & SEJAL
    o    PTJ : Kobayashi Munehito
    o    Schedule
    5/11 AM : Move to Tokyo (morning)
         PM : Meeting with TEX & SEJAL

Schedule line format: `M/DD(DDD) AM : <am>   PM : <pm>`; a single-item day is
`M/DD(DDD) : <item>`. Reuse the AM/PM/weekday values already computed for the
workbook — **don't recompute weekdays.**

## Referencing Obsidian project notes

Yejun's projects each have an overview note in the Obsidian vault
(`vault_root:` in `_config\local-paths.md`). Use them to (a) fill in agenda
detail the user left vague and (b) classify each activity as Project vs
Pre-Project for the mail.

- **Find the note.** The overview note is `0_<project>.md`, e.g.
  `0_POSCO_K3C_Revamp.md`, `0_POSCO_P2H_Production.md`, `0_PSC_UL_CM_FM9.md`.
  Grep the vault for the line/project code (`K3CX`/`K3C`, `P2H`, `P3PL`, `FM9`,
  `JSW`, `Poongsan`/`PSC`, etc.). Only read to inform the schedule/mail — **never
  edit vault notes here.**
- **Contract status = Project vs Pre-Project.** The overview note tells you:
  - **Pre-Project** (before contract) — the note's activities live under a
    `## 2. Sales Activities (Before contract)` heading, or the text says
    `계약 전` / `개산견적·견적 단계` / has a future `계약타겟`/`Contract Target`.
    Also, PARA location `03. Resources` / `02. Areas` or a `견적/개산` stage → pre.
  - **Main Project** (contracted) — the note shows a booked order (수주/계약 완료,
    a real PO/Order code in execution), i.e. past the contract baseline.
  - When unsure, treat it as **Pre-Project** and flag it in the review step.
- **Enrich agenda wording** from the note's line name and scope (e.g. K3CX =
  POSCO Gwangyang No.3 CM Hyper UCM revamp) so venues/agendas read correctly —
  but keep the cell text concise. Don't invent facts not in the note or the
  user's prose.

## Parsing rules (match the template)

- **One block per day you list** = 2 rows (AM top, PM bottom). Days the user
  doesn't mention are simply skipped (no empty rows for weekends, etc.).
- **Agenda merges across the two rows** when the day has a single entry
  (`fullday`, or only one of am/pm). When both AM and PM have content, they go
  in separate rows. (The script handles this from the data — just fill am/pm
  vs fullday correctly.)
- **Date / Venue / Notes always merge** across the day's two rows.
- **Evening events → Notes** (e.g. "석식"/"저녁" → `"notes": "Dinner"`), not a
  PM agenda row, following the original template.
- **Specific clock times** (Time column is fixed AM/PM): embed the time in the
  agenda text, e.g. `"FM9 Project – Confirm direction (11:00)"`.
- A travel day that changes city → put both in venue, e.g. `"Seoul → Pohang"`.
- **Return day.** A trip ends with the flight home — add a final day as a
  `fullday` entry `"Return to Japan"`. If the user didn't give its date, ask or
  infer the day after the last activity; don't silently drop the return.
- **The Time column is NEVER merged.** Every day always shows `AM` and `PM` on
  two separate rows. "Merging" for a single-entry day (`fullday` or one of
  am/pm) applies to the **Agenda cell only** (D column, merged across the two
  rows); Date/Venue/Notes are also merged — but AM/PM stay two rows.

## How it's built

Blank-master copy + fill (formatting preserved 100%):

- `_templates/business_trip_master.xlsx` — header + styles only (regenerate with
  `scripts/build_master.py`). Keeps empty `Hotel` / `Visitors` sheets too.
- `scripts/generate_schedule.py` — copies the master and fills the `Schedule`
  sheet from the JSON, applying fonts, merges, and the horizontal grid.

Needs Python 3 with `openpyxl` — run with plain `python`; if the module is
missing on this PC: `python -m pip install openpyxl`.

## Reference

`reference/Business_trip_Mar2026(Korea, China).xlsx` — the original company
example this skill reproduces (source of all formatting values).
