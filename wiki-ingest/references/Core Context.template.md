---
type: core-context
aliases:
  - User Context
  - 핵심 맥락
description: User's identity, knowledge-reuse axes, and principles. wiki-ingest reads this BEFORE extraction so notes align with purpose, not just structure.
tags:
  - system
  - core-context
date created: {YYYY-MM-DD}
date modified: {YYYY-MM-DD}
snapshot_date: {YYYY-MM-DD}
status: template
version: "1.0"
---

# 🧭 Core Context — 업무 위키 사용자 맥락

> **사용법**: 아래 placeholder를 채우고 `status: template` → `status: active`로 바꾼다.
> 위키 루트(`90. Wiki`가 있는 볼트 루트)에 `Core Context.md`로 둔다.
> wiki-ingest가 추출 **전에** 먼저 읽어 "어떤 엔티티·개념이 재활용 가치 있나"를 판단한다.

---

## 1. Who — 정체성
- **이름 / 역할**: `{이름}` · `{직무}` (예: Primetals 영업·프로젝트)
- **전문 분야**: `{도메인}` (예: 제철 설비, 견적, 계약/LoA, 일본·중국 고객)
- **연속성 선언**: "{내 업무 기록이 결국 무엇을 더 잘하기 위한 것인지 1~2문장}"

## 2. Why — 재활용 축 (이 위키가 어디에 쓰일 것인가)
wiki-ingest는 추출 후보를 이 축 기준으로 우선순위 매긴다. 5~9개 권장 — 본인에 맞게 수정.
1. **제안 / 견적** — 고객 제안서·견적 작성에 재활용될 사실
2. **기술 자문** — 설비·기술 사양, 트러블슈팅 지식
3. **고객 대응** — 고객사·담당자·이력·요구사항
4. **프로젝트 실행** — 일정·납기·계약·LoA 관련
5. **교훈 (Learning from failure)** — 실패·리스크·재발방지
6. `{축 6}`
7. `{축 7}`

## 3. How — 추출 원칙 (3~5개)
- `{원칙 1}` (예: 확신 없는 추출은 만들지 말고 "확인 필요"로 보고)
- `{원칙 2}` (예: 고객사·설비·기술용어는 반드시 원자 노트로 분리)
- `{원칙 3}` (예: 회의록 원문·출처 링크는 절대 끊지 않는다)

## 4. 채우고 나서
- [ ] §1 정체성, §2 재활용 축(5~9), §3 원칙
- [ ] frontmatter `status: active` + `snapshot_date` 오늘 날짜
- [ ] `snapshot_date`가 30일 이상 오래되면 wiki-ingest가 갱신 권유
