import random, datetime as dt
from openpyxl.chart import BarChart, PieChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Font
from openpyxl.comments import Comment
from common import *

N0, N1 = 7, 1506  # journal rows
TX = "Transactions"
TXB = R(TX, f"$B${N0}:$B${N1}"); TXC = R(TX, f"$C${N0}:$C${N1}"); TXE = R(TX, f"$E${N0}:$E${N1}")
TXG = R(TX, f"$G${N0}:$G${N1}"); TXH = R(TX, f"$H${N0}:$H${N1}"); TXI = R(TX, f"$I${N0}:$I${N1}")
PA = "Paramètres"
P_NAME = R(PA, "$C$6"); P_YEAR = R(PA, "$C$7"); P_MONTH = R(PA, "$C$8"); P_SAVE = R(PA, "$C$9")
MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
MCOURT = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
MONTH_NAME = "CHOOSE({m}," + ",".join(f'"{x}"' for x in MOIS) + ")"
TYPES = ["Revenu", "Charges fixes", "Abonnement", "Dépense courante", "Achat unitaire", "Remboursement crédit", "Épargne & placement"]
TYPE_COL = dict(zip(TYPES, ["green", "peach", "pink", "blue", "yellow", "lav", "mint"]))

CATS = [
    ("Salaire", "Revenu", 2450), ("Prime / bonus", "Revenu", 0), ("Side business", "Revenu", 300),
    ("Remboursements reçus", "Revenu", 0), ("Autre revenu", "Revenu", 0),
    ("Loyer", "Charges fixes", 750), ("Électricité / gaz", "Charges fixes", 70), ("Eau", "Charges fixes", 25),
    ("Internet", "Charges fixes", 30), ("Téléphone", "Charges fixes", 15), ("Assurance habitation", "Charges fixes", 15),
    ("Assurance auto", "Charges fixes", 45), ("Mutuelle santé", "Charges fixes", 35),
    ("Netflix", "Abonnement", 14), ("Spotify", "Abonnement", 11), ("Salle de sport", "Abonnement", 30),
    ("Amazon Prime", "Abonnement", 7), ("Cloud / stockage", "Abonnement", 3),
    ("Courses", "Dépense courante", 350), ("Transport / essence", "Dépense courante", 90),
    ("Restaurants / sorties", "Dépense courante", 120), ("Loisirs", "Dépense courante", 80),
    ("Shopping", "Dépense courante", 80), ("Santé", "Dépense courante", 30), ("Soins perso", "Dépense courante", 30),
    ("Cadeaux", "Dépense courante", 30), ("Éducation / livres", "Dépense courante", 25), ("Divers", "Dépense courante", 40),
    ("Électronique", "Achat unitaire", 0), ("Mobilier / maison", "Achat unitaire", 0), ("Voyage", "Achat unitaire", 0),
    ("Gros achat", "Achat unitaire", 0),
]
LOANS = [("Crédit auto", 12000, 0.049, 60, dt.date(2025, 3, 1)), ("Prêt étudiant", 8000, 0.012, 72, dt.date(2024, 9, 1))]
PLACES = [("Livret A", "Livret", 4500, 6250, 0.024, 150, 10), ("PEA", "Actions / ETF", 3000, 5600, 0.07, 200, 20),
          ("Assurance-vie", "Assurance-vie", 2000, 2380, 0.035, 50, 15), ("Crypto", "Crypto", 500, 740, 0.10, 0, 5)]
LOAN_ROWS = list(range(7, 13)); PL_ROWS = list(range(7, 13))
CAT_ROW = {}
LISTS = {}


def sumtx(*crit):
    return f"SUMIFS({TXE}," + ",".join(f"{a},{b}" for a, b in crit) + ")"


