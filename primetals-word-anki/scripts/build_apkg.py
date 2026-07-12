# -*- coding: utf-8 -*-
r"""Primetals 일본어 Anki 덱 전체 리빌드 (옵시디언 노트 + TTS mp3 → 음성 내장 apkg).

사용법: python build_apkg.py [노트폴더] [mp3루트] [출력apkg]
  기본값: 노트   = C:\Users\yejun\Yejun\15. Training\15.10. 일본어
         mp3   = G:\내 드라이브\12_TTS  (구글 드라이브 데스크톱 마운트 — 직접 읽음)
         출력   = Desktop\Claude Code\일본어 공부\Primetals_Anki\01_Primetals일본어.apkg
  ※ G: 마운트가 없는 PC에서는 mp3루트를 인자로 지정 (예: 로컬 복사본 폴더)

- 노트 형식: |T|D|P|E| 표 (단어|뜻|읽기|예문), 파일명 YYMMDD_*.md
- mp3 파일명: "単語(よみ).mp3" / "単語.mp3" / "N. 単語.mp3" (순번 접두 자동 제거)
- guid를 (단어,읽기)로 고정 → 재임포트해도 기존 카드 학습기록 유지, 신규만 추가
- MODEL_ID/DECK_ID는 절대 바꾸지 말 것 (바꾸면 기존 덱과 병합 안 됨)
"""
import glob
import os
import re
import sys

import genanki

NOTES_DIR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:\Users\yejun\Yejun\15. Training\15.10. 일본어"
MP3ROOT = sys.argv[2] if len(sys.argv) > 2 else r"G:\내 드라이브\12_TTS"
OUT = sys.argv[3] if len(sys.argv) > 3 else \
    r"C:\Users\yejun\Desktop\Claude Code\일본어 공부\Primetals_Anki\01_Primetals일본어.apkg"

MODEL_ID = 1720712001   # 고정 — 변경 금지
DECK_ID = 1720712002    # 고정 — 변경 금지

# 노트 표기 ↔ mp3 분할 표기 수동 매핑 (mp3 여러 개면 이어서 재생)
SPLIT_MAP = {
    "干潮審査": ["干潮", "審査"],
    "仕切り立て": ["仕切り", "立て"],
    "消化体制": ["消化"],
    "工事積算": ["積算"],
}

# --- 노트 파싱 ---
words = []
seen = set()
for path in sorted(glob.glob(os.path.join(NOTES_DIR, "*.md"))):
    date = os.path.basename(path)[:6]
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or set(line) <= {"|", "-", " "}:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4 or cells[0] in ("T", ""):
                continue
            key = (cells[0], cells[2])
            if key in seen:
                continue
            seen.add(key)
            words.append({"date": date, "word": cells[0], "meaning": cells[1],
                          "reading": cells[2], "example": cells[3]})

# --- mp3 인덱스 ---
mp3_index = {}
for p in glob.glob(os.path.join(MP3ROOT, "**", "*.mp3"), recursive=True):
    name = os.path.splitext(os.path.basename(p))[0]
    name = re.sub(r"^\d+\.\s*", "", name)
    key = re.sub(r"\(.*?\)$", "", name).strip()
    mp3_index.setdefault(key, p)

MODEL = genanki.Model(
    MODEL_ID,
    "Primetals JP Vocab (TTS)",
    fields=[{"name": "단어"}, {"name": "읽기"}, {"name": "뜻"},
            {"name": "예문"}, {"name": "음성"}],
    templates=[{
        "name": "단어 카드",
        "qfmt": '<div class="word">{{단어}}</div>{{음성}}',
        "afmt": '{{FrontSide}}<hr id="answer">'
                '<div class="reading">{{읽기}}</div>'
                '<div class="meaning">{{뜻}}</div>'
                '<div class="example">{{예문}}</div>',
    }],
    css="""
.card { font-family: "Meiryo UI", "Malgun Gothic", sans-serif; text-align: center;
        background: #fff; color: #000; }
.word { font-size: 44px; font-weight: bold; color: #0C2340; margin-top: 24px; }
.reading { font-size: 24px; color: #00587C; margin-top: 14px; }
.meaning { font-size: 26px; color: #E87722; font-weight: bold; margin-top: 8px; }
.example { font-size: 18px; color: #333; margin-top: 16px; line-height: 1.6; }
""",
)

deck = genanki.Deck(DECK_ID, "01_Primetals일본어")
media = []
missing = []
for w in words:
    word_clean = re.sub(r"\(.*?\)$", "", w["word"]).strip()
    keys = SPLIT_MAP.get(word_clean, [word_clean])
    mp3s = [mp3_index[k] for k in keys if k in mp3_index]
    if not mp3s and w["word"] in mp3_index:
        mp3s = [mp3_index[w["word"]]]
    sound = ""
    if mp3s:
        media.extend(mp3s)
        sound = "".join(f"[sound:{os.path.basename(m)}]" for m in mp3s)
    else:
        missing.append(f'{w["word"]}({w["reading"]}) [{w["date"]}]')
    deck.add_note(genanki.Note(
        model=MODEL,
        fields=[w["word"], w["reading"], w["meaning"], w["example"], sound],
        tags=[f'primetals_{w["date"]}'],
        guid=genanki.guid_for("primetals_jp", w["word"], w["reading"]),
    ))

pkg = genanki.Package(deck)
pkg.media_files = media
pkg.write_to_file(OUT)

print("카드:", len(words), "| 음성 있음:", len(words) - len(missing),
      "| 음성 없음:", len(missing))
for m in missing:
    print("  무음:", m)
print("OUT:", OUT)
