---
name: tiro-meeting-note
description: Tiro 음성 회의를 Tiro MCP로 끌어와 사용자의 회의록_Template 노트로 옮겨 담고, 맞는 프로젝트 폴더에 파일링한다. Tiro에 이미 생성된 '옵시디언 회의록' 문서가 있으면 그대로 가져오고(재요약 금지), 없으면 요약·전사를 받아 스킬에 내장된 '옵시디언 회의록' 양식(Background/Meeting Minutes/Follow ups)으로 직접 정리한다 — 예준님이 Tiro 앱에서 문서 생성을 안 눌러도 됨. 확정된 고유명사 오인식만 치환(Tiro Edited: corrected). 트리거 - "Tiro 회의록 정리해줘", "어제 미팅 옵시디언에 정리", "Tiro에서 회의록 가져와", "미팅 노트 만들어줘", "회의록 작성", "meeting minutes". Tiro 미팅 1건을 골라 볼트 프로젝트 폴더에 회의록으로 넣고 싶을 때.
---

# tiro-meeting-note — Tiro 요약 → Obsidian 회의록

Tiro가 **이미 만들어 둔 회의 요약본**(한 페이지 문서, Obsidian 친화 양식)을 **Tiro MCP로 직접 끌어와** 사용자의 `회의록_Template` 노트에 옮겨 담고, 맞는 프로젝트 폴더에 파일링한다. **예준님이 손으로 Tiro에서 복사해 붙여넣던 작업을 대신하는 것** — 그 이상의 가공(원문 전사 끌어오기, 재요약, 문장 변경)은 하지 않는다. 단 **소스·위키·볼트로 확정된 고유명사 오인식은 치환**한다(아래 "용어 치환" 규칙, 2026-07-06 예준님 결정).

**역할 분담:** 이 스킬은 **Tiro 회의 1건** 전담이다. 이메일·문서(.msg/docx/pdf) 다이제스트는 `note-digest`가 맡는다. 볼트 통합 기계장치(폴더 파일링·mentions·위키연결)는 **note-digest 규율을 그대로 따른다**(§3~§5에서 참조).

## 언제 사용하나
- "Tiro 회의록 정리해줘", "어제 미팅 옵시디언에 정리", "Tiro에서 회의록 가져와", "미팅 노트 만들어줘", "회의록 작성", "meeting minutes"
- Tiro 미팅 1건을 골라 볼트의 프로젝트 폴더에 회의록으로 넣고 싶을 때.
- (전사본·이메일·PDF만으로 회의록을 만드는 경우는 이 스킬이 아니라 `note-digest`.)

## 사전 조건 — Tiro MCP 연결
- 등록(전역, 1회): `claude mcp add --scope user --transport http tiro https://mcp.tiro.ooo/mcp`
- 인증: 첫 연결 시 `/mcp`에서 **Tiro 선택 → OAuth(Google) 로그인**. `auth_status` 도구로 세션 확인.
- **연결돼 있나 확인** — `auth_status` 또는 `list_notes` 호출이 되면 OK. 안 되면 사용자에게 `/mcp`로 인증을 안내하고, 그동안은 **붙여넣은 요약본**으로 진행(아래 §1b).
- (CLI는 무거운 파일·배치용이라 이 용도엔 불필요. 필요 시 `npm i -g @theplato/tiro-cli` → `tiro auth login` → `tiro notes get <guid> --output <파일>`.)

## 워크플로우

### 1. Tiro 요약본 확보
**(a) Tiro MCP — 주 경로.**
1. **미팅 식별** — `list_notes`(최근 목록) 또는 `search_notes "<키워드>" --since 7d`로 대상 회의를 특정(제목·날짜·참석자). 후보가 여럿이면 사용자에게 어느 회의인지 확인.
2. **내용 받기** — `get_note <guid>` (include: `["summary","documents"]`)로 제목 / 일시 / 참석자 / **webUrl**과 함께:
   - **생성된 "옵시디언 회의록" 문서(documents)가 있으면** → 그 문서를 그대로 `# Tiro` 본문으로 쓴다(기존 방식 — 재요약·문장 변경 금지).
   - **없으면(요약만 있음) → 직접 정리 모드 (2026-07-07 결정):** summary를 아래 **[옵시디언 회의록 양식]**으로 재구성해 `# Tiro`에 넣는다. 요약이 너무 얇아 섹션을 못 채우면 그때만 `get_note_transcript`로 전사를 보충. 예준님이 Tiro 앱에서 문서 생성을 누르지 않아도 된다.
   - webUrl = frontmatter `Tiro Address`.

**(b) 붙여넣은 요약본 — 폴백.** MCP 미연결이거나 사용자가 Tiro 화면에서 복사해 직접 줄 때. 이미 회의록 양식이면 그대로, 아니면 직접 정리 모드로 [옵시디언 회의록 양식] 적용(용어 치환 규칙은 동일).

### 1.5 [옵시디언 회의록 양식] — 직접 정리 모드 스펙
Tiro 템플릿 "옵시디언 회의록"(templateId 7213)과 동일 구조. 양식이 바뀐 것 같으면 `get_document_template 7213`으로 최신본 확인 가능.

