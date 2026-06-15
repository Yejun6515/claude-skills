# -*- coding: utf-8 -*-
"""PTJ 내부견적 見積纏め(영업가산) 빌더.

견적부서가 製造原価까지 낸 견적파일에 見積纏め 시트를 추가하고 영업 가산치를 채운다.
검증된 파이프라인: 시트복사 → 영업입력 → EBIT/Nego 초기값 → 외부링크 제거 → 깨진 정의된이름 삭제.

usage:
  build  <quotation.xlsx> <out.xlsx> --main M --sv S [opts]
  verify <out.xlsx>

새 見積纏め 시트만 추가(기존 시트 불변). 시작점 입력 → 자동 総原価 → 受注価格.
build 옵션:
  --start total|manf  시작점: total=総原価(J列), manf=製造原価(H列)+FC자동→J  [기본 total]
  --main FLOAT     機械 원가 (total=総原価분 / manf=製造原価분, 千円)  [필수]
  --sv   FLOAT     SV 원가  (total=総原価분 / manf=製造原価분, 千円)  [필수]
  --svdays INT     SV 일수, 売値 L24=220×일수(고정)                   [기본 0]
  --name STR       案件명 (B22)
  --date YYYYMMDD  작성일 (P1)   --author STR  작성자 (P2)
  --fc   FLOAT     manf start의 FC(=販管費 R&D+M&S+G&A) 요율 (J14)    [기본 0.12]
  --ebit FLOAT     EBIT (受注価格 = 총원가 / (1-EBIT))               [기본 0.03]
  --nego FLOAT     Nego (Offer = 受注価格 / (1-Nego))                [기본 0.0]
  --spare-cost FLOAT  추천예비품 Total cost(J25) (선택)
"""
import argparse, copy, re, sys, datetime, warnings, os
import openpyxl
from openpyxl.styles import PatternFill, Border
warnings.filterwarnings('ignore')

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_DIR, 'assets', 'nemae_template.xlsx')
EXT = re.compile(r'\[\d+\]')


def copy_sheet(src_ws, tgt_wb, title):
    tgt = tgt_wb.create_sheet(title)
    for k, v in src_ws.column_dimensions.items():
        if v.width is not None:
            tgt.column_dimensions[k].width = v.width
        tgt.column_dimensions[k].hidden = v.hidden
    for k, v in src_ws.row_dimensions.items():
        if v.height is not None:
            tgt.row_dimensions[k].height = v.height
    for row in src_ws.iter_rows():
        for c in row:
            nc = tgt.cell(c.row, c.column, c.value)
            if c.has_style:
                nc.font = copy.copy(c.font)
                nc.fill = copy.copy(c.fill)
                nc.border = copy.copy(c.border)
                nc.alignment = copy.copy(c.alignment)
                nc.number_format = c.number_format
                nc.protection = copy.copy(c.protection)
    for mc in src_ws.merged_cells.ranges:
        tgt.merge_cells(str(mc))
    tgt.sheet_format = copy.copy(src_ws.sheet_format)
    tgt.sheet_properties = copy.copy(src_ws.sheet_properties)
    tgt.freeze_panes = src_ws.freeze_panes
    tgt.sheet_view.showGridLines = src_ws.sheet_view.showGridLines
    return tgt


def strip_external_links(wb, wbv):
    """외부참조 셀을 캐시값으로 치환하고 외부링크 제거."""
    replaced = 0
    for ws in wb.worksheets:
        vsheet = wbv[ws.title] if ws.title in wbv.sheetnames else None
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str) and v.startswith('=') and EXT.search(v):
                    c.value = vsheet[c.coordinate].value if vsheet is not None else None
                    replaced += 1
    n_ext = len(wb._external_links)
    wb._external_links = []
    return replaced, n_ext


def drop_junk_defined_names(wb):
    """#REF!/#N/A/외부참조/배열상수 등 깨진 정의된 이름 삭제."""
    def junk(val):
        if val is None:
            return False
        v = str(val)
        return ('#REF!' in v) or ('#N/A' in v) or v.strip().startswith('{') or ('[' in v and ']' in v)
    removed = 0
    for nm in list(wb.defined_names.keys()):
        if junk(wb.defined_names[nm].value):
            del wb.defined_names[nm]
            removed += 1
    for ws in wb.worksheets:
        try:
            keys = list(ws.defined_names.keys())
        except Exception:
            keys = []
        for nm in keys:
            if junk(ws.defined_names[nm].value):
                del ws.defined_names[nm]
                removed += 1
    return removed


