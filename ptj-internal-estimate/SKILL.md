---
name: ptj-internal-estimate
description: "PTJ 내부견적서(見積纏め) 작성 — '내부 견적서 준비'·'내부 견적서'는 이 스킬. 견적부서 見積計算書（まとめ）의 製造原価를 받아 새 '見積纏め_Sales added' 시트를 맨 왼쪽에 추가(기존 시트 절대 수정 금지)하고 영업 가산(COMM·insurance·bond·CIT·Local Tax Agent·EBIT)을 채운다. §3는 overlay 행분해(機械=COMM/insurance/bond, SV=COMM/CIT/Local Tax Agent, 모두 受注価×%)이고 H31은 비순환 닫힌형이라 Excel 반복계산 불필요. SV 売値=D16(단가)×MD 고정, §5 残業·SV売値는 D16에 자동연동. 사용자가 PTJ 내부 견적, 내부 견적서 준비, 영업가산, 見積纏め, 商社口銭/COMM, 製造原価 기준 견적 등을 요청할 때 사용. (고객제출 견적서는 별개 스킬 견적서-작성)"
---

# PTJ 내부견적서 (見積纏め) — v2

견적부서가 `見積計算書（まとめ）`까지 낸 견적파일에 **새 `見積纏め_Sales added` 시트만 맨 왼쪽에 추가**하고, 영업 가산치를 입력하면 시트 수식이 受注価格·Offer를 산출한다. 빈 템플릿 `assets/nemae_template.xlsx`, 생성기 `scripts/build_template_v2.py`. **설계 전체는 `REDESIGN_SPEC.md` 참조.**

> - **"내부 견적서 준비"·"내부 견적서" = 이 스킬.**
> - ⚠️ **기존 시트 절대 수정 금지.** 오직 `見積纏め_Sales added` 새 시트만(맨 왼쪽).

## まとめ ↔ 見積纏め 매핑 (행·열 고정 금지 — 항목명/내용으로 찾기)
| まとめ 항목 | 見積纏め | 규칙 |
|---|---|---|
| 製造原価 (機械/SV분) | §3 **Pure Manf. Cost** D22/D26 | `その他` 비면 여기가 시작점 |
| `その他` | §3 indv.Tax/CIT/others | 차있으면 이미 포함(입력X), 비면 영업 입력 |
| `CONTI (WA)+(EX)+(PS)` | **RC = Risk Conti** | 차있으면 이미 원가포함 → §3에 안 더함 |
| `試験研究費(R&D)+販売間接費(M&S)+一般管理費(G&A)` | **FC = Function Cost** | 차있으면 이미 **総原価** → FC 안 더함 |

## 핵심 모델 (확정)
- **§3 = 열 레이아웃**(원래 양식): `Pure Manf.Cost(C) | indv.Tax(D) | CIT(E) | Local Tax Agent(F) | others(G) | RC(H) | Manf.Cost(I)=SUM(C:H) | FC(J) | Total cost(K)=I+J | EBIT(L) | TotalCost+EBIT(M) | nego(N) | Offer(O) | Remarks(P)`. 행: 22機械·23SV·24予備品·25Total.
  - `PTKorea COMM`(J5): **機械+SV**. `insurance`(J6)·`bond`(J7): **機械만**(機械 others=`(J5+J6+J7)×M`). `CIT`(J12)·`Local Tax Agent`(J13): **SV만**(×M23). SV others=`J5×M23`(COMM만).
  - **SV indivisual Tax**(§3 D23): SV만, **절대금액** = §1 `C16`(kJPY/MM) × Man-Months `C11`. §2-1 `J11='=C16'`. (L×% 아님)
  - FC(J)=`FC%×M`. Manf.Cost(I)=SUM(C:H). Total cost(K)=Manf.Cost+FC.
- **입력셀만 녹색(C6EFCE)**, 나머지 테두리만: §2-1 율·§1 C16/D16·§3 C22/C23/C24(base)·L25(EBIT)·O25(Offer)·§4 MD·FX·案件名.
- §4는 MD 표만(`MAIN ITEM/Proportion/Submit/price/ea` 우측표 **삭제**).
- **SV 売値 H26 = D16(c-md 단가)×D11(SV計MD) 고정** → SV overlay·원가 고정. **機械이 차액 흡수**.
- **비순환 닫힌형** (Excel 반복계산 OFF): `M25(총受注価) = (C22 + K23 + K24 − r機械×(M23+M24)) / (1 − EBIT − r機械)`, r機械=COMM+insurance+bond+FC.
  - M25가 자기참조 안 함 → 라이브 수식인데 순환 없음. `M22(機械受注価)=M25−M23−M24`(잔차), `M23(SV)=D16×D11` 고정.
