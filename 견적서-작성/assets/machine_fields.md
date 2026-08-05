# 기계 견적서 필드맵 — machine_master.xlsx

시트: `quotation  (2)`  ·  통화: JPY  ·  베이스: POSCO K1H Servo valve

수식(자동, **건드리지 말 것**): `W28=SUM(W24:W27)` 장비소계 · `W34=N34*L34` SV가격 · `W37=W28+W34` 총계

**문구 표준(2026-08 승인 지적 반영) → C-2 필독.** 결제·보증 조항의 콜론·일수 표기·어순 규칙. verify가 [FAIL]로 잡는다.

**T&C 섹션 구성(2026-06 개정):** 1.Price · 2.Terms of Payment(Equipment + Supervising) · 3.Time of Delivery · 4.Terms of Delivery · 5.General conditions · 6.Guarantee Period · 7.Validity · 8.Other Conditions(우선순위 조항만). 세금·Export Control은 표준약관(첨부 PDF) Art.6/Art.22가 커버하므로 본문 미포함.

**1.Price 하위 넘버링:** `(1)` 견적건명 → 그 아래 `1) Equipment / 2) Supervising / 3) Total`, `(2)` Conditions of dispatching SV. (상위 `1.~8.`와 구분)

**⚠️ machine_master.xlsx는 손질본(hand-maintained)** — 1.Price 표 레이아웃(넘버링·`N:V` 병합·표만 테두리·인쇄 fit)은 Excel에서 수동 조정됨. **build_masters.py로 재생성하지 말 것**(레이아웃 날아감). 손으로 다듬은 draft를 마스터로 되접으려면 `python build_masters.py <draft.xlsx>` (헤더 토큰만 복원).

**⚠️ 인쇄 레이아웃(칸 폭·행 높이·병합)은 E 섹션 규칙을 지킬 것.** 칸을 넓히면 인쇄 축소율이 떨어져 글자가 다시 작아진다.

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
  - (1) D67 `100% of the total price shall be paid by T/T within (30) days after the signing of a time sheet.`
  - (2) **삭제** — `fill`이 C68/D68을 자동으로 비움(행은 지우지 않아 아래 참조 보존).
- B는 `fill`이 D67 교체 + C68/D68 비움까지 한 번에 처리하므로 `cells`로 손댈 필요 없음. A↔B 전환이 필요하면 master에서 새 `new`로 다시 시작(B는 비가역적으로 D68을 비우므로).

## C-2. ⚠ 결제·보증 문구 표준 (2026-08 승인절차 지적 반영)

승인에서 지적받은 문구 규칙. **master는 이미 수정됨**. 고객 조건에 맞춰 결제줄을 손으로 고쳐 쓸 때도 이 형태를 유지할 것 — `verify`가 아래 패턴을 **[FAIL]로 검출**한다(`quote.py`의 `BANNED_PHRASES`).

| # | 금지 | 표준 | 이유 |
|---|---|---|---|
| 1 | `...total price: Shall be paid...` | `...total price shall be paid...` | 콜론+대문자 시작은 문장 아님. 모든 결제줄 동일 양식 |
| 2 | `within 30days`, `within 90days` | `within (30) days`, `within (90) days` | 일수는 **괄호 + 띄어쓰기**로 통일 |
| 3 | `shall be paid ... within 1 month` | `... within (30) days` | 결제기간은 **일(days)**로 통일 (납기의 months는 정상) |
| 4 | `paid by T/T as for Advance Payment within (30) days` | `paid by T/T within (30) days as for Advance Payment` | 기간을 `by T/T` 바로 뒤에 — 어느 기간인지 모호해짐 방지 |
| 5 | `from the date of presentation of Final Acceptance Certificate` | `from the date of Final Acceptance Certificate` | "presentation"이 애매한 표현 |

**적용 후 master 표준문구:**
- D59 `{{PAY_ADV_PCT}}% of the total price shall be paid by T/T within (30) days as for Advance Payment against our invoice after the contract.`
- D60/D61 `{{PAY_LC_PCT}}% of the total price shall be paid by the way of an irrevocable letter of credit (L/C) issued by the customer's Bank in favor of the Seller within (90) days after contract.`
- D62/D63 `{{PAY_FINAL_PCT}}% of the total price shall be paid by T/T within (30) days after the Buyer's receipt of the Seller's invoice, Final Acceptance Certificate issued by Buyer.`
- D81/D82 `Guarantee Period is 12months from the date of Final Acceptance Certificate, or 22 months after FOB/FCA date, whichever comes earlier.`
  - ※ 소프트웨어 건은 D82를 `or 22 months after the Seller's delivery of the software, whichever comes earlier.` 로 교체(사례 있음).

