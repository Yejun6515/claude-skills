---
name: 견적서-작성
description: "Primetals 고객 제출용 견적서(Quotation) 작성. 견적 내용(고객/품목/금액/납기/결제조건)을 주면 기계메인 또는 스페어 양식을 자동 선택해 빈 마스터를 채우고, 섹션별로 하나씩 확인하며 최종 draft xlsx까지 작성. 이전 건 텍스트 잔존(C)·고객별 결제/L/C 조건 누락(D)을 검증으로 잡아줌. 마스터는 스킬에 번들(self-contained). 사용자가 제출 견적서, 고객사 제출 견적서, 고객 제출용 견적서, 견적서 만들어줘, quotation 작성, 스페어 견적, 기계 견적 등을 요청할 때 사용. (내부견적 見積纏め는 ptj-internal-estimate 스킬 — 별개)"
---

# 견적서 작성

견적 내용을 받아 양식을 골라 채우고 **하나씩 확인하며** 최종 draft를 만든다.
마스터·필드맵은 **스킬에 번들**돼 있다 → `<skill>/assets/` (`machine_master.xlsx`, `spare_master.xlsx`, `*_fields.md`, `build_masters.py`). `quote.py`가 자동으로 찾으므로 `--templates`는 생략 가능(다른 위치를 쓸 때만 지정).

## 핵심 원칙
- **마스터는 절대 직접 수정 금지.** 항상 복사본에 작성.
- **수식 보존**: 단가·소계·합계, 스페어 유효기일(=견적일+45일)은 자동계산 → 건드리지 않는다.
- **두 가지 사고를 반드시 잡는다**:
  - **C 빠뜨림** → `{{마커}}` 잔존 스캔 (안 바꾼 고객명·Ref.No·Subject·Spec번호)
  - **D 틀림** → 결제·L/C·납기·준거법은 **자동통과 금지**, 매번 사용자에게 확인 질문.

## 워크플로

### 1. 양식 판별
입력에서 기계메인 vs 스페어 추정. 애매하면 한 번만 질문.
- 스페어 신호: "spare parts", 롤/WR/BUR/센서 등 부품 목록, 1페이지, SV 없음
- 기계 신호: 설비 개조/revamp, Supervising/SV 파견, Spec 첨부, 결제에 L/C·선급

### 2. 새 draft 생성
```
python <skill>/scripts/quote.py new <machine|spare> "견적서/<폴더>/YYYYMMDD_quotation_<고객>_<대상>.xlsx"
```

### 3. 섹션별 인터뷰 (하나씩 확인)
해당 `_fields.md`를 읽고 순서대로 사용자와 확인하며 값을 모은다:
헤더(고객·Subject·Ref.No·날짜) → 품목·수량·금액 → 결제조건 → 납기 → Validity → (기계: SV/잔업/보증).
**매 섹션 끝에 "이렇게 넣을게, 맞아?" 확인.** 특히 결제·L/C는 표준값을 그대로 두지 말고 이 고객 조건을 물어본다.
- **Ref.No 신규 vs 개정**: 같은 건 재제출이면 **`-R1`, `-R2`** 접미(예 `0025S242-R1`). 첫 제출은 접미 없음 — 어느 쪽인지 물어본다.
- **추천 예비품(Spare) 유무**: 없으면 1.(1).1 헤더가 `Equipment`로 자동 정리됨(`fill` 자동감지; 강제는 `"spare":false`). 예비품 빠진 개정건에서 흔함.
- **기계 Supervising Services 결제는 2지선다 — 반드시 물어본다**:
  - **A**: (1) 50% (man-day 50% 리포트 시) + (2) 나머지 50% (전체 man-day 리포트 시) ← 기본
  - **B**: (1) 100% (time sheet 서명 후 1개월 내 일괄)
- **SV 단가 220,000/MD 확인**: 표준 일비. MD수(L34)는 내부견적 `見積纏め` §4 計 C-MD와 일치해야. verify가 SV 알라밍으로 표면화.

