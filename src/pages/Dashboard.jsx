import { useMemo, useState } from 'react';
import { Coins, Users, Receipt, Percent, Plus, ArrowRight, Bell, Check, X, CalendarX } from 'lucide-react';
import { useData, useAlerts } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { KPICard } from '../components/KPICard';
import { Panel, SelectBox, Badge } from '../components/UI';
import { RevenueBarChart, DonutChart, ServiceBarChart } from '../components/Charts';
import { ReservationModal, RESERVATION_STATUS } from '../components/ReservationModal';
import {
  PERIOD_OPTIONS, PERIOD_PHRASES, CATEGORY_KEYS, CATEGORY_LABELS, CATEGORY_COLORS, STOCK_STATUS,
  summarize, periodRange, revenueSeries, coversSeries, metricSeries, dishSalesRows, stockStatus, purchaseTotals,
} from '../data/analytics';
import { TODAY_ISO, formatMoney, formatNumber, formatPercent, formatQuantity, formatDateShort, formatDayMonth, percentChange } from '../utils/format';

const COVERS_PERIODS = [
  { value: 'week', label: 'Cette semaine' },
  { value: 'month', label: 'Ce mois' },
  { value: 'year', label: 'Cette année' },
];

export default function DashboardPage() {
  const { db, dayIndex, selectedDate, actions } = useData();
  const { navigate } = useNav();
  const toast = useToast();
  const alerts = useAlerts();
  const currency = db.settings.currency;

  const [revenuePeriod, setRevenuePeriod] = useState('week');
  const [splitPeriod, setSplitPeriod] = useState('today');
  const [salesPeriod, setSalesPeriod] = useState('today');
  const [coversPeriod, setCoversPeriod] = useState('week');
  const [salesSort, setSalesSort] = useState('units');
  const [reservationModal, setReservationModal] = useState({ open: false, reservation: null });
  const [noteDraft, setNoteDraft] = useState(null);

  const today = summarize(dayIndex, periodRange('today', selectedDate));
  const yesterday = summarize(dayIndex, periodRange('yesterday', selectedDate));
  const isToday = selectedDate === TODAY_ISO;
  const dayWord = isToday ? "aujourd'hui" : `le ${formatDayMonth(selectedDate)}`;

  const revenueData = useMemo(() => revenueSeries(dayIndex, revenuePeriod, selectedDate), [dayIndex, revenuePeriod, selectedDate]);
  const coversData = useMemo(() => coversSeries(dayIndex, coversPeriod, selectedDate, db.settings.capacity), [dayIndex, coversPeriod, selectedDate, db.settings.capacity]);

  const split = summarize(dayIndex, periodRange(splitPeriod, selectedDate));
  const splitTotal = CATEGORY_KEYS.reduce((s, k) => s + split.byCategory[k], 0);
  const donutData = CATEGORY_KEYS.map((k) => ({
    key: k, name: CATEGORY_LABELS[k], value: split.byCategory[k], color: CATEGORY_COLORS[k],
    display: formatMoney(split.byCategory[k], currency),
    pct: splitTotal ? Math.round((split.byCategory[k] / splitTotal) * 100) : 0,
  }));

  // Ventes par plat ajustées à l'activité de la date choisie
  const salesRows = useMemo(() => {
    const ref = summarize(dayIndex, periodRange(salesPeriod, TODAY_ISO)).revenue;
    const cur = summarize(dayIndex, periodRange(salesPeriod, selectedDate)).revenue;
    const factor = ref ? cur / ref : 1;
    return dishSalesRows(db.dishes, salesPeriod, factor)
      .sort((a, b) => (b[salesSort] - a[salesSort]) || a.name.localeCompare(b.name))
      .slice(0, 5);
  }, [db.dishes, dayIndex, salesPeriod, selectedDate, salesSort]);

  const dayReservations = db.reservations
    .filter((r) => r.date === selectedDate && r.status !== 'cancelled')
    .sort((a, b) => a.time.localeCompare(b.time));

  const recentPurchases = db.purchases
    .filter((p) => p.date <= selectedDate)
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 5);

  const toggleStatus = (r) => {
    const next = r.status === 'confirmed' ? 'pending' : 'confirmed';
    actions.reservations.update(r.id, { status: next });
    toast(`${r.name} · ${r.time} : ${RESERVATION_STATUS[next].label.toLowerCase()}`, next === 'confirmed' ? 'success' : 'info');
  };

  const saveNote = () => {
    if (!noteDraft?.title?.trim()) return setNoteDraft(null);
    actions.notes.add({ title: noteDraft.title.trim(), detail: noteDraft.detail?.trim() || '', tone: 'blue' });
    toast('Note ajoutée');
    setNoteDraft(null);
  };

  const periodLabel = PERIOD_OPTIONS.find((p) => p.value === splitPeriod)?.label.toLowerCase();

  return (
    <div className="page dashboard">
      <PageHero
        title={`Bonjour ${db.settings.managerName} !`}
        subtitle={`Voici un aperçu de l’activité de ${db.settings.name} ${dayWord}.`}
      />

      <div className="kpi-grid">
        <KPICard id="ca" icon={Coins} title="Chiffre d'affaires" value={formatMoney(today.revenue, currency)} change={percentChange(today.revenue, yesterday.revenue)} series={metricSeries(dayIndex, selectedDate, 14, 'revenue')} onClick={() => navigate('revenue')} />
        <KPICard id="covers" icon={Users} title="Couverts" value={formatNumber(today.covers)} change={percentChange(today.covers, yesterday.covers)} series={metricSeries(dayIndex, selectedDate, 14, 'covers')} onClick={() => navigate('covers')} />
        <KPICard id="ticket" icon={Receipt} title="Ticket moyen" value={formatMoney(today.avgTicket, currency, 2)} change={percentChange(today.avgTicket, yesterday.avgTicket)} series={metricSeries(dayIndex, selectedDate, 14, 'ticket')} onClick={() => navigate('reports', { report: 'ticket' })} />
        <KPICard id="margin" icon={Percent} title="Marge brute" value={formatPercent(today.margin)} change={Math.round(today.margin) - Math.round(yesterday.margin)} series={metricSeries(dayIndex, selectedDate, 14, 'margin')} onClick={() => navigate('reports', { report: 'margin' })} />
      </div>

      <div className="dash-row row-2">
        <Panel
          title="Évolution du chiffre d’affaires"
          className="panel-revenue"
          actions={<SelectBox label="Période du graphique" value={revenuePeriod} onChange={setRevenuePeriod} options={PERIOD_OPTIONS} />}
        >
          <RevenueBarChart data={revenueData} currency={currency} height={210} barSize={revenueData.length > 12 ? 14 : 32} />
        </Panel>

        <Panel
          title="Répartition du CA"
          className="panel-split"
          actions={<SelectBox label="Période de la répartition" value={splitPeriod} onChange={setSplitPeriod} options={PERIOD_OPTIONS} />}
        >
          <div className="split">
            <DonutChart
              data={donutData}
              size={190}
              centerValue={formatMoney(splitTotal, currency)}
              centerLabel={periodLabel === "aujourd'hui" && !isToday ? `le ${formatDayMonth(selectedDate)}` : periodLabel}
              onSliceClick={(d) => navigate('revenue', { category: d.key, period: splitPeriod === 'today' ? 'week' : splitPeriod })}
            />
            <ul className="legend">
              {donutData.map((d) => (
                <li key={d.key}>
                  <button type="button" onClick={() => navigate('revenue', { category: d.key, period: splitPeriod === 'today' ? 'week' : splitPeriod })} title={`${d.display} — voir le détail`}>
                    <span className="dot" style={{ background: d.color }} />
                    <span className="legend-name">{d.name}</span>
                    <span className="legend-value">{d.pct} %</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </Panel>
      </div>

      <div className="dash-row row-3">
        <Panel
          title="Ventes par plat"
          className="panel-sales"
          actions={<SelectBox label="Période des ventes" value={salesPeriod} onChange={setSalesPeriod} options={PERIOD_OPTIONS} small />}
        >
          <div className="table-wrap">
            <table className="table table-dense">
              <thead>
                <tr>
                  <th className="col-rank">#</th>
                  <th>Plat</th>
                  {[['units', 'Ventes'], ['revenue', 'CA'], ['marginPct', 'Marge']].map(([key, label]) => (
                    <th key={key} className="num th-sort">
                      <button type="button" className={salesSort === key ? 'sorted' : ''} onClick={() => setSalesSort(key)}>{label}</button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {salesRows.map((row, i) => (
                  <tr key={row.id} className="row-click" onClick={() => navigate('sales', { query: row.name })}>
                    <td className="col-rank">{i + 1}</td>
                    <td className="ellipsis">{row.name}</td>
                    <td className="num">{formatNumber(row.units)}</td>
                    <td className="num">{formatMoney(row.revenue, currency)}</td>
                    <td className="num">{formatPercent(row.marginPct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button type="button" className="link panel-link" onClick={() => navigate('sales', { period: salesPeriod })}>
            Voir tous les plats <ArrowRight size={15} />
          </button>
        </Panel>

        <Panel
          title="Couverts par service"
          className="panel-covers"
          actions={<SelectBox label="Période des couverts" value={coversPeriod} onChange={setCoversPeriod} options={COVERS_PERIODS} small />}
        >
          <div className="chart-legend">
            <span><i style={{ background: '#cfb285' }} />Midi</span>
            <span><i style={{ background: '#7f9cc0' }} />Soir</span>
          </div>
          <ServiceBarChart data={coversData} height={196} barSize={coversData.length > 10 ? 6 : 12} />
        </Panel>

        <Panel
          title="Réservations du jour"
          className="panel-reservations"
          actions={
            <button type="button" className="btn btn-gold btn-sm" onClick={() => setReservationModal({ open: true, reservation: null })}>
              <Plus size={15} /> Ajouter
            </button>
          }
        >
          {dayReservations.length === 0 ? (
            <div className="empty compact">
              <CalendarX size={22} />
              <p>Aucune réservation {dayWord}.</p>
            </div>
          ) : (
            <ul className="res-list">
              {dayReservations.map((r) => (
                <li key={r.id}>
                  <button type="button" className="res-open" onClick={() => setReservationModal({ open: true, reservation: r })} title={`${r.name}${r.comment ? ` — ${r.comment}` : ''}`}>
                    <span className="res-time">{r.time}</span>
                    <span className="res-people">{r.people} pers.</span>
                  </button>
                  <Badge tone={RESERVATION_STATUS[r.status].tone} onClick={() => toggleStatus(r)} title={r.status === 'confirmed' ? 'Mettre en attente' : 'Confirmer'}>
                    {RESERVATION_STATUS[r.status].label}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
          <button type="button" className="link panel-link right" onClick={() => navigate('reservations', { date: selectedDate })}>
            Voir toutes les réservations <ArrowRight size={15} />
          </button>
        </Panel>
      </div>

      <div className="dash-row row-4">
        <Panel title="État des stocks" className="panel-stock" actions={<button type="button" className="link-muted" onClick={() => navigate('stock')}>Voir tout</button>}>
          <table className="table table-plain">
            <tbody>
              {db.stock.slice(0, 5).map((item) => {
                const st = STOCK_STATUS[stockStatus(item, db.settings.stockAlertMargin)];
                return (
                  <tr key={item.id} className="row-click" onClick={() => navigate('stock', { query: item.name })}>
                    <td className="ellipsis">{item.name}</td>
                    <td>{formatQuantity(item.quantity)} {item.unit}</td>
                    <td className="num"><Badge tone={st.tone}>{st.label}</Badge></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Panel>

        <Panel title="Achats récents" className="panel-purchases" actions={<button type="button" className="link-muted" onClick={() => navigate('stock', { tab: 'purchases' })}>Voir tout</button>}>
          <table className="table table-dense">
            <thead>
              <tr><th>Date</th><th>Fournisseur</th><th className="num">Montant</th></tr>
            </thead>
            <tbody>
              {recentPurchases.map((p) => (
                <tr key={p.id} className="row-click" onClick={() => navigate('stock', { tab: 'purchases', supplier: p.supplier })}>
                  <td>{formatDateShort(p.date)}</td>
                  <td className="ellipsis">{p.supplier}</td>
                  <td className="num">{formatMoney(purchaseTotals(p).ttc, currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        <Panel
          title="Notes & alertes"
          icon={Bell}
          className="panel-alerts"
          actions={
            <button type="button" className="icon-btn" onClick={() => setNoteDraft(noteDraft ? null : { title: '', detail: '' })} aria-label={noteDraft ? 'Fermer' : 'Ajouter une note'} title="Ajouter une note">
              {noteDraft ? <X size={16} /> : <Plus size={16} />}
            </button>
          }
        >
          {noteDraft && (
            <div className="note-form">
              <input className="input" autoFocus placeholder="Nouvelle note…" value={noteDraft.title} onChange={(e) => setNoteDraft({ ...noteDraft, title: e.target.value })} onKeyDown={(e) => e.key === 'Enter' && saveNote()} />
              <div className="note-form-row">
                <input className="input" placeholder="Détail (facultatif)" value={noteDraft.detail} onChange={(e) => setNoteDraft({ ...noteDraft, detail: e.target.value })} onKeyDown={(e) => e.key === 'Enter' && saveNote()} />
                <button type="button" className="btn btn-gold btn-sm" onClick={saveNote}>Ajouter</button>
              </div>
            </div>
          )}
          <ul className="alerts">
            {alerts.map((a) => (
              <li key={a.id}>
                <button type="button" className="alert-main" onClick={() => (a.page ? navigate(a.page, a.params) : null)} disabled={!a.page}>
                  <span className={`dot dot-${a.tone}`} />
                  <span>
                    <strong>{a.title}</strong>
                    {a.detail && <small>{a.detail}</small>}
                  </span>
                </button>
                {a.noteId && (
                  <button type="button" className="icon-btn alert-done" onClick={() => { actions.notes.remove(a.noteId); toast('Note terminée'); }} aria-label={`Marquer « ${a.title} » comme fait`} title="Marquer comme fait">
                    <Check size={15} />
                  </button>
                )}
              </li>
            ))}
            {alerts.length === 0 && <li className="dropdown-empty">Tout est en ordre.</li>}
          </ul>
        </Panel>
      </div>

      <ReservationModal
        open={reservationModal.open}
        reservation={reservationModal.reservation}
        defaultDate={selectedDate}
        onClose={() => setReservationModal({ open: false, reservation: null })}
      />
    </div>
  );
}
