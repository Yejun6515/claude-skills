---
name: breakdown-rev-compare
description: "Use when comparing two revisions of a PTJ/POSCO cost breakdown (e.g. Rev4 vs Rev7), adding a new offer block (260630 등) to a K3CX_ME-style breakdown sheet, allocating a firm offer price into per-line Final Submit by markup, making a breakdown's check cell (e.g. AG2) come out TRUE, or building an increase/decrease comparison sheet for customer/internal approval. POSCO·PTJ 견적 breakdown, 블록 추가, 마크업/Final Submit, scope diff."
---

# Breakdown Rev 비교 / 블록 추가

K3CX_ME형 breakdown 시트에 새 Rev의 offer 블록을 추가하고, Rev 간 원가를 비교한다.
**견적계산서 읽기(Eng/Manu 추출)는 `견적서-작성` 스킬의 `assets/meisai_breakdown_read.md` 참조.**

## breakdown 시트 구조 (K3CX_ME)
좌우로 **offer 블록**이 나란히. 각 블록 = 10열:
`[타입, Eng, Manu, M+E(=Eng+Manu), Total(=Eng+Manu), %(=M+E/(c)), Firm안분(=(h)×%), Markup%(=Final/M+E), Final Submit(수동), 비고]`
- 데이터 행 + 합계행: **(a) Sum Engi / (b) Sum Manu / (c) Total=(a)+(b) / HTC(d) / (e)=(c)+(d) / SV행 / Total incl SV**.
- 앵커: **(h) firm offer w/o SV** (하드코딩 셀), **(c)=SUM** 셀. %·Firm안분은 이 앵커 참조($절대).
- **(h) = 제출가 − SV.** SV = 일단가 × MD (예 220kJPY/day; PTJ 일수, HTC MD). incl-SV 합 = 제출 총액.

## 워크플로
1. **추출**: 새 Rev `見積計算書(詳細)` → 품목코드별 Eng/Manu 피벗 (meisai_breakdown_read.md). 헬퍼 시트로 만들어두면 검증 편함.
2. **scope diff**: 코드별 原価計 old vs new → 변경 후보. **Eng 불변·Manu만 상승 = 제작원가 재산정(스코프 변경 아님)**; Eng 급증 = 신규설계.
3. **블록 추가**: 직전 블록 열범위(예 P:Y)를 **통째 복사** → 새 위치(Z:AI). 복사 후:
   - 절대앵커 참조 교체: `$V$1→$AF$1`, `$Y$1→$AI$1` (Range.Replace, +10열 시).
   - Eng/Manu 입력열만 새 값으로 덮어쓰기(정적). 복사가 가져온 특수수식(예 `=194206-R35`)·정적 소계(72/73행)·수동 lump(1-57 r58, S58)·잔여 정적 M+E(Cooler) 모두 새 값으로 정리.
   - 앵커 갱신: (h)·HTC(d)·SV행. 합계행 (a)=`(c)-(b)`, (b)=`SUM(M+E열)` 수식화.
4. **검증(필수)**: 라인↔코드 맵을 **직전 Rev 피벗에 흘려 기존 블록 Eng/Manu를 재현(FAIL=0)** 하면 맵 신뢰 → 새 Rev 값 대입. 분할라인(예 `1-11 9)`=기어박스/스핀들)은 부품행으로 분할, 합쳐진 라인(`6),7)` 등)은 코드합.
5. **Final Submit & 체크(AG2 TRUE)**:
   - 체크셀 = `(Firm안분합 == Final합)`. Final합(`SUM`)이 **firm offer (h)** 와 같아야 TRUE.
   - 각 manu 라인 Final = **직전 Rev markup% × 새 M+E → 라운드**. 작은 변동 항목은 직전 Rev Final 그대로(설명 최소화).
   - **엔지니어링 lump 행**(Sum Engi)이 잔액 흡수(=`(h) − Σmanu`) → 합 정확히 일치. (또는 엔지 고정시 한 항목이 잔액 흡수.)
   - firm offer가 비-라운드(예 ...640)면 **한 항목이 끝자리 흡수**(완전 라운드 불가).
   - AF2(안분합)는 `=ROUND(SUM(...),0)`로 두면 float 불일치 회피.
6. **비교 시트**: 큰 항목만(소액은 '기타' 합산), **증가 빨강/감소 파랑**, "주요 원인" 열(내부승인용). 일/한 버전 가능. lump 아티팩트(분할→합산) 주의해 묶어서 표기.

## Excel/COM 함정 (중요)
| 증상 | 대응 |
|---|---|
| 복잡 워크북에서 `.Value2`에 2D/1D 배열 대입 간헐 `cast to String` 실패 | **per-cell `.Value2`** 가 가장 안정적 |
| 코드 `1-5`가 날짜로 자동변환 | 라벨열 `NumberFormat="@"` 먼저 |
| 파일 열 때 "update external links" 팝업 | 링크 끊기: `LinkSources(1)` 순회 `wb.BreakLink($name,1)` (현재값 고정) |
| `$o.Range($o.Cells.Item(..),$o.Cells.Item(..))` 인라인이 오버로드 오답 | 선계산 `$top/$bot` 변수 사용 |
| 사용자가 파일 열어둔 채 저장 | 잠금 → **닫아달라고 요청** 후 저장 |

## 검산 (항상)
- (c) = (a)+(b), AE74(또는 해당)=100%, Firm안분합=(h), Final합=(h)→체크 TRUE.
- (e)=(c)+(d), incl SV = (e)+SV = 제출 총액(= 제출가 PTJ+HTC).
- 분할 소계가 원래 라인값(기어박스→r15, 스핀들→r16) 재현.

## 흔한 실수
- Twin→Single Drive 등 **이전 Rev에도 있던 변경을 신규 원인으로 오인** → Eng 델타로 스코프변경 여부 판별.
- lump 분할 아티팩트(ROLL COOLANT를 한 행에 합치면 Back Wash/Cooler가 −100%로 보임) → 묶어서 net으로 설명.
- 체크셀 한쪽(안분합)이 비어 항상 FALSE → 양쪽 다 채울 것.