### 4. 채우기
모은 값을 `values.json`으로 만들어 적용. `tokens`(마커치환, 반복 항목 자동) + `cells`(숫자/날짜 직접):
```json
{ "tokens": {"REF_NO":"0025S242","DATE":"May 15, 2026","CUSTOMER":"POSCO Co., Ltd. (Attn: Mr. ...)","CUSTOMER_SHORT":"POSCO","SUBJECT":"...",
             "SPEC_NO":"...","DELIVERY_MONTHS":"22","VALIDITY_DATE":"June 15, 2026","EQ1_DESC":"...",
             "PAY_ADV_PCT":"20","PAY_LC_PCT":"70","PAY_FINAL_PCT":"10"},
  "cells":  {"W24":76766000,"N24":76766000,"L34":95} }
```
> 기계 Supervising 결제는 **2지선다**(토큰 아님) — `values.json`에 `"sv_payment":"A"`(50/50, 기본) 또는 `"B"`(100%/time sheet 서명 후 1개월)를 넣는다. B는 `fill`이 D67 교체 + C68/D68 비움까지 자동 처리. 인터뷰에서 어느 쪽인지 반드시 확인.
> **Ref.No 개정**: REF_NO 토큰에 `-R1` 등 접미를 포함해 넣는다(예 `"REF_NO":"0025S242-R1"`).
> **Spare 헤더**: 예비품 품목 없으면 `fill`이 E22를 `Equipment`로 자동 정리(E24:E27에 'spare' 없을 때). 강제 유지/삭제는 `"spare": true|false`.
> **세금(Tax) 조항은 기본 미포함.** 고객이 본문에 명시적 세금조건을 요구하는 건에만 추가(표준약관 PDF 커버 여부는 원문 확인).
```
python <skill>/scripts/quote.py fill "<draft.xlsx>" values.json
```

### 5. 검증
```
python <skill>/scripts/quote.py verify "<draft.xlsx>" <machine|spare>
```
- `[FAIL]` (마커 잔존, 견적일 누락 등) → 반드시 수정 후 재실행.
- `[확인]` (결제%합·L/C·Validity 미래·준거법) → **Claude가 사용자와 직접 점검**. 통과 못 하면 멈춘다.
- 필요시 `quote.py dump` 로 전체 셀을 눈으로 재확인.

### 6. 완료 보고
draft 경로 + 검증 결과 + 사용자에게 확인받은 [확인] 항목을 요약.

## 見積計算書(詳細) 읽기 (breakdown용)
고객 제출 breakdown(예: K3CX_ME)을 만들 때 각 라인의 Eng(설계비)·Manu(제작비)는 `見積計算書(詳細)`에서 추출한다: **Eng=設計費(社内)+設計費(社外), Manu=原価計−Eng**, 품목코드(A열)로 group. 컬럼 위치는 견적서마다 다르니 **헤더 텍스트로 찾을 것**. 스코프 한정·날짜자동변환·분할코드 등 상세 절차 → **`assets/meisai_breakdown_read.md`**. (Rev 비교/블록추가는 `breakdown-rev-compare` 스킬)

## 참고
- **Primetals 로고**는 헤더(좌상단)에 자동 삽입된다. 원본은 `scripts/logo_primetals.jpeg`.
  openpyxl이 저장 때 이미지를 떨어뜨리므로 `new`/`fill` 끝에 `ensure_logo`로 다시 넣는다(멱등). 수동 복구는 `python quote.py logo <draft.xlsx>`.
- 셀 매핑·검증규칙: `<skill>/assets/machine_fields.md`, `assets/spare_fields.md`
- 행 추가(품목 多)·월별 납기표(Zhengrui 스타일)는 fields.md의 안내 참조.
- **마스터 관리**: 마스터는 `<skill>/assets/`에 번들. 스페어는 `assets/build_masters.py`로 생성. **기계는 손질본(hand-maintained)** — Price 표 레이아웃이 수동 조정돼 있어 재생성 금지. 사용자가 draft 레이아웃을 손보면 `python assets/build_masters.py <draft.xlsx>` 로 마스터에 되접음(헤더 토큰 복원).
