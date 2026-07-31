#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
doc-verify / verify.py  —  숫자 검증 엔진 (결정론)

가장 중요한 건 숫자다. 이 스크립트는 "사람이 다시 더해보면 알 수 있는 것"만 본다.
추측하지 않고, 못 읽은 건 못 읽었다고 말한다.

subcommand
  numbers  <file>                  대상 파일 1개의 내부 산술 검증
  crossref <folder> [--target f]   폴더 전체에서 숫자를 뽑아 값→출처 인덱스(대조 기준값 후보)

옵션 : --json <path> 기계용 JSON / --all 식별자(전화·주소)까지 표시 / --min N 최소 절대값

심각도 : FAIL(계산이 안 맞음·확정 결함) / CHECK(사람이 봐야 함) / INFO(참고) / OK(검산 통과)

실제 견적서는 빈 행·중첩 소계·시트 중간 헤더가 섞인 희소(sparse) 레이아웃이라
"헤더 1개 + 합계 1행" 가정이 통하지 않는다. 그래서
  · 헤더 행을 경계로 블록을 나누고
  · 합계/소계 행마다 위쪽 숫자를 모아 여러 합산 가설(H1~H4)을 세워 맞는 것을 찾는다.
어느 가설과도 안 맞으면 추정하지 않고 FAIL로 올린다.
"""
import sys, os, re, json, glob, warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract import extract, READERS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# --------------------------------------------------------------------------- 라벨 사전
# 합계 라벨은 '포함'이 아니라 '그 단어로 시작'해야 한다.
# ("20% of the total price shall be paid…" 를 합계 행으로 오인하면 안 됨)
TOTAL_KEYS = ["grand total", "sub-total", "sub total", "subtotal", "총합계", "합계", "총계",
              "총액", "소계", "総計", "合計", "小計", "総額", "total", "amount total"]
SUBTOTAL_KEYS = ["sub-total", "sub total", "subtotal", "소계", "小計"]
EXACT_TOTAL_KEYS = ["계", "計", "sum", "합"]   # 짧고 흔해서 완전일치만 인정
LABEL_MAX = 30
TAIL_MAX = 15      # 키워드 뒤 꼬리 허용 길이 — "Total( 1 + 2 )", "Total Price (JPY)"

PERCENT_HINTS = ["%", "％", "率", "rate", "ratio", "percent", "비율"]
QTY_HINTS = ["수량", "数量", "qty", "q'ty", "quantity", "台数", "員数", "ea", "mds", "md", "set"]
PRICE_HINTS = ["단가", "単価", "unit price", "price/ea", "price/md", "u/price", "price/unit"]
AMOUNT_HINTS = ["금액", "金額", "amount", "price(", "price (", "가격", "価格", "price"]
HEADER_HINTS = (QTY_HINTS + PRICE_HINTS + AMOUNT_HINTS +
                ["items", "item", "description", "品名", "名称", "내역", "품목", "no.", "구분"])
CURRENCY_RE = re.compile(r"(?:JPY|USD|EUR|KRW|CNY|RMB|SGD|¥|\$|€|£|₩|円|원)", re.I)

NUM_TOKEN = re.compile(
    r"(?<![\w.])\(?\s*(?:JPY|USD|EUR|KRW|CNY|RMB|¥|\$|€|£|₩)?\s*"
    r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|"
    r"(?<![\w.,])-?\d+(?:\.\d+)?(?![\w.,]*\d)", re.I)


# --------------------------------------------------------------------------- 기초 유틸
def parse_num(s):
    """셀/토큰 문자열 -> float. 숫자로 못 보면 None."""
    if s is None:
        return None
    t = str(s).strip()
    if not t:
        return None
    neg = False
    if t.startswith("(") and t.endswith(")"):
        inner = t[1:-1].strip()
        # (1) (2) 같은 항목 번호를 회계식 음수로 오독하지 않는다 — 2자리 이상만 음수
        if len(re.sub(r"\D", "", inner)) < 2:
            return None
        neg, t = True, inner
    if t[:1] in ("△", "▲"):
        neg, t = True, t[1:].strip()
    t = CURRENCY_RE.sub("", t).strip()
    t = t.replace("%", "").replace("％", "")
    t = t.replace(",", "").replace(" ", "").replace("　", "")
    if t.endswith("-"):
        neg, t = True, t[:-1]
    if not re.fullmatch(r"[-+]?\d*\.?\d+", t):
        return None
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def is_int_like(v):
    return abs(v - round(v)) < 1e-9


def fmt(v):
    if v is None:
        return "-"
    if is_int_like(v):
        return "{:,}".format(int(round(v)))
    return "{:,.4f}".format(v).rstrip("0").rstrip(".")


def matches(text, hints):
    t = (text or "").strip().lower()
    return bool(t) and any(h.lower() in t for h in hints)


def _norm_label(text):
    return re.sub(r"^[\W_]+", "", (text or "").strip())


def is_total_label(text):
    t = _norm_label(text)
    if not t or len(t) > LABEL_MAX:
        return False
    if t.strip(" :：()").lower() in EXACT_TOTAL_KEYS:
        return True
    low = t.lower()
    return any(low.startswith(k.lower()) and len(t) - len(k) <= TAIL_MAX for k in TOTAL_KEYS)


def is_subtotal_label(text):
    t = _norm_label(text)
    if not t or len(t) > LABEL_MAX:
        return False
    low = t.lower()
    return any(low.startswith(k.lower()) and len(t) - len(k) <= TAIL_MAX for k in SUBTOTAL_KEYS)


ITEM_NO_RE = re.compile(r"^[\(\[]?\s*\d+\s*[\)\].]?$")   # "3)", "(1)", "2." 같은 항목번호


def label_of(row):
    """행의 라벨. 항목번호 셀('3)')이 앞에 있어도 진짜 라벨을 집는다."""
    texts = [c.strip() for c in row if c and parse_num(c) is None]
    if not texts:
        return ""
    for t in texts:                       # 합계 라벨이 있으면 그것이 우선
        if is_total_label(t):
            return t
    for t in texts:                       # 항목번호는 라벨로 보지 않는다
        if not ITEM_NO_RE.match(t):
            return t
    return texts[0]


def is_blank_row(row):
    return not any(x for x in row)


def is_header_row(row):
    """열 이름 행인지 — 문자 셀 2개 이상이고 그중 하나가 알려진 열 이름."""
    texts = [c for c in row if c and parse_num(c) is None]
    if len(texts) < 2:
        return False
    return any(matches(t, HEADER_HINTS) for t in texts)


def F(sev, kind, loc, msg, detail=""):
    return {"severity": sev, "kind": kind, "loc": loc, "msg": msg, "detail": detail}


# --------------------------------------------------------------------------- 열 합계 검증
def collect_above(rows, i, c, stop_at_header):
    """합계 행 i 의 c열 위쪽 숫자를 모은다. 빈 행은 건너뛴다.
    반환 [(행번호, 값, 'item'|'subtotal')] — 위에서 아래 순."""
    entries, blanks, j = [], 0, i - 1
    while j >= 0:
        r2 = rows[j]
        if is_blank_row(r2):
            blanks += 1
            if blanks > 8:
                break
            j -= 1
            continue
        blanks = 0
        lab = label_of(r2)
        if is_total_label(lab) and not is_subtotal_label(lab):
            break                       # 이전 최상위 합계에서 정지
        if is_header_row(r2):
            if stop_at_header:
                break
            j -= 1
            continue
        v = parse_num(r2[c]) if c < len(r2) else None
        if v is not None:
            entries.append((j, v, "subtotal" if is_subtotal_label(lab) else "item"))
        j -= 1
    return list(reversed(entries))


def hypotheses(near, wide):
    """합계가 무엇의 합인지 가설 목록. (이름, 합, 항목수)"""
    hs = []
    if near:
        hs.append(("바로 위 블록", sum(v for _, v, _ in near), len(near)))
    items = [v for _, v, k in wide if k == "item"]
    subs = [v for _, v, k in wide if k == "subtotal"]
    if items:
        hs.append(("항목 전체", sum(items), len(items)))
    if subs:
        hs.append(("소계 합", sum(subs), len(subs)))
    if subs:
        # 소계 + (어떤 소계에도 안 잡힌 항목) — 2단 구조의 최상위 합계
        uncovered, run = [], []
        for _, v, k in wide:
            if k == "subtotal":
                run = []
            else:
                run.append(v)
        uncovered = run
        hs.append(("소계 + 미포함 항목", sum(subs) + sum(uncovered), len(subs) + len(uncovered)))
    return hs


def check_column_totals(table):
    out = []
    rows, loc = table["rows"], table["loc"]
    for i, row in enumerate(rows):
        lab = label_of(row)
        if not is_total_label(lab):
            continue
        sub = is_subtotal_label(lab)
        for c, cell in enumerate(row):
            total = parse_num(cell)
            if total is None:
                continue
            if is_percent_col(rows, i, c):
                continue
            # 0.03 · 0.92 같은 비율·계수 칸은 합계가 아니다
            if 0 < abs(total) < 1:
                continue
            near = collect_above(rows, i, c, stop_at_header=True)
            wide = near if sub else collect_above(rows, i, c, stop_at_header=False)
            hs = hypotheses(near, wide)
            hs = [h for h in hs if h[2] >= 2]
            # 항목들이 전부 1 미만이면 비율 블록 — 합계 검산 대상이 아니다
            hs = [h for h in hs if abs(h[1]) >= 1]
            if not hs:
                continue
            where = "%s / %d행 · %s열" % (loc, i + 1, col_letter(c + 1))
            head = "%s %s" % (_norm_label(lab)[:24], fmt(total))
            exact = [h for h in hs if abs(h[1] - total) <= 1e-9]
            if exact:
                h = exact[0]
                out.append(F("OK", "합계", where,
                             "%s = %s (%d개 항목)" % (head, h[0], h[2])))
                continue
            best = min(hs, key=lambda h: abs(h[1] - total))
            diff = total - best[1]
            tol = 0.5 * max(1, best[2])
            if abs(diff) <= tol:
                out.append(F("CHECK", "합계", where,
                             "%s vs %s %s — 차이 %s (반올림 오차 가능)"
                             % (head, best[0], fmt(best[1]), fmt(diff))))
            else:
                tried = " / ".join("%s %s" % (h[0], fmt(h[1])) for h in hs)
                out.append(F("FAIL", "합계", where,
                             "%s 인데 어느 합과도 안 맞음 — 가장 가까운 %s %s (차이 %s)"
                             % (head, best[0], fmt(best[1]), fmt(diff)),
                             "시도한 합산 : " + tried))
    return out


def is_percent_col(rows, i, c):
    """행 i 위쪽에서 가장 가까운 헤더의 c열 이름이 %/율인지."""
    for j in range(i - 1, max(-1, i - 40), -1):
        if is_header_row(rows[j]):
            name = rows[j][c] if c < len(rows[j]) else ""
            return matches(name, PERCENT_HINTS)
    return False


def col_letter(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def col_index(s):
    n = 0
    for ch in s.upper():
        n = n * 26 + (ord(ch) - 64)
    return n


# --------------------------------------------------------------------------- 행 산술 (단가×수량)
def segment_blocks(rows):
    """헤더 행을 경계로 (헤더행, 시작, 끝) 블록 목록."""
    blocks, hdr = [], None
    for i, row in enumerate(rows):
        if is_header_row(row):
            if hdr is not None:
                blocks.append((hdr, hdr + 1, i))
            hdr = i
    if hdr is not None:
        blocks.append((hdr, hdr + 1, len(rows)))
    return blocks


def find_col(rows, h, hints, exclude=()):
    """헤더 h 에서 hints 에 맞는 열. 이미 다른 역할로 잡힌 열은 제외한다.
    ('Price/MD(JPY)' 와 'Price(JPY)' 가 같은 열로 잡히는 것을 막는다)"""
    if h is None or h >= len(rows):
        return None
    for c, name in enumerate(rows[h]):
        if c in exclude or not name:
            continue
        if matches(name, hints):
            return c
    return None


def check_row_arithmetic(table):
    """단가 × 수량 = 금액 을 블록별 헤더 기준으로 행마다 검산."""
    out = []
    rows, loc = table["rows"], table["loc"]
    for h, s, e in segment_blocks(rows):
        cq = find_col(rows, h, QTY_HINTS)
        cp = find_col(rows, h, PRICE_HINTS)
        ca = find_col(rows, h, AMOUNT_HINTS)
        if cq is None or cp is None or ca is None or len({cq, cp, ca}) < 3:
            continue
        for i in range(s, e):
            row = rows[i]
            if max(cq, cp, ca) >= len(row):
                continue
            q, p, a = parse_num(row[cq]), parse_num(row[cp]), parse_num(row[ca])
            if q is None or p is None or a is None:
                continue
            lab = label_of(row)
            if is_total_label(lab):
                continue
            exp = q * p
            diff = a - exp
            where = "%s / %d행" % (loc, i + 1)
            if abs(diff) <= (0.5 if is_int_like(exp) else 0.01):
                out.append(F("OK", "행산술", where,
                             "%s : %s × %s = %s" % (_norm_label(lab)[:24], fmt(p), fmt(q), fmt(a))))
            else:
                out.append(F("FAIL", "행산술", where,
                             "%s : 단가 %s × 수량 %s = %s 이어야 하나 금액이 %s — 차이 %s"
                             % (_norm_label(lab)[:24], fmt(p), fmt(q), fmt(exp), fmt(a), fmt(diff))))
    return out


# --------------------------------------------------------------------------- 백분율
def check_percent_sums(table):
    out = []
    rows, loc = table["rows"], table["loc"]
    for h, s, e in segment_blocks(rows):
        for c, name in enumerate(rows[h]):
            if not (name and matches(name, PERCENT_HINTS)):
                continue
            vals = [parse_num(rows[i][c]) for i in range(s, e)
                    if c < len(rows[i]) and not is_total_label(label_of(rows[i]))]
            vals = [v for v in vals if v is not None]
            if len(vals) < 2:
                continue
            tot = sum(vals)
            where = "%s / %s열" % (loc, name)
            if abs(tot - 100) < 1e-6 or abs(tot - 1) < 1e-9:
                out.append(F("OK", "백분율", where, "%% 합 = %s" % fmt(tot)))
            else:
                out.append(F("CHECK", "백분율", where,
                             "%% 합이 %s (100 아님) — %s" % (fmt(tot), " + ".join(fmt(v) for v in vals)),
                             "의도된 것인지 확인"))
    return out


PCT_TERM = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%\s*(?:of\s+the\s+total|of\s+the\s+contract|of\s+total|의\s*총액|총액의)", re.I)


def check_payment_percent_text(doc):
    """본문 결제조건의 % 가 합쳐서 100 인지 (표가 아니라 문장으로 쓰인 경우)."""
    out = []
    terms = []
    for t in doc["texts"]:
        for m in PCT_TERM.finditer(t["text"]):
            terms.append((float(m.group(1)), t["loc"], t["text"][:120]))
    if len(terms) < 2:
        return out
    tot = sum(v for v, _, _ in terms)
    detail = " + ".join("%s%%(%s)" % (fmt(v), loc) for v, loc, _ in terms)
    if abs(tot - 100) < 1e-6:
        out.append(F("OK", "결제조건", "본문", "결제조건 %% 합 = 100 — %s" % detail))
    elif abs(tot % 100) < 1e-6:
        out.append(F("CHECK", "결제조건", "본문",
                     "결제조건 %% 합이 %s — 기자재/서비스 등 조건이 2벌 이상인지 확인" % fmt(tot), detail))
    else:
        out.append(F("FAIL", "결제조건", "본문",
                     "결제조건 %% 합이 %s (100 아님)" % fmt(tot), detail))
    return out


# --------------------------------------------------------------------------- Excel 전용
SUM_RE = re.compile(r"^=\s*SUM\(\s*([A-Z]{1,3})(\d+)\s*:\s*([A-Z]{1,3})(\d+)\s*\)\s*$", re.I)


def check_excel_formulas(table):
    """합계 셀이 손입력인지 / =SUM(범위) 캐시값이 실제 합과 맞는지."""
    out = []
    rows, loc = table["rows"], table["loc"]
    formulas = table.get("formulas") or {}
    for i, row in enumerate(rows):
        lab = label_of(row)
        if not is_total_label(lab):
            continue
        for c, cell in enumerate(row):
            v = parse_num(cell)
            if v is None or is_percent_col(rows, i, c):
                continue
            key = "%d,%d" % (i + 1, c + 1)
            where = "%s / %s%d" % (loc, col_letter(c + 1), i + 1)
            if key not in formulas:
                out.append(F("CHECK", "수식누락", where,
                             "'%s' 합계에 수식이 없고 %s 이 직접 입력돼 있음"
                             % (_norm_label(lab)[:24], fmt(v)),
                             "항목이 바뀌어도 자동으로 안 따라감 — 손으로 고친 흔적일 수 있음"))
                continue
            m = SUM_RE.match(formulas[key].strip())
            if not m:
                continue
            c1, r1 = col_index(m.group(1)), int(m.group(2))
            c2, r2 = col_index(m.group(3)), int(m.group(4))
            tot = 0.0
            for r in range(min(r1, r2), max(r1, r2) + 1):
                for cc in range(min(c1, c2), max(c1, c2) + 1):
                    if r - 1 < len(rows) and cc - 1 < len(rows[r - 1]):
                        x = parse_num(rows[r - 1][cc - 1])
                        if x is not None:
                            tot += x
            if abs(tot - v) > 0.5:
                out.append(F("FAIL", "수식대조", where,
                             "%s 재계산 %s ≠ 저장된 값 %s — 차이 %s"
                             % (formulas[key], fmt(tot), fmt(v), fmt(v - tot))))
    return out


# --------------------------------------------------------------------------- 표기·오염
SPELLED = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
           "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15,
           "twenty": 20, "thirty": 30, "sixty": 60, "ninety": 90}
SPELLED_RE = re.compile(r"\b(%s)\s+(\(?)(\d+)(\)?)" % "|".join(SPELLED), re.I)


def check_notation(doc):
    """숫자 병기 표기 — 'three 3 years' 같은 괄호 누락·불일치."""
    out, ok, bad = [], 0, 0
    for t in doc["texts"]:
        for m in SPELLED_RE.finditer(t["text"]):
            word, lp, digit, rp = m.group(1), m.group(2), m.group(3), m.group(4)
            if SPELLED.get(word.lower()) != int(digit):
                out.append(F("FAIL", "표기", t["loc"],
                             "글자 '%s' 와 숫자 '%s' 가 다름 — '%s'" % (word, digit, m.group(0)),
                             t["text"][:170]))
            elif lp == "(" and rp == ")":
                ok += 1
            else:
                bad += 1
                out.append(F("CHECK", "표기", t["loc"],
                             "'%s' — 괄호 없음. 문서 표준은 '%s (%s)'" % (m.group(0), word, digit),
                             t["text"][:170]))
    if ok and bad:
        out.append(F("CHECK", "표기", "문서 전체",
                     "숫자 병기 표기 혼재 — 괄호형 %d곳, 비괄호형 %d곳" % (ok, bad)))
    return out


MONTHS = ("january|february|march|april|may|june|july|august|september|october|november|december"
          "|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec")
DATE_CTX = re.compile(r"\b(%s)\b|년|年|月|일자|date|years?\b|期間" % MONTHS, re.I)
YEARISH = re.compile(r"(?<![\d,.])((?:19|20)\d{3,})(?![\d,.])")
NEAR = 25   # 날짜 키워드가 이 글자수 안에 있어야 '날짜 문맥'으로 본다
# 코드·품번·특허번호는 숫자 오염이 아니다
ID_CTX = re.compile(r"(patent|no\.|ref|model|part|serial|code|ｺｰﾄﾞ|コード|코드|品番|型式|規格"
                    r"|ISO|DIN|JIS|ASTM|WBS|予算)", re.I)
TABLE_LOC = re.compile(r"!r\d+|table", re.I)


def is_prose(loc):
    """문장인지 표 셀인지. 붙여넣기 사고는 문장에서 일어나고,
    표 셀의 품번·도번(R10301, 1315C780)은 정상이다."""
    return not TABLE_LOC.search(loc or "")


def check_year_anomaly(doc):
    """날짜 문맥에 연도로 볼 수 없는 숫자 — 편집 중 글자·숫자가 엉킨 흔적.
    원가코드·품번이 '月' 같은 글자와 같은 줄에 있다고 걸리면 안 되므로,
    날짜 키워드가 해당 숫자 '바로 옆'(NEAR자 이내)에 있을 때만 본다."""
    out = []
    for t in doc["texts"]:
        line = t["text"]
        if not is_prose(t["loc"]) or ID_CTX.search(line):
            continue
        for m in YEARISH.finditer(line):
            if 1900 <= int(m.group(1)) <= 2100:
                continue
            near = line[max(0, m.start() - NEAR):m.end() + NEAR]
            if not DATE_CTX.search(near):
                continue
            out.append(F("FAIL", "숫자오염", t["loc"],
                         "날짜 문맥에 연도로 볼 수 없는 숫자 '%s' 가 있음" % m.group(1),
                         line[:180]))
    return out


# 글자에 숫자가 붙었는데 그 뒤에 다시 글자가 오면 식별자(US20250001477A1)이지 오염이 아니다
GLUED = re.compile(r"\d[-/]\d{3,}(?=[A-Za-z가-힣])|(?<=[A-Za-z가-힣])\d{4,}(?![\d,.A-Za-z])")


def check_glued_tokens(doc):
    out = []
    for t in doc["texts"]:
        if not is_prose(t["loc"]) or ID_CTX.search(t["text"]):
            continue
        for m in GLUED.finditer(t["text"]):
            out.append(F("CHECK", "숫자오염", t["loc"],
                         "숫자와 글자가 공백 없이 붙어 있음 '%s'" % m.group(0),
                         t["text"][:180]))
    return out


def check_thousand_sep(doc):
    out, w, o, sw, so = [], 0, 0, [], []
    for t in doc["texts"]:
        for m in re.finditer(r"(?<![\d,.])\d{1,3}(?:,\d{3})+(?![\d,])", t["text"]):
            w += 1
            if len(sw) < 3:
                sw.append("%s (%s)" % (m.group(0), t["loc"]))
        for m in re.finditer(r"(?<![\d,.\-/])\d{5,}(?![\d,.\-/])", t["text"]):
            o += 1
            if len(so) < 3:
                so.append("%s (%s)" % (m.group(0), t["loc"]))
    if w and o:
        out.append(F("INFO", "표기", "문서 전체",
                     "천단위 콤마 표기 혼재 — 콤마 있음 %d곳, 없음 %d곳" % (w, o),
                     "콤마有: %s / 콤마無: %s" % ("; ".join(sw), "; ".join(so))))
    return out


def check_currency_mix(doc):
    out, found = [], {}
    norm = {"¥": "JPY", "円": "JPY", "$": "USD", "€": "EUR", "£": "GBP",
            "₩": "KRW", "원": "KRW", "RMB": "CNY"}
    for t in doc["texts"]:
        for m in CURRENCY_RE.finditer(t["text"]):
            k = m.group(0).upper()
            found.setdefault(norm.get(k, k), []).append(t["loc"])
    if len(found) > 1:
        out.append(F("CHECK", "통화", "문서 전체",
                     "통화 표기가 %d종 섞여 있음 — %s"
                     % (len(found), ", ".join("%s(%d곳)" % (k, len(v)) for k, v in found.items())),
                     "환산 대상인지, 오기인지 확인"))
    return out


def check_revisions(doc):
    out, rev = [], doc.get("revisions") or {}
    if rev.get("tracked_insert") or rev.get("tracked_delete"):
        out.append(F("FAIL", "개정흔적", "문서 전체",
                     "확정되지 않은 변경이력이 남아 있음 — 삽입 %d · 삭제 %d"
                     % (rev["tracked_insert"], rev["tracked_delete"]),
                     "제출 전 '모든 변경 내용 적용' 필요"))
    if rev.get("comments"):
        out.append(F("FAIL", "개정흔적", "문서 전체",
                     "코멘트 %d개가 남아 있음" % rev["comments"], "제출 전 삭제 필요"))
    return out


MARKER_RE = re.compile(r"\{\{[^}]{1,40}\}\}|<<[^>]{1,40}>>|\[TBD\]|\bTBD\b|XXX+|＿＿+|___+", re.I)


def check_markers(doc):
    out = []
    for t in doc["texts"]:
        for m in MARKER_RE.finditer(t["text"]):
            out.append(F("FAIL", "미기입", t["loc"],
                         "채우지 않은 자리표시자 '%s'" % m.group(0), t["text"][:170]))
    return out


# --------------------------------------------------------------------------- runner
def run_numbers(path, sheet=None):
    doc = extract(path)
    if sheet:
        keep = [t for t in doc["tables"] if sheet.lower() in t["loc"].lower()]
        if not keep:
            raise SystemExit("시트/표 '%s' 없음. 있는 것: %s"
                             % (sheet, ", ".join(t["loc"] for t in doc["tables"])))
        doc["tables"] = keep
        doc["texts"] = [t for t in doc["texts"] if sheet.lower() in t["loc"].lower()]
    f = []
    for tb in doc["tables"]:
        f += check_column_totals(tb)
        f += check_row_arithmetic(tb)
        f += check_percent_sums(tb)
        if doc["type"] in ("xlsx", "xlsm"):
            f += check_excel_formulas(tb)
    f += check_payment_percent_text(doc)
    f += check_notation(doc)
    f += check_year_anomaly(doc)
    f += check_glued_tokens(doc)
    f += check_thousand_sep(doc)
    f += check_currency_mix(doc)
    f += check_revisions(doc)
    f += check_markers(doc)
    seen, uniq = set(), []
    for x in f:
        k = (x["severity"], x["kind"], x["loc"], x["msg"])
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    return doc, uniq


# --------------------------------------------------------------------------- crossref
SIG_RE = re.compile(r"^\s*(T|M|F|Tel|Fax|Mobile|Ext\.?|Phone|Cell|내선)\s*[:.．]", re.I)
ADDR_RE = re.compile(r"(chome|machi|-ku|-ro|-gu|-si|-do\b|Korea|Japan|\bJP\b|Hiroshima|Pohang"
                     r"|Gyeongsangbuk|번지|우편|zip)", re.I)
MONEY_RE = re.compile(r"(JPY|USD|EUR|KRW|CNY|RMB|SGD|¥|\$|€|£|₩|円|원|金額|금액|price|amount"
                      r"|合計|합계|総額|총액|単価|단가|見積|견적|cost|원가|百万|million)", re.I)


def classify_number(line, m):
    if SIG_RE.match(line) or ADDR_RE.search(line):
        return "식별자"
    if line[max(0, m.start() - 1):m.start()] in "-/" or line[m.end():m.end() + 1] in "-/":
        return "식별자"
    return "금액" if MONEY_RE.search(line) else "일반"


def read_msg_text(path):
    try:
        import extract_msg
        m = extract_msg.Message(path)
        txt = (m.subject or "") + "\n" + (m.body or "")
        m.close()
        return txt
    except Exception:
        return ""


def _harvest_lines(lines, fname, index, min_abs):
    for ln, line in enumerate(lines, 1):
        line = (line or "").strip()
        if not line:
            continue
        for m in NUM_TOKEN.finditer(line):
            v = parse_num(m.group(0))
            if v is None or abs(v) < min_abs:
                continue
            index.setdefault(round(v, 4), []).append(
                {"file": fname, "loc": "L%d" % ln, "ctx": line[:200],
                 "class": classify_number(line, m)})


def gather_files(folder, scope="folder"):
    """scope='folder' 지정 폴더만 / 'project' 상위 프로젝트 폴더의 형제 폴더까지.
    baseline(이전 rev·원계약)이 형제 폴더에 있는 경우가 많다 — 실제로 P2H NDA가 그랬다."""
    roots = [folder]
    if scope == "project":
        parent = os.path.dirname(os.path.normpath(folder))
        if parent and os.path.isdir(parent):
            roots = [parent]
    files = []
    for root in roots:
        for ext in list(READERS) + [".msg"]:
            files += glob.glob(os.path.join(root, "**", "*" + ext), recursive=True)
    return sorted(set(f for f in files if not os.path.basename(f).startswith("~$")))


def run_crossref(folder, target=None, min_abs=1000, scope="folder"):
    files = gather_files(folder, scope)
    index, errors, scanned = {}, [], []
    for f in files:
        name = os.path.relpath(f, folder if scope == "folder"
                               else os.path.dirname(os.path.normpath(folder)))
        if f.lower().endswith(".msg"):
            _harvest_lines(read_msg_text(f).splitlines(), name, index, min_abs)
            continue
        try:
            doc = extract(f)
        except Exception as e:
            errors.append((name, ("%s: %s" % (type(e).__name__, e))[:120]))
            continue
        chars = sum(len(t["text"]) for t in doc["texts"])
        if doc["type"] == "pdf" and chars < 200:
            # 스캔 PDF — 텍스트가 없다. 숨기지 말고 "눈으로 봐야 한다"고 올린다.
            scanned.append(name)
            continue
        _harvest_lines([t["text"] for t in doc["texts"]], name, index, min_abs)
    res = {"folder": folder, "scope": scope, "files": [os.path.basename(f) for f in files],
           "errors": errors, "scanned": scanned, "index": {}}
    for k in sorted(index, key=lambda x: -abs(x)):
        srcs = index[k]
        classes = [s["class"] for s in srcs]
        kind = "금액" if "금액" in classes else ("일반" if "일반" in classes else "식별자")
        res["index"][fmt(k)] = {"value": k, "class": kind, "n": len(srcs),
                                "files": sorted(set(s["file"] for s in srcs)),
                                "samples": srcs[:6]}
    if target:
        tn = os.path.basename(target)
        res["target"] = {
            "name": tn,
            "only_in_target": [d for d, e in res["index"].items()
                               if e["files"] == [tn]],
            "shared": [d for d, e in res["index"].items()
                       if tn in e["files"] and len(e["files"]) > 1]}
    return res


# --------------------------------------------------------------------------- 출력
LIMIT = 40   # 콘솔에 자세히 찍을 최대 건수 (--json 에는 전부 들어간다)


def print_findings(doc, findings):
    order = {"FAIL": 0, "CHECK": 1, "INFO": 2, "OK": 3}
    findings = sorted(findings, key=lambda f: (order.get(f["severity"], 9), f["kind"]))
    n = {k: sum(1 for f in findings if f["severity"] == k) for k in order}
    print("파일 : %s (%s)" % (doc["path"], doc["type"]))
    print("표 %d개 · 텍스트 %d줄" % (len(doc["tables"]), len(doc["texts"])))
    print("결과 : FAIL %d · CHECK %d · INFO %d · OK %d\n" % (n["FAIL"], n["CHECK"], n["INFO"], n["OK"]))

    kinds = {}
    for f in findings:
        if f["severity"] in ("FAIL", "CHECK"):
            kinds.setdefault((f["severity"], f["kind"]), 0)
            kinds[(f["severity"], f["kind"])] += 1
    if len(findings) - n["OK"] > 12:
        print("--- 유형별 집계 ---")
        for (sev, kind), cnt in sorted(kinds.items(), key=lambda x: (-x[1], x[0])):
            print("  %-5s %-8s %d건" % (sev, kind, cnt))
        print("")

    shown = 0
    for f in findings:
        if f["severity"] == "OK":
            continue
        if shown >= LIMIT:
            print("\n... 그 외 %d건 (전체는 --json 으로)" % (len(findings) - n["OK"] - shown))
            break
        shown += 1
        print("[%-5s] %-6s %s" % (f["severity"], f["kind"], f["loc"]))
        print("        %s" % f["msg"])
        if f["detail"]:
            print("        └ %s" % f["detail"][:200])
    ok = [f for f in findings if f["severity"] == "OK"]
    if ok:
        print("\n--- 검산 통과 %d건 ---" % len(ok))
        for f in ok[:40]:
            print("  OK  %-6s %-28s %s" % (f["kind"], f["loc"], f["msg"]))
        if len(ok) > 40:
            print("  ... %d건 더" % (len(ok) - 40))
    if not findings:
        print("검산할 수 있는 표·숫자 구조를 찾지 못했다. extract.py 로 추출 결과를 먼저 확인할 것.")


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, path = sys.argv[1], sys.argv[2]
    outjson = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    minabs = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 1000
    show_id = "--all" in sys.argv

    if cmd == "numbers":
        sheet = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else None
        doc, findings = run_numbers(path, sheet)
        print_findings(doc, findings)
        if outjson:
            with open(outjson, "w", encoding="utf-8") as fh:
                json.dump({"doc": {"path": doc["path"], "type": doc["type"]},
                           "findings": findings}, fh, ensure_ascii=False, indent=1)
            print("\nJSON: %s" % outjson)

    elif cmd == "crossref":
        target = sys.argv[sys.argv.index("--target") + 1] if "--target" in sys.argv else None
        scope = "project" if "--project" in sys.argv else "folder"
        res = run_crossref(path, target, minabs, scope)
        print("폴더 : %s  (scope=%s)" % (res["folder"], res["scope"]))
        print("파일 %d개 : %s\n" % (len(res["files"]), ", ".join(res["files"])))
        for e in res["errors"]:
            print("  ! 읽기 실패 %s : %s" % e)
        if res["scanned"]:
            print("  ! 스캔 PDF(텍스트 없음) — 숫자 대조 불가, 이미지로 직접 읽어야 함:")
            for s in res["scanned"]:
                print("      %s" % s)
            print("")
        for want in ("금액", "일반", "식별자"):
            if want == "식별자" and not show_id:
                continue
            rows = [(d, e) for d, e in res["index"].items()
                    if e["class"] == want and len(e["files"]) > 1]
            if not rows:
                continue
            print("--- [%s] 2개 이상 파일에 공통으로 나오는 숫자 (대조 기준값 후보) ---" % want)
            for d, e in rows:
                print("  %16s  %s" % (d, " / ".join(e["files"])))
                for s in e["samples"][:2]:
                    print("                    %s: %s" % (s["file"], s["ctx"][:105]))
            print("")
        if not show_id:
            print("(전화·주소·참조번호로 분류된 %d건 숨김 — 보려면 --all)\n"
                  % sum(1 for e in res["index"].values() if e["class"] == "식별자"))
        if res.get("target"):
            t = res["target"]
            solo = [d for d in t["only_in_target"]
                    if show_id or res["index"][d]["class"] != "식별자"]
            print("--- 대상 '%s' 에만 있고 폴더의 다른 자료에는 없는 숫자 ---" % t["name"])
            print("  " + (", ".join(solo[:60]) if solo else "없음"))
        if outjson:
            with open(outjson, "w", encoding="utf-8") as fh:
                json.dump(res, fh, ensure_ascii=False, indent=1)
            print("\nJSON: %s" % outjson)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
