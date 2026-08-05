# -*- coding: utf-8 -*-
r"""누적 TTS 단어장(_tts단어장.csv) 공용 접근 모듈.

정본 위치: {vault_root}\15. Training\15.10. 일본어\_tts단어장.csv
  볼트는 집·회사 PC가 동기화되므로, 어느 PC에서 만든 단어든 중복 방지가 이어진다.
  vault_root 는 PC별 설정 %USERPROFILE%\.claude\skills\_config\local-paths.md 에서 읽는다.

쓰는 스킬: jp-drama-word-tts · tiro-word-tts · primetals-word-anki

스킬 scripts/ 에서 쓰는 법:
    import os, sys
    sys.path.insert(0, os.path.expanduser(r"~\.claude\skills\_config"))
    from vocab_db import vocab_csv_path, load_done_words
"""
import csv
import os

HEADER = ["단어", "읽기", "뜻", "생성일", "출처", "mp3파일명"]
LOCAL_PATHS = os.path.expanduser(r"~\.claude\skills\_config\local-paths.md")


def config_value(key):
    """local-paths.md 에서 `키: 값` 한 줄을 읽는다. 없으면 빈 문자열."""
    if not os.path.exists(LOCAL_PATHS):
        return ""
    with open(LOCAL_PATHS, encoding="utf-8") as f:
        for line in f:
            if line.startswith(key + ":"):
                return line.split(":", 1)[1].strip()
    return ""


def jp_dir():
    """볼트의 일본어 학습 폴더(단어 노트 YYMMDD_Primetals.md 가 있는 곳)."""
    vault_root = config_value("vault_root")
    if not vault_root:
        raise SystemExit("vault_root 키가 없습니다 — %s 에 추가하세요." % LOCAL_PATHS)
    return os.path.join(vault_root, "15. Training", "15.10. 일본어")


def vocab_csv_path(create=True):
    """누적 단어장 CSV 절대경로. create=True면 없을 때 헤더만 넣어 새로 만든다."""
    path = os.path.join(jp_dir(), "_tts단어장.csv")
    if create and not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(HEADER)
    return path


def load_done_words():
    """단어장에 이미 기록된 단어 집합(피커 회색 처리용). 파일 없으면 빈 집합."""
    path = vocab_csv_path(create=False)
    words = set()
    if not os.path.exists(path):
        return words
    with open(path, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i and row:
                words.add(row[0].strip())
    return words