## D. 고정 조항 (보통 그대로, 필요시만 손댐)
- **4. Terms of Delivery** (D74): `FOB / FCA ... INCOTERMS 2020` 기본.
- **5. General conditions**: 표준약관(첨부 PDF)을 계약에 편입하는 조항. 첨부 PDF명만 최신인지 확인. **삭제 금지**(이게 T&C 효력의 고리).
- **8. Other Conditions**: 견적서 조건이 표준약관(Sales-Conditions)보다 우선한다는 precedence 조항만.
- **세금(Tax/Duties) 조항**: 기본 미포함(삭제됨). **표준약관 PDF Article 6 "Taxes, Fees, etc."가 커버함(2026-06 원문 확인)** — "모든 세금·관세·customs duties는 Customer 부담". 5. General conditions가 PDF로 연결하므로 본문 삭제 안전. 고객이 본문에 명시적 세금조항을 요구하는 건에만 5번 위에 추가.

## E. 인쇄 레이아웃 표준 (2026-08-05 개정) — 글자 크기 사고 방지

**문제였던 것**: 인쇄영역 `A:X` 총 폭이 777pt(A4 인쇄가능폭 524pt의 1.5배)라 「1페이지 너비 맞춤」이 **67%로 축소** → 셀은 Arial 11pt인데 **종이에서 7.2pt**. 게다가 41~42행 SV 조건문이 **우측에서 잘려 인쇄**되고 있었음(`...from 0` / `one-wa` 에서 끊김).

**개정 후**: 총 폭 **617pt → 인쇄 83% → 본문 9.1pt**(제목 16.6pt). 2페이지 유지, 잘림 없음.

### E-1. 칸 폭 (pt) — **넓히지 말 것**
| A | B | C | D | E~J | K | L | M | N~S | T | U | V | W | X |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 12 | 22 | 15 | 15 | 105 | 19 | 19 | 15 | 6 | 5 | 60 | 120 | 42 |

Excel `ColumnWidth`(문자단위) = `(pt - 3.75) / 6`. 표 구성은 Items `E:K`(195pt) · EA `L:M`(38) · Price/EA `N:V`(161) · Price `W`(120), `X`는 표 밖 여백. 품목명이 길면 **K를 넓히지 말고 줄바꿈**(`Alt+Enter`)으로 처리.

### E-2. 병합 + 자동줄바꿈 셀 (긴 조건문)
행을 늘리면 셀 주소가 밀려 필드맵이 깨지므로, **행 추가 대신 병합+wrap**으로 처리한다.

| 셀 | 병합 범위 | 행 높이 | 내용 |
|---|---|---|---|
| E41 | `E41:X41` | 56pt (4줄) | SV 근무조건 문장 **전체**. 예전엔 E41/E42로 쪼개져 있었음 → **E42는 비움**(행 높이 3pt) |
| D59 | `D59:X59` | 28pt (2줄) | Equipment 선급 결제 |
| D67 | `D67:X67` | 28pt (2줄) | Supervising 결제 (1) |
| D68 | `D68:X68` | 28pt (2줄) | Supervising 결제 (2) |

병합셀은 세로정렬 **위(top)**, 짝이 되는 번호칸(C59·C67·C68·D41)도 top으로 맞춤.
⚠ 병합+wrap 셀은 Excel이 **자동 행높이를 못 잡는다** — 문구를 길게 고치면 행 높이를 직접 올릴 것.

### E-3. 수동 분할 유지 셀 (문구 동일, 나누는 위치만 조정)
`D60`/`D61`(L/C), `D62`/`D63`(잔금), `D89`/`D90`(precedence), `E43`/`E44`(overtime) 는 두 셀 분할을 유지한다. **`{{마커}}`가 실제 값(`70` 등)보다 길기 때문에** 마커 상태에서도 안 잘리는 위치에서 끊어 놨다.

