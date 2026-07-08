# -*- coding: utf-8 -*-
"""Extract full mails (with body) for specific ids from a _headers.txt index.

Uses the `extract_msg` library (pip install extract-msg) — reads .msg files
directly, NO Outlook COM. Preferred over extract_msg_by_id.ps1: COM hangs
indefinitely on some messages (S/MIME signed etc.); this never does.

Usage:
  python extract_msg_by_id.py --headers "<_headers.txt>" --base "<folder>" --ids "12,45,301" [--maxbody 2500] [--out bodies.txt]
Output goes to --out if given, else stdout (UTF-8).
"""
import argparse, io, re, sys
import extract_msg

p = argparse.ArgumentParser()
p.add_argument('--headers', required=True)
p.add_argument('--base', required=True)
p.add_argument('--ids', required=True, help='comma-separated ids from _headers.txt (#NN)')
p.add_argument('--maxbody', type=int, default=2500)
p.add_argument('--out', default=None)
a = p.parse_args()

ids = [int(x) for x in a.ids.split(',') if x.strip()]
idmap = {}
with open(a.headers, encoding='utf-8') as f:
    for ln in f:
        m = re.match(r'^#(\d+) \| (.+)$', ln.rstrip('\n'))
        if m and int(m.group(1)) in ids:
            idmap[int(m.group(1))] = m.group(2)

out = open(a.out, 'w', encoding='utf-8') if a.out else io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for i in ids:
    if i not in idmap:
        out.write(f"== #{i} NOT FOUND in headers ==\n\n"); continue
    path = a.base.rstrip('\\/') + '\\' + idmap[i]
    try:
        msg = extract_msg.openMsg(path)
        body = msg.body or ''
        if not body.strip() and getattr(msg, 'htmlBody', None):
            hb = msg.htmlBody
            if isinstance(hb, bytes):
                hb = hb.decode('utf-8', errors='replace')
            body = re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', hb))
        body = re.sub(r'\r\n', '\n', body).strip()
        note = ''
        if a.maxbody > 0 and len(body) > a.maxbody:
            note = f"\n... [TRUNCATED at {a.maxbody}, full={len(body)}]"
            body = body[:a.maxbody]
        atts = [x.longFilename or x.shortFilename or '?' for x in msg.attachments]
        atts = [x for x in atts if not re.match(r'^image\d+\.(png|jpe?g|gif)$', str(x), re.I)]
        out.write(f"========== #{i} | {idmap[i]} ==========\n")
        out.write(f"SUBJECT: {msg.subject}\nFROM: {msg.sender}\nTO: {msg.to}\nCC: {msg.cc}\nSENT: {msg.date}\n")
        if atts: out.write(f"ATT: {'; '.join(map(str, atts))}\n")
        out.write(f"---- BODY ----\n{body}{note}\n\n")
        msg.close()
    except Exception as e:
        out.write(f"== #{i} FAILED: {type(e).__name__}: {e} ==\n\n")
if a.out: out.close()
