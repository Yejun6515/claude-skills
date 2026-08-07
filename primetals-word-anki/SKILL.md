---
name: primetals-word-anki
description: "Primetals 업무 일본어 단어 배치 워크플로우 — 옵시디언 15.10. 일본어 폴더에 새 단어 노트(YYMMDD_Primetals.md, T|D|P|E 표)가 생기면 ①새 단어만 word-tts로 MP3 생성 ②스마트 글라스용 단어정리 txt ③Anki 덱(01_Primetals일본어) 전체 리빌드 apkg — **음성 없는 텍스트 전용이 기본** ④Anki 임포트 창 실행 ⑤_tts단어장.csv 기록. 트리거: '프리메탈 단어 처리해줘', '프리메탈 단어 정리', 'primetals 단어 tts', '새 단어 노트 anki에 넣어줘', 'Primetals 단어 anki 임포트', 'Primetals 일본어 배치'. 회사 PC Anki 설치 완료(2026-07-31), 192단어 검증."
---

# primetals-word-anki (Primetals 단어 배치 워크플로우)

업무 중 모은 Primetals 일본어 단어를 **TTS(귀) + 스마트 글라스 txt(눈) + Anki(복습)**로
연결한다. 학습 체제: Anki는 `01_Primetals일본어` + `Language Reactor`(드라마) 2덱 체제.

## 전제 (예준님의 습관 — 스킬은 여기서부터 시작)

