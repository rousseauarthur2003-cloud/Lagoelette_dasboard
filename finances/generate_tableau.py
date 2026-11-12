import random, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, DataBarRule, FormulaRule
from openpyxl.chart import BarChart, PieChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.comments import Comment

OUT = "/home/user/Lagoelette_dasboard/finances/Tableau_Finances_Perso.xlsx"
F = "Arial"
NAVY = "0F172A"; ACCENT = "6366F1"; LIGHT = "EEF2FF"; INPUT = "FEF9C3"; WHITE = "FFFFFF"
GREEN = "059669"; RED = "E11D48"; AMBER = "F59E0B"; SKY = "0EA5E9"; SLATE = "64748B"
PAGE = "F1F5F9"; HEAD = "1E293B"; INK = "1E293B"; BLUE_IN = "1D4ED8"
EUR = '#,##0 €;-#,##0 €;"–"'
EUR2 = '#,##0.00 €;-#,##0.00 €;"–"'
PCT = '0.0%;-0.0%;"–"'
thin = Side(style="thin", color="E2E8F0")
BOX = Border(bottom=thin)
N = 2000  # last journal row
SHEET_COLOR = {}

def font(**k):
    k.setdefault("name", F); return Font(**k)

def title(ws, text, sub, last_col="P", color=NAVY):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 24
    ws.row_dimensions[4].height = 14
    for r in (2, 3):
        for c in range(2, ord(last_col) - 63):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=color)
    ws["B2"] = text; ws["B2"].font = font(size=22, bold=True, color=WHITE)
    ws["B2"].alignment = Alignment(vertical="center", indent=1)
    ws["B3"] = sub; ws["B3"].font = font(size=10, color="CBD5E1")
    ws["B3"].alignment = Alignment(vertical="top", indent=1)
    SHEET_COLOR[ws.title] = color

def header(ws, row, col, labels, fill=HEAD):
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=l)
        c.font = font(bold=True, color=WHITE, size=10)
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = Border()
    ws.row_dimensions[row].height = 32

def section(ws, ref, text, color=ACCENT):
    ws[ref] = text; ws[ref].font = font(size=14, bold=True, color=INK)
    ws[ref].border = Border(bottom=Side(style="medium", color=color))

def cell(ws, ref, value, fmt=None, inp=False, bold=False, color=None, size=10):
    c = ws[ref]; c.value = value
    c.font = font(bold=bold, size=size, color=color or (BLUE_IN if inp else INK))
    c.fill = PatternFill("solid", fgColor=INPUT if inp else WHITE)
    if fmt: c.number_format = fmt
    c.border = BOX
    c.alignment = Alignment(vertical="center")
    return c

def pie_labels():
    dl = DataLabelList(); dl.showPercent = True
    dl.showVal = dl.showCatName = dl.showSerName = dl.showLegendKey = False
    return dl

def color_points(series, colors):
    from openpyxl.chart.series import DataPoint
    for i, colr in enumerate(colors):
        pt = DataPoint(idx=i); pt.graphicalProperties.solidFill = colr
        pt.graphicalProperties.line.solidFill = WHITE
        series.dPt.append(pt)

def soften(chart):
    from openpyxl.chart.shapes import GraphicalProperties
    from openpyxl.drawing.line import LineProperties
    chart.legend.position = "b"
    if chart.y_axis.majorGridlines is not None:
        chart.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="E2E8F0"))
    chart.x_axis.delete = False; chart.y_axis.delete = False

wb = Workbook()
dash = wb.active; dash.title = "Dashboard"
tx = wb.create_sheet("Transactions")
cr = wb.create_sheet("Crédits")
pl = wb.create_sheet("Placements")
pa = wb.create_sheet("Paramètres")
guide = wb.create_sheet("Mode d'emploi")
for ws, col in [(dash, NAVY), (tx, ACCENT), (cr, RED), (pl, GREEN), (pa, SLATE), (guide, AMBER)]:
    ws.sheet_properties.tabColor = col

# ---------------------------------------------------------------- Crédits (inputs needed by Paramètres)
loans = [  # name, capital, rate, months, start
    ("Crédit auto", 12000, 0.049, 60, dt.date(2025, 3, 1)),
    ("Prêt étudiant", 8000, 0.012, 72, dt.date(2024, 9, 1)),
]
places = [  # name, type, solde initial, valeur actuelle, rendement, versement mensuel, horizon
    ("Livret A", "Livret", 4500, 6250, 0.024, 150, 10),
    ("PEA", "Actions / ETF", 3000, 5600, 0.07, 200, 20),
    ("Assurance-vie", "Assurance-vie", 2000, 2380, 0.035, 50, 15),
    ("Crypto", "Crypto", 500, 740, 0.10, 0, 5),
]

