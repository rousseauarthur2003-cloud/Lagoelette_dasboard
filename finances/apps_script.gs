/**
 * 💰 Finances — automatisations Google Sheets
 * Installation : Extensions → Apps Script → coller ce fichier → Enregistrer → recharger le Sheet.
 * Un menu « 💰 Finances » apparaît dans la barre.
 */

const TX = 'Transactions';
const FIRST_ROW = 5;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('💰 Finances')
    .addItem('➕ Ajout rapide d\'une transaction', 'quickAdd')
    .addItem('🔁 Copier les charges fixes du mois dernier', 'copyRecurring')
    .addItem('↕️ Trier le journal par date', 'sortJournal')
    .addSeparator()
    .addItem('📊 Aller au Dashboard', 'goDashboard')
    .addItem('📅 Dashboard → mois en cours', 'setCurrentMonth')
    .addToUi();
}

/** Première ligne vide du journal (colonne A). */
function nextRow_(sh) {
  const vals = sh.getRange(FIRST_ROW, 1, sh.getMaxRows() - FIRST_ROW + 1, 1).getValues();
  for (let i = 0; i < vals.length; i++) if (vals[i][0] === '') return FIRST_ROW + i;
  return sh.getMaxRows() + 1;
}

function quickAdd() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActive();
  const cats = ss.getSheetByName('Paramètres').getRange('B8:B60').getValues().flat().filter(String);

  const c = ui.prompt('Catégorie', 'Ex : ' + cats.slice(0, 6).join(', ') + '…', ui.ButtonSet.OK_CANCEL);
  if (c.getSelectedButton() !== ui.Button.OK) return;
  const cat = c.getResponseText().trim();
  if (!cats.includes(cat)) { ui.alert('Catégorie inconnue : ' + cat); return; }

  const m = ui.prompt('Montant (€)', 'Montant positif, ex : 42.50', ui.ButtonSet.OK_CANCEL);
  if (m.getSelectedButton() !== ui.Button.OK) return;
  const amount = parseFloat(m.getResponseText().replace(',', '.'));
  if (isNaN(amount) || amount < 0) { ui.alert('Montant invalide'); return; }

  const d = ui.prompt('Description (optionnel)', '', ui.ButtonSet.OK_CANCEL);
  if (d.getSelectedButton() !== ui.Button.OK) return;

  const sh = ss.getSheetByName(TX);
  const r = nextRow_(sh);
  sh.getRange(r, 1, 1, 5).setValues([[new Date(), cat, d.getResponseText(), amount, 'Carte bancaire']]);
  ss.toast(`${cat} — ${amount.toFixed(2)} € ajouté ligne ${r}`, '💰 Finances');
}

/**
 * Copie les opérations « fixes » du mois précédent (loyer, charges, crédits, placements,
 * salaire, abonnements) vers le mois en cours, en sautant celles déjà présentes.
 */
function copyRecurring() {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(TX);
  const last = nextRow_(sh) - 1;
  if (last < FIRST_ROW) return;
  const data = sh.getRange(FIRST_ROW, 1, last - FIRST_ROW + 1, 6).getValues();
  const fixedTypes = ['Revenu', 'Loyer & charges', 'Remboursement crédit', 'Placement'];
  const fixedCats = ['Abonnements', 'Salaire'];

  const now = new Date();
  const prev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  const sameMonth = (dt, ref) => dt instanceof Date && dt.getMonth() === ref.getMonth() && dt.getFullYear() === ref.getFullYear();

  const existing = new Set(data.filter(r => sameMonth(r[0], now)).map(r => r[1] + '|' + r[2]));
  const toAdd = data
    .filter(r => sameMonth(r[0], prev) && (fixedTypes.includes(r[5]) || fixedCats.includes(r[1])))
    .filter(r => r[1] !== 'Prime / bonus' && !existing.has(r[1] + '|' + r[2]))
    .map(r => {
      const day = Math.min(r[0].getDate(), 28);
      return [new Date(now.getFullYear(), now.getMonth(), day), r[1], r[2], r[3], r[4]];
    });

  if (!toAdd.length) { ss.toast('Rien à copier — déjà à jour.', '💰 Finances'); return; }
  sh.getRange(last + 1, 1, toAdd.length, 5).setValues(toAdd);
  ss.toast(`${toAdd.length} opérations fixes copiées.`, '💰 Finances');
}

function sortJournal() {
  const sh = SpreadsheetApp.getActive().getSheetByName(TX);
  const last = nextRow_(sh) - 1;
  if (last <= FIRST_ROW) return;
  sh.getRange(FIRST_ROW, 1, last - FIRST_ROW + 1, 5).sort({ column: 1, ascending: true });
}

function goDashboard() {
  const ss = SpreadsheetApp.getActive();
  ss.setActiveSheet(ss.getSheetByName('Dashboard'));
}

function setCurrentMonth() {
  const ss = SpreadsheetApp.getActive();
  ss.getSheetByName('Dashboard').getRange('F4').setValue(new Date().getMonth() + 1);
  goDashboard();
}

/** Optionnel : déclencheur mensuel (Apps Script → Déclencheurs → copyRecurring, mensuel, le 1er). */
