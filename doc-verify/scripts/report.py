#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
doc-verify / report.py  —  검증 결과 -> Primetals 브랜드 HTML (자기완결 단일파일)

입력은 JSON 하나. verify.py 가 낸 기계 findings 와, Claude 가 폴더 자료를 읽고 판단한
컨텍스트 findings 를 합쳐서 넣는다.

  python report.py <input.json> <out.html>

입력 스키마 (없는 키는 생략 가능):
{
  "title":   "POSCO P3ZRM ARCC NDA 최종본",
  "subtitle":"제출 전 검증",
  "target":  "260803_...docx",            # 검증 대상
  "purpose": "고객사 제출" | "내부 승인" | "사내 보고",
  "context_files": ["같이 읽은 자료1", ...],
  "unreadable":    ["스캔이라 못 읽은 파일", ...],
  "summary": ["한 줄 요약", ...],
  "findings": [
     {"severity":"FAIL|CHECK|INFO|OK", "kind":"합계", "loc":"...",
      "msg":"...", "detail":"...", "source":"script|context"}
  ],
  "checked":   [["검산 항목","결과"], ...],     # 통과한 것 — 무엇을 봤는지 보여주는 용도
  "checklist": [{"item":"...","detail":"...","owner":"...","status":"MUST FIX|CONFIRM|OPEN"}]
}
"""
import sys, json, html, io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CSS = """
:root{--navy:#0C2340;--orange:#E87722;--teal:#00587C;--steel:#425563;--ink:#000;
      --mut:#97999B;--green:#7A9A01;--red:#CE0037;--line:#D0D0CE;--line2:#ECECEA;
      --bg:#F4F5F5;--card:#fff}
*{box-sizing:border-box}
body{margin:0;font-family:Arial,"Malgun Gothic",sans-serif;background:var(--bg);color:var(--ink);
     line-height:1.65;font-size:15px}
.wrap{max-width:1020px;margin:0 auto;padding:0 22px 70px}
header.top{background:linear-gradient(135deg,#0C2340,#163a5c);color:#fff;padding:32px 22px 26px;
     margin-bottom:24px;border-bottom:4px solid var(--orange)}
header.top .inner{max-width:1020px;margin:0 auto}
header.top .kicker{font-size:12.5px;letter-spacing:1.5px;color:#E87722;text-transform:uppercase;margin-bottom:8px}
header.top h1{margin:0;font-size:24px;font-weight:700;letter-spacing:-.3px}
header.top .sub{margin-top:9px;font-size:13.5px;color:#C7CDD4}
header.top .meta{margin-top:13px;font-size:12.5px;color:#9AA6B2;display:flex;gap:18px;flex-wrap:wrap}
h2{font-size:19px;color:var(--navy);margin:32px 0 12px;padding-bottom:7px;border-bottom:2px solid var(--line);
   display:flex;align-items:center;gap:9px}
h2 .n{background:var(--orange);color:#fff;font-size:13px;width:24px;height:24px;border-radius:6px;
      display:inline-flex;align-items:center;justify-content:center;font-weight:700}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0;
      box-shadow:0 1px 2px rgba(12,35,64,.05)}
.summary{border-left:4px solid var(--orange)}
.scoreboard{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}
.score{flex:1;min-width:130px;background:#fff;border:1px solid var(--line);border-radius:12px;
       padding:14px 16px;text-align:center}
.score .v{font-size:30px;font-weight:700;line-height:1.1}
.score .l{font-size:12px;color:var(--mut);margin-top:4px;letter-spacing:.5px}
.score.fail .v{color:var(--red)} .score.check .v{color:var(--orange)}
.score.info .v{color:var(--teal)} .score.ok .v{color:var(--green)}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:13.5px;background:#fff;
      border-radius:10px;overflow:hidden;border:1px solid var(--line)}
th{background:#F2F2F1;color:var(--navy);text-align:left;padding:9px 11px;font-weight:700;font-size:13px;
   border-bottom:1px solid var(--line)}
td{padding:9px 11px;border-bottom:1px solid var(--line2);vertical-align:top}
tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:#FAFAF9}
.tag{display:inline-block;font-size:11.5px;padding:2px 9px;border-radius:20px;font-weight:600;white-space:nowrap}
.t-fail{background:#FBE3E9;color:var(--red)}
.t-check{background:#FCEBDD;color:#C25E15}
.t-info{background:#E4F2F8;color:var(--teal)}
.t-ok{background:#EFF3DC;color:#5E7A00}
.t-src{background:#EFEFEE;color:#6B6D6F}
.loc{font-size:12px;color:var(--mut);white-space:nowrap}
.detail{font-size:12.5px;color:var(--steel);margin-top:4px;word-break:break-word}
code{background:#F0F1F1;border-radius:4px;padding:1px 6px;font-size:12.5px;color:var(--navy)}
.callout{background:#FCF4EC;border:1px solid #F2D9C0;border-left:4px solid var(--orange);
         border-radius:10px;padding:13px 17px;margin:13px 0;font-size:14px}
.callout.red{background:#FBEEF1;border-color:#F0CBD5;border-left-color:var(--red)}
.callout.green{background:#F3F6E6;border-color:#DCE5BC;border-left-color:var(--green)}
ul{margin:8px 0 8px 4px;padding-left:20px} li{margin:5px 0}
.files{font-size:12.5px;color:var(--steel)}
.files span{display:inline-block;background:#EFEFEE;border-radius:5px;padding:2px 8px;margin:3px 4px 0 0}
.foot{margin-top:32px;padding-top:15px;border-top:1px solid var(--line);font-size:12px;color:var(--mut)}
"""

SEV = {"FAIL": ("t-fail", "FAIL"), "CHECK": ("t-check", "CHECK"),
       "INFO": ("t-info", "INFO"), "OK": ("t-ok", "OK")}
STATUS = {"MUST FIX": "t-fail", "CONFIRM": "t-check", "OPEN": "t-info", "DONE": "t-ok"}


def e(s):
    return html.escape("" if s is None else str(s))


def build(d):
    o = io.StringIO()
    w = o.write
    fnd = d.get("findings") or []
    n = {k: sum(1 for f in fnd if f.get("severity") == k) for k in SEV}

    w('<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    w("<title>%s</title><style>%s</style></head><body>" % (e(d.get("title", "검증 결과")), CSS))

    w('<header class="top"><div class="inner">')
    w('<div class="kicker">Primetals Technologies · %s 검증</div>'
      % e(d.get("purpose", "제출 전")))
    w("<h1>%s</h1>" % e(d.get("title", "검증 결과")))
    if d.get("subtitle"):
        w('<div class="sub">%s</div>' % e(d["subtitle"]))
    w('<div class="meta">')
    for k in ("target", "date", "verifier"):
        if d.get(k):
            lab = {"target": "대상", "date": "검증일", "verifier": "검증"}[k]
            w("<span>%s : %s</span>" % (lab, e(d[k])))
    w("</div></div></header><div class='wrap'>")

    # 점수판
    w('<div class="scoreboard">')
    for key, lab in (("FAIL", "고쳐야 함"), ("CHECK", "확인 필요"), ("INFO", "참고"), ("OK", "검산 통과")):
        w('<div class="score %s"><div class="v">%d</div><div class="l">%s</div></div>'
          % (key.lower(), n[key], lab))
    w("</div>")

    if d.get("summary"):
        w('<div class="card summary"><h3 style="margin-top:0;font-size:15.5px;color:#425563">핵심 요약</h3><ul>')
        for s in d["summary"]:
            w("<li>%s</li>" % s)          # 요약은 굵게/링크 등 인라인 HTML 허용
        w("</ul></div>")

    # 무엇을 근거로 봤는가
    if d.get("context_files") or d.get("unreadable"):
        w('<h2><span class="n">0</span>검증 근거</h2><div class="card">')
        if d.get("context_files"):
            w('<div class="files"><b>같이 읽은 자료</b><br>')
            for f in d["context_files"]:
                w("<span>%s</span>" % e(f))
            w("</div>")
        if d.get("unreadable"):
            w('<div class="callout red" style="margin-bottom:0"><b>읽지 못한 자료 — 대조에서 빠졌음</b><ul>')
            for f in d["unreadable"]:
                w("<li>%s</li>" % e(f))
            w("</ul></div>")
        w("</div>")

    # 지적 사항
    sec = 1
    for key, title in (("FAIL", "고쳐야 할 것"), ("CHECK", "확인이 필요한 것"), ("INFO", "참고")):
        rows = [f for f in fnd if f.get("severity") == key]
        if not rows:
            continue
        w('<h2><span class="n">%d</span>%s <span style="font-size:14px;color:#97999B">(%d건)</span></h2>'
          % (sec, e(title), len(rows)))
        sec += 1
        w("<table><thead><tr><th style='width:78px'>구분</th><th style='width:150px'>위치</th>"
          "<th>내용</th><th style='width:74px'>출처</th></tr></thead><tbody>")
        for f in rows:
            cls, lab = SEV[key]
            src = "자료 대조" if f.get("source") == "context" else "자동 검산"
            w("<tr><td><span class='tag %s'>%s</span><div style='margin-top:4px;font-size:11.5px;color:#97999B'>%s</div></td>"
              % (cls, lab, e(f.get("kind", ""))))
            w("<td class='loc'>%s</td><td>%s" % (e(f.get("loc", "")), e(f.get("msg", ""))))
            if f.get("detail"):
                w("<div class='detail'><code>%s</code></div>" % e(f["detail"]))
            w("</td><td><span class='tag t-src'>%s</span></td></tr>" % e(src))
        w("</tbody></table>")

    # 검산 통과 — 무엇을 실제로 봤는지 보여준다
    oks = [f for f in fnd if f.get("severity") == "OK"]
    if oks or d.get("checked"):
        w('<h2><span class="n">%d</span>검산 통과 — 실제로 확인한 것</h2>' % sec)
        sec += 1
        w("<table><thead><tr><th style='width:110px'>항목</th><th style='width:190px'>위치</th>"
          "<th>확인 내용</th></tr></thead><tbody>")
        for f in oks:
            w("<tr><td>%s</td><td class='loc'>%s</td><td>%s</td></tr>"
              % (e(f.get("kind", "")), e(f.get("loc", "")), e(f.get("msg", ""))))
        for row in (d.get("checked") or []):
            w("<tr><td>%s</td><td class='loc'>-</td><td>%s</td></tr>" % (e(row[0]), e(row[1])))
        w("</tbody></table>")

    # 체크리스트
    if d.get("checklist"):
        w('<h2><span class="n">%d</span>제출 전 체크리스트</h2>' % sec)
        w("<table><thead><tr><th style='width:34px'>#</th><th style='width:210px'>항목</th>"
          "<th>내용</th><th style='width:110px'>담당</th><th style='width:88px'>상태</th></tr></thead><tbody>")
        for i, c in enumerate(d["checklist"], 1):
            cls = STATUS.get(c.get("status", ""), "t-info")
            w("<tr><td>%d</td><td><b>%s</b></td><td>%s</td><td>%s</td>"
              "<td><span class='tag %s'>%s</span></td></tr>"
              % (i, e(c.get("item", "")), e(c.get("detail", "")), e(c.get("owner", "")),
                 cls, e(c.get("status", ""))))
        w("</tbody></table>")

    if not fnd:
        w('<div class="callout green"><b>지적 사항 없음.</b> 다만 자동 검산이 닿지 않는 항목이 '
          '있을 수 있으니 위 "검증 근거"에서 무엇을 읽었는지 확인할 것.</div>')

    w('<div class="foot">doc-verify · 자동 검산은 결정론적 계산만 수행하며, 자료 대조 항목은 판단이 '
      '포함되어 있다. 최종 판단은 사용자가 한다.<br>'
      'Restricted © Primetals Technologies 2021-2026. All rights reserved.</div>')
    w("</div></body></html>")
    return o.getvalue()


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: report.py <input.json> <out.html>")
    with open(sys.argv[1], encoding="utf-8") as fh:
        d = json.load(fh)
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        fh.write(build(d))
    print("WROTE:", sys.argv[2])


if __name__ == "__main__":
    main()
