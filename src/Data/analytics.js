// Calculs métier purs (aucun affichage ici) : CA, couverts, marges, stocks, achats.

import { addDaysISO, parseISODate, toISODate, weekdayShort, formatDayMonth, MONTH_NAMES_SHORT, round2, WEEK_DAYS } from '../utils/format';

export const CATEGORY_KEYS = ['food', 'drinks', 'desserts'];
export const CATEGORY_LABELS = { food: 'Nourriture', drinks: 'Boissons', desserts: 'Desserts' };
export const CATEGORY_COLORS = { food: '#566e83', drinks: '#cfb285', desserts: '#a8badb' };
export const PAYMENT_KEYS = ['cb', 'tickets', 'especes', 'cheque'];
export const PAYMENT_LABELS = { cb: 'Carte bancaire', tickets: 'Tickets restaurant', especes: 'Espèces', cheque: 'Chèques' };
export const PAYMENT_COLORS = { cb: '#cfb285', tickets: '#566e83', especes: '#a8badb', cheque: '#7a8793' };
export const SERVICE_LABELS = { lunch: 'Midi', dinner: 'Soir' };

export const PERIOD_OPTIONS = [
  { value: 'today', label: "Aujourd'hui" },
  { value: 'week', label: 'Cette semaine' },
  { value: 'month', label: 'Ce mois' },
  { value: 'year', label: 'Cette année' },
];

export const PERIOD_PHRASES = { today: "aujourd'hui", yesterday: 'hier', week: '7 derniers jours', month: 'ce mois', year: 'cette année' };

export function indexDays(days) {
  const map = new Map();
  days.forEach((d) => map.set(d.date, d));
  return map;
}

function daysInMonth(year, monthIndex) {
  return new Date(year, monthIndex + 1, 0).getDate();
}

export function periodRange(period, refIso) {
  switch (period) {
    case 'yesterday': {
      const y = addDaysISO(refIso, -1);
      return { from: y, to: y };
    }
    case 'week':
      return { from: addDaysISO(refIso, -6), to: refIso };
    case '30days':
      return { from: addDaysISO(refIso, -29), to: refIso };
    case 'month':
      return { from: `${refIso.slice(0, 8)}01`, to: refIso };
    case 'year':
      return { from: `${refIso.slice(0, 5)}01-01`, to: refIso };
    default:
      return { from: refIso, to: refIso };
  }
}

// Période équivalente précédente (hier, 7 jours avant, mois précédent au même jour, année précédente)
export function previousPeriodRange(period, refIso) {
  if (period === 'week') return periodRange('week', addDaysISO(refIso, -7));
  if (period === '30days') return periodRange('30days', addDaysISO(refIso, -30));
  if (period === 'month') {
    const d = parseISODate(refIso);
    const prevMonth = new Date(d.getFullYear(), d.getMonth() - 1, 1);
    const day = Math.min(d.getDate(), daysInMonth(prevMonth.getFullYear(), prevMonth.getMonth()));
    return periodRange('month', toISODate(new Date(prevMonth.getFullYear(), prevMonth.getMonth(), day)));
  }
  if (period === 'year') {
    const prev = `${Number(refIso.slice(0, 4)) - 1}${refIso.slice(4)}`;
    return periodRange('year', prev === `${Number(refIso.slice(0, 4)) - 1}-02-29` ? prev.replace('29', '28') : prev);
  }
  return periodRange('today', addDaysISO(refIso, -1));
}

export function eachDay(from, to) {
  const list = [];
  let d = from;
  while (d <= to) {
    list.push(d);
    d = addDaysISO(d, 1);
  }
  return list;
}

// filters : { service: 'all'|'lunch'|'dinner', category: 'all'|'food'|…, payment: 'all'|'cb'|… }
export function dayRevenue(day, filters = {}) {
  if (!day) return 0;
  const services = filters.service === 'lunch' || filters.service === 'dinner' ? [filters.service] : ['lunch', 'dinner'];
  const cats = filters.category && filters.category !== 'all' ? [filters.category] : CATEGORY_KEYS;
  let total = 0;
  services.forEach((s) => cats.forEach((c) => { total += day[s][c]; }));
  if (filters.payment && filters.payment !== 'all') total *= day.payments[filters.payment] || 0;
  return total;
}

export function dayCovers(day, service = 'all') {
  if (!day) return 0;
  if (service === 'lunch') return day.lunch.covers;
  if (service === 'dinner') return day.dinner.covers;
  return day.lunch.covers + day.dinner.covers;
}