# ===================================================================== Paramètres
def build_params(wb):
    ws = wb.create_sheet(PA)
    widths = {"B": 26, "C": 22, "D": 16, "E": 2, "F": 22, "G": 2, "H": 18, "I": 2, "J": 22, "K": 2, "L": 16, "M": 2,
              "N": 16, "O": 2, "P": 18, "Q": 2, "R": 22, "S": 8, "T": 8, "U": 10, "V": 2, "W": 18, "X": 2, "Y": 22, "Z": 2, "AA": 18}
    setup(ws, "⚙️ Paramètres", "Réglages globaux, catégories et listes déroulantes — le texte bleu est modifiable", 27, 90, widths, tab="grey")
    card(ws, 5, 2, 3, 6, "Réglages", "lav")
    for i, (lab, v, fmt) in enumerate([("Prénom", "Alex", None), ("Année suivie", YEAR, "0"), ("Mois affiché (1-12)", MONTH, "0"),
                                       ("Objectif taux d'épargne", 0.2, PCT)]):
        put(ws, 6 + i, 2, lab, bold=True)
        put(ws, 6 + i, 3, v, fmt, inp=True, align=CENTER)
    put(ws, 10, 2, "Mois en toutes lettres", color=MUTED)
    put(ws, 10, 3, "=" + MONTH_NAME.format(m="C8") + '&" "&C7', align=CENTER, bold=True, color=PAL["lav"][2])
    ws["C8"].comment = Comment("Pilote tous les onglets mensuels (Budget, Habitudes, Bien-être, Journal…).", "Planner")
    dv_list(ws, "=$W$6:$W$17" if False else '"1,2,3,4,5,6,7,8,9,10,11,12"', "C8")

    r0 = 12
    card(ws, r0, 2, 3, 3 + len(CATS) + 12 + 8, "Catégories financières", "green")
    th(ws, r0 + 1, 2, ["Catégorie", "Type", "Budget mensuel"], "green")
    r = r0 + 2
    for name, typ, bud in CATS:
        put(ws, r, 2, name, inp=True); put(ws, r, 3, typ, inp=True); put(ws, r, 4, bud, EUR, inp=True)
        CAT_ROW[name] = r; r += 1
    LISTS["loan_cat_rows"] = []
    for lr in LOAN_ROWS:
        put(ws, r, 2, f'=IF(Crédits!B{lr}="","",Crédits!B{lr})', color="3D8B57")
        put(ws, r, 3, f'=IF(B{r}="","","Remboursement crédit")')
        put(ws, r, 4, f'=IF(B{r}="","",Crédits!G{lr})', EUR)
        LISTS["loan_cat_rows"].append(r); r += 1
    LISTS["pl_cat_rows"] = []
    for prr in PL_ROWS:
        put(ws, r, 2, f'=IF(Placements!B{prr}="","",Placements!B{prr})', color="3D8B57")
        put(ws, r, 3, f'=IF(B{r}="","","Épargne & placement")')
        put(ws, r, 4, f'=IF(B{r}="","",Placements!J{prr})', EUR)
        LISTS["pl_cat_rows"].append(r); r += 1
    LISTS["spare_rows"] = list(range(r, r + 8))
    for _ in range(8):
        put(ws, r, 2, None, inp=True); put(ws, r, 3, None, inp=True); put(ws, r, 4, None, EUR, inp=True); r += 1
    last = r - 1
    LISTS["cat"] = f"='{PA}'!$B${r0+2}:$B${last}"
    LISTS["cat_rng"] = (R(PA, f"$B${r0+2}:$B${last}"), R(PA, f"$C${r0+2}:$C${last}"), R(PA, f"$D${r0+2}:$D${last}"))
    note(ws, last + 2, 2, "Crédits et placements sont ajoutés automatiquement depuis leurs onglets. 8 lignes libres pour tes catégories.", 3)
    dv_list(ws, f"=$F$7:$F${6+len(TYPES)}", f"C{r0+2}:C{last}", strict=True)

    lists = [
        ("F", "Types", TYPES, "green"),
        ("H", "Paiement", ["Carte bancaire", "Virement", "Prélèvement", "Espèces", "Chèque", "PayPal"], "blue"),
        ("J", "Domaines de vie", ["Carrière", "Finances", "Santé & sport", "Mental", "Relations", "Apprentissage", "Maison", "Loisirs", "Contribution"], "peach"),
        ("L", "Statuts", ["Backlog", "À faire", "En cours", "En attente", "Terminé"], "pink"),
        ("N", "Priorités", ["Très haute", "Haute", "Moyenne", "Basse"], "yellow"),
        ("P", "Activités", ["Travail", "Sport", "Apprentissage", "Repos", "Social", "Admin", "Perso", "Trajet"], "mint"),
        ("W", "Sports", ["Musculation", "Course", "Vélo", "Natation", "Yoga", "HIIT", "Marche", "Sport co", "Mobilité"], "green"),
        ("Y", "Rayons courses", ["Fruits & légumes", "Viandes & poissons", "Crémerie", "Épicerie", "Surgelés", "Boissons", "Hygiène", "Maison"], "blue"),
        ("AA", "Types placement", ["Livret", "Actions / ETF", "Assurance-vie", "Crypto", "Immobilier / SCPI", "Obligations", "Autre"], "lav"),
    ]
    for col, title, items, pc in lists:
        from openpyxl.utils import column_index_from_string as CI
        c = CI(col)
        card(ws, 5, c, 1, len(items) + 4, title, pc, size=8)
        for i, it in enumerate(items):
            put(ws, 6 + i, c, it, inp=True)
        LISTS[title] = f"='{PA}'!${col}$6:${col}${6+len(items)+2}"
    # frequencies
    freqs = [("Chaque semaine", 7, 0, 52 / 12), ("Toutes les 2 semaines", 14, 0, 26 / 12), ("Toutes les 4 semaines", 28, 0, 13 / 12),
             ("Chaque mois", 0, 1, 1), ("Tous les 2 mois", 0, 2, 1 / 2), ("Chaque trimestre", 0, 3, 1 / 3),
             ("Tous les 6 mois", 0, 6, 1 / 6), ("Chaque année", 0, 12, 1 / 12), ("Une fois", 0, 0, 0)]
    card(ws, 5, 18, 4, len(freqs) + 3, "Fréquences", "lav", size=8)
    th(ws, 6, 18, ["Fréquence", "Jours", "Mois", "× / mois"], "lav")
    for i, (f, d, m, k) in enumerate(freqs):
        put(ws, 7 + i, 18, f); put(ws, 7 + i, 19, d, "0"); put(ws, 7 + i, 20, m, "0"); put(ws, 7 + i, 21, k, "0.00")
    LISTS["freq"] = f"='{PA}'!$R$7:$R${6+len(freqs)}"
    LISTS["freq_tbl"] = (R(PA, f"$R$7:$R${6+len(freqs)}"), R(PA, f"$S$7:$S${6+len(freqs)}"),
                         R(PA, f"$T$7:$T${6+len(freqs)}"), R(PA, f"$U$7:$U${6+len(freqs)}"))
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Transactions
def sample_tx():
    random.seed(7)
    rows = []
    for m in range(1, 12):
        lastday = 13 if m == 11 else 28
        def d(day): return dt.date(2026, m, day)
        base = [
            (1, "Salaire", "Salaire net", 2450, "Virement"), (3, "Loyer", "Loyer appartement", 750, "Prélèvement"),
            (5, "Électricité / gaz", "EDF", round(random.uniform(48, 92)), "Prélèvement"), (6, "Eau", "Veolia", 24.6, "Prélèvement"),
            (6, "Internet", "Box fibre", 29.99, "Prélèvement"), (6, "Téléphone", "Forfait mobile", 14.99, "Prélèvement"),
            (7, "Assurance habitation", "MAIF", 14.5, "Prélèvement"), (7, "Assurance auto", "Assurance voiture", 44.9, "Prélèvement"),
            (8, "Mutuelle santé", "Mutuelle", 34.5, "Prélèvement"),
            (4, "Netflix", "Netflix", 13.49, "Carte bancaire"), (4, "Spotify", "Spotify", 10.99, "Carte bancaire"),
            (2, "Salle de sport", "Abonnement salle", 29.9, "Prélèvement"), (9, "Amazon Prime", "Prime", 6.99, "Carte bancaire"),
            (9, "Cloud / stockage", "iCloud 200 Go", 2.99, "Carte bancaire"),
            (5, "Crédit auto", "Mensualité crédit auto", 225.91, "Prélèvement"), (10, "Prêt étudiant", "Mensualité prêt étudiant", 115.21, "Prélèvement"),
            (2, "Livret A", "Virement épargne", 150, "Virement"), (2, "PEA", "DCA ETF World", 200, "Virement"),
            (2, "Assurance-vie", "Versement programmé", 50, "Virement"),
            (8, "Courses", "Supermarché", round(random.uniform(95, 140), 2), "Carte bancaire"),
            (16, "Courses", "Supermarché", round(random.uniform(90, 135), 2), "Carte bancaire"),
            (24, "Courses", "Marché + supermarché", round(random.uniform(80, 125), 2), "Carte bancaire"),
            (11, "Transport / essence", "Plein d'essence", round(random.uniform(45, 70), 2), "Carte bancaire"),
            (25, "Transport / essence", "Plein d'essence", round(random.uniform(35, 60), 2), "Carte bancaire"),
            (12, "Restaurants / sorties", "Resto entre amis", round(random.uniform(30, 70), 2), "Carte bancaire"),
            (20, "Restaurants / sorties", "Bar / ciné", round(random.uniform(20, 60), 2), "Carte bancaire"),
            (18, "Loisirs", "Activité week-end", round(random.uniform(20, 90), 2), "Carte bancaire"),
            (13, "Soins perso", "Coiffeur / soins", round(random.uniform(15, 35), 2), "Carte bancaire"),
            (21, "Éducation / livres", "Livres", round(random.uniform(10, 30), 2), "Carte bancaire"),
        ]
        if m >= 3: base.append((15, "Side business", "Ventes en ligne", round(random.uniform(180, 460)), "Virement"))
        if m in (3, 9): base.append((20, "Prime / bonus", "Prime semestrielle", 600, "Virement"))
        if random.random() < .6: base.append((23, "Shopping", "Vêtements", round(random.uniform(30, 110), 2), "Carte bancaire"))
        if random.random() < .4: base.append((14, "Santé", "Pharmacie / médecin", round(random.uniform(10, 55), 2), "Carte bancaire"))
        if random.random() < .3: base.append((19, "Cadeaux", "Cadeau anniversaire", round(random.uniform(20, 60), 2), "Carte bancaire"))
        rows += [(d(day), *rest) for day, *rest in base if day <= lastday]
    rows += [(dt.date(2026, 2, 17), "Électronique", "Nouveau laptop", 1099, "Carte bancaire"),
             (dt.date(2026, 5, 9), "Mobilier / maison", "Canapé", 549, "Carte bancaire"),
             (dt.date(2026, 7, 21), "Voyage", "Vacances Portugal", 890, "Carte bancaire"),
             (dt.date(2026, 10, 4), "Gros achat", "Vélo", 420, "Carte bancaire")]
    rows.sort(key=lambda x: x[0])
    return rows