- **§1 D16(SV단가) 입력 → §5 残業(`C45=D16*1000`…) 과 SV売値(H26) 자동연동.**
- **시작점**: `その他` 비면 製造原価를 Pure Manf Cost(D22/D26)에. (`その他`/`CONTI`/`R&D…` 채워졌으면 각각 이미 포함 → 안 더함.)
- §3 **Remarks 자동입력 없음**(영업이 직접 작성). §2-1에 total(others) 없음(적용범위 달라 무의미).

## 파일명 규칙
- 산출본 = 원본 견적계산서명 + `_Sales added`. 예: `0925S170 見積計算書 Rev.2.xlsx` → `…_Sales added.xlsx`.

## 워크플로
### 1. 입력 수집
- 견적파일 경로(`見積計算書（まとめ）` + `現地ＳＶ費`). **기존 시트 수정 금지.**
- 機械/SV **製造原価**(まとめ에서 항목명으로), EBIT(기본 3%, 案件별), COMM(商社口銭) 율, SV CIT·Local Tax Agent 율, 案件명, 최종 Offer(미지정시 受注価 라운드업).
- SV 단가(기본 220 kJPY/c-md), SV計MD(`現地ＳＶ費` 자동참조; 실패시 `--svdays`).

### 2. 빌드
```
# §3 base는 まとめ 셀 링크 권장(--main-cell/--sv-cell): 값 하드코딩 X, まとめ 바뀌면 자동연동(내부참조).
python <skill>/scripts/nemae.py build "<견적.xlsx>" "<원본명>_Sales added.xlsx" \
  --main-cell <機械製造原価셀 예F36> --sv-cell <SV製造原価셀 예G36> \
  --comm 0.05 --insurance 0.005 --bond 0.005 --sv-indiv-tax 120 --cit 0.10 --lta 0.02 \
  --ebit 0.08 --offer <최종Offer> --name "<案件명>" [--svdays <MD>] [--unit-price 220]
```
기본값: **FC 12%** · insurance 0.5% · bond 0.5% · SV indiv Tax 120k/MM · Local Tax Agent 2% · CIT 10% · COMM 5% · EBIT 3% · 단가 220. (건별 override) `--offer` 미지정시 受注価 라운드업. (まとめ에 R&D+M&S+G&A가 차 있으면 이미 総原価 → `--fc 0`)
자동: 새 시트 맨 왼쪽 추가 → 입력 채움 → `現地ＳＶ費` 자동참조(전각ＳＶ·'移動日含み/実労働日' 헤더 인식) → 외부링크/깨진 정의이름 정리. **반복계산 OFF**(비순환).

### 3. 검증
```
python <skill>/scripts/nemae.py verify "<out.xlsx>"
```
`externalLink 0` · 새시트 `#REF! 0` · 입력셀(C2/D22/D26/G31/J31/D16) 채움 · **H31 비자기참조(iterate off)** · D7=§4計·H26=단가×MD·C45=§5연동 링크 확인.

### 4. 완료 보고
out 경로 + 機械/SV cost·受注価 + Total cost + EBIT·Offer 요약. Excel `Enable Editing`만 하면 값 표시(반복계산 불필요).

## 주의
- ⚠️ 기존 시트 절대 수정 금지. **빌드는 ZIP 주입 방식**(`inject_sheet`): 원본 xlsx ZIP은 그대로 두고 새 시트 part 1개만 끼워넣음(styles는 offset-append, 문자열 inline화, calcChain만 제거→Excel 재생성). → openpyxl 통째 재저장이 도형/이미지/컨트롤을 떨궈 "복구" 경고를 내던 문제 해결, **원본 시트의 drawing·media·customXml 100% 보존.**
- 템플릿 구조 변경은 `scripts/build_template_v2.py` 수정 후 재생성(이후 nemae.py의 셀맵 `C{}` 동기화).
- 기밀자료 — 외부 공유 시 실데이터(원가·마진·고객명) 주의.
