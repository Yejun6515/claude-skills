# 일본어 단어 배치 — 풀 파이프라인 (6단계)

일본어 단어를 **2개 이상** 배치로 만들 때는 mp3에서 멈추지 않고 **아래 6단계를 끝까지** 한다.
(2026-08-07 예준님 지시: "mp3 만들고 단어정리 누적단어장 csv 구글 업로드 볼트, 안키 리빌드 전부")

사용자가 명시적으로 일부를 빼라고 할 때만 그 단계를 건너뛴다(예: "볼트 노트는 빼고").
단어 **1개**만 요청했거나 모드 B(IT/AI 용어)면 이 파이프라인 대상이 아니다 — mp3만 만든다.

---

## 출력 폴더

| 상황 | 폴더 |
|------|------|
| 소스 폴더(U:\ 회의·자료 폴더)가 있는 흐름 | `{소스폴더}\YYMMDD_Primetals\` ★기본 |
| 소스 폴더가 없는 단독 요청 | `{tts_output_root}\12_TTS\YYMMDD_Primetals\` |
| G: 드라이브 마운트 PC(집) | `G:\내 드라이브\12_TTS\YYMMDD_Primetals\` (5단계 생략) |

대본은 그 아래 `_대본\`. `YYMMDD` = 작업일. 드라이브 폴더명·볼트 노트 파일명과 일치시킨다.

---

## 순서 (앞 단계가 뒤 단계의 입력이므로 순서 고정)

### 1. 단어정리 txt  ★ mp3보다 먼저
`{출력폴더}\YYMMDD_단어정리.txt` — SKILL.md '스마트 글라스용 단어 정리 txt' 양식.
**여기서 매긴 번호가 mp3 순번이자 CSV의 mp3파일명이 된다.**

### 2. MP3 배치
대본 작성(모드 A 전 규칙) → 생성. 파일명 `N. 単語.mp3` (순번 접두, 1단계 번호).

```
python "<word-tts>\scripts\tts.py" "<_대본tts.txt>" -o "<출력폴더>\N. 単語.mp3"
```

- 배치 전 ElevenLabs 잔여 크레딧 확인(단어당 약 500자).
- ★ 생성 전 **TTS 대본에 한자가 남아 있지 않은지 프로그램으로 검증**하고 시작한다
  (한자 1글자라도 있으면 오독 → 크레딧 낭비). `[c for c in 대본 if "\u4e00" <= c <= "\u9fff"]`

### 3. 볼트 단어 노트
`{vault_root}\15. Training\15.10. 일본어\YYMMDD_Primetals.md`

```
출처: [회의명](Tiro webUrl) YYYY-MM-DD · 회의 자료 `파일명.xlsx` (예문 출처: 발화 N / 자료 N / 창작 N)

| T | D | P | E |
| --- | --- | --- | --- |
| 単語 | 뜻(부연설명) | よみ | 例文。(번역.) |
```

- frontmatter·푸터 없음. 같은 날 노트가 이미 있으면 표에 append.
- 출처 줄: Tiro 링크 + (자료 문장을 섞었으면) 자료 파일명 + 예문 출처 집계.
- 이 노트가 4·6단계(Anki)의 입력이다.

### 4. 누적 단어장 CSV 기록
```
python "<word-tts>\scripts\record_vocab.py" "<출력폴더>\YYMMDD_단어정리.txt" ^
       --source "YYMMDD 회의명" --mp3-dir "<출력폴더>"
```
정본 = `{vault_root}\15. Training\15.10. 일본어\_tts단어장.csv` (`_config\vocab_db.py`가 계산).
단어 기준 중복 제거. 피커 회색 처리·드라마 스킬과 같은 파일을 공유한다.

> ⚠️ 다른 PC의 단어장을 옮길 때는 **덮어쓰지 말고 행 합치기**(단어 기준 중복 제거).

### 5. 구글 드라이브 업로드
```
python "<tiro-word-tts>\scripts\upload_drive.py" "<출력폴더>" YYMMDD_Primetals
```
→ `gdrive:12_TTS/YYMMDD_Primetals` (mp3 + 단어정리 txt만, 대본 제외).
**G: 마운트 PC(집)는 이 단계 불필요** — 출력 폴더가 곧 드라이브.
`gdrive:` 원격 미설정이면 스크립트가 안내만 하고 종료 → `! rclone config create gdrive drive`.

### 6. Anki 덱 리빌드 + 임포트  ★ 배치당 1회, 이 PC에서만
```
python "<primetals-word-anki>\scripts\build_apkg.py"
Start-Process "$env:LOCALAPPDATA\Programs\Anki\anki.exe" -ArgumentList "`"<apkg>`""
```
- 볼트 노트 **전체**를 읽어 덱을 통째로 재생성(텍스트 전용 기본). guid=(단어,읽기) 고정이라
  재임포트해도 학습기록 유지·신규만 추가. MODEL_ID/DECK_ID 변경 금지.
- 마지막 Import 클릭 + AnkiWeb 동기화(Y)는 GUI라 **사용자가** 한다. 창까지 띄우고 보고.
- ★ **다른 PC에서 같은 배치를 다시 돌릴 때 6단계는 건너뛴다**(2026-08-07 예준님 지시).
  Anki는 AnkiWeb으로 자체 동기화되므로 이미 반영돼 있다. 두 PC에서 각각 임포트하면
  동기화 충돌이 나고, 충돌 화면에서 **Upload to AnkiWeb을 누르면 다른 쪽 학습기록이 덮어써진다.**
  헷갈리면 Download 쪽을 고르고 사용자에게 물을 것.
- 1~5단계는 다른 PC에서 다시 돌려도 무해(CSV는 중복 스킵, 드라이브는 덮어쓰기).

---

## 완료 보고 형식

| 산출물 | 위치 | 상태 |
|---|---|---|
| MP3 N개 + 단어정리 txt + 대본 | `<출력폴더>` | ✅ |
| 볼트 단어 노트 | `15.10. 일본어\YYMMDD_Primetals.md` | ✅ |
| 누적 단어장 CSV | `15.10. 일본어\_tts단어장.csv` (총 N행) | ✅ |
| 구글 드라이브 | `gdrive:12_TTS/YYMMDD_Primetals` (N개) | ✅ |
| Anki 덱 | 카드 N개, 임포트 창 실행 — Import·동기화는 사용자 | ⏳ |

Tiro 흐름이면 **예문 출처 내역(발화 N / 자료 N / 창작 N)**을 함께 밝힌다.
