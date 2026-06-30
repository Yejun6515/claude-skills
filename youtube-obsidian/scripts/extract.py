#!/usr/bin/env python3
"""
extract.py — YouTube 링크 1개에서 분류·노트화에 필요한 모든 재료를 뽑아 UTF-8 JSON으로 저장한다.

쓰임:
    python extract.py "<youtube_url_or_id>" "<output_json_path>"

설계 메모(왜 이렇게 짰는지):
- 자막은 youtube-transcript-api(순수 파이썬, 한글 깨짐 없음)로 가져온다.
- 제목/채널/업로드일/설명란은 yt-dlp를 **파이썬 라이브러리로** 호출한다.
  CLI(yt-dlp --print)를 bash 파이프로 받으면 Windows 콘솔이 cp949로 재인코딩해
  한글이 깨진다. 라이브러리는 결과를 유니코드 str로 주므로 json.dump가 깔끔하다.
- 제목/채널은 oembed(빠르고 JS런타임 불필요)를 1순위로 쓰되, 비면 yt-dlp 값으로 채운다.
- 어떤 단계가 실패해도 죽지 않고 빈 값 + 에러 메모를 남긴다(폴백은 호출자가 판단).
"""
import sys, re, json, io, urllib.request, urllib.parse

ID_RE = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/|live/))([A-Za-z0-9_-]{11})")

def extract_id(s: str) -> str:
    s = s.strip()
    m = ID_RE.search(s)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    raise ValueError(f"영상 ID를 찾을 수 없습니다: {s}")

def get_transcript(vid):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        f = api.fetch(vid, languages=["ko", "en", "ja"])
        snips = f.snippets if hasattr(f, "snippets") else f
        text = " ".join((s.text if hasattr(s, "text") else s["text"]) for s in snips)
        lang = getattr(f, "language_code", None)
        return {"transcript": text, "transcript_lang": lang, "transcript_ok": bool(text.strip())}
    except Exception as e:
        return {"transcript": "", "transcript_lang": None, "transcript_ok": False,
                "transcript_err": f"{type(e).__name__}: {e}"}

def get_oembed(url):
    try:
        q = urllib.parse.quote(url, safe="")
        o = urllib.request.urlopen(
            f"https://www.youtube.com/oembed?url={q}&format=json", timeout=10)
        m = json.load(o)
        return {"title": m.get("title"), "channel": m.get("author_name")}
    except Exception:
        return {"title": None, "channel": None}

def get_ytdlp(url):
    """yt-dlp 라이브러리로 메타데이터(설명란·업로드일 포함)를 유니코드로 가져온다."""
    try:
        import yt_dlp
        opts = {"quiet": True, "skip_download": True, "no_warnings": True,
                "noplaylist": True, "extract_flat": False}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "channel": info.get("uploader") or info.get("channel"),
            "upload_date": info.get("upload_date"),          # 'YYYYMMDD'
            "description": info.get("description") or "",
            "duration": info.get("duration"),                 # 초
            "tags": info.get("tags") or [],
            "ytdlp_ok": True,
        }
    except Exception as e:
        return {"title": None, "channel": None, "upload_date": None, "description": "",
                "duration": None, "tags": [], "ytdlp_ok": False,
                "ytdlp_err": f"{type(e).__name__}: {e}"}

def main():
    if len(sys.argv) < 3:
        print("usage: python extract.py <url_or_id> <output_json_path>", file=sys.stderr)
        sys.exit(2)
    raw, out_path = sys.argv[1], sys.argv[2]
    vid = extract_id(raw)
    url = f"https://www.youtube.com/watch?v={vid}"

    out = {"video_id": vid, "url": url, "input": raw}
    out.update(get_transcript(vid))
    ob = get_oembed(url)
    yt = get_ytdlp(url)

    # 제목/채널: oembed 우선, 비면 yt-dlp
    out["title"] = ob.get("title") or yt.get("title")
    out["channel"] = ob.get("channel") or yt.get("channel")
    out["upload_date"] = yt.get("upload_date")
    out["description"] = yt.get("description")
    out["duration"] = yt.get("duration")
    out["hashtags"] = yt.get("tags")
    out["meta_ok"] = bool(out["title"])
    if not yt.get("ytdlp_ok"):
        out["ytdlp_err"] = yt.get("ytdlp_err")

    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # 콘솔에는 ASCII-안전 요약만(한글 깨짐 방지)
    print(json.dumps({
        "video_id": vid,
        "transcript_ok": out["transcript_ok"],
        "transcript_chars": len(out["transcript"]),
        "lang": out["transcript_lang"],
        "upload_date": out["upload_date"],
        "meta_ok": out["meta_ok"],
        "out": out_path,
    }))

if __name__ == "__main__":
    main()
