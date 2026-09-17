import { useMemo, useState } from 'react';
import { Download, Printer, Coins, Users, Receipt, Percent, ShoppingCart, Package, ChefHat } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { Panel, SelectBox, StatCard } from '../components/UI';
import { SimpleBarChart, ServiceBarChart, HorizontalBarChart } from '../components/Charts';
import {
  summarize, periodRange, eachDay, dayRevenue, dayCovers, coversSeries, dishSalesRows, stockStatus, STOCK_STATUS,
  purchasesInRange, purchaseTotals, sumPurchases,
} from '../data/analytics';
import { TODAY_ISO, formatMoney, formatNumber, formatPercent, formatDateShort, formatDayMonth, formatQuantity, weekdayShort, formatLongDate, MONTH_NAMES_SHORT, toISODate } from '../utils/format';
import { downloadCSV, printReport } from '../utils/export';

const REPORT_TYPES = [
  { value: 'revenue', label: "Chiffre d'affaires", icon: Coins },
  { value: 'covers', label: 'Couverts', icon: Users },
  { value: 'ticket', label: 'Ticket moyen', icon: Receipt },
  { value: 'margin', label: 'Marge brute', icon: Percent },
  { value: 'purchases', label: 'Achats', icon: ShoppingCart },
  { value: 'stock', label: 'Stocks', icon: Package },
  { value: 'dishes', label: 'Ventes par plat', icon: ChefHat },
];
const REPORT_PERIODS = [
  { value: 'week', label: '7 derniers jours' },
  { value: 'month', label: 'Ce mois' },
  { value: 'year', label: 'Cette année (par mois)' },
];

// Lignes jour par jour, ou mois par mois pour l'année
function reportBuckets(period, ref) {
  if (period !== 'year') {
    const r = periodRange(period, ref);
    return eachDay(r.from, r.to).map((iso) => ({ key: iso, label: `${weekdayShort(iso)} ${formatDayMonth(iso)}`, tick: formatDayMonth(iso), from: iso, to: iso }));
  }
  const year = Number(ref.slice(0, 4));
  const last = Number(ref.slice(5, 7)) - 1;
  return MONTH_NAMES_SHORT.slice(0, last + 1).map((name, m) => ({
    key: `${year}-${m}`, label: `${name} ${year}`, tick: name,
    from: toISODate(new Date(year, m, 1)), to: m === last ? ref : toISODate(new Date(year, m + 1, 0)),
  }));
}

