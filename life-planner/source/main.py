import sys, json
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.styles import Alignment, Border, Side
from common import *
import finance as FI
import life as LI

OUT = sys.argv[1]
GS = sys.argv[2]

wb = Workbook()
acc = wb.active; acc.title = "Accueil"
pa = FI.build_params(wb)
tx = FI.build_tx(wb)
cr = FI.build_credits(wb)
pl = FI.build_placements(wb)
rec = FI.build_recurrents(wb)
bud = FI.build_budget(wb)
fin = FI.build_finances(wb)
go = LI.build_goals(wb)
hab = LI.build_habits(wb)
wbs = LI.build_wellbeing(wb)
sp = LI.build_sport(wb)
nu = LI.build_nutrition(wb)
me = LI.build_mental(wb)
pro = LI.build_pro(wb)
ta = LI.build_tasks(wb)
pn = LI.build_planning(wb)
guide = wb.create_sheet("Guide")
REF = LI.REF

# ===================================================================== Accueil
ws = acc
widths = {"H": 2, "O": 2, "V": 2, "AD": 40}
setup(ws, "🌿 Life planning dashboard", "Ton tableau de bord de vie : argent, objectifs, santé, mental et carrière — tout se met à jour automatiquement",
      28, 72, widths, default_w=8.6, tab="peach")
# greeting
ws.merge_cells("B5:AB5"); ws.merge_cells("B6:AB6")
g = ws["B5"]; g.value = f'="Bonjour "&{FI.P_NAME}&" 👋  —  "&' + LI.DOW.format(d="TODAY()") + '&" "&DAY(TODAY())&" "&' + FI.MONTH_NAME.format(m="MONTH(TODAY())") + '&" "&YEAR(TODAY())'
g.font = font(14, True, INK); g.alignment = CENTER
quotes = ["La discipline est le pont entre les objectifs et la réussite.", "Petit à petit, l'oiseau fait son nid.",
          "Ce que tu fais chaque jour compte plus que ce que tu fais de temps en temps.", "Le meilleur moment pour commencer, c'était hier. Le deuxième, c'est maintenant.",
          "Prends soin de ton corps, c'est le seul endroit où tu es obligé de vivre.", "Investis en toi : c'est le placement le plus rentable.",
          "Un objectif sans plan n'est qu'un souhait.", "Tu n'as pas à être parfait, juste meilleur qu'hier.", "La constance bat le talent.",
          "Le succès est la somme de petits efforts répétés jour après jour."]
for i, q in enumerate(quotes):
    ws[f"AD{10+i}"] = q
ws.column_dimensions["AD"].hidden = True
q = ws["B6"]; q.value = f'="« "&INDEX($AD$10:$AD${9+len(quotes)},MOD(DAY(TODAY()),{len(quotes)})+1)&" »"'
q.font = font(9, False, MUTED, True); q.alignment = CENTER
s = Side(style="thin", color=BOXLINE)
for r in (5, 6):
    for c in range(2, 29):
        x = ws.cell(r, c); x.fill = fill(WHITE)
        x.border = Border(top=s if r == 5 else None, bottom=s if r == 6 else None, left=s if c == 2 else None, right=s if c == 28 else None)
ws.row_dimensions[5].height = 30; ws.row_dimensions[6].height = 20; ws.row_dimensions[7].height = 10

B = FI.LISTS["budget"]["sumrow"]
H = 34
SEC = [(2, "💰 Finances", "green"), (9, "🎯 Objectifs & tâches", "peach"), (16, "🌸 Bien-être", "pink"), (23, "💼 Pro & apprentissage", "blue")]
for c, t, col in SEC:
    card(ws, 8, c, 6, H, t, col, size=11)


def kp2(r, c, a, b, col):
    kpi(ws, r, c, 3, a[0], a[1], a[2], a[3] if len(a) > 3 else INK, big=13)
    kpi(ws, r, c + 3, 3, b[0], b[1], b[2], b[3] if len(b) > 3 else INK, big=13)


