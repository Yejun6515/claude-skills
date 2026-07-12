# -*- coding: utf-8 -*-
"""대표 사진 번호를 받아 Drive 공개권한을 걸고 노트용 마크다운 링크를 출력.

사용:
  python link_photos.py --numbers "1,4"            # 최근 이벤트(latest.json)
  python link_photos.py --numbers "2" --event "260712_난바 이자카야"

출력: JSON {event, note, links:[{index, name, markdown}], errors:[...]}
노트에 실제로 삽입하는 것은 스킬(클로드)이 이 출력을 받아 수행.
"""
import argparse
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_drive_service, load_state, save_state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numbers", required=True, help='예: "1,4" 또는 "1 4"')
    ap.add_argument("--event", default=None)
    args = ap.parse_args()

    nums = [int(n) for n in re.findall(r"\d+", args.numbers)]
    if not nums:
        sys.exit("번호를 해석할 수 없음: " + args.numbers)

    state, event = load_state(args.event)
    by_index = {p["index"]: p for p in state["photos"]}

    service = get_drive_service()
    links, errors = [], []
    for n in nums:
        p = by_index.get(n)
        if not p:
            errors.append(f"{n}번 없음 (1~{len(by_index)})")
            continue
        fid = p.get("drive_file_id")
        if not fid:
            errors.append(f"{n}번({p['name']})은 Drive 업로드 미확인 — 잠시 후 재시도")
            continue
        service.permissions().create(
            fileId=fid, body={"type": "anyone", "role": "reader"}
        ).execute()
        p["linked"] = True
        links.append({
            "index": n,
            "name": p["name"],
            "markdown": f"![image](https://lh3.googleusercontent.com/d/{fid})",
        })

    save_state(event, state)
    print(json.dumps({"event": event, "note": state.get("note", ""),
                      "links": links, "errors": errors}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
