---
name: china-entertainment-expense
description: 중국(및 해외) 접대비 정산 2종 서류를 한 번에 작성한다 — ①「飲食費（国税要件保存書類）」엑셀(참가자·실시일·가게명·통화/금액/레이트 → 円換算·인당단가·계정코드 자동) ②「Compliance Scorecard (China)」 xls의 이름칸·Remarks·participants 탭(중국측 참석자 mandatory field 전부). 참석자 명단만 주면 나머지를 채우고, 라디오/체크박스는 어디를 눌러야 하는지 계산해 알려준다. 트리거 - "접대비 정산", "접대비 엑셀 만들어줘", "飲食費 국세요건 보존서류", "스코어카드 작성", "China Scorecard", "participants 탭 채워줘", "회식비 정산", 회식 영수증/카드명세가 든 폴더를 주는 경우.
---

# china-entertainment-expense

**접대비(회식) 1건 → 제출서류 2개**를 반자동으로 만든다. 사람이 판단할 것(참석자·인원·금액 기준)만 묻고, 계산·전개·서식은 전부 스크립트가 한다.

산출물
1. `飲食費_<케이스>.xlsx` — 支払伝票에 **백흑 인쇄**해서 첨부하는 국세요건 보존서류
2. `Scorecard_China_<케이스>.xls` — 서명받아 제출하는 컴플라이언스 스코어카드 + `participants` 탭

빈 마스터는 스킬에 번들되어 있다(`assets\meal_master.xlsx`, `assets\scorecard_china_master.xls`). **사용자 원본 파일을 직접 고치지 않는다** — 항상 마스터에서 케이스 사본을 만든다.

## 물어볼 것 (반자동)

한 번에 묻고, 답 안 온 항목만 가정으로 채운 뒤 리포트에서 flag한다.

| 항목 | 비고 |
|---|---|
| **참석자 명단** (회사 / 직위 / 이름) | 제일 중요. PT측 포함 전원 |
| 실시일 · 가게명 | 영수증에서 읽을 수 있으면 안 물어봄 |
| Y-MAP 決裁管理番号 | 없으면 비워두고 flag |
| 금액 기준 | ⓐ 실제 영수증(통화·금액·레이트) ⓑ 사전승인 추정(인당 O엔) |
| 국가 · 도시 | 기본 China / 영수증의 도시 |

## 고정 규칙 (2026-07-29 확정)

- **participants 탭에는 중국 회사 소속만** 넣는다. PTCN·PTJ 등 Primetals 계열과 일본계 회사는 제외. (양식 안내문: "employees / members of Chinese companies / organizations")
- **飲食費 시트의 인당 단가는 PT측 포함 전원**으로 나눈다(같이 먹었으므로). `D57 = COUNTA(E7:E56)`가 자동으로 센다.
- **사전승인 건은 인당 5,000엔 기준**으로 잡고 RMB 환산은 반올림해서 넣는다(예: 5,000 ÷ 24.861 ≒ **201 RMB**). 실제 정산 때 실금액으로 교체.
- participants의 `N/O`(현지통화·인당액)에는 **승인 기준통화(JPY 5,000)**, `P/Q`에는 **RMB 환산액**을 넣는다. 검토자가 현지통화=CNY를 요구하면 N=CNY / O=RMB액 두 칸만 바꾸면 된다.
- **레이트는 카드 이용명세의 「換算レート」**를 쓰고, 그 명세 캡처가 `※Rate証明書` 첨부물이 된다. 円換算額이 실제 인출액과 1~2엔 어긋나는 것은 정상 — 어긋나면 리포트에 적어 사용자가 판단하게 한다.
- PT host = **PTJ**, PT contact = **Kim Yejun**, host 부서 = **Business Development Dep. No2**, Line Manager = **Kurata Kazuyuki** (마스터에 기본값으로 들어 있음).
- **라디오 버튼·체크박스는 클대리가 누르지 않는다.** ActiveX라 값만 바꾸면 인쇄물에 마크가 안 뜬다. 대신 **어디를 눌러야 하는지 계산해서 알려준다**(아래 표).

## 절차

### 1. 소스 읽기
영수증/카드명세(PDF·PNG·.msg)가 있으면 먼저 읽어 **가게명·일자·현지통화 금액·換算レート·엔화 인출액**을 뽑는다. 중국 가게명은 원문(중국어)을 그대로 쓰고, 영문 표기는 備考欄에만 병기한다.