def listrow(r, c, label, pct, col, label_ref=False):
    put(ws, r, c, label, size=8)
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + 2)
    barcell(ws, r, c + 3, pct, col, 9, merge=2)
    put(ws, r, c + 5, f"=IFERROR({pct},0)", PCT, bold=True, size=8)


# --- Finances
c = 2
subcard(ws, 9, c, 6, '="Budget · "&' + FI.R(FI.PA, "$C$10") if False else "Budget du mois", "green")
ws.cell(9, c).value = '="BUDGET · "&UPPER(' + FI.R(FI.PA, "$C$10") + ")"
kp2(10, c, ("Revenus du mois", "=Budget!B9", EUR, PAL["green"][2]), ("Dépenses du mois", "=Budget!E9", EUR, PAL["peach"][2]), "green")
subcard(ws, 12, c, 6, "Budget consommé", "green")
pct_b = f"Budget!E9/MAX(1,SUM(Budget!C{B['Charges fixes']}:C{B['Remboursement crédit']}))"
barcell(ws, 13, c, pct_b, "green", 22, merge=4)
put(ws, 13, c + 4, f"=IFERROR({pct_b},0)", PCT, bold=True, align=CENTER); ws.merge_cells(start_row=13, start_column=c + 4, end_row=13, end_column=c + 5)
kp2(14, c, ("Reste à dépenser", "=Budget!B12", EUR), ("Taux d'épargne (an)", f"=Finances!O{FI.LISTS['fin']['rT']}", PCT1, PAL["lav"][2]), "green")
subcard(ws, 16, c, 6, "Patrimoine", "green")
kp2(17, c, ("Patrimoine net", "=Placements!F13-Crédits!I13", EUR, PAL["mint"][2]), ("Capital restant dû", "=Crédits!I13", EUR, PAL["pink"][2]), "green")
subcard(ws, 19, c, 6, "Objectifs d'épargne", "green")
for i in range(6):
    listrow(20 + i, c, f"=Placements!B{17+i}", f"Placements!E{17+i}", "green")