def num(ws, addr, default=0.0):
    v = ws[addr].value
    return float(v) if isinstance(v, (int, float)) else default


def solve_offer(total_cost, ebit, nego):
    """--offer 미지정시 폴백: 受注価格=총원가/(1-EBIT), Offer=受注価格/(1-Nego)."""
    L26 = total_cost / (1 - ebit)
    N26 = L26 / (1 - nego) if (1 - nego) else L26
    return round(N26)


def read_sv_persons(quotation):
    """現地SV費 시트에서 SV 인원별 (이름, 見積MD=AS, 契約MD=AT) 추출.

    見積MD(歴日·移動日含み)=計(C-MD), 契約MD(実労働日)=実働.
    移動=見積MD−契約MD, 休日=0 (사용자 확정 룰). 行/列 번호는 고정하지 않고
    헤더('見積'+'MD' / '契約'+'MD')·항목명으로 문맥에서 찾는다.
    """
    try:
        wb = openpyxl.load_workbook(quotation, data_only=True)
    except Exception:
        return []
    sname = next((s for s in wb.sheetnames if '現地SV' in s or 'SV費' in s), None)
    if not sname:
        return []
    ws = wb[sname]
    col_est = col_con = None
    for row in ws.iter_rows(min_row=1, max_row=6):
        for c in row:
            if isinstance(c.value, str):
                v = c.value
                if col_est is None and '見積' in v and 'MD' in v:
                    col_est = c.column
                if col_con is None and '契約' in v and 'MD' in v:
                    col_con = c.column
    if col_est is None:
        return []
    persons = []
    for r in range(1, ws.max_row + 1):
        nm = ws.cell(r, 1).value
        if isinstance(nm, str) and '合計' in nm:
            break
        est = ws.cell(r, col_est).value
        if isinstance(est, (int, float)) and est > 0:
            con = ws.cell(r, col_con).value if col_con else est
            con = float(con) if isinstance(con, (int, float)) else float(est)
            persons.append((str(nm).strip() if nm else '', float(est), con))
    return persons


def fill_sv_md(ws, persons):
    """SV-MD 카운트 표(rows 31-36, SV A-F) 채우기. 実働=AT·休日=0·移動=AS−AT, 計=SUM 수식.

    G37(合計) → D7('=G37') → D11 → L24=D16×D11=220×MD 로 자동 반영. SV항목명은 익명(SV A,B…).
    """
    from openpyxl.comments import Comment
    for i in range(6):
        r = 31 + i
        if i < len(persons):
            nm, est, con = persons[i]
            ws['D%d' % r] = round(con)               # 実働 (契約MD)
            ws['E%d' % r] = 0                         # 休日
            ws['F%d' % r] = round(est - con)         # 移動 (見積MD−契約MD)
            ws['B%d' % r].comment = Comment(
                '現地SV費: %s (見積MD=%s, 契約MD=%s)' % (nm, round(est), round(con)), 'PTJ-skill')
        else:
            ws['D%d' % r] = None; ws['E%d' % r] = None; ws['F%d' % r] = None
    return sum(round(e) for _, e, _ in persons)      # 計 합계 = 見積MD 합계