function buildReport(type, period, ctx) {
  const { db, dayIndex, selectedDate } = ctx;
  const cur = db.settings.currency;
  const money = (v) => formatMoney(v, cur);
  const buckets = reportBuckets(period, selectedDate);
  const range = periodRange(period, selectedDate);
  const total = summarize(dayIndex, range);

  if (type === 'revenue' || type === 'ticket' || type === 'margin') {
    const rows = buckets.map((b) => {
      const s = summarize(dayIndex, b);
      return { key: b.key, tick: b.tick, label: b.label, lunch: dayRangeSum(dayIndex, b, (d) => dayRevenue(d, { service: 'lunch' })), dinner: dayRangeSum(dayIndex, b, (d) => dayRevenue(d, { service: 'dinner' })), revenue: s.revenue, covers: s.covers, ticket: s.avgTicket, cost: s.cost, margin: s.margin };
    });
    if (type === 'revenue') {
      return {
        summary: [['CA total', money(total.revenue)], ['CA moyen / jour', money(total.avgRevenuePerDay)], ['Nourriture', money(total.byCategory.food)], ['Boissons', money(total.byCategory.drinks)]],
        chart: { kind: 'bar', data: rows.map((r) => ({ ...r, value: Math.round(r.revenue) })), format: money, name: 'CA' },
        columns: [{ key: 'label', label: 'Période' }, { key: 'lunch', label: 'Midi', money: true }, { key: 'dinner', label: 'Soir', money: true }, { key: 'revenue', label: 'CA total', money: true }],
        rows,
      };
    }
    if (type === 'ticket') {
      return {
        summary: [['Ticket moyen', formatMoney(total.avgTicket, cur, 2)], ['CA', money(total.revenue)], ['Couverts', formatNumber(total.covers)], ['Meilleur ticket', formatMoney(Math.max(...rows.map((r) => r.ticket)), cur, 2)]],
        chart: { kind: 'bar', data: rows.map((r) => ({ ...r, value: Math.round(r.ticket * 100) / 100 })), format: (v) => formatMoney(v, cur, 2), name: 'Ticket moyen' },
        columns: [{ key: 'label', label: 'Période' }, { key: 'revenue', label: 'CA', money: true }, { key: 'covers', label: 'Couverts', number: true }, { key: 'ticket', label: 'Ticket moyen', money: true, decimals: 2 }],
        rows,
      };
    }
    return {
      summary: [['Marge brute', formatPercent(total.margin, 1)], ['CA', money(total.revenue)], ['Coût matière', money(total.cost)], ['Marge en valeur', money(total.revenue - total.cost)]],
      chart: { kind: 'bar', data: rows.map((r) => ({ ...r, value: Math.round(r.margin * 10) / 10 })), format: (v) => `${formatNumber(v, 1)} %`, name: 'Marge' },
      columns: [{ key: 'label', label: 'Période' }, { key: 'revenue', label: 'CA', money: true }, { key: 'cost', label: 'Coût matière', money: true }, { key: 'margin', label: 'Marge %', percent: true }],
      rows,
    };
  }

  if (type === 'covers') {
    const rows = period === 'year'
      ? coversSeries(dayIndex, 'year', selectedDate, db.settings.capacity)
      : buckets.map((b) => { const d = dayIndex.get(b.from); return { key: b.key, tick: weekdayShort(b.from), label: b.label, lunch: dayCovers(d, 'lunch'), dinner: dayCovers(d, 'dinner'), total: dayCovers(d) }; });
    return {
      summary: [['Couverts', formatNumber(total.covers)], ['Midi', formatNumber(total.lunchCovers)], ['Soir', formatNumber(total.dinnerCovers)], ['Moyenne / jour', formatNumber(total.avgCoversPerDay, 1)]],
      chart: { kind: 'service', data: rows },
      columns: [{ key: 'label', label: 'Période' }, { key: 'lunch', label: 'Midi', number: true }, { key: 'dinner', label: 'Soir', number: true }, { key: 'total', label: 'Total', number: true }],
      rows,
    };
  }

  if (type === 'purchases') {
    const list = purchasesInRange(db.purchases, range).sort((a, b) => b.date.localeCompare(a.date));
    const sums = sumPurchases(list);
    const rows = list.map((p) => ({ key: p.id, label: formatDateShort(p.date), supplier: p.supplier, product: p.product, ...purchaseTotals(p) }));
    const bySupplier = Object.entries(list.reduce((acc, p) => ({ ...acc, [p.supplier]: (acc[p.supplier] || 0) + purchaseTotals(p).ttc }), {}))
      .map(([label, value]) => ({ label, value: Math.round(value) })).sort((a, b) => b.value - a.value);
    return {
      summary: [['Total TTC', money(sums.ttc)], ['Total HT', money(sums.ht)], ['TVA récupérable', money(sums.vat)], ['Achats / CA', formatPercent(total.revenue ? (sums.ht / total.revenue) * 100 : 0, 1)]],
      chart: { kind: 'horizontal', data: bySupplier, format: money, name: 'Achats TTC' },
      columns: [{ key: 'label', label: 'Date' }, { key: 'supplier', label: 'Fournisseur' }, { key: 'product', label: 'Produit' }, { key: 'ht', label: 'HT', money: true, decimals: 2 }, { key: 'vatAmount', label: 'TVA', money: true, decimals: 2 }, { key: 'ttc', label: 'TTC', money: true, decimals: 2 }],
      rows,
    };
  }

  if (type === 'stock') {
    const rows = db.stock.map((i) => {
      const st = stockStatus(i, db.settings.stockAlertMargin);
      return { key: i.id, label: i.name, quantity: i.quantity, unit: i.unit, minimum: i.minimum, supplier: i.supplier, price: i.price, value: i.quantity * i.price, status: STOCK_STATUS[st].label };
    });
    const alerts = rows.filter((r) => r.status !== 'OK').length;
    return {
      summary: [['Produits', formatNumber(rows.length)], ['À réapprovisionner', formatNumber(alerts)], ['Valeur HT', money(rows.reduce((s, r) => s + r.value, 0))], ['Fournisseurs', formatNumber(new Set(rows.map((r) => r.supplier)).size)]],
      chart: { kind: 'horizontal', data: [...rows].sort((a, b) => b.value - a.value).slice(0, 8).map((r) => ({ label: r.label, value: Math.round(r.value) })), format: money, name: 'Valeur HT' },
      columns: [{ key: 'label', label: 'Produit' }, { key: 'quantity', label: 'Quantité', qty: true }, { key: 'unit', label: 'Unité' }, { key: 'minimum', label: 'Seuil', qty: true }, { key: 'supplier', label: 'Fournisseur' }, { key: 'value', label: 'Valeur HT', money: true }, { key: 'status', label: 'Statut' }],
      rows,
    };
  }

  // Ventes par plat
  const refRevenue = summarize(dayIndex, periodRange(period, TODAY_ISO)).revenue;
  const rows = dishSalesRows(db.dishes, period, refRevenue ? total.revenue / refRevenue : 1)
    .sort((a, b) => b.revenue - a.revenue)
    .map((d, i) => ({ key: d.id, rank: i + 1, label: d.name, category: d.category, units: d.units, revenue: d.revenue, marginPct: d.marginPct, grossProfit: d.grossProfit }));
  return {
    summary: [['Plats vendus', formatNumber(rows.reduce((s, r) => s + r.units, 0))], ['CA des plats', money(rows.reduce((s, r) => s + r.revenue, 0))], ['Marge dégagée', money(rows.reduce((s, r) => s + r.grossProfit, 0))], ['N° 1', rows[0]?.label || '—']],
    chart: { kind: 'horizontal', data: rows.slice(0, 8).map((r) => ({ label: r.label, value: Math.round(r.revenue) })), format: money, name: 'CA' },
    columns: [{ key: 'rank', label: '#' }, { key: 'label', label: 'Plat' }, { key: 'category', label: 'Catégorie' }, { key: 'units', label: 'Ventes', number: true }, { key: 'revenue', label: 'CA', money: true }, { key: 'marginPct', label: 'Marge %', percent: true }],
    rows,
  };
}

