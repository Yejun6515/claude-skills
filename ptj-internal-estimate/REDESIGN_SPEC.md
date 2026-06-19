# 見積纏め_Sales added 재설계 스펙 (사용자 확정 ①~⑨)

> 출처: 0925S170 작업 중 김예준님 구술 정리. 적용 대상 = `assets/nemae_template.xlsx` + `scripts/nemae.py`.
> 핵심: 영업이 §2-1·§3에 가산하는 모델. 행·열 고정 금지(항목명/내용으로 まとめ 참조).

## ① RC = Risk Conti
- = まとめ `CONTI (WA)+(EX)+(PS)` 합 → §3 RC.
- まとめに 値이 있으면 → 이미 製造原価에 포함 → 영업 별도 입력 없음(중복 금지).

## ② FC = Function Cost (출처)
- = まとめ `試験研究費(R&D)+販売間接費(M&S)+一般管理費(G&A)` 합 → §3 FC.
- 채워져 있으면 → 이미 **総原価** 상태.

## ③ FC 계산식
- FC = FC% × `TotalCost+EBIT (w/o nego)` 열(= 受注価, nego 전). (※ 모든 %항목 공통 베이스 = 이 열)

## ④ indv.Tax / CIT / others 매핑
- = まとめ `その他`. 차 있으면 이미 포함(입력 불필요). **비어 있으면 영업이 §3에서 직접 입력.**
- 항목은 추후 늘어날 수 있음.

## ⑤ §2-1 ↔ §3 적용범위 & total(others) 삭제
- `PTKorea COMM`(J5): **機械 + SV 둘 다**.
- `insurance`(J6)·`bond charge`(J7): **機械에만**.
- §2-1 `total(others)`(J8) **삭제**(적용범위 달라 무의미).
- §3 overlay는 **행으로 분해**(열 추가 금지 — §1/§4/§5와 열 그리드 공유). 機械 아래 COMM/insurance/bond, SV 아래 COMM/CIT/Local Tax Agent 소계 행.

## ⑥ SV Local Tax Agent Fee (신규)
- 현지회계사무소 비용. 라벨 **"Local Tax Agent Fee"**(협소시 "Local Tax Agent").
- §2-1 `TAX(CIT)` 바로 밑 행 추가. §3는 SV overlay 행으로 추가.
- **SV에만** 적용. 베이스 = ③의 L열. 스킬 기본값 **2%**(건별 override).

## ⑦ §3 시작점 판정
- まとめ `その他` 비어있음 → 시작점 = **Pure Manf. Cost (C)**: まとめ 製造原価를 C에 넣고 overlay는 영업이 쌓음.
- `その他` 채워짐 → 製造原価/総原価가 시작점.
- `CONTI` 채워짐 → RC 비움. `R&D/M&S/G&A` 채워짐 → FC 안 더함(=総原価).

## ⑧ §3 Remarks 자동입력 제거
- O22 자동 요약 메모 삭제. Remarks 칸은 비워두고 영업이 직접 작성.

## ⑨ §1 SV단가(D16) ↔ §5 残業 연동
- §5는 이미 D16 참조(`C39=D16*1000`, `D39=C39/8`, `C40~44=ROUNDUP(D39×배율,-3)` 배율 1.25/1.5/1.5/1.75/2). L24=D16×MD도 동일.
- 할 일: **D16(SV c-md 단가)을 입력값으로 노출**(기본 220), 빌드 시 §5·L24 수식 **flatten 금지**(D16 참조 유지).

## ★ 비순환(닫힌형) 산출 — 반복계산 OFF
- SV 売값 L24 = D16×MD 고정 → SV overlay·원가 고정.
- 닫힌형: `L26 = (C機械 + J_SV − r機械×L_SV) / (1 − EBIT − r機械)`  (r機械 = COMM+insurance+bond)
  - J_SV = C_SV + r_SV×L_SV (r_SV = COMM+CIT+LocalTaxAgent)
- L26 1발 산출 → L23 = L26−L24−L25 → overlay = L×요율 → J(forward) → 순환참조 0.
- 셀에는 닫힌형 결과를 드라이버로 기입(정적) + 나머지 forward 수식.

## ⑩ 후속 피드백 (v2 빌드 후)
- **색 채움 제거** — 시트는 테두리만(가독성). 생성기에 fill 미적용.
- **SV indivisual Tax 복원** — §2-1·§3. SV에만, **절대금액** = §1 Man-Month단가 C16(kJPY/MM, 기본 120) × Man-Months C11. (옛 `D24=J12*C11`) §2-1 `J8='=C16'`, §3 `E27='=J8*C11'`. 닫힌형엔 상수로 더해져 비순환 유지.

## 스킬 기본값(저장)
- **FC 12%** · insurance 0.5% · bond 0.5% · SV indiv Tax 120k/MM · Local Tax Agent 2% · CIT 10% · COMM 5% (다음 건 디폴트, 건별 override). まとめ R&D+M&S+G&A 차 있으면 --fc 0.

## 검증 케이스: 0925S170 (HSC D2H Model upgrade)
- その他=0 → Pure Manf start. C機械=22,800 / C_SV=12,416. CONTI 포함 → RC 0. R&D/M&S/G&A=0 → FC 0.
- COMM 5%(機械·SV), SV CIT 10% + Local Tax Agent 2%, insurance/bond 0(이 건).
- SV MD=92(計), L24=220×92=20,240.
- 기대: J_SV=15,857 / L26≈43,270 / Offer=43,300 / J26=39,808 / 전체 마진 ≈8.06%.
</content>