### 2. 케이스 JSON 작성
`assets\case_example.json`을 본떠 scratchpad에 UTF-8로 쓴다. `meal`·`scorecard` 키는 **엑셀 셀 주소**, `"YYYY-MM-DD"` 문자열은 스크립트가 날짜로 변환한다.

### 3. 실행
```
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.claude\skills\china-entertainment-expense\scripts\fill_expense.ps1" `
  -Case "<scratchpad>\case.json" -OutDir "<출력 폴더>" -Force -Preview
```
스크립트는 채운 뒤 **결과값을 되읽어 출력**한다 — 인당단가·계정코드·총점·경고문구(L열). `-Preview`면 `_preview\*.pdf`도 만든다.

### 4. 눈으로 검증
`_preview\meal.pdf` / `scorecard.pdf` / `participants.pdf`를 PNG로 렌더해 **Read 도구로 직접 본다**.
```
python -c "import fitz; d=fitz.open(r'<pdf>'); [p.get_pixmap(dpi=110).save(r'<png %d>'%i) for i,p in enumerate(d)]"
```
확인 포인트: 「入力して下さい」 경고가 남아 있는지, 가게명이 셀에 안 들어가 축소되진 않았는지(길면 원문만 남기고 영문은 備考欄으로), participants 6행 이하 서식이 5행과 같은지.

### 5. 사용자에게 넘길 것
- 눌러야 할 라디오/체크박스 목록(아래 표 기준, 이번 건 값으로)
- 예상 총점과 결재 경로(**16점 이하 = 라인매니저 서명만 / 17점 이상 = 컴플라이언스 오피서 사전 상담**)
- 가정한 항목(성/이름 분리, Mr/Ms, Public Sector 여부 등) flag
- 다음 단계: 飲食費는 **백흑 인쇄** → 支払伝票 첨부, 스코어카드·Y-MAP 인쇄본도 함께 첨부

## 셀 맵 — 飲食費（国税要件保存書類）

시트 1개(`飲食費　国税要件保存書類（白黒印刷で提出）`), 시트 보호 O / 입력칸만 잠금해제.

| 셀 | 항목 | 값 |
|---|---|---|
| I2 | Y-MAP 決裁管理番号 | 텍스트 |
| C7:E56 | 참가자 会社名 / 役職 / 氏名 | B열 번호·D57 인원수 자동 |
| I6 | 実施年月日 | 날짜 |
| I8 | 使用店名 | 짧게(원문). 길면 자동축소돼 인쇄가 안 보임 |
| I10 | 取引 | `適格事業者取引` / `免税事業者取引` / **`外貨取引`** |
| K12 | 타사와 折半? | `YES` / `NO` (YES면 I14·J14·K14, I15·K15) |
| K23·K24 | 適格: 税込합계 · 税区분(10/8/0) | 円貨 지불 시 |
| K32·K33 | 免税: 税込합계 · 税区분 | 등록번호(T~) 없는 영수증 |
| K41·K42·K43 | **外貨: 금액 · 통화(USD/EUR/CNY/VND) · Rate** | 해외 카드결제 시 |
| H50 | 備考欄 (H50:K56) | 출장·상대사·통화·레이트 근거를 여기에 |

자동: `K44 = K41×K43`(円換算額) → `K45 = 円換算額 ÷ D57`(인당단가) → `H44/H45`가 계정 판정
**단가 10,000엔 초과 → `66160010 交際費(社外飲食費1万円超)` / 이하 → `66150010 交際費(社外飲食費1万円以下)`**
L열에 빨간 안내문(「〜を入力して下さい」)이 남아 있으면 **미완성**이다.

## 셀 맵 — China Scorecard

| 셀 | 항목 |
|---|---|
| D6 / D7 | host 이름 / PT 부서 (기본값 있음) |
| D8 / D9 | 상대 회사 / 상대 이름 (여러 명이면 "OOO and N others (see participants tab)") |
| D10 | 제공일자 |
| J17:O20 | **Remarks** — 영문 요약(상황·목적·인원·인당금액·공무원/배우자 없음·영수증 첨부) |
| J25:O27 | 컴플라이언스 오피서 코멘트(해당 시) |
| M29 / D31 | Line Manager / 기증자 서명란 (기본값 있음) |
| F26 | 총점 (= `Calculation!E17`, 자동) |

### 눌러야 하는 컨트롤 (사용자 클릭)

| 위치 | 항목 | 점수 |
|---|---|---|
| B12 / C12 / E12 | Meal / Gift / Meal & Gift | — |
| G13 ☑ | Occasion a) 상담 전후·업무 관련 | 0 |
| G14 ☑ | b) 수주 임박 등 중대 결정 직전 | +10 |
| G16 ☑ | 상대가 공무원·국유기업 | +23 |
| G17 ☑ | 2년 내 같은 상대에게 재차 제공 | +6 |
| G18 ☑ | 배우자·동반자 초대 | +23 |
| D20 / E20 / F20 / G20 ◉ | 인당 금액 ≤¥200 / >200–500 / >500–1000 / >1000 | 0 / 5 / 15 / 23 |
| D22 / E22 / F22 ◉ | host 최고 직급 Senior Mgmt / Mgmt / Employee | −3 / −1 / 0 |
| C24 / D24 / E24 / F24 ◉ | 상대 **최저** 직급 Mgmt.Board / Senior / Mgmt / Employee | −3 / −2 / −1 / 0 |

> 금액 구간은 **RMB 기준**이다. host는 참석한 PT측 중 **가장 높은** 직급, 상대는 초대객 중 **가장 낮은** 직급을 고른다.
> 마스터 기본 선택은 `Meal / Occasion a / >¥200&≤¥500 / host Senior Mgmt / 상대 Mgmt = 총 1점`이다. 이번 건이 이와 같으면 "누를 것 없음"이라고 알려준다.

### participants 탭 (5행부터)

**mandatory**: A 날짜 · B 성 · C 이름 · D Mr/Ms · G 직위 · H 회사 · J Public Sector(Yes/No) · K G&H type(Meal) · L 국가 · M 도시 · N 현지통화 · O 인당액(현지통화) · P `RMB` · Q 인당액(RMB) · R PT Entity(`PTJ`) · S PT Contact(`Kim Yejun`)
**optional**: E 중문 이름 · F 생년월일 · I 중문 회사명

중국인 이름은 **앞 토큰이 성(姓)** 이라고 가정해 B/C로 나누고, 확신 없으면 flag한다(예: `Lei Shi`가 施磊면 성이 Shi). Mr/Ms를 모르면 `Mr`로 넣고 flag.

## 함정 (실측)

- **PS 5.1 COM 캐스팅** — JSON에서 나온 문자열을 `[string]$v`로 캐스팅하거나 함수 반환값으로 넘기면 `Specified cast is not valid`로 실패한다. 반드시 `$v -is [string]` 분기 + `"$v"` 재생성. 숫자는 `[double]$v`. (스크립트에 반영됨)
- **병합셀 ClearContents 불가** — `Range("D8").MergeArea.ClearContents()`로 해야 한다.
- **드라이브 간 이동 금지** — `os.replace`/`Move-Item`은 U:↔C:에서 실패. `Copy-Item`.
- **`fill_expense.ps1`은 UTF-8 BOM으로 저장해야 한다.** BOM이 없으면 PS 5.1이 스크립트 안의 `"飲食費_"` 리터럴을 cp932로 오독해 파일명이 `鬟ｲ鬟溯ｲｻ_...`로 깨진다. 스크립트를 편집했으면 BOM을 다시 확인할 것:
  `python -c "p=r'...fill_expense.ps1'; b=open(p,'rb').read(); open(p,'wb').write(b if b[:3]==b'\xef\xbb\xbf' else b'\xef\xbb\xbf'+b)"`
- 시트가 보호돼 있어도 입력칸은 `Locked=False`라 COM 쓰기가 된다. 잠긴 칸에 쓰면 예외 → 그건 채우면 안 되는 칸이다.
- Excel COM은 `AutomationSecurity=3`(매크로 강제 비활성)으로 연다. .xls의 ActiveX 컨트롤(19개)은 저장해도 보존된다 — 저장 후 `Shapes.Count`로 확인 가능.
- 영수증이 중국어면 가게명 원문을 살린다. 영문 표기는 예: `湖州老土家餐饮有限公司` → `Laotujia Restaurant, Huzhou`.

## 실적

- 2026-07-23 Hengtong/TEX 회식(湖州, 1,323.55 CNY @24.861 = 32,904엔, 8명 → 인당 4,113엔 → 66150010) — 飲食費 + 스코어카드 + participants 4명 작성 완료. 스코어카드는 사전승인 기준 인당 5,000엔(=201 RMB), 총 1점.
