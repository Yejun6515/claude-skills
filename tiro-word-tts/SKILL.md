---
name: tiro-word-tts
description: "Tiro 회의 단어 TTS 워크플로우 — 일본어 회의 전사에서 단어를 추출해 ①단어 피커 HTML 생성(LLN 드라마 피커의 회의 버전) ②사용자가 고른 단어를 볼트 YYMMDD_Primetals.md 단어 노트에 추가 ③word-tts로 MP3 배치 생성(예문=실제 회의 발화 우선, 부족분만 창작) ④스마트 글라스용 단어정리 txt ⑤rclone으로 구글 드라이브 12_TTS 자동 업로드. 트리거: 'Tiro 단어 피커', '회의 단어 피커 만들어줘', 피커에서 복사한 단어 목록 붙여넣기('단어 골랐어'), '회의 단어 TTS'. tiro-meeting-note/meeting-folder-brief가 일본어 회의를 정리할 때 1단계(피커)를 자동 실행한다."
---

# tiro-word-tts (Tiro 회의 단어 TTS 워크플로우)

jp-drama-word-tts(넷플릭스 LLN 파이프라인)의 **회의 버전**. Tiro 일본어 회의 전사에서
단어를 추출해 피커로 고르게 하고, 고른 단어를 **기존 Primetals 단어 파이프라인**
(볼트 단어 노트 → word-tts → Drive 12_TTS → primetals-word-anki)에 흘려 넣는다.
예준님이 수동으로 하던 ①단어 수집 ②드라이브 창에 mp3 끌어넣기를 자동화하는 것.

## 전체 흐름 (2단계)

```
[1단계: 피커 — 회의록 정리 때 자동]
1. 전사 확보    : mcp__tiro__get_note_transcript <guid>
2. 단어 추출    : Claude가 전사에서 학습가치 있는 일본어 단어를 추출(아래 기준)
                  → {작업폴더}\_tiro_words.json
3. 피커 생성    : build_picker.py → {작업폴더}\단어피커_{제목}.html
                  (볼트 단어 노트에 이미 있는 단어는 회색·선택불가)
4. 안내         : "피커 열어서 선택 → [선택 목록 복사] → 채팅에 붙여넣기"

[2단계: 사용자가 단어 목록을 붙여넣으면 ("단어 골랐어")]
5. 단어 노트    : {vault}\15. Training\15.10. 일본어\YYMMDD_Primetals.md 에
                  |T|D|P|E| 표로 추가 (예문 = 실제 회의 발화). 같은 날 노트 있으면 append.
6. 대본 작성    : word-tts 모드 A 규칙. 예문 첫째 = 실제 회의 발화(히라가나 변환).
                  → {스테이징}\대본\単語(よみ)_대본.txt + _대본tts.txt
7. 단어정리 txt : {스테이징}\YYMMDD_단어정리.txt (글라스용, word-tts 양식)
                  ★ 배치보다 먼저 — 이 txt의 번호가 mp3 순번이 된다
8. 배치 실행    : run_tts_batch.py → {스테이징}\N. 単語(よみ).mp3
                  (N = 단어정리 txt 번호 = 피커 선택 순서)
9. 업로드       : upload_drive.py → 구글 드라이브 12_TTS\YYMMDD_Primetals\
                  (mp3 + 단어정리 txt만. 집 PC처럼 G: 마운트가 있으면 이 단계 불필요)
10. 안내        : 탐색기로 스테이징 폴더 열기 + 보고
```

## 경로 (PC별)

