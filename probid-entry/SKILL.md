---
name: probid-entry
description: ProBid(사내 웹 시스템)에 案件을 생성·갱신할 때 입력창에 그대로 복사해 붙일 영어 텍스트를 만든다 — Project description(개요) · Strategy(수주 전략) · Actions(대표 액션 한 줄) · Notes(날짜별 활동 이력). 프로젝트 폴더나 이름(예 "Dongkuk Side Trimmer", "P3PL") 하나만 주면 옵시디언 개요 노트 §2 활동표와 이벤트 노트를 읽어 복붙용 코드블록으로 돌려준다. 예준님이 매번 영작하는 걸 없애려고 만든 스킬이므로 해설 없이 붙일 것만 낸다. 트리거 - "ProBid 만들어야 돼", "프로비드 입력", "ProBid에 넣을 내용", "개요랑 전략이랑 action 정리해줘", "Actions/Strategy 써줘", "probid description 영어로", ProBid 화면 캡처를 붙이며 뭘 쓸지 묻는 경우. 신규 회사 등록(JARVIS 선등록) 절차는 이 스킬이 아니라 `90. Wiki\Concepts\Probid 신규 회사 등록 (JARVIS).md` 참조.
---

# probid-entry — ProBid 案件 입력문 작성

**목적: 예준님이 ProBid 웹에 案件을 생성할 때 입력창에 복사만 하면 되게 한다.**
매번 영작하는 게 귀찮아서 만든 스킬이다. 프로젝트가 어느 정도 진행된 뒤(견적 단계 진입 등) 입력하는 경우가 대부분이라,
옵시디언에 이미 쌓인 활동 기록을 읽어 영어 문장으로 바꿔주는 게 전부다.

대상 화면: 案件의 **「Actions/Strat./Notes」 탭** — `Actions` 텍스트박스, `Strategy` 텍스트박스,
`Level`·`Note` 로그 테이블(Add new Note). 여기에 Master Data 탭용 **Project description** 한 줄을 더해 4개를 낸다.

확도(A/BA/B)·금액·계약목표월·TSP·Bid/NoBid 판정 같은 **구조 필드는 다루지 않는다**
(월례 수주계획표와 [[LoA]] 게이트 소관).

## 대원칙 (2026-07-30 예준님 확정)

- **영어로만.** ProBid는 글로벌 시스템(일본·오스트리아 본사가 읽음). 한국어·일본어 혼입 금지.
- **전 필드가 같은 문장 감 — 짧은 한 문장.** 예준님 확정본의 감각:
  > Build on Primetals' position as the original supplier of this PL-TCM (2007 installation) to keep the revamp a sole-source negotiated deal rather than an open tender if possible.

  한 호흡에 읽히고, 수식어를 겹치지 않고, 부수 정보를 덧붙이지 않는다.
  description·Actions는 한 문장, Notes는 한 행이 한 문장. **초안이 두 문장 이상이면 자른다.**
- **전반적인 상황 설명. 기술 상세로 파고들지 않는다.** 케이스명·토크·kW·패스수·안전율 같은 건 넣지 않는다.
  판단 기준: *"이 프로젝트를 모르는 본사 영업이 읽고 안건과 진행 상황을 파악하는가?"*
- **버전 여러 개 제시 금지.** 고를 게 있으면 그것도 일이 된다 — 바로 붙일 하나만 낸다.
- **출력은 코드블록만.** 서론·해설·요약 붙이지 않는다. 블록 밖에 쓸 말은 미확인 항목 한두 줄뿐.
- 라인 코드는 한 번 풀어 쓴다 → `PL-TCM (pickling line + tandem cold mill)`, `P3PL (No.3 Plate Mill)`.
- **미확정은 미확정으로** — "not yet agreed", "answer pending", "to be confirmed". 단, 한 줄 안에서 짧게.
- 파일 저장 안 함 (채팅 출력 전용).

## 필드별 작성 규칙

### 1) Project description — **영어 한 문장**

**무슨 설비를 어디서 어떻게 하는 안건인가.**

```
<Revamp / Upgrade / New> of <설비> on <고객 + 라인(풀네임)> in <국가>, <견적 구성>,
with <후속 스코프> as follow-on scope.
```

