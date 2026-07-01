---
name: meeting-folder-brief
description: 회의/안건 소스 폴더(U:\ 메일·문서 묶음) 하나를 받아 끝까지 처리하는 오케스트레이션 스킬 — ① 업무 위키에서 프로젝트 현황 확인 → ② 폴더 안 소스(.msg/.xlsx/.docx/.pptx/.pdf) 읽기 → ③ Tiro에서 같은 회의 녹음 매칭·요약 → ④ Obsidian 회의록/Event 노트 작성(맞는 프로젝트 폴더에 확인 후 삽입, 위키 연결) → ⑤ Primetals 브랜드 HTML 검토자료를 소스 폴더에 생성. 트리거 - "이 폴더 검토해서 정리해줘", "[폴더명] HTML+노트+Tiro 해줘", "견적설명회/회의 폴더 정리", "폴더 주면 다 해주는 거". 폴더명(또는 경로) 하나만 주면 정해진 순서로 전부 수행한다.
---

# meeting-folder-brief — 폴더명 하나로 검토 HTML + 옵시디언 노트 + Tiro

회의·안건의 **소스 폴더**(보통 `U:\新_海外営業部\Kim Yejun\...` 아래 메일·엑셀·문서 묶음) 하나를 받아, 매번 반복하던 작업(위키 확인 → 소스 읽기 → Tiro 매칭 → 회의록 노트 → HTML 검토자료)을 **정해진 순서로 한 번에** 수행한다.

> **이 스킬은 얇은 오케스트레이터다.** 각 단계의 상세 규칙은 기존 스킬에 있고, 여기서는 **호출 순서 + HTML 검토자료 생성 단계 + 저장/명명 규칙**만 정의한다. 각 단계는 해당 스킬의 정책을 그대로 따른다:
> - 위키 확인 → `steel-project-wiki-context`
> - 소스 추출·노트 작성·프로젝트 폴더 삽입·위키 연결 → `note-digest`
> - Tiro 요약 가져오기 → `tiro-meeting-note`
> - HTML/문서 브랜드 스타일 → `primetals-text-style`

## 언제 사용하나
- 사용자가 **소스 폴더 경로/이름 하나**를 주고 "검토해서 HTML + 옵시디언 노트 + Tiro 확인해줘", "이 폴더 정리해줘(끝까지)", "[폴더명] 해줘" 류로 요청할 때.
- 한 회의/안건의 산출물(메일 의사록 + 첨부 엑셀·문서 + Tiro 녹음)을 **노트 1개 + HTML 검토자료 1개**로 묶고 싶을 때.
- 단순히 노트만(HTML 없이) 원하면 `note-digest`, Tiro 요약만 옮기려면 `tiro-meeting-note`로 충분 — 이 스킬은 **둘 다 + 위키 확인 + HTML**까지 한 번에 할 때.

## 입력
- 소스 폴더 경로(예: `U:\新_海外営業部\Kim Yejun\1_POSCO\7_POSCO_P2H_Production\260629_견적설명회`) 또는 그 폴더명만. 폴더명만 주면 부모 경로를 맥락(직전 대화·프로젝트)으로 추정하고, 모호하면 전체 경로를 되묻는다.

## 워크플로우 (이 순서를 지킨다)

### 1. 위키 컨텍스트 확인
- 폴더 내용/경로에서 **고객사·라인코드·설비**(POSCO·P2H·K3CX 등)를 잡고, `steel-project-wiki-context` 절차로 **위키(`90. Wiki`) + 프로젝트 폴더의 현황·마스터 스케줄·최근 노트 1~3개**를 먼저 읽는다. 철강 안건이면 필수, 무관하면 건너뛴다.
- 목적: 이 회의가 **직전 진행상황의 어디에 위치하는지** 파악해, 노트·HTML에 "직전 대비 변화"를 정확히 쓰기 위함.

### 2. 폴더 안 소스 읽기
- `note-digest`의 추출 스크립트로 폴더 전체를 덤프:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\note-digest\scripts\extract_sources.ps1" -FolderPath "<소스 폴더>"
  ```
  → 생성된 `_extracted_sources.txt`를 **Read**. PDF·본문 박힌 사진은 `note-digest` 규칙대로 **Read 도구로 직접** 본다.
- 메일(무슨 일) ↔ 첨부 엑셀·도면·사양(근거·수치)을 **하나의 사건으로 교차**해 파악한다(note-digest 핵심2).

### 3. Tiro 매칭
- Tiro MCP로 같은 회의 녹음을 찾는다: `mcp__tiro__list_notes`(keyword=라인코드/프로젝트, 또는 날짜로 필터) → 폴더 날짜와 같은 **녹음 1건**을 고른다(제목 표기가 폴더명과 달라도 날짜·주제로 매칭. 예: 폴더 "견적설명회" ↔ 메일 "見積方針会議" ↔ Tiro "견적서검토회"가 동일 회의일 수 있음).
- `mcp__tiro__get_note`(include=["summary"])로 요약을 가져온다. **Tiro 요약은 그대로** 쓰고(용어 보정·재요약 금지 — `tiro-meeting-note` 정책), 노트의 `# Tiro` 섹션에 1회 기입. Tiro 전사 오인식 용어(예: 헤저=Edger, 초우수=長油柱, 휴대화=径大化, 연타=벤더)는 **# Tiro는 손대지 말고** 내 분석(`# Claude Code`)에서 올바른 용어로 정리.
- 녹음이 없으면 그 사실을 알리고 Tiro 단계는 생략(노트는 메일·문서 기반 Event/회의록으로).

