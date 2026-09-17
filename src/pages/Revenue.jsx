import { useMemo, useState } from 'react';
import { RotateCcw, Target, BarChart3, LineChart as LineIcon } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { PageHero } from '../components/PageHero';
import { Panel, SelectBox, StatCard, Segmented, ProgressBar, Tabs } from '../components/UI';
import { RevenueBarChart, RevenueAreaChart, DonutChart } from '../components/Charts';
import {
  CATEGORY_KEYS, CATEGORY_LABELS, CATEGORY_COLORS, PAYMENT_KEYS, PAYMENT_LABELS, PAYMENT_COLORS,
  summarize, periodRange, previousPeriodRange, revenueSeries, dayRevenue, dayCovers,
} from '../data/analytics';
import { formatMoney, formatNumber, formatDayMonth, weekdayShort, percentChange, MONTH_NAMES } from '../utils/format';

const REVENUE_PERIODS = [
  { value: 'today', label: "Aujourd'hui" },
  { value: 'week', label: '7 derniers jours' },
  { value: 'month', label: 'Ce mois' },
  { value: 'year', label: 'Cette année' },
];
const DEFAULT_REVENUE_FILTERS = { period: 'week', service: 'all', category: 'all', payment: 'all' };

export default function RevenuePage() {
  const { db, dayIndex, selectedDate } = useData();
  const { route } = useNav();
  const currency = db.settings.currency;
  const [filters, setFilters] = useState(() => ({
    ...DEFAULT_REVENUE_FILTERS,
    ...(route.params.category ? { category: route.params.category } : {}),
    ...(route.params.period ? { period: route.params.period } : {}),
  }));
  const [chartType, setChartType] = useState('bar');
  const set = (key) => (value) => setFilters((f) => ({ ...f, [key]: value }));
  const dataFilters = { service: filters.service, category: filters.category, payment: filters.payment };

  const cards = [
    ['today', "CA aujourd'hui", 'vs. hier'],
    ['yesterday', 'CA hier', 'vs. avant-hier'],
    ['week', 'CA 7 jours', 'vs. 7 j. précédents'],
    ['month', 'CA du mois', 'vs. mois précédent'],
    ['year', "CA de l'année", 'vs. année précédente'],
  ].map(([period, label, changeLabel]) => {
    const cur = summarize(dayIndex, periodRange(period, selectedDate), dataFilters).revenue;
    const prevRange = period === 'yesterday' ? previousPeriodRange('today', periodRange('yesterday', selectedDate).from) : previousPeriodRange(period, selectedDate);
    const prev = summarize(dayIndex, prevRange, dataFilters).revenue;
    return { period, label, changeLabel, value: cur, change: percentChange(cur, prev) };
  });

  const current = summarize(dayIndex, periodRange(filters.period, selectedDate), dataFilters);
  const series = useMemo(() => revenueSeries(dayIndex, filters.period, selectedDate, dataFilters), [dayIndex, filters, selectedDate]); // eslint-disable-line react-hooks/exhaustive-deps

  const month = summarize(dayIndex, periodRange('month', selectedDate));
  const year = summarize(dayIndex, periodRange('year', selectedDate));
  const day = summarize(dayIndex, periodRange('today', selectedDate));
  const monthName = MONTH_NAMES[Number(selectedDate.slice(5, 7)) - 1];

  const paymentTotal = PAYMENT_KEYS.reduce((s, k) => s + current.byPayment[k], 0);
  const paymentData = PAYMENT_KEYS.map((k) => ({ key: k, name: PAYMENT_LABELS[k], value: current.byPayment[k], color: PAYMENT_COLORS[k], display: formatMoney(current.byPayment[k], currency), pct: paymentTotal ? Math.round((current.byPayment[k] / paymentTotal) * 100) : 0 }));
  const categoryTotal = CATEGORY_KEYS.reduce((s, k) => s + current.byCategory[k], 0);

  const detailRows = useMemo(() => {
    if (filters.period === 'today') return [];
    return series.map((row) => {
      if (filters.period === 'year') return { key: row.key, label: row.label, value: row.value };
      const d = dayIndex.get(row.key);
      const lunch = dayRevenue(d, { ...dataFilters, service: 'lunch' });
      const dinner = dayRevenue(d, { ...dataFilters, service: 'dinner' });
      const covers = dayCovers(d, filters.service);
      return { key: row.key, label: `${weekdayShort(row.key)} ${formatDayMonth(row.key)}`, lunch, dinner, value: row.value, covers, ticket: covers ? dayRevenue(d, { service: filters.service }) / covers : 0 };
    }).reverse();
  }, [series, filters, dayIndex]); // eslint-disable-line react-hooks/exhaustive-deps

  const activeFilters = filters.service !== 'all' || filters.category !== 'all' || filters.payment !== 'all' || filters.period !== DEFAULT_REVENUE_FILTERS.period;

  return (
    <div className="page">
      <PageHero title="Chiffre d’affaires" subtitle="Suivez vos recettes par période, par service, par catégorie et par mode de paiement." />

      <div className="toolbar">
        <SelectBox label="Période" value={filters.period} onChange={set('period')} options={REVENUE_PERIODS} />
        <Segmented label="Service" value={filters.service} onChange={set('service')} options={[{ value: 'all', label: 'Tous services' }, { value: 'lunch', label: 'Midi' }, { value: 'dinner', label: 'Soir' }]} />
        <SelectBox label="Catégorie" value={filters.category} onChange={set('category')} options={[{ value: 'all', label: 'Toutes catégories' }, ...CATEGORY_KEYS.map((k) => ({ value: k, label: CATEGORY_LABELS[k] }))]} />
        <SelectBox label="Mode de paiement" value={filters.payment} onChange={set('payment')} options={[{ value: 'all', label: 'Tous paiements' }, ...PAYMENT_KEYS.map((k) => ({ value: k, label: PAYMENT_LABELS[k] }))]} />
        {activeFilters && (
          <button type="button" className="btn btn-outline" onClick={() => setFilters(DEFAULT_REVENUE_FILTERS)}>
            <RotateCcw size={15} /> Réinitialiser
          </button>
        )}
      </div>

      <div className="stat-grid five">
        {cards.map((c) => (
          <StatCard key={c.period} label={c.label} value={formatMoney(c.value, currency)} change={c.change} changeLabel={c.changeLabel} accent={c.period === filters.period} onClick={c.period !== 'yesterday' ? () => set('period')(c.period) : undefined} />
        ))}
      </div>

      <div className="grid-2-1">
        <Panel
          title={`CA · ${REVENUE_PERIODS.find((p) => p.value === filters.period).label.toLowerCase()}`}
          actions={<Tabs label="Type de graphique" value={chartType} onChange={setChartType} options={[{ value: 'bar', label: 'Barres', icon: BarChart3 }, { value: 'area', label: 'Courbe', icon: LineIcon }]} />}
        >
          <div className="chart-summary">
            <span><strong>{formatMoney(current.revenue, currency)}</strong> sur la période</span>
            <span>{formatNumber(current.covers)} couverts</span>
            <span>Ticket moyen {formatMoney(current.avgTicket, currency, 2)}</span>
          </div>
          {chartType === 'bar'
            ? <RevenueBarChart data={series} currency={currency} height={270} barSize={series.length > 12 ? 16 : 36} />
            : <RevenueAreaChart data={series} currency={currency} height={270} goal={filters.period === 'week' || filters.period === 'month' ? db.settings.goalDay : undefined} />}
        </Panel>

        <Panel title="Objectifs" icon={Target}>
          <div className="goals">
            {[
              ["Aujourd'hui", day.revenue, db.settings.goalDay],
              [`Mois de ${monthName}`, month.revenue, db.settings.goalMonth],
              ['Année', year.revenue, db.settings.goalYear],
            ].map(([label, value, goal]) => (
              <div key={label} className="goal">
                <div className="goal-top">
                  <span>{label}</span>
                  <strong>{goal ? Math.round((value / goal) * 100) : 0} %</strong>
                </div>
                <ProgressBar value={value} max={goal} label={label} />
                <small>{formatMoney(value, currency)} sur {formatMoney(goal, currency)}</small>
              </div>
            ))}
          </div>
          <h3 className="sub-title">Par catégorie</h3>
          <ul className="bar-list">
            {CATEGORY_KEYS.map((k) => (
              <li key={k}>
                <button type="button" className={filters.category === k ? 'active' : ''} onClick={() => set('category')(filters.category === k ? 'all' : k)}>
                  <span className="bar-list-top"><span><i className="dot" style={{ background: CATEGORY_COLORS[k] }} />{CATEGORY_LABELS[k]}</span><strong>{formatMoney(current.byCategory[k], currency)}</strong></span>
                  <span className="bar-track"><span style={{ width: `${categoryTotal ? (current.byCategory[k] / categoryTotal) * 100 : 0}%`, background: CATEGORY_COLORS[k] }} /></span>
                </button>
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <div className="grid-1-2">
        <Panel title="Modes de paiement">
          <div className="split vertical">
            <DonutChart data={paymentData} size={180} centerValue={formatMoney(paymentTotal, currency)} centerLabel="encaissé" onSliceClick={(d) => set('payment')(filters.payment === d.key ? 'all' : d.key)} />
            <ul className="legend">
              {paymentData.map((d) => (
                <li key={d.key}>
                  <button type="button" className={filters.payment === d.key ? 'active' : ''} onClick={() => set('payment')(filters.payment === d.key ? 'all' : d.key)}>
                    <span className="dot" style={{ background: d.color }} />
                    <span className="legend-name">{d.name}</span>
                    <span className="legend-value">{d.pct} %</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </Panel>

        <Panel title="Détail de la période">
          {filters.period === 'today' ? (
            <table className="table">
              <thead><tr><th>Créneau</th><th className="num">CA</th></tr></thead>
              <tbody>{series.map((r) => <tr key={r.key}><td>{r.label}</td><td className="num">{formatMoney(r.value, currency)}</td></tr>)}</tbody>
            </table>
          ) : (
            <div className="table-wrap scroll-y">
              <table className="table">
                <thead>
                  <tr>
                    <th>{filters.period === 'year' ? 'Mois' : 'Jour'}</th>
                    {filters.period !== 'year' && <><th className="num">Midi</th><th className="num">Soir</th></>}
                    <th className="num">Total</th>
                    {filters.period !== 'year' && <><th className="num">Couverts</th><th className="num">Ticket moyen</th></>}
                  </tr>
                </thead>
                <tbody>
                  {detailRows.map((r) => (
                    <tr key={r.key}>
                      <td>{r.label}</td>
                      {filters.period !== 'year' && <><td className="num">{formatMoney(r.lunch, currency)}</td><td className="num">{formatMoney(r.dinner, currency)}</td></>}
                      <td className="num strong">{formatMoney(r.value, currency)}</td>
                      {filters.period !== 'year' && <><td className="num">{r.covers}</td><td className="num">{formatMoney(r.ticket, currency, 2)}</td></>}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>
    </div>
  );
}
