---
name: primetals-word-anki
description: "Primetals 업무 일본어 단어 배치 워크플로우 — 옵시디언 15.10. 일본어 폴더에 새 단어 노트(YYMMDD_Primetals.md, T|D|P|E 표)가 생기면 ①새 단어만 word-tts로 MP3 생성 ②스마트 글라스용 단어정리 txt ③Anki 덱(01_Primetals일본어) 전체 리빌드 apkg ④_tts단어장.csv 기록. 트리거: '프리메탈 단어 처리해줘', '프리메탈 단어 정리', 'primetals 단어 tts', '새 단어 노트 anki에 넣어줘', 'Primetals 일본어 배치'. 2026-07-12 164단어(음성 144)로 첫 구축."
---

# primetals-word-anki (Primetals 단어 배치 워크플로우)

업무 중 모은 Primetals 일본어 단어를 **TTS(귀) + 스마트 글라스 txt(눈) + Anki(복습)**로
연결한다. 학습 체제: Anki는 `01_Primetals일본어` + `Language Reactor`(드라마) 2덱 체제.

## 전제 (예준님의 습관 — 스킬은 여기서부터 시작)

- 새 단어는 옵시디언 `C:\Users\yejun\Yejun\15. Training\15.10. 일본어\YYMMDD_Primetals.md`에
  `|T|D|P|E|` 표(단어|뜻|읽기|예문)로 정리돼 있다. (볼트는 집·회사 클라우드 동기화)
  — 손으로 모은 노트 외에, **tiro-word-tts 스킬**(Tiro 회의 단어 피커)이 같은 형식으로
  단어 노트를 만들기도 한다(그 경우 TTS·Drive 업로드까지 tiro-word-tts가 이미 완료).
- **mp3 마스터 = 구글 드라이브 `12_TTS` 폴더** — 집 노트북에는 드라이브 데스크톱 앱이
  마운트돼 있어 `G:\내 드라이브\12_TTS\YYMMDD_Primetals\`를 로컬처럼 직접 읽는다(검증 2026-07-12).
  TTS를 어느 PC에서 만들든 이 폴더에 저장하면 업로드 단계 없이 자동 동기화.
- **2-PC 분업 시나리오**: 회사 PC(Anki 없음)에서 노트 작성+TTS 생성(G: 저장) →
  집 노트북에서 리빌드+Anki 임포트. 집에서 전부 해도 동일.
- `Desktop\Claude Code\일본어 공부\Primetals_Anki\mp3\`는 2026-07-12 초기 구축 때의 로컬
  사본(백업)이며 이후 마스터는 드라이브.

## 처리 순서 (★ TTS → txt → Anki. apkg가 mp3를 내장하므로 Anki가 마지막)

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
                       → 사용자에게 더블클릭 임포트 안내
                       (guid=(단어,읽기) 고정이라 재임포트해도 학습기록 유지·신규만 추가)
5. 단어장 기록       : 새 단어를 일본어 공부\_tts단어장.csv에 추가
                       (단어,읽기,뜻,생성일,출처=Primetals YYMMDD,mp3파일명)
                       → 드라마 피커에서도 중복 방지됨
```

## 스크립트

```
python scripts\build_apkg.py                     # 기본 경로로 전체 리빌드
python scripts\build_apkg.py <노트폴더> <mp3루트> <출력apkg>   # 경로 오버라이드(회사 PC 등)
```

- **MODEL_ID(1720712001)·DECK_ID(1720712002)는 절대 변경 금지** — 바꾸면 기존 덱과 병합이 깨져
  중복 덱이 생긴다.
- mp3 매칭 규칙: `単語(よみ).mp3` / `単語.mp3` / `N. 単語.mp3`(순번 자동 제거).
  노트 표기와 mp3가 나뉜 단어는 스크립트의 `SPLIT_MAP`에 추가(여러 mp3 이어 재생).
- 카드: 앞면 = 단어 + 음성 자동재생 / 뒷면 = 읽기·뜻·예문. 태그 `primetals_YYMMDD`.

## 주의

- 한글 경로 + 파이썬: 코드를 stdin으로 넘기지 말고 .py 파일로 실행, `PYTHONIOENCODING=utf-8`.
- genanki 필요 (`pip install genanki`).
- Anki 백업이 필요한 작업(덱 삭제 등)은 **Anki 완전 종료 후** `%APPDATA%\Anki2` 폴더째 복사.
- 노트 내 중복 단어(같은 단어+읽기)는 첫 등장만 카드화.

**Version**: 1.0 — 2026-07-12 초기 구축(노트 6개·164단어·음성 144, 무음 22개는 보류).
관련: word-tts(음성 생성·txt 양식), jp-drama-word-tts(드라마 쪽 대응 스킬), _tts단어장.csv 공유.
