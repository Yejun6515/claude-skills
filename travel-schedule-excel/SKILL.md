---
name: travel-schedule-excel
description: 출장 스케줄 Excel 작성. 출장 일정을 글(prose)로 주면 Business_trip 양식 그대로 영어 일정표(.xlsx)를 생성. 하루=AM/PM 2행, 날짜·요일 자동 계산, 단일 항목 Agenda 병합, 저녁 일정은 Notes. 빈 마스터 복사·채우기 방식이라 테두리·폰트·병합 서식이 그대로 보존됨. 사용자가 출장 스케줄 만들어줘, 출장 일정표, business trip schedule, travel schedule excel, 출장 엑셀 등을 요청할 때 사용.
---

# Travel Schedule Excel

Turn a free-form trip description into an English `Business_trip` schedule
workbook (.xlsx), matching the company template exactly: Yu Gothic header,
Arial body, horizontal hair grid, AM/PM two-row day blocks, no gridlines.

## Output is always ENGLISH

The deliverable must be English regardless of input language. If the user
writes the itinerary in Korean/Japanese, **translate each agenda/venue into
concise English** (e.g. "포항으로 이동" → "Move to Pohang", "전략기획팀 미팅"
→ "Strategy & Planning Team Meeting").

## Workflow

1. **Read the user's itinerary prose** and extract, per day: the date, the
   AM item, the PM item, the venue, and any notes.
2. **Resolve the year.** If the prose has no year, infer it from context
   (e.g. a folder name like `260615_Korea` → 2026); if still ambiguous, ask.
3. **Confirm save folder + countries** for the filename (default:
   `Business_trip_<MonYYYY>(<countries>).xlsx`). Ask if not given.
4. **Write `schedule_data.json`** (shape below) next to the output file.
5. **Run** `scripts/generate_schedule.py <data.json> <output.xlsx>`.
6. **Review**: show the parsed table (Date / AM / PM / Venue / Notes) and the
   judgment calls you made (inferred destinations, year, dinner→Notes, etc.)
   so the user can correct anything. Re-run if needed.

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

## How it's built

Blank-master copy + fill (formatting preserved 100%):

- `_templates/business_trip_master.xlsx` — header + styles only (regenerate with
  `scripts/build_master.py`). Keeps empty `Hotel` / `Visitors` sheets too.
- `scripts/generate_schedule.py` — copies the master and fills the `Schedule`
  sheet from the JSON, applying fonts, merges, and the horizontal grid.

Needs Python with `openpyxl` (system Python has it:
`C:\Users\Z006K14G\AppData\Local\Programs\Python\Python312`).

## Reference

`reference/Business_trip_Mar2026(Korea, China).xlsx` — the original company
example this skill reproduces (source of all formatting values).