- 계약·공사 일정은 **넣지 않는다** — ProBid에 계약목표월 필드가 따로 있어 중복.
- 스코프 분담이 특이할 때만 한 절 (`PTJ mechanical + design, customer's own electrical package`).
- 기술 목표는 결과 지표 하나까지 (`to increase capacity`). 수치 나열 금지.
- ⚠️ 고객 소관 항목(전기 모터 등)을 주어로 세우면 당사 공급범위 오해 → `capacity-up` 같은 중립 표현으로.

### 2) Strategy — **영어 한 문장**

수주 전략은 **딱 한 문장**. 2026-07-30 예준님 정정 — 초안이 3문장이었고 "더 간단하게".

```
Build on <우리 포지션의 근거> to keep this <어떤 형태의 수주로> if possible.
```

- 포지션 근거는 **하나만**: original supplier(납품연도) / 설계 authority / 기존 라인 실적 / 현지 대응(PTKR).
- 수주 형태: `sole-source negotiated deal rather than an open tender` / `win against <경쟁사>`
  — 경쟁이 있으면 이름을 쓴다(사내 시스템이므로 솔직하게).
- **단정하지 않는다** — 예준님은 `if possible` 같은 완충을 붙인다. 전략은 의도이지 확정이 아니므로.
- 후속 스코프 확장·제출 타이밍 같은 부수 레버는 **넣지 않는다**(초안에서 잘린 부분). 한 수만 쓴다.

### 3) Actions — **영어 한 줄, 대표 액션 하나** ★

Actions는 이력 나열이 아니다. **이 案件을 대표하는 액션 하나**를 한 줄로 쓴다
(이력은 Notes 담당 — 아래 4번). 2026-07-30 예준님 정정 사항.

```
Following <대표 이벤트 + 날짜>, where <거기서 정해진 것>, PTJ is <현재 하고 있는 대표 액션>.
```

- **대표 이벤트 = 안건의 분기점이 된 사건** (고객 방문·기술발표, RFQ 수령, 견적 제출 등).
  개요 노트 §2 활동표에서 "이 건이 실제로 굴러가기 시작한 행"을 고른다.
  Dongkuk의 경우 2026-06-22 고객 5명 PTJ 방문(스코프 합의) → 이게 배경.
- 뒤에 **현재 하고 있는 일**을 붙여 한 문장으로 닫는다 (`is preparing the budget quotation`).
- 날짜 나열·bullet 금지. 한 줄이면 끝.

### 4) Notes — **날짜별 활동 이력** ★

`Level`·`Note` 로그 테이블. **이력이 여기 들어간다.**

```
YYYY-MM-DD — <한 문장. 누가 무엇을 했고 그 결과가 무엇인가>
YYYY-MM-DD — ...
```

- **소스 = 개요 노트 §2 Sales Activities 활동표**. 표는 최신순이지만 **Notes는 오래된 것부터(시간순)**.
- 표의 모든 행을 담는다(안건 시작 ~ 현재). 요약해서 뭉개지 말 것 — 이력이 목적.
- 각 행은 **한 문장, 결과 중심**: `customer accepted 620 mm minimum trimming width`,
  `PTJ quotation order 0126S468 issued`, `answer pending`.
- 사내 절차 이벤트도 넣는다 (견적오더 발행, 견적 담당 지정, 의뢰서 발행) — 사내 시스템이므로 의미 있음.
- 오더코드·번호는 그대로 (`0126S468`, 전기 `0926S472`) — 추적에 쓰임.
- 미팅 행은 온라인/대면 구분 명시 (`Online meeting` / `<고객> visited PTJ` / `Meeting at <장소>`).
  "최근 온라인 미팅"을 물으면 **대면과 섞지 말 것** — 노트 frontmatter `Category: online meeting`으로 판별.
- Add new Note로 한 줄씩 넣을 수도, 한 칸에 통째로 붙일 수도 있으니 **줄 단위로 잘라 쓸 수 있게** 출력한다.

## 워크플로

