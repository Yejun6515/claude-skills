# -*- coding: utf-8 -*-
"""Match sent mails to received mails by normalized subject and build triage lists.

Reads a _headers.txt produced by extract_msg_headers.py/.ps1 where ids under
'받은 메일\\' are received and '보낸 메일\\' are sent. Writes:
  _match_report.txt — per sent mail: To/CC + matched received (id, date, FROM)
  _triage.txt       — MATCHED SENT (one line each) / UNMATCHED SENT / RECEIVED WITHOUT REPLY

Usage: python match_triage.py --headers "<_headers.txt>" --outdir "<folder>"
"""
import argparse, re
from collections import defaultdict

p = argparse.ArgumentParser()
p.add_argument('--headers', required=True)
p.add_argument('--outdir', required=True)
a = p.parse_args()

mails = {}  # id -> dict
cur = None
with open(a.headers, encoding='utf-8') as f:
    for ln in f:
        m = re.match(r'^#(\d+) \| (.+)$', ln.rstrip('\n'))
        if m:
            cur = {'id': int(m.group(1)), 'path': m.group(2), 'subj': '', 'from': '', 'to': '', 'cc': '', 'sent': '', 'failed': False}
            mails[cur['id']] = cur
            continue
        if cur is None: continue
        s = ln.rstrip('\n')
        if s.startswith('  SUBJ: '): cur['subj'] = s[8:]
        elif s.startswith('  FROM: '): cur['from'] = s[8:]
        elif s.startswith('  TO: '): cur['to'] = s[6:]
        elif s.startswith('  CC: '): cur['cc'] = s[6:]
        elif s.startswith('  SENT: '): cur['sent'] = s[8:]
        elif s.startswith('  !! FAILED'): cur['failed'] = True

def norm(subj):
    s = subj or ''
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'^\s*((RE|FW|FWD|Fw|Re|回复|答复|자동\s*회신|자동\s*응답)\s*:|EXT\s*:)\s*', '', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip().lower()

recv = [m for m in mails.values() if m['path'].startswith('받은 메일') and not m['failed']]
sent = [m for m in mails.values() if m['path'].startswith('보낸 메일') and not m['failed']]
failed = [m for m in mails.values() if m['failed']]

ridx = defaultdict(list)
for r in recv: ridx[norm(r['subj'])].append(r)

def fromshort(r):
    f = r['from'] or ''
    f = re.sub(r'\s*<[^>]*>?\s*$', '', f).strip().strip('"')
    return f or '?'

matched, unmatched = [], []
matched_recv_ids = set()
for s in sorted(sent, key=lambda x: x['sent']):
    partners = sorted(ridx.get(norm(s['subj']), []), key=lambda x: x['sent'])
    if partners:
        matched.append((s, partners))
        matched_recv_ids.update(r['id'] for r in partners)
    else:
        unmatched.append(s)

with open(a.outdir.rstrip('\\/') + r'\_match_report.txt', 'w', encoding='utf-8') as out:
    for s, partners in matched:
        out.write(f"[S#{s['id']}] {s['sent']} | {s['subj']}\n")
        out.write(f"   sent-> TO: {s['to']} | CC: {s['cc']}\n")
        for r in partners:
            out.write(f"   <-[R#{r['id']}] {r['sent']} | FROM: {r['from'][:160]}\n")
        out.write('\n')

with open(a.outdir.rstrip('\\/') + r'\_triage.txt', 'w', encoding='utf-8') as out:
    out.write('== MATCHED SENT (one line: S#id | date | recvFroms => subj) ==\n')
    for s, partners in matched:
        froms = []
        for r in partners:
            fs = fromshort(r)
            if fs not in froms: froms.append(fs)
        out.write(f"S#{s['id']}|{s['sent']}|x{len(partners)}[{','.join(froms[:5])}] => {s['subj']}\n")
    out.write('\n== UNMATCHED SENT ==\n')
    for s in unmatched:
        out.write(f"S#{s['id']}|{s['sent']} => {s['subj']}\n")
    out.write('\n== RECEIVED WITHOUT REPLY (R#id | from => subj) ==\n')
    for r in sorted(recv, key=lambda x: x['sent']):
        if r['id'] not in matched_recv_ids:
            out.write(f"R#{r['id']}|{fromshort(r)} => {r['subj']}\n")
    if failed:
        out.write('\n== FAILED TO READ ==\n')
        for m in failed:
            out.write(f"#{m['id']} {m['path']}\n")

print(f"sent={len(sent)} recv={len(recv)} matched_sent={len(matched)} unmatched_sent={len(unmatched)} failed={len(failed)}")
