/**
 * 🌿 Life Planner — automatisations Google Sheets
 * Installation : Extensions → Apps Script → coller ce fichier → Enregistrer → recharger le Sheet.
 * Un menu « 🌿 Planner » apparaît dans la barre de menus.
 */

const CHECK_RANGES = [["Objectifs", "H62:H78"], ["Habitudes", "D19:J38"], ["Habitudes", "K19:Q38"], ["Habitudes", "R19:X38"], ["Habitudes", "Y19:AE38"], ["Habitudes", "AF19:AH38"], ["Nutrition", "F16:F55"], ["Pro", "J43:J52"], ["Tâches", "L47:M126"], ["Planning", "K12:K14"], ["Planning", "N20:N37"], ["Planning", "B44:B49"], ["Planning", "F44:F49"]];
const TX = 'Transactions', TX_FIRST = 7;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🌿 Planner')
    .addItem('🏠 Aller à l\'accueil', 'goHome')
    .addItem('📅 Afficher le mois en cours', 'setCurrentMonth')
    .addSeparator()
    .addItem('☑️ Activer les vraies cases à cocher', 'enableCheckboxes')
    .addItem('➕ Ajout rapide d\'une dépense / d\'un revenu', 'quickAdd')
    .addItem('↕️ Trier le journal par date', 'sortJournal')
    .addSeparator()
    .addItem('🔄 Nouveau jour : décocher priorités & routines', 'newDay')
    .addItem('🧺 Vider les articles achetés (courses)', 'clearBoughtGroceries')
    .addItem('🗓️ Nouveau mois : vider habitudes & journal', 'newMonth')
    .addToUi();
}

const ss = () => SpreadsheetApp.getActive();
const isChecked = v => v === true || v === '✓';

function goHome() { ss().setActiveSheet(ss().getSheetByName('Accueil')); }

function setCurrentMonth() {
  const p = ss().getSheetByName('Paramètres');
  const now = new Date();
  p.getRange('C7').setValue(now.getFullYear());
  p.getRange('C8').setValue(now.getMonth() + 1);
  ss().toast('Tous les onglets affichent maintenant le mois en cours.', '🌿 Planner');
}

/** Transforme toutes les zones « ✓ » en vraies cases à cocher Google Sheets (les ✓ existants restent cochés). */
function enableCheckboxes() {
  CHECK_RANGES.forEach(([sheet, a1]) => {
    const rng = ss().getSheetByName(sheet).getRange(a1);
    const vals = rng.getValues().map(r => r.map(isChecked));
    rng.clearDataValidations();
    rng.insertCheckboxes();
    rng.setValues(vals);
  });
  ss().toast(CHECK_RANGES.length + ' zones converties en cases à cocher.', '🌿 Planner');
}

function resetRange_(sheet, a1) {
  const rng = ss().getSheetByName(sheet).getRange(a1);
  const vals = rng.getValues().map(r => r.map(v => (v === true || v === false) ? false : ''));
  rng.setValues(vals);
}

function newDay() {
  CHECK_RANGES.filter(([s]) => s === 'Planning').forEach(([s, a1]) => resetRange_(s, a1));
  ss().toast('Priorités, time blocking et routines remis à zéro.', '🌿 Planner');
}

function clearBoughtGroceries() {
  const range = CHECK_RANGES.find(([s]) => s === 'Nutrition');
  if (!range) return;
  const sh = ss().getSheetByName('Nutrition');
  const chk = sh.getRange(range[1]);
  const first = chk.getRow(), n = chk.getNumRows(), col = chk.getColumn();
  const vals = chk.getValues();
  for (let i = n - 1; i >= 0; i--) {
    if (isChecked(vals[i][0])) {
      sh.getRange(first + i, 2, 1, 4).clearContent();
      sh.getRange(first + i, col).setValue(vals[i][0] === true ? false : '');
    }
  }
  ss().toast('Articles achetés retirés de la liste.', '🌿 Planner');
}

function newMonth() {
  const ui = SpreadsheetApp.getUi();
  if (ui.alert('Nouveau mois', 'Vider la grille d\'habitudes et le journal Mental / Bien-être ?', ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  CHECK_RANGES.filter(([s]) => s === 'Habitudes').forEach(([s, a1]) => resetRange_(s, a1));
  ss().getSheetByName('Mental').getRange('D33:I63').clearContent();
  ss().getSheetByName('Bien-être').getRange('D21:F51').clearContent();
  ss().getSheetByName('Bien-être').getRange('H21:P51').clearContent();
  setCurrentMonth();
}

function quickAdd() {
  const ui = SpreadsheetApp.getUi();
  const cats = ss().getSheetByName('Paramètres').getRange('B14:B80').getValues().flat().filter(String);
  const c = ui.prompt('Catégorie', 'Ex : ' + cats.slice(0, 8).join(', ') + '…', ui.ButtonSet.OK_CANCEL);
  if (c.getSelectedButton() !== ui.Button.OK) return;
  const cat = c.getResponseText().trim();
  if (!cats.includes(cat)) { ui.alert('Catégorie inconnue : ' + cat); return; }
  const m = ui.prompt('Montant (€)', 'Montant positif, ex : 42,50', ui.ButtonSet.OK_CANCEL);
  if (m.getSelectedButton() !== ui.Button.OK) return;
  const amount = parseFloat(m.getResponseText().replace(',', '.'));
  if (isNaN(amount) || amount < 0) { ui.alert('Montant invalide'); return; }
  const d = ui.prompt('Description (optionnel)', '', ui.ButtonSet.OK_CANCEL);
  if (d.getSelectedButton() !== ui.Button.OK) return;
  const sh = ss().getSheetByName(TX);
  const col = sh.getRange(TX_FIRST, 2, sh.getMaxRows() - TX_FIRST, 1).getValues();
  let r = col.findIndex(v => v[0] === '');
  r = r < 0 ? sh.getLastRow() + 1 : TX_FIRST + r;
  sh.getRange(r, 2, 1, 5).setValues([[new Date(), cat, d.getResponseText(), amount, 'Carte bancaire']]);
  ss().toast(`${cat} — ${amount.toFixed(2)} € ajouté (ligne ${r})`, '🌿 Planner');
}

function sortJournal() {
  const sh = ss().getSheetByName(TX);
  const col = sh.getRange(TX_FIRST, 2, sh.getMaxRows() - TX_FIRST, 1).getValues();
  const n = col.findIndex(v => v[0] === '');
  const count = n < 0 ? col.length : n;
  if (count > 1) sh.getRange(TX_FIRST, 2, count, 5).sort({ column: 2, ascending: true });
}
