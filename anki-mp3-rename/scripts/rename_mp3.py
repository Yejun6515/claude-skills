#!/usr/bin/env python3
"""
Anki MP3 Rename Script
Anki CSV에서 일본어 텍스트를 추출해 MP3 파일을 일괄 이름 변경.

사용법:
    python rename_mp3.py <mp3_folder> <csv_file>

예시:
    python rename_mp3.py "C:/Anki/collection.media" "C:/Anki/deck.csv"
"""

import os
import re
import sys


def sanitize(text: str) -> str:
    """파일명에서 금지 문자 제거."""
    return re.sub(r'[\\/:*?"<>|]', '_', text)[:100]


def main(project_dir: str, csv_path: str) -> None:
    sound_pattern = re.compile(r'\[sound:(\d+\.mp3)\]')
    cloze_pattern = re.compile(r'\{\{c1::(.*?)::', re.DOTALL)
    ja_pattern = re.compile(r'dc-(?:lang-ja )?dc-orig">([^<]+)</span>')

    mp3_mapping: dict[str, str] = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '[sound:' not in line:
                continue
            sound_match = sound_pattern.search(line)
            cloze_match = cloze_pattern.search(line)
            if not (sound_match and cloze_match):
                continue
            mp3_file = sound_match.group(1)
            cloze_content = cloze_match.group(1)
            ja_matches = ja_pattern.findall(cloze_content)
            if ja_matches:
                japanese_text = re.sub(r'\s+', '', ''.join(ja_matches).strip())
                mp3_mapping[mp3_file] = japanese_text

    sorted_files = sorted(
        mp3_mapping.keys(),
        key=lambda x: int(x.replace('.mp3', ''))
    )

    total = len(sorted_files)
    print(f"{total}개 파일 변경 시작합니다")

    for i, old_file in enumerate(sorted_files, 1):
        old_path = os.path.join(project_dir, old_file)
        new_name = f"{i}_{sanitize(mp3_mapping[old_file])}.mp3"
        new_path = os.path.join(project_dir, new_name)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            if i % 10 == 0 or i == total:
                print(f"[{i}/{total}]")
        else:
            print(f"[{i}/{total}] 건너뜀 (파일 없음): {old_file}")

    print(f"{total}개 파일 변경 완료!")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("사용법: python rename_mp3.py <mp3_폴더> <csv_파일>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
