# 기계 견적서 필드맵 — machine_master.xlsx

시트: `quotation  (2)`  ·  통화: JPY  ·  베이스: POSCO K1H Servo valve

수식(자동, **건드리지 말 것**): `W28=SUM(W24:W27)` 장비소계 · `W34=N34*L34` SV가격 · `W37=W28+W34` 총계

**T&C 섹션 구성(2026-06 개정):** 1.Price · 2.Terms of Payment(Equipment + Supervising) · 3.Time of Delivery · 4.Terms of Delivery · 5.General conditions · 6.Guarantee Period · 7.Validity · 8.Other Conditions(우선순위 조항만). 세금·Export Control은 표준약관(첨부 PDF) Art.6/Art.22가 커버하므로 본문 미포함.

**1.Price 하위 넘버링:** `(1)` 견적건명 → 그 아래 `1) Equipment / 2) Supervising / 3) Total`, `(2)` Conditions of dispatching SV. (상위 `1.~8.`와 구분)

**⚠️ machine_master.xlsx는 손질본(hand-maintained)** — 1.Price 표 레이아웃(넘버링·`N:V` 병합·표만 테두리·인쇄 fit)은 Excel에서 수동 조정됨. **build_masters.py로 재생성하지 말 것**(레이아웃 날아감). 손으로 다듬은 draft를 마스터로 되접으려면 `python build_masters.py <draft.xlsx>` (헤더 토큰만 복원).

---

## A. 식별값 — `{{마커}}` (안 채우면 검증에서 적발 = 문제 C)

| 마커 | 셀 | 의미 | 비고 |
|---|---|---|---|
| `{{REF_NO}}` | W2 | Ref. No. (예: 0025S242) | 첫 제출=접미 없음. **재제출(개정)은 `-R1`,`-R2`** (예: `0025S242-R1`). 인터뷰에서 "신규 vs 개정 Rn" 확인 |
| `{{DATE}}` | W3 | 견적일 (예: May 15, 2026) | |
| `{{CUSTOMER}}` | B7 | 수신처 Messrs (정식명 + Attn 담당자) | 예: POSCO Co., Ltd. (Attn: Mr. Kim Sangbeom) |
| `{{CUSTOMER_SHORT}}` | E50 | 통역 준비 주체 = **회사 약칭만** (Attn 없이) | 예: POSCO. 통역은 회사 차원 준비라 담당자 표기 안 함 |
| `{{SUBJECT}}` | B11, B14, D20 | 건명 | **3곳** 모두 동일하게 |
| `{{EQ1_DESC}}`..`{{EQ4_DESC}}` | E24~E27 | 장비 품목명 | 안 쓰는 행은 행 삭제 |
| `{{SPEC_NO}}` | E29, E35, E53, D109 | Proposal Spec 번호 | **4곳** 모두 |
| `{{DELIVERY_MONTHS}}` | D71 | 납기 개월수 | 숫자 |
| `{{VALIDITY_DATE}}` | D85 | 유효기일 | **견적일보다 미래** |

**1.(1).1 헤더(E22) — Spare 자동 정리:** `Equipment + Recommended Spare parts`. **추천 예비품 품목이 없으면 `Equipment`로 자동 변경**(`fill`이 E24:E27에 'spare' 문자 없으면 자동 정리). 강제 유지/삭제는 `values.json`의 `"spare": true|false`. 예비품 빠지는 개정건(Rev.1 등)에서 흔함.

## B. 숫자 입력칸 — 빈칸 (인터뷰에서 채움)

| 셀 | 의미 |
|---|---|
| N24~N27 | 장비 품목 Price/EA |
| W24~W27 | 장비 품목 Price (보통 N과 동일; 수량 있으면 N×수량) |
| L34 | SV dispatch MD 수 (내부견적 `見積纏め` §4 計 C-MD와 일치하는지 확인) |
| N34 | SV 단가 — **표준 JPY 220,000/MD**. ⚠ **SV 알라밍**: verify가 항상 `220,000×L34 MD`를 표면화해 확인 요구, **N34≠220,000이면 경고**. 다르면 의도 명시 |

## B-2. SV dispatch conditions (Supervising Service) — 표준 (master `(2) Conditions of dispatching` 블록)
- **MD 기준 = CMD (Calendar Man-Days)** — 달력 기준 산입(주말·휴일 포함한 체재일). 내부견적 `見積纏め` §4 計 **C-MD**와 일치. (표 라벨은 `CMDs` 로; WMDs 아님)
- **근무조건**: 주 **6일(월~토)**, 1일 **8 working hours, 08:00–17:00 (점심 1시간 포함)**.
- **이동일**: MD에 **산입**. **일본 왕복은 편도당 1일** 계상.
- **Overtime**(근무조건 초과분) 요율(엔/시/인): 월~토 ~22시 **35,000** / 22시~ **42,000**; 일·휴일 8~17시 **42,000** / 17~22시 **49,000** / 22시~ **55,000**.
- **통역**: 고객({{CUSTOMER_SHORT}}) 준비.
- ⚠ **Overtime 요일 그룹핑은 근무주에 맞출 것**: 6일제면 `월~토 / 일·휴일`, 5일제 건이면 `월~금 / 토·일·휴일`로 수정. (master 기본값=6일제)

