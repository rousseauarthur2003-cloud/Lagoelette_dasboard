// Adaptateur Google Sheets — prêt à être branché.
//
// 1. Créez un Google Sheet avec un onglet par collection :
//    dailyStats, dishes, reservations, stock, purchases, team, notes, settings
// 2. La première ligne de chaque onglet contient les noms de colonnes
//    (ex. reservations : id | date | time | name | phone | people | service | status | comment)
// 3. Pour la lecture seule, une clé API suffit. Pour l'écriture, passez par un petit
//    backend (Apps Script ou serveur) : ne mettez jamais d'identifiants secrets dans le navigateur.
// 4. Dans data/dataSource.js, remplacez localAdapter par createGoogleSheetsAdapter({...}).

const SHEETS_COLLECTIONS = ['dishes', 'reservations', 'stock', 'purchases', 'team', 'notes', 'settings', 'dailyStats'];

function rowsToObjects(values = []) {
  const [header = [], ...rows] = values;
  return rows.map((row) =>
    Object.fromEntries(
      header.map((key, i) => {
        const raw = row[i] ?? '';
        const num = Number(String(raw).replace(',', '.'));
        return [key, raw !== '' && !Number.isNaN(num) && !/^0\d/.test(raw) ? num : raw];
      })
    )
  );
}

export function createGoogleSheetsAdapter({ spreadsheetId, apiKey, writeEndpoint }) {
  const base = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values`;
  return {
    id: 'google-sheets',
    label: 'Google Sheets',
    async load() {
      const entries = await Promise.all(
        SHEETS_COLLECTIONS.map(async (name) => {
          const res = await fetch(`${base}/${name}?key=${apiKey}`);
          if (!res.ok) throw new Error(`Lecture de l'onglet « ${name} » impossible (${res.status})`);
          const json = await res.json();
          return [name, rowsToObjects(json.values)];
        })
      );
      const db = Object.fromEntries(entries);
      db.settings = db.settings[0] || {};
      // Les colonnes lunch_covers, lunch_food… sont regroupées au format attendu par l'app
      db.dailyStats = db.dailyStats.map((r) => ({
        date: r.date,
        lunch: { covers: r.lunch_covers, food: r.lunch_food, drinks: r.lunch_drinks, desserts: r.lunch_desserts },
        dinner: { covers: r.dinner_covers, food: r.dinner_food, drinks: r.dinner_drinks, desserts: r.dinner_desserts },
        payments: { cb: r.pay_cb, tickets: r.pay_tickets, especes: r.pay_especes, cheque: r.pay_cheque },
        costRatio: r.cost_ratio,
      }));
      db.team = db.team.map((m) => ({ ...m, shifts: typeof m.shifts === 'string' ? JSON.parse(m.shifts) : m.shifts }));
      db.dishes = db.dishes.map((d) => ({ ...d, sales: typeof d.sales === 'string' ? JSON.parse(d.sales) : d.sales }));
      return db;
    },
    async save(collection, data) {
      if (!writeEndpoint) return false;
      const res = await fetch(writeEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ collection, data }),
      });
      return res.ok;
    },
    async reset() {
      return this.load();
    },
  };
}
