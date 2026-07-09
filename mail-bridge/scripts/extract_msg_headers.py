# -*- coding: utf-8 -*-
"""Extract HEADERS ONLY from .msg files under a folder (recursive) — python
extract_msg version of extract_msg_headers.ps1. No Outlook COM, no hang, ~5-10x faster.
Output format is identical (#N | relpath / SUBJ / FROM / TO / CC / SENT / ATT).

Usage: python extract_msg_headers.py --folder "<folder>" --out "<_headers.txt>"
"""
import argparse, os, re
import extract_msg

p = argparse.ArgumentParser()
p.add_argument('--folder', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()

root = a.folder.rstrip('\\/')
files = []
for dp, _, fns in os.walk(root):
    for fn in fns:
        if fn.lower().endswith('.msg'):
            files.append(os.path.join(dp, fn))
files.sort()

with open(a.out, 'w', encoding='utf-8') as out:
    for i, full in enumerate(files, 1):
        rel = full[len(root) + 1:]
        try:
            msg = extract_msg.openMsg(full)
            atts = [x.longFilename or x.shortFilename or '?' for x in msg.attachments]
            atts = [x for x in atts if not re.match(r'^image\d+\.(png|jpe?g|gif)$', str(x), re.I)]
            out.write(f"#{i} | {rel}\n")
            out.write(f"  SUBJ: {msg.subject}\n")
            out.write(f"  FROM: {msg.sender}\n")
            out.write(f"  TO: {msg.to}\n")
            if msg.cc: out.write(f"  CC: {msg.cc}\n")
            out.write(f"  SENT: {msg.date}\n")
            if atts: out.write(f"  ATT: {'; '.join(map(str, atts))}\n")
            msg.close()
        except Exception as e:
            out.write(f"#{i} | {rel}\n  !! FAILED: {type(e).__name__}: {e}\n")
# NOTE: keep this ASCII-only — stdout may be cp932/cp949 and non-ASCII paths crash print()
print(f"OK: {len(files)} mails indexed")
