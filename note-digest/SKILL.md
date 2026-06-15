---
name: note-digest
description: Read the source files behind an Obsidian note — Outlook emails (.msg), Word/Excel/PowerPoint/PDF documents, whether loose in a folder or in the U:\ folder a note links to — and organize them into that note following the user's Event or 회의록 template (frontmatter normalized, shortcut link preserved, English description, entity/topic tags). Use when the user points at a note or a source folder and asks to 정리/요약/digest it, organize emails or documents into a note, or turn a mail thread / linked folder into a clean Obsidian note.
---

# note-digest — 소스 → Obsidian 노트 정리

노트 뒤에 있는 **소스 파일**(Outlook 메일 `.msg`, Word `.docx`, Excel `.xlsx`, PowerPoint `.pptx`, `.pdf`)을 읽어 **하나의 Obsidian 노트**로 정리한다. 메일뿐 아니라 노트에 **링크된 `U:\` 폴더의 첨부 문서**까지 처리한다. 결과 노트는 사용자의 **Event / 회의록 템플릿**을 그대로 따르고, **바로가기 링크를 보존**하며, 요약 + 출처 목록을 담아 검색·추적이 쉽다.

## 언제 사용하나
- "이 메일/폴더 정리해줘", "노트로 정리", "이 노트에 링크된 폴더 정리", "digest", "메일 요약 md로", "organize these into a note"
- 보통 업무 폴더의 `.msg` 묶음이거나, 볼트 노트가 가리키는 `U:\新_海外営業部\Kim Yejun\...` 폴더(메일 + 첨부 문서).

## 입력 두 가지
1. **소스 폴더** — 사용자가 폴더 경로를 줌. 그 안의 `.msg`/`.docx`/`.xlsx`/`.pptx`/`.pdf`를 모두 읽음.
2. **기존 노트** — 노트 본문의 바로가기(`[...](<file:///U:\...>)`)가 가리키는 폴더를 읽어 그 노트를 채움. **바로가기 링크는 그대로 둔다.**

답장 체인(`RE:`)은 한 `.msg`에 과거 메일이 통째로 들어 있으므로 **같은 스레드의 중복 인용은 한 번만** 다룬다.

## 워크플로우

### 1. 소스 추출
폴더 안 파일을 타입별로 텍스트 덤프(Outlook/Word/Excel/PowerPoint COM 필요 — 이 PC 사용 가능):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skillDir>\scripts\extract_sources.ps1" -FolderPath "<소스 폴더>"
```
- `.msg`→제목/발신/수신/CC/날짜/첨부/본문, `.docx`→본문+표, `.xlsx`→시트별 used range, `.pptx`→슬라이드 텍스트, `.pdf`→포인터(직접 **Read** 도구로 PDF를 읽는다).
- 기본 출력 `<폴더>\_extracted_sources.txt` → **Read**로 읽는다. (`.msg`만 있으면 `extract_msg.ps1`도 가능.)
- PDF는 덤프에 포인터만 남으므로, 중요 PDF는 **Read 도구로 직접** 읽는다.

### 2. 내용 파악
- **주체(회사/담당)**, **쟁점**, **책임소재**, **합의/미결**, **다음 액션**, 문서면 **핵심 수치·일정·조건**을 잡는다.
- 답장 체인은 시간순으로 흐름을 푼다. 메일/문서에 **없는 사실은 지어내지 않는다**(불명확은 "미확인").

### 3. 노트 작성 — 사용자 템플릿 준수
템플릿 원본(정본)은 볼트 `C:\Users\Z006K14G\Desktop\Yejun\50. Template\`:
- **Event template.md** — 메일·이벤트·문서 정리의 기본. frontmatter `Date / Catetory / mentions / Google Drive / description / tags`, 본문 `## Event`.
- **회의록_Template.md** — 실제 회의록일 때. frontmatter `Date / Catetory / Venue / mentions / Tiro Address / Tiro Edited / description / tags`, 본문 `# Yejun's memo` / `# Claude Code` / `# Tiro`.

**회의록 작성 규칙 (중요):**
- 내가(=Claude) 정리·요약한 내용은 **`# Claude Code` 섹션에만** 쓴다.
- **소스 바로가기 링크(첨부 .msg/문서·Google Docs·관련 노트 위키링크)는 `# Yejun's memo` 아래**에 둔다. 즉 # Yejun's memo = 사용자 메모+소스 링크, # Claude Code = 내 분석 본문, # Tiro = 전사앱(불가침).
- **`# Tiro`는 절대 건드리지 않는다** — 사용자가 쓰는 별도 전사(transcription) 요약 앱의 영역.

기존 노트를 채우는 경우, **frontmatter를 표준 템플릿으로 정규화**하되:
- `Date`·기존 `Catetory`·`Google Drive` 등 실값은 보존. 비표준 필드(`Participants`/`Status`/`Transcription Accuracy`/`Notebook LM` 등)는 정리하되 **데이터가 있는 필드(링크 등)는 삭제하지 말고 본문으로 살린다**.
- **본문의 바로가기 링크는 그대로 둔다.**
- 철자 `Catetory`는 템플릿 원본대로 유지(Vault Bases가 이 키로 인덱싱).

저장 위치는 **그 소스가 속한 폴더/노트 자리**. **Obsidian Vault로 옮기지 않는다**(사용자가 수동 이동).

Event 본문 구조(상황에 맞게 가감):
```markdown
## Event
[<기존 바로가기 그대로>](<file:///U:\...>)

### 개요
<2~4줄: 무슨 건이고 현재 상태>

### 등장 주체 / 신청 내역 / 공정 구성 …
| ... | ... |

### 쟁점·이슈 또는 핵심 내용
- 내용 / 원인 / **책임소재** / 합의·미결 …

### 다음 액션
- [ ] <할 일> — <담당> <기한>

### 출처 (Sources)
1. **<제목/문서명>** — <YYYY-MM-DD> · <발신→수신 또는 작성자> · 첨부: <…> · `<파일명>`
```

### 4. 보고
저장 경로 + 핵심 2~3줄 요약을 보고한다.

## 작성 규칙
- **템플릿 frontmatter를 변형하지 않는다** — 필드명·순서·철자(`Catetory` 포함) 유지, 임의 필드 추가 금지.
- **회의록은 `# Claude Code`에만 작성, `# Tiro`/`# Yejun's memo`는 손대지 않는다.**
- **`description:`은 영어로 ~2줄(약 2문장)** — progressive(미리보기)용. 고유명사(SEJAL, PTJ, K-104 등)·수치 유지. 콜론/특수문자 있으면 큰따옴표. ([[note-description]]와 동일 정책)
- **`mentions:`는 비워둔다** — 사용자가 직접 입력. (채울 땐 YAML 리스트+큰따옴표 `- "[[이름]]"`; 인라인 `[[A]] [[B]]`는 `[`를 flow 시퀀스로 오인해 frontmatter 전체를 깨뜨린다.)
- **`tags:`는 [[obsidian-tagging-convention]]을 따른다** — nested `entity/<거래처>`·`topic/<주제>`. 메일 다이제스트면 `email-digest` 타입 태그를 추가해도 됨.
- **출처는 빠짐없이** — 모든 소스 파일을 한 줄씩(제목/문서명·날짜·발신→수신·첨부·파일명).
- 날짜는 `YYYY-MM-DD`로 통일(상대 날짜 금지). 파일명은 날짜 prefix(`260610_<주제>.md`).
- 한국어 정리는 [[korean-mom-gaejosik-style]](개조식 ~함 종결) 권장.
- 파일은 **BOM 없는 UTF-8**, 1행이 `---`(Write 도구 기본값으로 충족).
- 덤프(`_extracted_sources.txt`)는 작업용 중간산물 — 기본은 남겨두고, 원하면 삭제.

## 주의
- COM(Outlook/Word/Excel/PowerPoint) 보안 프롬프트가 뜨면 사용자에게 허용 요청.
- `.eml`/PST는 미지원(.msg). PDF는 덤프 포인터 → 필요 시 **Read 도구로 직접** 읽는다.