# ---------------------------------------------------------------- Paramètres
title(pa, "⚙️  Paramètres", "Catégories, types et budgets mensuels — les cases jaunes sont modifiables", "H", "334155")
pa["B5"] = "Année suivie"; pa["B5"].font = font(bold=True)
cell(pa, "C5", 2026, "0", inp=True)
pa["C5"].comment = Comment("Le Dashboard filtre les transactions sur cette année.", "Finances")
header(pa, 7, 2, ["Catégorie", "Type", "Budget mensuel (€)"])
TYPES = ["Revenu", "Loyer & charges", "Dépense courante", "Achat unitaire", "Remboursement crédit", "Placement"]
cats = [
    ("Salaire", "Revenu", None), ("Prime / bonus", "Revenu", None), ("Autre revenu", "Revenu", None),
    ("Loyer", "Loyer & charges", 750), ("Électricité / gaz", "Loyer & charges", 70),
    ("Internet / mobile", "Loyer & charges", 35), ("Assurance habitation", "Loyer & charges", 15),
    ("Courses", "Dépense courante", 350), ("Transport", "Dépense courante", 70),
    ("Restaurants / sorties", "Dépense courante", 120), ("Loisirs", "Dépense courante", 80),
    ("Abonnements", "Dépense courante", 30), ("Santé", "Dépense courante", 30),
    ("Shopping", "Dépense courante", 80), ("Divers", "Dépense courante", 40),
    ("Électronique", "Achat unitaire", None), ("Mobilier / maison", "Achat unitaire", None),
    ("Vêtements (gros achat)", "Achat unitaire", None), ("Voyage", "Achat unitaire", None),
    ("Autre achat", "Achat unitaire", None),
]
r = 8
CAT_ROWS = {}
for name, typ, bud in cats:
    cell(pa, f"B{r}", name, inp=True); cell(pa, f"C{r}", typ, inp=True)
    cell(pa, f"D{r}", bud, EUR, inp=True); CAT_ROWS[name] = r; r += 1
# loans & placements: names pulled from their sheets (green = cross-sheet link)
LOAN_ROWS = list(range(6, 12))   # Crédits rows 6..11
PL_ROWS = list(range(6, 12))     # Placements rows 6..11
for lr in LOAN_ROWS:
    c = cell(pa, f"B{r}", f'=IF(Crédits!B{lr}="","",Crédits!B{lr})', color="008000")
    cell(pa, f"C{r}", f'=IF(B{r}="","","Remboursement crédit")')
    cell(pa, f"D{r}", f'=IF(B{r}="","",Crédits!G{lr})', EUR); r += 1
for prr in PL_ROWS:
    cell(pa, f"B{r}", f'=IF(Placements!B{prr}="","",Placements!B{prr})', color="008000")
    cell(pa, f"C{r}", f'=IF(B{r}="","","Placement")')
    cell(pa, f"D{r}", f'=IF(B{r}="","",Placements!J{prr})', EUR); r += 1
for _ in range(10):  # spare rows for user categories
    cell(pa, f"B{r}", None, inp=True); cell(pa, f"C{r}", None, inp=True); cell(pa, f"D{r}", None, EUR, inp=True); r += 1
CAT_LAST = r - 1
pa[f"B{r+1}"] = "Les catégories crédits / placements viennent automatiquement des onglets Crédits et Placements. Lignes vides en bas : ajoute tes propres catégories."
pa[f"B{r+1}"].font = font(size=9, italic=True, color=SLATE)
header(pa, 7, 6, ["Types (fixes)"])
for i, t in enumerate(TYPES):
    cell(pa, f"F{8+i}", t)
header(pa, 7, 8, ["Moyens de paiement"])
PAY = ["Carte bancaire", "Virement", "Prélèvement", "Espèces", "Chèque"]
for i, p in enumerate(PAY):
    cell(pa, f"H{8+i}", p, inp=True)
for col, w in zip("BCDEFGH", [28, 22, 18, 3, 22, 3, 20]):
    pa.column_dimensions[col].width = w
dv = DataValidation(type="list", formula1="=$F$8:$F$13", allow_blank=True)
pa.add_data_validation(dv); dv.add(f"C8:C{CAT_LAST}")
CATS = f"Paramètres!$B$8:$B${CAT_LAST}"; CTYPES = f"Paramètres!$C$8:$C${CAT_LAST}"; CBUD = f"Paramètres!$D$8:$D${CAT_LAST}"

# ---------------------------------------------------------------- Transactions
title(tx, "🧾  Journal des transactions", "Une ligne = une opération. Remplis Date, Catégorie, Description, Montant, Paiement — Type / Mois / Année se calculent seuls.", "H", "3730A3")
header(tx, 4, 1, ["Date", "Catégorie", "Description", "Montant (€)", "Moyen de paiement", "Type (auto)", "Mois (auto)", "Année (auto)"])
for col, w in zip("ABCDEFGH", [13, 26, 34, 14, 18, 22, 11, 11]):
    tx.column_dimensions[col].width = w
tx.freeze_panes = "A5"
tx.auto_filter.ref = f"A4:H{N}"

