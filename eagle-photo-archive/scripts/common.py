# -*- coding: utf-8 -*-
"""eagle-photo-archive 공용: 경로 상수, Drive 서비스, Eagle API 헬퍼."""
import io
import json
import os
import pickle
import sys
import time
import urllib.request
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ── 고정 경로 (미니PC 기준) ──────────────────────────────────────
OAUTH_DIR = r"G:\다른 컴퓨터\노트북\Google Drive desktop\Eagle\eagle to obsidian manual"
LIBRARY_DIR = r"G:\다른 컴퓨터\노트북\Google Drive desktop\Eagle\Inspiration.library"
VAULT_ROOT = r"C:\Users\Kim Yejun\Desktop\Obsidian\Yejun"
MAP_VIEW_DIR = os.path.join(VAULT_ROOT, "30. Map view")
STATE_DIR = r"C:\Users\Kim Yejun\Desktop\M-Workplace\Slack작업\_eagle_pending"
EAGLE_EXE = r"C:\Program Files\Eagle\Eagle.exe"
PARENT_FOLDER_NAME = "Map memories"  # 이벤트 폴더를 만들 Eagle 최상위 폴더


_PORT_CACHE = None


def _eagle_port():
    """정식 API는 41595 (막히면 41596+). 41593은 내부 서버라 제외.
    주의: Eagle은 라이브러리 로드가 끝나야 API를 켠다('Local server: enabled')."""
    global _PORT_CACHE
    if _PORT_CACHE:
        return _PORT_CACHE
    for port in range(41595, 41600):
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/application/info", timeout=3
            ) as res:
                if json.loads(res.read().decode("utf-8")).get("status") == "success":
                    _PORT_CACHE = port
                    return port
        except Exception:
            continue
    return 41595



SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    """노트북 시절 만든 token.pickle 재사용. 만료 시 refresh 후 다시 저장."""
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    token_path = os.path.join(OAUTH_DIR, "token.pickle")
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)
        else:
            raise RuntimeError(
                "Drive 토큰이 유효하지 않고 refresh도 불가 — "
                f"{OAUTH_DIR} 에서 get_eagle_link.py를 한 번 실행해 재인증 필요"
            )
    return build("drive", "v3", credentials=creds)


# ── Eagle API ────────────────────────────────────────────────────
def _eagle_token():
    try:
        settings = os.path.join(os.environ["APPDATA"], "Eagle", "Settings")
        with open(settings, encoding="utf-8") as f:
            return json.load(f)["preferences"]["developer"]["apiToken"]
    except Exception:
        return None


def eagle_call(endpoint, payload=None, method=None):
    """Eagle 로컬 API 호출. payload 있으면 POST(JSON), 없으면 GET."""
    url = f"http://localhost:{_eagle_port()}{endpoint}"
    token = _eagle_token()
    if token:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}token={token}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method or ("POST" if data else "GET"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.loads(res.read().decode("utf-8"))
    if body.get("status") != "success":
        raise RuntimeError(f"Eagle API 실패 {endpoint}: {body}")
    return body.get("data")


def ensure_eagle_running(wait_sec=300):
    """Eagle API가 응답할 때까지 대기. 프로세스 없으면 실행."""
    import subprocess

    def alive():
        try:
            eagle_call("/api/application/info")
            return True
        except Exception:
            return False

    if alive():
        return
    # 프로세스 확인 후 없으면 기동
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Eagle.exe"],
            capture_output=True, text=True,
        ).stdout
        if "Eagle.exe" not in out:
            subprocess.Popen([EAGLE_EXE])
    except Exception:
        pass
    deadline = time.time() + wait_sec
    while time.time() < deadline:
        if alive():
            return
        time.sleep(5)
    raise RuntimeError(f"Eagle API가 {wait_sec}초 내에 응답하지 않음 — Eagle 실행/라이브러리 로드 확인 필요")


def find_or_create_folder(name, parent_id=None):
    """이름으로 Eagle 폴더 찾고 없으면 생성. 반환: folder id."""
    def walk(folders):
        for f in folders:
            if f.get("name") == name:
                return f.get("id")
            got = walk(f.get("children") or [])
            if got:
                return got
        return None

    tree = eagle_call("/api/folder/list")
    fid = walk(tree)
    if fid:
        return fid
    payload = {"folderName": name}
    if parent_id:
        payload["parent"] = parent_id
    created = eagle_call("/api/folder/create", payload)
    return created["id"]


# ── 상태 파일 ────────────────────────────────────────────────────
def state_path(event):
    os.makedirs(STATE_DIR, exist_ok=True)
    safe = "".join(c for c in event if c not in '\\/:*?"<>|')
    return os.path.join(STATE_DIR, f"{safe}.json")


def save_state(event, data):
    p = state_path(event)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(STATE_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump({"event": event, "path": p}, f, ensure_ascii=False)
    return p


def load_state(event=None):
    if not event:
        with open(os.path.join(STATE_DIR, "latest.json"), encoding="utf-8") as f:
            event = json.load(f)["event"]
    with open(state_path(event), encoding="utf-8") as f:
        return json.load(f), event
