# -*- coding: utf-8 -*-
"""
parse_cards.py — Remember(명함첩) export → structured contact records + dedup report.

Reads a Remember / Google-Contacts export (.xlsx or .csv), normalizes the company
name to a canonical vault Company + target folder (via reference/company_map.json),
and scans the existing '20. Contacts' vault folder to flag duplicates (by e-mail,
then by exact name appearing in a note).

It does NOT write any notes and does NOT romanize names — that is Claude's job,
done after the user confirms the report. This script only produces:
  - <out>/cards.json    : one record per card, with normalization + dedup status
  - <out>/report.md     : human-readable summary for the user to confirm

Usage:
  python parse_cards.py --export "<path to .xlsx/.csv>" \
      --vault "C:\\Users\\Z006K14G\\Desktop\\Yejun" \
      --out "<scratchpad dir>"

Dependencies: openpyxl (for .xlsx). csv is stdlib.
"""
import argparse, json, os, re, sys, glob

# ---- column header matching (Remember & Google Contacts variants) ---------
HEADER_KEYS = {
    "company": ["회사", "회사명", "company", "organization", "organization name"],
    "name":    ["이름", "성명", "name", "given name", "full name"],
    "dept":    ["부서", "department", "organization department"],
    "title":   ["직함", "직급", "title", "organization title", "job title"],
    "email":   ["전자 메일 주소", "이메일", "메일", "e-mail", "email", "e-mail 1 - value", "email 1 - value"],
    "mobile":  ["휴대폰", "휴대전화", "mobile", "핸드폰", "cell", "phone 1 - value"],
    "office":  ["근무처 전화", "직장 전화", "office", "work phone", "회사 전화"],
    "memo":    ["메모", "비고", "notes", "remark", "remarks"],
}

def norm_ws(s):
    return re.sub(r"\s+", " ", (s or "").strip())

def match_header(h):
    hl = norm_ws(h).lower()
    for field, keys in HEADER_KEYS.items():
        for k in keys:
            if hl == k.lower():
                return field
    # loose contains-match as fallback
    for field, keys in HEADER_KEYS.items():
        for k in keys:
            if k.lower() in hl:
                return field
    return None

