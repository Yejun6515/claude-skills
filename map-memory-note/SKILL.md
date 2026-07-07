---
name: map-memory-note
description: 구글맵/네이버맵 링크 + "○○랑 왔어/갔어" 한 줄을 받아 Obsidian "30. Map view"에 추억 노트를 자동 생성. 링크에서 가게명·좌표(Location)를 추출해 frontmatter에 넣고, 동행자는 "20. Contacts"에서 찾아 [[위키링크]]로, 당일 Tiro 녹음이 있으면 링크도 삽입. 사진은 수동(처리 안 함). 트리거 - 맵 링크(maps.app.goo.gl, goo.gl/maps, naver.me, map.naver.com)와 함께 "~랑 왔어/갔어", "추억 노트", "맵 노트", "여기 저장", "map view에 추가" 류 요청. 슬랙 #작업 채널에서 폰으로 보내는 게 주 사용처.
---

# map-memory-note — 맵 링크 → 추억 노트

한 줄 입력(맵 링크 + 동행자)을 받아 `30. Map view`에 지도 플러그인이 인식하는 노트를 만든다.

## 경로 (고정)
- 볼트: `C:\Users\Kim Yejun\Desktop\Obsidian\Yejun`
- 노트 생성 위치: `30. Map view\` (루트. `Good time\` 하위 아님 — 최근 노트 관례)
- 연락처: `20. Contacts\` (하위폴더 Friends/POSCO/Primetals/MHI/HSC/Others…)
- 템플릿 정본: `50. Template\추억_template.md` (frontmatter 키 참조용)

## 절차

### 1. 입력 파싱
메시지에서 뽑는다:
- **맵 링크** (필수): `maps.app.goo.gl`, `goo.gl/maps`, `naver.me`, `map.naver.com` 등
- **동행자**: "미즈키랑", "엄마와", "with ○○" 등. 없으면 Participants 비움(혼자)
- **날짜**: "어제", "그저께", 명시 날짜. 없으면 오늘(KST)
- **메모/한줄평**: 나머지 텍스트가 있으면 Event 본문에 넣는다

### 2. 맵 링크 해석 → 가게명·좌표
**구글맵** (`maps.app.goo.gl`, `goo.gl/maps`):
```bash
curl -sI -o /dev/null -w '%{redirect_url}' '<링크>'
```
리다이렉트 URL 형식: `https://www.google.com/maps/place/<이름(URL인코딩)>/@<중심좌표>/data=...!3d<위도>!4d<경도>...`
- **좌표는 반드시 `!3d`/`!4d` 값**을 쓴다 (`@` 뒤는 지도 중심이라 부정확)
- 이름은 URL 디코드. 전각 영문(ＭａｒｒｉｙｅｌｌＮ)이 오면 반각으로 정규화
- 이름에 주소(〒733-0877 Hiroshima, Nishi Ward...)가 섞여 오면 → 가게명 부분만 제목에, 주소는 본문에

**네이버맵** (`naver.me`):
```bash
curl -sIL -o /dev/null -w '%{url_effective}' '<링크>'
```
최종 URL에서 place id·좌표 파라미터 추출. 좌표가 URL에 없으면 WebFetch로 페이지를 열어 가게명을 얻고, 가게명으로 WebSearch 해 주소·좌표를 확보한다.
- frontmatter `Url:`에는 **사용자가 준 원래 단축링크**를 그대로 넣는다 (기존 노트 관례)

**Country/City**: 리다이렉트 URL·주소에서 판단 (Hiroshima → Japan/Hiroshima, 부산 → Korea/Busan). 불명확하면 좌표 범위로 추정.

### 3. 동행자 → Contacts 매칭
`20. Contacts`에서 이름 검색 (한글 호칭 ↔ 영문 파일명 매핑 주의):
```bash
find "…\20. Contacts" -iname '*<이름후보>*'
```
- 예: 미즈키 → `Nishisako Mizuki.md` → `"[[Nishisako Mizuki]]"`
- 알려진 매핑: 미즈키=Nishisako Mizuki, 엄마=Mom
- 파일명을 못 찾으면: Contacts 안을 Grep으로 한 번 더 (본문에 한글명 있을 수 있음) → 그래도 없으면 **위키링크 없이 이름 텍스트만** 넣고, 응답에 "Contacts에 없어 텍스트로 넣음"이라 보고

