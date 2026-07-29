# -*- coding: utf-8 -*-
r"""TTS 배치: {스테이징}\대본\*_대본tts.txt → {스테이징}\N. 単語(よみ).mp3

사용법: python run_tts_batch.py <스테이징 폴더>
- word-tts 스킬의 tts.py 사용 (Taehyung 단일 음성)
- 파일명 = "N. 単語(よみ).mp3" (N = 글라스용 단어정리 txt의 번호 = 피커 선택 순서)
  · 단어정리 txt가 없으면 순번 없이 "単語(よみ).mp3"로 생성
  · Anki build_apkg.py는 "^숫자. " 접두를 자동 제거하므로 매칭에 영향 없음
- 이미 생성된 mp3(10KB 초과)는 스킵 → 중단돼도 재실행하면 이어서 진행
  · 순번 없는 기존 mp3가 있으면 순번 붙은 이름으로 rename (재생성 안 함)
- 실패(크레딧 소진 등) 시 즉시 중단
"""
import glob
import os
import re
import subprocess
import sys

STAGE = sys.argv[1]
SC = os.path.join(STAGE, "대본")
TTS_PY = os.path.expanduser(r"~\.claude\skills\word-tts\scripts\tts.py")


def key_of(name):
    """'共吊り(ともづり)' / '共吊り (ともづり)' → '共吊り'"""
    return re.sub(r"\(.*?\)\s*$", "", name).strip()


# --- 순번 = 글라스용 단어정리 txt의 번호 ---
order = {}
for gp in glob.glob(os.path.join(STAGE, "*단어정리*.txt")):
    with open(gp, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"\s*(\d+)\.\s*(\S.*)$", line)
            if m:
                order.setdefault(key_of(m.group(2)), int(m.group(1)))
    break

files = sorted(f for f in os.listdir(SC) if f.endswith("_대본tts.txt"))
items = []
for f in files:
    base = f[: -len("_대본tts.txt")]            # "共吊り(ともづり)"
    n = order.get(key_of(base))
    items.append((n if n else 10**6, base, f, n))
items.sort()

done = skipped = renamed = 0
for _, base, f, n in items:
    out_name = f"{n}. {base}.mp3" if n else f"{base}.mp3"
    mp3 = os.path.join(STAGE, out_name)
    if os.path.exists(mp3) and os.path.getsize(mp3) > 10000:
        skipped += 1
        continue
    plain = os.path.join(STAGE, base + ".mp3")   # 순번 없이 만들어둔 기존 파일
    if n and os.path.exists(plain) and os.path.getsize(plain) > 10000:
        os.replace(plain, mp3)
        renamed += 1
        print(f"[rename] {base}.mp3 → {out_name}", flush=True)
        continue
    r = subprocess.run(
        [sys.executable, TTS_PY, os.path.join(SC, f), "-o", mp3],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"[FAIL] {base}: {r.stdout[-300:]} {r.stderr[-300:]}", flush=True)
        sys.exit(1)
    done += 1
    print(f"[{done + skipped + renamed}/{len(items)}] {out_name} OK", flush=True)

if not order:
    print("주의: 단어정리 txt를 찾지 못해 순번 없이 생성했습니다.", flush=True)
print(f"완료: 생성 {done}, 스킵 {skipped}, 이름변경 {renamed}")