def read_rows(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        rows = [[("" if c is None else str(c)) for c in r]
                for r in ws.iter_rows(values_only=True)]
    elif ext == ".csv":
        import csv
        # try utf-8-sig then cp949
        for enc in ("utf-8-sig", "cp949", "utf-8"):
            try:
                with open(path, encoding=enc, newline="") as f:
                    rows = [list(r) for r in csv.reader(f)]
                break
            except UnicodeDecodeError:
                continue
    else:
        raise SystemExit("Unsupported export type: %s (use .xlsx or .csv)" % ext)
    return rows

def load_company_map(skill_dir):
    p = os.path.join(skill_dir, "reference", "company_map.json")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    alias2canon = {}
    for entry in data["companies"]:
        for a in entry["aliases"]:
            alias2canon[norm_ws(a).lower()] = (entry["company"], entry["folder"])
    personal = set(norm_ws(x).lower() for x in data.get("personal_to_others", []))
    return alias2canon, personal

def normalize_company(raw, alias2canon, personal):
    key = norm_ws(raw).lower()
    if key == "" or key in personal:
        return ("", "Others", "personal_or_unknown")
    if key in alias2canon:
        c, f = alias2canon[key]
        return (c, f, "mapped")
    # unknown — flag for user; default folder = the raw company (Claude/user decides)
    return (norm_ws(raw), norm_ws(raw), "UNKNOWN")

# ---- dedup: scan existing contact notes -----------------------------------
EMAIL_RE = re.compile(r"^##\s*3\.\s*E-?mail\s*:?\s*(.+)$", re.IGNORECASE | re.MULTILINE)

def scan_vault(contacts_dir):
    """Return list of (filepath, filename, email, fulltext)."""
    notes = []
    for p in glob.glob(os.path.join(contacts_dir, "**", "*.md"), recursive=True):
        try:
            with open(p, encoding="utf-8") as f:
                txt = f.read()
        except Exception:
            continue
        m = EMAIL_RE.search(txt)
        email = norm_ws(m.group(1)).lower() if m else ""
        notes.append((p, os.path.splitext(os.path.basename(p))[0], email, txt))
    return notes

def find_dup(email, name, notes):
    email = norm_ws(email).lower()
    name = norm_ws(name)
    # 1) e-mail exact match (strongest)
    if email:
        for p, fn, e, txt in notes:
            if e and e == email:
                return {"by": "email", "file": p, "filename": fn}
    # 2) exact name string appears in a note body (Korean/Japanese原文)
    if name:
        for p, fn, e, txt in notes:
            if name and name in txt:
                return {"by": "name", "file": p, "filename": fn}
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    contacts_dir = os.path.join(args.vault, "20. Contacts")
    os.makedirs(args.out, exist_ok=True)

    rows = read_rows(args.export)
    if not rows:
        raise SystemExit("Empty export.")
    header = rows[0]
    colmap = {}
    for i, h in enumerate(header):
        f = match_header(h)
        if f and f not in colmap:
            colmap[f] = i

    alias2canon, personal = load_company_map(skill_dir)
    notes = scan_vault(contacts_dir)

    cards = []
    for ridx, r in enumerate(rows[1:], start=2):
        def g(field):
            i = colmap.get(field)
            return norm_ws(r[i]) if (i is not None and i < len(r)) else ""
        raw_company = g("company")
        name = g("name")
        if not name and not g("email"):
            continue  # skip blank rows
        company, folder, cstatus = normalize_company(raw_company, alias2canon, personal)
        email = g("email")
        dept = g("dept")
        title = g("title")
        mobile = g("mobile")
        office = g("office")
        dup = find_dup(email, name, notes)
        cards.append({
            "row": ridx,
            "raw_company": raw_company,
            "company": company,
            "folder": folder,
            "company_status": cstatus,
            "name": name,
            "dept": dept,
            "title": title,
            "email": email,
            "mobile": mobile,
            "office": office,
            "phone": mobile or office,
            "memo": g("memo"),
            "duplicate": dup,
        })

    with open(os.path.join(args.out, "cards.json"), "w", encoding="utf-8") as f:
        json.dump({"export": args.export, "count": len(cards), "cards": cards},
                  f, ensure_ascii=False, indent=2)

    # ---- report.md ----
    L = []
    L.append("# 명함 임포트 리포트 (%d건)\n" % len(cards))
    L.append("소스: `%s`\n" % args.export)
    unknown = [c for c in cards if c["company_status"] == "UNKNOWN"]
    dups = [c for c in cards if c["duplicate"]]
    news = [c for c in cards if not c["duplicate"]]
    L.append("- 신규(추정): **%d** / 중복(추정): **%d** / 미매핑 회사: **%d**\n"
             % (len(news), len(dups), len(unknown)))
    if unknown:
        L.append("## ⚠ 미매핑 회사 (company_map.json에 추가 필요)")
        for c in sorted(set(c["raw_company"] for c in unknown)):
            L.append("- `%s`" % c)
        L.append("")
    L.append("## 회사별")
    by_folder = {}
    for c in cards:
        by_folder.setdefault(c["folder"], []).append(c)
    for folder in sorted(by_folder):
        L.append("\n### %s (%d)" % (folder, len(by_folder[folder])))
        for c in by_folder[folder]:
            flag = ""
            if c["duplicate"]:
                flag = " 🔁중복→ `%s`" % c["duplicate"]["filename"]
            title = (", " + c["title"]) if c["title"] else ""
            L.append("- **%s**%s — %s%s%s"
                     % (c["name"], title, c["email"] or "(이메일없음)",
                        (" · " + c["dept"]) if c["dept"] else "", flag))
    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print("cards:", len(cards), "| new:", len(news),
          "| dup:", len(dups), "| unknown-company:", len(unknown))
    print("wrote:", os.path.join(args.out, "cards.json"))
    print("wrote:", os.path.join(args.out, "report.md"))

if __name__ == "__main__":
    main()