def build_tx(wb):
    ws = wb.create_sheet(TX)
    widths = {"B": 13, "C": 24, "D": 32, "E": 14, "F": 17, "G": 22, "H": 9, "I": 9}
    setup(ws, "🧾 Journal des transactions", "Une ligne = une opération • montant toujours positif • Type, Mois et Année se remplissent seuls", 9, N1 + 2, widths, tab="blue")
    card(ws, 5, 2, 8, N1 - 3, "Toutes les opérations", "blue")
    th(ws, 6, 2, ["Date", "Catégorie", "Description", "Montant", "Paiement", "Type (auto)", "Mois", "Année"], "blue")
    rows = sample_tx()
    cat, typ, _ = LISTS["cat_rng"]
    for i in range(N0, N1 + 1):
        k = i - N0
        v = rows[k] if k < len(rows) else (None,) * 5
        put(ws, i, 2, v[0], DATE, inp=True); put(ws, i, 3, v[1], inp=True); put(ws, i, 4, v[2], inp=True)
        put(ws, i, 5, v[3], EUR2, inp=True); put(ws, i, 6, v[4], inp=True)
        put(ws, i, 7, f'=IF(C{i}="","",IFERROR(INDEX({typ},MATCH(C{i},{cat},0)),"⚠ inconnue"))', color=MUTED, align=CENTER)
        put(ws, i, 8, f'=IF(B{i}="","",MONTH(B{i}))', "0", color=MUTED)
        put(ws, i, 9, f'=IF(B{i}="","",YEAR(B{i}))', "0", color=MUTED)
    dv_list(ws, LISTS["cat"], f"C{N0}:C{N1}", strict=True)
    dv_list(ws, LISTS["Paiement"], f"F{N0}:F{N1}")
    for t, c in TYPE_COL.items():
        ws.conditional_formatting.add(f"G{N0}:G{N1}", CellIsRule(operator="equal", formula=[f'"{t}"'], fill=fill(PAL[c][0]),
                                                                font=Font(name=FONT, color=PAL[c][2], size=9)))
    ws.conditional_formatting.add(f"B{N0}:F{N1}", FormulaRule(formula=[f'AND($B{N0}<>"",MOD(ROW(),2)=0)'], fill=fill("FAFAFC")))
    ws.freeze_panes = "A7"
    ws.auto_filter.ref = f"B6:I{N1}"
    return ws