### E-4. 한 줄 길이 한도 (Arial 11pt)
| 시작 열 | 최대 폭 |
|---|---|
| D열 시작 | **563pt** (≈ 118자) |
| E열 시작 | **548pt** (≈ 115자) |
| F열 시작 | **533pt** |

넘으면 인쇄에서 **오른쪽이 잘린다**(경고 없음). 조건문을 고쳐 쓸 때 한 줄이 이 길이를 넘으면 병합+wrap으로 바꾸거나 다음 행으로 나눌 것.

### E-5. 행 높이 · 2페이지 유지
- 기본 본문행 **14pt**(조건문 나열 구간 43~53·58~63은 13pt), 여백행 8pt, 제목행(5·11) 27pt
- 품목행 24~27 = **28pt**(품목명 2줄용), Sub Total 28행 = 22pt
- **병합+wrap 행은 예외**: 41행 **56pt**(4줄), 59·67·68행 **28pt**(2줄)
- ⚠ **행 높이를 일괄 조정할 때 41·59·67·68을 건드리지 말 것** — 줄이면 두 번째 줄부터 소리 없이 잘린다(2026-08-05 실제 발생)
- **페이지1(1~64행) 합계 ≤ 890pt 권장** — 현재 896.5pt이고 인쇄 83%에서 744pt(한도 757pt)로 통과. 여기서 더 늘리면 3페이지가 된다
- 품목이 4개를 넘어 행을 추가하면 이 한도를 먼저 확인. 반대로 안 쓰는 `{{EQ2~4_DESC}}` 행을 지우면 여유가 늘어난다.

### E-7. 마스터 위생 (2026-08-05 정리) — 건드리면 draft가 안 열린다
원본 워크북에서 딸려온 쓰레기를 제거했다. **되살리지 말 것.**
- **외부 링크 13개 제거** — `\\Mhsv1203\...`, `C:\ＭＨ共用\...` 등 2003~2004년 미쓰비시·히타치 공유드라이브 파일 참조. 남아 있으면 **Excel로 마스터를 한 번이라도 저장하는 순간 openpyxl 라운드트립 결과물을 Excel이 못 연다**(externalLink rels의 rId 불일치). 즉 `quote.py fill` 산출물이 열리지 않는다. 마스터를 Excel에서 편집할 때 다른 파일을 참조하는 수식을 절대 넣지 말 것.
- **정의된 이름 528개 삭제**(대부분 `#REF!`) — `Print_Area`/`Print_Titles`만 유지.
- **`N24:V24`~`N27:V27` 병합 추가** — 이 병합이 없어서 Price/EA에 금액을 넣으면 열 폭이 좁아 **`#`으로 표시**되던 문제(헤더 `N23:V23`·SV행 `N34:V34`는 원래 병합돼 있었음).

**마스터를 Excel에서 손본 뒤 반드시 회귀 확인**:
```
python scripts/quote.py new machine <tmp>.xlsx && python scripts/quote.py fill <tmp>.xlsx values.json
```
→ 만든 xlsx가 **Excel에서 정상적으로 열리는지** 확인. 안 열리면 외부 링크가 다시 생긴 것이다.

### E-6. 스페어 양식
`spare_master.xlsx`는 인쇄 92% / 본문 9~11pt로 이미 정상. 다만 인쇄영역이 `A1:V72`로 잡혀 **빈 2페이지가 딸려 나오던 것을 `A1:V63`으로 수정**(2026-08-05). 양식 자체가 `P. 1/1` 표기이므로 **항상 1페이지**여야 한다.

---

## 검증 체크리스트 (draft 완성 후 자동 실행)

1. **마커 잔존 스캔**: `{{` 하나라도 남으면 → 안 채운 칸. 전부 0이어야 통과.
1-b. **문구 표준 스캔**(C-2): 콜론+`Shall be paid` / `30days` / 결제 `1 month` / Advance 어순 / `presentation of` → [FAIL]. 고객 요구로 예외를 써야 하면 사용자에게 확인 후 `BANNED_PHRASES`가 아닌 표현으로 재작성.
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
13. **인쇄 확인(E 섹션)**: 품목 행을 추가·삭제했으면 ① 페이지1 행높이 합계 ≤ 890pt(=2페이지 유지) ② 조건문을 고쳐 썼으면 한 줄이 D열 563pt / E열 548pt 이내인지. 애매하면 PDF로 뽑아 **우측 잘림**과 **페이지 수**를 눈으로 확인.
