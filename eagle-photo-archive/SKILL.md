---
name: eagle-photo-archive
description: 슬랙(#작업)으로 보낸 사진을 Eagle 라이브러리(Map memories/YYMMDD_장소명)에 자동 아카이브하고, 번호 답장으로 고른 대표 사진만 Google Drive 공개링크(lh3)로 Obsidian 맵 노트에 삽입한다. 트리거 - 사진 첨부와 함께 "아카이브/이글에 저장/사진 정리", 맵 노트 직후 사진만 전송, 스레드에서 "1, 4" 같은 번호 답장, "대표 사진 n번". map-memory-note로 만든 노트의 후속 단계. 집밥 모드 - 슬랙 #이글에 "집밥" + 사진이 오면 노트 연결 없이 Eagle "집 요리" 폴더에 바로 아카이브하고 끝낸다(대표 사진 선택 없음).
---

# eagle-photo-archive — 슬랙 사진 → Eagle 아카이브 → 노트 링크

폰만으로 완결되는 3단계 추억 기록의 2·3단계를 담당한다.
(1단계 = map-memory-note가 맵 링크로 노트 생성)

- **2단계**: 사진 N장 수신 → HEIC→JPG → Eagle `Map memories/YYMMDD_장소명`에 임포트 → Drive fileId 확보 → "번호를 답해달라" 응답
- **3단계**: 번호 답장 → 해당 사진만 `anyone/reader` 권한 → `![image](lh3...)`를 노트에 삽입
- **집밥 모드**: 노트가 없는 집 요리 사진은 2단계에서 짧게 끝낸다 (아래 "집밥 모드" 절)

## 고정 경로 (scripts/common.py에 정의)

| 항목 | 값 |
|---|---|
| Eagle 라이브러리 | `C:\Eagle\Inspiration.library` (2026-07-12 로컬 이사 — Drive 데스크톱이 백업) |
| OAuth (client_secret/token.pickle) | `C:\Eagle\eagle to obsidian manual\` — **레포에 복사 금지** |
| 맵 노트 | `C:\Users\Kim Yejun\Desktop\Obsidian\Yejun\30. Map view\` (하위 폴더 포함) |
| 상태 파일 | `...\Slack작업\_eagle_pending\<이벤트>.json` + `latest.json` |

⚠️ Eagle은 미니PC에서만 상시 실행 (노트북과 동시 실행 시 라이브러리 손상 위험).
⚠️ 사진 원본은 Eagle이 관리 — 볼트에 이미지 파일을 복사하지 않는다. 노트에는 링크만.

## 2단계 실행 순서 (사진이 왔을 때)

메시지에 "집밥"이 있으면 이 절이 아니라 아래 "집밥 모드"로 간다.

1. **노트 매칭**: 사용자가 노트를 지정하지 않았으면 `30. Map view`(하위 포함)에서 파일명 `YYMMDD_...` 가 가장 최근인 노트. 오늘 만든 노트가 있으면 그것. 애매하면 사용자에게 어느 노트인지 물어본다.
2. **이벤트 폴더명**: 노트 파일명 `YYMMDD_장소 with 동행자.md` → `YYMMDD_장소` (with 앞까지).
3. 사진 순서 = 보낸 순서. `_incoming`의 `<ms>_이름` 파일명을 **이름순 정렬**하면 보낸 순서다.
4. 실행:
   ```
   python "<이 스킬>/scripts/archive_photos.py" --event "260712_장소명" --note "노트파일명.md" 사진1 사진2 ...
   ```
   - Eagle이 꺼져 있으면 스크립트가 자동 실행·대기함 (로컬 라이브러리라 기동 ~30초 내).
   - Drive 업로드 폴링 기본 10분. `drive_upload_missing`이 비어 있지 않으면 그 번호는 아직 업로드 전 — 응답에 명시.
5. **슬랙 응답**: `N장을 Eagle "<이벤트폴더>"에 저장했어요. 노트에 넣을 대표 사진 번호를 답해주세요 (보낸 순서대로 1~N, 예: 1, 4)`

## 3단계 실행 순서 (번호 답장이 왔을 때)

1. 실행 (스레드가 이어져 있으면 이벤트를 알고 있음; 새 세션이면 `--event` 생략 → latest 사용):
   ```
   python "<이 스킬>/scripts/link_photos.py" --numbers "1, 4" [--event "260712_장소명"]
   ```
2. 출력의 `links[].markdown`을 **노트 본문 맨 끝**에 한 줄씩 추가 (기존 내용·frontmatter 보존, 이미 같은 링크가 있으면 중복 추가 금지). 노트는 상태 JSON의 `note` 파일명을 `30. Map view`에서 찾는다.
3. **슬랙 응답**: `노트 "<제목>"에 N장 연결 완료` (+errors 있으면 그대로 전달).

## 집밥 모드 (노트 연결 없음)

슬랙 **#이글**에 "집밥" + 사진이 오면 노트를 만들지도, 찾지도 않는다. Eagle `집 요리` 폴더(`Family` 하위)에 바로 넣고 끝.

1. 실행:
   ```
   python "<이 스킬>/scripts/archive_photos.py" --folder "집 요리" --no-drive 사진1 사진2 ...
   ```
   - `--folder`는 Eagle 폴더 트리를 **이름만으로 재귀 탐색**하므로 `Family/집 요리` 경로를 몰라도 찾는다.
   - `--no-drive`는 Drive fileId 확보·상태 저장을 건너뛴다. HEIC→JPG 변환과 Eagle 자동 기동은 그대로.
2. **슬랙 응답**: `N장을 Eagle "집 요리"에 저장했어요` — 한 줄로 끝.

하지 않는 것: 맵 노트 매칭, 이벤트 폴더 생성, Drive fileId 폴링, 상태 파일 저장, 대표 사진 번호 질문. **3단계로 넘어가지 않는다** (번호 답장을 기다리지 않음).

2026-08-02 검증: `Family` 하위 `집 요리`를 이름만으로 찾음(folder_id `MSB8LA3IRM3P3`), 1초 이내 완료.

## 복구·엣지 케이스

- 봇 재시작으로 스레드 세션이 끊겨도 `_eagle_pending\latest.json`으로 마지막 이벤트 복구 가능.
- 대표 사진을 안 고르면 그냥 둔다 (원본은 이미 Eagle에 보존됨). 리마인더 불필요.
- lh3 링크는 렌더링에 몇 초 걸릴 수 있음 — 정상.
- Drive 토큰 만료 + refresh 실패 시: `eagle to obsidian manual`의 `get_eagle_link.py`를 GUI 세션에서 한 번 실행해 재인증하라고 안내.