function dayRangeSum(dayIndex, bucket, fn) {
  return eachDay(bucket.from, bucket.to).reduce((s, iso) => s + fn(dayIndex.get(iso)), 0);
}

function formatCell(col, value, currency) {
  if (col.money) return formatMoney(value, currency, col.decimals || 0);
  if (col.percent) return formatPercent(value, 1);
  if (col.number) return formatNumber(value);
  if (col.qty) return formatQuantity(value);
  return value;
}

export default function ReportsPage() {
  const ctx = useData();
  const { db, selectedDate } = ctx;
  const { route } = useNav();
  const toast = useToast();
  const [type, setType] = useState(REPORT_TYPES.some((r) => r.value === route.params.report) ? route.params.report : 'revenue');
  const [period, setPeriod] = useState('month');
  const currency = db.settings.currency;

  const report = useMemo(() => buildReport(type, period, ctx), [type, period, ctx]);
  const meta = REPORT_TYPES.find((r) => r.value === type);
  const periodLabel = REPORT_PERIODS.find((p) => p.value === period).label;

  const exportCsv = () => {
    try {
      downloadCSV(`la-goelette_${type}_${period}_${selectedDate}.csv`, report.columns, report.rows);
      toast('Export CSV téléchargé');
    } catch (e) {
      toast("L'export CSV a échoué dans ce navigateur", 'error');
    }
  };
  const exportPdf = () => {
    try {
      printReport();
    } catch (e) {
      toast("L'impression n'est pas autorisée ici. Ouvrez l'application dans un onglet.", 'error');
    }
  };

  return (
    <div className="page">
      <PageHero title="Rapports" subtitle="Choisissez un rapport, une période, puis exportez-le en CSV ou en PDF." />

      <div className="report-types no-print" role="tablist" aria-label="Type de rapport">
        {REPORT_TYPES.map((r) => (
          <button key={r.value} type="button" role="tab" aria-selected={type === r.value} className={`report-type ${type === r.value ? 'active' : ''}`} onClick={() => setType(r.value)}>
            <r.icon size={18} />
            {r.label}
          </button>
        ))}
      </div>

      <div className="toolbar no-print">
        {type !== 'stock' && <SelectBox label="Période" value={period} onChange={setPeriod} options={REPORT_PERIODS} />}
        <div className="push-right toolbar-group">
          <button type="button" className="btn btn-outline" onClick={exportCsv}><Download size={16} /> Exporter CSV</button>
          <button type="button" className="btn btn-gold" onClick={exportPdf}><Printer size={16} /> Exporter PDF</button>
        </div>
      </div>

      <div className="print-area">
        <div className="print-header">
          <strong>{db.settings.name}</strong> · Rapport « {meta.label} » · {type === 'stock' ? 'état au' : periodLabel.toLowerCase() + ' au'} {formatLongDate(selectedDate).toLowerCase()}
        </div>

        <div className="stat-grid four">
          {report.summary.map(([label, value]) => <StatCard key={label} label={label} value={value} />)}
        </div>

        <Panel title={meta.label}>
          {report.chart.kind === 'bar' && <SimpleBarChart data={report.chart.data} height={240} valueFormatter={report.chart.format} name={report.chart.name} />}
          {report.chart.kind === 'service' && <ServiceBarChart data={report.chart.data} height={240} stacked />}
          {report.chart.kind === 'horizontal' && (report.chart.data.length
            ? <HorizontalBarChart data={report.chart.data} height={Math.max(160, report.chart.data.length * 34)} valueFormatter={report.chart.format} name={report.chart.name} />
            : <p className="panel-note">Aucune donnée sur cette période.</p>)}
        </Panel>

        <Panel title={`Détail · ${report.rows.length} ligne${report.rows.length > 1 ? 's' : ''}`} bodyClassName="no-pad-x">
          <div className="table-wrap scroll-y tall">
            <table className="table">
              <thead>
                <tr>{report.columns.map((c) => <th key={c.key} className={c.money || c.number || c.percent || c.qty ? 'num' : ''}>{c.label}</th>)}</tr>
              </thead>
              <tbody>
                {report.rows.map((row) => (
                  <tr key={row.key}>
                    {report.columns.map((c) => <td key={c.key} className={c.money || c.number || c.percent || c.qty ? 'num' : ''}>{formatCell(c, row[c.key], currency)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
