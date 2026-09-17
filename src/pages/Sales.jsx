import { useEffect, useMemo, useState } from 'react';
import { Plus, Pencil, Trash2, Search, ChefHat, Coins, Percent, Trophy } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { Panel, SelectBox, StatCard, SortableTh, Field, Badge, EmptyState } from '../components/UI';
import { Modal, ConfirmDialog } from '../components/Modal';
import { HorizontalBarChart } from '../components/Charts';
import { PERIOD_OPTIONS, summarize, periodRange, dishSalesRows } from '../data/analytics';
import { TODAY_ISO, formatMoney, formatNumber, formatPercent, normalizeText, round2 } from '../utils/format';
import { useSortedRows } from '../utils/hooks';

const DISH_CATEGORIES = ['Entrées', 'Plats', 'Desserts', 'Boissons'];
const EMPTY_DISH = { name: '', category: 'Plats', price: '', cost: '', salesToday: 0 };

function marginTone(pct) {
  if (pct >= 70) return 'green';
  if (pct >= 60) return 'gold';
  return 'orange';
}

function DishModal({ open, dish, onClose }) {
  const { actions, db } = useData();
  const toast = useToast();
  const [form, setForm] = useState(EMPTY_DISH);
  const [error, setError] = useState('');
  const currency = db.settings.currency;

  useEffect(() => {
    if (!open) return;
    setError('');
    setForm(dish ? { name: dish.name, category: dish.category, price: dish.price, cost: dish.cost, salesToday: dish.sales?.today ?? 0 } : EMPTY_DISH);
  }, [open, dish]);

  const price = Number(form.price) || 0;
  const cost = Number(form.cost) || 0;
  const margin = round2(price - cost);
  const marginPct = price ? (margin / price) * 100 : 0;

  const submit = () => {
    if (!form.name.trim()) return setError('Indiquez le nom du plat.');
    if (!(price > 0)) return setError('Le prix de vente doit être supérieur à 0.');
    if (cost < 0) return setError('Le coût matière ne peut pas être négatif.');
    const today = Math.max(0, Math.round(Number(form.salesToday) || 0));
    const base = dish?.sales || {};
    const ratio = dish?.sales?.today ? today / dish.sales.today : null;
    const sales = ratio !== null
      ? { today, week: Math.round(base.week * ratio), month: Math.round(base.month * ratio), year: Math.round(base.year * ratio) }
      : { today, week: today * 6, month: today * 15, year: today * 160 };
    const payload = { name: form.name.trim(), category: form.category, price: round2(price), cost: round2(cost), sales };
    if (dish) {
      actions.dishes.update(dish.id, payload);
      toast(`${payload.name} mis à jour`);
    } else {
      actions.dishes.add(payload);
      toast(`${payload.name} ajouté à la carte`);
    }
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={dish ? 'Modifier le plat' : 'Ajouter un plat'}
      footer={<><button type="button" className="btn btn-outline" onClick={onClose}>Annuler</button><button type="button" className="btn btn-gold" onClick={submit}>Enregistrer</button></>}
    >
      <div className="form-grid">
        <Field label="Nom du plat" span={2}>
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="ex. Bar de ligne, beurre blanc" />
        </Field>
        <Field label="Catégorie">
          <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
            {DISH_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
        </Field>
        <Field label="Ventes aujourd'hui" hint="Les autres périodes sont recalculées en proportion.">
          <input className="input" type="number" min="0" value={form.salesToday} onChange={(e) => setForm({ ...form, salesToday: e.target.value })} />
        </Field>
        <Field label={`Prix de vente TTC (${currency})`}>
          <input className="input" type="number" min="0" step="0.1" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
        </Field>
        <Field label={`Coût matière (${currency})`}>
          <input className="input" type="number" min="0" step="0.05" value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })} />
        </Field>
      </div>
      <div className="calc-box">
        <div><span>Marge</span><strong>{formatMoney(margin, currency, 2)}</strong></div>
        <div><span>Taux de marge</span><strong><Badge tone={marginTone(marginPct)}>{formatPercent(marginPct, 1)}</Badge></strong></div>
        <div><span>Coefficient</span><strong>{cost ? `× ${formatNumber(price / cost, 2)}` : '—'}</strong></div>
      </div>
      {error && <p className="form-error">{error}</p>}
    </Modal>
  );
}