random.seed(7)
rows = []
for m in range(1, 12):
    d = lambda day: dt.date(2026, m, day)
    rows += [
        (d(1), "Salaire", "Salaire net", 2450, "Virement"),
        (d(3), "Loyer", "Loyer appartement", 750, "Prélèvement"),
        (d(5), "Électricité / gaz", "EDF", round(random.uniform(45, 95)), "Prélèvement"),
        (d(6), "Internet / mobile", "Box + forfait", 34.98, "Prélèvement"),
        (d(6), "Assurance habitation", "Assurance", 14.5, "Prélèvement"),
        (d(5), "Crédit auto", "Mensualité crédit auto", 225.9, "Prélèvement"),
        (d(10), "Prêt étudiant", "Mensualité prêt étudiant", 115.4, "Prélèvement"),
        (d(2), "Livret A", "Virement épargne", 150, "Virement"),
        (d(2), "PEA", "DCA ETF World", 200, "Virement"),
        (d(2), "Assurance-vie", "Versement programmé", 50, "Virement"),
        (d(8), "Courses", "Supermarché", round(random.uniform(140, 200), 2), "Carte bancaire"),
        (d(22), "Courses", "Supermarché", round(random.uniform(120, 190), 2), "Carte bancaire"),
        (d(12), "Transport", "Pass navigo / essence", round(random.uniform(50, 85), 2), "Carte bancaire"),
        (d(15), "Restaurants / sorties", "Resto / bar", round(random.uniform(40, 150), 2), "Carte bancaire"),
        (d(18), "Loisirs", "Cinéma / sport", round(random.uniform(20, 100), 2), "Carte bancaire"),
        (d(4), "Abonnements", "Streaming + salle", 29.97, "Carte bancaire"),
    ]
    if m in (3, 9): rows.append((d(20), "Prime / bonus", "Prime", 600, "Virement"))
    if random.random() < .5: rows.append((d(25), "Shopping", "Vêtements", round(random.uniform(30, 120), 2), "Carte bancaire"))
    if random.random() < .3: rows.append((d(14), "Santé", "Pharmacie / médecin", round(random.uniform(10, 60), 2), "Carte bancaire"))
rows += [
    (dt.date(2026, 2, 17), "Électronique", "Nouveau laptop", 1099, "Carte bancaire"),
    (dt.date(2026, 5, 9), "Mobilier / maison", "Canapé", 549, "Carte bancaire"),
    (dt.date(2026, 7, 21), "Voyage", "Vacances Portugal", 890, "Carte bancaire"),
    (dt.date(2026, 10, 4), "Vêtements (gros achat)", "Manteau d'hiver", 189, "Carte bancaire"),
]
rows.sort(key=lambda x: x[0])
alt = PatternFill("solid", fgColor="F7F9FD")
for i in range(5, N + 1):
    idx = i - 5
    if idx < len(rows):
        dte, cat, desc, amt, pay = rows[idx]
    else:
        dte = cat = desc = amt = pay = None
    for col, v, fmt in [("A", dte, "dd/mm/yyyy"), ("B", cat, None), ("C", desc, None), ("D", amt, EUR2), ("E", pay, None)]:
        c = tx[f"{col}{i}"]; c.value = v; c.font = font(color=BLUE_IN); c.border = BOX
        if fmt: c.number_format = fmt
    tx[f"F{i}"] = f'=IF(B{i}="","",IFERROR(INDEX({CTYPES},MATCH(B{i},{CATS},0)),"⚠ catégorie inconnue"))'
    tx[f"G{i}"] = f'=IF(A{i}="","",MONTH(A{i}))'
    tx[f"H{i}"] = f'=IF(A{i}="","",YEAR(A{i}))'
    for col in "FGH":
        tx[f"{col}{i}"].font = font(color="374151"); tx[f"{col}{i}"].border = BOX
        tx[f"{col}{i}"].alignment = Alignment(horizontal="center")
        tx[f"{col}{i}"].fill = PatternFill("solid", fgColor="F3F4F6")
dvc = DataValidation(type="list", formula1=f"={CATS}", allow_blank=True, showErrorMessage=True,
                     errorTitle="Catégorie", error="Choisis une catégorie de la liste (Paramètres).")
dvp = DataValidation(type="list", formula1="=Paramètres!$H$8:$H$14", allow_blank=True)
dvd = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True)
dvm = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
                     showErrorMessage=True, error="Montant positif uniquement — le type détermine si c'est une entrée ou une sortie.")
for v, rng in [(dvc, f"B5:B{N}"), (dvp, f"E5:E{N}"), (dvd, f"A5:A{N}"), (dvm, f"D5:D{N}")]:
    tx.add_data_validation(v); v.add(rng)
# colour by type
tcol = {"Revenu": "E6F4EA", "Placement": "E8F0FE", "Remboursement crédit": "FDECEA", "Achat unitaire": "FEF3E2"}
for t, colr in tcol.items():
    tx.conditional_formatting.add(f"F5:F{N}", CellIsRule(operator="equal", formula=[f'"{t}"'], fill=PatternFill("solid", fgColor=colr)))
tx.conditional_formatting.add(f"F5:F{N}", FormulaRule(formula=[f'LEFT(F5,1)="⚠"'], font=Font(color=RED, bold=True)))

# ---------------------------------------------------------------- Crédits
title(cr, "🏦  Crédits & remboursements", "Saisis tes prêts (cases jaunes) : mensualité, capital restant, intérêts et date de fin sont calculés.", "N", "9F1239")
header(cr, 5, 2, ["Nom du crédit", "Capital emprunté (€)", "Taux annuel", "Durée (mois)", "Date de début",
                  "Mensualité (€)", "Mois écoulés", "Capital restant dû (€)", "Remboursé (journal)",
                  "Coût total intérêts (€)", "Progression", "Date de fin"])
