"""Shared pastel design system for the Life Planner workbook."""
import datetime as dt
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.chart import DoughnutChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties

TODAY = dt.date(2026, 11, 13)
YEAR, MONTH = 2026, 11
FONT = "Arial"
INK = "2B2D35"; MUTED = "8A8F9C"; WHITE = "FFFFFF"; BG = "F3F3F6"; INPUT = "2E5AAC"
BOXLINE = "D9DBE2"; SUBHEAD = "FAFAFC"
# fill, border, text, strong (bars / charts)
PAL = {
    "green":  ("DDEFD9", "A9D3A1", "3D6B37", "8CC584"),
    "peach":  ("FBE2D2", "F1B898", "8A4B2A", "F2A57C"),
    "pink":   ("F9DDE7", "EDAAC1", "8A3555", "EA8FB1"),
    "blue":   ("D9E8F6", "9EC3E6", "2F5C85", "7FB1DF"),
    "lav":    ("E7E1F6", "BBB0E3", "4B3F80", "A397DD"),
    "yellow": ("FBF1CC", "EAD58C", "7A6214", "E8C75E"),
    "mint":   ("D7F0EC", "9CD4CB", "2D6A61", "6FC2B5"),
    "grey":   ("ECEDF1", "CFD2DA", "4A4F5C", "A9ADB8"),
}
CHART = [PAL[k][3] for k in ("blue", "peach", "green", "pink", "lav", "yellow", "mint", "grey")]

EUR = '#,##0 €;-#,##0 €;"–"'
EUR2 = '#,##0.00 €;-#,##0.00 €;"–"'
PCT = '0%;-0%;"–"'
PCT1 = '0.0%;-0.0%;"–"'
NUM = '#,##0;-#,##0;"–"'
NUM1 = '0.0;-0.0;"–"'
DATE = "dd/mm/yyyy"
DSHORT = "dd/mm"
GRID = Side(style="thin", color="E8E9EE")
CHECK_RANGES = []  # (sheet, A1 range) -> converted to real checkboxes by Apps Script

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", indent=1)
LEFTW = Alignment(horizontal="left", vertical="center", indent=1, wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center", indent=1)


def fill(c):
    return PatternFill("solid", fgColor=c)


def font(size=9, bold=False, color=INK, italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def side(col):
    return Side(style="thin", color=PAL[col][1])


def R(sheet, rng):
    return f"'{sheet}'!{rng}"


def bar(p, n=12):
    """Text progress bar that survives Google Sheets import (no data bars there)."""
    v = f"MIN(1,MAX(0,N({p})))"
    return f'=IFERROR(REPT("█",ROUND({v}*{n},0)),"")'


def done(ref):
    return f'OR({ref}="✓",{ref}=TRUE)'


def count_done(rng):
    return f'(COUNTIF({rng},"✓")+COUNTIF({rng},TRUE))'


def setup(ws, title, sub, last_col, max_row, widths=None, default_w=11, tab="grey"):
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    ws.sheet_properties.tabColor = PAL[tab][3]
    ws.column_dimensions["A"].width = 2.5
    for c in range(2, last_col + 2):
        ws.column_dimensions[CL(c)].width = default_w
    for k, v in (widths or {}).items():
        ws.column_dimensions[k].width = v
    for r in range(1, max_row + 1):
        for c in range(1, last_col + 2):
            ws.cell(r, c).fill = fill(BG)
    ws.row_dimensions[1].height = 12
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 18
    ws.row_dimensions[4].height = 10
    ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=last_col)
    t = ws.cell(2, 2, title.upper())
    t.font = font(18, True, INK); t.alignment = CENTER
    s = Side(style="thin", color=BOXLINE)
    for c in range(2, last_col + 1):
        x = ws.cell(2, c); x.fill = fill(WHITE)
        x.border = Border(top=s, bottom=s, left=s if c == 2 else None, right=s if c == last_col else None)
    ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=last_col)
    u = ws.cell(3, 2, sub); u.font = font(9, False, MUTED, True); u.alignment = CENTER
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0


def card(ws, r, c, w, h, title, col, size=10):
    f, b, t, _ = PAL[col]
    sd = side(col)
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + w - 1)
    hc = ws.cell(r, c, title.upper()); hc.font = font(size, True, t); hc.alignment = CENTER
    for j in range(c, c + w):
        x = ws.cell(r, j); x.fill = fill(f)
        x.border = Border(top=sd, bottom=sd, left=sd if j == c else None, right=sd if j == c + w - 1 else None)
    for i in range(r + 1, r + h):
        for j in range(c, c + w):
            x = ws.cell(i, j); x.fill = fill(WHITE)
            x.border = Border(left=sd if j == c else None, right=sd if j == c + w - 1 else None,
                              bottom=sd if i == r + h - 1 else None)
    ws.row_dimensions[r].height = 24


def subcard(ws, r, c, w, title, col):
    """Small pastel band inside a card (like 'BUDGET' / 'FITNESS' sub-headers)."""
    f, b, t, _ = PAL[col]
    sd = side(col)
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + w - 1)
    x = ws.cell(r, c, title.upper()); x.font = font(8, True, t); x.alignment = CENTER
    for j in range(c, c + w):
        y = ws.cell(r, j); y.fill = fill(f)
        y.border = Border(top=sd, bottom=sd, left=sd if j == c else None, right=sd if j == c + w - 1 else None)
    ws.row_dimensions[r].height = 18


def _keep(x, bottom=None):
    b = x.border
    keep_bottom = b.bottom if (b.bottom is not None and b.bottom.style) else bottom
    x.border = Border(left=b.left, right=b.right, top=b.top, bottom=keep_bottom)