- `{vault}` = `_config\local-paths.md`의 `vault_root:`
- **스테이징(mp3 출력)**:
  - **G: 마운트 PC(집)**: `G:\내 드라이브\12_TTS\YYMMDD_Primetals\` 직접 저장 → 9단계 생략
  - **마운트 없는 PC(회사)**: `{tts_output_root}\12_TTS\YYMMDD_Primetals\` 에 만들고 rclone 업로드
- **피커 HTML**: 소스 폴더(U:\)가 있는 흐름(meeting-folder-brief)이면 **소스 폴더에**,
  없으면(단독 tiro-meeting-note) 스테이징 폴더에. `_tiro_words.json`은 피커와 같은 폴더.
- `YYMMDD` = 단어 노트 작성일(오늘). 드라이브 폴더명과 볼트 노트 파일명을 일치시킨다
  (기존 컨벤션: `260724_Primetals`).

## 단어 추출 기준 (2단계 전사 → json)

- **뽑는 것**: 업무·기술 용어(설비·공정·계약), N3 이상 일반 어휘, 복합동사, 회의에서
  반복 등장한 표현. 고유명사(회사·인명·라인코드)는 제외.
- ★ **전사(발화)에 실제로 나온 단어를 우선한다** (2026-07-31 예준님 지시). 회의 자료
  (MOM 엑셀·첨부 문서)에만 있고 아무도 입으로 말하지 않은 단어는 **후순위** —
  발화 단어만으로 분량이 안 나올 때만 채운다. 뽑을 때 이미 이 순서로 정렬해 둔다.
- 항목당: `word`(한자 표기), `reading`(히라가나), `meaning`(한국어 뜻), `count`(등장횟수),
  `lines`(**최대 3개**, 짧고 명확한 순 — `[{"jp","ko","src"}]`). 발화가 대본 예문의
  재료이므로 등장할 때마다 다른 문장을 최대한 담는다(같은 문장 반복은 1개만).
  - `src`는 그 문장의 출처: **`"voice"`(전사 발화) / `"doc"`(회의 자료 문장) / `"made"`(창작)**.
    생략하면 `voice`로 본다. 전사 문장이 오인식으로 깨져 표기를 보정했어도 `voice`이며,
    보정 사실은 회의록 노트의 용어 보정표에 남긴다.
  - `lines`가 전부 `doc`/`made`인 단어는 피커에서 뒤로 보내고, 그 사실을 사용자에게 알린다.
- 전사 오인식 주의: 소스 자료·위키로 표기를 확정할 수 없는 단어는 뽑지 않는다
  ([[loa-surface-conservatively]]와 같은 정신 — 불확실한 표기로 mp3를 만들지 않음).
- json 스키마: `[{"word","reading","meaning","count","lines":[{"jp","ko"}]}]` (UTF-8, BOM 없음)

## 스크립트 사용법

```
python scripts\build_picker.py   "<작업폴더>" <제목>     # _tiro_words.json → 단어피커_{제목}.html
python scripts\run_tts_batch.py  "<스테이징>"            # 대본\*_대본tts.txt → 単語(よみ).mp3
python scripts\upload_drive.py   "<스테이징>" <YYMMDD_Primetals>   # rclone → gdrive:12_TTS/
```

- **한글 경로 주의**: 파이썬 코드를 stdin으로 넘기지 말고 .py 파일 실행 + `PYTHONIOENCODING=utf-8`.
- run_tts_batch는 백그라운드 권장, 기존 mp3(10KB 초과)는 스킵 → 재실행 시 이어하기.
- 배치 전 ElevenLabs 잔여 크레딧 확인(`GET /v1/user/subscription`, 대본당 약 500자).

## rclone (드라이브 업로드 — 회사 PC)

- 원격 이름 **`gdrive`** 고정. 설정 확인: `rclone listremotes`에 `gdrive:` 있으면 OK.
- **1회 설정(미설정 시)**: 사용자에게 `! rclone config create gdrive drive` 실행 안내
  (브라우저 OAuth — yejunkim0927@gmail.com 계정 승인). headless라 클대리가 대신 못 함.
- upload_drive.py는 `gdrive:` 없으면 안내문 출력 후 종료(파일은 스테이징에 남아 있으므로
  설정 후 재실행하면 됨).

## 대본·산출물 규칙

- 대본은 **word-tts SKILL.md 모드 A** 전 규칙 준수(히라가나 인라인, 한자는 한국 훈음,
  `<break time="0.3s" />`, 복합동사 분해, 숫자 한글).
- **예문은 실제 회의 발화 우선 (2026-07-27 예준님 지시 — 들었던 문장이라 암기에 유리).**
  `lines`의 발화를 예문 첫째부터 차례로 쓴다("첫째, 회의에서 나온 문장이에요." /
  "둘째, 이것도 회의에 나온 문장이에요." 로 표시, 히라가나 변환·긴 발화는 해당 구절만 발췌).
  볼트 단어 노트 E열(예문)도 `lines[0]`을 쓴다.
- ★ **예문 출처 우선순위 (2026-07-31 예준님 지시 — "가능한 발화에서").**
  **① 전사 발화(`voice`) → ② 회의 자료 문장(`doc`) → ③ 창작(`made`)** 순으로만 내려간다.
  전사에 해당 단어가 두세 번 나왔다면 **MOM 문장을 끌어오지 말고 전사 문장을 두세 개 다 쓴다.**
  ②·③은 발화가 모자랄 때만.
  - MOM·첨부 문서 문장은 "실제 회의 자료"이긴 해도 **귀로 들은 문장이 아니므로 발화와 같지 않다.**
    보고할 때 이 둘을 뭉뚱그려 "전부 실제 회의 발화"라고 말하지 않는다.
  - **보고 의무**: 배치가 끝나면 단어별 예문 출처 내역(발화 N개 / 자료 N개 / 창작 N개,
    자료·창작인 단어는 이름까지)을 사용자에게 밝힌다.
  - **볼트 단어 노트 머리말**: `출처:` 줄에 Tiro 링크만 걸지 말고, 자료 문장을 섞었으면
    자료 파일명도 함께 적는다 — 예)
    `출처: [회의명](Tiro webUrl) 2026-07-31 · 회의 자료 20260731_MOM.xlsx (예문 출처: 발화 16 / 자료 15 / 창작 1)`
- mp3 파일명 = `N. 単語(よみ).mp3` (가나 단어는 `N. 単語.mp3`) — **순번 접두 있음**
  (2026-07-29 예준님 지시: 스마트 글라스에서 단어정리 txt 번호와 재생 순서를 맞추기 위해).
  N은 단어정리 txt 번호 = 피커 선택 순서. Anki `build_apkg.py`가 `^\d+\.\s*`를 자동
  제거하므로 Primetals 매칭에는 영향 없음. run_tts_batch.py가 단어정리 txt를 읽어 자동 부여
  (txt 없으면 순번 없이 생성, 순번 없는 기존 mp3는 rename만 하고 재생성 안 함).
- 단어정리 txt = word-tts '스마트 글라스용 단어 정리 txt' 양식(번호+단어+뜻+한국 훈음,
  번호 사이 빈 줄). 번호는 피커 선택 순서. **mp3 배치보다 먼저 만든다.**
- 볼트 단어 노트 표: `| 単語 | 뜻 | よみ | 例文。(번역.) |` — 표 위에
  `출처: [회의명](Tiro webUrl) YYYY-MM-DD` 한 줄(파서는 표만 읽으므로 무해).

## 이후 파이프라인 (이 스킬 밖)

- Anki 반영·`_tts단어장.csv` 기록은 **primetals-word-anki**가 담당(집 PC에서 리빌드).
  이 스킬이 만든 단어 노트·Drive mp3를 그대로 재료로 쓴다.
- 중복 방지: 피커가 볼트 단어 노트 전체 + 누적 `_tts단어장.csv`를 읽어 기존 단어를
  회색 처리하므로 회의가 거듭돼도 중복 생성 없음. 단어장 경로는 `_config\vocab_db.py`가
  `vault_root` 기준으로 계산 — **드라마·Primetals 스킬과 같은 한 파일**을 본다.

**Version**: 1.1 — 2026-07-31 예문 출처 규칙 강화(발화 `voice` → 자료 `doc` → 창작 `made` 3단계,
`lines[].src` 필드, 출처 내역 보고 의무, 볼트 노트 `출처:` 줄에 자료 파일명·집계 병기).
1.0 — 2026-07-27 신설(예준님 아이디어: LLN 피커의 Tiro 버전 + Drive 업로드 자동화).
관련: jp-drama-word-tts(드라마 대응 스킬) · word-tts(대본·TTS 규칙) · primetals-word-anki(Anki)
· tiro-meeting-note/meeting-folder-brief(1단계 자동 발동 지점)
