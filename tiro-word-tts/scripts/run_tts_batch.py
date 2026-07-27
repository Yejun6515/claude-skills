# -*- coding: utf-8 -*-
r"""TTS 배치: {스테이징}\대본\*_대본tts.txt → {스테이징}\単語(よみ).mp3

사용법: python run_tts_batch.py <스테이징 폴더>
- word-tts 스킬의 tts.py 사용 (Taehyung 단일 음성)
- 파일명에 순번 없음 (Primetals 규칙: 単語(よみ).mp3)
- 이미 생성된 mp3(10KB 초과)는 스킵 → 중단돼도 재실행하면 이어서 진행
- 실패(크레딧 소진 등) 시 즉시 중단
"""
import os
import subprocess
import sys

STAGE = sys.argv[1]
SC = os.path.join(STAGE, "대본")
TTS_PY = os.path.expanduser(r"~\.claude\skills\word-tts\scripts\tts.py")

files = sorted(f for f in os.listdir(SC) if f.endswith("_대본tts.txt"))

done = skipped = 0
for f in files:
    base = f[: -len("_대본tts.txt")]          # "単語(よみ)"
    mp3 = os.path.join(STAGE, base + ".mp3")
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
