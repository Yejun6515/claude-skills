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


def solve_price(total_cost, ebit, nego):
    """受注価格 = Total cost(총원가) ÷ (1−EBIT);  Offer = 受注価格 ÷ (1−Nego).

    SV 売値는 L24=220×일수로 고정(시트 수식), 機械 = 受注価格 − SV(L23=L26−L24)로
    차액을 흡수한다. 개별 마진은 꼬여도 전체 EBIT는 위 식대로 유지된다.
    """
    L26 = total_cost / (1 - ebit)
    N26 = L26 / (1 - nego) if (1 - nego) else L26
    return round(L26), round(N26)


def cmd_build(a):
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

    from openpyxl.comments import Comment

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

    if a.start == 'manf':
        # 製造原価 start: H=製造原価 입력 → FC 자동 → J=Total cost(=총원가)
        clear(23, 'CDEFG'); clear(24, 'CDEFG')
        ws['H23'] = a.main; ws['I23'] = '=H23*$J$14'; ws['J23'] = '=H23+I23'
        ws['H24'] = a.sv;   ws['I24'] = '=H24*$J$14'; ws['J24'] = '=H24+I24'
        ws['H23'].comment = Comment('見積計算書（まとめ） 製造原価 (機械분; 항목명으로 문맥에서 찾기)', 'PTJ-skill')
        ws['H24'].comment = Comment('見積計算書（まとめ） 製造原価 (SV분; 항목명으로 문맥에서 찾기)', 'PTJ-skill')
        total_cost = (a.main + a.sv) * (1 + fc)
    else:
        # 総原価 start: J=Total cost(=총원가) 직접, 앞단 비움
        clear(23, 'CDEFGHI'); clear(24, 'CDEFGHI')
        ws['J23'] = a.main; ws['J24'] = a.sv
        ws['J23'].comment = Comment('見積計算書（まとめ） 総原価 (機械분; 항목명으로 문맥에서 찾기)', 'PTJ-skill')
        ws['J24'].comment = Comment('見積計算書（まとめ） 総原価 (SV분; 항목명으로 문맥에서 찾기)', 'PTJ-skill')
        total_cost = a.main + a.sv

    ws['D7'] = 0
    ws['D8'] = a.svdays
    # 추천예비품(선택): Total cost 직접
    if a.spare_cost is not None:
        clear(25, 'CDEFGHI')
        ws['J25'] = a.spare_cost
        total_cost += a.spare_cost
    if a.spare_l25 is not None:
        ws['L25'] = a.spare_l25
    if a.spare_n25 is not None:
        ws['N25'] = a.spare_n25

    # 受注価格 = 총원가 ÷ (1−EBIT);  Offer ÷ (1−Nego). SV 売値 220×일수 고정·機械 흡수.
    L26, N26 = solve_price(total_cost, a.ebit, a.nego)
    ws['L26'] = L26
    ws['N26'] = N26
    ws['O22'] = ('기준: %s start / Total cost=%s / EBIT %.1f%% / Nego %.1f%% / SV=220×日(差額은 機械吸収)'
                 % (a.start, round(total_cost), a.ebit * 100, a.nego * 100))

    # 정리: 외부링크 + 깨진 정의된이름
    rep, next_ = strip_external_links(wb, wbv)
    rmn = drop_junk_defined_names(wb)

    wb.save(a.out)
    print('SAVED:', a.out)
    print('  start=%s 機械=%s SV=%s Total cost=%s SVdays=%s' % (a.start, a.main, a.sv, round(total_cost), a.svdays))
    print('  L26(受注価格, EBIT %.1f%%)=%s  N26(Offer, Nego %.1f%%)=%s' % (a.ebit * 100, L26, a.nego * 100, N26))
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
        for a_ in ['B22', 'L26', 'N26', 'D8']:
            v = ws[a_].value
            flag = 'OK' if v not in (None, '') else '확인'
            print('   [%s] %s = %r' % (flag, a_, v))
        # 시작점 감지: J列(Total cost)이 숫자면 total, 아니면(H列 입력) manf
        J14 = num(ws, 'J14')

        def cost(hc, jc):
            jv = ws[jc].value
            if isinstance(jv, (int, float)):
                return float(jv)               # total start: J 직접
            hv = ws[hc].value
            return hv * (1 + J14) if isinstance(hv, (int, float)) else 0.0  # manf: J=H×(1+FC)

        start = 'total' if isinstance(ws['J23'].value, (int, float)) else 'manf'
        mc = cost('H23', 'J23'); sc = cost('H24', 'J24'); spare = num(ws, 'J25')
        total_cost = mc + sc + spare
        L26 = num(ws, 'L26'); N26 = num(ws, 'N26')
        L24 = num(ws, 'D16', 220.0) * (num(ws, 'D7') + num(ws, 'D8'))   # SV 売値 = 220×일수
        flag = 'OK' if (mc or sc) else '확인'
        print('   [%s] start=%s 機械=%s SV=%s Total cost=%s  SV売値(220×日)=%s'
              % (flag, start, round(mc), round(sc), round(total_cost), round(L24)))
        if L26:
            print('   [info] 재계산 EBIT%% = %.2f%%  Nego%% = %.2f%%  機械(=受注価格-SV)=%s'
                  % ((L26 - total_cost) / L26 * 100,
                     (N26 - L26) / N26 * 100 if N26 else 0,
                     round(L26 - L24)))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('quotation'); b.add_argument('out')
    b.add_argument('--start', choices=['total', 'manf'], default='total',
                   help='시작점: total=総原価(J) / manf=製造原価(H)+FC자동→J')
    b.add_argument('--main', type=float, required=True)
    b.add_argument('--sv', type=float, required=True)
    b.add_argument('--svdays', type=int, default=0)
    b.add_argument('--name'); b.add_argument('--date'); b.add_argument('--author', default='Kim YJ')
    b.add_argument('--fc', type=float, default=None)
    b.add_argument('--ebit', type=float, default=0.03)
    b.add_argument('--nego', type=float, default=0.0)
    b.add_argument('--spare-cost', type=float, default=None, dest='spare_cost')
    b.add_argument('--spare-l25', type=float, default=None, dest='spare_l25')
    b.add_argument('--spare-n25', type=float, default=None, dest='spare_n25')
    b.set_defaults(func=cmd_build)
    v = sub.add_parser('verify')
    v.add_argument('file')
    v.set_defaults(func=cmd_verify)
    a = p.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()
