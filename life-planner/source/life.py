import random, datetime as dt, calendar
from openpyxl.chart import BarChart, PieChart, LineChart, RadarChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.formatting.rule import CellIsRule, FormulaRule, ColorScaleRule
from openpyxl.styles import Font, Alignment, Border, Side
from common import *
from finance import P_YEAR, P_MONTH, P_NAME, LISTS, MONTH_NAME, MOIS

REF = {}
NDAYS = f"DAY(EOMONTH(DATE({P_YEAR},{P_MONTH},1),0))"
DOW = 'CHOOSE(WEEKDAY({d},2),"Lun","Mar","Mer","Jeu","Ven","Sam","Dim")'
DOMAINS = [("💼", "Carrière"), ("💰", "Finances"), ("💪", "Santé & sport"), ("🧠", "Mental"), ("❤️", "Relations"),
           ("📚", "Apprentissage"), ("🏡", "Maison"), ("🎨", "Loisirs"), ("🌍", "Contribution")]
RED_TXT = "C2415D"


def emoji_mood(ref):
    return f'IF(N({ref})=0,"",CHOOSE(MAX(1,MIN(5,ROUND({ref},0))),"😞","🙁","😐","🙂","😄"))'


# ===================================================================== Objectifs
def build_goals(wb):
    ws = wb.create_sheet("Objectifs")
    widths = {"B": 30, "C": 15, "D": 20, "E": 10, "F": 10, "G": 10, "H": 9, "I": 14, "J": 12, "K": 10, "L": 15, "M": 28}
    setup(ws, "🎯 Objectifs & vision", "Roue de la vie, objectifs mesurables et jalons — tout se met à jour avec tes valeurs actuelles", 13, 90, widths, tab="peach")
    # Wheel of life
    card(ws, 5, 2, 5, 12, "Roue de la vie (note sur 10)", "peach")
    th(ws, 6, 2, ["Domaine", "Note actuelle", "Objectif", "Écart", "Niveau"], "peach")
    notes = [6, 7, 6, 5, 8, 7, 6, 5, 4]
    for i, (e, d) in enumerate(DOMAINS):
        r = 7 + i
        put(ws, r, 2, f"{e}  {d}", bold=True)
        put(ws, r, 3, notes[i], "0", inp=True); put(ws, r, 4, 9, "0", inp=True)
        put(ws, r, 5, f"=D{r}-C{r}", "0")
        barcell(ws, r, 6, f"C{r}/10", "peach", 10)
    put(ws, 16, 2, "Moyenne", bold=True, bg=PAL["peach"][0])
    put(ws, 16, 3, "=AVERAGE(C7:C15)", NUM1, bold=True, bg=PAL["peach"][0]); put(ws, 16, 4, "=AVERAGE(D7:D15)", NUM1, bold=True, bg=PAL["peach"][0])
    put(ws, 16, 5, "=D16-C16", NUM1, bold=True, bg=PAL["peach"][0]); put(ws, 16, 6, None, bg=PAL["peach"][0])
    card(ws, 5, 8, 6, 12, "Équilibre de vie", "peach")
    rc = RadarChart(); rc.type = "filled"
    rc.add_data(Reference(ws, min_col=3, max_col=4, min_row=6, max_row=15), titles_from_data=True)
    rc.set_categories(Reference(ws, min_col=2, min_row=7, max_row=15))
    color_series(rc, [PAL["peach"][3], PAL["blue"][1]])
    rc.y_axis.delete = True
    rc.width, rc.height = 13, 6.3; rc.legend.position = "b"
    ws.add_chart(rc, "H6")

    # Goals table
    G0 = 31
    goals = [
        ("Obtenir une promotion / nouveau poste", "Carrière", "Étapes validées", 0, 5, 3, dt.date(2026, 12, 31), "Préparer l'entretien annuel"),
        ("Épargner 6 000 € de fonds d'urgence", "Finances", "€ épargnés", 2000, 6000, 4200, dt.date(2026, 12, 31), "Virement auto +50 €"),
        ("Courir un semi-marathon", "Santé & sport", "km en continu", 5, 21, 14, dt.date(2027, 4, 15), "Sortie longue dimanche"),
        ("Perdre 5 kg", "Santé & sport", "kg", 82, 77, 78.6, dt.date(2026, 12, 31), "Suivi repas 5j/7"),
        ("Méditer 200 sessions", "Mental", "sessions", 0, 200, 141, dt.date(2026, 12, 31), "Méditation au réveil"),
        ("Lire 24 livres", "Apprentissage", "livres", 0, 24, 17, dt.date(2026, 12, 31), "20 pages / soir"),
        ("Atteindre B2 en anglais", "Apprentissage", "% du programme", 0, 100, 62, dt.date(2027, 6, 30), "Cours 3×/semaine"),
        ("Voir mes proches 2×/mois", "Relations", "rencontres", 0, 24, 19, dt.date(2026, 12, 31), "Planifier dîner famille"),
        ("Lancer mon side business", "Finances", "€ de CA / mois", 0, 1000, 420, dt.date(2027, 3, 31), "Nouvelle offre en ligne"),
        ("Aménager le bureau", "Maison", "tâches", 0, 8, 6, dt.date(2026, 12, 15), "Acheter lampe"),
        ("Bénévolat 20 h", "Contribution", "heures", 0, 20, 7, dt.date(2026, 12, 31), "Inscription asso"),
        ("Apprendre la guitare (10 morceaux)", "Loisirs", "morceaux", 0, 10, 4, dt.date(2027, 6, 30), "15 min / jour"),
    ]
    NG = 25
    card(ws, G0, 2, 12, NG + 2, "Mes objectifs mesurables", "peach")
    th(ws, G0 + 1, 2, ["Objectif", "Domaine", "Indicateur", "Départ", "Cible", "Actuel", "%", "Progression", "Échéance", "Jours rest.", "Statut", "Prochaine étape"], "peach")
    for i in range(NG):
        r = G0 + 2 + i
        g = goals[i] if i < len(goals) else (None,) * 8
        put(ws, r, 2, g[0], inp=True, bold=True); put(ws, r, 3, g[1], inp=True); put(ws, r, 4, g[2], inp=True)
        put(ws, r, 5, g[3], NUM1, inp=True); put(ws, r, 6, g[4], NUM1, inp=True); put(ws, r, 7, g[5], NUM1, inp=True)
        put(ws, r, 8, f'=IF(B{r}="","",IFERROR(MIN(1,MAX(0,(G{r}-E{r})/(F{r}-E{r}))),0))', PCT, bold=True)
        barcell(ws, r, 9, f"H{r}", "peach", 12)
        put(ws, r, 10, g[6], DATE, inp=True)
        put(ws, r, 11, f'=IF(OR(B{r}="",J{r}=""),"",MAX(0,J{r}-TODAY()))', "0")
        exp = f"MIN(1,MAX(0,(TODAY()-DATE({P_YEAR},1,1))/MAX(1,J{r}-DATE({P_YEAR},1,1))))"
        put(ws, r, 12, f'=IF(B{r}="","",IF(H{r}>=1,"✅ Atteint",IF(AND(J{r}<>"",J{r}<TODAY()),"⏰ En retard",IF(H{r}>={exp}*0.75,"🟢 En bonne voie","🟠 À accélérer"))))', align=CENTER, size=8)
        put(ws, r, 13, g[7], inp=True)
    gl = G0 + 1 + NG
    dv_list(ws, LISTS["Domaines de vie"], f"C{G0+2}:C{gl}")
    for txt, c in (("✅", "green"), ("⏰", "pink"), ("🟢", "mint"), ("🟠", "yellow")):
        ws.conditional_formatting.add(f"L{G0+2}:L{gl}", FormulaRule(formula=[f'LEFT(L{G0+2},1)="{txt}"'], fill=fill(PAL[c][0])))
    REF["goals"] = (f"$C${G0+2}:$C${gl}", f"$H${G0+2}:$H${gl}", f"$B${G0+2}:$B${gl}")

    # progress by domain
    card(ws, 18, 2, 5, 12, "Progression par domaine", "peach")
    th(ws, 19, 2, ["Domaine", "Objectifs", "Moyenne", "Progression", ""], "peach")
    ws.merge_cells("E19:F19")
    dc, dp, dn = REF["goals"]
    REF["dom_rows"] = []
    for i, (e, d) in enumerate(DOMAINS):
        r = 20 + i
        put(ws, r, 2, f"{e}  {d}", bold=True)
        put(ws, r, 3, f'=COUNTIF({dc},"{d}")', "0")
        put(ws, r, 4, f'=IFERROR(AVERAGEIF({dc},"{d}",{dp}),0)', PCT, bold=True)
        barcell(ws, r, 5, f"D{r}", "peach", 14, merge=2)
        REF["dom_rows"].append(r)
    card(ws, 18, 8, 6, 12, "Vision de l'année", "yellow")
    vis = [("Mot de l'année", "Discipline"), ("Vision en une phrase", "Être en forme, serein et libre financièrement."),
           ("Priorité n°1", "Santé : bouger chaque jour"), ("Priorité n°2", "Finances : fonds d'urgence complet"),
           ("Priorité n°3", "Carrière : monter en compétences"), ("Pourquoi c'est important", "Avoir le choix et du temps pour mes proches."),
           ("Ce que j'arrête", "Scroller le soir"), ("Ce que je commence", "Deep work le matin"),
           ("Récompense si objectifs atteints", "Voyage au Japon")]
    for i, (k, v) in enumerate(vis):
        r = 19 + i
        put(ws, r, 8, k, bold=True, color=PAL["yellow"][2], size=8)
        put(ws, r, 9, None)
        ws.merge_cells(start_row=r, start_column=8, end_row=r, end_column=9)
        put(ws, r, 10, v, inp=True)
        for j in range(11, 14): put(ws, r, j, None)
        ws.merge_cells(start_row=r, start_column=10, end_row=r, end_column=13)

    J0 = gl + 3
    card(ws, J0, 2, 7, 20, "Jalons trimestriels", "peach")
    th(ws, J0 + 1, 2, ["Jalon", "Objectif lié", "Trimestre", "", "", "Échéance", "Fait"], "peach")
    jal = [("Entretien annuel préparé", "Carrière", "T4", dt.date(2026, 12, 5), "✓"), ("10 km sous 55 min", "Santé & sport", "T4", dt.date(2026, 11, 30), ""),
           ("5 000 € épargnés", "Finances", "T4", dt.date(2026, 12, 15), ""), ("Site du side business en ligne", "Finances", "T1", dt.date(2027, 1, 31), ""),
           ("Examen blanc anglais", "Apprentissage", "T1", dt.date(2027, 2, 15), ""), ("Semi-marathon inscrit", "Santé & sport", "T1", dt.date(2027, 1, 10), "✓")]
    for i in range(17):
        r = J0 + 2 + i
        j = jal[i] if i < len(jal) else (None,) * 5
        put(ws, r, 2, j[0], inp=True); put(ws, r, 3, j[1], inp=True); put(ws, r, 4, j[2], inp=True, align=CENTER)
        put(ws, r, 5, None); put(ws, r, 6, None)
        put(ws, r, 7, j[3], DATE, inp=True); put(ws, r, 8, j[4], inp=True, align=CENTER)
    dv_list(ws, '"T1,T2,T3,T4"', f"D{J0+2}:D{J0+18}")
    checks(ws, f"H{J0+2}:H{J0+18}", "peach")
    card(ws, J0, 10, 4, 6, "Jalons", "peach")
    kpi(ws, J0 + 1, 10, 2, "Validés", f'={count_done(f"H{J0+2}:H{J0+18}")}', "0", PAL["green"][2])
    kpi(ws, J0 + 1, 12, 2, "Restants", f'=COUNTIF(B{J0+2}:B{J0+18},"?*")-{count_done(f"H{J0+2}:H{J0+18}")}', "0")
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Habitudes
HABITS = [("⏰ Lever 6h30", 30, .8), ("💧 Boire 2 L d'eau", 30, .85), ("🏃 Sport 30 min", 20, .6), ("🧘 Méditation 10 min", 30, .75),
          ("📖 Lire 20 pages", 30, .7), ("📵 Pas d'écran avant de dormir", 30, .55), ("✍️ Journal / gratitude", 30, .7),
          ("🚶 10 000 pas", 25, .65), ("🥗 5 fruits & légumes", 30, .6), ("🍬 Pas de sucre ajouté", 25, .5),
          ("🗣️ Langue 30 min", 25, .65), ("🎯 Deep work 2 h", 22, .6), ("📱 Pas de réseaux avant midi", 30, .5),
          ("🤸 Étirements", 20, .55), ("🧹 Ranger 10 min", 30, .7), ("📞 Appeler un proche", 8, .3),
          ("💶 Noter mes dépenses", 30, .75), ("😴 Coucher avant 23 h", 30, .6), ("🚿 Douche froide", 15, .4), ("🗓️ Planifier demain", 30, .75)]
WEEKS = [(1, 7, "peach"), (8, 14, "pink"), (15, 21, "blue"), (22, 28, "yellow"), (29, 31, "green")]