- 새 단어는 옵시디언 `15. Training\15.10. 일본어\YYMMDD_Primetals.md`에
  `|T|D|P|E|` 표(단어|뜻|읽기|예문)로 정리돼 있다. 볼트 위치는 PC마다 다르고
  (집 `~\Yejun\`, 회사 `~\Desktop\Yejun\`) 스크립트가 자동 탐색한다.
  — 손으로 모은 노트 외에, **tiro-word-tts 스킬**(Tiro 회의 단어 피커)이 같은 형식으로
  단어 노트를 만들기도 한다(그 경우 TTS·Drive 업로드까지 tiro-word-tts가 이미 완료).
- **mp3 마스터 = 구글 드라이브 `12_TTS` 폴더** — 집 노트북에는 드라이브 데스크톱 앱이
  마운트돼 있어 `G:\내 드라이브\12_TTS\YYMMDD_Primetals\`를 로컬처럼 직접 읽는다(검증 2026-07-12).
  TTS를 어느 PC에서 만들든 이 폴더에 저장하면 업로드 단계 없이 자동 동기화.
  ※ Anki 덱은 이제 무음이라 mp3는 **글라스·이동중 청취 전용**. 덱 빌드와 무관해졌다.
- **회사 PC에서 전 과정 완결**(2026-07-31~): Anki를 회사 PC에도 설치해서
  노트 작성 → apkg 빌드 → 임포트 → AnkiWeb 동기화까지 한자리에서 끝난다.
  Anki 경로 `%LOCALAPPDATA%\Programs\Anki\anki.exe` (관리자 권한 없이 설치됨).
  AnkiWeb 동기화로 집 노트북·폰까지 전파. 집에서 전부 해도 동일.
- `Desktop\Claude Code\일본어 공부\Primetals_Anki\mp3\`는 2026-07-12 초기 구축 때의 로컬
  사본(백업)이며 이후 마스터는 드라이브.

## 처리 순서 (TTS → txt → Anki)

```
1. 새 노트 파싱      : 최신 YYMMDD_Primetals.md의 단어 목록 추출
2. TTS 생성          : 새 노트 단어만 word-tts 모드 A로 MP3 생성
                       → G:\내 드라이브\12_TTS\YYMMDD_Primetals\単語(よみ).mp3
                       (드라이브 자동 동기화 — 별도 업로드 불필요. 글라스 txt·대본도 같은 폴더에)
                       ※ G: 마운트 없는 PC(회사): {tts_output_root}\12_TTS\YYMMDD_Primetals\에
                         만들고 tiro-word-tts 스킬의 upload_drive.py(rclone)로 업로드
                       ※ 배치 전 ElevenLabs 크레딧 확인, 단어당 약 500자
                       ※ 과거 배치의 무음 단어(예: 22개, 2026-07-12 결정)는 사용자가 요청할 때만 소급 생성
3. 단어정리 txt      : word-tts 스킬 '스마트 글라스용 단어 정리 txt' 양식으로
                       mp3\YYMMDD_Primetals\YYMMDD_단어정리.txt (번호 사이 빈 줄)
4. Anki 리빌드       : scripts\build_apkg.py 실행 → 01_Primetals일본어.apkg 전체 재생성
                       **음성 없는 텍스트 전용이 기본**(2026-07-31 결정) — 앞면 단어,
                       뒷면 읽기·뜻·예문. 음성은 mp3로 따로 듣는다.
                       → 이어서 아래 '임포트' 명령으로 Anki 임포트 창까지 띄워준다
                       (guid=(단어,읽기) 고정이라 재임포트해도 학습기록 유지·신규만 추가)
5. 임포트·동기화     : 클대리가 창을 띄우고, 사용자가 Import 클릭 + 동기화(Y)
6. 단어장 기록       : word-tts\scripts\record_vocab.py 로 볼트 _tts단어장.csv에 추가
                       (경로는 _config\vocab_db.py의 vocab_csv_path()로 구한다)
                       (단어,읽기,뜻,생성일,출처=Primetals YYMMDD,mp3파일명)
                       → 드라마 피커에서도 중복 방지됨
```

> ★ **Anki 리빌드·임포트는 배치당 한 PC에서 1회만** (2026-08-07 예준님 지시).
> Anki는 AnkiWeb으로 자체 동기화되므로, 같은 배치를 다른 PC에서 다시 처리할 땐
> **4·5단계를 건너뛴다.** 양쪽에서 임포트하면 동기화 충돌 화면이 뜨고, 거기서
> **Upload to AnkiWeb을 누르면 반대쪽 학습기록이 덮어써진다.** 헷갈리면 Download 쪽을
> 고르고 사용자에게 물을 것. 나머지 단계(TTS·txt·csv·드라이브)는 재실행해도 무해.

> 배치 6단계 절차의 **정본은 `word-tts\references\full-pipeline.md`** — 이 스킬은 그중 뒷단.

## 스크립트

```
python scripts\build_apkg.py                     # 텍스트 전용 리빌드(기본). 경로 자동 탐색
python scripts\build_apkg.py --audio             # 예전처럼 mp3 내장
python scripts\build_apkg.py <노트폴더> <mp3루트> <출력apkg>   # 경로 오버라이드
```

- 경로는 집(`~\Yejun\...`)·회사(`~\Desktop\Yejun\...`) 볼트를 자동 탐색하므로 인자 불필요.

### 임포트 (클대리가 창까지 띄운다 — 검증 2026-07-31)

```powershell
Start-Process "$env:LOCALAPPDATA\Programs\Anki\anki.exe" -ArgumentList "`"<apkg 경로>`""
```

- Anki가 **이미 실행 중이어도** 실행 중인 인스턴스로 전달돼 임포트 화면이 뜬다.
- 마지막 Import 클릭과 동기화(Y)는 GUI라 사용자가 한다. 여기까지 안내하고 끝낼 것.
- **임포트 옵션은 건드릴 필요 없다**(기본값 그대로). genanki가 노트 mod를 생성 시각으로
  찍기 때문에 기본 "Update notes = If newer"로도 기존 카드가 갱신되고, 음성 있던 카드의
  음성 필드도 비워진다. 초기엔 "Always로 바꾸라"고 안내했는데 불필요했음 — 설명만 복잡해짐.
- 새 PC에 Anki를 붙일 땐 첫 로그인에서 반드시 **Download from AnkiWeb**
  (Upload를 누르면 빈 로컬 컬렉션이 기존 덱을 덮어쓴다). AnkiWeb 계정은 개인 Gmail.
- AnkiWeb 웹 화면은 복습·수동 카드 추가만 되고 **apkg/csv 임포트 불가** — 그래서 데스크톱 설치가
  필요했다. 폰(AnkiDroid/AnkiMobile)은 임포트 가능.

- **MODEL_ID(1720712001)·DECK_ID(1720712002)는 절대 변경 금지** — 바꾸면 기존 덱과 병합이 깨져
  중복 덱이 생긴다.
- mp3 매칭 규칙: `単語(よみ).mp3` / `単語.mp3` / `N. 単語.mp3`(순번 자동 제거).
  노트 표기와 mp3가 나뉜 단어는 스크립트의 `SPLIT_MAP`에 추가(여러 mp3 이어 재생).
- 카드: 앞면 = 단어(무음) / 뒷면 = 읽기·뜻·예문. 태그 `primetals_YYMMDD`.
  `--audio`일 때만 앞면에 음성 자동재생이 붙는다.

## 주의

- 한글 경로 + 파이썬: 코드를 stdin으로 넘기지 말고 .py 파일로 실행, `PYTHONIOENCODING=utf-8`.
- genanki 필요 (`pip install genanki`). 회사 PC 설치 완료(0.13.1, 2026-07-31).
- **Anki 실행 중에는 `collection.anki2`가 잠긴다** — 덱 내용을 sqlite로 직접 읽으려 하면
  `database is locked`. 카드 수 확인은 Anki 화면에서 하거나 Anki 종료 후에.
- Anki 백업이 필요한 작업(덱 삭제 등)은 **Anki 완전 종료 후** `%APPDATA%\Anki2` 폴더째 복사.
- 노트 내 중복 단어(같은 단어+읽기)는 첫 등장만 카드화.

**Version**: 1.2 — 2026-08-07 Anki 단계는 **배치당 한 PC에서 1회**(다른 PC는 AnkiWeb 동기화로
이미 반영 — 재임포트 시 충돌·덮어쓰기 위험), 단어장 기록은 `word-tts\scripts\record_vocab.py`,
절차 정본은 `word-tts\references\full-pipeline.md`. 265단어 리빌드 검증.
1.1 — 2026-07-31 텍스트 전용 기본화(`--audio`로 예전 동작), 볼트 경로 자동 탐색,
회사 PC Anki 설치 + 임포트 자동 실행. 노트 8개·192단어로 임포트 검증 완료.
1.0 — 2026-07-12 초기 구축(노트 6개·164단어·음성 144, 무음 22개는 보류).
관련: word-tts(음성 생성·txt 양식), jp-drama-word-tts(드라마 쪽 대응 스킬), _tts단어장.csv 공유.