export function summarize(dayIndex, range, filters = {}) {
  const result = {
    revenue: 0, grossRevenue: 0, serviceRevenue: 0, covers: 0, lunchCovers: 0, dinnerCovers: 0, cost: 0, days: 0,
    byCategory: { food: 0, drinks: 0, desserts: 0 },
    byPayment: { cb: 0, tickets: 0, especes: 0, cheque: 0 },
  };
  eachDay(range.from, range.to).forEach((iso) => {
    const day = dayIndex.get(iso);
    if (!day) return;
    const full = dayRevenue(day);
    result.days += 1;
    result.revenue += dayRevenue(day, filters);
    result.grossRevenue += full;
    result.serviceRevenue += dayRevenue(day, { service: filters.service });
    result.cost += full * day.costRatio;
    result.covers += dayCovers(day, filters.service);
    result.lunchCovers += day.lunch.covers;
    result.dinnerCovers += day.dinner.covers;
    CATEGORY_KEYS.forEach((c) => { result.byCategory[c] += dayRevenue(day, { ...filters, category: c }); });
    PAYMENT_KEYS.forEach((p) => { result.byPayment[p] += dayRevenue(day, { ...filters, payment: p }); });
  });
  result.avgTicket = result.covers ? result.serviceRevenue / result.covers : 0;
  result.margin = result.grossRevenue ? (1 - result.cost / result.grossRevenue) * 100 : 0;
  result.avgCoversPerDay = result.days ? result.covers / result.days : 0;
  result.avgRevenuePerDay = result.days ? result.revenue / result.days : 0;
  return result;
}

const HOURLY_SHARES = {
  lunch: [['12h', 0.25], ['13h', 0.45], ['14h', 0.3]],
  dinner: [['19h', 0.2], ['20h', 0.4], ['21h', 0.3], ['22h', 0.1]],
};

// Série de CA : heures (aujourd'hui), jours (semaine, mois) ou mois (année)
export function revenueSeries(dayIndex, period, refIso, filters = {}) {
  if (period === 'today' || period === 'yesterday') {
    const day = dayIndex.get(period === 'today' ? refIso : addDaysISO(refIso, -1));
    const rows = [];
    ['lunch', 'dinner'].forEach((service) => {
      if (filters.service && filters.service !== 'all' && filters.service !== service) return;
      const total = dayRevenue(day, { ...filters, service });
      HOURLY_SHARES[service].forEach(([hour, share]) => {
        rows.push({ key: `${service}-${hour}`, tick: `${hour}\n${SERVICE_LABELS[service].toLowerCase()}`, label: `${hour} (${SERVICE_LABELS[service].toLowerCase()})`, value: Math.round(total * share) });
      });
    });
    return rows;
  }
  if (period === 'year') {
    const year = Number(refIso.slice(0, 4));
    const lastMonth = Number(refIso.slice(5, 7)) - 1;
    return MONTH_NAMES_SHORT.slice(0, lastMonth + 1).map((name, m) => {
      const from = toISODate(new Date(year, m, 1));
      const to = m === lastMonth ? refIso : toISODate(new Date(year, m + 1, 0));
      const value = eachDay(from, to).reduce((sum, iso) => sum + dayRevenue(dayIndex.get(iso), filters), 0);
      return { key: from, tick: name, label: `${name} ${year}`, value: Math.round(value) };
    });
  }
  const range = periodRange(period, refIso);
  return eachDay(range.from, range.to).map((iso) => ({
    key: iso,
    tick: period === 'week' ? `${weekdayShort(iso)}\n${formatDayMonth(iso)}` : iso.slice(8),
    label: `${weekdayShort(iso)} ${formatDayMonth(iso)}`,
    value: Math.round(dayRevenue(dayIndex.get(iso), filters)),
  }));
}

