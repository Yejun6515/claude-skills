---
name: remember-contacts
description: 리멤버(명함첩) 앱에서 내보낸 명함 데이터(.xlsx/.csv)를 옵시디언 `20. Contacts` 연락처 노트로 변환한다. 회사명을 볼트 표준값으로 정규화(포스코/POSCO/POSCO Gwangyang→POSCO, 현대제철→HSC, PRIMETALS/PTK→Primetals 등)하고, 이메일·이름 기준으로 기존 노트와 중복을 감지해 신규 생성 vs 병합을 분리한다. 병합 시 기존 노트의 빈 이메일/전화만 채우고 description·Team·mail-bridge 이력은 건드리지 않는다. 이름은 로마자 "성 이름" 파일명(김세혁→Kim Sehyeok, 角正憲→Kado Masanori), 회사별 폴더, 개인 명함은 Others. 반드시 리포트로 사용자 확인 후 저장(자동 기입 금지). 트리거 - "명함 옵시디언에 넣어줘", "리멤버 명함 변환", "명함첩 엑셀 연락처로", "이 명함 정리", "card import".
---

# remember-contacts — 리멤버 명함 → 옵시디언 연락처 노트

리멤버(명함관리 앱)에는 공식 API도 MCP 커넥터도 없다. 유일한 경로는 **리멤버 → 내보내기(엑셀/CSV) → 디스크 경유 변환**이다. 이 스킬은 그 내보내기 파일 하나를 받아 `20. Contacts` 노트로 옮긴다.

원칙(옵시디언 파이프라인 공통): **승인 전 자동 기입 금지.** 반드시 파싱 리포트로 사용자에게 신규/중복/미매핑 회사를 보여주고 확인받은 뒤에만 파일을 쓴다. 위키 노트는 읽기만. (`note-digest`·`note-description`와 동일 게이트)

## 입력
- 내보내기 파일: `.xlsx` 또는 `.csv` (같은 컬럼 매핑). 보통 `C:\Users\Z006K14G\Downloads\개인명함첩_*.xlsx`.
- 사용자가 파일을 명시하지 않으면 Downloads에서 `개인명함첩_*` 최신본을 찾아 확인.

## 볼트 컨벤션 (반드시 준수)
- 대상 폴더: `C:\Users\Z006K14G\Desktop\Yejun\20. Contacts\<회사폴더>\`
- 노트 포맷 (**현재 볼트 포맷** — 옛 `Category`/`#Contact` 태그 포맷 아님):
  ```markdown
  ---
  Company: POSCO
  description: "one-line English summary"
  ---

  ## 1. Team : 투자엔지니어링실 EM그룹

  ## 2. Name & Title : 김세혁, 차장

  ## 3. E-mail : noworries@posco.com

  ## 4. Phone number : 010-9290-6471

  ## 5. Remarks
  ```
  - `Company:` 스칼라 한 값. 콜론 앞뒤 공백 `## 1. Team : ` 형식 유지.
  - `description`: 영어 한 줄. 명함만 있는 콜드 컨택은 과장 금지 — 회사·직무·"from business card" 수준의 사실만. 프로젝트 링크를 지어내지 말 것.
  - 태그 섹션(`## 6. Tags`) 없음. `## 5. Remarks`는 비워둠(향후 mail-bridge가 이력 축적).
- 파일명: 쉼표 없는 **로마자 "성 이름"** (`contact-name-convention`). 한국인 로마자(김세혁→`Kim Sehyeok`), 일본인 romaji `Family Given`(角正憲→`Kado Masanori`), 서양·중화권 명함은 표기를 "성 이름" 순으로(MASAHIRO KUCHI→`Kuchi Masahiro`, Yang Qiang→`Yang Qiang`). ALL-CAPS는 Title Case로.
- 파일은 BOM 없는 UTF-8, 날짜 `YYYY-MM-DD`, 태그에 공백 금지.