export default function SalesPage() {
  const { db, dayIndex, selectedDate, actions } = useData();
  const { route } = useNav();
  const toast = useToast();
  const currency = db.settings.currency;

  const [period, setPeriod] = useState(route.params.period || 'month');
  const [category, setCategory] = useState('all');
  const [query, setQuery] = useState(route.params.query || '');
  const [editing, setEditing] = useState({ open: false, dish: null });
  const [toDelete, setToDelete] = useState(null);

  const factor = useMemo(() => {
    const ref = summarize(dayIndex, periodRange(period, TODAY_ISO)).revenue;
    const cur = summarize(dayIndex, periodRange(period, selectedDate)).revenue;
    return ref ? cur / ref : 1;
  }, [dayIndex, period, selectedDate]);

  const rows = useMemo(() => {
    const q = normalizeText(query);
    return dishSalesRows(db.dishes, period, factor).filter((d) => (category === 'all' || d.category === category) && (!q || normalizeText(d.name).includes(q)));
  }, [db.dishes, period, factor, category, query]);

  const { sorted, sort, toggleSort } = useSortedRows(rows, 'revenue');

  const totals = rows.reduce((acc, r) => ({ revenue: acc.revenue + r.revenue, units: acc.units + r.units, profit: acc.profit + r.grossProfit }), { revenue: 0, units: 0, profit: 0 });
  const top = [...rows].sort((a, b) => b.units - a.units)[0];
  const chartData = [...rows].sort((a, b) => b.revenue - a.revenue).slice(0, 8).map((r) => ({ label: r.name, value: r.revenue }));
  const periodText = PERIOD_OPTIONS.find((p) => p.value === period).label.toLowerCase();

  return (
    <div className="page">
      <PageHero title="Plats & Ventes" subtitle="Votre carte, vos marges et ce qui se vend le mieux." />

      <div className="toolbar">
        <div className="input-icon">
          <Search size={16} />
          <input className="input" placeholder="Rechercher un plat" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Rechercher un plat" />
        </div>
        <SelectBox label="Catégorie" value={category} onChange={setCategory} options={[{ value: 'all', label: 'Toutes catégories' }, ...DISH_CATEGORIES.map((c) => ({ value: c, label: c }))]} />
        <SelectBox label="Période" value={period} onChange={setPeriod} options={PERIOD_OPTIONS} />
        <button type="button" className="btn btn-gold push-right" onClick={() => setEditing({ open: true, dish: null })}><Plus size={16} /> Ajouter un plat</button>
      </div>

      <div className="stat-grid four">
        <StatCard icon={ChefHat} label="Plats affichés" value={formatNumber(rows.length)} />
        <StatCard icon={Coins} label={`CA généré · ${periodText}`} value={formatMoney(totals.revenue, currency)} />
        <StatCard icon={Percent} label="Marge moyenne pondérée" value={formatPercent(totals.revenue ? (totals.profit / totals.revenue) * 100 : 0)} />
        <StatCard icon={Trophy} label="Plat le plus vendu" value={top ? top.name : '—'}>
          {top && <small className="stat-foot">{formatNumber(top.units)} ventes · {periodText}</small>}
        </StatCard>
      </div>

      <div className="grid-2-1">
        <Panel title="La carte" bodyClassName="no-pad-x">
          {sorted.length === 0 ? (
            <EmptyState icon={ChefHat} title="Aucun plat ne correspond" text="Modifiez la recherche ou la catégorie, ou ajoutez un nouveau plat." action={<button type="button" className="btn btn-gold" onClick={() => setEditing({ open: true, dish: null })}><Plus size={15} /> Ajouter un plat</button>} />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <SortableTh label="Plat" sortKey="name" sort={sort} onSort={toggleSort} />
                    <SortableTh label="Catégorie" sortKey="category" sort={sort} onSort={toggleSort} />
                    <SortableTh label="Prix" sortKey="price" sort={sort} onSort={toggleSort} align="right" />
                    <SortableTh label="Coût" sortKey="cost" sort={sort} onSort={toggleSort} align="right" />
                    <SortableTh label="Marge" sortKey="margin" sort={sort} onSort={toggleSort} align="right" />
                    <SortableTh label="Marge %" sortKey="marginPct" sort={sort} onSort={toggleSort} align="right" />
                    <SortableTh label="Ventes" sortKey="units" sort={sort} onSort={toggleSort} align="right" />
                    <SortableTh label="CA" sortKey="revenue" sort={sort} onSort={toggleSort} align="right" />
                    <th className="num"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((d) => (
                    <tr key={d.id}>
                      <td className="strong">{d.name}</td>
                      <td className="muted">{d.category}</td>
                      <td className="num">{formatMoney(d.price, currency, 2)}</td>
                      <td className="num">{formatMoney(d.cost, currency, 2)}</td>
                      <td className="num">{formatMoney(d.margin, currency, 2)}</td>
                      <td className="num"><Badge tone={marginTone(d.marginPct)}>{formatPercent(d.marginPct)}</Badge></td>
                      <td className="num">{formatNumber(d.units)}</td>
                      <td className="num strong">{formatMoney(d.revenue, currency)}</td>
                      <td className="num actions">
                        <button type="button" className="icon-btn" onClick={() => setEditing({ open: true, dish: d })} aria-label={`Modifier ${d.name}`}><Pencil size={15} /></button>
                        <button type="button" className="icon-btn danger" onClick={() => setToDelete(d)} aria-label={`Supprimer ${d.name}`}><Trash2 size={15} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
        <Panel title="Top CA par plat">
          <HorizontalBarChart data={chartData} height={Math.max(180, chartData.length * 38)} valueFormatter={(v) => formatMoney(v, currency)} name="CA" />
        </Panel>
      </div>

      <DishModal open={editing.open} dish={editing.dish} onClose={() => setEditing({ open: false, dish: null })} />
      <ConfirmDialog
        open={!!toDelete}
        title="Supprimer ce plat ?"
        message={toDelete ? `« ${toDelete.name} » sera retiré de la carte et des statistiques de ventes.` : ''}
        onClose={() => setToDelete(null)}
        onConfirm={() => { actions.dishes.remove(toDelete.id); toast(`${toDelete.name} supprimé`); }}
      />
    </div>
  );
}
