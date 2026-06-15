---
name: jp-drama-excel
description: "일본 드라마 대사 엑셀 분석 작업. 원본 엑셀(A:번호, B:일본어문장)을 읽어 B열(단어/문법 분석), C열(원문), D열(한국어 번역) 4열 구조로 완성. 사용자가 일본어 드라마 문장 분석, 엑셀 만들어줘, 단어 문법 추출, 한국어 번역 엑셀 등을 요청할 때 사용. JLPT N3 수준 학습자 대상."
---

# JP Drama Excel

## 개요

일본 드라마 대사 엑셀을 JLPT N3 학습자용 분석 자료로 변환. 상세 규칙은 `references/guide.md` 참조.

## 워크플로

### 1단계: 원본 파일 확인
```
python scripts/build_excel.py restructure <원본.xlsx> <작업용.xlsx>
```
B열(일본어)을 C열로 이동, B/D열 비움

### 2단계: 50개씩 분석
원본 엑셀에서 C열 문장을 읽어 B열(분석)과 D열(번역)을 채움.

**출력 형식 (JSON):**
```json
[
  {"b": "単語(よみ) - 뜻, ~文法 - 의미", "d": "한국어 번역"},
  ...
]
```

### 3단계: 엑셀 저장
```
python scripts/build_excel.py write <작업용.xlsx> <분석.json> <정리_1-50번.xlsx>
```

### 4단계: 파일 결합 (전체 작업 후)
```
python scripts/build_excel.py merge 정리_1-50번.xlsx 정리_51-100번.xlsx ... 최종완성본.xlsx
```

## 분석 핵심 규칙

- **B열**: `単語(よみがな) - 한국어` 형식, 동사는 반드시 원형, 최소 2개, 인물명 제외
- **D열**: 자연스러운 구어체, 인물명은 `(킨조)` 형태로 괄호 표시
- **C열**: 절대 수정 금지

## 참고

- 상세 규칙 및 예시: `references/guide.md`
- 엑셀 조작 스크립트: `scripts/build_excel.py`
