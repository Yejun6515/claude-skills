---
name: note-digest
description: Read the source files behind an Obsidian note — Outlook emails (.msg), Word/Excel/PowerPoint/PDF documents, whether loose in a folder or in the U:\ folder a note links to — and organize them into a note following the user's Event or 회의록 template (frontmatter normalized, shortcut link preserved, English description, entity/topic tags). Can also file the finished note into the matching project folder inside the Obsidian vault — but always confirms the target folder with the user first. Use when the user points at a note or a source folder and asks to 정리/요약/digest it, organize emails or documents into a note, file/insert a note into the right project, or turn a mail thread / linked folder into a clean Obsidian note.
---

# note-digest — 소스 → Obsidian 노트 정리

노트 뒤에 있는 **소스 파일**(Outlook 메일 `.msg`, Word `.docx`, Excel `.xlsx`, PowerPoint `.pptx`, `.pdf`)을 읽어 **하나의 Obsidian 노트**로 정리한다. 메일뿐 아니라 노트에 **링크된 `U:\` 폴더의 첨부 문서**까지 처리한다. 결과 노트는 사용자의 **Event / 회의록 템플릿**을 그대로 따르고, **바로가기 링크를 보존**하며, 요약 + 출처 목록을 담아 검색·추적이 쉽다.

**핵심 1 — 노트에서 폴더로 바로 가는 클릭형 링크 (반드시 넣는다).** 노트 맨 위(`# Yejun's memo` 아래)에 **소스 폴더 자체를 가리키는 바로가기**를 둔다: `[<폴더명>](<file:///U:\...폴더경로>)`. 옵시디언에서 이 링크를 클릭하면 **그 폴더가 탐색기로 바로 열려** 원본 메일·문서·도면을 즉시 확인할 수 있다. 포인트는 개별 파일이 아니라 **폴더**를 거는 것 — 소스가 여러 개여도 한 번에 닿는다. 경로에 공백·한글이 있어도 `<file:///...>`처럼 `<>`로 감싸면 동작한다. 기존 노트를 채우는 경우, 본문에 이미 있는 바로가기는 **그대로 둔다**.

**핵심 2 — 폴더 안 소스는 교차로 읽어 하나의 사건으로 엮는다.** 메일이 "무슨 일"이면, 함께 든 ITB·계약서·사양서·도면·본문 스크린샷은 그 **근거·수치·물증**이다. 메일이 어떤 조항/사양/사진을 인용하면 **그 원문 서류를 직접 열어 확인**하고(예: ITB 4.1.2조 원문, 사양서의 효율 규정, 능효 라벨 사진), 노트에 "주장 ↔ 근거 서류"로 연결해 적는다. 소스를 따로따로 요약하지 말고 **시간순 흐름 + 쟁점별 근거**로 통합한다.

## 언제 사용하나
- "이 메일/폴더 정리해줘", "노트로 정리", "이 노트에 링크된 폴더 정리", "digest", "메일 요약 md로", "organize these into a note"
- **"이 폴더 보고 옵시디언에 정리해줘", "맞는 프로젝트 찾아서 노트 넣어줘", "볼트에 삽입/파일링"** — 소스 폴더만 주고, 볼트에서 프로젝트를 찾아 노트를 삽입까지 원할 때(§4의 폴더 확인 단계를 거친다).
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
- **메일 본문에 박힌 스크린샷/사진(`image003.png` 등)은 텍스트 덤프에 안 나온다.** 본문이 "사양서에는 / 아래 사진처럼 / ITB에는" 하며 이미지를 가리키면, Outlook COM으로 첨부를 임시폴더에 `SaveAsFile` 한 뒤 **Read 도구로 그 이미지를 직접 본다**(효율 규정 표·능효 라벨 등급·현품 사진이 거기 들어 있는 경우가 많다). 작업 후 임시폴더는 지운다.

### 2. 내용 파악
- **주체(회사/담당)**, **쟁점**, **책임소재**, **합의/미결**, **다음 액션**, 문서면 **핵심 수치·일정·조건**을 잡는다.
- 답장 체인은 시간순으로 흐름을 푼다. 메일/문서에 **없는 사실은 지어내지 않는다**(불명확은 "미확인").

### 3. 노트 작성 — 사용자 템플릿 준수
**노트 템플릿이 항상 우선이다.** 본문 구조는 내가 보기 좋다고 바꾸지 말고 **정본 템플릿을 그대로 따른다**(사용자가 모든 노트를 이 템플릿 형태로 통일해 나가는 중이므로, 기존 노트가 옛 구조라도 새로 쓸 땐 템플릿 구조를 쓴다). 정본은 볼트 `C:\Users\Z006K14G\Desktop\Yejun\50. Template\`:
- **Event template.md** — 메일·이벤트·문서 정리의 기본. frontmatter `Date / Catetory / mentions / Google Drive / description / tags`, **본문 `# Yejun's memo` / `# Claude Code`** (※ 더 이상 `## Event` 단일 구조가 아님 — 작업 전에 템플릿 파일을 **Read해 현재 섹션을 확인**할 것).
- **회의록_Template.md** — 실제 회의록일 때. frontmatter `Date / Catetory / Venue / mentions / Tiro Address / Tiro Edited / description / tags`, 본문 `# Yejun's memo` / `# Claude Code` / `# Tiro`.