# ===================================================================== Crédits
def build_credits(wb):
    ws = wb.create_sheet("Crédits")
    widths = {"B": 18, "C": 13, "D": 9, "E": 9, "F": 12, "G": 13, "H": 9, "I": 14, "J": 13, "K": 13, "L": 9, "M": 14, "N": 11}
    setup(ws, "🏦 Crédits & remboursements", "Saisis tes prêts : mensualité, capital restant, intérêts, date de fin et amortissement sont calculés", 14, 400, widths, tab="lav")
    card(ws, 5, 2, 13, 9, "Mes crédits", "lav")
    th(ws, 6, 2, ["Crédit", "Capital", "Taux", "Durée (mois)", "Début", "Mensualité", "Mois payés", "Capital restant",
                  "Remboursé (journal)", "Coût intérêts", "Fait", "Progression", "Fin"], "lav")
    for lr in LOAN_ROWS:
        i = lr - 7
        L = LOANS[i] if i < len(LOANS) else (None,) * 5
        put(ws, lr, 2, L[0], inp=True, bold=True); put(ws, lr, 3, L[1], EUR, inp=True); put(ws, lr, 4, L[2], "0.00%", inp=True)
        put(ws, lr, 5, L[3], "0", inp=True); put(ws, lr, 6, L[4], DATE, inp=True)
        put(ws, lr, 7, f'=IF(B{lr}="","",IF(D{lr}=0,C{lr}/E{lr},PMT(D{lr}/12,E{lr},-C{lr})))', EUR2)
        put(ws, lr, 8, f'=IF(B{lr}="","",MIN(E{lr},MAX(0,DATEDIF(F{lr},TODAY(),"m")+1)))', "0")
        put(ws, lr, 9, f'=IF(B{lr}="","",IF(H{lr}>=E{lr},0,IF(D{lr}=0,C{lr}-G{lr}*H{lr},-FV(D{lr}/12,H{lr},-G{lr},C{lr}))))', EUR, bold=True)
        put(ws, lr, 10, f'=IF(B{lr}="","",SUMIFS({TXE},{TXC},B{lr}))', EUR)
        put(ws, lr, 11, f'=IF(B{lr}="","",G{lr}*E{lr}-C{lr})', EUR)
        put(ws, lr, 12, f'=IF(B{lr}="","",1-I{lr}/C{lr})', PCT)
        barcell(ws, lr, 13, f"L{lr}", "lav", 10)
        put(ws, lr, 14, f'=IF(B{lr}="","",EDATE(F{lr},E{lr}))', "mm/yyyy")
    put(ws, 13, 2, "TOTAL", bold=True)
    for c in (3, 7, 9, 10, 11):
        put(ws, 13, c, f"=SUM({CL(c)}7:{CL(c)}12)", EUR, bold=True)
    put(ws, 13, 12, "=IFERROR(1-I13/C13,0)", PCT, bold=True)
    barcell(ws, 13, 13, "L13", "lav", 10)

    card(ws, 15, 2, 13, 4, "Synthèse dettes", "lav")
    kpi(ws, 16, 3, 2, "Capital restant dû", "=I13", EUR, PAL["pink"][2])
    kpi(ws, 16, 6, 2, "Mensualités / mois", "=G13", EUR)
    kpi(ws, 16, 9, 2, "Intérêts totaux", "=K13", EUR)
    kpi(ws, 16, 12, 3, "Libre de dettes le", "=IFERROR(MAX(N7:N12),\"\")", "mm/yyyy", PAL["green"][2])

    card(ws, 20, 2, 7, 368, "Tableau d'amortissement", "lav")
    put(ws, 21, 2, "Crédit affiché ▸", bold=True)
    put(ws, 21, 3, "Crédit auto", inp=True, bold=True, align=CENTER)
    ws.merge_cells("C21:D21")
    dv_list(ws, "=$B$7:$B$12", "C21")
    hl = [("Capital", "C", EUR), ("Taux", "D", "0.00%"), ("Durée", "E", "0"), ("Début", "F", DATE), ("Mensualité", "G", EUR2)]
    for i, (lab, col, fmt) in enumerate(hl):
        put(ws, 22, 2 + i, lab, color=MUTED, size=8, align=CENTER)
    for i, (lab, col, fmt) in enumerate(hl):
        put(ws, 23, 2 + i, f'=IFERROR(INDEX(${col}$7:${col}$12,MATCH($C$21,$B$7:$B$12,0)),0)', fmt, bold=True, align=CENTER)
    th(ws, 24, 2, ["N°", "Échéance", "Mensualité", "Intérêts", "Capital", "Restant dû", "Statut"], "lav")
    for k in range(1, 361):
        rr = 24 + k
        prev = "$B$23" if k == 1 else f"G{rr-1}"
        put(ws, rr, 2, f'=IF({k}<=$D$23,{k},"")', "0", size=8)
        put(ws, rr, 3, f'=IF(B{rr}="","",EDATE($E$23,B{rr}-1))', "mm/yyyy", size=8)
        put(ws, rr, 4, f'=IF(B{rr}="","",$F$23)', EUR2, size=8)
        put(ws, rr, 5, f'=IF(B{rr}="","",{prev}*$C$23/12)', EUR2, size=8)
        put(ws, rr, 6, f'=IF(B{rr}="","",D{rr}-E{rr})', EUR2, size=8)
        put(ws, rr, 7, f'=IF(B{rr}="","",MAX(0,{prev}-F{rr}))', EUR2, size=8)
        put(ws, rr, 8, f'=IF(B{rr}="","",IF(C{rr}<=TODAY(),"✓ Payé","À venir"))', size=8, align=CENTER)
    ws.conditional_formatting.add("H25:H384", CellIsRule(operator="equal", formula=['"✓ Payé"'], fill=fill(PAL["green"][0]),
                                                         font=Font(name=FONT, color=PAL["green"][2], size=8)))
    card(ws, 20, 10, 5, 18, "Capital restant dû", "lav")
    lc = LineChart()
    lc.add_data(Reference(ws, min_col=7, min_row=24, max_row=84), titles_from_data=True)
    lc.set_categories(Reference(ws, min_col=3, min_row=25, max_row=84))
    color_series(lc, [PAL["lav"][3]], line=True)
    lc.y_axis.numFmt = '#,##0 €'; lc.x_axis.number_format = "mm/yy"
    ws.add_chart(finish(lc, 11.5, 7.5, None, None), "J21")
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Placements
def build_placements(wb):
    ws = wb.create_sheet("Placements")
    widths = {"B": 18, "C": 15, "D": 13, "E": 14, "F": 13, "G": 13, "H": 11, "I": 11, "J": 13, "K": 9, "L": 14, "M": 13}
    setup(ws, "📈 Placements & épargne", "Versements tirés du journal • valeur actuelle à mettre à jour • projections par intérêts composés", 13, 70, widths, tab="mint")
    card(ws, 5, 2, 12, 9, "Mes placements", "mint")
    th(ws, 6, 2, ["Placement", "Type", "Solde 1er janv.", "Versé cette année", "Valeur actuelle", "Plus-value", "Perf.",
                  "Rendement /an", "Versement /mois", "Horizon (ans)", "Valeur projetée", "Dont intérêts"], "mint")
    for prr in PL_ROWS:
        i = prr - 7
        P = PLACES[i] if i < len(PLACES) else (None,) * 7
        put(ws, prr, 2, P[0], inp=True, bold=True); put(ws, prr, 3, P[1], inp=True); put(ws, prr, 4, P[2], EUR, inp=True)
        put(ws, prr, 5, f'=IF(B{prr}="","",SUMIFS({TXE},{TXC},B{prr},{TXI},{P_YEAR}))', EUR)
        put(ws, prr, 6, P[3], EUR, inp=True)
        put(ws, prr, 7, f'=IF(B{prr}="","",F{prr}-(D{prr}+E{prr}))', EUR)
        put(ws, prr, 8, f'=IF(B{prr}="","",IFERROR(G{prr}/(D{prr}+E{prr}),0))', PCT1)
        put(ws, prr, 9, P[4], "0.0%", inp=True); put(ws, prr, 10, P[5], EUR, inp=True); put(ws, prr, 11, P[6], "0", inp=True)
        put(ws, prr, 12, f'=IF(B{prr}="","",IF(I{prr}=0,F{prr}+J{prr}*K{prr}*12,FV(I{prr}/12,K{prr}*12,-J{prr},-F{prr})))', EUR, bold=True)
        put(ws, prr, 13, f'=IF(B{prr}="","",L{prr}-F{prr}-J{prr}*K{prr}*12)', EUR)
    put(ws, 13, 2, "TOTAL", bold=True)
    for c in (4, 5, 6, 7, 10, 12, 13):
        put(ws, 13, c, f"=SUM({CL(c)}7:{CL(c)}12)", EUR, bold=True)
    put(ws, 13, 8, "=IFERROR(G13/(D13+E13),0)", PCT1, bold=True)
    dv_list(ws, LISTS["Types placement"], "C7:C12")
    for rng in ("G7:H13",):
        ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], font=Font(name=FONT, color="3D8B57", bold=True)))
        ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, color="C2415D", bold=True)))

    goals = [("Fonds d'urgence (3 mois)", 6000, 4200), ("Vacances été", 1500, 900), ("Nouvelle voiture", 8000, 2100),
             ("Apport immobilier", 25000, 6400), ("Formation / certif", 1200, 650), ("Projet perso", 2000, 300)]
    card(ws, 15, 2, 6, 10, "Objectifs d'épargne", "green")
    th(ws, 16, 2, ["Objectif", "Cible", "Épargné", "%", "Progression", ""], "green")
    ws.merge_cells("F16:G16")
    for i, (g, t, s) in enumerate(goals):
        r = 17 + i
        put(ws, r, 2, g, inp=True); put(ws, r, 3, t, EUR, inp=True); put(ws, r, 4, s, EUR, inp=True)
        put(ws, r, 5, f'=IF(C{r}="","",IFERROR(D{r}/C{r},0))', PCT, bold=True)
        barcell(ws, r, 6, f"E{r}", "green", 14, merge=2)
    put(ws, 23, 2, "TOTAL", bold=True)
    put(ws, 23, 3, "=SUM(C17:C22)", EUR, bold=True); put(ws, 23, 4, "=SUM(D17:D22)", EUR, bold=True)
    put(ws, 23, 5, "=IFERROR(D23/C23,0)", PCT, bold=True); barcell(ws, 23, 6, "E23", "green", 14, merge=2)

    card(ws, 15, 9, 5, 10, "Répartition du patrimoine", "mint")
    pie = PieChart()
    pie.add_data(Reference(ws, min_col=6, min_row=7, max_row=12))
    pie.set_categories(Reference(ws, min_col=2, min_row=7, max_row=12))
    color_points(pie.series[0], CHART); pie.dataLabels = pie_labels()
    ws.add_chart(finish(pie, 11, 5.6, None, "r"), "I16")

    card(ws, 26, 2, 12, 24, "Projection du patrimoine sur 20 ans", "mint")
    th(ws, 27, 2, ["Année", "Valeur projetée"], "mint")
    for y in range(21):
        rr = 28 + y
        put(ws, rr, 2, YEAR + y, "0")
        put(ws, rr, 3, "=" + "+".join(
            f'IF(B{p}="",0,IF(I{p}=0,F{p}+J{p}*12*MIN({y},K{p}),FV(I{p}/12,{y}*12,-J{p},-F{p})))' for p in PL_ROWS), EUR)
    lc = LineChart()
    lc.add_data(Reference(ws, min_col=3, min_row=27, max_row=48), titles_from_data=True)
    lc.set_categories(Reference(ws, min_col=2, min_row=28, max_row=48))
    color_series(lc, [PAL["mint"][3]], line=True); lc.y_axis.numFmt = '#,##0 €'
    ws.add_chart(finish(lc, 21, 8.5, None, None), "E28")
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Récurrents
REC_IN = [("Salaire", "Chaque mois", 2450, dt.date(2026, 1, 1), None, "Compte courant", "Moi"),
          ("Side business", "Chaque mois", 300, dt.date(2026, 3, 15), None, "Compte pro", "Moi"),
          ("Prime semestrielle", "Tous les 6 mois", 600, dt.date(2026, 3, 20), None, "Compte courant", "Moi"),
          ("Mission freelance", "Une fois", 1200, dt.date(2026, 12, 10), None, "Compte pro", "Moi"),
          ("Cours particuliers", "Chaque semaine", 40, dt.date(2026, 9, 7), dt.date(2027, 6, 30), "Espèces", "Moi")]