### 4. Obsidian 노트 작성
- `note-digest` §3~4.5를 그대로 따른다:
  - **템플릿** : Tiro 녹음이 있으면 `회의록_Template`(# Yejun's memo / # Claude Code / # Tiro), 없으면 `Event template`. 작업 전 `50. Template\`에서 정본 Read.
  - **섹션 규칙** : 소스 폴더 바로가기 = `# Yejun's memo`, 내 분석 전부 = `# Claude Code`, Tiro 요약 = `# Tiro`(불가침). HTML 링크는 `# Claude Code`의 `## 정리 자료 (HTML)`에 `file:///`로.
  - **저장 폴더는 AskUserQuestion으로 확인**(§4) — 소스가 프로젝트 소스 트리 안이라 대상이 명확해도 확인. 파일명 `YYMMDD_<주제>.md`.
  - **mentions** : Contacts 대조 후 **확인받아야** 기입(§3.5). 내부 회의 등 참석자가 많으면 비워 두고 보고에 사유를 남겨도 된다.
  - **위키 연결**(§4.5) : `0_Wiki MOC.md` 어휘로 `# Claude Code` 안 `## 관련 위키`에 `[[링크]]`, 없는 개념은 **ingest 후보**로 보고(생성 금지).

### 5. HTML 검토자료 생성 (이 스킬의 추가 단계)
- `primetals-text-style`를 적용한 **자기완결 단일파일 HTML**을 만든다(브랜드 팔레트 + 한국어 기본, `reference/examples/krakatau_survey_KO.html` 구조 미러: 네이비 헤더+오렌지 룰, 오렌지 섹션 배지, 검정 본문, 티얼 링크, 상태 태그). 이미지가 있으면 base64 인라인 임베드([[html-self-contained-default]]).
- **내용** = 노트 `# Claude Code` 분석을 HTML로 재구성(개요·범위·일정·전략·핵심표·미결·출처). 메일+엑셀+Tiro를 **통합한 검토본**이지 단순 나열이 아니다.
- **저장 위치 = 소스 폴더(U:\ ...)** — 볼트 용량 절약을 위해 볼트에 두지 않는다([[html-output-in-source-folder]]). 파일명 `YYMMDD_<프로젝트> <주제> 검토.html`.
- 노트 `## 정리 자료 (HTML)`에 이 파일을 `file:///`(소스 폴더 경로)로 링크.

### 6. 보고
- 만든 것: **노트 경로 + HTML 경로 + Tiro 매칭 결과** 한눈에.
- **확인/미결**: 노트 저장 폴더(확인됨), mentions 처리, **추가한 위키 링크 / 신규 ingest 후보**, 그리고 소스에서 확인 필요한 항목(예: 약어·제작처 명칭).

## 규칙 (각 스킬 정책 승계 + 이 스킬 고정값)
- **순서 고정** : 1(위키)→2(소스)→3(Tiro)→4(노트)→5(HTML)→6(보고). 위키 확인 없이 노트/HTML로 직행하지 않는다(틀린 맥락 방지).
- **확인 게이트** : 노트 저장 폴더(AskUserQuestion), mentions는 **사용자 확인 후에만**. 폴더가 명확해도 확인.
- **HTML은 소스 폴더(U:\)에**, 노트는 **볼트 프로젝트 폴더**에. 둘을 바꾸지 않는다.
- **# Tiro·# Yejun's memo 불가침**, 위키 노트는 읽기 전용(생성은 `wiki-ingest`).
- **개조식(~함)** 한국어, BOM 없는 UTF-8, 날짜 `YYYY-MM-DD`.
- 소스에 **없는 사실은 지어내지 않는다**(불명확은 "미확인"으로 표기하고 보고).

## 참고 메모리
[[obsidian-meeting-note-sections]] · [[html-self-contained-default]] · [[html-output-in-source-folder]] · [[korean-mom-gaejosik-style]] · [[obsidian-tagging-convention]] · [[tiro-mcp-setup]]
