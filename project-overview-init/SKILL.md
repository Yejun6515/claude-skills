---
name: project-overview-init
description: 새 프로젝트 폴더에 표준 개요 노트(`0_<폴더명>.md`)와 문서이력 Base(`0_<폴더명>_submission.base`)를 만든다. 5섹션 표준구조(Project Overview·Sales Activities·Stakeholders·Project management·Learning), 활동 4칼럼 테이블(최신순), PO 계약 기준선, submission Base(폴더필터+Date DESC)로 생성하고, Stakeholder 이름은 `20. Contacts`에 있으면 `[[링크]]`로 잇는다. 트리거 - "프로젝트 개요 만들어줘", "0_ 개요랑 base 만들자", "프로젝트 개요랑 base 작성", "새 프로젝트 폴더 세팅", "개요 노트 만들어줘". 폴더 하나(또는 방금 만든 프로젝트 폴더) 대상.
---

# project-overview-init

새 프로젝트 폴더에 **개요 노트 `0_<폴더명>.md` + 문서이력 `0_<폴더명>_submission.base`** 한 쌍을 표준구조로 생성한다. Vault 루트: `%USERPROFILE%\.claude\skills\_config\local-paths.md`의 `vault_root:` 값(없으면 사용자에게 물어 저장).

> **왜 정형화하나**: 새 프로젝트를 시작할 때마다 반복되는 세팅(개요 5섹션 + submission Base)이라, 매번 기존 예시를 찾아 미러링하지 않고 일관되게 찍어낸다. 구조는 [[project-overview-template-convention]] 컨벤션을 따른다.

## 절차
1. **대상 폴더 확정**: 사용자가 준 폴더 경로. "방금 만든 프로젝트"면 직전에 생성/작업한 프로젝트 폴더. 불명확하면 물어본다. 폴더명 = 파일명 접두어(`0_<폴더명>`).
2. **중복 가드**: 폴더에 이미 `0_*.md`·`0_*_submission.base`가 있으면 **덮어쓰지 말고** 사용자에게 알린다(기존 유지/갱신 여부 확인). 없을 때만 신규 생성.
3. **맥락 수집(있으면)**: 폴더 안 이벤트/Inquiry 노트(`YYMMDD_*.md`)나 위키 프로젝트 현황을 읽어 **고객·설비·현단계·담당자**를 파악한다. 없으면 빈 스캐폴드로 생성(나중에 채움).
4. **개요 노트 생성** `0_<폴더명>.md` — **정본 템플릿 `{vault}\50. Template\Primetals_Project 템플릿.md`를 매번 Read해 복사**(하드코딩 금지, 개정본 자동 반영). 템플릿의 `<!-- HTML 주석 -->`은 채우기 가이드 — 내용을 채우며 소비/대체한다. 파악된 내용만 채우고 미상은 공란/“미정”. **프론트매터 없음**(`## 1.`로 시작). 상세 규칙(PO 계약 기준선·최신순 테이블·섹션 취급·key man 3.Stakeholders 승격 등)은 [[project-overview-template-convention]] 참조.
5. **Stakeholder 이름 → Contacts 링크**(§3):
   - PTJ/내부 담당자 이름을 `{vault}\20. Contacts` 노트와 대조 → **정확히 일치하는 노트가 있으면 `[[이름]]`** 으로 링크.
   - **동명이인 주의**: 성만 같은 경우(예 Kobayashi Munehito ↔ Toshimitsu) 메일주소·풀네임으로 인물을 특정한 뒤 링크. 확신 없으면 텍스트로 두고 보고.
   - **고객사·상사(TEX 등) 측 인물은 링크하지 않는다**(Contacts에 두지 않는 컨벤션). 고객사·제조파트너 자체는 위키 엔티티 링크(`[[Jiangsu Fullways]]`·`[[SEJAL]]`)로.
6. **Base 생성** `0_<폴더명>_submission.base` — 아래 Base 템플릿. `file.folder`에 **vault 기준 상대경로**(백슬래시→슬래시, 예 `01. Projects/01.03 Other Customer/<폴더명>`)를 넣는다. 필터는 `Category.contains("submission")`, 정렬 Date DESC.
7. **보고**: 생성한 두 파일 경로 + 링크한 Contacts + (선택) 신규 프로젝트를 위키/상위 MOC에 이을지 제안.

## 개요 노트 = 정본 템플릿 복사
- 구조/문구는 `{vault}\50. Template\Primetals_Project 템플릿.md`가 정본(5섹션 + HTML 채우기 가이드). **하드코딩 사본을 두지 않는다** — 스킬 실행 시 정본을 Read해서 쓴다.
- 이 스킬이 정본에 **추가하는 것**: ① §2 리드줄·활동표를 폴더 맥락으로 초안 채움 ② §3 Stakeholder 이름을 `20. Contacts` 대조해 `[[링크]]`(절차 5) ③ 짝이 되는 submission Base 생성(아래).

## Base 템플릿 (`0_<폴더명>_submission.base`)
```yaml
views:
  - type: table
    name: 표
    filters:
      and:
        - file.folder == "<vault 기준 상대경로>"
        - Category.contains("submission")
    order:
      - file.name
      - Date
      - Category
    sort:
      - property: Date
        direction: DESC
      - property: Category
        direction: DESC
      - property: file.name
        direction: ASC
    columnSize:
      file.name: 573
      note.Date: 253
```

## 제약
- **덮어쓰기 금지**: 기존 `0_` 파일이 있으면 확인 없이 갱신/삭제하지 않는다.
- 개요 노트는 **프론트매터 없이** `## 1.`로 시작(활동 테이블은 최신순).
- 소스에 **없는 사실은 지어내지 않는다**(미상은 “미정”·공란).
- Base `file.folder`는 반드시 **vault 상대경로·슬래시(/)** — 절대경로·백슬래시는 매칭 실패.
- BOM 없는 UTF-8, 날짜 `YYYY-MM-DD`, 한국어 개조식(~함).
- 위키/상위 MOC 연결이나 소스→노트 정리는 이 스킬 밖 — 각각 [[wiki-ingest]]·[[note-digest]] 소관. `meeting-folder-brief`가 새 프로젝트 감지 시 이 스킬을 호출할 수 있다.