**본문 섹션 규칙 (Event·회의록 공통, 중요):**
- 내가(=Claude) 정리·요약·분석한 내용은 **`# Claude Code` 섹션에만** 쓴다(개요·등장 주체·쟁점·근거·다음 액션·출처 등 내 정리 전부 여기).
- **소스 바로가기 링크(첨부 .msg/문서·Google Docs·관련 노트 위키링크)는 `# Yejun's memo` 아래**에 둔다. 즉 # Yejun's memo = 사용자 메모 + 소스 링크, # Claude Code = 내 분석 본문, # Tiro = 전사앱(불가침).
- **`# Yejun's memo`의 기존 사용자 메모는 손대지 않는다** — 소스 링크만 그 아래에 추가/유지한다.
- **`# Tiro`는 절대 건드리지 않는다**(회의록에만 존재) — 사용자가 쓰는 별도 전사(transcription) 요약 앱의 영역. ([[obsidian-meeting-note-sections]])

기존 노트를 채우는 경우, **frontmatter를 표준 템플릿으로 정규화**하되:
- `Date`·기존 `Catetory`·`Google Drive` 등 실값은 보존. 비표준 필드(`Participants`/`Status`/`Transcription Accuracy`/`Notebook LM` 등)는 정리하되 **데이터가 있는 필드(링크 등)는 삭제하지 말고 본문으로 살린다**.
- **본문의 바로가기 링크는 그대로 둔다.**
- 철자 `Catetory`는 템플릿 원본대로 유지(Vault Bases가 이 키로 인덱싱).

저장 위치: 기존 노트를 채우는 경우엔 **그 노트 자리 그대로**. 소스 폴더만 받아 새로 만드는 경우엔 **§4에서 볼트의 맞는 프로젝트 폴더를 찾아 사용자 확인 후 거기에 삽입**한다(확인 전에는 절대 쓰지 않는다).

Event 본문 구조(템플릿 우선, 상황에 맞게 가감) — **소스 링크는 `# Yejun's memo`, 내 분석은 `# Claude Code`**:
```markdown
# Yejun's memo
[<폴더명>](<file:///U:\...소스 폴더 경로>)
<기존 사용자 메모가 있으면 그대로 둔다>

# Claude Code

## 개요
<2~4줄: 무슨 건이고 현재 상태>

## 등장 주체 / 신청 내역 / 공정 구성 …
| ... | ... |

## 쟁점·이슈 또는 핵심 내용
- 내용 / 원인 / **책임소재** / 합의·미결 / **주장 ↔ 근거 서류** …

## 다음 액션
- [ ] <할 일> — <담당> <기한>

## 출처 (Sources)
1. **<제목/문서명>** — <YYYY-MM-DD> · <발신→수신 또는 작성자> · 첨부: <…> · `<파일명>`
```
※ `# Claude Code` 안에서는 소제목을 `##`/`###`로 둔다(`#`은 본문 최상위 섹션 전용).

### 3.5 mentions 연결 — 사람 이름 ↔ Contacts (제안 → 확인 → 반영)
노트에 등장하는 **사람**을 `20. Contacts`의 연락처 노트와 연결해 `mentions:`로 올린다. 단, **반드시 사용자 확인 후에만 반영**한다(자동 기입 절대 금지).

1. **이름 추출** — 회의록이면 `# Tiro` 전사·`# Yejun's memo`·참석자, Event/메일이면 발신·수신·CC·본문에서 등장 인물을 모은다. 회의에 참석한 사용자 본인(Kim Yejun)도 포함.
2. **Contacts 대조** — 추출 이름을 `C:\Users\Z006K14G\Desktop\Yejun\20. Contacts\**`의 연락처 **파일명**과 매칭한다. 표기 흔들림에 관대하게(이름 순서·공백·콤마·로마자/한글/한자 변형: 예 "Yang yohan"=양요한, "Doho, Haruka"=道法 春香). 매칭되면 **정확한 연락처 파일명**으로 위키링크를 만든다(`[[Ozeni Shin]]`처럼 실제 파일명과 일치해야 링크가 풀린다).
3. **분류해서 제시** — (a) **연락처 있음** → `- "[[파일명]]"` 후보, (b) **연락처 없음(신규 인물)** → 별도 목록으로 보고. 신규 인물은 임의로 mentions에 넣지 말고, 새 연락처 생성/ bare 링크 여부를 사용자에게 묻는다.
4. **사용자 확인 (필수)** — 제안 목록을 보여주고(AskUserQuestion 등) **승인된 사람만** `mentions:`에 기입한다. 매칭이 확실해 보여도 확인 없이는 쓰지 않는다.
5. **기존 mentions 보존·병합** — 이미 있는 항목은 유지하고 중복 제거. 형식은 YAML 리스트+큰따옴표 `- "[[이름]]"`(인라인 `[[A]] [[B]]`는 `[`를 flow 시퀀스로 오인해 frontmatter 전체를 깨뜨린다).