for lr in LOAN_ROWS:
    i = lr - 6
    L = loans[i] if i < len(loans) else (None,) * 5
    cell(cr, f"B{lr}", L[0], inp=True); cell(cr, f"C{lr}", L[1], EUR, inp=True)
    cell(cr, f"D{lr}", L[2], '0.00%', inp=True); cell(cr, f"E{lr}", L[3], "0", inp=True)
    cell(cr, f"F{lr}", L[4], "dd/mm/yyyy", inp=True)
    cell(cr, f"G{lr}", f'=IF(B{lr}="","",IF(D{lr}=0,C{lr}/E{lr},PMT(D{lr}/12,E{lr},-C{lr})))', EUR2)
    cell(cr, f"H{lr}", f'=IF(B{lr}="","",MIN(E{lr},MAX(0,DATEDIF(F{lr},TODAY(),"m")+1)))', "0")
    cell(cr, f"I{lr}", f'=IF(B{lr}="","",IF(H{lr}>=E{lr},0,IF(D{lr}=0,C{lr}-G{lr}*H{lr},-FV(D{lr}/12,H{lr},-G{lr},C{lr}))))', EUR)
    cell(cr, f"J{lr}", f'=IF(B{lr}="","",SUMIFS(Transactions!$D$5:$D${N},Transactions!$B$5:$B${N},B{lr}))', EUR)
    cell(cr, f"K{lr}", f'=IF(B{lr}="","",G{lr}*E{lr}-C{lr})', EUR)
    cell(cr, f"L{lr}", f'=IF(B{lr}="","",1-I{lr}/C{lr})', '0%')
    cell(cr, f"M{lr}", f'=IF(B{lr}="","",EDATE(F{lr},E{lr}))', "mm/yyyy")
r = LOAN_ROWS[-1] + 1
cell(cr, f"B{r}", "TOTAL", bold=True)
for col in "CGIJK":
    cell(cr, f"{col}{r}", f"=SUM({col}6:{col}{r-1})", EUR, bold=True)
for col in "BCDEFGHIJKLM":
    cr[f"{col}{r}"].fill = PatternFill("solid", fgColor=LIGHT)
cr.conditional_formatting.add("L6:L11", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="1E8E5A"))
for col, w in zip("BCDEFGHIJKLM", [20, 15, 10, 10, 13, 14, 10, 16, 15, 15, 13, 11]):
    cr.column_dimensions[col].width = w
# amortisation
section(cr, "B15", "📋  Tableau d'amortissement", RED)
cr["B16"] = "Crédit à afficher ▸"; cr["B16"].font = font(bold=True)
cell(cr, "C16", "Crédit auto", inp=True)
cr.merge_cells("C16:D16")
dva = DataValidation(type="list", formula1="=$B$6:$B$11", allow_blank=False)
cr.add_data_validation(dva); dva.add("C16")
helpers = [("F16", "Capital", "C"), ("H16", "Taux", "D"), ("J16", "Durée", "E")]
cr["F16"] = "Capital"; cr["H16"] = "Taux"; cr["J16"] = "Durée"; cr["L16"] = "Mensualité"
cell(cr, "G16", '=IFERROR(INDEX($C$6:$C$11,MATCH($C$16,$B$6:$B$11,0)),0)', EUR)
cell(cr, "I16", '=IFERROR(INDEX($D$6:$D$11,MATCH($C$16,$B$6:$B$11,0)),0)', '0.00%')
cell(cr, "K16", '=IFERROR(INDEX($E$6:$E$11,MATCH($C$16,$B$6:$B$11,0)),0)', "0")
cell(cr, "M16", '=IFERROR(INDEX($G$6:$G$11,MATCH($C$16,$B$6:$B$11,0)),0)', EUR2)
cell(cr, "N16", '=IFERROR(INDEX($F$6:$F$11,MATCH($C$16,$B$6:$B$11,0)),0)', "dd/mm/yyyy")
cr["N15"] = "Début"; cr["N15"].font = font(size=9, color=SLATE)
for ref in ("F16", "H16", "J16", "L16"):
    cr[ref].font = font(bold=True, color=SLATE); cr[ref].alignment = Alignment(horizontal="right")
header(cr, 18, 2, ["N°", "Échéance", "Mensualité", "Intérêts", "Capital remboursé", "Capital restant", "Statut"])
for k in range(1, 361):
    rr = 18 + k
    prev = "$G$16" if k == 1 else f"G{rr-1}"
    cr[f"B{rr}"] = f'=IF({k}<=$K$16,{k},"")'
    cr[f"C{rr}"] = f'=IF(B{rr}="","",EDATE($N$16,B{rr}-1))'
    cr[f"D{rr}"] = f'=IF(B{rr}="","",$M$16)'
    cr[f"E{rr}"] = f'=IF(B{rr}="","",{prev}*$I$16/12)'
    cr[f"F{rr}"] = f'=IF(B{rr}="","",D{rr}-E{rr})'
    cr[f"G{rr}"] = f'=IF(B{rr}="","",MAX(0,{prev}-F{rr}))'
    cr[f"H{rr}"] = f'=IF(B{rr}="","",IF(C{rr}<=TODAY(),"✔ Payé","À venir"))'
    for col, fmt in zip("BCDEFGH", ["0", "mm/yyyy", EUR2, EUR2, EUR2, EUR2, None]):
        c = cr[f"{col}{rr}"]; c.font = font(size=9); c.border = BOX
        if fmt: c.number_format = fmt
        c.alignment = Alignment(horizontal="center")
