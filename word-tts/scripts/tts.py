#!/usr/bin/env python3
"""
word-tts - 단어/용어 설명 대본을 ElevenLabs로 MP3 변환 (Windows)

Claude가 작성한 설명 대본(한국어 해설 + 일본어/영어 단어 혼합)을 받아
multilingual 음성으로 읽어주는 가벼운 TTS 스크립트.

요약/문서추출 없음. 입력 = 이미 완성된 내레이션 대본.
"""

import os
import sys
import re
import argparse
import time
from pathlib import Path

# Windows 콘솔에서 한글/일본어 출력 시 인코딩 에러 방지
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# .env 지원 (선택)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_VOICE_ID = "m3gJBS8OofDJfycyA2Ip"      # Taehyung - 한국어 남성 (IT/AI 모드 등 단일 음성용)
DEFAULT_MODEL_ID = "eleven_multilingual_v2"     # 한+일+영 혼합 읽기
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"  # 무료 플랜 호환 (192는 Creator 등급부터)
MAX_RETRIES = 3


def light_clean(text: str) -> str:
    """최소 전처리: 마크다운 흔적만 제거, <break> 태그·일본어·한국어는 그대로 보존.
    (발음 매핑은 하지 않음 — 일본어는 일본어로, 영어는 Claude가 대본에서 이미 한글로 작성)"""
    # 마크다운 헤더
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 볼드/이탤릭 마커
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # 인용블록 마커
    text = re.sub(r'^\s*>\s?(?!break)', '', text, flags=re.MULTILINE)
    # 백틱 코드
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 구분선
    text = re.sub(r'^\s*-{3,}\s*$', '', text, flags=re.MULTILINE)
    # HTML 태그 제거하되 <break .../> 는 보존
    text = re.sub(r'<(?!break\b)[^>]+>', '', text)
    # 공백 정리
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def read_input(args) -> str:
    if args.text:
        return args.text
    if args.input:
        p = Path(args.input)
        if p.exists():
            return p.read_text(encoding='utf-8')
        return args.input  # 파일이 아니면 텍스트로 간주
    return ""


def generate_audio(text, voice_id, model_id, output_path, fmt):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("에러: ELEVENLABS_API_KEY 환경변수가 없습니다.\n"
              '  등록: setx ELEVENLABS_API_KEY "sk_..."  (새 터미널에서 적용)',
              file=sys.stderr)
        return False

    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=api_key)

    delay = 2
    for attempt in range(MAX_RETRIES):
        try:
            response = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=model_id,
                output_format=fmt,
            )
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in response:
                    f.write(chunk)

            size = Path(output_path).stat().st_size
            if size == 0:
                raise ValueError("생성된 오디오가 비어있습니다")
            print(f"OK: {output_path} ({size/1024:.1f} KB)", file=sys.stderr)
            return True
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"재시도 {attempt+1}/{MAX_RETRIES}: {e}", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
            else:
                print(f"실패 ({MAX_RETRIES}회): {e}", file=sys.stderr)
                return False


def main():
    ap = argparse.ArgumentParser(description="단어 설명 대본 -> MP3 (ElevenLabs)")
    ap.add_argument("input", nargs="?", help="입력 대본 파일 경로 또는 텍스트")
    ap.add_argument("--text", "-t", help="직접 텍스트(대본) 입력")
    ap.add_argument("--output", "-o", default="output.mp3", help="출력 MP3 경로")
    ap.add_argument("--voice", default=DEFAULT_VOICE_ID, help="ElevenLabs Voice ID")
    ap.add_argument("--model", default=DEFAULT_MODEL_ID, help="ElevenLabs Model ID")
    ap.add_argument("--format", default=DEFAULT_OUTPUT_FORMAT, help="출력 포맷")
    args = ap.parse_args()

    raw = read_input(args)
    if not raw or not raw.strip():
        print("에러: 입력 대본이 비어있습니다", file=sys.stderr)
        sys.exit(1)

    cleaned = light_clean(raw)
    if len(cleaned) < 5:
        print("에러: 전처리 후 텍스트가 너무 짧습니다", file=sys.stderr)
        sys.exit(1)

    print(f"입력: {len(cleaned)}자 | 음성: {args.voice} | 모델: {args.model}", file=sys.stderr)
    ok = generate_audio(cleaned, args.voice, args.model, args.output, args.format)
    if ok:
        print(f"Output: {args.output}")
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
