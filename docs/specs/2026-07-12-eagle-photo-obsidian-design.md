# Eagle 사진 → Google Drive 링크 → Obsidian 노트 자동 연결 (설계, 브레인스토밍 중)

날짜: 2026-07-12
상태: **✅ 설계 확정·구현 완료 (2026-07-12 미니PC)** — 구현 내역은 [2026-07-12-eagle-photo-obsidian-plan.md](2026-07-12-eagle-photo-obsidian-plan.md), 실행 스킬은 `eagle-photo-archive`. 남은 것: 폰 슬랙 E2E 테스트.
작성 경위: 노트북 PC의 Claude Code 세션에서 브레인스토밍한 내용을 미니 PC로 인계하기 위한 문서.

## 목표

**폰(아이폰)만으로** 다음이 끝나게 한다:

1. 슬랙에 구글/네이버 맵 링크 전송 → Obsidian `30. Map view`에 추억 노트 자동 생성 (✅ 이미 구현돼 있음, 미니 PC에서 24시간 가동)
2. 사진을 찍어 슬랙에 전송 → 원본 전부가 Eagle 라이브러리의 이벤트 폴더에 자동 아카이브
3. 대표 사진 몇 장만 골라 노트에 Google Drive 공개 링크(`![image](...)`)로 연결 — Obsidian에는 파일이 아니라 **주소만** 넣는다

## 현재 상태 (2026-07-12 기준)

- **Eagle 라이브러리**: `Inspiration.library`, 노트북에서는 `C:\Users\yejun\Desktop\Google Drive desktop\Eagle\` 안에 있고 **Google Drive 데스크톱으로 동기화**됨. 폴더 정리 규칙: 이벤트별 폴더 `YYMMDD_이벤트명` (예: `260709_우에다상 환영회`), 상위 분류는 Works people/Friends 등.
- **기존 수동 도구**: `...\Eagle\eagle to obsidian manual\` 폴더의 `실행하기.bat` + `get_eagle_link.py`. 사진을 콘솔에 드래그하면 Drive API로 파일명+부모폴더명 검색 → `anyone/reader` 권한 부여 → `https://lh3.googleusercontent.com/d/{fileId}` 링크를 `![image](...)` 형태로 클립보드 복사. **OAuth 인증 정보(`client_secret.json`, `token.pickle`)가 이 폴더에 이미 있음** — 재사용 가능.
- **미니 PC**: 24시간 가동, 슬랙→노트 자동화가 여기서 돌아감. **Eagle 미설치** (설치 예정, Drive의 기존 라이브러리를 연결하면 됨).
- **아이폰 사진**: iCloud에 있음. Drive와 직접 연결 없음 → 슬랙이 다리 역할.

## 확정된 워크플로우 설계

### 1단계 — 노트 생성 (기존 그대로)
슬랙에 맵 링크 → 미니 PC가 노트 생성 → 봇이 노트 제목 응답.

### 2단계 — 사진 아카이브 (신규)
사진 N장을 슬랙에 전송 → 미니 PC가:
1. 사진 다운로드, HEIC → JPG 변환
2. Eagle API(`http://localhost:41595`)로 폴더 생성 + 임포트
   - 폴더명: 노트 제목에서 가져온 `YYMMDD_장소명`
   - 사진↔노트 매칭 기본 규칙: **가장 최근 생성된 맵 노트**
3. Google Drive 동기화 완료 대기 → Drive API로 각 사진 파일 ID 확보
   - 검색은 Eagle의 `images/XXXX.info` 부모 폴더명 기준 (전역 고유라 정확)
4. 봇 응답: "N장 Eagle 저장 완료. 대표 사진 번호를 답해주세요 (보낸 순서대로 1~N, 예: 1, 4, 7)"

### 3단계 — 대표 사진 연결 (신규)
번호 답장 (예: "1, 4") → 미니 PC가:
1. 해당 사진만 `anyone/reader` 권한 부여
2. `![image](https://lh3.googleusercontent.com/d/{fileId})` 를 노트에 삽입
3. 봇 응답: "노트에 2장 연결 완료"

## 검토했다 버린 대안

- **Drive 인박스 폴더 감시**: 폰에서 Drive 앱을 한 번 더 거쳐야 하고, 어느 노트에 붙일지 매칭이 애매해서 기각.
- **Eagle 생략(Drive 폴더만)**: "원본은 Eagle에서 관리"라는 목적에 어긋나 기각.

## 주의사항

- ⚠️ **Eagle 라이브러리 동시 접근 금지**: 노트북과 미니 PC 양쪽에서 Eagle을 동시에 켜면 클라우드 동기화 충돌로 라이브러리가 깨질 수 있음. Eagle 상시 실행은 **미니 PC 한 곳**으로 정하고, 노트북은 미니 PC 쪽을 끄고 열거나 열람용으로만.
- HEIC 처리: 슬랙 경유 사진이 HEIC일 수 있음 → JPG 변환 후 Eagle 임포트 (lh3 링크 렌더링 호환성).
- Drive 동기화 대기: 임포트 직후엔 Drive에 파일이 없음 → 폴링 필요 (타임아웃 두기).

## 남은 확인 사항 (미니 PC에서 이어서 할 것)

1. **기존 슬랙→노트 자동화의 실체 파악**: 미니 PC 어디에 어떤 형태로 있나 (Claude Code 상주 세션? 커스텀 스크립트? 훅?). 사진 처리를 여기에 붙일지, 별도 프로세스로 둘지 결정.
2. **Eagle 설치 + Drive 라이브러리 연결** (미니 PC).
3. Eagle 안에서 새 이벤트 폴더를 만들 **상위 폴더 위치** 결정 (예: Friends > memory 아래? 별도 "Map memories"?).
4. 대표 사진을 안 고르고 넘어간 경우 처리 (그냥 두기 vs 리마인더) — 일단 "그냥 두기"로 가정.
5. OAuth 인증 재사용: 노트북의 `client_secret.json`을 미니 PC로 복사 (Drive 동기화 폴더라 이미 접근 가능할 것).
6. 설계 확정 후 구현 계획(writing-plans) 작성.

## 미니 PC에서 재개하는 방법

Claude Code를 열고 이렇게 요청:
> `~/.claude/skills/docs/specs/2026-07-12-eagle-photo-obsidian-design.md` 읽고 Eagle 사진 자동화 이어서 진행해줘. "남은 확인 사항" 1번부터.