```markdown
## 1. Background

### Meeting Purpose
- 참석자·일시·장소(확인되는 경우) + 회의 목적·주요 안건

## 2. Meeting Minutes

### 합의 사항
**주제:**
- 내용:

### 기술 이슈 ⚠️
**이슈명:**
- 배경:
- 해결책:

### Q&A
**Q:**
- A: | 담당: | 상태:

## 3. Follow ups

### PTJ 과제
**과제명:** 마감: | 담당: | 상태:
- 내용:

### 협력사 과제
**과제명:** 마감: | 담당: | 상태:
- 내용:

### 고객사 과제
**과제명:** 마감: | 담당:
- 내용:
```

작성 규칙 (원 템플릿 지침 요약):
- 반드시 **한글**, 핵심만 bullet 개조식(구어체→문어체 "~함", 간투사 "음/저기/그" 제거, 반복 표현 제거, 불완전 문장은 문맥으로 완성)
- **§2 Meeting Minutes는 우선순위 순서** — 합의 사항 → 기술 이슈 → Q&A.
- **필요 없는 섹션은 삭제** (Q&A 없으면 제거; 개인·비업무 회의면 Follow ups의 PTJ/협력사/고객사 구분 대신 그냥 "할 일"로)
- **과도한 설명은 "첨부파일 참조"로 처리** — 회의록에 원문을 옮겨 담지 않음.
- 이모지: ✅ 완료 / 🟡 진행중·확인필요 / 🔴 긴급·미해결 / ⚠️ 경고 / ⭕ 미시작
- 우선순위 표기가 필요하면 **높음 / 중간 / 낮음**.
- 마감일 `YYYY.MM.DD` (TBD 지양), **담당자는 1명만 명시**(책임 소재 명확화), 협력사는 회사명(Moog·Hitachi·ABB 등)
- 숫자·날짜·금액 정확히. **전사에서 혼동 가능성이 있으면 값 옆에 🟡(확인필요)** 표기하고 §6 보고에 올림.
- **추측 금지** — 자료에 있는 내용만.
- 전사 오인식은 `{vault}\100. Market information\Tiro 등록 단어.md` 참조해 보정(§2 용어 치환 규칙과 동일하게 확정된 것만)

### 2. 노트 조립 — 회의록_Template
작업 전 정본 템플릿 `{vault}\50. Template\회의록_Template.md`를 **Read**해 현재 필드·섹션을 확인한다(임의 변형 금지). `{vault}` = `%USERPROFILE%\.claude\skills\_config\local-paths.md`의 `vault_root:` 값(PC마다 다름; 없으면 사용자에게 물어 저장). 매핑:

| 위치 | 채우는 값 |
|---|---|
| frontmatter `Date` | 회의 일자 `YYYY-MM-DD` |
| `Category` | 일의 종류 (`meeting`·`submission`·`inquiry` 등 기존 어휘에서 선택 — 고객사명 아님) |
| `Venue` | 온라인/오프라인·장소(요약에 있으면) |
| `mentions` | 참석자 ↔ Contacts (§4, **확인 후에만**) |
| `Tiro Address` | Tiro 노트 **webUrl** |
| `Tiro Edited` | 용어 치환을 했으면 `corrected`, 안 했으면 `raw` |
| `description` | 영어 ~2줄(§5 정책) |
| `tags` | `entity/<거래처>`·`topic/<주제>` nested |
| `# Yejun's memo` | Tiro 노트 바로가기 링크 + (**기존 사용자 메모는 그대로 둠**) |
| `# Claude Code` | 비워두거나 `## 관련 위키`만(§5). 내용 본문은 여기 쓰지 않음 |
| `# Tiro` | **Tiro 요약본을 그대로** 기입 |

