// Données de démonstration réalistes pour La Goëlette.
// Chaque « collection » a la même forme que les onglets d'un futur Google Sheet
// (voir data/adapters/googleSheetsAdapter.js).

import { TODAY_ISO, addDaysISO, parseISODate, round2 } from '../utils/format';

function seededRandom(seed) {
  let a = seed;
  return function next() {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const SEASONALITY = [0.55, 0.6, 0.7, 0.85, 1.0, 1.2, 1.55, 1.65, 1.15, 0.9, 0.65, 0.7];
const WEEKDAY_FACTOR = [1.15, 0.8, 0.85, 0.9, 0.95, 1.1, 1.25]; // dim → sam
const DEFAULT_PAYMENTS = { cb: 0.66, tickets: 0.14, especes: 0.12, cheque: 0.08 };

function splitRevenue(amount, foodShare, drinksShare) {
  const food = round2(amount * foodShare);
  const drinks = round2(amount * drinksShare);
  return { food, drinks, desserts: round2(amount - food - drinks) };
}

function buildDay(date, lunchCovers, dinnerCovers, revenue, costRatio, shares, payments) {
  const total = lunchCovers + dinnerCovers || 1;
  return {
    date,
    lunch: { covers: lunchCovers, ...splitRevenue((revenue * lunchCovers) / total, shares.food, shares.drinks) },
    dinner: { covers: dinnerCovers, ...splitRevenue((revenue * dinnerCovers) / total, shares.food, shares.drinks) },
    payments,
    costRatio: round2(costRatio * 1000) / 1000,
  };
}

// Journées récentes calées sur la capture : [couverts midi, couverts soir, CA, ratio coût matière]
const DAY_OVERRIDES = {
  '2026-09-11': [33, 24, 1390, 0.33],
  '2026-09-12': [32, 25, 1395, 0.33],
  '2026-09-13': [30, 28, 1405, 0.33],
  '2026-09-14': [36, 31, 1630, 0.32],
  '2026-09-15': [35, 34, 1680, 0.33],
  '2026-09-16': [32, 36, 1640, 0.34],
  '2026-09-17': [34, 40, 1842, 0.32],
};

function generateDailyStats() {
  const rand = seededRandom(20260917);
  const days = [];
  let date = '2025-01-01';
  while (date <= TODAY_ISO) {
    const d = parseISODate(date);
    const growth = d.getFullYear() === 2025 ? 0.93 : 1;
    const factor = SEASONALITY[d.getMonth()] * WEEKDAY_FACTOR[d.getDay()] * growth;
    const lunch = Math.min(80, Math.round(36 * factor * (0.85 + rand() * 0.3)));
    const dinner = Math.min(80, Math.round(33 * factor * (0.85 + rand() * 0.3)));
    const ticket = 23 + rand() * 3;
    const shares = { food: 0.74 + rand() * 0.05, drinks: 0.17 + rand() * 0.04 };
    const cb = 0.62 + rand() * 0.08;
    const tickets = 0.1 + rand() * 0.05;
    const especes = 0.09 + rand() * 0.05;
    const cheque = Math.max(0.02, 1 - cb - tickets - especes);
    const sum = cb + tickets + especes + cheque;
    const payments = { cb: cb / sum, tickets: tickets / sum, especes: especes / sum, cheque: cheque / sum };
    const override = DAY_OVERRIDES[date];
    if (override) {
      days.push(buildDay(date, override[0], override[1], override[2], override[3], { food: 0.77, drinks: 0.19 }, DEFAULT_PAYMENTS));
    } else {
      days.push(buildDay(date, lunch, dinner, (lunch + dinner) * ticket, 0.3 + rand() * 0.04, shares, payments));
    }
    date = addDaysISO(date, 1);
  }
  return days;
}

// sales : nombre de ventes au jour de référence (TODAY_ISO) sur chaque période
function dish(id, name, category, price, cost, today) {
  const r = seededRandom(id.length * 97 + today * 13);
  return {
    id,
    name,
    category,
    price,
    cost,
    sales: {
      today,
      week: Math.round(today * (6.1 + r() * 0.8)),
      month: Math.round(today * (14.5 + r() * 2)),
      year: Math.round(today * (158 + r() * 25)),
    },
  };
}

const DISHES = [
  dish('dish-burger', 'Burger La Goëlette', 'Plats', 25, 7.25, 18),
  dish('dish-moules', 'Moules marinières', 'Plats', 24, 7.68, 16),
  dish('dish-daurade', 'Daurade royale', 'Plats', 29, 10.15, 12),
  dish('dish-tartare', 'Tartare de thon', 'Plats', 32, 10.88, 9),
  dish('dish-cesar', 'Salade César', 'Plats', 20, 5.6, 8),
  dish('dish-huitres', 'Huîtres de Vendée (6)', 'Entrées', 14, 5.2, 7),
  dish('dish-prefou', "Préfou à l'ail", 'Entrées', 7, 1.4, 7),
  dish('dish-mouclade', 'Mouclade vendéenne', 'Plats', 23, 7.4, 6),
  dish('dish-brioche', 'Brioche perdue, caramel', 'Desserts', 9, 2.2, 6),
  dish('dish-sole', 'Sole meunière', 'Plats', 36, 14.4, 5),
  dish('dish-cafe', 'Café gourmand', 'Desserts', 9.5, 2.8, 5),
  dish('dish-plateau', 'Plateau de fruits de mer', 'Plats', 48, 21, 3),
];

const RESERVATIONS = [
  ['2026-09-16', '12:30', 'Marchand', '06 12 45 78 90', 3, 'confirmed', ''],
  ['2026-09-16', '20:00', 'Petit', '06 98 74 12 30', 5, 'confirmed', 'Anniversaire'],
  ['2026-09-17', '12:00', 'Martin', '06 11 22 33 44', 4, 'confirmed', ''],
  ['2026-09-17', '12:30', 'Rousseau', '07 81 42 55 10', 2, 'confirmed', 'Terrasse si possible'],
  ['2026-09-17', '13:00', 'Famille Bernard', '06 45 67 89 01', 6, 'confirmed', '1 chaise haute'],
  ['2026-09-17', '19:00', 'Lefèvre', '06 22 18 90 43', 4, 'confirmed', ''],
  ['2026-09-17', '19:30', 'Morel', '07 66 30 21 08', 2, 'pending', ''],
  ['2026-09-17', '20:00', 'Girard', '06 70 51 44 29', 6, 'confirmed', 'Allergie crustacés (1 pers.)'],
  ['2026-09-17', '20:30', 'Dubois', '06 03 88 17 62', 4, 'confirmed', ''],
  ['2026-09-18', '12:15', 'Garnier', '06 54 32 10 98', 2, 'confirmed', ''],
  ['2026-09-18', '19:30', 'Faure', '06 77 41 23 56', 8, 'pending', 'Repas d’entreprise'],
  ['2026-09-18', '20:15', 'Chevalier', '07 12 90 34 78', 3, 'confirmed', ''],
  ['2026-09-19', '12:00', 'Lambert', '06 31 64 97 20', 4, 'pending', ''],
  ['2026-09-19', '13:00', 'Fontaine', '06 85 20 74 13', 2, 'confirmed', 'Vue mer'],
  ['2026-09-19', '19:45', 'Roux', '06 49 57 13 82', 5, 'confirmed', ''],
  ['2026-09-19', '20:30', 'Blanc', '07 58 26 39 04', 4, 'pending', ''],
  ['2026-09-20', '12:30', 'Guérin', '06 16 83 50 27', 7, 'confirmed', 'Baptême'],
  ['2026-09-20', '19:00', 'Mercier', '06 92 07 61 45', 2, 'pending', ''],
].map(([date, time, name, phone, people, status, comment], i) => ({
  id: `res-${i + 1}`,
  date,
  time,
  name,
  phone,
  people,
  service: time < '16:00' ? 'lunch' : 'dinner',
  status,
  comment,
}));

const STOCK = [
  ['Saumon fumé', 1.2, 'kg', 1, 'PassionFroid', 38.5, 'Poissonnerie'],
  ['Daurade royale', 0.8, 'kg', 0.5, 'Criée des Sables', 16.9, 'Poissonnerie'],
  ['Moules', 3.5, 'kg', 2, 'Criée des Sables', 4.2, 'Poissonnerie'],
  ['Crème liquide', 0.4, 'L', 1, 'Métro', 4.6, 'Crèmerie'],
  ['Citron', 2, 'kg', 1, 'Transgourmet', 3.1, 'Fruits & légumes'],
  ['Thon rouge', 2.1, 'kg', 1.5, 'Criée des Sables', 34, 'Poissonnerie'],
  ['Huîtres n°3', 6, 'douz.', 3, 'Criée des Sables', 9.5, 'Poissonnerie'],
  ['Beurre doux', 2.5, 'kg', 1, 'Métro', 9.8, 'Crèmerie'],
  ['Pains burger', 36, 'pièces', 24, 'Promocash', 0.55, 'Boulangerie'],
  ['Pommes de terre', 18, 'kg', 10, 'Transgourmet', 1.1, 'Fruits & légumes'],
  ['Muscadet (bouteille)', 22, 'btl', 12, 'Kenty', 6.4, 'Boissons'],
  ['Farine T55', 4, 'kg', 2, 'Métro', 1.2, 'Épicerie'],
].map(([name, quantity, unit, minimum, supplier, price, category], i) => ({
  id: `stk-${i + 1}`,
  name,
  quantity,
  unit,
  minimum,
  supplier,
  price,
  category,
}));

export const SUPPLIERS = ['Métro', 'PassionFroid', 'Transgourmet', 'Promocash', 'Criée des Sables', 'Kenty'];

function generatePurchases() {
  const rand = seededRandom(85460);
  const lines = [
    { supplier: 'Métro', product: 'Épicerie & crèmerie', vat: 5.5 },
    { supplier: 'PassionFroid', product: 'Surgelés & produits de la mer', vat: 5.5 },
    { supplier: 'Transgourmet', product: 'Fruits & légumes', vat: 5.5 },
    { supplier: 'Promocash', product: 'Boulangerie & épicerie', vat: 5.5 },
    { supplier: 'Criée des Sables', product: 'Poissons & coquillages', vat: 5.5 },
    { supplier: 'Kenty', product: 'Boissons', vat: 20 },
  ];
  const list = [];
  let date = '2026-06-01';
  let n = 0;
  while (date <= '2026-09-12') {
    const count = rand() < 0.55 ? 1 : rand() < 0.3 ? 2 : 0;
    for (let i = 0; i < count; i += 1) {
      const line = lines[Math.floor(rand() * lines.length)];
      n += 1;
      list.push({ id: `pur-g${n}`, date, supplier: line.supplier, product: line.product, quantity: 1, unit: 'lot', unitPrice: round2(120 + rand() * 380), vat: line.vat });
    }
    date = addDaysISO(date, 1);
  }
  const recent = [
    ['2026-09-17', 'Métro', 'Épicerie & crèmerie', 310.9],
    ['2026-09-16', 'PassionFroid', 'Surgelés & produits de la mer', 203.79],
    ['2026-09-15', 'Transgourmet', 'Fruits & légumes', 456.87],
    ['2026-09-14', 'Métro', 'Épicerie & crèmerie', 185.78],
    ['2026-09-13', 'Promocash', 'Boulangerie & épicerie', 293.84],
  ].map(([d, supplier, product, unitPrice], i) => ({ id: `pur-r${i + 1}`, date: d, supplier, product, quantity: 1, unit: 'lot', unitPrice, vat: 5.5 }));
  return [...recent, ...list.reverse()];
}

const TEAM = [
  { id: 'emp-1', firstName: 'Arthur', role: 'Gérant', hours: '10h – 15h / 18h – 23h', color: '#cfb285', shifts: { lun: 'repos', mar: 'journee', mer: 'journee', jeu: 'journee', ven: 'journee', sam: 'journee', dim: 'midi' } },
  { id: 'emp-2', firstName: 'Camille', role: 'Cheffe de cuisine', hours: '9h30 – 14h30 / 18h – 22h30', color: '#7f9cc0', shifts: { lun: 'repos', mar: 'repos', mer: 'journee', jeu: 'journee', ven: 'journee', sam: 'journee', dim: 'journee' } },
  { id: 'emp-3', firstName: 'Julien', role: 'Second de cuisine', hours: '10h – 15h / 18h – 23h', color: '#a8badb', shifts: { lun: 'journee', mar: 'journee', mer: 'repos', jeu: 'repos', ven: 'soir', sam: 'journee', dim: 'journee' } },
  { id: 'emp-4', firstName: 'Léa', role: 'Cheffe de rang', hours: '11h30 – 15h / 18h30 – 23h', color: '#d98f5a', shifts: { lun: 'midi', mar: 'midi', mer: 'repos', jeu: 'journee', ven: 'journee', sam: 'soir', dim: 'repos' } },
  { id: 'emp-5', firstName: 'Thomas', role: 'Serveur', hours: '11h30 – 15h / 18h30 – 23h', color: '#6fb58a', shifts: { lun: 'soir', mar: 'repos', mer: 'repos', jeu: 'soir', ven: 'journee', sam: 'journee', dim: 'journee' } },
  { id: 'emp-6', firstName: 'Inès', role: 'Commis & plonge', hours: '10h – 15h / 18h – 22h', color: '#b58ad1', shifts: { lun: 'repos', mar: 'soir', mer: 'midi', jeu: 'journee', ven: 'repos', sam: 'journee', dim: 'midi' } },
  { id: 'emp-7', firstName: 'Maxime', role: 'Barman', hours: '17h – 00h', color: '#e0c36a', shifts: { lun: 'repos', mar: 'repos', mer: 'soir', jeu: 'soir', ven: 'soir', sam: 'soir', dim: 'repos' } },
];

const NOTES = [
  { id: 'note-1', title: 'Inventaire hebdomadaire', detail: 'Prévu le 20/09', tone: 'blue' },
  { id: 'note-2', title: 'Pense à passer commande poissons', detail: 'pour le week-end.', tone: 'grey' },
];

const SETTINGS = {
  name: 'La Goëlette',
  managerName: 'Arthur',
  address: "L'Aiguillon-sur-Mer, 85460",
  phone: '02 51 00 00 00',
  email: 'contact@restaurantlagoelette.fr',
  currency: '€',
  vatFood: 10,
  vatAlcohol: 20,
  vatPurchases: 5.5,
  goalDay: 1800,
  goalMonth: 42000,
  goalYear: 420000,
  capacity: 80,
  defaultMinimum: 1,
  stockAlertMargin: 0,
  showHeroPhoto: true,
  compactMode: false,
  chartAnimations: true,
};

export function createMockDatabase() {
  return JSON.parse(
    JSON.stringify({
      dailyStats: generateDailyStats(),
      dishes: DISHES,
      reservations: RESERVATIONS,
      stock: STOCK,
      purchases: generatePurchases(),
      team: TEAM,
      notes: NOTES,
      settings: SETTINGS,
    })
  );
}