export function coversSeries(dayIndex, period, refIso, capacity = 80) {
  const toRow = (key, tick, label, lunch, dinner, days = 1) => ({
    key, tick, label, lunch, dinner, total: lunch + dinner,
    lunchRate: capacity ? Math.round((lunch / (capacity * days)) * 100) : 0,
    dinnerRate: capacity ? Math.round((dinner / (capacity * days)) * 100) : 0,
  });
  if (period === 'year') {
    const year = Number(refIso.slice(0, 4));
    const lastMonth = Number(refIso.slice(5, 7)) - 1;
    return MONTH_NAMES_SHORT.slice(0, lastMonth + 1).map((name, m) => {
      const from = toISODate(new Date(year, m, 1));
      const to = m === lastMonth ? refIso : toISODate(new Date(year, m + 1, 0));
      const days = eachDay(from, to);
      const lunch = days.reduce((s, iso) => s + dayCovers(dayIndex.get(iso), 'lunch'), 0);
      const dinner = days.reduce((s, iso) => s + dayCovers(dayIndex.get(iso), 'dinner'), 0);
      return toRow(from, name, `${name} ${year}`, lunch, dinner, days.length);
    });
  }
  const range = periodRange(period === 'today' ? 'week' : period, refIso);
  return eachDay(range.from, range.to).map((iso) => {
    const day = dayIndex.get(iso);
    const tick = period === 'week' || period === 'today' ? weekdayShort(iso) : iso.slice(8);
    return toRow(iso, tick, `${weekdayShort(iso)} ${formatDayMonth(iso)}`, dayCovers(day, 'lunch'), dayCovers(day, 'dinner'));
  });
}

// Moyenne des couverts par jour de semaine sur une période
export function coversByWeekday(dayIndex, range) {
  const buckets = WEEK_DAYS.map((d) => ({ tick: d.label, lunch: 0, dinner: 0, count: 0 }));
  eachDay(range.from, range.to).forEach((iso) => {
    const day = dayIndex.get(iso);
    if (!day) return;
    const idx = (parseISODate(iso).getDay() + 6) % 7;
    buckets[idx].lunch += day.lunch.covers;
    buckets[idx].dinner += day.dinner.covers;
    buckets[idx].count += 1;
  });
  return buckets.map((b) => ({ key: b.tick, tick: b.tick, label: b.tick, lunch: b.count ? Math.round(b.lunch / b.count) : 0, dinner: b.count ? Math.round(b.dinner / b.count) : 0 }));
}

// Série courte pour les mini-courbes des cartes KPI
export function metricSeries(dayIndex, refIso, length, metric) {
  return eachDay(addDaysISO(refIso, -(length - 1)), refIso).map((iso) => {
    const day = dayIndex.get(iso);
    const revenue = dayRevenue(day);
    const covers = dayCovers(day);
    let value = revenue;
    if (metric === 'covers') value = covers;
    if (metric === 'ticket') value = covers ? revenue / covers : 0;
    if (metric === 'margin') value = day ? (1 - day.costRatio) * 100 : 0;
    return { key: iso, value: round2(value) };
  });
}

// Plats : les ventes de référence sont ajustées à l'activité de la date choisie
export function dishMetrics(dish) {
  const margin = round2(dish.price - dish.cost);
  return { margin, marginPct: dish.price ? (margin / dish.price) * 100 : 0 };
}

export function dishSalesRows(dishes, period, factor = 1) {
  return dishes.map((dish) => {
    const sales = Math.round((dish.sales?.[period] ?? 0) * factor);
    const { margin, marginPct } = dishMetrics(dish);
    return { ...dish, units: sales, revenue: round2(sales * dish.price), margin, marginPct, grossProfit: round2(sales * margin) };
  });
}

export function stockStatus(item, alertMarginPct = 0) {
  const qty = Number(item.quantity) || 0;
  if (qty <= 0) return 'rupture';
  if (qty <= Number(item.minimum) * (1 + (Number(alertMarginPct) || 0) / 100)) return 'low';
  return 'ok';
}

export const STOCK_STATUS = {
  ok: { label: 'OK', tone: 'green' },
  low: { label: 'Bientôt vide', tone: 'orange' },
  rupture: { label: 'Rupture', tone: 'red' },
};

export function purchaseTotals(purchase) {
  const ht = round2((Number(purchase.quantity) || 0) * (Number(purchase.unitPrice) || 0));
  const vatAmount = round2((ht * (Number(purchase.vat) || 0)) / 100);
  return { ht, vatAmount, ttc: round2(ht + vatAmount) };
}

export function purchasesInRange(purchases, range) {
  return purchases.filter((p) => p.date >= range.from && p.date <= range.to);
}

export function sumPurchases(list) {
  return list.reduce((acc, p) => {
    const t = purchaseTotals(p);
    acc.ht += t.ht;
    acc.ttc += t.ttc;
    acc.vat += t.vatAmount;
    return acc;
  }, { ht: 0, ttc: 0, vat: 0, count: list.length });
}