## 워크플로우

### 1) 파싱 + 정규화 + 중복 스캔 (스크립트)
```
python scripts\parse_cards.py --export "<xlsx/csv>" --vault "C:\Users\Z006K14G\Desktop\Yejun" --out "<scratchpad>"
```
- 컬럼 헤더를 유연 매칭(회사/이름/부서/직함/전자 메일 주소/휴대폰/근무처 전화/메모; Google Contacts 영문 헤더도 지원).
- `reference\company_map.json`으로 회사명 → 표준 `Company` + 폴더. 매핑에 없으면 `UNKNOWN`으로 리포트(사용자에게 폴더 확정 요청 후 map에 추가).
- 개인·비업무 명함(빈 회사, 웨딩/호텔/의료 등 `personal_to_others`)은 `Others` 폴더.
- 중복: 기존 `20. Contacts\**\*.md`에서 `## 3. E-mail :` 값과 본문을 스캔해 **이메일 완전일치**(강) → **이름 원문 완전포함**(중) 순으로 매칭. `cards.json`·`report.md` 출력.

### 2) 사용자에게 리포트 제시 (게이트)
`report.md`를 보여주고 확인받는다:
- 신규 N / 중복 N / 미매핑 회사 목록
- 신규 폴더가 새로 생기는 회사 목록
- 중복 건은 "기존 노트의 빈 이메일/전화만 채움"임을 명시
- 미매핑 회사가 있으면 폴더명 확정 → `company_map.json`에 alias 추가 후 재실행

### 3) 노트 계획 작성 (Claude)
`cards.json`을 읽어 `notes.json`을 만든다. 카드별로:
- 신규: `folder`, 로마자 `filename`, `company`, 영어 `description`, `team`(부서), `name_title`("이름, 직함" — 원문 이름 그대로 두되 필요시 정돈), `email`, `phone`, (선택)`remarks`.
- 중복: `status:"merge"`, `merge_file`(기존 노트 절대경로), `email`, `phone`만. **기존 description·Team·이력은 절대 덮어쓰지 않는다.**
  - 병합 대상 노트의 Team이 카드의 부서와 다르면(예: TF 역할 vs 기본 소속) 기존 값을 존중하고 이메일/전화만 채운다.

### 4) 노트 생성/병합 (스크립트)
먼저 `--dry-run`으로 검증 후 실제 실행:
```
python scripts\write_notes.py --plan "<notes.json>" --vault "C:\Users\Z006K14G\Desktop\Yejun" --dry-run
python scripts\write_notes.py --plan "<notes.json>" --vault "C:\Users\Z006K14G\Desktop\Yejun"
```
- 신규: 폴더 없으면 생성, 파일 있으면 **덮어쓰지 않고 SKIP**(리포트).
- 병합: 빈 `## 3. E-mail :` / `## 4. Phone number :` 라인만 채움. 그 외 불가침.

### 5) 마무리
- 생성/병합/스킵 건수를 보고.
- key man·반복 등장 인물이면 프로젝트 개요 3.Stakeholders 승격을 옵션으로 추천(`project-overview-keyman-suggest`).
- 새로 생긴 회사 폴더가 있으면 알림.

## 회사 매핑 유지
`reference\company_map.json`이 진실의 원천. 새 회사가 나오면 canonical `company`+`folder`+`aliases`를 추가한다. 약어·표기변형(포스코/POSCO/POSCO Gwangyang Works, 현대제철/Hyundai Steel, PRIMETALS/PTK/PTJ)은 모두 aliases로.

## 관련
- `contact-name-convention`(파일명), `note-digest`/`note-description`(정리 게이트·frontmatter), `mail-bridge`(Remarks 이력 축적), `project-overview-init`(Stakeholder 링크).
- (나중에) 경로 B 완전자동화: 리멤버→구글 주소록→Zapier/Sheets 폴링. 현재는 경로 A(수동 내보내기) 채택.
