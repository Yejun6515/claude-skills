# -*- coding: utf-8 -*-
r"""TTS 배치: {화 폴더}\TTS\대본\*_대본tts.txt → {화 폴더}\TTS\N. 単語.mp3

사용법: python run_tts_batch.py <화 폴더>
- word-tts 스킬의 tts.py 사용 (Taehyung 단일 음성)
- 이미 생성된 mp3(10KB 초과)는 스킵 → 중단돼도 재실행하면 이어서 진행
- 실패(크레딧 소진 등) 시 즉시 중단
"""
import os
import re
import subprocess
import sys

EP_DIR = sys.argv[1]
OUT = os.path.join(EP_DIR, "TTS")
SC = os.path.join(OUT, "대본")
TTS_PY = os.path.expanduser(r"~\.claude\skills\word-tts\scripts\tts.py")

files = [f for f in os.listdir(SC) if f.endswith("_대본tts.txt")]
files.sort(key=lambda f: int(re.match(r"(\d+)\.", f).group(1)))

done = skipped = 0
for f in files:
    base = f[: -len("_대본tts.txt")]          # "1. 開廷"
    mp3 = os.path.join(OUT, base + ".mp3")
    if os.path.exists(mp3) and os.path.getsize(mp3) > 10000:
        skipped += 1
        continue
    r = subprocess.run(
        [sys.executable, TTS_PY, os.path.join(SC, f), "-o", mp3],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"[FAIL] {base}: {r.stdout[-300:]} {r.stderr[-300:]}", flush=True)
        sys.exit(1)
    done += 1
    print(f"[{done + skipped}/{len(files)}] {base} OK", flush=True)

print(f"완료: 생성 {done}, 스킵 {skipped}")
