---
name: loa-risk-matching
description: "Build a contract-specific LoA risk matching sheet (리스크 매칭 시트) that maps every LoA Risk Questionnaire item (Small HQ-003-09 74항목 / Standard HQ-003-05 100항목) to the current contract's judgment — 구분(N/A/RC확정/판단 요/보류), 근거 문서·조항, draft 대비 충돌 — reusing the bundled 해설 매뉴얼 for Korean readings and RC criteria. Also serves/regenerates the 해설 매뉴얼 (question EN original + 한글 해석 + Explanatory Notes 기반 의미·목적 + 예시 + RC 기준). Use when the user asks for LoA 매칭 시트, 리스크 매칭, LoA 판정 정리, questionnaire 항목별 계약 매칭, LoA 해설 매뉴얼, or after a consistency 검토 to package results."
---

# LoA 리스크 매칭 (해설 매뉴얼 + 매칭 시트)

LoA 검토 산출물 3종 세트의 ②·③을 만든다. 스킬은 자기완결 — 매뉴얼·스크립트 전부 번들, U:\ 의존 없음.

| # | 산출물 | 성격 | 저장 위치 |
|---|---|---|---|
| ① | consistency 판정 xlsx | 계약 전용, 4렌즈 루프 판정 원본 | 계약 검토 폴더 (별도 프로세스: consistency-loop) |
| ② | 해설 매뉴얼 xlsx | **회사 공용 교육자료** (계약 무관, 재사용) | `assets/`에 번들; 사본은 공용/교육 폴더에 |
| ③ | 리스크 매칭 시트 xlsx | **계약 전용** — 매뉴얼 항목 × 이번 계약 판정 | 계약 검토 폴더, consistency 파일 옆, **별도 파일** |

②와 ③을 한 파일에 섞지 않는다(매뉴얼 재사용성). 사용자가 매뉴얼 안에 시트로 넣자고 하면 그때만 합친다.

## 번들 자산

- `assets/Small_LoA_해설매뉴얼.xlsx` — HQ-003-09 V5.4, 74항목
- `assets/Standard_LoA_해설매뉴얼.xlsx` — HQ-003-05 V5.3, 100항목(No="1.1"형), 마지막 열 = Small 대응번호
- `scripts/build_small_manual.py` / `build_std_manual.py` — 매뉴얼 재생성(내용이 코드에 전부 내장, 질문 개정 시 수정 후 재실행)
- `scripts/build_matching_template.py` — 매칭 시트 생성 템플릿

매뉴얼 열 구성: No / 대분류 / 소분류 / 질문 원문(EN) / **한글 해석(E열)** / 의미·목적(Explanatory Notes 기반) / 예시 / **RC 판정 기준(H열)** / 해설§(Small) 또는 Small대응(Standard). 매칭 시트는 E·H열을 읽어 쓴다.

## 매칭 시트 워크플로

1. **입력 확보**: 계약 폴더의 consistency xlsx('근거 (KO)' 시트, 컬럼 레이아웃은 템플릿 docstring 참조)와 status 메모(있으면). consistency가 없으면 매칭 불가 — 먼저 consistency 검토(4렌즈 루프)부터.
2. **상태 분류 확정**: 판정을 6구분으로 매핑해 템플릿 CONFIG의 set에 기입.
   - `N/A(초안 유지)` (기본값) / `N/A 종결(조항 확인)` / `RC 확정(RC3 등)` / `Region/Business`(Small 전용) / `판단 요`(★최우선/★핵심 표시) / `🔔 보류(문서 미입수)`
   - **판단 요 vs 종결의 경계**: 조항상 해당 "소지"가 확인됐지만 기재(escalation) 여부가 남은 것은 전부 판단 요 — 판단은 사용자 몫, 스킬은 보수적으로 surface만 한다.
3. **기준 문서 서술(BASIS)**: 판정에 실제 사용한 문서(GTC·사양서·draft 조건)와 **미입수 문서(특별조건·TLoA·위임액 등)를 헤더에 명시**. 미입수 근거 항목은 보류, 상위문서(특별조건 등) 없이 GTC 단독으로 종결한 항목은 비고에 "상위 계약문서 입수 후 재확인"(REVISIT set).
4. **생성**: `build_matching_template.py`를 scratchpad에 복사 → CONFIG만 채워 실행. `$env:PYTHONIOENCODING='utf-8'` 필수(PS5.1 cp932 오류 방지).
5. **검증(필수)**: 재오픈해 ①항목 수 = N_ITEMS ②빈 셀 0 ③구분 합계 = N_ITEMS ④최우선 항목 spot check. 요약 블록 건수를 채팅 보고에 그대로 사용.
6. 계약 폴더의 status 메모(`_LoA_status.md` 류)에 산출물·분포 한 줄 기록.

## 서식 (Primetals, primetals-text-style 준수)

맑은 고딕 10(EN 원문은 Arial 9) / 제목·No열 Dark Blue `0C2340` / 섹션행 Orange `E87722` + 연회색 fill / 헤더행 Dark Blue fill + 흰 글씨. 구분 색: 보류 Red `CE0037` · 판단 요 Orange · RC확정/Region Teal `00587C` · N/A Green `7A9A01`. 충돌 있으면 충돌열 Red. 틀고정 A6, 오토필터, zoom 90.

## 원칙

- **기준 문서를 항상 헤더에 명시**하고, 없는 문서로 아는 척하지 않는다 — 미입수는 보류로 드러낸다.
- 침묵·공백(조항 부재 = 무제한 책임 등)도 리스크로 surface. escalation 결정은 사용자.
- ★최우선/★핵심 표시는 Legal 서명 요건·자유기재(74/35.1) 문안의 근거 항목과 일치시킨다.

## 매뉴얼 재생성/확장

질문지 개정(V5.x) 시: 새 xlsm에서 질문 덤프 → build 스크립트의 데이터 블록 수정 → 재실행 → assets 교체. 의미·목적의 원 근거는 "Explanatory Notes to LoA Risk Questionnaire"(회사 공식 해설서, 번호체계=Standard, 끝에 Standard↔Small 매핑표). 소재 위치는 `_config/local-paths.md` 참조 대상이 아니라 사내 Template/Manual 폴더 — 필요 시 사용자에게 확인.
