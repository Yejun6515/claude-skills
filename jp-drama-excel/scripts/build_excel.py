#!/usr/bin/env python3
"""
JP Drama Excel Builder
원본 엑셀(A: 번호, B: 일본어)을 읽어 분석용 구조로 변환하고,
Claude가 채운 분석 데이터를 최종 엑셀로 저장.

사용법:
    # 원본 구조 변환 (B열→C열 이동, B/D열 비움)
    python build_excel.py restructure <원본.xlsx> <출력.xlsx>

    # 분석 데이터(JSON)를 엑셀로 저장
    python build_excel.py write <원본.xlsx> <분석.json> <출력.xlsx>

    # 여러 엑셀 파일 합치기
    python build_excel.py merge <파일1.xlsx> <파일2.xlsx> ... <최종.xlsx>
"""

import sys
import json
import pandas as pd
from pathlib import Path


def restructure(src: str, dst: str) -> None:
    """원본(A:번호, B:일본어) → 작업용(A:번호, B:빈칸, C:일본어, D:빈칸)."""
    df = pd.read_excel(src, header=None)
    result = pd.DataFrame({
        'A': df.iloc[:, 0],
        'B': '',
        'C': df.iloc[:, 1],
        'D': '',
    })
    result.to_excel(dst, index=False, header=False)
    print(f"변환 완료: {len(result)}개 문장 → {dst}")


def write(src: str, json_path: str, dst: str) -> None:
    """분석 JSON을 엑셀에 기록.

    JSON 형식:
    [
      {"b": "単語分析...", "d": "한국어 번역..."},
      ...
    ]
    """
    df = pd.read_excel(src, header=None)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = pd.DataFrame({
        'A': df.iloc[:, 0],
        'B': [d.get('b', '') for d in data],
        'C': df.iloc[:, 1],
        'D': [d.get('d', '') for d in data],
    })
    result.to_excel(dst, index=False, header=False)
    print(f"저장 완료: {len(result)}개 문장 → {dst}")


def merge(files: list[str], dst: str) -> None:
    """여러 엑셀 파일을 순서대로 합치기."""
    dfs = [pd.read_excel(f, header=None) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_excel(dst, index=False, header=False)
    print(f"결합 완료: {sum(len(d) for d in dfs)}개 문장 → {dst}")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'restructure' and len(sys.argv) == 4:
        restructure(sys.argv[2], sys.argv[3])
    elif cmd == 'write' and len(sys.argv) == 5:
        write(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'merge' and len(sys.argv) >= 4:
        merge(sys.argv[2:-1], sys.argv[-1])
    else:
        print(__doc__)
