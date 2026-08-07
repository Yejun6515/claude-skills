# -*- coding: utf-8 -*-
r"""단어정리 txt → 누적 단어장(_tts단어장.csv) 기록.

사용법:
  python record_vocab.py "<YYMMDD_단어정리.txt>" [--date YYYY-MM-DD] [--source "출처문구"]
                                                  [--mp3-dir "<mp3 폴더>"]

- 단어정리 txt(스마트 글라스용) 블록을 파싱해 CSV에 append 한다.
  블록 형식:  `N. 単語 (よみ)` / 뜻 / (한자 훈음…) / 빈 줄
- 이미 단어장에 있는 단어는 스킵(단어 기준 중복 제거).
- --date 생략 시 파일명 앞 YYMMDD에서 유추, --source 생략 시 "YYMMDD 단어 배치".
- --mp3-dir 주면 `N. 単語.mp3` 존재 여부를 확인해 없는 것만 경고(기록은 그대로 진행).
- CSV 정본 경로는 _config\vocab_db.py 가 vault_root 기준으로 계산한다.

※ 다른 PC의 단어장을 옮길 때는 **덮어쓰지 말고 행 합치기(단어 기준 중복 제거)**.
"""
import argparse
import csv
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.expanduser(r"~\.claude\skills\_config"))
from vocab_db import vocab_csv_path, load_done_words  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("txt", help="YYMMDD_단어정리.txt 경로")
ap.add_argument("--date", help="생성일 YYYY-MM-DD (기본: 파일명 YYMMDD)")
ap.add_argument("--source", help="출처 문구 (기본: 'YYMMDD 단어 배치')")
ap.add_argument("--mp3-dir", help="mp3 폴더 (주면 존재 여부 검증)")
args = ap.parse_args()

TXT = Path(args.txt)
if not TXT.exists():
    sys.exit(f"단어정리 txt 없음: {TXT}")

m6 = re.match(r"(\d{6})", TXT.name)
yymmdd = m6.group(1) if m6 else ""
if args.date:
    date = args.date
elif yymmdd:
    date = f"20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"
else:
    sys.exit("--date 를 지정하세요 (파일명에서 YYMMDD 를 찾지 못함).")
source = args.source or (f"{yymmdd} 단어 배치" if yymmdd else "단어 배치")

rows = []
for block in TXT.read_text(encoding="utf-8").split("\n\n"):
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if not lines:
        continue
    m = re.match(r"^(\d+)\.\s+(.+?)(?:\s+\((.+?)\))?\s*$", lines[0])
    if not m:
        sys.exit(f"파싱 실패: {lines[0]}")
    idx, word, reading = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
    meaning = lines[1].strip() if len(lines) > 1 else ""
    rows.append([word, reading, meaning, date, source, f"{idx}. {word}.mp3"])

if args.mp3_dir:
    miss = [r[5] for r in rows if not (Path(args.mp3_dir) / r[5]).exists()]
    if miss:
        print("[경고] mp3 없음:", ", ".join(miss))

path = vocab_csv_path(create=True)
existed = load_done_words()
new = [r for r in rows if r[0] not in existed]
dup = [r[0] for r in rows if r[0] in existed]

with open(path, "a", encoding="utf-8-sig", newline="") as f:
    csv.writer(f).writerows(new)

print(f"CSV: {path}")
print(f"기존 등록어 {len(existed)}개 / 이번 {len(rows)}개 / 신규 추가 {len(new)}개"
      + (f" / 중복 스킵 {dup}" if dup else ""))
with open(path, encoding="utf-8-sig", newline="") as f:
    print("총 행수(헤더 제외):", sum(1 for _ in csv.reader(f)) - 1)