cr.conditional_formatting.add("H19:H378", CellIsRule(operator="equal", formula=['"✔ Payé"'], font=Font(color=GREEN), fill=PatternFill("solid", fgColor="E6F4EA")))
cr.freeze_panes = "A6"; cr.column_dimensions["N"].width = 12

# ---------------------------------------------------------------- Placements
title(pl, "📈  Placements financiers", "Versements tirés du journal • Valeur actuelle à mettre à jour • Projection par intérêts composés", "M", "065F46")
header(pl, 5, 2, ["Placement", "Type", "Solde au 1er janv. (€)", "Versements année (journal)", "Valeur actuelle (€)",
                  "Plus / moins-value (€)", "Performance", "Rendement annuel estimé", "Versement mensuel prévu (€)",
                  "Horizon (années)", "Valeur projetée (€)", "Dont intérêts (€)"])
PTYPES = ["Livret", "Actions / ETF", "Assurance-vie", "Crypto", "Immobilier / SCPI", "Obligations", "Autre"]
for prr in PL_ROWS:
    i = prr - 6
    P = places[i] if i < len(places) else (None,) * 7
    cell(pl, f"B{prr}", P[0], inp=True); cell(pl, f"C{prr}", P[1], inp=True)
    cell(pl, f"D{prr}", P[2], EUR, inp=True)
    cell(pl, f"E{prr}", f'=IF(B{prr}="","",SUMIFS(Transactions!$D$5:$D${N},Transactions!$B$5:$B${N},B{prr},Transactions!$H$5:$H${N},Paramètres!$C$5))', EUR)
    cell(pl, f"F{prr}", P[3], EUR, inp=True)
    cell(pl, f"G{prr}", f'=IF(B{prr}="","",F{prr}-(D{prr}+E{prr}))', EUR)
    cell(pl, f"H{prr}", f'=IF(B{prr}="","",IFERROR(G{prr}/(D{prr}+E{prr}),0))', PCT)
    cell(pl, f"I{prr}", P[4], '0.0%', inp=True); cell(pl, f"J{prr}", P[5], EUR, inp=True)
    cell(pl, f"K{prr}", P[6], "0", inp=True)
    cell(pl, f"L{prr}", f'=IF(B{prr}="","",IF(I{prr}=0,F{prr}+J{prr}*K{prr}*12,FV(I{prr}/12,K{prr}*12,-J{prr},-F{prr})))', EUR)
    cell(pl, f"M{prr}", f'=IF(B{prr}="","",L{prr}-F{prr}-J{prr}*K{prr}*12)', EUR)
r = PL_ROWS[-1] + 1
cell(pl, f"B{r}", "TOTAL", bold=True)
for col in "DEFGJLM":
    cell(pl, f"{col}{r}", f"=SUM({col}6:{col}{r-1})", EUR, bold=True)
cell(pl, f"H{r}", f"=IFERROR(G{r}/(D{r}+E{r}),0)", PCT, bold=True)
for col in "BCDEFGHIJKLM":
    pl[f"{col}{r}"].fill = PatternFill("solid", fgColor=LIGHT)
dvt = DataValidation(type="list", formula1='"' + ",".join(PTYPES) + '"', allow_blank=True)
pl.add_data_validation(dvt); dvt.add("C6:C11")
for rng in ("G6:G12", "H6:H12"):
    pl.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], font=Font(color=GREEN, bold=True)))
    pl.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], font=Font(color=RED, bold=True)))
for col, w in zip("BCDEFGHIJKLM", [18, 16, 15, 16, 15, 15, 12, 13, 15, 10, 16, 15]):
    pl.column_dimensions[col].width = w
pie = PieChart(); pie.title = "Répartition du patrimoine financier"
pie.add_data(Reference(pl, min_col=6, min_row=5, max_row=11), titles_from_data=True)
pie.set_categories(Reference(pl, min_col=2, min_row=6, max_row=11))
pie.dataLabels = pie_labels(); color_points(pie.series[0], [SKY, ACCENT, "8B5CF6", AMBER, GREEN, RED]); pie.legend.position = "r"
pie.height, pie.width = 8, 12
pl.add_chart(pie, "B15")
# projection year by year (total)
section(pl, "J15", "🔭  Projection du patrimoine", GREEN)
header(pl, 16, 10, ["Année", "Valeur projetée (€)"])
for y in range(0, 21):
    rr = 17 + y
    cell(pl, f"J{rr}", y, "0")
    cell(pl, f"K{rr}", "=" + "+".join(
        f'IF(B{p}="",0,IF(I{p}=0,F{p}+J{p}*12*MIN(J{rr},K{p}),FV(I{p}/12,J{rr}*12,-J{p},-F{p})))' for p in PL_ROWS), EUR)
lc = LineChart(); lc.title = "Évolution projetée"; lc.legend = None
lc.add_data(Reference(pl, min_col=11, min_row=16, max_row=37), titles_from_data=True)
lc.set_categories(Reference(pl, min_col=10, min_row=17, max_row=37))
lc.y_axis.numFmt = '#,##0 €'; lc.height, lc.width = 8, 14
lc.series[0].graphicalProperties.line.solidFill = GREEN; lc.series[0].graphicalProperties.line.width = 28000
lc.y_axis.delete = False; lc.x_axis.delete = False; pl.add_chart(lc, "M16")

