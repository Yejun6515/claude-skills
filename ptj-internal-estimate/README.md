# PTJ 내부견적서 스킬 (ptj-internal-estimate) — v2

Claude Code 스킬. 견적부서 `見積計算書（まとめ）`의 **製造原価**를 받아 새 `見積纏め_Sales added` 시트만 추가하고(기존 시트 절대 수정 안 함), 영업 가산(COMM·insurance·bond·CIT·Local Tax Agent·EBIT)을 채운다. "내부 견적서 준비"·"내부 견적서" = 이 스킬.

## 구성
- `SKILL.md` — 스킬 정의(매핑·모델·워크플로)
- `REDESIGN_SPEC.md` — v2 재설계 스펙(①~⑨, 사용자 확정) ★ 변경 시 먼저 읽기
- `scripts/nemae.py` — 빌더(`build`) / 검증(`verify`)
- `scripts/build_template_v2.py` — 빈 템플릿 생성기(구조 변경 시 이걸 수정 후 재생성)
- `assets/nemae_template.xlsx` — 빈 `見積纏め` v2 템플릿 (`*.v1backup.xlsx`/`*.OLD.xlsx` = 구버전 백업)

## 모델 (요약)
- §3 overlay **행분해**: 機械=COMM/insurance/bond, SV=COMM/CIT/Local Tax Agent, 전부 受注価(L)×%.
- SV 売値 = `D16(단가)×MD` 고정, 機械이 차액 흡수. §5 残業·SV売値는 D16 자동연동.
- **비순환 닫힌형** `H31=(D22+F26−r機械×H26)/(1−EBIT−r機械)` → Excel 반복계산 불필요.
- まとめ `その他`/`CONTI(RC)`/`R&D+M&S+G&A(FC)` 채워졌으면 이미 포함 → §3에 안 더함. `その他` 비면 製造原価를 Pure Manf Cost에.

## 사용
```
python scripts/nemae.py build "<견적.xlsx>" "<원본명>_Sales added.xlsx" \
  --main <機械製造原価> --sv <SV製造原価> \
  --comm 0.05 --insurance 0.005 --bond 0.005 --cit 0.10 --lta 0.02 \
  --ebit 0.08 --offer <최종Offer> --name "<案件명>" [--svdays <MD>] [--unit-price 220]

python scripts/nemae.py verify "<out.xlsx>"
```
- 기본값: insurance 0.5% · bond 0.5% · Local Tax Agent 2% · CIT 10% · COMM 5% · EBIT 3% · 단가 220 (건별 override)
- SV MD는 `現地ＳＶ費` 자동참조(전각ＳＶ·'移動日含み/実労働日' 헤더 인식), 실패시 `--svdays`

## 설치 (다른 PC)
`~/.claude/skills/ptj-internal-estimate/` 에 폴더째.

> ⚠️ 사내 기밀 워크플로. 실제 견적/원가/고객 데이터는 커밋하지 말 것.
</content>
