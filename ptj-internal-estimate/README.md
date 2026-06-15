# PTJ 내부견적서 스킬 (ptj-internal-estimate)

Claude Code 스킬. 견적부서 `見積計算書（まとめ）`의 **製造原価/総原価**를 받아 새 `見積纏め` 시트만 추가하고(기존 시트는 절대 수정 안 함), 입력값으로부터 자동으로 `총원가 → 受注価格(EBIT 3%)`을 산출한다. "내부 견적서 준비"·"내부 견적서"는 이 스킬을 뜻한다.

## 구성
- `SKILL.md` — 스킬 정의(트리거·매핑·모델·워크플로)
- `scripts/nemae.py` — 빌더(`build`) / 검증(`verify`)
- `assets/nemae_template.xlsx` — 빈 `見積纏め` 템플릿

## 매핑 (見積計算書（まとめ） ↔ §3) — 행·열 고정 금지, 항목명으로 문맥에서 찾기
- Manf. Cost(H) = **製造原価** / FC(I,~12%) = **販管費(R&D+M&S+G&A)** / Total cost(J) = **総原価** / +EBIT 3% → **受注価格**
- `受注価格 = 총원가 ÷ (1−EBIT)`. SV는 **220k×일수 고정**, 機械 = 受注価格 − SV(차액 흡수), **受注価格부터 시작 불가**.

## 사용
```
# 総原価 start (기본): J列에 총원가 직접
python scripts/nemae.py build "<견적.xlsx>" "<원본명>_Sales added.xlsx" \
  --start total --main <機械 総原価> --sv <SV 総原価> --svdays <일수> --name "<案件명>"

# 製造原価 start: H列에 제조원가 → FC 12% 자동 → J=총원가
python scripts/nemae.py build ... --start manf --main <機械 製造原価> --sv <SV 製造原価> --fc 0.12 ...

python scripts/nemae.py verify "<out.xlsx>"
```
- `--main/--sv` 千円 단위 (SV 합산형이면 機械=총액−SV, 별도형이면 그대로)
- 기본 `--ebit 0.03 --nego 0` (Nego는 영업이 별도 가산; 산출본은 `_Sales added` 파일명)

## 핵심 처리
- **기존 시트 불변** — `見積纏め` 새 시트만 추가
- 외부링크 정리(깨진 `[n]`참조→캐시값) + 깨진 정의된이름 삭제 → Excel "복구" 경고 방지 (셀 데이터/구조 불변)

## 설치 (다른 PC)
`~/.claude/skills/ptj-internal-estimate/` 에 폴더째 두면 Claude Code가 자동 인식.

> ⚠️ 사내 기밀 워크플로. 실제 견적/원가/고객 데이터는 이 저장소에 커밋하지 말 것.