def cmd_build(a):
    from openpyxl.comments import Comment
    wb = openpyxl.load_workbook(a.quotation)
    wbv = openpyxl.load_workbook(a.quotation, data_only=True)
    if '見積纏め' in wb.sheetnames:
        del wb['見積纏め']
    src = openpyxl.load_workbook(TEMPLATE)['見積纏め']
    ws = copy_sheet(src, wb, '見積纏め')
    # 위치: 見積計算書（まとめ） 다음
    try:
        anchor = wb.sheetnames.index('見積計算書（まとめ）')
        wb.move_sheet('見積纏め', anchor + 1 - (len(wb.sheetnames) - 1))
    except ValueError:
        wb.move_sheet('見積纏め', -(len(wb.sheetnames) - 1))

    # 헤더
    ws['P1'] = a.date or datetime.date.today().strftime('%Y%m%d')
    if a.author:
        ws['P2'] = a.author
    if a.name:
        ws['B22'] = a.name

    def clear(row, cols):
        for c in cols:
            ws['%s%d' % (c, row)] = None

    # 요율 0 (총원가/제조원가에 이미 반영). manf만 FC(=販管費) 유지.
    for cell in ('J5', 'J6', 'J7', 'J12', 'J13', 'J18'):
        ws[cell] = 0
    fc = a.fc if a.fc is not None else 0.12
    ws['J14'] = fc if a.start == 'manf' else 0
    ws['B23'] = '機械'
    ws['B24'] = 'SV'
    ws['K26'] = a.ebit                            # EBIT 입력 셀; L26='=J26/(1-K26)' 수식이 참조

    if a.start == 'manf':
        # 製造原価 start: H=製造原価 입력 → FC 자동 → J=Total cost(=총원가)
        clear(23, 'CDEFG'); clear(24, 'CDEFG')
        ws['H23'] = a.main; ws['I23'] = '=H23*$J$14'; ws['J23'] = '=H23+I23'
        ws['H24'] = a.sv;   ws['I24'] = '=H24*$J$14'; ws['J24'] = '=H24+I24'
        ws['H23'].comment = Comment('見積計算書（まとめ） 製造原価 (機械분)', 'PTJ-skill')
        ws['H24'].comment = Comment('見積計算書（まとめ） 製造原価 (SV분)', 'PTJ-skill')
        total_cost = (a.main + a.sv) * (1 + fc)
    else:
        # 総原価 start: J=Total cost(=총원가) 직접, 총원가 앞단(C~I) 전부 비움(사용자 룰)
        clear(23, 'CDEFGHI'); clear(24, 'CDEFGHI'); clear(25, 'CDEFGHI')
        ws['J23'] = a.main; ws['J24'] = a.sv
        ws['J23'].comment = Comment('見積計算書（まとめ） 総原価 (機械분)', 'PTJ-skill')
        ws['J24'].comment = Comment('見積計算書（まとめ） 総原価 (SV분)', 'PTJ-skill')
        total_cost = a.main + a.sv

    # 추천예비품(선택): Total cost 직접
    if a.spare_cost is not None:
        clear(25, 'CDEFGHI')
        ws['J25'] = a.spare_cost
        total_cost += a.spare_cost

    # SV-MD 카운트: 現地SV費 참조 → SV A-F·計合計 → D7('=G37') → L24=220×MD 자동
    persons = read_sv_persons(a.quotation)
    sv_md = fill_sv_md(ws, persons)
    if a.svdays is not None:                      # 수동 override (template 기본은 '=G37')
        ws['D7'] = a.svdays
        sv_md = a.svdays

    # Offer price (N26, 녹색 입력). 미지정시 nego로 폴백. L26·機械/SV 분배는 모두 수식.
    N26 = round(a.offer) if a.offer is not None else solve_offer(total_cost, a.ebit, a.nego)
    ws['N26'] = N26
    ws['O22'] = ('기준: %s start / Total cost=%s / EBIT %.1f%% / Offer(N26)=%s / SV %sMD(220×日,差額은機械吸収)'
                 % (a.start, round(total_cost), a.ebit * 100, N26, round(sv_md)))

    # 정리: 외부링크 + 깨진 정의된이름
    rep, next_ = strip_external_links(wb, wbv)
    rmn = drop_junk_defined_names(wb)

    wb.save(a.out)
    print('SAVED:', a.out)
    print('  start=%s 機械=%s SV=%s Total cost=%s' % (a.start, a.main, a.sv, round(total_cost)))
    print('  EBIT(K26)=%.1f%%  Offer(N26)=%s  SV인원=%d  計C-MD=%s' % (a.ebit * 100, N26, len(persons), round(sv_md)))
    print('  외부참조치환=%d 외부링크제거=%d 깨진정의된이름삭제=%d' % (rep, next_, rmn))
    print('  → verify 로 검증하세요.')


