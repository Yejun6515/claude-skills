# -*- coding: utf-8 -*-
"""
write_notes.py — create/merge Obsidian contact notes from a notes.json plan.

Claude produces notes.json (after the user confirms the parse report), giving the
final romanized filename, English description, Team, Name & Title, e-mail, phone,
and remarks for each card. This script does the mechanical file I/O:

  - status "new"   : create '20. Contacts/<folder>/<filename>.md' (folder made if
                     missing). If the file already exists it is SKIPPED (never
                     overwritten) and reported, unless --overwrite is passed.
  - status "merge" : open the existing note at "merge_file" and fill ONLY empty
                     '## 3. E-mail :' / '## 4. Phone number :' lines. All other
                     content (description, Team, Name & Title, Remarks, mail-bridge
                     history) is left untouched. Reports each field filled.

Files are written BOM-less UTF-8 with LF newlines.

notes.json schema:
{
  "cards": [
    {
      "status": "new" | "merge",
      "folder": "Sendzimir",              // new only
      "filename": "Kuchi Masahiro",       // new only (no .md)
      "company": "Sendzimir",             // new only
      "description": "one-line english",  // new only
      "team": "...",                      // new only  -> ## 1. Team :
      "name_title": "口 昌宏, DIRECTOR",   // new only  -> ## 2. Name & Title :
      "email": "kuchi@sendzimir.co.jp",
      "phone": "+81 3-6222-9650",
      "remarks": "",                       // new only, optional body under ## 5.
      "merge_file": "C:/.../Sung Yura.md"  // merge only (absolute path)
    }
  ]
}

Usage:
  python write_notes.py --plan "<notes.json>" --vault "C:\\Users\\Z006K14G\\Desktop\\Yejun" [--overwrite] [--dry-run]
"""
import argparse, json, os, re

def w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def build_new(c):
    lines = []
    lines.append("---")
    lines.append("Company: %s" % c.get("company", ""))
    desc = (c.get("description") or "").replace('"', "'")
    lines.append('description: "%s"' % desc)
    lines.append("---")
    lines.append("")
    lines.append("## 1. Team : %s" % c.get("team", ""))
    lines.append("")
    lines.append("## 2. Name & Title : %s" % c.get("name_title", ""))
    lines.append("")
    lines.append("## 3. E-mail : %s" % c.get("email", ""))
    lines.append("")
    lines.append("## 4. Phone number : %s" % c.get("phone", ""))
    lines.append("")
    lines.append("## 5. Remarks")
    rem = (c.get("remarks") or "").strip()
    if rem:
        lines.append("")
        lines.append(rem)
    lines.append("")
    return "\n".join(lines)

# NOTE: use [ \t]* (not \s*) after the colon so the trailing newline / blank line
# between sections is NOT consumed — otherwise the merge collapses the template's
# blank-line spacing between ## sections.
EMPTY_EMAIL = re.compile(r"^(##[ \t]*3\.[ \t]*E-?mail[ \t]*:)[ \t]*$", re.IGNORECASE | re.MULTILINE)
EMPTY_PHONE = re.compile(r"^(##[ \t]*4\.[ \t]*Phone number[ \t]*:)[ \t]*$", re.IGNORECASE | re.MULTILINE)

def merge_into(path, email, phone, dry):
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    changes = []
    if email and EMPTY_EMAIL.search(txt):
        txt = EMPTY_EMAIL.sub(lambda m: "%s %s" % (m.group(1), email), txt, count=1)
        changes.append("email=" + email)
    if phone and EMPTY_PHONE.search(txt):
        txt = EMPTY_PHONE.sub(lambda m: "%s %s" % (m.group(1), phone), txt, count=1)
        changes.append("phone=" + phone)
    if changes and not dry:
        w(path, txt)
    return changes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    plan = json.load(open(args.plan, encoding="utf-8"))
    contacts = os.path.join(args.vault, "20. Contacts")
    created, skipped, merged, nochange = [], [], [], []

    for c in plan["cards"]:
        if c["status"] == "new":
            folder = os.path.join(contacts, c["folder"])
            path = os.path.join(folder, c["filename"] + ".md")
            if os.path.exists(path) and not args.overwrite:
                skipped.append(path); continue
            if not args.dry_run:
                os.makedirs(folder, exist_ok=True)
                w(path, build_new(c))
            created.append(path)
        elif c["status"] == "merge":
            ch = merge_into(c["merge_file"], c.get("email", ""), c.get("phone", ""), args.dry_run)
            if ch:
                merged.append((c["merge_file"], ch))
            else:
                nochange.append(c["merge_file"])

    print("CREATED (%d):" % len(created))
    for p in created: print("  +", p)
    if skipped:
        print("SKIPPED-exists (%d):" % len(skipped))
        for p in skipped: print("  =", p)
    print("MERGED (%d):" % len(merged))
    for p, ch in merged: print("  ~", p, "->", ", ".join(ch))
    if nochange:
        print("MERGE no-op (already filled) (%d):" % len(nochange))
        for p in nochange: print("  .", p)
    if args.dry_run:
        print("\n[DRY RUN — no files written]")

if __name__ == "__main__":
    main()
