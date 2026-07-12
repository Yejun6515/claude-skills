# Eagle 사진 자동화 — 구현 계획 (미니PC, 2026-07-12)

설계 문서: [2026-07-12-eagle-photo-obsidian-design.md](2026-07-12-eagle-photo-obsidian-design.md)
상태: ✅ 구현 + 로컬 E2E 테스트 완료 (2026-07-12). 남은 것: 폰 슬랙 E2E 테스트(테스트 계획 3번).

## 구현하며 알게 된 것 (트러블슈팅 기록)

- **Eagle 4.0 API는 라이브러리 로드가 끝나야 켜진다** — 로그에 `Library loaded` → `Local server: enabled`가 찍힌 뒤에야 41595가 응답. 그 전에는 연결 거부.
- **41593 포트는 함정** — Eagle이 별도로 여는 내부 서버로, 어떤 경로를 요청해도 앱 정보만 반환한다. 정식 API는 41595 (`{"status":"success"}` 래퍼가 있는지로 구분). `common.py`가 41595~41599를 프로브해 자동 감지.
- Drive 업로드는 작은 JPG 기준 수십 초 내 완료, `wait_drive_ids` 10초 간격 폴링으로 충분.
- lh3 링크는 권한 부여 직후 바로 HTTP 200 (image/jpeg) 확인됨.
- Eagle 시작프로그램 등록됨 (`shell:startup\Eagle.lnk`) — 미니PC 재부팅에도 API 유지.
- Eagle V1 API에는 폴더 삭제가 없다 — 테스트로 만든 빈 폴더(`Map memories/260712_자동화테스트`)는 Eagle에서 수동 삭제.

## 미니PC에서 확인 완료된 사실 (설계 문서 "남은 확인 사항" 답)

1. **기존 슬랙→노트 자동화의 실체**: `C:\Users\Kim Yejun\slack-mail-bot\watcher.js`의 **#작업 채널 핸들러**.
   - 슬랙 메시지 → `claude -p --dangerously-skip-permissions` 스폰 (cwd = `WORK_ROOT` = `C:\Users\Kim Yejun\Desktop\M-Workplace\Slack작업`).
   - 스레드 답글 = `--resume <session_id>`로 **같은 클로드 세션이 이어짐** → "번호 답장" 단계가 세션 문맥으로 자연 해결.
   - 첨부파일은 watcher.js가 이미 `WORK_ROOT\_incoming\<ts>_<이름>`에 다운로드해 프롬프트에 경로를 넣어줌.
   - 맵링크→노트는 이 채널에서 `map-memory-note` 스킬이 발동되는 구조.
   - **결정: 사진 처리도 같은 채널에 "스킬"로 붙인다** (watcher.js 수정·봇 재시작 불필요).
2. **Eagle**: `C:\Program Files\Eagle`에 설치됨. 라이브러리는 Drive 스트리밍 마운트 `G:\다른 컴퓨터\노트북\Google Drive desktop\Eagle\Inspiration.library` (이미지 2,472항목, 쓰기 가능 확인). 노트북 Eagle은 꺼두기로 확인받음 — **상시 실행은 미니PC 담당**.
3. **상위 폴더**: 새 최상위 **"Map memories"** (예준님 확정). 이벤트 폴더 `YYMMDD_장소명`을 전부 이 아래 생성, 재분류는 나중에 Eagle에서 수동.
4. **대표 사진 미선택 시**: 그냥 두기 (설계 문서 가정 유지).
5. **OAuth**: `G:\...\Eagle\eagle to obsidian manual\`의 `client_secret.json` + `token.pickle` 미니PC에서 접근 가능 확인. 스코프 `drive` 전체라 권한 부여까지 커버.
   - ⚠️ skills 레포는 GitHub 공개 저장소 성격 — **인증 파일은 절대 레포에 넣지 않는다.** 스킬은 G:\ 경로를 직접 참조.
6. 이 문서가 그 구현 계획.

## 환경 확인

- Python 3.13.12, `google-api-python-client` 있음. **`pillow` + `pillow-heif` 설치 필요** (HEIC→JPG).
- Eagle API: `http://localhost:41595` (Eagle 실행 중일 때만).

## 구현물: 스킬 `eagle-photo-archive`

위치: `~/.claude/skills/eagle-photo-archive/`

### 트리거
- #작업 채널(또는 로컬)에서 사진 여러 장 첨부 + "아카이브/이글/사진 저장" 류, 혹은 첨부만 온 경우 최근 맵 노트 문맥.
- 스레드에서 번호 답장("1, 4", "대표 1번") → 3단계 실행.

### scripts/
| 파일 | 역할 |
|---|---|
| `archive_photos.py` | ①HEIC→JPG 변환 ②Eagle API로 `Map memories` 아래 이벤트 폴더 생성(+캐시) ③`/api/item/addFromPaths` 임포트 ④Drive 업로드 폴링(파일명+부모폴더 검색, 타임아웃 10분) ⑤`pending.json`에 [보낸순서→fileId] 기록 |
| `link_photos.py` | 번호 목록 받아 해당 fileId에 `anyone/reader` 권한 → `![image](https://lh3.googleusercontent.com/d/{id})` 마크다운 출력 |

- 상태 파일: `WORK_ROOT\_eagle_pending\<노트제목>.json` — 봇 재시작으로 세션이 끊겨도 번호 답장 복구 가능.
- 노트 매칭 기본 규칙: `30. Map view`에서 **가장 최근 생성된 맵 노트** (스킬이 mtime 아닌 파일명 YYMMDD + frontmatter로 판단, 사용자가 노트명을 지정하면 그걸 우선).
- 링크 삽입 위치: 노트 본문 끝 (frontmatter 아래 기존 내용 보존).

### Eagle 상시 실행
- Eagle이 꺼져 있으면 스킬이 `Start-Process`로 켜고 API 폴링 후 진행.
- 시작프로그램 등록(선택): `shell:startup`에 Eagle 바로가기.

## 남은 리스크
- G:\ 스트리밍 마운트 위 라이브러리 — 대량 임포트 시 성능·오프라인 캐시 이슈 가능. 문제가 생기면 라이브러리를 `내 드라이브`로 옮겨 미러링 검토.
- lh3 링크는 Google 썸네일 서버 — 간혹 첫 로드 지연 있음(기존 수동 도구와 동일).

## 테스트 계획
1. 로컬: 샘플 JPG 1장으로 `archive_photos.py` — Eagle 폴더 생성·임포트·Drive fileId 확보 확인.
2. 로컬: `link_photos.py` — 권한 부여 + 링크 마크다운, 노트 삽입.
3. E2E(폰): 슬랙 #작업에 맵링크 → 노트 생성 → 사진 2~3장 전송 → "1" 답장 → 노트에 링크 확인.