REC_OUT = [("Loyer", "Chaque mois", 750, dt.date(2026, 1, 3), None, "Compte courant", "Logement"),
           ("Électricité / gaz", "Chaque mois", 70, dt.date(2026, 1, 5), None, "Compte courant", "Logement"),
           ("Internet + mobile", "Chaque mois", 45, dt.date(2026, 1, 6), None, "Compte courant", "Logement"),
           ("Assurances", "Chaque mois", 94, dt.date(2026, 1, 7), None, "Compte courant", "Assurance"),
           ("Abonnements", "Chaque mois", 64, dt.date(2026, 1, 4), None, "Carte", "Abonnements"),
           ("Crédit auto", "Chaque mois", 225.91, dt.date(2025, 3, 5), dt.date(2030, 2, 5), "Compte courant", "Crédit"),
           ("Prêt étudiant", "Chaque mois", 115.21, dt.date(2024, 9, 10), dt.date(2030, 8, 10), "Compte courant", "Crédit"),
           ("Épargne programmée", "Chaque mois", 400, dt.date(2026, 1, 2), None, "Livret / PEA", "Épargne"),
           ("Courses", "Chaque semaine", 85, dt.date(2026, 1, 5), None, "Carte", "Vie courante"),
           ("Taxe foncière / habitation", "Chaque année", 450, dt.date(2026, 10, 15), None, "Compte courant", "Impôts"),
           ("Entretien voiture", "Tous les 6 mois", 180, dt.date(2026, 4, 12), None, "Carte", "Transport")]


def rec_table(ws, r0, title, col, data, nrows):
    card(ws, r0, 2, 23, nrows + 3, title, col)
    heads = ["Source", "Fréquence", "Montant", "1er paiement", "Fin", "Compte", "Catégorie / qui", "≈ / mois", "Prochain", "Statut"] + MCOURT + ["Total année"]
    th(ws, r0 + 1, 2, heads, col)
    ft, fd, fm, fk = LISTS["freq_tbl"]
    first = r0 + 2
    for i in range(nrows):
        r = first + i
        v = data[i] if i < len(data) else (None,) * 7
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True, align=CENTER); put(ws, r, 4, v[2], EUR2, inp=True)
        put(ws, r, 5, v[3], DATE, inp=True); put(ws, r, 6, v[4], DATE, inp=True); put(ws, r, 7, v[5], inp=True); put(ws, r, 8, v[6], inp=True)
        # hidden helpers: Z = step days, AA = step months
        ws[f"Z{r}"] = f'=IFERROR(INDEX({fd},MATCH(C{r},{ft},0)),0)'
        ws[f"AA{r}"] = f'=IFERROR(INDEX({fm},MATCH(C{r},{ft},0)),0)'
        put(ws, r, 9, f'=IF(B{r}="","",IF(AND(F{r}<>"",F{r}<TODAY()),0,D{r}*IFERROR(INDEX({fk},MATCH(C{r},{ft},0)),0)))', EUR, bold=True)
        nxt_d = f'E{r}+CEILING(MAX(0,TODAY()-E{r})/Z{r},1)*Z{r}'
        n_m = f'CEILING(DATEDIF(E{r},TODAY(),"m")/AA{r},1)*AA{r}'
        nxt_m = f'IF(E{r}>=TODAY(),E{r},IF(EDATE(E{r},{n_m})>=TODAY(),EDATE(E{r},{n_m}),EDATE(E{r},{n_m}+AA{r})))'
        nxt = f'IF(Z{r}>0,{nxt_d},IF(AA{r}>0,{nxt_m},E{r}))'
        put(ws, r, 10, f'=IF(OR(B{r}="",E{r}=""),"",IF(OR({nxt}<TODAY(),AND(F{r}<>"",{nxt}>F{r})),"",{nxt}))', DATE)
        put(ws, r, 11, f'=IF(B{r}="","",IF(J{r}="","Terminé",IF(E{r}>TODAY(),"À venir","Actif")))', align=CENTER)
        for m in range(1, 13):
            c = 11 + m
            ms = f"DATE({P_YEAR},{m},1)"; me = f"EOMONTH({ms},0)"
            e = f'IF(F{r}="",{me},MIN(F{r},{me}))'
            days = f'D{r}*MAX(0,INT(({e}-E{r})/Z{r})-CEILING(MAX(0,{ms}-E{r})/Z{r},1)+1)'
            diff = f'((YEAR({ms})*12+{m})-(YEAR(E{r})*12+MONTH(E{r})))'
            mon = f'IF(AND({diff}>=0,MOD({diff},AA{r})=0,OR(F{r}="",DATE({P_YEAR},{m},MIN(DAY(E{r}),DAY({me})))<=F{r})),D{r},0)'
            once = f'IF(AND(E{r}>={ms},E{r}<={me}),D{r},0)'
            put(ws, r, c, f'=IF(OR(B{r}="",E{r}=""),"",IF(Z{r}>0,{days},IF(AA{r}>0,{mon},{once})))', EUR, size=8)
        put(ws, r, 24, f'=IF(B{r}="","",SUM(L{r}:W{r}))', EUR, bold=True)
    last = first + nrows - 1
    tr = last + 1
    put(ws, tr, 2, "TOTAL", bold=True)
    for c in [4, 9] + list(range(12, 25)):
        put(ws, tr, c, f"=SUM({CL(c)}{first}:{CL(c)}{last})", EUR, bold=True, bg=PAL[col][0])
    dv_list(ws, LISTS["freq"], f"C{first}:C{last}", strict=True)
    for st, cc in (("Actif", "green"), ("À venir", "blue"), ("Terminé", "grey")):
        ws.conditional_formatting.add(f"K{first}:K{last}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[cc][0]),
                                                                       font=Font(name=FONT, color=PAL[cc][2], size=9, bold=True)))
    fcols = {"Chaque semaine": "green", "Toutes les 2 semaines": "blue", "Toutes les 4 semaines": "blue", "Chaque mois": "lav",
             "Une fois": "pink", "Chaque année": "yellow", "Tous les 6 mois": "peach", "Chaque trimestre": "mint", "Tous les 2 mois": "mint"}
    for f, cc in fcols.items():
        ws.conditional_formatting.add(f"C{first}:C{last}", CellIsRule(operator="equal", formula=[f'"{f}"'], fill=fill(PAL[cc][0])))
    return first, last, tr


