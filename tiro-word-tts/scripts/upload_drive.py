# -*- coding: utf-8 -*-
r"""스테이징 폴더의 mp3 + 단어정리 txt를 구글 드라이브 12_TTS로 업로드 (rclone).

사용법: python upload_drive.py <스테이징 폴더> <드라이브 폴더명>
  예:   python upload_drive.py "C:\...\Desktop\TTS\12_TTS\260727_Primetals" 260727_Primetals
- 원격 이름 gdrive 고정. 미설정이면 안내문 출력 후 종료(코드 2).
- 대본\ 하위는 올리지 않음 (mp3와 *단어정리*.txt만).
"""
import glob as _glob
import os
import shutil
import subprocess
import sys

STAGE = sys.argv[1]
FOLDER = sys.argv[2]


def find_rclone():
    p = shutil.which("rclone")
    if p:
        return p
    for pat in (r"%LOCALAPPDATA%\Microsoft\WinGet\Links\rclone.exe",
                r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Rclone.Rclone_*\rclone-*\rclone.exe"):
        hits = _glob.glob(os.path.expandvars(pat))
        if hits:
            return hits[0]
    return None


RCLONE = find_rclone()
if not RCLONE:
    print("rclone을 찾을 수 없음. winget install Rclone.Rclone 후 재시도.")
    sys.exit(2)


def run(*args):
    return subprocess.run([RCLONE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


remotes = run("listremotes").stdout
if "gdrive:" not in remotes:
    print("rclone 원격 'gdrive' 미설정. 1회 설정 필요(브라우저 OAuth):")
    print("  rclone config create gdrive drive")
    print("설정 후 이 스크립트를 재실행하면 업로드됩니다. 파일은 스테이징에 남아 있음:")
    print(" ", STAGE)
    sys.exit(2)

dest = f"gdrive:12_TTS/{FOLDER}"
r = run("copy", STAGE, dest,
        "--include", "*.mp3", "--include", "*단어정리*.txt",
        "--stats-one-line", "-v")
print(r.stdout[-2000:])
if r.returncode != 0:
    print("[FAIL]", r.stderr[-1000:])
    sys.exit(1)

chk = run("lsf", dest)
files = [ln for ln in chk.stdout.splitlines() if ln.strip()]
print(f"업로드 완료: {dest} ({len(files)}개 파일)")
for ln in files:
    print(" ", ln)
