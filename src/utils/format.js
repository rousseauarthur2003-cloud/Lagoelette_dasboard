// Formats et dates — tout est en français, dates au format ISO (AAAA-MM-JJ) en interne.

export const TODAY_ISO = '2026-09-17';

export const DAY_NAMES_SHORT = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
export const WEEK_DAYS = [
  { key: 'lun', label: 'Lun', long: 'Lundi' },
  { key: 'mar', label: 'Mar', long: 'Mardi' },
  { key: 'mer', label: 'Mer', long: 'Mercredi' },
  { key: 'jeu', label: 'Jeu', long: 'Jeudi' },
  { key: 'ven', label: 'Ven', long: 'Vendredi' },
  { key: 'sam', label: 'Sam', long: 'Samedi' },
  { key: 'dim', label: 'Dim', long: 'Dimanche' },
];
export const MONTH_NAMES_SHORT = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'];
export const MONTH_NAMES = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];

export function parseISODate(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

export function toISODate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function addDaysISO(iso, n) {
  const d = parseISODate(iso);
  d.setDate(d.getDate() + n);
  return toISODate(d);
}

export function weekdayShort(iso) {
  return DAY_NAMES_SHORT[parseISODate(iso).getDay()];
}

export function capitalize(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : '';
}

export function formatLongDate(iso) {
  const d = parseISODate(iso);
  const days = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
  return capitalize(`${days[d.getDay()]} ${d.getDate()} ${MONTH_NAMES[d.getMonth()]} ${d.getFullYear()}`);
}

export function formatDayMonth(iso) {
  const [, m, d] = iso.split('-');
  return `${d}/${m}`;
}

export function formatDateShort(iso) {
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y.slice(2)}`;
}

export function formatNumber(value, decimals = 0) {
  const n = Number.isFinite(value) ? value : 0;
  return new Intl.NumberFormat('fr-FR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
    .format(n)
    .replace(/[\u202f\u00a0]/g, ' ');
}

export function formatMoney(value, currency = '€', decimals = 0) {
  const n = formatNumber(value, decimals);
  if (currency === '$' || currency === '£') return `${currency}${n}`;
  return `${n} ${currency}`;
}

export function formatPercent(value, decimals = 0) {
  return `${formatNumber(value, decimals)} %`;
}

export function formatQuantity(value) {
  const n = Number(value) || 0;
  return formatNumber(n, Number.isInteger(n) ? 0 : 1);
}

// Évolution en % tronquée (ex. +12,3 % → 12)
export function percentChange(current, previous) {
  if (!previous) return null;
  return Math.trunc(((current - previous) / previous) * 100);
}

export function round2(n) {
  return Math.round((Number(n) || 0) * 100) / 100;
}

export function uid(prefix = 'id') {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}

export function normalizeText(text) {
  return String(text || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}
