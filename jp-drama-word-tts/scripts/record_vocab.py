# -*- coding: utf-8 -*-
r"""단어정리 txt를 파싱해 {부모 폴더}\_tts단어장.csv에 기록.

사용법: python record_vocab.py <화 폴더> <제목> <출처라벨> <날짜 YYYY-MM-DD>
  예:   python record_vocab.py "...\260712_쿠조1" 쿠조1 "쿠조의 대죄 1화" 2026-07-12
- 입력: {화 폴더}\TTS\{제목}_단어정리.txt (블록: "N. 단어 (읽기)\\n뜻\\n한자줄", 빈 줄 구분)
- 이미 단어장에 있는 단어는 스킵, mp3 파일 존재 확인 후 기록
"""
import csv
import os
import re
import sys

EP_DIR, TITLE, SOURCE, DATE = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
TXT = os.path.join(EP_DIR, "TTS", f"{TITLE}_단어정리.txt")
MP3DIR = os.path.join(EP_DIR, "TTS")
DB = os.path.join(os.path.dirname(os.path.abspath(EP_DIR)), "_tts단어장.csv")

with open(TXT, encoding="utf-8") as f:
    blocks = [b for b in f.read().strip().split("\n\n") if b.strip()]

existing = set()
if os.path.exists(DB):
    with open(DB, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i and row:
                existing.add(row[0])
else:
    with open(DB, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow(["단어", "읽기", "뜻", "생성일", "출처", "mp3파일명"])

added = 0
with open(DB, "a", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    for b in blocks:
        lines = b.strip().split("\n")
        m = re.match(r"(\d+)\.\s*(.+?)(?:\s*\((.+?)\))?$", lines[0])
        n, word, reading = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
        if not reading:
            reading = word
        meaning = lines[1].strip()
        mp3 = f"{n}. {word}.mp3"
        if word in existing:
            continue
        if not os.path.exists(os.path.join(MP3DIR, mp3)):
            print("MP3 없음, 스킵:", mp3)
            continue
        w.writerow([word, reading, meaning, DATE, SOURCE, mp3])
        added += 1

print("단어장 기록:", added, "건 →", DB)