### 4. 볼트 프로젝트 폴더 찾기 → 확인 → 삽입 (소스 폴더만 받은 경우)
사용자가 **소스 폴더만** 주고 "옵시디언/볼트에 정리·삽입"을 원하면, 노트를 **볼트의 맞는 프로젝트 폴더에 넣되 반드시 먼저 확인**한다.

1. **프로젝트/고객 추론** — 소스 내용에서 프로젝트·고객명을 잡는다(메일이면 **최신 메일**의 건명·당사자·본문 기준; 폴더명·경로의 고객 키워드 SEJAL·Zhengrui·POSCO·HSC 등도 단서).
2. **볼트 스캔** — 프로젝트는 `C:\Users\Z006K14G\Desktop\Yejun\01. Projects\<카테고리>\<프로젝트>`에 있다([[obsidian-vault-root]]). 하위 폴더명을 훑어 **후보를 1~3개** 추린다(고객명·약어·기존 노트의 태그/내용으로 매칭).
3. **사용자 확인 (필수)** — **AskUserQuestion**으로 "이 프로젝트 폴더에 넣을까요?"를 물어 후보를 제시한다. 확신해도 **확인 없이는 쓰지 않는다**. 못 찾으면 후보 없음을 알리고 경로를 직접 받거나, 새 프로젝트 폴더 생성 여부를 묻는다.
4. **삽입** — 승인된 폴더에만 노트를 생성한다. 파일명은 날짜 prefix(`YYMMDD_<주제>.md`). 같은 폴더의 기존 노트 양식(frontmatter `Catetory`·태그 컨벤션)을 맞춘다.
5. **MOC 링크는 보류** — 프로젝트 `0_<프로젝트>.md`(MOC)에 자동으로 링크 추가하지 않는다(추후 별도 합의 전까지).

### 5. 보고
저장 경로 + 핵심 2~3줄 요약을 보고한다.

## 작성 규칙
- **볼트에 삽입할 땐 폴더를 반드시 사용자 확인** — 매칭이 확실해 보여도 AskUserQuestion으로 대상 프로젝트 폴더를 확인받기 전에는 노트를 쓰지 않는다(§4).
- **템플릿 frontmatter를 변형하지 않는다** — 필드명·순서·철자(`Catetory` 포함) 유지, 임의 필드 추가 금지.
- **내 분석은 `# Claude Code`에만 작성(Event·회의록 공통), 소스 폴더 바로가기는 `# Yejun's memo`에. `# Tiro`(회의록 전용)·`# Yejun's memo`의 기존 사용자 메모는 손대지 않는다.**
- **노트 템플릿이 우선** — 새로 쓰는 노트는 정본 템플릿 구조를 따른다(사용자가 전 노트를 이 형태로 통일 중). 옛 `## Event` 단일 구조로 쓰지 말 것. 작업 전 `50. Template\Event template.md`를 Read해 현재 섹션을 확인한다.
- **`description:`은 영어로 ~2줄(약 2문장)** — progressive(미리보기)용. 고유명사(SEJAL, PTJ, K-104 등)·수치 유지. 콜론/특수문자 있으면 큰따옴표. ([[note-description]]와 동일 정책)
- **`mentions:`는 Contacts와 대조해 제안하되 사용자 확인 후에만 반영한다(§3.5)** — 자동 기입 금지. 미확인·신규 인물은 넣지 말고 따로 보고. 형식은 YAML 리스트+큰따옴표 `- "[[이름]]"`(인라인 `[[A]] [[B]]`는 `[`를 flow 시퀀스로 오인해 frontmatter 전체를 깨뜨린다).
- **`tags:`는 [[obsidian-tagging-convention]]을 따른다** — nested `entity/<거래처>`·`topic/<주제>`. 메일 다이제스트면 `email-digest` 타입 태그를 추가해도 됨.
- **출처는 빠짐없이** — 모든 소스 파일을 한 줄씩(제목/문서명·날짜·발신→수신·첨부·파일명).
- 날짜는 `YYYY-MM-DD`로 통일(상대 날짜 금지). 파일명은 날짜 prefix(`260610_<주제>.md`).
- 한국어 정리는 [[korean-mom-gaejosik-style]](개조식 ~함 종결) 권장.
- 파일은 **BOM 없는 UTF-8**, 1행이 `---`(Write 도구 기본값으로 충족).
- 덤프(`_extracted_sources.txt`)는 작업용 중간산물 — 기본은 남겨두고, 원하면 삭제.

## 주의
- COM(Outlook/Word/Excel/PowerPoint) 보안 프롬프트가 뜨면 사용자에게 허용 요청.
- `.eml`/PST는 미지원(.msg). PDF는 덤프 포인터 → 필요 시 **Read 도구로 직접** 읽는다.