## C. 조건문 — MUST-CONFIRM (표준문구 유지, 매번 명시 확인 = 문제 D)

| 마커/셀 | 표준값 | 확인 포인트 |
|---|---|---|
| `{{PAY_ADV_PCT}}` | D59 | 보통 10~20 | Equipment 선급 % |
| `{{PAY_LC_PCT}}` | D60 | 보통 70~80 | **L/C %·발행조건이 이 고객에 맞나** |
| `{{PAY_FINAL_PCT}}` | D62 | 보통 10 | Equipment 잔금 % |
| Supervising 결제 (D67/D68) | **2지선다** — 인터뷰에서 반드시 어느 쪽인지 물어볼 것 | 토큰 아님. `fill`의 `"sv_payment":"A"|"B"`로 선택 |

**Supervising Services 결제조건 2지선다** (`values.json`의 `"sv_payment"`):
- **옵션 A** (기본, master 기본값) — `"sv_payment":"A"` 또는 생략:
  - (1) D67 `50% of Supervisory Services price shall be paid by T/T within (30) days of receiving Seller's Invoice with report showing 50% of man-days used.`
  - (2) D68 `Remaining 50% shall be paid by T/T within (30) days of receiving invoice with report showing all contract man-days used.`
- **옵션 B** (time sheet 일괄) — `"sv_payment":"B"`:
  - (1) D67 `100% of the total price: Shall be paid by T/T within 1 month after the signing of a time sheet.`
  - (2) **삭제** — `fill`이 C68/D68을 자동으로 비움(행은 지우지 않아 아래 참조 보존).
- B는 `fill`이 D67 교체 + C68/D68 비움까지 한 번에 처리하므로 `cells`로 손댈 필요 없음. A↔B 전환이 필요하면 master에서 새 `new`로 다시 시작(B는 비가역적으로 D68을 비우므로).

## D. 고정 조항 (보통 그대로, 필요시만 손댐)
- **4. Terms of Delivery** (D74): `FOB / FCA ... INCOTERMS 2020` 기본.
- **5. General conditions**: 표준약관(첨부 PDF)을 계약에 편입하는 조항. 첨부 PDF명만 최신인지 확인. **삭제 금지**(이게 T&C 효력의 고리).
- **8. Other Conditions**: 견적서 조건이 표준약관(Sales-Conditions)보다 우선한다는 precedence 조항만.
- **세금(Tax/Duties) 조항**: 기본 미포함(삭제됨). **표준약관 PDF Article 6 "Taxes, Fees, etc."가 커버함(2026-06 원문 확인)** — "모든 세금·관세·customs duties는 Customer 부담". 5. General conditions가 PDF로 연결하므로 본문 삭제 안전. 고객이 본문에 명시적 세금조항을 요구하는 건에만 5번 위에 추가.

## 검증 체크리스트 (draft 완성 후 자동 실행)

1. **마커 잔존 스캔**: `{{` 하나라도 남으면 → 안 채운 칸. 전부 0이어야 통과.
2. **이전 건 잔존**: Subject/Ref.No/Spec번호에 다른 프로젝트 코드(0422N522 등) 안 남았는지.
3. **Ref.No 개정 버전**: 재제출이면 `-R1`,`-R2` 표기했는지 (verify가 Ref.No 표면화).
4. **결제 % 합**: `PAY_ADV + PAY_LC + PAY_FINAL = 100` (Equipment). Supervising은 옵션 A(50/50) 또는 B(100%/time sheet) — verify가 어느 쪽인지 표면화하니 의도한 쪽인지 확인.
5. **L/C 조건 확인**: 자동통과 금지 — "이 고객 L/C 조건이 D60 그대로 맞나?" 반드시 질문.
6. **Validity > 견적일**: D85 날짜가 W3보다 미래인지.
7. **합계 재계산**: Σ(W24:W27)=W28, N34×L34=W34, W28+W34=W37 일치(엑셀 재계산값).
8. **⚠ SV 알라밍**: N34=220,000(표준 일비)×L34 MD 확인. **N34≠220,000이면 경고** — 의도 명시. L34 MD수가 내부견적 §4 計와 맞는지도 확인.
9. **Equipment 헤더(E22)**: 예비품 품목 없으면 'Equipment'로 정리됐는지 (Spare 잔존 경고).
10. **납기·INCOTERMS**: D71 개월수 채움 + FOB/FCA 표기 존재.
11. **통화 JPY** 표기 존재.
12. **세금 조항 필요 여부** 1회 확인 (기본 미포함).