**핵심 규칙(이 스킬 고유):**
- **`# Tiro`에 Tiro 요약본을 넣는다.** 이게 이 스킬의 본체다 — 예준님이 복사하던 그 요약을 옮기는 것. Tiro가 만든 Obsidian 양식(소제목·bullet)을 보존한다. (note-digest의 "# Tiro 보호" 규칙은 이 스킬에는 적용하지 않음 — 여기선 # Tiro를 *채우는* 게 목적.)
- **Tiro 생성 문서를 가져온 경우: 재요약·문장 변경·구어→문어 변환을 하지 않는다.** 명백한 깨진 줄바꿈·중복 헤더 정도만 정리 가능. (직접 정리 모드는 §1.5 양식대로 재구성하는 게 일이므로 예외 — 단 추측 금지는 동일.)
- **용어 치환 (2026-07-06 예준님 결정, 방식 B):** 소스 자료(관련 폴더 문서·위키 `0_Wiki MOC`·볼트 기존 노트)로 **확정된 고유명사 오인식만** `# Tiro` 본문에서 정식 표기로 치환한다(예: Limiter→VinMetal, First Couple→First Copper). 치환하면 `Tiro Edited: corrected`, **치환 내역은 `# Claude Code`에 용어 보정표**로 남긴다(원문 표기는 보정표 + `Tiro Address` 웹 원본으로 보존). **불확실하거나 근거 없는 표기는 치환 금지** — 보정표에 "추정/미확인"으로만.
- **오인식 사전 축적:** 새로 확정된 오인식 패턴·신규 고유명사는 `{vault}\100. Market information\Tiro 등록 단어.md`의 등록 단어 리스트·오인식 패턴 표에 추가하고 최종 업데이트 날짜를 갱신한다(예준님이 Tiro 앱 등록단어에 반영하는 원본).
- `# Yejun's memo` 아래에 Tiro 노트 바로가기(webUrl 링크 또는 `[<제목>](<webUrl>)`)를 둔다. **기존 메모·바로가기는 손대지 않는다.**

### 3. 볼트 프로젝트 폴더 찾기 → 확인 → 저장
**`note-digest` §4 정책을 그대로 따른다.** 확인 전에는 절대 쓰지 않는다.
1. 요약 내용에서 프로젝트·고객명 추론(POSCO·FCT·Zhengrui·SEJAL 등).
2. `{vault}\01. Projects\<카테고리>\<프로젝트>` 스캔 → 후보 1~3개.
3. **AskUserQuestion**으로 대상 폴더 확인. 못 찾으면 경로 직접 받기 / 새 폴더 생성 여부 질문.
4. 승인된 폴더에만 생성. 파일명 `YYMMDD_<주제>.md`. 같은 폴더 기존 노트 컨벤션을 맞춤.
5. MOC(`0_<프로젝트>.md`) 자동 링크는 보류.

### 4. mentions 연결 — 사람 ↔ Contacts (제안 → 확인 → 반영)
**`note-digest` §3.5를 그대로 따른다.** 자동 기입 절대 금지.
- 이름 추출 — `get_note` 참석자 + 요약 본문 + `# Yejun's memo`(본인 Kim Yejun 포함).
- `{vault}\20. Contacts\**` 파일명과 매칭(표기 변형에 관대).
- 사용자 확인 후 승인된 사람만 기입. 형식 `- "[[이름]]"`(YAML 리스트+큰따옴표; 인라인 `[[A]] [[B]]`는 frontmatter를 깨뜨림).
- 미확인·신규 인물은 따로 보고.

### 5. 위키 연결 + description
**`note-digest` §4.5 / `wiki-link` 정책을 그대로 따른다.**
- `90. Wiki\0_Wiki MOC.md`를 읽어 어휘 파악 → 요약 본문의 고객사·라인·설비·기술/계약 개념을 `[[링크]]` 매칭 → **`# Claude Code` 안 `## 관련 위키`**에 모음. **인물은 링크 안 함.** 위키에 없는 개념은 자동생성 말고 **"ingest 후보"로 보고**. `# Tiro`·`# Yejun's memo`는 안 건드림.
- `description`: 영어 ~2줄, 고유명사(SEJAL/PTJ/K-104 등)·수치 유지, 콜론·특수문자 있으면 큰따옴표.

### 6. 보고
저장 경로 + 핵심 2~3줄 요약 + 추가한 위키 링크 / 신규 ingest 후보 / 확인이 필요한 숫자·인물을 보고한다.

## 작성 규칙
- **볼트 저장 전 폴더는 반드시 사용자 확인(§3).** 확신해도 확인 없이 쓰지 않음.
- **템플릿 frontmatter 불변** — 필드명·순서 유지, 임의 필드 추가 금지. 작업 전 템플릿 Read(정본이 정답 — 과거 오타 `Catetory`는 볼트 전체 교정 완료, 현재는 `Category`).
- **Tiro 요약은 `# Tiro`에.** 재요약·문장 변경 금지, 확정 고유명사 치환만 허용(§2 용어 치환 규칙, `Tiro Edited`로 표시). `# Yejun's memo`의 기존 사용자 메모는 손대지 않음. 위키 링크는 `# Claude Code`의 `## 관련 위키`에만.
- **mentions는 확인 후에만(§4).** 미확인·신규 인물은 따로 보고.
- `tags`는 `entity/<거래처>`·`topic/<주제>` nested (어휘 마스터: `note-description` 스킬 SKILL.md — 새 태그는 거기에 추가).
- 날짜 `YYYY-MM-DD`. 한국어 보고는 개조식(~함/~임).
- 파일은 **BOM 없는 UTF-8**, 1행 `---`.
- **추측 금지** — Tiro 요약에 있는 내용만. 불명확은 "미확인".

## 주의
- **MCP 미연결 시:** Tiro 경로는 건너뛰고 (b) 붙여넣은 요약본으로 진행. 인증은 `/mcp` → Tiro → OAuth로 사용자에게 안내.
- 원문 전사(`get_note_transcript`)는 기본적으로 **가져오지 않는다**(토큰·불필요). 예외: 직접 정리 모드에서 summary만으로 양식을 못 채울 때, 또는 사용자가 명시적으로 원문까지 원할 때.
- Tiro MCP 도구: `auth_status`, `list_notes`, `search_notes`, `get_note`, `folder_search`, wiki/share-links. (`get_note`가 요약+webUrl을 준다.)