1. **프로젝트 특정** — 폴더 경로면 그대로. 코드/이름이면 `C:\Users\Z006K14G\Desktop\Yejun\01. Projects\` 하위
   회사 폴더 → 프로젝트 폴더로 직행 (볼트 전체 Grep 금지).
2. **소스 읽기** — `0_<폴더명>.md`의 §1 Overview(일정·오더코드) + **§2 활동표 전체** + §3 Stakeholders.
   활동표만으로 문장이 안 되는 행은 그 행에 링크된 이벤트 노트를 열어 확인.
   `90. Wiki\Entities\<고객>.md`에 영어 description이 있으면 표현을 재활용(용어 통일).
3. **ProBid 코드 확인** — `01. Projects\0_probid.md` 마스터 표. 없으면 최신 월례 노트 확인,
   그래도 없으면 블록 뒤에 한 줄로 알리고 표에 행만 만들어 둔다.
4. **4개 블록 출력** — description / Strategy / Actions / Notes. 해설 없이.
   요청이 "Actions랑 Strategy만"처럼 일부면 그 블록만 낸다(하나씩 확인받는 진행 방식).
5. 예준님이 실제 입력한 문구가 초안과 다르면 그 차이를 「실전 예」에 반영.

## 코드 매핑 마스터

`C:\Users\Z006K14G\Desktop\Yejun\01. Projects\0_probid.md`
— 담당 案件의 ProBid 4자리 코드 · PTJ 오더코드 · 확도 · 계약목표 · 금액 · 프로젝트 폴더 링크.
월례 수주계획 노트를 정리할 때 이 표도 같이 갱신한다.

## 실전 예 — Dongkuk CM Side Trimmer (2026-07-30, 이 형식이 정답)

**Project description**
> Revamp of the side trimmer on Dongkuk CM's PL-TCM (pickling line + tandem cold mill) in Korea, quoted as two alternative solutions, with pickling tank replacement and a possible Hyper UCM upgrade as follow-on scope.

**Strategy** — ★ 예준님이 실제 입력한 확정본 (초안 3문장을 1문장으로 잘라냄. 문장 감의 기준)
> Build on Primetals' position as the original supplier of this PL-TCM (2007 installation) to keep the revamp a sole-source negotiated deal rather than an open tender if possible.

**Actions** (대표 액션 한 줄 — 6/22 고객 방문을 배경으로)
> Following Dongkuk CM's visit to PTJ on 22 June 2026 where the revamp scope was agreed, PTJ is preparing the budget quotation.

**Notes** (날짜별 이력 — 한 행 한 문장)
> 2026-05-21 — Dongkuk CM approached PTJ for a PL-TCM rationalisation study.
> 2026-06-22 — Five-person delegation visited PTJ; scope to be quoted agreed (side trimmer 2 options, pickling tank 2 options, Hyper UCM study).
> 2026-06-30 — Customer issued the final side trimmer RFQ with two options: full housing replacement or new FWC.
> 2026-07-01 — PTJ estimating engineer assigned and estimate request issued.
> 2026-07-02 — PTJ quotation order 0126S468 issued (electrical 0926S472).
> 2026-07-08 — Customer accepted 620 mm minimum trimming width and kept the full housing replacement condition.
> 2026-07-10 — Welder notcher knife shape requested from the customer via PTKR; answer pending.

### 하지 말 것 — 예준님 정정 3건 (2026-07-30)

1. **기술적으로 너무 깊게** 썼다 — 케이스명·토크·안전율·오버로드율을 넣었고 "전반적인 상황을 간단히"로 정정.
2. **Actions에 날짜별 이력**을 넣었다 → 이력은 **Notes**, Actions는 **대표 액션 한 줄**.
   Actions 끝에 붙였던 `Next —` 줄도 불필요(잘림).
3. 필드마다 짧은/긴 버전을 2벌씩 냈다 → 붙일 것 **하나만**.

## 관련
- `90. Wiki\Concepts\Probid 신규 회사 등록 (JARVIS).md` — 신규 고객을 ProBid에서 검색 가능하게 만드는 선행 절차
- `90. Wiki\Concepts\LoA.md` — Bid/NoBid 게이트, ProBid 예외 기록 요건
- `project-overview-init` / `note-digest` — 이 스킬이 읽는 소스(개요 노트 §2 활동표)를 만드는 쪽