def build_habits(wb):
    ws = wb.create_sheet("Habitudes")
    widths = {"B": 30, "C": 8, "AI": 7, "AJ": 7, "AK": 7, "AL": 12, "AM": 7, "AN": 7}
    for d in range(1, 32): widths[CL(3 + d)] = 3.6
    setup(ws, "✅ Suivi des habitudes", "Mets ✓ chaque jour réalisé • les semaines sont colorées • séries et top 10 calculés automatiquement", 40, 75, widths, tab="lav")
    H0 = 19; NH = 20; H1 = H0 + NH - 1
    for c in range(42, 74): ws.column_dimensions[CL(c)].hidden = True
    ws.column_dimensions["AO"].hidden = True
    ws["AO5"] = "=" + NDAYS
    ws["AO6"] = f"=IF(AND({P_MONTH}=MONTH(TODAY()),{P_YEAR}=YEAR(TODAY())),DAY(TODAY()),AO5)"
    # KPI block
    card(ws, 5, 2, 2, 9, "Ce mois-ci", "lav")
    put(ws, 6, 2, "=UPPER(" + MONTH_NAME.format(m=P_MONTH) + '&" "&' + P_YEAR + ")", bold=True, align=CENTER, color=PAL["lav"][2], size=11)
    ws.merge_cells("B6:C6")
    rows = [("Habitudes complétées", f"=SUM(AI{H0}:AI{H1})", "0", "green"), ("Restantes à faire", f"=SUM(AJ{H0}:AJ{H1})", "0", "peach"),
            ("Jours dans le mois", "=AO5", "0", "blue"), ("Progression globale", f"=IFERROR(SUM(AI{H0}:AI{H1})/SUM(C{H0}:C{H1}),0)", PCT, "lav"),
            ("Meilleure série", f"=MAX(AN{H0}:AN{H1})", '0" j"', "yellow"), ("Habitudes suivies", f'=COUNTIF(B{H0}:B{H1},"?*")', "0", "pink")]
    for i, (lab, f, fmt, c) in enumerate(rows):
        r = 7 + i
        put(ws, r, 2, lab.upper(), bold=True, size=8, bg=PAL[c][0], color=PAL[c][2])
        put(ws, r, 3, f, fmt, bold=True, size=11, align=CENTER)
        ws.row_dimensions[r].height = 22
    REF["hab_pct"] = "Habitudes!$C$10"; REF["hab_best"] = "Habitudes!$C$11"
    # line chart of daily completion
    card(ws, 5, 4, 31, 9, "Habitudes réalisées par jour", "lav")
    card(ws, 5, 35, 6, 9, "Progression du mois", "lav")
    ws["AO8"] = f"=SUM(AI{H0}:AI{H1})"; ws["AO9"] = f"=MAX(0,SUM(C{H0}:C{H1})-AO8)"
    put(ws, 12, 35, "=C10", PCT, bold=True, size=14, color=PAL["lav"][2], align=CENTER, line=False)
    ws.merge_cells("AI12:AN12")
    # week header
    card(ws, 15, 2, 39, NH + 9, "Vue mensuelle", "lav")
    th(ws, 18, 2, ["Habitude", "Objectif"], "lav")
    for a, b, col in WEEKS:
        c1, c2 = 3 + a, 3 + b
        ws.merge_cells(start_row=17, start_column=c1, end_row=17, end_column=c2)
        x = ws.cell(17, c1, f"SEMAINE {WEEKS.index((a, b, col)) + 1}")
        x.font = font(8, True, PAL[col][2]); x.alignment = CENTER
        for c in range(c1, c2 + 1):
            ws.cell(17, c).fill = fill(PAL[col][0])
            ws.cell(17, c).border = Border(top=side(col), bottom=side(col))
    ws.merge_cells("B17:C17"); ws["B17"].value = "SEMAINES"; ws["B17"].font = font(8, True, PAL["lav"][2]); ws["B17"].alignment = CENTER
    for d in range(1, 32):
        c = 3 + d
        col = [w[2] for w in WEEKS if w[0] <= d <= w[1]][0]
        x = ws.cell(18, c, f'=IF({d}<=$AO$5,{d},"")'); x.font = font(8, True, PAL[col][2]); x.alignment = CENTER
        x.fill = fill(PAL[col][0])
        y = ws.cell(16, c, f'=IF({d}<=$AO$5,LEFT({DOW.format(d=f"DATE({P_YEAR},{P_MONTH},{d})")},1),"")')
        y.font = font(7, True, MUTED); y.alignment = CENTER
    th(ws, 18, 35, ["Fait", "Reste", "%", "Progression", "Série", "Record"], "lav")
    random.seed(3)
    for i in range(NH):
        r = H0 + i
        h = HABITS[i] if i < len(HABITS) else (None, None, 0)
        put(ws, r, 2, h[0], inp=True, bold=True); put(ws, r, 3, h[1], "0", inp=True)
        for d in range(1, 32):
            c = 3 + d
            v = "✓" if (h[0] and d < TODAY.day and random.random() < h[2]) or (h[0] and d == TODAY.day and random.random() < h[2] * .5) else None
            x = put(ws, r, c, v, align=CENTER, size=9, inp=True)
            x.border = Border(left=Side(style="thin", color="EEEEF2"), right=Side(style="thin", color="EEEEF2"), bottom=GRID)
            hc = 41 + d  # helper streak AP..
            prev = "0" if d == 1 else f"{CL(hc-1)}{r}"
            ws.cell(r, hc, f"=IF({done(f'{CL(c)}{r}')},{prev}+1,0)")
        rng = f"D{r}:AH{r}"
        put(ws, r, 35, f'=IF(B{r}="","",{count_done(rng)})', "0", bold=True)
        put(ws, r, 36, f'=IF(B{r}="","",MAX(0,C{r}-AI{r}))', "0")
        put(ws, r, 37, f'=IF(B{r}="","",IFERROR(AI{r}/C{r},0))', PCT, bold=True)
        barcell(ws, r, 38, f"AK{r}", "lav", 10)
        hr = f"$AP{r}:$BT{r}"
        put(ws, r, 39, f'=IF(B{r}="","",IF(INDEX({hr},1,$AO$6)>0,INDEX({hr},1,$AO$6),IF($AO$6>1,INDEX({hr},1,$AO$6-1),0)))', "0", align=CENTER)
        put(ws, r, 40, f'=IF(B{r}="","",MAX({hr}))', "0", align=CENTER, bold=True)
        ws[f"AO{r}"] = f'=IF(B{r}="",-1,N(AK{r}))+ROW()/1000000'
    ws.column_dimensions["AO"].hidden = True
    ws.conditional_formatting.add(f"D{H0}:AH{H1}", FormulaRule(formula=["D$18=\"\""], fill=fill("EFEFF3"), stopIfTrue=True))
    for a, b, col in WEEKS:
        checks(ws, f"{CL(3+a)}{H0}:{CL(3+b)}{H1}", col)
    ws.conditional_formatting.add(f"AK{H0}:AK{H1}", CellIsRule(operator="greaterThanOrEqual", formula=["1"], font=Font(name=FONT, color="3D8B57", bold=True)))
    # daily totals
    rT = H1 + 1; rP = H1 + 2; rW = H1 + 3; rB = H1 + 4
    put(ws, rT, 2, "Complétées / jour", bold=True, bg=SUBHEAD); put(ws, rP, 2, "% du jour", bold=True, bg=SUBHEAD)
    put(ws, rW, 2, "Progression hebdo", bold=True, bg=SUBHEAD); put(ws, rB, 2, "", bg=SUBHEAD)
    for d in range(1, 32):
        c = 3 + d
        put(ws, rT, c, f'=IF({CL(c)}$18="","",{count_done(f"{CL(c)}{H0}:{CL(c)}{H1}")})', "0", size=8, align=CENTER)
        put(ws, rP, c, f'=IF({CL(c)}$18="","",IFERROR({CL(c)}{rT}/$C$12,0))', PCT, size=7, align=CENTER)
    for a, b, col in WEEKS:
        c1, c2 = 3 + a, 3 + b
        rng_t = f"{CL(c1)}{rT}:{CL(c2)}{rT}"; rng_d = f"{CL(c1)}18:{CL(c2)}18"
        put(ws, rW, c1, f"=IFERROR(SUM({rng_t})/($C$12*COUNT({rng_d})),0)", PCT, bold=True, align=CENTER, color=PAL[col][2], bg=PAL[col][0])
        ws.merge_cells(start_row=rW, start_column=c1, end_row=rW, end_column=c2)
        put(ws, rB, c1, bar(f"{CL(c1)}{rW}", 6 if b - a > 3 else 3), color=PAL[col][3], size=8, align=CENTER)
        ws.merge_cells(start_row=rB, start_column=c1, end_row=rB, end_column=c2)
    ws.conditional_formatting.add(f"D{rT}:AH{rT}", ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF", end_type="num", end_value=20, end_color=PAL["lav"][3]))
    lc = LineChart()
    lc.add_data(Reference(ws, min_col=4, max_col=34, min_row=rT), from_rows=True, titles_from_data=False)
    lc.set_categories(Reference(ws, min_col=4, max_col=34, min_row=18))
    color_series(lc, [PAL["peach"][3]], line=True)
    ws.add_chart(finish(lc, 25, 4.3, None, None), "D6")
    donut(ws, "AI6", Reference(ws, min_col=41, min_row=8, max_row=9), Reference(ws, min_col=41, min_row=8, max_row=9),
          [PAL["lav"][3], "ECEDF1"], w=5.6, h=3.4)
    # Top 10
    T0 = rB + 2
    card(ws, T0, 2, 2, 13, "Top 10 du mois", "lav")
    th(ws, T0 + 1, 2, ["Habitude", "%"], "lav")
    for k in range(1, 11):
        r = T0 + 1 + k
        put(ws, r, 2, f'=IFERROR(IF(LARGE($AO${H0}:$AO${H1},{k})<0,"",{k}&". "&INDEX($B${H0}:$B${H1},MATCH(LARGE($AO${H0}:$AO${H1},{k}),$AO${H0}:$AO${H1},0))),"")', size=9)
        put(ws, r, 3, f'=IFERROR(IF(LARGE($AO${H0}:$AO${H1},{k})<0,"",ROUND(LARGE($AO${H0}:$AO${H1},{k}),2)),"")', PCT, bold=True)
    card(ws, T0, 4, 37, 13, "Progression par semaine", "lav")
    for i, (a, b, col) in enumerate(WEEKS):
        c1 = 3 + a
        put(ws, T0 + 2, 6 + i * 6, f"SEMAINE {i+1}", bold=True, align=CENTER, color=PAL[col][2], bg=PAL[col][0], size=8)
        ws.merge_cells(start_row=T0 + 2, start_column=6 + i * 6, end_row=T0 + 2, end_column=10 + i * 6)
        put(ws, T0 + 3, 6 + i * 6, f"={CL(c1)}{rW}", PCT, bold=True, align=CENTER, size=14, color=PAL[col][2])
        ws.merge_cells(start_row=T0 + 3, start_column=6 + i * 6, end_row=T0 + 3, end_column=10 + i * 6)
        ws.row_dimensions[T0 + 3].height = 30
        put(ws, T0 + 4, 6 + i * 6, f'=SUM({CL(c1)}{rT}:{CL(3+b)}{rT})&" réalisées"', align=CENTER, color=MUTED, size=8)
        ws.merge_cells(start_row=T0 + 4, start_column=6 + i * 6, end_row=T0 + 4, end_column=10 + i * 6)
    note(ws, T0 + 6, 5, "Astuce : menu 💰 Planner → « Nouveau mois » vide la grille ; « Activer les cases à cocher » transforme les ✓ en vraies cases Google Sheets.", 30)
    ws.freeze_panes = "D5"
    return ws


# ===================================================================== Bien-être
def build_wellbeing(wb):
    ws = wb.create_sheet("Bien-être")
    widths = {"B": 11, "C": 7, "D": 9, "E": 9, "F": 9, "G": 6, "H": 9, "I": 9, "J": 8, "K": 9, "L": 9, "M": 10, "N": 9, "O": 9, "P": 34}
    setup(ws, "🌸 Bien-être quotidien", "Sommeil, humeur, énergie, hydratation, activité — une ligne par jour (mois choisi dans Paramètres)", 16, 100, widths, tab="pink")
    D0 = 21; D1 = D0 + 30
    card(ws, 19, 2, 15, 35, "Journal quotidien", "pink")
    th(ws, 20, 2, ["Date", "Jour", "Sommeil (h)", "Qualité /5", "Humeur /5", "", "Énergie /5", "Stress /5", "Eau (L)", "Pas",
                   "Sport (min)", "Méditation (min)", "Écran (h)", "Poids (kg)", "Note du jour"], "pink")
    random.seed(5)
    notes_txt = ["Bonne journée productive", "Fatigué après le sport", "Soirée entre amis", "Journée calme", "Stress au travail",
                 "Super séance de sport", "Lecture au parc", "Bien dormi", "Rendez-vous médical", "Journée créative", "Repas en famille", "Petite baisse d'énergie"]
    for d in range(1, 32):
        r = D0 + d - 1
        put(ws, r, 2, f'=IF({d}<={NDAYS},DATE({P_YEAR},{P_MONTH},{d}),"")', DATE)
        put(ws, r, 3, f'=IF(B{r}="","",{DOW.format(d=f"B{r}")})', align=CENTER, color=MUTED)
        filled = d < TODAY.day
        vals = [round(random.uniform(6, 8.6) * 2) / 2, random.randint(3, 5), random.randint(3, 5), None, random.randint(2, 5),
                random.randint(1, 4), round(random.uniform(1.4, 2.6), 1), random.randint(5200, 13500), random.choice([0, 0, 30, 45, 60]),
                random.choice([0, 10, 10, 15]), round(random.uniform(1.5, 4.5), 1), round(82 - 0.12 * d - 3.2 + random.uniform(-0.4, 0.4), 1),
                notes_txt[d % len(notes_txt)]] if filled else [None] * 13
        fm = [NUM1, "0", "0", None, "0", "0", NUM1, NUM, "0", "0", NUM1, NUM1, None]
        for j, (v, f) in enumerate(zip(vals, fm)):
            c = 4 + j
            if c == 7:
                put(ws, r, c, "=" + emoji_mood(f"F{r}"), align=CENTER)
            else:
                put(ws, r, c, v, f, inp=True, align=CENTER if f else LEFT)
    for col in ("E", "F", "H"):
        ws.conditional_formatting.add(f"{col}{D0}:{col}{D1}", ColorScaleRule(start_type="num", start_value=1, start_color="F9DDE7",
                                                                              mid_type="num", mid_value=3, mid_color="FBF1CC", end_type="num", end_value=5, end_color="DDEFD9"))
    ws.conditional_formatting.add(f"I{D0}:I{D1}", ColorScaleRule(start_type="num", start_value=1, start_color="DDEFD9", mid_type="num", mid_value=3,
                                                                  mid_color="FBF1CC", end_type="num", end_value=5, end_color="F9DDE7"))
    ws.conditional_formatting.add(f"B{D0}:P{D1}", FormulaRule(formula=[f"AND($B{D0}<>\"\",$B{D0}=TODAY())"], fill=fill(PAL["yellow"][0])))
    for col, lo, hi in (("E", 1, 5), ("F", 1, 5), ("H", 1, 5), ("I", 1, 5)):
        from openpyxl.worksheet.datavalidation import DataValidation
        dv = DataValidation(type="whole", operator="between", formula1=str(lo), formula2=str(hi), allow_blank=True)
        ws.add_data_validation(dv); dv.add(f"{col}{D0}:{col}{D1}")
    # Goals + KPIs
    card(ws, 5, 2, 15, 13, "Objectifs & résultats du mois", "pink")
    th(ws, 6, 2, ["Indicateur", "", "Objectif", "Moyenne", "Atteint", "", "% jours OK", "Progression", "", ""], "pink")
    ws.merge_cells("B6:C6"); ws.merge_cells("F6:G6"); ws.merge_cells("I6:K6")
    goals = [("😴 Sommeil (h/nuit)", 8, "D", ">="), ("💧 Eau (L/jour)", 2, "J", ">="), ("🚶 Pas / jour", 10000, "K", ">="),
             ("🏃 Sport (min/jour)", 30, "L", ">="), ("🧘 Méditation (min/jour)", 10, "M", ">="), ("📱 Écran (h max/jour)", 3, "N", "<="),
             ("😊 Humeur (/5)", 4, "F", ">="), ("⚡ Énergie (/5)", 4, "H", ">="), ("😣 Stress (max /5)", 2, "I", "<=")]
    REF["wb_rows"] = {}
    for i, (lab, g, col, op) in enumerate(goals):
        r = 7 + i
        put(ws, r, 2, lab, bold=True); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        put(ws, r, 4, g, NUM if g > 100 else NUM1, inp=True, align=CENTER)
        rng = f"{col}{D0}:{col}{D1}"
        put(ws, r, 5, f"=IFERROR(AVERAGE({rng}),0)", NUM if g > 100 else NUM1, bold=True, align=CENTER)
        put(ws, r, 6, f'=IF(E{r}=0,"",IF(E{r}{op}D{r},"✓","✗"))', align=CENTER, bold=True)
        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=7)
        put(ws, r, 8, f'=IFERROR(COUNTIF({rng},"{op}"&D{r})/COUNT({rng}),0)', PCT, align=CENTER)
        barcell(ws, r, 9, f"H{r}", "pink", 14, merge=3)
        REF["wb_rows"][lab] = r
    ws.conditional_formatting.add("F7:F15", CellIsRule(operator="equal", formula=['"✓"'], fill=fill(PAL["green"][0]), font=Font(name=FONT, color=PAL["green"][2], bold=True)))
    ws.conditional_formatting.add("F7:F15", CellIsRule(operator="equal", formula=['"✗"'], fill=fill(PAL["pink"][0]), font=Font(name=FONT, color=RED_TXT, bold=True)))
    kp = [("Jours suivis", f"=COUNT(D{D0}:D{D1})", "0", INK), ("Humeur moyenne", "=" + emoji_mood("E13"), None, INK),
          ("Sport total", f'=SUM(L{D0}:L{D1})', '0" min"', PAL["green"][2]), ("Poids actuel", f'=IFERROR(LOOKUP(2,1/(O{D0}:O{D1}<>""),O{D0}:O{D1}),"–")', '0.0" kg"', PAL["blue"][2])]
    for i, (lab, f, fmt, colr) in enumerate(kp):
        kpi(ws, 7 + (i // 2) * 3, 13 + (i % 2) * 2, 2, lab, f, fmt, colr, big=13)

    REF["wb"] = dict(sleep="'Bien-être'!$E$7", mood="'Bien-être'!$E$13", steps="'Bien-être'!$E$9", sport="'Bien-être'!$M$11" if False else f"'Bien-être'!$L$22",
                     stress="'Bien-être'!$E$15", D0=D0, D1=D1)
    REF["wb"]["sport_total"] = f"SUM('Bien-être'!$L${D0}:$L${D1})"
    # charts
    C0 = D1 + 3
    card(ws, C0, 2, 7, 17, "Sommeil (h)", "pink")
    bc = BarChart(); bc.type = "col"
    bc.add_data(Reference(ws, min_col=4, min_row=D0, max_row=D1), titles_from_data=False)
    bc.set_categories(Reference(ws, min_col=2, min_row=D0, max_row=D1)); bc.x_axis.number_format = "dd"
    color_series(bc, [PAL["blue"][3]]); bc.gapWidth = 40
    ws.add_chart(finish(bc, 13, 7.6, None, None), f"B{C0+1}")
    card(ws, C0, 10, 7, 17, "Humeur · énergie · stress", "pink")
    lc = LineChart()
    for col in (6, 8, 9):
        lc.add_data(Reference(ws, min_col=col, min_row=20, max_row=D1), titles_from_data=True)
    lc.set_categories(Reference(ws, min_col=2, min_row=D0, max_row=D1)); lc.x_axis.number_format = "dd"
    color_series(lc, [PAL["pink"][3], PAL["yellow"][3], PAL["lav"][3]], line=True)
    ws.add_chart(finish(lc, 13, 7.6), f"J{C0+1}")
    C1 = C0 + 18
    card(ws, C1, 2, 7, 17, "Pas par jour", "pink")
    sc = BarChart(); sc.type = "col"
    sc.add_data(Reference(ws, min_col=11, min_row=D0, max_row=D1), titles_from_data=False)
    sc.set_categories(Reference(ws, min_col=2, min_row=D0, max_row=D1)); sc.x_axis.number_format = "dd"
    color_series(sc, [PAL["green"][3]]); sc.gapWidth = 40
    ws.add_chart(finish(sc, 13, 7.6, None, None), f"B{C1+1}")
    card(ws, C1, 10, 7, 17, "Poids (kg)", "pink")
    wc = LineChart()
    wc.add_data(Reference(ws, min_col=15, min_row=D0, max_row=D1), titles_from_data=False)
    wc.set_categories(Reference(ws, min_col=2, min_row=D0, max_row=D1)); wc.x_axis.number_format = "dd"
    color_series(wc, [PAL["peach"][3]], line=True); wc.y_axis.scaling.min = 70
    ws.add_chart(finish(wc, 13, 7.6, None, None), f"J{C1+1}")
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Sport
def build_sport(wb):
    ws = wb.create_sheet("Sport")
    widths = {"B": 13, "C": 15, "D": 24, "E": 10, "F": 10, "G": 10, "H": 2, "I": 13, "J": 12, "K": 10, "L": 10, "M": 10, "N": 12, "O": 10}
    setup(ws, "💪 Sport & forme", "Programme, séances, records et mensurations — le suivi hebdo compare prévu et réalisé", 15, 170, widths, tab="green")
    L0 = 64; L1 = L0 + 99
    LD = f"$B${L0}:$B${L1}"; LT = f"$C${L0}:$C${L1}"; LM = f"$E${L0}:$E${L1}"; LK = f"$G${L0}:$G${L1}"; LC = f"$H${L0}:$H${L1}"
    # KPIs
    card(ws, 5, 2, 14, 4, "Ce mois-ci", "green")
    ms = f"DATE({P_YEAR},{P_MONTH},1)"; me = f"EOMONTH({ms},0)"
    crit = f'{LD},">="&{ms},{LD},"<="&{me}'
    kp = [("Séances", f"=COUNTIFS({crit})", "0"), ("Minutes", f"=SUMIFS({LM},{crit})", NUM), ("Kilomètres", f"=SUMIFS(F{L0}:F{L1},{crit})", NUM1),
          ("Calories", f"=SUMIFS(H{L0}:H{L1},{crit})", NUM), ("Semaine : réalisé / prévu", '=K21&" / "&J21', None)]
    pos = [2, 4, 6, 9, 12]
    for i, (lab, f, fmt) in enumerate(kp):
        kpi(ws, 6, pos[i] + (1 if i < 3 else 0), 2 if i < 4 else 3, lab, f, fmt, PAL["green"][2] if i == 0 else INK)
    REF["sport"] = dict(done="Sport!$K$21", planned="Sport!$J$21", month_sessions="Sport!$C$7")
    # programme
    prog = [("Lundi", "Musculation", "Haut du corps", 60), ("Mardi", "Course", "Footing 8 km", 45), ("Mercredi", "Yoga", "Mobilité", 30),
            ("Jeudi", "Musculation", "Bas du corps", 60), ("Vendredi", "HIIT", "Circuit 20 min", 25), ("Samedi", "Course", "Sortie longue", 75),
            ("Dimanche", "Repos", "Marche / récup", 0)]
    card(ws, 10, 2, 5, 10, "Programme de la semaine", "green")
    th(ws, 11, 2, ["Jour", "Type", "Séance", "Durée", "Heure"], "green")
    for i, (j, t, s, d) in enumerate(prog):
        r = 12 + i
        put(ws, r, 2, j, bold=True); put(ws, r, 3, t, inp=True); put(ws, r, 4, s, inp=True)
        put(ws, r, 5, d, '0" min"', inp=True); put(ws, r, 6, ["18:30", "07:00", "19:00", "18:30", "12:30", "09:30", ""][i], inp=True, align=CENTER)
    dv_list(ws, LISTS["Sports"].replace("$W$14", "$W$15") + "", "C12:C18")
    # this week
    card(ws, 10, 9, 7, 10, "Cette semaine", "green")
    th(ws, 11, 9, ["Jour", "Date", "Prévu", "Réalisé", "Minutes", "Statut", ""], "green")
    for i in range(7):
        r = 12 + i
        put(ws, r, 9, prog[i][0], bold=True)
        put(ws, r, 10, f"=TODAY()-WEEKDAY(TODAY(),2)+{i+1}", DSHORT)
        put(ws, r, 11, f'=IF(OR(C{r}="",C{r}="Repos"),0,1)', "0", align=CENTER)
        put(ws, r, 12, f"=COUNTIF({LD},J{r})", "0", align=CENTER)
        put(ws, r, 13, f"=SUMIFS({LM},{LD},J{r})", '0" min"')
        put(ws, r, 14, f'=IF(L{r}>=K{r},IF(L{r}>0,"✓",IF(K{r}=0,"Repos","")),IF(J{r}<TODAY(),"✗","À faire"))', align=CENTER, bold=True)
        put(ws, r, 15, None)
    put(ws, 19, 9, "Total", bold=True, bg=PAL["green"][0])
    put(ws, 19, 10, None, bg=PAL["green"][0])
    for c, f in ((11, "=SUM(K12:K18)"), (12, "=SUM(L12:L18)"), (13, "=SUM(M12:M18)")):
        put(ws, 19, c, f, "0" if c < 13 else '0" min"', bold=True, bg=PAL["green"][0], align=CENTER)
    put(ws, 19, 14, None, bg=PAL["green"][0]); put(ws, 19, 15, None, bg=PAL["green"][0])
    ws["J21"] = "=K19"; ws["K21"] = "=L19"
    ws["J21"].font = font(1, color=BG); ws["K21"].font = font(1, color=BG)
    for v, c in (("✓", "green"), ("✗", "pink"), ("À faire", "yellow")):
        ws.conditional_formatting.add("N12:N18", CellIsRule(operator="equal", formula=[f'"{v}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], bold=True)))
    # records + measurements
    card(ws, 22, 2, 6, 10, "Records personnels", "green")
    th(ws, 23, 2, ["Exercice", "Unité", "Record", "Objectif", "%", "Progression"], "green")
    recs = [("Développé couché", "kg", 72.5, 85), ("Squat", "kg", 95, 110), ("Soulevé de terre", "kg", 115, 140),
            ("Tractions", "reps", 9, 15), ("5 km", "min", 26.5, 24), ("10 km", "min", 56, 52), ("Gainage", "sec", 150, 240)]
    for i in range(8):
        r = 24 + i
        rc = recs[i] if i < len(recs) else (None,) * 4
        put(ws, r, 2, rc[0], inp=True, bold=True); put(ws, r, 3, rc[1], inp=True, align=CENTER)
        put(ws, r, 4, rc[2], NUM1, inp=True, align=CENTER); put(ws, r, 5, rc[3], NUM1, inp=True, align=CENTER)
        put(ws, r, 6, f'=IF(B{r}="","",IFERROR(IF(C{r}="min",E{r}/D{r},D{r}/E{r}),0))', PCT, bold=True)
        barcell(ws, r, 7, f"F{r}", "green", 8)
    card(ws, 22, 9, 7, 15, "Mensurations", "green")
    th(ws, 23, 9, ["Date", "Poids", "Taille (cm)", "Masse grasse", "Bras (cm)", "Cuisses (cm)", "IMC"], "green")
    put(ws, 23, 15, "IMC")
    ws["O23"].comment = None
    for i in range(12):
        r = 24 + i
        if i < 11:
            v = (dt.date(2026, i + 1, 1), round(82 - i * 0.32, 1), round(88 - i * 0.4, 1), round(0.21 - i * 0.003, 3), round(33 + i * 0.1, 1), round(57 - i * 0.15, 1))
        else:
            v = (None,) * 6
        put(ws, r, 9, v[0], DATE, inp=True); put(ws, r, 10, v[1], NUM1, inp=True); put(ws, r, 11, v[2], NUM1, inp=True)
        put(ws, r, 12, v[3], PCT1, inp=True); put(ws, r, 13, v[4], NUM1, inp=True); put(ws, r, 14, v[5], NUM1, inp=True)
        put(ws, r, 15, f'=IF(J{r}="","",J{r}/($O$37^2))', NUM1)
    put(ws, 37, 14, "Taille (m)", bold=True, size=8, align=RIGHT); put(ws, 37, 15, 1.78, "0.00", inp=True)
    # charts
    card(ws, 39, 2, 6, 22, "Prévu vs réalisé (semaine)", "green")
    bc = BarChart(); bc.type = "col"
    bc.add_data(Reference(ws, min_col=11, max_col=12, min_row=11, max_row=18), titles_from_data=True)
    bc.set_categories(Reference(ws, min_col=9, min_row=12, max_row=18))
    bc.series[0].tx = SeriesLabel(v="Prévu"); bc.series[1].tx = SeriesLabel(v="Réalisé")
    color_series(bc, ["E3E4EA", PAL["green"][3]]); bc.gapWidth = 50
    ws.add_chart(finish(bc, 13.5, 10.5), "B40")
    card(ws, 39, 9, 7, 22, "Évolution du poids", "green")
    lc = LineChart()
    lc.add_data(Reference(ws, min_col=10, min_row=23, max_row=34), titles_from_data=True)
    lc.set_categories(Reference(ws, min_col=9, min_row=24, max_row=34)); lc.x_axis.number_format = "mmm"
    color_series(lc, [PAL["green"][3]], line=True); lc.y_axis.scaling.min = 75
    ws.add_chart(finish(lc, 16, 10.5, None, None), "I40")
    # log
    card(ws, L0 - 2, 2, 9, L1 - L0 + 3, "Journal d'entraînement", "green")
    th(ws, L0 - 1, 2, ["Date", "Type", "Séance / détail", "Durée (min)", "Distance (km)", "Intensité /10", "Calories", "Ressenti", "Notes"], "green")
    ws.cell(L0 - 1, 8).value = "CALORIES"; ws.cell(L0 - 1, 7).value = "INTENSITÉ /10"
    random.seed(9)
    log = []
    day = dt.date(2026, 9, 1)
    while day < TODAY:
        p = prog[day.weekday()]
        if p[1] != "Repos" and random.random() < 0.75:
            dist = round(random.uniform(6, 14), 1) if p[1] == "Course" else None
            dur = p[3] + random.randint(-10, 10)
            log.append((day, p[1], p[2], dur, dist, random.randint(5, 9), int(dur * random.uniform(7, 11)),
                        random.choice(["😄", "🙂", "🙂", "😐"]), ""))
        day += dt.timedelta(days=1)
    log.sort(key=lambda x: x[0], reverse=True)
    # columns: B date, C type, D détail, E durée, F distance, G intensité, H calories(not used -> I), I calories, J ressenti -> map
    for i in range(L1 - L0 + 1):
        r = L0 + i
        v = log[i] if i < len(log) else (None,) * 9
        put(ws, r, 2, v[0], DATE, inp=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], inp=True)
        put(ws, r, 5, v[3], "0", inp=True); put(ws, r, 6, v[4], NUM1, inp=True); put(ws, r, 7, v[5], "0", inp=True)
        put(ws, r, 8, v[6], NUM, inp=True); put(ws, r, 9, v[7], inp=True, align=CENTER); put(ws, r, 10, v[8], inp=True)
    # calories are in column H -> fix KPI references
    ws["I7"].value = f"=SUMIFS(H{L0}:H{L1},{crit})" if False else ws["I7"].value
    dv_list(ws, LISTS["Sports"], f"C{L0}:C{L1}")
    dv_list(ws, '"😄,🙂,😐,🙁,😞"', f"I{L0}:I{L1}")
    ws.conditional_formatting.add(f"G{L0}:G{L1}", ColorScaleRule(start_type="num", start_value=1, start_color="FFFFFF", end_type="num", end_value=10, end_color=PAL["green"][3]))
    REF["sport_cal_fix"] = (L0, L1, crit)
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Nutrition
def build_nutrition(wb):
    ws = wb.create_sheet("Nutrition")
    widths = {"B": 15, "C": 16, "D": 16, "E": 16, "F": 16, "G": 16, "H": 16, "I": 16, "J": 2, "K": 14, "L": 14, "M": 12, "N": 12, "O": 12}
    setup(ws, "🥗 Nutrition & courses", "Menu de la semaine, repas du jour, liste de courses et objectifs nutritionnels", 15, 80, widths, tab="yellow")
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    menu = {
        "Petit-déjeuner": ["Porridge banane", "Œufs brouillés", "Yaourt granola", "Smoothie bowl", "Tartines avocat", "Pancakes", "Brunch maison"],
        "Déjeuner": ["Bowl poulet riz", "Salade quinoa", "Wrap thon", "Pâtes complètes", "Buddha bowl", "Sushi maison", "Rôti légumes"],
        "Dîner": ["Saumon brocolis", "Soupe + tartine", "Curry pois chiches", "Omelette salade", "Pizza maison", "Tacos", "Gratin légumes"],
        "Collations": ["Pomme + amandes", "Fromage blanc", "Barre protéinée", "Fruits secs", "Carottes houmous", "Chocolat noir", "Fruits"],
    }
    mcol = {"Petit-déjeuner": "peach", "Déjeuner": "green", "Dîner": "yellow", "Collations": "pink"}
    card(ws, 5, 2, 8, 6, "Menu de la semaine", "yellow")
    th(ws, 6, 2, [""] + days, "yellow")
    for i, (meal, items) in enumerate(menu.items()):
        r = 7 + i
        put(ws, r, 2, meal.upper(), bold=True, size=8, align=CENTER, bg=PAL[mcol[meal]][0], color=PAL[mcol[meal]][2])
        for j, it in enumerate(items):
            put(ws, r, 3 + j, it, inp=True, align=CENTER)
            ws.cell(r, 3 + j).alignment = CENTER
        ws.row_dimensions[r].height = 34
    ws.conditional_formatting.add("C6:I10", FormulaRule(formula=["COLUMN(C6)-2=WEEKDAY(TODAY(),2)"], fill=fill(PAL["yellow"][0])))
    card(ws, 5, 11, 5, 6, "Repas du jour", "yellow")
    put(ws, 6, 11, '="Aujourd\'hui · "&' + DOW.format(d="TODAY()"), bold=True, align=CENTER, color=PAL["yellow"][2])
    ws.merge_cells("K6:O6")
    for i, meal in enumerate(menu):
        r = 7 + i
        put(ws, r, 11, meal.upper(), bold=True, size=8, align=CENTER, bg=PAL[mcol[meal]][0], color=PAL[mcol[meal]][2])
        put(ws, r, 12, f"=INDEX(C{r}:I{r},1,WEEKDAY(TODAY(),2))", align=CENTER, bold=True)
        ws.merge_cells(start_row=r, start_column=12, end_row=r, end_column=15)
    REF["meals"] = [(m, f"Nutrition!$L${7+i}") for i, m in enumerate(menu)]
    # groceries
    G0 = 14; NG = 40
    card(ws, G0, 2, 6, NG + 3, "Liste de courses", "yellow")
    th(ws, G0 + 1, 2, ["Article", "Rayon", "Quantité", "Prix estimé", "Acheté", ""], "yellow")
    items = [("Bananes", "Fruits & légumes", "1 kg", 2.2, ""), ("Épinards", "Fruits & légumes", "500 g", 2.5, "✓"),
             ("Avocats", "Fruits & légumes", "3", 3.6, ""), ("Brocolis", "Fruits & légumes", "2", 2.8, ""), ("Poulet", "Viandes & poissons", "1 kg", 9.5, ""),
             ("Saumon", "Viandes & poissons", "400 g", 8.9, "✓"), ("Œufs", "Crémerie", "12", 3.9, ""), ("Fromage blanc", "Crémerie", "1 kg", 2.6, ""),
             ("Riz complet", "Épicerie", "1 kg", 2.4, "✓"), ("Quinoa", "Épicerie", "500 g", 3.2, ""), ("Flocons d'avoine", "Épicerie", "1 kg", 1.9, ""),
             ("Pois chiches", "Épicerie", "2 boîtes", 1.8, ""), ("Eau pétillante", "Boissons", "6 × 1 L", 3.0, ""), ("Dentifrice", "Hygiène", "1", 2.5, "✓"),
             ("Éponges", "Maison", "pack", 1.9, "")]
    for i in range(NG):
        r = G0 + 2 + i
        it = items[i] if i < len(items) else (None,) * 5
        put(ws, r, 2, it[0], inp=True, bold=True); put(ws, r, 3, it[1], inp=True); put(ws, r, 4, it[2], inp=True, align=CENTER)
        put(ws, r, 5, it[3], EUR2, inp=True); put(ws, r, 6, it[4], inp=True, align=CENTER); put(ws, r, 7, None)
    gl = G0 + 1 + NG
    dv_list(ws, LISTS["Rayons courses"], f"C{G0+2}:C{gl}")
    checks(ws, f"F{G0+2}:F{gl}", "yellow")
    ws.conditional_formatting.add(f"B{G0+2}:E{gl}", FormulaRule(formula=[done(f"$F{G0+2}")], font=Font(name=FONT, color="B5B8C2", strike=True)))
    A, F_ = f"B{G0+2}:B{gl}", f"F{G0+2}:F{gl}"
    tobuy = f'SUMPRODUCT((LEN({A})>0)*({F_}<>"✓")*({F_}<>TRUE))'
    card(ws, G0, 11, 5, 9, "Courses en un coup d'œil", "yellow")
    kpi(ws, G0 + 1, 11, 2, "Articles à acheter", f"={tobuy}", "0", PAL["yellow"][2], big=18)
    kpi(ws, G0 + 1, 14, 2, "Déjà achetés", f"={count_done(F_)}", "0", PAL["green"][2], big=18)
    kpi(ws, G0 + 4, 11, 2, "Budget restant", f'=SUMPRODUCT((LEN({A})>0)*({F_}<>"✓")*({F_}<>TRUE)*E{G0+2}:E{gl})', EUR2)
    kpi(ws, G0 + 4, 14, 2, "Budget total", f"=SUM(E{G0+2}:E{gl})", EUR2)
    REF["grocery"] = dict(tobuy=f"Nutrition!$K${G0+2}", budget=f"Nutrition!$K${G0+5}")
    card(ws, G0 + 10, 11, 5, 11, "Par rayon (à acheter)", "yellow")
    th(ws, G0 + 11, 11, ["Rayon", "", "Articles", "Budget", ""], "yellow")
    rays = ["Fruits & légumes", "Viandes & poissons", "Crémerie", "Épicerie", "Surgelés", "Boissons", "Hygiène", "Maison"]
    C_ = f"C{G0+2}:C{gl}"
    for i, ry in enumerate(rays):
        r = G0 + 12 + i
        put(ws, r, 11, ry, bold=True); ws.merge_cells(start_row=r, start_column=11, end_row=r, end_column=12)
        put(ws, r, 13, f'=SUMPRODUCT(({C_}="{ry}")*({F_}<>"✓")*({F_}<>TRUE))', "0", align=CENTER)
        put(ws, r, 14, f'=SUMPRODUCT(({C_}="{ry}")*({F_}<>"✓")*({F_}<>TRUE)*E{G0+2}:E{gl})', EUR2)
        put(ws, r, 15, None)
    card(ws, G0 + 22, 11, 5, 9, "Objectifs nutritionnels / jour", "yellow")
    for i, (k, v, f) in enumerate([("Calories", 2300, '#,##0" kcal"'), ("Protéines", 140, '0" g"'), ("Glucides", 260, '0" g"'),
                                   ("Lipides", 75, '0" g"'), ("Fibres", 30, '0" g"'), ("Eau", 2, '0.0" L"'), ("Repas maison / semaine", 12, "0")]):
        r = G0 + 23 + i
        put(ws, r, 11, k, bold=True); ws.merge_cells(start_row=r, start_column=11, end_row=r, end_column=13)
        put(ws, r, 14, v, f, inp=True, align=CENTER); put(ws, r, 15, None)
    R0 = gl + 3
    card(ws, R0, 2, 8, 13, "Recettes favorites", "yellow")
    th(ws, R0 + 1, 2, ["Recette", "Repas", "Temps", "Portions", "Ingrédients clés", "", "", "Note"], "yellow")
    rec = [("Bowl poulet teriyaki", "Déjeuner", "25 min", 2, "poulet, riz, brocolis, sauce soja", "★★★★★"),
           ("Curry pois chiches", "Dîner", "30 min", 4, "pois chiches, lait coco, épinards", "★★★★☆"),
           ("Overnight oats", "Petit-déjeuner", "5 min", 1, "avoine, lait, chia, fruits rouges", "★★★★★"),
           ("Saumon au four", "Dîner", "20 min", 2, "saumon, citron, haricots verts", "★★★★☆")]
    for i in range(10):
        r = R0 + 2 + i
        v = rec[i] if i < len(rec) else (None,) * 6
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], inp=True, align=CENTER)
        put(ws, r, 5, v[3], "0", inp=True); put(ws, r, 6, v[4], inp=True)
        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
        put(ws, r, 9, v[5], inp=True, align=CENTER, color=PAL["yellow"][3])
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Mental
def build_mental(wb):
    ws = wb.create_sheet("Mental")
    widths = {"B": 11, "C": 7, "D": 24, "E": 24, "F": 24, "G": 26, "H": 26, "I": 26, "J": 9, "K": 9}
    setup(ws, "🧠 Mental & journal", "Gratitude, victoires, leçons et revue hebdomadaire — l'humeur est reprise de l'onglet Bien-être", 11, 110, widths, tab="lav")
    J0 = 33; J1 = J0 + 30
    card(ws, 5, 2, 10, 4, "Ce mois-ci", "lav")
    wbD0 = REF["wb"]["D0"]; wbD1 = REF["wb"]["D1"]
    kp = [("Entrées de journal", f'=COUNTIF(D{J0}:D{J1},"?*")', "0", PAL["lav"][2], 2, 2), ("Humeur moyenne", "=IFERROR(AVERAGE(J" + f"{J0}:J{J1}),0)", '0.0" / 5"', INK, 4, 1),
          ("Stress moyen", f"=IFERROR(AVERAGE('Bien-être'!I{wbD0}:I{wbD1}),0)", '0.0" / 5"', INK, 5, 1),
          ("Note moyenne des semaines", "=IFERROR(AVERAGE(F14:F18),0)", '0.0" / 10"', PAL["green"][2], 6, 1),
          ("Méditation ce mois", f"=SUM('Bien-être'!M{wbD0}:M{wbD1})", '0" min"', PAL["blue"][2], 7, 1),
          ("Jours sans écrire", f'=MAX(0,DAY(MIN(TODAY(),EOMONTH(DATE({P_YEAR},{P_MONTH},1),0)))-COUNTIF(D{J0}:D{J1},"?*"))', "0", PAL["pink"][2], 8, 1)]
    for lab, f, fmt, colr, c, w in kp:
        kpi(ws, 6, c + (0 if c == 2 else 0), w, lab, f, fmt, colr, big=13)
    REF["mental"] = dict(entries="Mental!$B$7")
    # weekly review
    card(ws, 10, 2, 10, 10, "Revue hebdomadaire", "lav")
    th(ws, 11, 2, ["Semaine", "", "Ce qui a marché", "À améliorer", "Note /10", "Focus de la semaine suivante", "Gratitude de la semaine", "Petite victoire", "", ""], "lav")
    ws.merge_cells("B11:C11"); ws.merge_cells("I11:K11")
    ws["F11"].value = "NOTE /10"
    rev = [("Routine du matin tenue 5/7", "Coucher trop tard", 7, "Couper les écrans à 22h", "Soutien de l'équipe", "Premier 10 km"),
           ("Gros projet livré", "Peu de sport", 8, "3 séances minimum", "Dîner en famille", "Promotion évoquée"),
           ("Méditation tous les jours", "Grignotage", 7, "Préparer les repas", "Belle randonnée", "Budget respecté"),
           ("Lecture régulière", "Procrastination admin", 6, "Bloc admin vendredi", "Appel avec un ami", "Dossier impôts fini")]
    for i in range(5):
        r = 12 + i + 2 if False else 14 + i
    for i in range(5):
        r = 14 + i
        v = rev[i] if i < len(rev) else (None,) * 6
        put(ws, r, 2, f"Semaine {i+1}", bold=True, color=PAL[WEEKS[i][2]][2], bg=PAL[WEEKS[i][2]][0])
        put(ws, r, 3, None, bg=PAL[WEEKS[i][2]][0])
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        put(ws, r, 4, v[0], inp=True, align=LEFTW); put(ws, r, 5, v[1], inp=True, align=LEFTW)
        put(ws, r, 6, v[2], "0", inp=True, align=CENTER, bold=True); put(ws, r, 7, v[3], inp=True, align=LEFTW)
        put(ws, r, 8, v[4], inp=True, align=LEFTW); put(ws, r, 9, v[5], inp=True, align=LEFTW)
        ws.merge_cells(start_row=r, start_column=9, end_row=r, end_column=11)
        ws.row_dimensions[r].height = 30
    for r in (12, 13):
        for c in range(2, 12):
            ws.cell(r, c).value = None
    ws.row_dimensions[12].height = 4; ws.row_dimensions[13].height = 4
    ws.conditional_formatting.add("F14:F18", ColorScaleRule(start_type="num", start_value=1, start_color="F9DDE7", mid_type="num", mid_value=5,
                                                            mid_color="FBF1CC", end_type="num", end_value=10, end_color="DDEFD9"))
    # values, stress, ideas
    card(ws, 21, 2, 3, 10, "Mes valeurs & affirmations", "lav")
    aff = ["Je progresse un peu chaque jour.", "Ma santé est ma priorité.", "Je mérite le calme et la réussite.", "Discipline = liberté.",
           "Je choisis mes pensées.", "J'ose sortir de ma zone de confort.", "Je suis reconnaissant pour ce que j'ai.", "Valeurs : honnêteté, famille, croissance."]
    for i, a in enumerate(aff):
        r = 22 + i
        put(ws, r, 2, a, inp=True); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    card(ws, 21, 5, 4, 10, "Stress : déclencheurs & solutions", "lav")
    th(ws, 22, 5, ["Déclencheur", "Ce que je fais", "Efficacité", ""], "lav")
    st = [("Réunions tardives", "Bloquer mon agenda", "★★★★☆"), ("Charge de travail", "Liste de 3 priorités", "★★★★★"),
          ("Finances serrées", "Revue budget dimanche", "★★★★☆"), ("Manque de sommeil", "Routine du soir", "★★★☆☆")]
    for i in range(7):
        r = 23 + i
        v = st[i] if i < len(st) else (None,) * 3
        put(ws, r, 5, v[0], inp=True); put(ws, r, 6, v[1], inp=True); put(ws, r, 7, v[2], inp=True, color=PAL["lav"][3]); put(ws, r, 8, None)
    card(ws, 21, 9, 3, 10, "Idées & notes en vrac", "lav")
    for i, t in enumerate(["Planifier un week-end détox digitale", "Essayer la cohérence cardiaque", "Livre : « Atomic Habits »", "Podcast : Change ma vie"]):
        r = 22 + i
        put(ws, r, 9, "• " + t, inp=True); ws.merge_cells(start_row=r, start_column=9, end_row=r, end_column=11)
    # journal
    card(ws, J0 - 2, 2, 10, 34, "Journal quotidien", "lav")
    th(ws, J0 - 1, 2, ["Date", "Jour", "Gratitude 1", "Gratitude 2", "Gratitude 3", "Victoire du jour", "Leçon apprise", "Intention pour demain", "Humeur", ""], "lav")
    ws.merge_cells(start_row=J0 - 1, start_column=10, end_row=J0 - 1, end_column=11)
    random.seed(12)
    g = ["Un café au soleil", "Ma famille", "Ma santé", "Un bon repas", "Un collègue sympa", "Une belle séance", "Un message d'un ami",
         "Le calme du matin", "Un bon livre", "Mon chez-moi", "Une balade", "Un fou rire"]
    wins = ["Séance de sport faite", "Projet avancé", "Budget respecté", "Méditation 15 min", "Couché tôt", "Rangé le bureau", "Appelé ma mère",
            "20 pages lues", "Mangé équilibré", "Dit non à une distraction", "Fini une formation", "Aidé un collègue"]
    les = ["Préparer la veille aide", "Le sport booste mon humeur", "Je dois déléguer", "Respirer avant de répondre", "Moins de café l'après-midi",
           "Faire simple", "Demander de l'aide", "Le progrès > la perfection", "Écouter mon corps", "Bloquer du temps pour moi", "Dire merci", "Bouger dès le matin"]
    ints = ["Commencer par la tâche difficile", "Boire plus d'eau", "Sortir marcher à midi", "Couper les notifs", "Être patient", "Sourire", "Lire le soir"]
    for d in range(1, 32):
        r = J0 + d - 1
        put(ws, r, 2, f'=IF({d}<={NDAYS},DATE({P_YEAR},{P_MONTH},{d}),"")', DATE)
        put(ws, r, 3, f'=IF(B{r}="","",{DOW.format(d=f"B{r}")})', align=CENTER, color=MUTED)
        fill_ = d < TODAY.day
        vals = [random.choice(g), random.choice(g), random.choice(g), random.choice(wins), random.choice(les), random.choice(ints)] if fill_ else [None] * 6
        for j, v in enumerate(vals):
            put(ws, r, 4 + j, v, inp=True, size=8)
        put(ws, r, 10, f"=IFERROR(IF(INDEX('Bien-être'!$F${wbD0}:$F${wbD1},{d})=\"\",\"\",INDEX('Bien-être'!$F${wbD0}:$F${wbD1},{d})),\"\")", "0", align=CENTER)
        put(ws, r, 11, "=" + emoji_mood(f"J{r}"), align=CENTER)
    ws.conditional_formatting.add(f"B{J0}:K{J1}", FormulaRule(formula=[f"AND($B{J0}<>\"\",$B{J0}=TODAY())"], fill=fill(PAL["yellow"][0])))
    ws.conditional_formatting.add(f"J{J0}:J{J1}", ColorScaleRule(start_type="num", start_value=1, start_color="F9DDE7", mid_type="num", mid_value=3, mid_color="FBF1CC", end_type="num", end_value=5, end_color="DDEFD9"))
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Pro
def build_pro(wb):
    ws = wb.create_sheet("Pro")
    widths = {"B": 28, "C": 14, "D": 12, "E": 12, "F": 12, "G": 12, "H": 10, "I": 9, "J": 12, "K": 12, "L": 18, "M": 18}
    setup(ws, "💼 Pro & apprentissage", "Projets, compétences, formations, lectures et réseau — progression calculée automatiquement", 13, 140, widths, tab="blue")
    P0 = 12; NP = 12
    card(ws, 5, 2, 12, 5, "Vue d'ensemble", "blue")
    # projects
    card(ws, P0 - 1, 2, 12, NP + 3, "Projets", "blue")
    th(ws, P0, 2, ["Projet", "Domaine", "Priorité", "Statut", "Début", "Échéance", "Jours rest.", "%", "Progression", "", "Prochaine action", ""], "blue")
    ws.merge_cells(start_row=P0, start_column=10, end_row=P0, end_column=11); ws.merge_cells(start_row=P0, start_column=12, end_row=P0, end_column=13)
    projs = [("Refonte du site client", "Carrière", "Très haute", "En cours", dt.date(2026, 9, 1), dt.date(2026, 12, 15), .7, "Valider maquettes"),
             ("Certification Google Analytics", "Apprentissage", "Haute", "En cours", dt.date(2026, 10, 1), dt.date(2026, 12, 20), .45, "Module 4"),
             ("Boutique en ligne side business", "Finances", "Haute", "En cours", dt.date(2026, 6, 1), dt.date(2027, 1, 31), .55, "Fiches produits"),
             ("Présentation annuelle", "Carrière", "Moyenne", "À faire", dt.date(2026, 11, 20), dt.date(2026, 12, 10), 0, "Collecter les chiffres"),
             ("Portfolio personnel", "Carrière", "Moyenne", "En attente", dt.date(2026, 8, 1), dt.date(2027, 2, 28), .3, "Choisir 5 projets"),
             ("Automatiser la compta", "Finances", "Basse", "Terminé", dt.date(2026, 3, 1), dt.date(2026, 5, 1), 1, "—")]
    for i in range(NP):
        r = P0 + 1 + i
        v = projs[i] if i < len(projs) else (None,) * 8
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], inp=True, align=CENTER)
        put(ws, r, 5, v[3], inp=True, align=CENTER); put(ws, r, 6, v[4], DATE, inp=True); put(ws, r, 7, v[5], DATE, inp=True)
        put(ws, r, 8, f'=IF(OR(B{r}="",G{r}=""),"",IF(E{r}="Terminé",0,G{r}-TODAY()))', "0")
        put(ws, r, 9, v[6], PCT, inp=True, bold=True)
        barcell(ws, r, 10, f"I{r}", "blue", 14, merge=2)
        put(ws, r, 12, v[7], inp=True); put(ws, r, 13, None)
        ws.merge_cells(start_row=r, start_column=12, end_row=r, end_column=13)
    pl = P0 + NP
    dv_list(ws, LISTS["Domaines de vie"], f"C{P0+1}:C{pl}"); dv_list(ws, LISTS["Priorités"], f"D{P0+1}:D{pl}"); dv_list(ws, LISTS["Statuts"], f"E{P0+1}:E{pl}")
    for st, c in (("Terminé", "green"), ("En cours", "blue"), ("En attente", "yellow"), ("À faire", "peach"), ("Backlog", "grey")):
        ws.conditional_formatting.add(f"E{P0+1}:E{pl}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], bold=True)))
    for st, c in (("Très haute", "pink"), ("Haute", "peach"), ("Moyenne", "yellow"), ("Basse", "green")):
        ws.conditional_formatting.add(f"D{P0+1}:D{pl}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0])))
    ws.conditional_formatting.add(f"H{P0+1}:H{pl}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, color=RED_TXT, bold=True)))
    REF["proj"] = (f"Pro!$B${P0+1}:$B${pl}", f"Pro!$E${P0+1}:$E${pl}", f"Pro!$I${P0+1}:$I${pl}", P0 + 1, pl)
    # skills
    S0 = pl + 3; NS = 10
    card(ws, S0, 2, 6, NS + 2, "Compétences", "blue")
    th(ws, S0 + 1, 2, ["Compétence", "Catégorie", "Niveau /10", "Cible /10", "Écart", "Progression"], "blue")
    sk = [("Anglais professionnel", "Langue", 6, 8), ("Excel / Google Sheets", "Outils", 7, 9), ("Prise de parole", "Soft skill", 5, 8),
          ("Python", "Tech", 4, 7), ("Marketing digital", "Métier", 6, 8), ("Gestion de projet", "Métier", 7, 9), ("Négociation", "Soft skill", 5, 7), ("Design (Figma)", "Outils", 4, 6)]
    for i in range(NS):
        r = S0 + 2 + i
        v = sk[i] if i < len(sk) else (None,) * 4
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], "0", inp=True, align=CENTER)
        put(ws, r, 5, v[3], "0", inp=True, align=CENTER); put(ws, r, 6, f'=IF(B{r}="","",E{r}-D{r})', "0", align=CENTER)
        barcell(ws, r, 7, f"IF(E{r}=0,0,D{r}/E{r})", "blue", 10)
    REF["skills"] = (f"Pro!$B${S0+2}:$B${S0+1+NS}", f"Pro!$D${S0+2}:$D${S0+1+NS}", f"Pro!$E${S0+2}:$E${S0+1+NS}", S0 + 2)
    card(ws, S0, 9, 5, NS + 2, "Niveau vs cible", "blue")
    bc = BarChart(); bc.type = "bar"
    bc.add_data(Reference(ws, min_col=4, max_col=5, min_row=S0 + 1, max_row=S0 + 1 + len(sk)), titles_from_data=True)
    bc.set_categories(Reference(ws, min_col=2, min_row=S0 + 2, max_row=S0 + 1 + len(sk)))
    color_series(bc, [PAL["blue"][3], "E3E4EA"]); bc.gapWidth = 40; bc.y_axis.scaling.max = 10
    ws.add_chart(finish(bc, 13.5, 5.8), f"I{S0+1}")
    # courses
    F0 = S0 + NS + 4; NF = 10
    card(ws, F0, 2, 12, NF + 2, "Formations & cours", "blue")
    th(ws, F0 + 1, 2, ["Formation", "Plateforme", "Heures totales", "Heures faites", "%", "Progression", "", "Statut", "Certificat", "Début", "Fin prévue", ""], "blue")
    ws.merge_cells(start_row=F0 + 1, start_column=7, end_row=F0 + 1, end_column=8)
    fo = [("Google Analytics 4", "Google Skillshop", 20, 9, "", dt.date(2026, 10, 1), dt.date(2026, 12, 20)),
          ("Anglais B2", "Babbel", 120, 74, "", dt.date(2026, 1, 10), dt.date(2027, 6, 30)),
          ("Python pour débutants", "OpenClassrooms", 30, 30, "✓", dt.date(2026, 3, 1), dt.date(2026, 5, 15)),
          ("Prise de parole", "Udemy", 8, 3, "", dt.date(2026, 11, 1), dt.date(2026, 12, 31))]
    for i in range(NF):
        r = F0 + 2 + i
        v = fo[i] if i < len(fo) else (None,) * 7
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], "0", inp=True, align=CENTER)
        put(ws, r, 5, v[3], "0", inp=True, align=CENTER); put(ws, r, 6, f'=IF(B{r}="","",IFERROR(MIN(1,E{r}/D{r}),0))', PCT, bold=True)
        barcell(ws, r, 7, f"F{r}", "blue", 12, merge=2)
        put(ws, r, 9, f'=IF(B{r}="","",IF(F{r}>=1,"Terminé",IF(E{r}>0,"En cours","À faire")))', align=CENTER)
        put(ws, r, 10, v[4], inp=True, align=CENTER); put(ws, r, 11, v[5], DATE, inp=True); put(ws, r, 12, v[6], DATE, inp=True); put(ws, r, 13, None)
    fl = F0 + 1 + NF
    checks(ws, f"J{F0+2}:J{fl}", "blue")
    for st, c in (("Terminé", "green"), ("En cours", "blue"), ("À faire", "peach")):
        ws.conditional_formatting.add(f"I{F0+2}:I{fl}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], bold=True)))
    # reading
    B0 = fl + 3; NB = 15
    card(ws, B0, 2, 12, NB + 2, "Lectures", "blue")
    th(ws, B0 + 1, 2, ["Livre", "Auteur", "Catégorie", "Pages", "Pages lues", "%", "Progression", "", "Statut", "Note /5", "Terminé le", "À retenir"], "blue")
    ws.merge_cells(start_row=B0 + 1, start_column=8, end_row=B0 + 1, end_column=9)
    bk = [("Atomic Habits", "James Clear", "Développement perso", 320, 320, 5, dt.date(2026, 2, 10), "1 % mieux chaque jour"),
          ("L'investisseur intelligent", "B. Graham", "Finance", 640, 410, None, None, "Marge de sécurité"),
          ("Deep Work", "Cal Newport", "Productivité", 300, 300, 4, dt.date(2026, 6, 2), "Bloquer le temps profond"),
          ("Sapiens", "Y. N. Harari", "Histoire", 512, 120, None, None, ""),
          ("Le pouvoir du moment présent", "E. Tolle", "Mental", 240, 0, None, None, "")]
    for i in range(NB):
        r = B0 + 2 + i
        v = bk[i] if i < len(bk) else (None,) * 8
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], inp=True)
        put(ws, r, 5, v[3], "0", inp=True, align=CENTER); put(ws, r, 6, v[4], "0", inp=True, align=CENTER)
        put(ws, r, 7, f'=IF(B{r}="","",IFERROR(MIN(1,F{r}/E{r}),0))', PCT, bold=True)
        barcell(ws, r, 8, f"G{r}", "blue", 12, merge=2)
        put(ws, r, 10, f'=IF(B{r}="","",IF(G{r}>=1,"Lu",IF(F{r}>0,"En cours","À lire")))', align=CENTER)
        put(ws, r, 11, v[5], "0", inp=True, align=CENTER); put(ws, r, 12, v[6], DATE, inp=True); put(ws, r, 13, v[7], inp=True)
    bl = B0 + 1 + NB
    for st, c in (("Lu", "green"), ("En cours", "blue"), ("À lire", "grey")):
        ws.conditional_formatting.add(f"J{B0+2}:J{bl}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], bold=True)))
    # network
    N0 = bl + 3; NN = 12
    card(ws, N0, 2, 12, NN + 2, "Réseau & contacts", "blue")
    th(ws, N0 + 1, 2, ["Nom", "Entreprise", "Rôle", "Dernier contact", "Relancer (jours)", "Prochaine relance", "Statut", "", "Canal", "", "Notes", ""], "blue")
    co = [("Sarah M.", "Agence Nova", "Directrice", dt.date(2026, 9, 20), 60, "LinkedIn", "Opportunité freelance"),
          ("Karim B.", "StartUp Lab", "CTO", dt.date(2026, 10, 30), 30, "Café", "Conseils Python"),
          ("Julie R.", "Banque", "Conseillère", dt.date(2026, 6, 10), 90, "Email", "Prêt immo"),
          ("Thomas L.", "Ancien collègue", "Manager", dt.date(2026, 11, 2), 45, "Téléphone", "Recommandation")]
    for i in range(NN):
        r = N0 + 2 + i
        v = co[i] if i < len(co) else (None,) * 7
        put(ws, r, 2, v[0], inp=True, bold=True); put(ws, r, 3, v[1], inp=True); put(ws, r, 4, v[2], inp=True)
        put(ws, r, 5, v[3], DATE, inp=True); put(ws, r, 6, v[4], "0", inp=True, align=CENTER)
        put(ws, r, 7, f'=IF(OR(B{r}="",E{r}=""),"",E{r}+F{r})', DATE)
        put(ws, r, 8, f'=IF(G{r}="","",IF(G{r}<=TODAY(),"🔔 À relancer","OK"))', align=CENTER)
        ws.merge_cells(start_row=r, start_column=8, end_row=r, end_column=9)
        put(ws, r, 10, v[5], inp=True); put(ws, r, 12, v[6], inp=True)
        ws.merge_cells(start_row=r, start_column=10, end_row=r, end_column=11); ws.merge_cells(start_row=r, start_column=12, end_row=r, end_column=13)
    nl = N0 + 1 + NN
    ws.conditional_formatting.add(f"H{N0+2}:H{nl}", FormulaRule(formula=[f'LEFT(H{N0+2},1)="🔔"'], fill=fill(PAL["pink"][0]), font=Font(name=FONT, color=RED_TXT, bold=True)))
    # overview KPIs
    pb, pe, pi, p1, p2 = REF["proj"]
    kp = [("Projets actifs", f'=COUNTIF(E{p1}:E{p2},"En cours")', "0", PAL["blue"][2], 2, 2), ("Avancement moyen", f'=IFERROR(AVERAGEIF(E{p1}:E{p2},"<>Terminé",I{p1}:I{p2}),0)', PCT, INK, 4, 2),
          ("Heures de formation", f"=SUM(E{F0+2}:E{fl})", '0" h"', INK, 6, 2), ("Livres lus", f'=COUNTIF(J{B0+2}:J{bl},"Lu")', "0", PAL["green"][2], 8, 2),
          ("Pages lues", f"=SUM(F{B0+2}:F{bl})", NUM, INK, 10, 2), ("À relancer", f'=COUNTIF(H{N0+2}:H{nl},"🔔*")', "0", RED_TXT, 12, 2)]
    for lab, f, fmt, colr, c, w in kp:
        kpi(ws, 6, c, w, lab, f, fmt, colr, big=14)
    REF["pro"] = dict(active="Pro!$B$7", avg="Pro!$D$7", hours="Pro!$F$7", books="Pro!$H$7", relance="Pro!$L$7")
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Tâches
def build_tasks(wb):
    ws = wb.create_sheet("Tâches")
    widths = {"I": 2, "J": 13, "K": 11, "L": 9, "M": 9, "N": 13, "O": 2, "P": 28, "Q": 12, "R": 12, "S": 2, "T": 10, "U": 10, "V": 10, "W": 10}
    for c in "BCDEFGH": widths[c] = 5.6
    setup(ws, "☑️ Tâches & priorités", "Calendrier, matrice d'Eisenhower, tâches du jour et à venir — tout part de la liste en bas", 23, 150, widths, tab="pink")
    T0 = 47; NT = 80; T1 = T0 + NT - 1
    TT = f"$B${T0}:$B${T1}"; TD = f"$J${T0}:$J${T1}"; TP = f"$K${T0}:$K${T1}"; TQ = f"$N${T0}:$N${T1}"
    TR = f"$P${T0}:$P${T1}"; TDUE = f"$Q${T0}:$Q${T1}"; TS = f"$R${T0}:$R${T1}"
    for c in ("Y", "Z"): ws.column_dimensions[c].hidden = True
    # calendar
    card(ws, 5, 2, 7, 12, "Calendrier", "blue")
    put(ws, 6, 2, "Année", bold=True, size=8); ws.merge_cells("B6:C6")
    put(ws, 6, 4, f"={P_YEAR}", "0", bold=True, align=CENTER); ws.merge_cells("D6:E6")
    put(ws, 6, 6, f"={P_MONTH}", "0", bold=True, align=CENTER, color=BG, size=1)
    put(ws, 6, 7, "=" + MONTH_NAME.format(m="F6"), bold=True, align=CENTER, color=PAL["blue"][2]); ws.merge_cells("G6:H6")
    for i, dname in enumerate("LMMJVSD"):
        put(ws, 7, 2 + i, dname, bold=True, size=8, align=CENTER, bg=PAL["blue"][0], color=PAL["blue"][2])
    for w in range(6):
        for dw in range(7):
            r, c = 8 + w, 2 + dw
            n = f"({w*7+dw+1}-(WEEKDAY(DATE($D$6,$F$6,1),2)-1))"
            put(ws, r, c, f'=IF(AND({n}>=1,{n}<=DAY(EOMONTH(DATE($D$6,$F$6,1),0))),{n},"")', "0", align=CENTER, size=9)
            ws.cell(r, c).border = Border(left=ws.cell(r, c).border.left, right=ws.cell(r, c).border.right, bottom=Side(style="thin", color="EEEEF2"))
        ws.row_dimensions[8 + w].height = 22
    ws.conditional_formatting.add("B8:H13", FormulaRule(formula=["AND(B8<>\"\",DATE($D$6,$F$6,B8)=TODAY())"], fill=fill(PAL["peach"][3]), font=Font(name=FONT, bold=True, color=WHITE), stopIfTrue=True))
    ws.conditional_formatting.add("B8:H13", FormulaRule(formula=[f"AND(B8<>\"\",COUNTIF({TDUE},DATE($D$6,$F$6,B8))>0)"], fill=fill(PAL["blue"][0]), font=Font(name=FONT, bold=True, color=PAL["blue"][2])))
    note(ws, 15, 2, "Orange = aujourd'hui · bleu = tâche prévue", 7)
    # KPI + donut
    card(ws, 5, 10, 5, 12, "Tâches terminées", "green")
    put(ws, 6, 10, f'=COUNTIF({TS},"Terminé")&" SUR "&COUNTIF({TT},"?*")', bold=True, align=CENTER, color=PAL["green"][2])
    ws.merge_cells("J6:N6")
    ws["Y5"] = f'=COUNTIF({TS},"Terminé")'; ws["Y6"] = f'=MAX(0,COUNTIF({TT},"?*")-Y5)'
    donut(ws, "J7", Reference(ws, min_col=25, min_row=5, max_row=6), Reference(ws, min_col=25, min_row=5, max_row=6), [PAL["green"][3], "ECEDF1"], w=6.2, h=3.6)
    put(ws, 15, 10, f'=IFERROR(Y5/(Y5+Y6),0)', PCT, bold=True, align=CENTER, size=14, color=PAL["green"][2], line=False)
    ws.merge_cells("J15:N15")
    REF["tasks"] = dict(pct="'Tâches'!$J$15", late="'Tâches'!$U$7" , today="'Tâches'!$T$7")
    # today / upcoming
    card(ws, 5, 16, 3, 12, "Aujourd'hui", "pink")
    put(ws, 6, 16, f'="À faire aujourd\'hui : "&COUNTIFS({TDUE},TODAY(),{TS},"<>Terminé",{TT},"?*")', bold=True, color=PAL["pink"][2], align=CENTER)
    ws.merge_cells("P6:R6")
    th(ws, 7, 16, ["Tâche", "Contexte", "Statut"], "pink")
    for k in range(1, 9):
        r = 7 + k
        put(ws, r, 16, f'=IFERROR(INDEX({TT},MATCH({k},$Y${T0}:$Y${T1},0)),"")')
        put(ws, r, 17, f'=IFERROR(INDEX({TR},MATCH({k},$Y${T0}:$Y${T1},0)),"")', size=8)
        put(ws, r, 18, f'=IFERROR(INDEX({TS},MATCH({k},$Y${T0}:$Y${T1},0)),"")', size=8, align=CENTER)
    card(ws, 18, 16, 3, 16, "À venir (non terminées)", "pink")
    th(ws, 19, 16, ["Tâche", "Échéance", "Priorité"], "pink")
    for k in range(1, 14):
        r = 19 + k
        key = f"SMALL($Z${T0}:$Z${T1},{k})"
        put(ws, r, 16, f'=IFERROR(INDEX({TT},MATCH({key},$Z${T0}:$Z${T1},0)),"")')
        put(ws, r, 17, f'=IFERROR(INT({key}),"")', DATE, size=8)
        put(ws, r, 18, f'=IFERROR(INDEX({TP},MATCH({key},$Z${T0}:$Z${T1},0)),"")', size=8, align=CENTER)
    for st, c in (("Très haute", "pink"), ("Haute", "peach"), ("Moyenne", "yellow"), ("Basse", "green")):
        ws.conditional_formatting.add("R20:R32", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0])))
    # KPI strip + Eisenhower
    card(ws, 5, 20, 4, 4, "Alertes", "yellow")
    kpi(ws, 6, 20, 2, "Aujourd'hui", f'=COUNTIFS({TDUE},TODAY(),{TS},"<>Terminé",{TT},"?*")', "0", PAL["pink"][2])
    kpi(ws, 6, 22, 2, "En retard", f'=COUNTIFS({TDUE},"<"&TODAY(),{TS},"<>Terminé",{TT},"?*")', "0", RED_TXT)
    REF["tasks"]["today"] = "'Tâches'!$T$7"; REF["tasks"]["late"] = "'Tâches'!$V$7"
    REF["tasks"]["week"] = f'COUNTIFS(\'Tâches\'!{TDUE},">="&TODAY(),\'Tâches\'!{TDUE},"<="&TODAY()+7,\'Tâches\'!{TS},"<>Terminé")'
    card(ws, 10, 20, 4, 24, "Matrice d'Eisenhower", "lav")
    quads = [("1 · Faire", "Urgent + important", "pink", 11), ("2 · Planifier", "Important, pas urgent", "blue", 11),
             ("3 · Déléguer", "Urgent, pas important", "yellow", 22), ("4 · Éliminer", "Ni urgent ni important", "green", 22)]
    for i, (q, sub, c, r) in enumerate(quads):
        col = 20 + (i % 2) * 2
        subcard(ws, r, col, 2, q, c)
        put(ws, r + 1, col, sub, size=7, color=MUTED, align=CENTER, line=False); ws.merge_cells(start_row=r + 1, start_column=col, end_row=r + 1, end_column=col + 1)
        ws[f"Z{5+i}"] = None
        cnt = f'COUNTIFS({TQ},"{q}",{TS},"<>Terminé")'
        put(ws, r + 8, col, f'=IFERROR({cnt}/COUNTIFS({TQ},"?*",{TS},"<>Terminé"),0)', PCT, bold=True, size=14, color=PAL[c][2], align=CENTER, line=False)
        ws.merge_cells(start_row=r + 8, start_column=col, end_row=r + 8, end_column=col + 1)
        put(ws, r + 9, col, f'={cnt}&" tâche(s)"', size=8, color=MUTED, align=CENTER, line=False)
        ws.merge_cells(start_row=r + 9, start_column=col, end_row=r + 9, end_column=col + 1)
        ws.cell(5 + 2 * i, 27, f"={cnt}")  # AA
        ws.cell(6 + 2 * i, 27, f"=MAX(0,COUNTIFS({TQ},\"?*\",{TS},\"<>Terminé\")-AA{5+2*i})")
        donut(ws, f"{CL(col)}{r+2}", Reference(ws, min_col=27, min_row=5 + 2 * i, max_row=6 + 2 * i), Reference(ws, min_col=27, min_row=5 + 2 * i, max_row=6 + 2 * i),
              [PAL[c][3], "ECEDF1"], w=3.6, h=2.9)
    for c in ("AA", "AB"): ws.column_dimensions[c].hidden = True
    # status & priority & domain tables + pies
    card(ws, 18, 2, 7, 27, "Statut des tâches", "blue")
    stats = ["Backlog", "À faire", "En cours", "En attente", "Terminé"]
    for i, s in enumerate(stats):
        r = 19 + i
        put(ws, r, 2, s, bold=True, size=8); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        put(ws, r, 6, f'=COUNTIF({TS},"{s}")', "0", align=CENTER)
        put(ws, r, 7, f'=IFERROR(F{r}/SUM($F$19:$F$23),0)', PCT, size=8); ws.merge_cells(start_row=r, start_column=7, end_row=r, end_column=8)
    pie = PieChart(); pie.add_data(Reference(ws, min_col=6, min_row=19, max_row=23)); pie.set_categories(Reference(ws, min_col=2, min_row=19, max_row=23))
    color_points(pie.series[0], [PAL["grey"][3], PAL["peach"][3], PAL["blue"][3], PAL["yellow"][3], PAL["green"][3]]); pie.dataLabels = pie_labels()
    ws.add_chart(finish(pie, 7.6, 5.2, None, "r"), "B25")
    prios = ["Très haute", "Haute", "Moyenne", "Basse"]
    card(ws, 18, 10, 5, 27, "Priorités & domaines", "green")
    for i, p in enumerate(prios):
        r = 19 + i
        put(ws, r, 10, p, bold=True, size=8); ws.merge_cells(start_row=r, start_column=10, end_row=r, end_column=11)
        put(ws, r, 12, f'=COUNTIFS({TP},"{p}",{TS},"<>Terminé")', "0", align=CENTER)
        barcell(ws, r, 13, f"L{r}/MAX(1,MAX($L$19:$L$22))", "green", 10, merge=2)
    pie2 = PieChart(); pie2.add_data(Reference(ws, min_col=12, min_row=19, max_row=22)); pie2.set_categories(Reference(ws, min_col=10, min_row=19, max_row=22))
    color_points(pie2.series[0], [PAL["pink"][3], PAL["peach"][3], PAL["yellow"][3], PAL["green"][3]]); pie2.dataLabels = pie_labels()
    ws.add_chart(finish(pie2, 8.6, 5.2, None, "r"), "J24")
    # task list
    card(ws, T0 - 2, 2, 22, NT + 2, "Liste des tâches", "pink")
    th(ws, T0 - 1, 2, ["Tâche", "", "", "", "", "", "", "", "Domaine", "Priorité", "Urgent", "Important", "Quadrant (auto)", "",
                       "Contexte / responsable", "Échéance", "Statut", "", "Notes", "", "", ""], "pink")
    ws.merge_cells(start_row=T0 - 1, start_column=2, end_row=T0 - 1, end_column=8)
    ws.merge_cells(start_row=T0 - 1, start_column=20, end_row=T0 - 1, end_column=23)
    tasks = [("Envoyer le devis client", "Carrière", "Très haute", "✓", "✓", "Moi", 0, "En cours"),
             ("Payer la facture d'électricité", "Finances", "Haute", "✓", "✓", "Moi", 0, "À faire"),
             ("Préparer la présentation annuelle", "Carrière", "Haute", "", "✓", "Moi", 5, "À faire"),
             ("Réserver le contrôle technique", "Maison", "Moyenne", "✓", "", "Garage", 3, "À faire"),
             ("Appeler la banque (prêt immo)", "Finances", "Moyenne", "", "✓", "Conseillère", 9, "Backlog"),
             ("Inscription semi-marathon", "Santé & sport", "Haute", "", "✓", "Moi", 2, "Terminé"),
             ("Trier les mails", "Carrière", "Basse", "✓", "", "Assistant", 1, "En attente"),
             ("Acheter cadeau anniversaire Léa", "Relations", "Moyenne", "✓", "✓", "Moi", 4, "À faire"),
             ("Mettre à jour le CV", "Carrière", "Moyenne", "", "✓", "Moi", 12, "Backlog"),
             ("Ranger le garage", "Maison", "Basse", "", "", "Moi", 20, "Backlog"),
             ("Déclarer les revenus side business", "Finances", "Haute", "", "✓", "Comptable", 15, "À faire"),
             ("Prendre RDV dentiste", "Santé & sport", "Moyenne", "", "✓", "Moi", -2, "À faire"),
             ("Planifier les vacances d'hiver", "Loisirs", "Basse", "", "", "Moi", 25, "Backlog"),
             ("Faire la revue hebdomadaire", "Mental", "Haute", "", "✓", "Moi", 2, "À faire"),
             ("Renouveler la mutuelle", "Finances", "Moyenne", "✓", "", "Moi", -5, "Terminé"),
             ("Finir module 4 formation GA4", "Apprentissage", "Haute", "", "✓", "Moi", 6, "En cours"),
             ("Bénévolat — inscription asso", "Contribution", "Basse", "", "✓", "Asso", 18, "Backlog"),
             ("Commander la lampe de bureau", "Maison", "Basse", "", "", "Moi", 0, "Terminé")]
    for i in range(NT):
        r = T0 + i
        v = tasks[i] if i < len(tasks) else (None,) * 8
        put(ws, r, 2, v[0], inp=True, bold=True)
        for c in range(3, 9): put(ws, r, c, None)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        put(ws, r, 9, None)
        put(ws, r, 10, v[1], inp=True); put(ws, r, 11, v[2], inp=True, align=CENTER)
        put(ws, r, 12, v[3], inp=True, align=CENTER); put(ws, r, 13, v[4], inp=True, align=CENTER)
        put(ws, r, 14, f'=IF(B{r}="","",IF(AND({done(f"L{r}")},{done(f"M{r}")}),"1 · Faire",IF({done(f"M{r}")},"2 · Planifier",IF({done(f"L{r}")},"3 · Déléguer","4 · Éliminer"))))', size=8, align=CENTER)
        put(ws, r, 15, None)
        put(ws, r, 16, v[5], inp=True)
        put(ws, r, 17, (TODAY + dt.timedelta(days=v[6])) if v[6] is not None else None, DATE, inp=True)
        put(ws, r, 18, v[7], inp=True, align=CENTER)
        put(ws, r, 19, None)
        for c in range(20, 24): put(ws, r, c, None, inp=True)
        ws.merge_cells(start_row=r, start_column=20, end_row=r, end_column=23)
        ws[f"Y{r}"] = f'=IF(AND(B{r}<>"",Q{r}=TODAY(),R{r}<>"Terminé"),MAX($Y${T0-1}:Y{r-1})+1,"")'
        ws[f"Z{r}"] = f'=IF(AND(B{r}<>"",Q{r}<>"",Q{r}>=TODAY(),R{r}<>"Terminé"),Q{r}+ROW()/100000,"")'
    dv_list(ws, LISTS["Domaines de vie"], f"J{T0}:J{T1}"); dv_list(ws, LISTS["Priorités"], f"K{T0}:K{T1}"); dv_list(ws, LISTS["Statuts"], f"R{T0}:R{T1}")
    checks(ws, f"L{T0}:M{T1}", "pink")
    for st, c in (("Terminé", "green"), ("En cours", "blue"), ("En attente", "yellow"), ("À faire", "peach"), ("Backlog", "grey")):
        ws.conditional_formatting.add(f"R{T0}:R{T1}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], bold=True)))
    for q, c in (("1 · Faire", "pink"), ("2 · Planifier", "blue"), ("3 · Déléguer", "yellow"), ("4 · Éliminer", "green")):
        ws.conditional_formatting.add(f"N{T0}:N{T1}", CellIsRule(operator="equal", formula=[f'"{q}"'], fill=fill(PAL[c][0])))
    for st, c in (("Très haute", "pink"), ("Haute", "peach"), ("Moyenne", "yellow"), ("Basse", "green")):
        ws.conditional_formatting.add(f"K{T0}:K{T1}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=fill(PAL[c][0])))
    ws.conditional_formatting.add(f"Q{T0}:Q{T1}", FormulaRule(formula=[f'AND(Q{T0}<>"",Q{T0}<TODAY(),R{T0}<>"Terminé")'], font=Font(name=FONT, color=RED_TXT, bold=True)))
    ws.conditional_formatting.add(f"B{T0}:B{T1}", FormulaRule(formula=[f'R{T0}="Terminé"'], font=Font(name=FONT, color="B5B8C2", strike=True)))
    ws.freeze_panes = "A5"
    return ws


# ===================================================================== Planning
ACT_COL = {"Travail": "blue", "Sport": "green", "Apprentissage": "lav", "Repos": "mint", "Social": "pink", "Admin": "yellow", "Perso": "peach", "Trajet": "grey"}


def build_planning(wb):
    ws = wb.create_sheet("Planning")
    widths = {"B": 8, "J": 2, "K": 8, "L": 30, "M": 14, "N": 11, "O": 11}
    for c in "CDEFGHI": widths[c] = 13
    setup(ws, "🗓️ Planning & time blocking", "Ta journée, ta semaine type et tes routines — choisis une activité dans la liste pour colorer le créneau", 15, 90, widths, tab="mint")
    # week planner
    HRS = list(range(6, 24))
    card(ws, 5, 2, 8, len(HRS) + 3, "Semaine type", "mint")
    th(ws, 6, 2, ["Heure", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"], "mint")
    plan = {6: ["Sport", "Repos", "Sport", "Repos", "Sport", "Repos", "Repos"], 7: ["Perso"] * 5 + ["Repos", "Repos"],
            8: ["Trajet"] * 5 + ["Sport", "Repos"], 9: ["Travail"] * 5 + ["Sport", "Perso"], 10: ["Travail"] * 5 + ["Perso", "Social"],
            11: ["Travail"] * 5 + ["Admin", "Social"], 12: ["Repos"] * 5 + ["Social", "Social"], 13: ["Travail"] * 5 + ["Perso", "Repos"],
            14: ["Travail"] * 5 + ["Perso", "Repos"], 15: ["Travail"] * 5 + ["Apprentissage", "Perso"], 16: ["Travail"] * 4 + ["Admin", "Apprentissage", "Perso"],
            17: ["Travail"] * 5 + ["Social", "Admin"], 18: ["Trajet"] * 5 + ["Social", "Apprentissage"], 19: ["Sport", "Apprentissage", "Repos", "Sport", "Social", "Social", "Perso"],
            20: ["Perso", "Perso", "Apprentissage", "Perso", "Social", "Social", "Perso"], 21: ["Apprentissage", "Repos", "Perso", "Apprentissage", "Social", "Social", "Admin"],
            22: ["Repos"] * 7, 23: ["Repos"] * 7}
    for i, h in enumerate(HRS):
        r = 7 + i
        put(ws, r, 2, f"{h:02d}:00", bold=True, align=CENTER, color=MUTED, size=8)
        for j in range(7):
            put(ws, r, 3 + j, plan[h][j], inp=True, align=CENTER, size=8)
        ws.row_dimensions[r].height = 18
    gl = 6 + len(HRS)
    dv_list(ws, LISTS["Activités"], f"C7:I{gl}")
    for a, c in ACT_COL.items():
        ws.conditional_formatting.add(f"C7:I{gl}", CellIsRule(operator="equal", formula=[f'"{a}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], size=8, bold=True)))
        ws.conditional_formatting.add(f"M20:M37", CellIsRule(operator="equal", formula=[f'"{a}"'], fill=fill(PAL[c][0]), font=Font(name=FONT, color=PAL[c][2], size=9, bold=True)))
    ws.conditional_formatting.add(f"C6:I6", FormulaRule(formula=["COLUMN(C6)-2=WEEKDAY(TODAY(),2)"], fill=fill(PAL["mint"][3]), font=Font(name=FONT, color=WHITE, bold=True)))
    # hours per activity
    S0 = gl + 3
    card(ws, S0, 2, 8, 14, "Heures par activité (semaine)", "mint")
    th(ws, S0 + 1, 2, ["", "Activité", "Heures", "%", "", "", "", ""], "mint")
    for i, (a, c) in enumerate(ACT_COL.items()):
        r = S0 + 2 + i
        put(ws, r, 2, None)
        put(ws, r, 3, a, bold=True, color=PAL[c][2], bg=PAL[c][0])
        put(ws, r, 4, f'=COUNTIF($C$7:$I${gl},C{r})', '0" h"', align=CENTER)
        put(ws, r, 5, f'=IFERROR(D{r}/SUM($D${S0+2}:$D${S0+9}),0)', PCT, align=CENTER)
    pie = PieChart(); pie.add_data(Reference(ws, min_col=4, min_row=S0 + 2, max_row=S0 + 9)); pie.set_categories(Reference(ws, min_col=3, min_row=S0 + 2, max_row=S0 + 9))
    color_points(pie.series[0], [PAL[c][3] for c in ACT_COL.values()]); pie.dataLabels = pie_labels()
    ws.add_chart(finish(pie, 9.5, 5.6, None, "r"), f"F{S0+1}")
    # today
    card(ws, 5, 11, 5, 12, "Aujourd'hui", "mint")
    ws.merge_cells("K6:K8")
    x = ws["K6"]; x.value = "=DAY(TODAY())"; x.font = font(26, True, INK); x.alignment = CENTER
    for r in range(6, 9): ws.cell(r, 11).fill = fill("ECEDF1")
    put(ws, 6, 12, "=" + DOW.format(d="TODAY()").replace('"Lun"', '"Lundi"').replace('"Mar"', '"Mardi"').replace('"Mer"', '"Mercredi"').replace('"Jeu"', '"Jeudi"').replace('"Ven"', '"Vendredi"').replace('"Sam"', '"Samedi"').replace('"Dim"', '"Dimanche"'), bold=True, size=13, line=False)
    put(ws, 7, 12, "=" + MONTH_NAME.format(m="MONTH(TODAY())") + '&" "&YEAR(TODAY())', color=MUTED, line=False)
    subcard(ws, 9, 12, 4, "🎯 Tâche principale du jour", "mint")
    put(ws, 10, 12, "Envoyer le devis client", inp=True, bold=True, align=CENTER, size=11); ws.merge_cells("L10:O10")
    ws.row_dimensions[10].height = 26
    subcard(ws, 11, 12, 4, "Top 3 priorités", "mint")
    tops = [("Envoyer le devis client", "✓"), ("Séance de sport 18h30", ""), ("Revue budget hebdo", "")]
    for i, (t, d) in enumerate(tops):
        r = 12 + i
        put(ws, r, 11, d, inp=True, align=CENTER, bold=True)
        put(ws, r, 12, t, inp=True); ws.merge_cells(start_row=r, start_column=12, end_row=r, end_column=15)
    checks(ws, "K12:K14", "mint")
    note(ws, 15, 11, "Coche ✓ quand c'est fait", 5)
    REF["today"] = dict(main="Planning!$L$10", tops=[("Planning!$L$12", "Planning!$K$12"), ("Planning!$L$13", "Planning!$K$13"), ("Planning!$L$14", "Planning!$K$14")])
    # time blocking
    card(ws, 18, 11, 5, 21, "Time blocking du jour", "mint")
    th(ws, 19, 11, ["Heure", "Description", "Type", "Fait", ""], "mint")
    tb = [("07:00", "Routine du matin + méditation", "Perso"), ("08:00", "Trajet + podcast", "Trajet"), ("09:00", "Deep work : devis client", "Travail"),
          ("11:00", "Réunions d'équipe", "Travail"), ("12:30", "Déjeuner + marche", "Repos"), ("14:00", "Emails & admin", "Admin"),
          ("15:00", "Projet refonte site", "Travail"), ("17:30", "Trajet", "Trajet"), ("18:30", "Musculation", "Sport"),
          ("20:00", "Dîner", "Perso"), ("21:00", "Cours d'anglais", "Apprentissage"), ("22:30", "Lecture + coucher", "Repos")]
    for i in range(18):
        r = 20 + i
        v = tb[i] if i < len(tb) else (None,) * 3
        put(ws, r, 11, v[0], inp=True, align=CENTER, bold=True); put(ws, r, 12, v[1], inp=True); put(ws, r, 13, v[2], inp=True, align=CENTER)
        put(ws, r, 14, "✓" if i < 4 else None, inp=True, align=CENTER); put(ws, r, 15, None)
    dv_list(ws, LISTS["Activités"], "M20:M37")
    checks(ws, "N20:N37", "mint")
    # events
    card(ws, 40, 11, 5, 12, "Événements à venir", "mint")
    th(ws, 41, 11, ["J-", "Événement", "Date", "Heure", "Lieu"], "mint")
    ev = [("Anniversaire de Léa", 4, "19:00", "Restaurant"), ("Dentiste", 7, "10:00", "Cabinet"), ("Réunion bilan annuel", 12, "14:00", "Bureau"),
          ("Week-end ski", 35, "", "Alpes"), ("Semi-marathon", 150, "08:30", "Paris")]
    for i in range(9):
        r = 42 + i
        v = ev[i] if i < len(ev) else (None,) * 4
        put(ws, r, 11, f'=IF(M{r}="","",M{r}-TODAY())', "0", bold=True)
        put(ws, r, 12, v[0], inp=True); put(ws, r, 13, (TODAY + dt.timedelta(days=v[1])) if v[1] is not None else None, DATE, inp=True)
        put(ws, r, 14, v[2], inp=True, align=CENTER); put(ws, r, 15, v[3], inp=True)
    ws.conditional_formatting.add("K42:K50", CellIsRule(operator="between", formula=["0", "7"], fill=fill(PAL["pink"][0]), font=Font(name=FONT, color=RED_TXT, bold=True)))
    # routines
    R0 = S0 + 16
    for k, (title, items, c0) in enumerate([("☀️ Routine du matin", ["Verre d'eau au réveil", "5 min d'étirements", "Méditation 10 min", "Journal : 3 gratitudes",
                                                                      "Petit-déjeuner protéiné", "Revoir mes 3 priorités"], 2),
                                             ("🌙 Routine du soir", ["Ranger 10 min", "Préparer la journée de demain", "Couper les écrans 22h", "Lecture 20 pages",
                                                                     "Noter mes dépenses", "Coucher avant 23h"], 6)]):
        card(ws, R0, c0, 4, 9, title, "mint")
        for i, it in enumerate(items):
            r = R0 + 1 + i
            put(ws, r, c0, "✓" if i < 3 else None, inp=True, align=CENTER)
            put(ws, r, c0 + 1, it, inp=True); ws.merge_cells(start_row=r, start_column=c0 + 1, end_row=r, end_column=c0 + 3)
        checks(ws, f"{CL(c0)}{R0+1}:{CL(c0)}{R0+6}", "mint")
        put(ws, R0 + 7, c0, f'={count_done(f"{CL(c0)}{R0+1}:{CL(c0)}{R0+6}")}&" / 6"', bold=True, align=CENTER, color=PAL["mint"][2])
        barcell(ws, R0 + 7, c0 + 1, f'{count_done(f"{CL(c0)}{R0+1}:{CL(c0)}{R0+6}")}/6', "mint", 12, merge=3)
    ws.freeze_panes = "A5"
    return ws