subcard(ws, 26, c, 6, "Échéances", "green")
kp2(27, c, ("Libre de dettes le", "=Crédits!L17", "mm/yyyy", PAL["green"][2]), ("Prochain revenu", "=Récurrents!N7", DATE), "green")
subcard(ws, 29, c, 6, "Accès rapide", "green")
for i, (t, tg) in enumerate([("Budget", "Budget"), ("Journal", "Transactions"), ("Récurrents", "Récurrents"), ("Crédits", "Crédits"),
                             ("Placements", "Placements"), ("Vue annuelle", "Finances")]):
    link(ws, 30 + i // 2 * 2, c + (i % 2) * 3, 3, "→ " + t, tg, "green")

# --- Objectifs & tâches
c = 9
subcard(ws, 9, c, 6, "Objectifs par domaine", "peach")
for i, r in enumerate(REF["dom_rows"]):
    listrow(10 + i, c, f"=Objectifs!B{r}", f"Objectifs!D{r}", "peach")
subcard(ws, 19, c, 6, "Aujourd'hui", "peach")
ws.merge_cells(start_row=20, start_column=c, end_row=21, end_column=c + 1)
x = ws.cell(20, c, "=DAY(TODAY())"); x.font = font(22, True, INK); x.alignment = CENTER
for r in (20, 21):
    for cc in (c, c + 1): ws.cell(r, cc).fill = fill("ECEDF1")
put(ws, 20, c + 2, "=" + LI.DOW.format(d="TODAY()").replace('"Lun"', '"Lundi"').replace('"Mar"', '"Mardi"').replace('"Mer"', '"Mercredi"').replace('"Jeu"', '"Jeudi"').replace('"Ven"', '"Vendredi"').replace('"Sam"', '"Samedi"').replace('"Dim"', '"Dimanche"'), bold=True, size=11, line=False)
put(ws, 21, c + 2, "=" + FI.MONTH_NAME.format(m="MONTH(TODAY())") + '&" "&YEAR(TODAY())', color=MUTED, line=False)
put(ws, 22, c, "🎯 TÂCHE PRINCIPALE", bold=True, size=7, color=PAL["peach"][2], line=False)
ws.merge_cells(start_row=22, start_column=c, end_row=22, end_column=c + 5)
put(ws, 23, c, f"={REF['today']['main']}", bold=True, align=CENTER, bg=PAL["peach"][0]); ws.merge_cells(start_row=23, start_column=c, end_row=23, end_column=c + 5)
subcard(ws, 24, c, 6, "Top 3 priorités", "peach")
for i, (t, d) in enumerate(REF["today"]["tops"]):
    r = 25 + i
    put(ws, r, c, f'=IF(OR({d}="✓",{d}=TRUE),"✓","○")', align=CENTER, bold=True, color=PAL["green"][2])
    put(ws, r, c + 1, f"={t}"); ws.merge_cells(start_row=r, start_column=c + 1, end_row=r, end_column=c + 5)
subcard(ws, 28, c, 6, "Tâches", "peach")
kp2(29, c, ("Terminées", f"={REF['tasks']['pct']}", PCT, PAL["green"][2]), ("En retard", f"={REF['tasks']['late']}", "0", "C2415D"), "peach")
kp2(31, c, ("Aujourd'hui", f"={REF['tasks']['today']}", "0", PAL["peach"][2]), ("7 prochains jours", f"={REF['tasks']['week']}", "0"), "peach")
for i, (t, tg) in enumerate([("Objectifs", "Objectifs"), ("Tâches", "Tâches"), ("Planning", "Planning"), ("Habitudes", "Habitudes")]):
    link(ws, 34 + i // 2 * 2, c + (i % 2) * 3, 3, "→ " + t, tg, "peach")

# --- Bien-être
c = 16
w = REF["wb"]
subcard(ws, 9, c, 6, "Ce mois-ci", "pink")
kp2(10, c, ("Sommeil moyen", f"={w['sleep']}", '0.0" h"', PAL["blue"][2]), ("Humeur", "=" + LI.emoji_mood(w["mood"]), None), "pink")
kp2(12, c, ("Pas / jour", f"={w['steps']}", NUM, PAL["green"][2]), ("Sport", f"={w['sport_total']}", '0" min"', PAL["peach"][2]), "pink")
subcard(ws, 14, c, 6, "Habitudes", "pink")
kp2(15, c, ("Progression", f"={REF['hab_pct']}", PCT, PAL["lav"][2]), ("Meilleure série", f"={REF['hab_best']}", '0" j"', PAL["yellow"][2]), "pink")
subcard(ws, 17, c, 6, "Repas du jour", "pink")
mc = {"Petit-déjeuner": "peach", "Déjeuner": "green", "Dîner": "yellow", "Collations": "pink"}
for i, (m, ref) in enumerate(REF["meals"]):
    r = 18 + i
    put(ws, r, c, m.upper(), bold=True, size=7, align=CENTER, bg=PAL[mc[m]][0], color=PAL[mc[m]][2])
    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + 1)
    put(ws, r, c + 2, f"={ref}", align=CENTER, size=8); ws.merge_cells(start_row=r, start_column=c + 2, end_row=r, end_column=c + 5)
subcard(ws, 22, c, 6, "Sport cette semaine", "pink")
kp2(23, c, ("Séances réalisées", f"={REF['sport']['done']}", "0", PAL["green"][2]), ("Prévues", f"={REF['sport']['planned']}", "0"), "pink")
subcard(ws, 25, c, 6, "Courses", "pink")
kp2(26, c, ("Articles à acheter", f"={REF['grocery']['tobuy']}", "0", PAL["yellow"][2]), ("Budget restant", f"={REF['grocery']['budget']}", EUR), "pink")
subcard(ws, 28, c, 6, "Mental", "pink")
kp2(29, c, ("Entrées journal", f"={REF['mental']['entries']}", "0", PAL["lav"][2]), ("Stress moyen", f"={w['stress']}", '0.0" / 5"'), "pink")
for i, (t, tg) in enumerate([("Bien-être", "Bien-être"), ("Sport", "Sport"), ("Nutrition", "Nutrition"), ("Mental", "Mental")]):
    link(ws, 32 + i // 2 * 2, c + (i % 2) * 3, 3, "→ " + t, tg, "pink")

# --- Pro
c = 23
p = REF["pro"]
subcard(ws, 9, c, 6, "Projets", "blue")
kp2(10, c, ("Projets actifs", f"={p['active']}", "0", PAL["blue"][2]), ("Avancement moyen", f"={p['avg']}", PCT), "blue")
pb, pe, pi, p1, p2 = REF["proj"]
for i in range(6):
    listrow(12 + i, c, f'=IF(Pro!B{p1+i}="","",Pro!B{p1+i})', f"N(Pro!I{p1+i})", "blue")
subcard(ws, 18, c, 6, "Apprentissage", "blue")
kp2(19, c, ("Heures de formation", f"={p['hours']}", '0" h"'), ("Livres lus", f"={p['books']}", "0", PAL["green"][2]), "blue")
subcard(ws, 21, c, 6, "Compétences (niveau / cible)", "blue")
sn, sd, se, s0 = REF["skills"]
for i in range(6):
    listrow(22 + i, c, f'=IF(Pro!B{s0+i}="","",Pro!B{s0+i})', f"IFERROR(Pro!D{s0+i}/Pro!E{s0+i},0)", "blue")
subcard(ws, 28, c, 6, "Réseau", "blue")
kp2(29, c, ("Contacts à relancer", f"={p['relance']}", "0", "C2415D"), ("Roue de la vie", "=Objectifs!C16", '0.0" / 10"', PAL["peach"][2]), "blue")
link(ws, 32, c, 3, "→ Pro", "Pro", "blue"); link(ws, 32, c + 3, 3, "→ Paramètres", "Paramètres", "blue")
link(ws, 34, c, 3, "→ Guide", "Guide", "blue"); link(ws, 34, c + 3, 3, "→ Objectifs", "Objectifs", "blue")

# --- charts row
CR = 8 + H + 1
for i, (cc, t, col) in enumerate([(2, "Cash-flow de l'année", "green"), (9, "Habitudes réalisées / jour", "peach"),
                                   (16, "Humeur & énergie du mois", "pink"), (23, "Avancement des projets", "blue")]):
    card(ws, CR, cc, 6, 16, t, col)
rT = FI.LISTS["fin"]["rr"]
ch = BarChart(); ch.type = "col"
ch.add_data(Reference(fin, min_col=2, max_col=14, min_row=rT), from_rows=True, titles_from_data=True)
ch.add_data(Reference(fin, min_col=2, max_col=14, min_row=rT + 7), from_rows=True, titles_from_data=True)
ch.set_categories(Reference(fin, min_col=3, max_col=14, min_row=15))
color_series(ch, [PAL["green"][3], PAL["peach"][3]]); ch.y_axis.numFmt = '#,##0'; ch.gapWidth = 50
ws.add_chart(finish(ch, 11, 7), f"B{CR+1}")
lc = LineChart()
lc.add_data(Reference(hab, min_col=4, max_col=34, min_row=39), from_rows=True, titles_from_data=False)
lc.set_categories(Reference(hab, min_col=4, max_col=34, min_row=18))
color_series(lc, [PAL["peach"][3]], line=True)
ws.add_chart(finish(lc, 11, 7, None, None), f"I{CR+1}")
mc_ = LineChart()
for col in (6, 8):
    mc_.add_data(Reference(wbs, min_col=col, min_row=20, max_row=w["D1"]), titles_from_data=True)
mc_.set_categories(Reference(wbs, min_col=2, min_row=w["D0"], max_row=w["D1"])); mc_.x_axis.number_format = "dd"
color_series(mc_, [PAL["pink"][3], PAL["yellow"][3]], line=True)
ws.add_chart(finish(mc_, 11, 7), f"P{CR+1}")
pc = BarChart(); pc.type = "bar"
pc.add_data(Reference(pro, min_col=9, min_row=p1, max_row=p1 + 5), titles_from_data=False)
pc.set_categories(Reference(pro, min_col=2, min_row=p1, max_row=p1 + 5))
color_series(pc, [PAL["blue"][3]]); pc.y_axis.numFmt = "0%"; pc.y_axis.scaling.max = 1; pc.gapWidth = 40
ws.add_chart(finish(pc, 11, 7, None, None), f"W{CR+1}")
ws.freeze_panes = "A5"

# ===================================================================== Guide
widths = {"B": 24, "C": 70, "D": 40}
setup(guide, "📘 Guide d'utilisation", "Tout ce qu'il faut savoir pour utiliser ton Life Planner en 5 minutes", 4, 60, widths, tab="yellow")
card(guide, 5, 2, 3, 22, "Les onglets", "yellow")
th(guide, 6, 2, ["Onglet", "À quoi il sert", "Ce que tu remplis"], "yellow")
tabs = [("🌿 Accueil", "Vue d'ensemble de ta vie : finances, objectifs, tâches, bien-être, pro. Rien à saisir.", "—"),
        ("🎯 Objectifs", "Roue de la vie, objectifs mesurables avec progression et statut auto, vision, jalons.", "Notes /10, objectifs, valeurs actuelles"),
        ("✅ Habitudes", "20 habitudes × 31 jours, semaines colorées, séries, top 10, progression hebdo.", "✓ chaque jour"),
        ("☑️ Tâches", "Calendrier, Eisenhower, tâches du jour / à venir, statuts et priorités.", "La liste des tâches (bas de page)"),
        ("🗓️ Planning", "Semaine type colorée, time blocking du jour, top 3, événements, routines.", "Créneaux, priorités, routines"),
        ("🌸 Bien-être", "Sommeil, humeur, énergie, stress, eau, pas, sport, méditation, poids.", "Une ligne par jour"),
        ("💪 Sport", "Programme, prévu vs réalisé, records, mensurations, journal d'entraînement.", "Séances, records, mensurations"),
        ("🥗 Nutrition", "Menu de la semaine, repas du jour, liste de courses par rayon, recettes.", "Menu, articles, ✓ acheté"),
        ("🧠 Mental", "Journal (gratitude, victoire, leçon), revue hebdo, valeurs, gestion du stress.", "Journal du jour, revue du dimanche"),
        ("💼 Pro", "Projets, compétences, formations, lectures, réseau avec relances auto.", "Avancement, heures, pages"),
        ("💶 Budget", "Budget prévu vs réel du mois par catégorie, top 5 dépenses, graphiques.", "Budgets dans Paramètres"),
        ("📊 Finances", "Vue annuelle mois par mois, taux d'épargne, patrimoine.", "—"),
        ("🧾 Transactions", "Journal de toutes les opérations : le type se déduit de la catégorie.", "Date, catégorie, montant"),
        ("🔁 Récurrents", "Revenus & paiements récurrents (hebdo, mensuel, annuel…) projetés sur 12 mois.", "Fréquence, montant, dates"),
        ("🏦 Crédits", "Mensualités, capital restant, intérêts, date de liberté, amortissement.", "Capital, taux, durée, début"),
        ("📈 Placements", "Plus-values, objectifs d'épargne, projection sur 20 ans.", "Valeur actuelle, objectifs"),
        ("⚙️ Paramètres", "Prénom, année, MOIS AFFICHÉ, catégories, budgets et listes déroulantes.", "Mois à afficher, budgets")]
for i, (a, b, c2) in enumerate(tabs):
    r = 7 + i
    put(guide, r, 2, a, bold=True); put(guide, r, 3, b, align=LEFTW); put(guide, r, 4, c2, color=PAL["blue"][2])
    guide.row_dimensions[r].height = 22
card(guide, 28, 2, 3, 12, "Règles d'or", "green")
rules = [("Texte bleu", "Case à remplir. Texte noir = formule automatique (ne pas écraser)."),
         ("Mois affiché", "Change le mois dans Paramètres (C8) : Budget, Habitudes, Bien-être, Mental et Calendrier suivent."),
         ("✓ = fait", "Dans les colonnes à cocher, choisis ✓ dans la liste. Le menu 🌿 Planner peut les transformer en vraies cases à cocher."),
         ("Montants", "Toujours positifs dans le journal : la catégorie décide si c'est un revenu ou une dépense."),
         ("Nouvelle catégorie", "Ajoute-la dans les lignes libres de Paramètres avec son type et son budget."),
         ("Nouveau mois", "Menu 🌿 Planner → « Nouveau mois » pour vider la grille d'habitudes et le journal mental."),
         ("Données d'exemple", "Tout est pré-rempli pour te montrer le rendu : remplace par tes infos ou vide les cases bleues."),
         ("Google Sheets", "Fichier importé : Fichier → Enregistrer au format Google Sheets, puis Extensions → Apps Script pour le menu.")]
for i, (a, b) in enumerate(rules):
    r = 29 + i
    put(guide, r, 2, a, bold=True, color=PAL["green"][2]); put(guide, r, 3, b, align=LEFTW)
    guide.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    guide.row_dimensions[r].height = 22
card(guide, 41, 2, 3, 10, "Routine conseillée", "pink")
rout = [("Chaque jour (5 min)", "Habitudes ✓ · Bien-être (1 ligne) · Journal mental · Dépenses du jour · Top 3 du lendemain"),
        ("Chaque semaine (20 min)", "Revue hebdo (Mental) · Tâches de la semaine · Menu + courses · Prévu vs réalisé (Sport)"),
        ("Chaque mois (30 min)", "Budget vs réel · Valeur des placements · Objectifs (valeurs actuelles) · Nouveau mois"),
        ("Chaque trimestre", "Roue de la vie · Jalons · Compétences · Réajuster les budgets"),
        ("Chaque année", "Vision & mot de l'année · Nouveaux objectifs · Changer l'année dans Paramètres")]
for i, (a, b) in enumerate(rout):
    r = 42 + i
    put(guide, r, 2, a, bold=True, color=PAL["pink"][2]); put(guide, r, 3, b, align=LEFTW)
    guide.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    guide.row_dimensions[r].height = 22

# ===================================================================== order + ghost columns
order = ["Accueil", "Objectifs", "Habitudes", "Tâches", "Planning", "Bien-être", "Sport", "Nutrition", "Mental", "Pro",
         "Budget", "Finances", "Transactions", "Récurrents", "Crédits", "Placements", "Paramètres", "Guide"]
wb._sheets = [wb[n] for n in order]
wb.active = 0


def ghost(ws, cols, rows):
    for col in cols:
        ws.column_dimensions[col].hidden = False
        ws.column_dimensions[col].width = 0.7
        for r in range(1, rows):
            x = ws[f"{col}{r}"]
            x.font = font(1, color=BG); x.fill = fill(BG)


ghost(bud, ["AB", "AC"], 40)
ghost(hab, ["AO"], 45)
ghost(ta, ["Y", "AA"], 130)
for n in order:
    wb[n].sheet_view.tabSelected = (n == "Accueil")
wb.save(OUT)

# ===================================================================== Apps Script
ranges = json.dumps([[s, r] for s, r in CHECK_RANGES], ensure_ascii=False)
import os
gs = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps_script_template.js")).read().replace("__CHECK_RANGES__", ranges)
open(GS, "w").write(gs)
print("saved", OUT, len(CHECK_RANGES), "check ranges")