def put(ws, r, c, v, fmt=None, inp=False, bold=False, color=None, size=9, align=None, bg=None, line=True):
    from openpyxl.cell.cell import MergedCell
    x = ws.cell(r, c)
    if isinstance(x, MergedCell):
        if bg: x.fill = fill(bg)
        if line: _keep(x, GRID)
        return x
    x.value = v
    x.font = font(size, bold, color or (INPUT if inp else INK))
    if fmt: x.number_format = fmt
    if bg: x.fill = fill(bg)
    if align is None:
        align = LEFT if fmt is None else (CENTER if fmt in (DATE, DSHORT, "mm/yyyy", "0", "hh:mm") else RIGHT)
    x.alignment = align
    if line: _keep(x, GRID)
    return x


def th(ws, r, c, labels, col, size=8):
    sd = side(col)
    for i, l in enumerate(labels):
        x = ws.cell(r, c + i, l.upper() if l else l)
        x.font = font(size, True, PAL[col][2]); x.alignment = CENTER; x.fill = fill(SUBHEAD)
        b = x.border
        x.border = Border(left=b.left, right=b.right, top=b.top, bottom=sd)
    ws.row_dimensions[r].height = 26


def kpi(ws, r, c, w, label, val, fmt=None, color=INK, big=15, col=None):
    s = Side(style="thin", color=PAL[col][1] if col else BOXLINE)
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + w - 1)
    ws.merge_cells(start_row=r + 1, start_column=c, end_row=r + 1, end_column=c + w - 1)
    a = ws.cell(r, c, label.upper()); a.font = font(7.5, True, MUTED); a.alignment = CENTER
    b = ws.cell(r + 1, c, val); b.font = font(big, True, color); b.alignment = CENTER
    if fmt: b.number_format = fmt
    for i in (r, r + 1):
        for j in range(c, c + w):
            x = ws.cell(i, j)
            x.fill = fill(PAL[col][0] if (col and i == r) else WHITE)
            x.border = Border(top=s if i == r else None, bottom=s if i == r + 1 else None,
                              left=s if j == c else None, right=s if j == c + w - 1 else None)
    ws.row_dimensions[r + 1].height = 30


def barcell(ws, r, c, pref, col, n=12, merge=1):
    x = put(ws, r, c, bar(pref, n), color=PAL[col][3], size=8, align=Alignment(horizontal="left", vertical="center"))
    if merge > 1:
        for j in range(c + 1, c + merge):
            _keep(ws.cell(r, j), GRID)
        ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + merge - 1)
    return x


def dv_list(ws, src, rng, strict=False):
    d = DataValidation(type="list", formula1=src, allow_blank=True, showErrorMessage=strict)
    ws.add_data_validation(d); d.add(rng)
    return d


def checks(ws, rng, col="green"):
    dv_list(ws, '"✓"', rng)
    first = rng.split(":")[0]
    ws.conditional_formatting.add(rng, FormulaRule(formula=[done(first)], fill=fill(PAL[col][0]),
                                                   font=Font(name=FONT, color=PAL[col][2], bold=True)))
    CHECK_RANGES.append((ws.title, rng))


def link(ws, r, c, w, text, target, col):
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + w - 1)
    x = ws.cell(r, c, text); x.hyperlink = f"#'{target}'!A1"
    x.font = Font(name=FONT, size=9, bold=True, color=PAL[col][2], underline="single")
    x.alignment = CENTER
    s = side(col)
    for j in range(c, c + w):
        y = ws.cell(r, j); y.fill = fill(PAL[col][0])
        y.border = Border(top=s, bottom=s, left=s if j == c else None, right=s if j == c + w - 1 else None)
    ws.row_dimensions[r].height = 22


def note(ws, r, c, text, w=None):
    x = ws.cell(r, c, text); x.font = font(8, False, MUTED, True)
    x.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    if w:
        ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + w - 1)


# ---------------------------------------------------------------- charts
def _grid(ch):
    try:
        ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="ECECF0"))
    except AttributeError:
        pass
    ch.y_axis.delete = False; ch.x_axis.delete = False


def color_series(ch, colors, line=False):
    for s, c in zip(ch.series, colors):
        if line:
            s.graphicalProperties.line.solidFill = c; s.graphicalProperties.line.width = 24000; s.smooth = False
        else:
            s.graphicalProperties.solidFill = c; s.graphicalProperties.line.solidFill = c


def color_points(series, colors):
    for i, c in enumerate(colors):
        pt = DataPoint(idx=i); pt.graphicalProperties.solidFill = c
        pt.graphicalProperties.line.solidFill = WHITE
        series.dPt.append(pt)


def finish(ch, w, h, title=None, legend="b"):
    ch.width, ch.height = w, h
    ch.title = title
    if legend is None:
        ch.legend = None
    else:
        ch.legend.position = legend
    if hasattr(ch, "y_axis"):
        _grid(ch)
    return ch


def donut(ws, anchor, data_ref, cats_ref, colors, w=5.2, h=4.6, title=None, labels=False):
    d = DoughnutChart(); d.holeSize = 62
    d.add_data(data_ref, titles_from_data=False)
    d.set_categories(cats_ref)
    color_points(d.series[0], colors)
    if labels:
        from openpyxl.chart.label import DataLabelList
        dl = DataLabelList(); dl.showPercent = True
        dl.showVal = dl.showCatName = dl.showSerName = dl.showLegendKey = False
        d.dataLabels = dl
    finish(d, w, h, title, legend=None)
    ws.add_chart(d, anchor)
    return d


def pie_labels():
    from openpyxl.chart.label import DataLabelList
    dl = DataLabelList(); dl.showPercent = True
    dl.showVal = dl.showSerName = dl.showLegendKey = False; dl.showCatName = False
    return dl
