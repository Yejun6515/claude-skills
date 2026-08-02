# -*- coding: utf-8 -*-
"""사진들을 Eagle(Map memories/이벤트폴더)에 임포트하고 Drive fileId를 확보해 상태 저장.

사용:
  python archive_photos.py --event "260712_난바 이자카야" 사진1.jpg 사진2.heic ...
  [--note "노트파일명.md"]  노트 경로 힌트(상태에 기록만; 링크 삽입은 link_photos 후 스킬이 수행)
  [--timeout 600]           Drive 업로드 폴링 제한(초)

  # 노트 연결 없이 기존 폴더에 바로 넣기(집 요리 등)
  python archive_photos.py --folder "집 요리" --no-drive 사진1.jpg 사진2.heic ...
  [--folder "이름"]  PARENT_FOLDER_NAME/이벤트폴더 대신 그 이름의 폴더에 바로 임포트
                     (find_or_create_folder는 트리를 재귀 탐색하므로 중첩 폴더도 이름만으로 찾음)
  [--no-drive]       Drive fileId 확보와 상태 저장을 건너뜀
                     출력: JSON {folder, folder_id, photos:[{index,name,item_id}]}

출력: JSON {event, folder_id, photos:[{index,name,item_id,drive_file_id}], pending_path}
사진 순서 = 인자 순서(슬랙 보낸 순서). watcher.js가 저장한 _incoming 파일은
파일명이 <ms타임스탬프>_원본명이라 이름순 정렬 = 보낸 순서.
"""
import argparse
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    PARENT_FOLDER_NAME, eagle_call, ensure_eagle_running,
    find_or_create_folder, get_drive_service, save_state,
)


def to_jpg_if_heic(path, staging):
    """HEIC/HEIF면 JPG로 변환한 경로를, 아니면 원본 경로를 반환."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".heic", ".heif"):
        return path
    from PIL import Image
    import pillow_heif

    pillow_heif.register_heif_opener()
    img = Image.open(path)
    out = os.path.join(staging, os.path.splitext(os.path.basename(path))[0] + ".jpg")
    img.convert("RGB").save(out, "JPEG", quality=92)
    return out


def wait_drive_ids(service, item_ids, timeout):
    """각 Eagle 아이템의 '<id>.info' 폴더가 Drive에 업로드될 때까지 폴링해 안의 이미지 fileId 확보."""
    remaining = dict.fromkeys(item_ids)  # item_id -> drive_file_id
    deadline = time.time() + timeout
    while time.time() < deadline and any(v is None for v in remaining.values()):
        for iid, got in list(remaining.items()):
            if got:
                continue
            q = (f"name = '{iid}.info' and mimeType = 'application/vnd.google-apps.folder'"
                 " and trashed = false")
            folders = service.files().list(q=q, fields="files(id)").execute().get("files", [])
            if not folders:
                continue
            fq = (f"'{folders[0]['id']}' in parents and trashed = false"
                  " and mimeType contains 'image/'")
            files = service.files().list(q=fq, fields="files(id,name)").execute().get("files", [])
            # 썸네일(_thumbnail) 제외한 원본만
            files = [f for f in files if "_thumbnail" not in f["name"]]
            if files:
                remaining[iid] = files[0]["id"]
        if any(v is None for v in remaining.values()):
            time.sleep(10)
    return remaining


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photos", nargs="+")
    ap.add_argument("--event", help="이벤트 폴더명 YYMMDD_장소명")
    ap.add_argument("--folder", help="이 이름의 기존/신규 폴더에 바로 임포트(부모 경로 무시)")
    ap.add_argument("--note", default="", help="연결 대상 노트 파일명(힌트)")
    ap.add_argument("--no-drive", action="store_true",
                    help="Drive fileId 확보와 상태 저장을 건너뜀")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    if not args.folder and not args.event:
        sys.exit("--event 또는 --folder 중 하나는 반드시 지정해야 합니다 "
                 '(예: --event "260712_난바 이자카야" 또는 --folder "집 요리")')

    for p in args.photos:
        if not os.path.isfile(p):
            sys.exit(f"파일 없음: {p}")

    ensure_eagle_running()

    if args.folder:
        target_name = args.folder
        event_id = find_or_create_folder(args.folder)
    else:
        target_name = args.event
        parent_id = find_or_create_folder(PARENT_FOLDER_NAME)
        event_id = find_or_create_folder(args.event, parent_id)

    staging = tempfile.mkdtemp(prefix="eagle_stage_")
    items = []
    for p in args.photos:
        conv = to_jpg_if_heic(p, staging)
        items.append({"path": conv, "name": os.path.splitext(os.path.basename(conv))[0]})

    item_ids = eagle_call("/api/item/addFromPaths", {"items": items, "folderId": event_id})
    if not isinstance(item_ids, list) or len(item_ids) != len(items):
        raise RuntimeError(f"임포트 결과 이상: {item_ids}")

    if args.no_drive:
        photos = [{"index": i, "name": os.path.basename(p), "item_id": iid}
                  for i, (p, iid) in enumerate(zip(args.photos, item_ids), start=1)]
        print(json.dumps({"folder": target_name, "folder_id": event_id, "photos": photos},
                         ensure_ascii=False, indent=2))
        return

    service = get_drive_service()
    id_map = wait_drive_ids(service, item_ids, args.timeout)

    photos = []
    for i, (p, iid) in enumerate(zip(args.photos, item_ids), start=1):
        photos.append({
            "index": i,
            "name": os.path.basename(p),
            "item_id": iid,
            "drive_file_id": id_map.get(iid),  # None이면 업로드 미완
        })
    state = {"event": target_name, "note": args.note, "photos": photos,
             "folder_id": event_id, "created": time.strftime("%Y-%m-%d %H:%M:%S")}
    pending = save_state(target_name, state)

    missing = [p["index"] for p in photos if not p["drive_file_id"]]
    print(json.dumps({**state, "pending_path": pending,
                      "drive_upload_missing": missing}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