### 4. Tiro 녹음 매칭 (있으면)
Tiro MCP(`mcp__tiro__list_notes`)로 해당 날짜(KST 0시~24시 → UTC로 변환: 전날 15:00Z ~ 당일 15:00Z) 노트를 조회.
- 외출과 관련돼 보이는 녹음(제목·시간대로 판단)을 고르고, `mcp__tiro__get_note`(include: summary)로 **Tiro 요약본**을 가져온다
- frontmatter에 `Tiro: <webUrl>` 키를 추가하고, 본문 맨 아래 `## Tiro` 섹션에 요약을 **"옵시디언 회의록" 양식으로 정리해** 넣는다 (`tiro-meeting-note` 스킬 §1.5의 양식 스펙과 동일 — 원문 프로즈 통째 붙여넣기 금지):
  - `### 1. Background`(목적·참석·장소) → `### 2. Meeting Minutes`(합의 사항 / 기술 이슈 ⚠️ / Q&A) → `### 3. Follow ups`(할 일)
  - 개인 외출이므로 필요 없는 섹션은 삭제, Follow ups는 PTJ/협력사 구분 없이 그냥 "할 일"로. 한글 개조식(~함), 이모지 ✅🟡🔴⚠️⭕, 추측 금지
- 여러 개면 관련 있어 보이는 것 하나만 (frontmatter Tiro 키는 1개). 애매하면 제일 그럴듯한 것을 넣고 나머지는 응답에 보고
- **Tiro MCP 도구가 없거나 인증 만료면 조용히 생략**하고 응답에 "Tiro 생략(연결 안 됨)"만 한 줄 — 노트 생성을 실패시키지 않는다

### 5. 노트 생성
파일명: `YYMMDD_<가게명> with <동행자>.md` (동행자 없으면 `YYMMDD_<가게명>.md`). 특수문자 `\ / : * ? " < > |` 제거.

```markdown
---
Date: YYYY-MM-DD
Country:
  - <Japan|Korea|...>
City:
  - <도시>
Participants:
  - "[[<Contacts 파일명>]]"
Url: <원래 단축링크>
Tiro: <tiro webUrl — 매칭된 녹음 있을 때만 이 키 추가>
tags:
Location: <위도>,<경도>
---

## Event : 

<가게명 (현지어 병기 가능)>
<주소>

[<가게명>](geo:<위도>,<경도>)

<사용자 메모가 있었으면 여기>

## Tiro

<Tiro 요약을 "옵시디언 회의록" 양식으로 정리 (### 1. Background / ### 2. Meeting Minutes / ### 3. Follow ups — 필요한 섹션만). 매칭된 녹음 없으면 이 섹션 생략>
```
- **UTF-8 BOM 없음**, 날짜 `YYYY-MM-DD` (볼트 규칙)
- `Location`은 반드시 `위도,경도` 한 줄 문자열 (map-view-plugin이 읽는 키)
- 사진은 넣지 않는다 — 예준님이 Google Drive에서 수동으로 `![image](https://lh3.googleusercontent.com/d/<id>)` 추가

### 6. 응답 (슬랙용)
굵게는 별표 하나, 헤더 기호 금지. 예:
```
📍 *Marriyell 웨딩홀* 노트 생성
- 파일: 30. Map view/260707_Marriyell 웨딩홀 with 미즈키.md
- 위치: 34.3935314,132.4050457 (Hiroshima, Japan)
- 동행: [[Nishisako Mizuki]]
- Tiro: 웨딩드래스 (33분) 링크 삽입
사진은 Drive에서 수동 추가하세요.
```

## 주의
- 같은 날 같은 장소 노트가 이미 있으면 새로 만들지 말고 그 파일을 알려주고 멈춘다 (Glob `30. Map view/YYMMDD_*`로 확인)
- 위키(90. Wiki) 연결 대상 아님 — 개인 추억 노트라 업무 위키 규칙 적용 제외
- 좌표를 끝내 못 얻으면 노트는 만들되 `Location:` 비우고 응답에 명시 (나중에 수동 보정)