# ---------------------------------------------------------------- Dashboard
title(dash, "💰  Tableau de bord financier", "Tout se met à jour automatiquement à partir du journal des transactions.", "P", NAVY)
dash["B4"] = "Année"; dash["B4"].font = font(bold=True, color=SLATE)
cell(dash, "C4", "=Paramètres!C5", "0", color="008000", bold=True)
dash["E4"] = "Mois analysé ▸"; dash["E4"].font = font(bold=True, color=SLATE); dash["E4"].alignment = Alignment(horizontal="right")
cell(dash, "F4", 11, "0", inp=True, bold=True)
dash["F4"].comment = Comment("Choisis le mois (1 à 12) pour le bloc Budget vs Réel.", "Finances")
MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
cell(dash, "G4", '=CHOOSE(F4,' + ",".join(f'"{m}"' for m in MOIS) + ")", bold=True, color=ACCENT)
dvmo = DataValidation(type="whole", operator="between", formula1="1", formula2="12")
dash.add_data_validation(dvmo); dvmo.add("F4")

# monthly matrix
MR = 16  # header row
section(dash, f"B{MR-1}", "📅  Synthèse mensuelle")
short = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
header(dash, MR, 2, ["Poste"] + short + ["Total année", "Moy. / mois"])
SUM = lambda typ, mcol: (f'SUMIFS(Transactions!$D$5:$D${N},Transactions!$F$5:$F${N},{typ},'
                         f'Transactions!$G$5:$G${N},{mcol},Transactions!$H$5:$H${N},$C$4)')
lines = ["Revenu", "Loyer & charges", "Dépense courante", "Achat unitaire", "Remboursement crédit", "Placement"]
labels = ["Revenus", "Loyer & charges", "Dépenses courantes", "Achats à l'unité", "Remboursements crédit", "Placements"]
cols = [chr(ord("C") + i) for i in range(12)]
for j, (t, lab) in enumerate(zip(lines, labels)):
    rr = MR + 1 + j
    cell(dash, f"B{rr}", lab, bold=True)
    dash[f"A{rr}"] = t; dash[f"A{rr}"].font = font(color=WHITE, size=1)  # hidden key
    for m, c in enumerate(cols, 1):
        cell(dash, f"{c}{rr}", "=" + SUM(f"$A{rr}", m), EUR)
    cell(dash, f"O{rr}", f"=SUM(C{rr}:N{rr})", EUR, bold=True)
    cell(dash, f"P{rr}", f'=IFERROR(O{rr}/MAX(1,COUNTIF(C{MR+1}:N{MR+1},">0")),0)', EUR)
R_REV, R_LOY, R_DEP, R_ACH, R_CRE, R_PLA = range(MR + 1, MR + 7)
R_SOR, R_RES, R_EPA, R_TAU = MR + 7, MR + 8, MR + 9, MR + 10
for c in cols + ["O", "P"]:
    cell(dash, f"{c}{R_SOR}", f"=SUM({c}{R_LOY}:{c}{R_CRE})", EUR, bold=True)
    cell(dash, f"{c}{R_RES}", f"={c}{R_REV}-{c}{R_SOR}-{c}{R_PLA}", EUR, bold=True)
    cell(dash, f"{c}{R_EPA}", f"={c}{R_PLA}+{c}{R_RES}", EUR, bold=True)
    cell(dash, f"{c}{R_TAU}", f"=IFERROR({c}{R_EPA}/{c}{R_REV},0)", PCT, bold=True)
for rr, lab, colr in [(R_SOR, "Total dépenses (hors placements)", "FFE4E6"), (R_RES, "Reste à vivre (non affecté)", LIGHT),
                      (R_EPA, "Épargne totale (placé + reste)", "D1FAE5"), (R_TAU, "Taux d'épargne", "D1FAE5")]:
    cell(dash, f"B{rr}", lab, bold=True)
    for c in ["B"] + cols + ["O", "P"]:
        dash[f"{c}{rr}"].fill = PatternFill("solid", fgColor=colr)