def cmd_verify(a):
    import zipfile
    z = zipfile.ZipFile(a.file)
    names = z.namelist()
    ext = [n for n in names if 'externalLink' in n]
    ref_total = 0
    for n in names:
        if 'worksheets/sheet' in n and n.endswith('.xml'):
            ref_total += z.read(n).decode('utf-8', 'ignore').count('#REF!')
    wb = openpyxl.load_workbook(a.file)
    ws = wb['見積纏め'] if '見積纏め' in wb.sheetnames else None
    # 우리가 제어하는 見積纏め 시트의 #REF!만 FAIL 대상
    ref_nemae = 0
    if ws:
        ref_nemae = sum(1 for row in ws.iter_rows() for c in row
                        if isinstance(c.value, str) and '#REF!' in c.value)
    print('=== verify:', a.file, '===')
    print(' [%s] externalLink 파트: %d' % ('OK' if not ext else 'FAIL', len(ext)))
    print(' [%s] 見積纏め 시트 #REF!: %d' % ('OK' if ref_nemae == 0 else 'FAIL', ref_nemae))
    print(' [info] 견적시트 #REF! 합계: %d (견적부서 수식 자체 오류, 본 스킬과 무관)' % ref_total)
    print(' [%s] 見積纏め 시트 존재' % ('OK' if ws else 'FAIL'))
    if ws:
        for a_, lbl in [('B22', '案件명'), ('J23', '機械총원가'), ('J24', 'SV총원가'),
                        ('K26', 'EBIT'), ('N26', 'Offer price')]:
            v = ws[a_].value
            flag = 'OK' if v not in (None, '') else '확인'
            print('   [%s] %s %s = %r' % (flag, a_, lbl, v))
        # 시작점 감지: J列(Total cost)이 숫자면 total, 아니면(H列 입력) manf
        start = 'total' if isinstance(ws['J23'].value, (int, float)) else 'manf'
        mc = num(ws, 'J23'); sc = num(ws, 'J24'); spare = num(ws, 'J25')
        if start == 'manf':                        # J=H×(1+FC) 환산
            J14 = num(ws, 'J14')
            mc = num(ws, 'H23') * (1 + J14); sc = num(ws, 'H24') * (1 + J14)
        total_cost = mc + sc + spare
        # SV-MD (rows 31-36): 実働(D)+休日(E)+移動(F)=計
        md = [(ws['B%d' % r].value, num(ws, 'D%d' % r), num(ws, 'E%d' % r), num(ws, 'F%d' % r))
              for r in range(31, 37) if isinstance(ws['D%d' % r].value, (int, float))]
        tot_md = sum(d + e + f for _, d, e, f in md)
        print('   [%s] start=%s 機械=%s SV=%s Total cost=%s'
              % ('OK' if (mc or sc) else '확인', start, round(mc), round(sc), round(total_cost)))
        print('   [%s] SV-MD %d명 計C-MD=%s (実働%s+休日%s+移動%s)  D7=%r → L24=220×MD'
              % ('OK' if md else '확인', len(md), round(tot_md),
                 round(sum(d for _, d, _, _ in md)), round(sum(e for _, _, e, _ in md)),
                 round(sum(f for _, _, _, f in md)), ws['D7'].value))
        ebit = num(ws, 'K26'); N26 = num(ws, 'N26')
        L26 = total_cost / (1 - ebit) if ebit and (1 - ebit) else 0
        if L26 and N26:
            print('   [info] (Excel재계산예상) 受注価格 L26≈%s · 全体nego≈%.2f%% · 機械Offer=N26-SV(220×%sMD)'
                  % (round(L26), (N26 - L26) / N26 * 100, round(tot_md)))
        print('   [note] L26·L23·N23·K%%·M%% 는 시트 수식 → Excel Enable Editing 후 재계산값 확인')


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('quotation'); b.add_argument('out')
    b.add_argument('--start', choices=['total', 'manf'], default='total',
                   help='시작점: total=総原価(J) / manf=製造原価(H)+FC자동→J')
    b.add_argument('--main', type=float, required=True)
    b.add_argument('--sv', type=float, required=True)
    b.add_argument('--svdays', type=int, default=None,
                   help='SV C-MD 수동 override. 기본은 現地SV費에서 자동(D7=G37)')
    b.add_argument('--offer', type=float, default=None,
                   help='Offer price(N26, 녹색 입력). 미지정시 --nego로 폴백 산출')
    b.add_argument('--name'); b.add_argument('--date'); b.add_argument('--author', default='Kim YJ')
    b.add_argument('--fc', type=float, default=None)
    b.add_argument('--ebit', type=float, default=0.03)
    b.add_argument('--nego', type=float, default=0.0)
    b.add_argument('--spare-cost', type=float, default=None, dest='spare_cost')
    b.set_defaults(func=cmd_build)
    v = sub.add_parser('verify')
    v.add_argument('file')
    v.set_defaults(func=cmd_verify)
    a = p.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()