def build_recurrents(wb):
    ws = wb.create_sheet("Récurrents")
    widths = {"B": 22, "C": 19, "D": 11, "E": 11, "F": 10, "G": 15, "H": 14, "I": 11, "J": 11, "K": 9, "X": 12}
    for m in range(12): widths[CL(12 + m)] = 8.5
    setup(ws, "🔁 Revenus & paiements récurrents", "Saisis chaque flux une seule fois : fréquence, montant, dates — le planning sur 12 mois se calcule seul", 24, 60, widths, tab="lav")
    ws.column_dimensions["Z"].hidden = True; ws.column_dimensions["AA"].hidden = True
    i1, i2, it = rec_table(ws, 10, "Revenus récurrents", "green", REC_IN, 8)
    o1, o2, ot = rec_table(ws, it + 2, "Paiements récurrents", "peach", REC_OUT, 14)
    nr = ot + 2
    card(ws, nr, 2, 23, 3, "Net mensuel projeté (revenus − paiements)", "lav")
    put(ws, nr + 1, 2, "Net", bold=True)
    put(ws, nr + 1, 9, f"=I{it}-I{ot}", EUR, bold=True)
    for c in range(12, 25):
        put(ws, nr + 1, c, f"={CL(c)}{it}-{CL(c)}{ot}", EUR, bold=True)
    ws.conditional_formatting.add(f"I{nr+1}:X{nr+1}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, color="C2415D", bold=True)))
    # KPI band
    card(ws, 5, 2, 23, 4, "Vue d'ensemble", "lav")
    kpi(ws, 6, 3, 3, "Revenus / mois", f"=I{it}", EUR, PAL["green"][2])
    kpi(ws, 6, 7, 2, "Paiements / mois", f"=I{ot}", EUR, PAL["peach"][2])
    kpi(ws, 6, 10, 3, "Net / mois", f"=I{it}-I{ot}", EUR)
    kpi(ws, 6, 14, 4, "Prochain revenu", f'=IFERROR(SMALL(J{i1}:J{i2},1),"–")', DATE, PAL["lav"][2])
    kpi(ws, 6, 19, 3, "Prochain paiement", f'=IFERROR(SMALL(J{o1}:J{o2},1),"–")', DATE)
    kpi(ws, 6, 23, 2, "Flux actifs", f'=COUNTIF(K{i1}:K{o2},"Actif")', "0")
    ch = BarChart(); ch.type = "col"
    ch.add_data(Reference(ws, min_col=12, max_col=23, min_row=it), from_rows=True, titles_from_data=False)
    ch.add_data(Reference(ws, min_col=12, max_col=23, min_row=ot), from_rows=True, titles_from_data=False)
    from openpyxl.chart.series import SeriesLabel
    ch.series[0].tx = SeriesLabel(v="Revenus"); ch.series[1].tx = SeriesLabel(v="Paiements")
    ch.set_categories(Reference(ws, min_col=12, max_col=23, min_row=11))
    color_series(ch, [PAL["green"][3], PAL["peach"][3]]); ch.y_axis.numFmt = '#,##0 €'; ch.gapWidth = 60
    card(ws, nr + 4, 2, 23, 18, "Revenus vs paiements sur 12 mois", "lav")
    ws.add_chart(finish(ch, 30, 8), f"C{nr+5}")
    ws.freeze_panes = "C5"
    return ws


# ===================================================================== Budget (monthly)
def build_budget(wb):
    ws = wb.create_sheet("Budget")
    widths = {}
    for base in ("B", "H", "N", "T"):
        from openpyxl.utils import column_index_from_string as CI
        c = CI(base)
        widths[CL(c)] = 21; widths[CL(c + 1)] = 10; widths[CL(c + 2)] = 10; widths[CL(c + 3)] = 10; widths[CL(c + 4)] = 5
    for g in ("G", "M", "S"): widths[g] = 2
    setup(ws, "💶 Budget du mois", "Budget prévu vs réel par catégorie — le mois se choisit dans Paramètres", 24, 80, widths, tab="green")
    for c in ("Z", "AA", "AB", "AC"): ws.column_dimensions[c].hidden = True
    cat, typ, bud = LISTS["cat_rng"]
    M = P_MONTH; Y = P_YEAR

    def real(name_ref):
        return sumtx((TXC, name_ref), (TXH, M), (TXI, Y))

    # month title + KPI
    ws.merge_cells("B5:F6")
    t = ws["B5"]; t.value = "=UPPER(" + MONTH_NAME.format(m=M) + '&" "&' + Y + ")"
    t.font = font(16, True, INK); t.alignment = CENTER
    s = Side(style="thin", color=BOXLINE)
    for r in (5, 6):
        for c in range(2, 7):
            ws.cell(r, c).fill = fill("ECEDF1")
            ws.cell(r, c).border = Border(top=s if r == 5 else None, bottom=s if r == 6 else None, left=s if c == 2 else None, right=s if c == 6 else None)
    ws.row_dimensions[5].height = 22; ws.row_dimensions[6].height = 22

    # boxes ---------------------------------------------------------
    def box(r0, c0, title, col, names_rows, revenue=False):
        n = len(names_rows)
        card(ws, r0, c0, 5, n + 3, title, col)
        th(ws, r0 + 1, c0, ["Catégorie", "Budget", "Réel", "Écart", "✓"], col)
        for i, prow in enumerate(names_rows):
            r = r0 + 2 + i
            put(ws, r, c0, f"='{PA}'!B{prow}")
            put(ws, r, c0 + 1, f"=N('{PA}'!D{prow})", EUR2)
            put(ws, r, c0 + 2, f'=IF({CL(c0)}{r}="",0,{real(f"{CL(c0)}{r}")})', EUR2)
            d = f"{CL(c0+2)}{r}-{CL(c0+1)}{r}" if revenue else f"{CL(c0+1)}{r}-{CL(c0+2)}{r}"
            put(ws, r, c0 + 3, f"={d}", EUR2)
            if revenue:
                put(ws, r, c0 + 4, f'=IF({CL(c0+2)}{r}=0,"",IF({CL(c0+2)}{r}>={CL(c0+1)}{r},"✓","…"))', align=CENTER, bold=True)
            else:
                put(ws, r, c0 + 4, f'=IF({CL(c0+2)}{r}=0,"",IF({CL(c0+2)}{r}<={CL(c0+1)}{r},"✓","⚠"))', align=CENTER, bold=True)
        tr = r0 + 2 + n
        put(ws, tr, c0, "Total", bold=True, bg=PAL[col][0])
        for k in (1, 2, 3):
            put(ws, tr, c0 + k, f"=SUM({CL(c0+k)}{r0+2}:{CL(c0+k)}{tr-1})", EUR2, bold=True, bg=PAL[col][0])
        put(ws, tr, c0 + 4, None, bg=PAL[col][0])
        rng = f"{CL(c0+3)}{r0+2}:{CL(c0+3)}{tr}"
        ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, color="C2415D", bold=True)))
        ws.conditional_formatting.add(f"{CL(c0+4)}{r0+2}:{CL(c0+4)}{tr}", CellIsRule(operator="equal", formula=['"✓"'], fill=fill(PAL["green"][0]), font=Font(name=FONT, color=PAL["green"][2], bold=True)))
        ws.conditional_formatting.add(f"{CL(c0+4)}{r0+2}:{CL(c0+4)}{tr}", CellIsRule(operator="equal", formula=['"⚠"'], fill=fill(PAL["pink"][0]), font=Font(name=FONT, color="C2415D", bold=True)))
        return tr

    rows_of = lambda t: [CAT_ROW[n] for n, ty, b in CATS if ty == t]
    R1 = 15
    # Summary by type
    card(ws, R1, 2, 5, len(TYPES) + 4, "Résumé du budget", "grey")
    th(ws, R1 + 1, 2, ["Type", "Budget", "Réel", "Écart", "✓"], "grey")
    SUMROW = {}
    for i, t in enumerate(TYPES):
        r = R1 + 2 + i; SUMROW[t] = r
        put(ws, r, 2, t, bold=True, color=PAL[TYPE_COL[t]][2])
        put(ws, r, 3, f'=SUMIFS({bud},{typ},B{r})', EUR2)
        put(ws, r, 4, "=" + sumtx((TXG, f"B{r}"), (TXH, M), (TXI, Y)), EUR2)
        put(ws, r, 5, f"=D{r}-C{r}" if t == "Revenu" else f"=C{r}-D{r}", EUR2)
        put(ws, r, 6, f'=IF(D{r}=0,"",IF({"D%d>=C%d" % (r, r) if t == "Revenu" else "D%d<=C%d" % (r, r)},"✓","⚠"))', align=CENTER, bold=True)
    rl = R1 + 2 + len(TYPES)
    put(ws, rl, 2, "Reste à budgéter", bold=True, bg=PAL["grey"][0])
    put(ws, rl, 3, f"=C{SUMROW['Revenu']}-SUM(C{SUMROW['Charges fixes']}:C{SUMROW['Épargne & placement']})", EUR2, bold=True, bg=PAL["grey"][0])
    put(ws, rl, 4, f"=D{SUMROW['Revenu']}-SUM(D{SUMROW['Charges fixes']}:D{SUMROW['Épargne & placement']})", EUR2, bold=True, bg=PAL["grey"][0])
    for c in (5, 6): put(ws, rl, c, None, bg=PAL["grey"][0])
    ws.conditional_formatting.add(f"E{R1+2}:E{rl}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, color="C2415D", bold=True)))
    ws.conditional_formatting.add(f"F{R1+2}:F{rl}", CellIsRule(operator="equal", formula=['"⚠"'], fill=fill(PAL["pink"][0]), font=Font(name=FONT, color="C2415D", bold=True)))
    ws.conditional_formatting.add(f"F{R1+2}:F{rl}", CellIsRule(operator="equal", formula=['"✓"'], fill=fill(PAL["green"][0]), font=Font(name=FONT, color=PAL["green"][2], bold=True)))

    t_fix = box(R1, 8, "Charges fixes", "peach", rows_of("Charges fixes"))
    t_cur = box(R1, 14, "Dépenses courantes", "blue", rows_of("Dépense courante"))
    t_sav = box(R1, 20, "Épargne & placements", "mint", LISTS["pl_cat_rows"])
    R2 = max(rl, t_fix, t_cur, t_sav) + 2
    t_rev = box(R2, 2, "Revenus", "green", rows_of("Revenu"), revenue=True)
    t_sub = box(R2, 8, "Abonnements", "pink", rows_of("Abonnement"))
    t_ach = box(R2, 14, "Achats & crédits", "yellow", rows_of("Achat unitaire") + LISTS["loan_cat_rows"])

    # top 5 spending categories (hidden helper Z/AA)
    exp_rows = [CAT_ROW[n] for n, ty, b in CATS if ty not in ("Revenu",)] + LISTS["loan_cat_rows"]
    for i, prow in enumerate(exp_rows):
        r = 6 + i
        ws[f"Z{r}"] = f"='{PA}'!B{prow}"
        ws[f"AA{r}"] = f'=IF(Z{r}="",0,{real(f"Z{r}")})+ROW()/1000000'
    hl = 6 + len(exp_rows) - 1
    card(ws, R2, 20, 5, 9, "Top 5 dépenses du mois", "lav")
    th(ws, R2 + 1, 20, ["Catégorie", "Dépensé", "% du total", "", ""], "lav")
    ws.merge_cells(start_row=R2 + 1, start_column=23, end_row=R2 + 1, end_column=24)
    ws.cell(R2 + 1, 23).value = "PART"
    tot_out = f"SUM(D{SUMROW['Charges fixes']}:D{SUMROW['Remboursement crédit']})"
    for k in range(1, 6):
        r = R2 + 1 + k
        put(ws, r, 21, f"=ROUND(LARGE($AA$6:$AA${hl},{k}),2)", EUR2, bold=True)
        put(ws, r, 20, f'=IF(U{r}<=0,"–",INDEX($Z$6:$Z${hl},MATCH(LARGE($AA$6:$AA${hl},{k}),$AA$6:$AA${hl},0)))')
        put(ws, r, 22, f"=IFERROR(U{r}/{tot_out},0)", PCT1)
        barcell(ws, r, 23, f"V{r}*2", "lav", 10, merge=2)
    put(ws, R2 + 7, 20, "Total dépensé", bold=True, bg=PAL["lav"][0])
    put(ws, R2 + 7, 21, f"={tot_out}", EUR2, bold=True, bg=PAL["lav"][0])
    for c in (22, 23, 24): put(ws, R2 + 7, c, None, bg=PAL["lav"][0])

    # KPIs under title
    rev = f"D{SUMROW['Revenu']}"; out = f"SUM(D{SUMROW['Charges fixes']}:D{SUMROW['Remboursement crédit']})"
    sav = f"D{SUMROW['Épargne & placement']}"
    kpi(ws, 8, 2, 2, "Total revenus", f"={rev}", EUR2, PAL["green"][2])
    kpi(ws, 8, 5, 2, "Total dépenses", f"={out}", EUR2, PAL["peach"][2])
    kpi(ws, 11, 2, 2, "Reste à dépenser", f"={rev}-{out}-{sav}", EUR2)
    kpi(ws, 11, 5, 2, "Reste à budgéter", f"=C{rl}", EUR2, PAL["lav"][2])
    for c in (4,):
        pass

    # daily balance helper (AB:AC) + charts
    for d in range(1, 32):
        r = 6 + d - 1
        dd = f"MIN(DATE({Y},{M},{d}),EOMONTH(DATE({Y},{M},1),0))"
        ws[f"AB{r}"] = d
        ws[f"AC{r}"] = (f'=SUMIFS({TXE},{TXG},"Revenu",{TXB},">="&DATE({Y},{M},1),{TXB},"<="&{dd})'
                        f'-SUMIFS({TXE},{TXG},"<>Revenu",{TXB},">="&DATE({Y},{M},1),{TXB},"<="&{dd})')
    ws["AC5"] = "Solde cumulé"
    card(ws, 5, 8, 5, 9, "Évolution du solde", "grey", size=9)
    lc = LineChart()
    lc.add_data(Reference(ws, min_col=29, min_row=5, max_row=36), titles_from_data=True)
    lc.set_categories(Reference(ws, min_col=28, min_row=6, max_row=36))
    color_series(lc, [PAL["blue"][3]], line=True); lc.y_axis.numFmt = '#,##0 €'
    ws.add_chart(finish(lc, 10.8, 4.6, None, None), "H6")
    card(ws, 5, 14, 5, 9, "Répartition des dépenses", "grey", size=9)
    pie = PieChart()
    pie.add_data(Reference(ws, min_col=4, min_row=SUMROW["Charges fixes"], max_row=SUMROW["Épargne & placement"]))
    pie.set_categories(Reference(ws, min_col=2, min_row=SUMROW["Charges fixes"], max_row=SUMROW["Épargne & placement"]))
    color_points(pie.series[0], [PAL[TYPE_COL[t]][3] for t in TYPES[1:]]); pie.dataLabels = pie_labels()
    ws.add_chart(finish(pie, 10.8, 4.6, None, "r"), "N6")
    card(ws, 5, 20, 5, 9, "Budget vs réel", "grey", size=9)
    bc = BarChart(); bc.type = "col"
    bc.add_data(Reference(ws, min_col=3, max_col=4, min_row=R1 + 1, max_row=SUMROW["Épargne & placement"]), titles_from_data=True)
    bc.set_categories(Reference(ws, min_col=2, min_row=R1 + 2, max_row=SUMROW["Épargne & placement"]))
    color_series(bc, [PAL["lav"][3], PAL["peach"][3]]); bc.y_axis.numFmt = '#,##0 €'; bc.gapWidth = 50
    ws.add_chart(finish(bc, 10.8, 4.6, None, "t"), "T6")
    ws.freeze_panes = "A5"
    LISTS["budget"] = dict(rev=f"Budget!{rev}", out=f"Budget!D{SUMROW['Charges fixes']}", sumrow=SUMROW, rl=rl)
    return ws


# ===================================================================== Finances (annual)
def build_finances(wb):
    ws = wb.create_sheet("Finances")
    widths = {"B": 26, "O": 12, "P": 11}
    setup(ws, "📊 Finances — vue annuelle", "Synthèse automatique de l'année à partir du journal", 16, 75, widths, default_w=9.5, tab="green")
    Y = P_YEAR
    MR = 15
    card(ws, MR - 1, 2, 15, len(TYPES) + 7, "Synthèse mensuelle", "green")
    th(ws, MR, 2, ["Poste"] + MCOURT + ["Total", "Moy."], "green")
    for j, t in enumerate(TYPES):
        r = MR + 1 + j
        put(ws, r, 2, t, bold=True, color=PAL[TYPE_COL[t]][2])
        for m in range(1, 13):
            put(ws, r, 2 + m, "=" + sumtx((TXG, f"$B{r}"), (TXH, m), (TXI, Y)), EUR, size=8)
        put(ws, r, 15, f"=SUM(C{r}:N{r})", EUR, bold=True, bg=PAL["green"][0])
        put(ws, r, 16, f'=IFERROR(O{r}/MAX(1,COUNTIF($C${MR+1}:$N${MR+1},">0")),0)', EUR, bg=PAL["green"][0])
    rr = MR + 1; rS = MR + 1 + len(TYPES); rN = rS + 1; rT = rS + 2
    labels = [(rS, "Total dépenses (hors épargne)", f"SUM({{c}}{rr+1}:{{c}}{rr+5})"),
              (rN, "Reste (non affecté)", f"{{c}}{rr}-{{c}}{rS}-{{c}}{rr+6}"),
              (rT, "Taux d'épargne", f"IFERROR(({{c}}{rr+6}+{{c}}{rN})/{{c}}{rr},0)")]
    for r, lab, f in labels:
        put(ws, r, 2, lab, bold=True, bg="F6F6F9")
        for c in range(3, 17):
            put(ws, r, c, "=" + f.format(c=CL(c)), PCT1 if r == rT else EUR, bold=True, size=8, bg="F6F6F9")
    ws.conditional_formatting.add(f"C{rN}:P{rN}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, color="C2415D", bold=True)))
    card(ws, 5, 2, 15, 8, "Indicateurs clés de l'année", "green")
    k1 = [("Revenus", f"=O{rr}", EUR, PAL["green"][2]), ("Dépenses", f"=O{rS}", EUR, PAL["peach"][2]),
          ("Épargné / investi", f"=O{rr+6}", EUR, PAL["mint"][2]), ("Taux d'épargne", f"=O{rT}", PCT1, PAL["lav"][2]),
          ("Reste / mois", f"=P{rN}", EUR, INK)]
    k2 = [("Patrimoine placé", "=Placements!F13", EUR, PAL["mint"][2]), ("Plus-values", "=Placements!G13", EUR, PAL["green"][2]),
          ("Capital restant dû", "=Crédits!I13", EUR, PAL["pink"][2]), ("Patrimoine net", "=Placements!F13-Crédits!I13", EUR, INK),
          ("Objectif épargne", f"={P_SAVE}", PCT, PAL["lav"][2])]
    cols = [(2, 1), (4, 2), (7, 2), (10, 2), (13, 3)]
    for i, (lab, f, fmt, colr) in enumerate(k1):
        kpi(ws, 6, cols[i][0], cols[i][1], lab, f, fmt, colr)
    for i, (lab, f, fmt, colr) in enumerate(k2):
        kpi(ws, 9, cols[i][0], cols[i][1], lab, f, fmt, colr)
    cr0 = rT + 3
    card(ws, cr0, 2, 7, 18, "Revenus vs dépenses vs épargne", "green")
    ch = BarChart(); ch.type = "col"
    for r in (rr, rS, rr + 6):
        ch.add_data(Reference(ws, min_col=2, max_col=14, min_row=r), from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=3, max_col=14, min_row=MR))
    color_series(ch, [PAL["green"][3], PAL["peach"][3], PAL["mint"][3]]); ch.y_axis.numFmt = '#,##0 €'; ch.gapWidth = 60
    ws.add_chart(finish(ch, 13.5, 8), f"B{cr0+1}")
    card(ws, cr0, 10, 7, 18, "Où part l'argent", "green")
    st = BarChart(); st.type = "col"; st.grouping = "stacked"; st.overlap = 100
    for r in range(rr + 1, rr + 6):
        st.add_data(Reference(ws, min_col=2, max_col=14, min_row=r), from_rows=True, titles_from_data=True)
    st.set_categories(Reference(ws, min_col=3, max_col=14, min_row=MR))
    color_series(st, [PAL[TYPE_COL[t]][3] for t in TYPES[1:6]]); st.y_axis.numFmt = '#,##0 €'; st.gapWidth = 60
    ws.add_chart(finish(st, 13.5, 8), f"J{cr0+1}")
    ws.freeze_panes = "A5"
    LISTS["fin"] = dict(rT=rT, rr=rr)
    return ws