for rr in (R_RES, R_EPA):
    dash.conditional_formatting.add(f"C{rr}:P{rr}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color=RED, bold=True)))
dash.conditional_formatting.add(f"C{R_TAU}:P{R_TAU}", CellIsRule(operator="greaterThanOrEqual", formula=["0.2"], font=Font(color=GREEN, bold=True)))

# KPI tiles (rows 6-12)
kpis = [
    ("B", "C", "💶  Revenus (année)", f"=O{R_REV}", EUR, GREEN),
    ("E", "F", "💸  Dépenses (année)", f"=O{R_SOR}", EUR, RED),
    ("H", "I", "📈  Investi (année)", f"=O{R_PLA}", EUR, ACCENT),
    ("K", "L", "🐷  Taux d'épargne", f"=O{R_TAU}", PCT, GREEN),
    ("N", "P", "🧮  Reste à vivre / mois", f"=P{R_RES}", EUR, NAVY),
]
kpis2 = [
    ("B", "C", "🏛️  Patrimoine placé", "=Placements!F12", EUR, GREEN),
    ("E", "F", "✨  Plus-values latentes", "=Placements!G12", EUR, GREEN),
    ("H", "I", "🏦  Capital restant dû", "=Crédits!I12", EUR, RED),
    ("K", "L", "💎  Patrimoine net", "=Placements!F12-Crédits!I12", EUR, NAVY),
    ("N", "P", "📆  Mensualités crédits", "=Crédits!G12", EUR, RED),
]
dash.row_dimensions[9].height = 12; dash.row_dimensions[13].height = 18
for row0, group in [(6, kpis), (10, kpis2)]:
    for c1, c2, lab, f, fmt, colr in group:
        dash.merge_cells(f"{c1}{row0}:{c2}{row0}"); dash.merge_cells(f"{c1}{row0+1}:{c2}{row0+2}")
        a = dash[f"{c1}{row0}"]; a.value = lab
        a.font = font(size=9, bold=True, color=SLATE); a.alignment = Alignment(horizontal="left", indent=1)
        b = dash[f"{c1}{row0+1}"]; b.value = f; b.number_format = fmt
        b.font = font(size=20, bold=True, color=colr); b.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        cs = [chr(x) for x in range(ord(c1), ord(c2) + 1)]
        for rr in range(row0, row0 + 3):
            for cc in cs:
                dash[f"{cc}{rr}"].fill = PatternFill("solid", fgColor=WHITE)
        for cc in cs:
            dash[f"{cc}{row0}"].border = Border(top=Side(style="thick", color=colr))
            dash[f"{cc}{row0+2}"].border = Border(bottom=Side(style="thin", color="CBD5E1"))
        dash.row_dimensions[row0].height = 22; dash.row_dimensions[row0+1].height = 20; dash.row_dimensions[row0+2].height = 20

# Budget vs réel (selected month)
BR = R_TAU + 3
section(dash, f"B{BR}", "🎯  Budget vs Réel — mois analysé", AMBER)
header(dash, BR + 1, 2, ["Catégorie", "Budget", "Réel", "Écart", "% utilisé"])
budget_cats = [n for n, t, b in cats if b]
for k, name in enumerate(budget_cats):
    rr = BR + 2 + k
    cell(dash, f"B{rr}", f"=Paramètres!B{CAT_ROWS[name]}")
    cell(dash, f"C{rr}", f"=Paramètres!D{CAT_ROWS[name]}", EUR)
    cell(dash, f"D{rr}", f'=SUMIFS(Transactions!$D$5:$D${N},Transactions!$B$5:$B${N},B{rr},Transactions!$G$5:$G${N},$F$4,Transactions!$H$5:$H${N},$C$4)', EUR)
    cell(dash, f"E{rr}", f"=C{rr}-D{rr}", EUR)
    cell(dash, f"F{rr}", f"=IFERROR(D{rr}/C{rr},0)", '0%')
BL = BR + 1 + len(budget_cats)
rr = BL + 1
cell(dash, f"B{rr}", "TOTAL", bold=True)
for col in "CDE":
    cell(dash, f"{col}{rr}", f"=SUM({col}{BR+2}:{col}{BL})", EUR, bold=True)
cell(dash, f"F{rr}", f"=IFERROR(D{rr}/C{rr},0)", '0%', bold=True)
for col in "BCDEF":
    dash[f"{col}{rr}"].fill = PatternFill("solid", fgColor=LIGHT)
dash.conditional_formatting.add(f"E{BR+2}:E{rr}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color=RED, bold=True), fill=PatternFill("solid", fgColor="FDECEA")))
dash.conditional_formatting.add(f"F{BR+2}:F{rr}", CellIsRule(operator="greaterThan", formula=["1"], font=Font(color=RED, bold=True)))
dash.conditional_formatting.add(f"F{BR+2}:F{rr}", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1.5, color="3B6EF5"))
dash[f"B{rr+1}"] = "Les budgets se modifient dans l'onglet Paramètres. Rouge = dépassement."
dash[f"B{rr+1}"].font = font(size=9, italic=True, color=SLATE)

# charts
ch = BarChart(); ch.type = "col"; ch.title = "Revenus vs dépenses vs placements"
for rrow in (R_REV, R_SOR, R_PLA):
    ch.add_data(Reference(dash, min_col=2, max_col=14, min_row=rrow), from_rows=True, titles_from_data=True)
ch.set_categories(Reference(dash, min_col=3, max_col=14, min_row=MR))
ch.y_axis.numFmt = '#,##0 €'; ch.height, ch.width = 8.5, 17; ch.gapWidth = 60
for s, colr in zip(ch.series, [GREEN, RED, ACCENT]):
    s.graphicalProperties.solidFill = colr; s.graphicalProperties.line.solidFill = colr
soften(ch); dash.add_chart(ch, f"H{BR}")

st = BarChart(); st.type = "col"; st.grouping = "stacked"; st.overlap = 100; st.title = "Où part l'argent chaque mois"
for rrow in (R_LOY, R_DEP, R_ACH, R_CRE):
    st.add_data(Reference(dash, min_col=2, max_col=14, min_row=rrow), from_rows=True, titles_from_data=True)
st.set_categories(Reference(dash, min_col=3, max_col=14, min_row=MR))
st.y_axis.numFmt = '#,##0 €'; st.height, st.width = 8.5, 17; st.gapWidth = 60
for s, colr in zip(st.series, [SLATE, ACCENT, AMBER, RED]):
    s.graphicalProperties.solidFill = colr; s.graphicalProperties.line.solidFill = colr
soften(st); dash.add_chart(st, f"H{BR+18}")

pc = PieChart(); pc.title = "Répartition des sorties (année)"
pc.add_data(Reference(dash, min_col=15, min_row=R_LOY, max_row=R_PLA))
pc.set_categories(Reference(dash, min_col=2, min_row=R_LOY, max_row=R_PLA))
pc.dataLabels = pie_labels(); color_points(pc.series[0], [SLATE, ACCENT, AMBER, RED, GREEN]); pc.legend.position = "r"
pc.height, pc.width = 8.5, 11
dash.add_chart(pc, f"B{rr+3}")

dash.column_dimensions["A"].width = 2
dash.column_dimensions["B"].width = 30
for c in cols: dash.column_dimensions[c].width = 11
dash.column_dimensions["O"].width = 13; dash.column_dimensions["P"].width = 12
dash.freeze_panes = "A5"; dash.row_dimensions[4].height = 26

# ---------------------------------------------------------------- Mode d'emploi
title(guide, "📘  Mode d'emploi", "3 minutes pour prendre le fichier en main", "C", "B45309")
steps = [
    ("1. Import Google Sheets", "drive.google.com → Nouveau → Importer un fichier → ouvrir avec Google Sheets (ou Fichier → Importer → Remplacer le classeur)."),
    ("2. Paramètres", "Choisis l'année suivie. Ajuste tes catégories et budgets mensuels (cases jaunes)."),
    ("3. Crédits", "Saisis chaque prêt : capital, taux, durée, date de début. Mensualité, capital restant, intérêts et tableau d'amortissement sont automatiques."),
    ("4. Placements", "Saisis tes comptes (Livret A, PEA…), le solde au 1er janvier et la valeur actuelle. Les versements viennent du journal."),
    ("5. Transactions", "Ajoute une ligne par opération : date, catégorie (liste déroulante), montant POSITIF. Le type se déduit de la catégorie."),
    ("6. Dashboard", "Tout se calcule : synthèse mensuelle, taux d'épargne, budget vs réel du mois choisi (case F4), graphiques."),
    ("Codes couleur", "Texte bleu sur fond jaune = à saisir • Noir = formule (ne pas toucher) • Vert = lien vers un autre onglet."),
    ("Remboursement de crédit", "Saisis chaque mensualité dans le journal avec la catégorie du crédit (ex. « Crédit auto ») : elle compte dans les dépenses et la colonne « Remboursé » de l'onglet Crédits."),
    ("Placement", "Un virement vers un placement = catégorie du placement (ex. « PEA »). Il est compté comme épargne, pas comme dépense."),
    ("Données d'exemple", "Le journal contient des exemples (janv.–nov. 2026). Supprime les lignes 5+ des colonnes A à E pour repartir de zéro — les formules restent."),
    ("Automatisation bonus", "Dans Google Sheets : Extensions → Apps Script, colle le script du fichier « apps_script.gs » pour ajouter un menu « 💰 Finances » (ajout rapide, tri du journal, copie des charges fixes du mois)."),
]
for k, (h, t) in enumerate(steps):
    rr = 5 + k * 2
    guide[f"B{rr}"] = h; guide[f"B{rr}"].font = font(bold=True, color=NAVY, size=11)
    guide[f"C{rr}"] = t; guide[f"C{rr}"].font = font(size=10); guide[f"C{rr}"].alignment = Alignment(wrap_text=True, vertical="top")
    guide.row_dimensions[rr].height = 32
guide.column_dimensions["B"].width = 26; guide.column_dimensions["C"].width = 110

tx.conditional_formatting.add(f"A5:E{N}", FormulaRule(formula=['AND($A5<>"",MOD(ROW(),2)=0)'], fill=PatternFill("solid", fgColor="F8FAFC")))
for i in range(5, 400):
    tx.row_dimensions[i].height = 20
for i in range(19, 379):
    cr.row_dimensions[i].height = 18
for ws in (pa, pl, cr):
    for i in range(6, 40):
        if ws.row_dimensions[i].height is None: ws.row_dimensions[i].height = 21
# dashboard "app" background: every unfilled cell becomes light slate
for row in dash.iter_rows(min_row=4, max_row=110, min_col=1, max_col=18):
    for c in row:
        if c.fill is None or c.fill.fgColor is None or c.fill.fgColor.rgb in ("00000000", None) or c.fill.fill_type is None:
            c.fill = PatternFill("solid", fgColor=PAGE)
for r in range(MR + 1, R_TAU + 1):
    dash.row_dimensions[r].height = 22
for c in ["B"] + cols + ["O", "P"]:
    dash[f"{c}{R_REV}"].font = font(bold=True, color=GREEN)
    dash[f"{c}{R_PLA}"].font = font(color=ACCENT, bold=(c in "OP"))
    if c != "B": dash[f"{c}{R_TAU}"].alignment = Alignment(horizontal="right", vertical="center")
for c in ["O", "P"]:
    for r in range(MR + 1, R_TAU + 1):
        if dash[f"{c}{r}"].fill.fgColor.rgb in ("00FFFFFF", "FFFFFFFF"):
            dash[f"{c}{r}"].fill = PatternFill("solid", fgColor=LIGHT)
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 90
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
wb.save(OUT)
print("ok", len(rows), "rows")
