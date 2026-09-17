import { useEffect, useMemo, useState } from 'react';
import { Plus, Minus, Pencil, Trash2, Search, Package, ShoppingCart, CheckCircle2, AlertTriangle, XCircle, Receipt } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { Panel, SelectBox, StatCard, SortableTh, Field, Badge, EmptyState, Tabs } from '../components/UI';
import { Modal, ConfirmDialog } from '../components/Modal';
import { SimpleBarChart, DonutChart } from '../components/Charts';
import { SUPPLIERS } from '../data/mockData';
import { STOCK_STATUS, stockStatus, purchaseTotals, purchasesInRange, sumPurchases, periodRange, eachDay } from '../data/analytics';
import { formatMoney, formatQuantity, formatDateShort, formatDayMonth, normalizeText, round2, addDaysISO, formatNumber } from '../utils/format';
import { useSortedRows } from '../utils/hooks';

const STOCK_UNITS = ['kg', 'L', 'pièces', 'douz.', 'btl', 'lot'];
const STOCK_CATEGORIES = ['Poissonnerie', 'Crèmerie', 'Fruits & légumes', 'Épicerie', 'Boulangerie', 'Boissons', 'Autre'];
const SUPPLIER_COLORS = ['#cfb285', '#566e83', '#a8badb', '#7f9cc0', '#d98f5a', '#6fb58a', '#8a95a1'];

function ProductModal({ open, item, onClose }) {
  const { db, actions } = useData();
  const toast = useToast();
  const empty = { name: '', quantity: '', unit: 'kg', minimum: db.settings.defaultMinimum, supplier: SUPPLIERS[0], price: '', category: 'Poissonnerie' };
  const [form, setForm] = useState(empty);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) return;
    setError('');
    setForm(item ? { ...item } : empty);
  }, [open, item]); // eslint-disable-line react-hooks/exhaustive-deps

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const preview = STOCK_STATUS[stockStatus({ quantity: Number(form.quantity) || 0, minimum: Number(form.minimum) || 0 }, db.settings.stockAlertMargin)];

  const submit = () => {
    if (!form.name.trim()) return setError('Indiquez le nom du produit.');
    if (form.quantity === '' || Number(form.quantity) < 0) return setError('La quantité doit être un nombre positif.');
    const payload = { ...form, name: form.name.trim(), quantity: round2(form.quantity), minimum: round2(form.minimum), price: round2(form.price) };
    delete payload.id;
    if (item) {
      actions.stock.update(item.id, payload);
      toast(`${payload.name} mis à jour`);
    } else {
      actions.stock.add(payload);
      toast(`${payload.name} ajouté au stock`);
    }
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={item ? 'Modifier le produit' : 'Ajouter un produit'}
      footer={<><button type="button" className="btn btn-outline" onClick={onClose}>Annuler</button><button type="button" className="btn btn-gold" onClick={submit}>Enregistrer</button></>}
    >
      <div className="form-grid">
        <Field label="Nom du produit" span={2}><input className="input" value={form.name} onChange={set('name')} placeholder="ex. Bar de ligne" /></Field>
        <Field label="Quantité actuelle"><input className="input" type="number" min="0" step="0.1" value={form.quantity} onChange={set('quantity')} /></Field>
        <Field label="Unité"><select className="input" value={form.unit} onChange={set('unit')}>{STOCK_UNITS.map((u) => <option key={u}>{u}</option>)}</select></Field>
        <Field label="Seuil minimum"><input className="input" type="number" min="0" step="0.1" value={form.minimum} onChange={set('minimum')} /></Field>
        <Field label={`Prix d'achat HT / unité (${db.settings.currency})`}><input className="input" type="number" min="0" step="0.01" value={form.price} onChange={set('price')} /></Field>
        <Field label="Fournisseur"><select className="input" value={form.supplier} onChange={set('supplier')}>{SUPPLIERS.map((s) => <option key={s}>{s}</option>)}</select></Field>
        <Field label="Catégorie"><select className="input" value={form.category} onChange={set('category')}>{STOCK_CATEGORIES.map((c) => <option key={c}>{c}</option>)}</select></Field>
      </div>
      <p className="form-preview">Statut après enregistrement : <Badge tone={preview.tone}>{preview.label}</Badge></p>
      {error && <p className="form-error">{error}</p>}
    </Modal>
  );
}

function StockTab({ initialQuery, initialStatus }) {
  const { db, actions } = useData();
  const toast = useToast();
  const currency = db.settings.currency;
  const [query, setQuery] = useState(initialQuery || '');
  const [status, setStatus] = useState(initialStatus || 'all');
  const [supplier, setSupplier] = useState('all');
  const [editing, setEditing] = useState({ open: false, item: null });
  const [toDelete, setToDelete] = useState(null);

  const withStatus = useMemo(() => db.stock.map((i) => ({ ...i, status: stockStatus(i, db.settings.stockAlertMargin), value: round2(i.quantity * i.price) })), [db.stock, db.settings.stockAlertMargin]);
  const counts = withStatus.reduce((acc, i) => ({ ...acc, [i.status]: acc[i.status] + 1 }), { ok: 0, low: 0, rupture: 0 });
  const filtered = withStatus.filter((i) => (status === 'all' || i.status === status) && (supplier === 'all' || i.supplier === supplier) && (!query || normalizeText(i.name).includes(normalizeText(query))));
  const { sorted, sort, toggleSort } = useSortedRows(filtered, 'name', 'asc');
  const stockValue = withStatus.reduce((s, i) => s + i.value, 0);

  const adjust = (item, delta) => {
    const quantity = Math.max(0, round2(Number(item.quantity) + delta));
    actions.stock.update(item.id, { quantity });
    const next = stockStatus({ ...item, quantity }, db.settings.stockAlertMargin);
    if (next !== item.status) toast(`${item.name} : ${STOCK_STATUS[next].label.toLowerCase()}`, next === 'ok' ? 'success' : 'info');
  };
  const step = (unit) => (unit === 'kg' || unit === 'L' ? 0.1 : 1);

  return (
    <>
      <div className="stat-grid four">
        <StatCard icon={CheckCircle2} label="Produits OK" value={counts.ok} accent={status === 'ok'} onClick={() => setStatus(status === 'ok' ? 'all' : 'ok')} />
        <StatCard icon={AlertTriangle} label="Bientôt vides" value={counts.low} accent={status === 'low'} onClick={() => setStatus(status === 'low' ? 'all' : 'low')} />
        <StatCard icon={XCircle} label="En rupture" value={counts.rupture} accent={status === 'rupture'} onClick={() => setStatus(status === 'rupture' ? 'all' : 'rupture')} />
        <StatCard icon={Package} label="Valeur du stock (HT)" value={formatMoney(stockValue, currency)} />
      </div>

      <div className="toolbar">
        <div className="input-icon">
          <Search size={16} />
          <input className="input" placeholder="Rechercher un produit" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Rechercher un produit" />
        </div>
        <SelectBox label="Statut" value={status} onChange={setStatus} options={[{ value: 'all', label: 'Tous les statuts' }, { value: 'ok', label: '🟢 OK' }, { value: 'low', label: '🟠 Bientôt vide' }, { value: 'rupture', label: '🔴 Rupture' }]} />
        <SelectBox label="Fournisseur" value={supplier} onChange={setSupplier} options={[{ value: 'all', label: 'Tous fournisseurs' }, ...SUPPLIERS.map((s) => ({ value: s, label: s }))]} />
        <button type="button" className="btn btn-gold push-right" onClick={() => setEditing({ open: true, item: null })}><Plus size={16} /> Ajouter un produit</button>
      </div>

      <Panel bodyClassName="no-pad-x">
        {sorted.length === 0 ? (
          <EmptyState icon={Package} title="Aucun produit ne correspond" text="Changez les filtres ou ajoutez un produit." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <SortableTh label="Produit" sortKey="name" sort={sort} onSort={toggleSort} />
                  <SortableTh label="Quantité" sortKey="quantity" sort={sort} onSort={toggleSort} align="right" />
                  <th>Unité</th>
                  <SortableTh label="Seuil min." sortKey="minimum" sort={sort} onSort={toggleSort} align="right" />
                  <SortableTh label="Fournisseur" sortKey="supplier" sort={sort} onSort={toggleSort} />
                  <SortableTh label="Prix d'achat HT" sortKey="price" sort={sort} onSort={toggleSort} align="right" />
                  <SortableTh label="Statut" sortKey="status" sort={sort} onSort={toggleSort} />
                  <th className="num"><span className="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((i) => (
                  <tr key={i.id} className={i.status !== 'ok' ? `row-${i.status}` : ''}>
                    <td className="strong">{i.name}<small className="cell-sub">{i.category}</small></td>
                    <td className="num">
                      <span className="qty-stepper">
                        <button type="button" onClick={() => adjust(i, -step(i.unit))} aria-label={`Retirer ${step(i.unit)} ${i.unit} de ${i.name}`} disabled={i.quantity <= 0}><Minus size={13} /></button>
                        <span>{formatQuantity(i.quantity)}</span>
                        <button type="button" onClick={() => adjust(i, step(i.unit))} aria-label={`Ajouter ${step(i.unit)} ${i.unit} à ${i.name}`}><Plus size={13} /></button>
                      </span>
                    </td>
                    <td>{i.unit}</td>
                    <td className="num">{formatQuantity(i.minimum)}</td>
                    <td>{i.supplier}</td>
                    <td className="num">{formatMoney(i.price, currency, 2)}</td>
                    <td><Badge tone={STOCK_STATUS[i.status].tone}>{STOCK_STATUS[i.status].label}</Badge></td>
                    <td className="num actions">
                      <button type="button" className="icon-btn" onClick={() => setEditing({ open: true, item: i })} aria-label={`Modifier ${i.name}`}><Pencil size={15} /></button>
                      <button type="button" className="icon-btn danger" onClick={() => setToDelete(i)} aria-label={`Supprimer ${i.name}`}><Trash2 size={15} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <ProductModal open={editing.open} item={editing.item} onClose={() => setEditing({ open: false, item: null })} />
      <ConfirmDialog
        open={!!toDelete}
        title="Supprimer ce produit ?"
        message={toDelete ? `« ${toDelete.name} » sera retiré de l'inventaire.` : ''}
        onClose={() => setToDelete(null)}
        onConfirm={() => { actions.stock.remove(toDelete.id); toast(`${toDelete.name} supprimé`); }}
      />
    </>
  );
}

function PurchasesTab({ initialSupplier }) {
  const { db, actions, selectedDate } = useData();
  const toast = useToast();
  const currency = db.settings.currency;
  const emptyPurchase = { date: selectedDate, supplier: SUPPLIERS[0], product: '', quantity: 1, unitPrice: '', vat: db.settings.vatPurchases };
  const [form, setForm] = useState(emptyPurchase);
  const [addToStock, setAddToStock] = useState(true);
  const [error, setError] = useState('');
  const [supplierFilter, setSupplierFilter] = useState(initialSupplier || 'all');
  const [historyPeriod, setHistoryPeriod] = useState('month');
  const [toDelete, setToDelete] = useState(null);

  const totals = purchaseTotals(form);
  const matchingItem = db.stock.find((s) => s.name.toLowerCase() === form.product.trim().toLowerCase());
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const dayTotal = sumPurchases(purchasesInRange(db.purchases, periodRange('today', selectedDate)));
  const weekTotal = sumPurchases(purchasesInRange(db.purchases, periodRange('week', selectedDate)));
  const monthTotal = sumPurchases(purchasesInRange(db.purchases, periodRange('month', selectedDate)));

  const dailyChart = useMemo(() => {
    const from = addDaysISO(selectedDate, -29);
    return eachDay(from, selectedDate).map((iso) => ({
      key: iso,
      tick: formatDayMonth(iso),
      label: formatDayMonth(iso),
      value: Math.round(sumPurchases(db.purchases.filter((p) => p.date === iso)).ttc),
    }));
  }, [db.purchases, selectedDate]);

  const monthPurchases = purchasesInRange(db.purchases, periodRange('month', selectedDate));
  const bySupplier = SUPPLIERS.map((s, i) => ({ key: s, name: s, value: round2(sumPurchases(monthPurchases.filter((p) => p.supplier === s)).ttc), color: SUPPLIER_COLORS[i] }))
    .filter((s) => s.value > 0)
    .map((s) => ({ ...s, display: formatMoney(s.value, currency) }));

  const history = db.purchases
    .filter((p) => (supplierFilter === 'all' || p.supplier === supplierFilter) && (historyPeriod === 'all' || (p.date >= periodRange(historyPeriod, selectedDate).from && p.date <= selectedDate)))
    .sort((a, b) => b.date.localeCompare(a.date));

  const submit = () => {
    if (!form.date) return setError('Choisissez la date de l’achat.');
    if (!form.product.trim()) return setError('Indiquez le produit acheté.');
    if (!(Number(form.quantity) > 0)) return setError('La quantité doit être supérieure à 0.');
    if (!(Number(form.unitPrice) >= 0) || form.unitPrice === '') return setError('Indiquez le prix unitaire HT.');
    const payload = { ...form, product: form.product.trim(), quantity: Number(form.quantity), unitPrice: round2(form.unitPrice), vat: Number(form.vat), unit: matchingItem?.unit || 'lot' };
    actions.purchases.add(payload, addToStock && !!matchingItem);
    toast(`Achat enregistré : ${formatMoney(totals.ttc, currency, 2)} TTC${addToStock && matchingItem ? ` · stock ${matchingItem.name} mis à jour` : ''}`);
    setForm({ ...emptyPurchase, supplier: form.supplier, date: form.date });
    setError('');
  };

  return (
    <>
      <div className="stat-grid three">
        <StatCard icon={Receipt} label="Achats du jour (TTC)" value={formatMoney(dayTotal.ttc, currency)}><small className="stat-foot">{dayTotal.count} achat{dayTotal.count > 1 ? 's' : ''}</small></StatCard>
        <StatCard icon={Receipt} label="Achats 7 derniers jours (TTC)" value={formatMoney(weekTotal.ttc, currency)}><small className="stat-foot">{weekTotal.count} achats · HT {formatMoney(weekTotal.ht, currency)}</small></StatCard>
        <StatCard icon={Receipt} label="Achats du mois (TTC)" value={formatMoney(monthTotal.ttc, currency)}><small className="stat-foot">{monthTotal.count} achats · TVA {formatMoney(monthTotal.vat, currency)}</small></StatCard>
      </div>

      <div className="grid-1-2">
        <Panel title="Enregistrer un achat" icon={ShoppingCart}>
          <div className="form-grid">
            <Field label="Date"><input className="input" type="date" value={form.date} onChange={set('date')} /></Field>
            <Field label="Fournisseur"><select className="input" value={form.supplier} onChange={set('supplier')}>{SUPPLIERS.map((s) => <option key={s}>{s}</option>)}</select></Field>
            <Field label="Produit" span={2}>
              <input className="input" list="stock-products" value={form.product} onChange={set('product')} placeholder="ex. Moules, Crème liquide…" />
              <datalist id="stock-products">{db.stock.map((s) => <option key={s.id} value={s.name} />)}</datalist>
            </Field>
            <Field label={`Quantité${matchingItem ? ` (${matchingItem.unit})` : ''}`}><input className="input" type="number" min="0" step="0.1" value={form.quantity} onChange={set('quantity')} /></Field>
            <Field label={`Prix unitaire HT (${currency})`}><input className="input" type="number" min="0" step="0.01" value={form.unitPrice} onChange={set('unitPrice')} /></Field>
            <Field label="TVA">
              <select className="input" value={form.vat} onChange={set('vat')}>
                {[0, 2.1, 5.5, 10, 20].map((v) => <option key={v} value={v}>{formatNumber(v, v % 1 ? 1 : 0)} %</option>)}
              </select>
            </Field>
            <Field label="Ajout au stock" group>
              <label className={`check ${matchingItem ? '' : 'disabled'}`}>
                <input type="checkbox" checked={addToStock && !!matchingItem} disabled={!matchingItem} onChange={(e) => setAddToStock(e.target.checked)} />
                {matchingItem ? `Ajouter à « ${matchingItem.name} »` : 'Produit hors inventaire'}
              </label>
            </Field>
          </div>
          <div className="calc-box">
            <div><span>Total HT</span><strong>{formatMoney(totals.ht, currency, 2)}</strong></div>
            <div><span>TVA</span><strong>{formatMoney(totals.vatAmount, currency, 2)}</strong></div>
            <div className="calc-main"><span>Montant TTC</span><strong>{formatMoney(totals.ttc, currency, 2)}</strong></div>
          </div>
          {error && <p className="form-error">{error}</p>}
          <button type="button" className="btn btn-gold btn-block" onClick={submit}><Plus size={16} /> Enregistrer l'achat</button>
        </Panel>

        <div className="stack">
          <Panel title="Achats par jour · 30 derniers jours">
            <SimpleBarChart data={dailyChart} height={200} valueFormatter={(v) => formatMoney(v, currency)} name="Achats TTC" />
          </Panel>
          <Panel title="Répartition par fournisseur · ce mois">
            {bySupplier.length ? (
              <div className="split">
                <DonutChart data={bySupplier} size={160} centerValue={formatMoney(monthTotal.ttc, currency)} centerLabel="TTC" onSliceClick={(d) => setSupplierFilter(d.key)} />
                <ul className="legend">
                  {bySupplier.map((s) => (
                    <li key={s.key}>
                      <button type="button" className={supplierFilter === s.key ? 'active' : ''} onClick={() => setSupplierFilter(supplierFilter === s.key ? 'all' : s.key)}>
                        <span className="dot" style={{ background: s.color }} /><span className="legend-name">{s.name}</span><span className="legend-value">{s.display}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : <EmptyState icon={Receipt} title="Aucun achat ce mois-ci" />}
          </Panel>
        </div>
      </div>

      <Panel
        title="Historique des achats"
        bodyClassName="no-pad-x"
        actions={
          <>
            <SelectBox small label="Fournisseur" value={supplierFilter} onChange={setSupplierFilter} options={[{ value: 'all', label: 'Tous fournisseurs' }, ...SUPPLIERS.map((s) => ({ value: s, label: s }))]} />
            <SelectBox small label="Période" value={historyPeriod} onChange={setHistoryPeriod} options={[{ value: 'week', label: '7 derniers jours' }, { value: 'month', label: 'Ce mois' }, { value: 'year', label: 'Cette année' }, { value: 'all', label: 'Tout' }]} />
          </>
        }
      >
        {history.length === 0 ? <EmptyState icon={Receipt} title="Aucun achat sur ces critères" /> : (
          <div className="table-wrap scroll-y tall">
            <table className="table">
              <thead><tr><th>Date</th><th>Fournisseur</th><th>Produit</th><th className="num">Qté</th><th className="num">Prix HT</th><th className="num">TVA</th><th className="num">Total HT</th><th className="num">TTC</th><th className="num"><span className="sr-only">Actions</span></th></tr></thead>
              <tbody>
                {history.map((p) => {
                  const t = purchaseTotals(p);
                  return (
                    <tr key={p.id}>
                      <td>{formatDateShort(p.date)}</td>
                      <td>{p.supplier}</td>
                      <td className="ellipsis">{p.product}</td>
                      <td className="num">{formatQuantity(p.quantity)} {p.unit}</td>
                      <td className="num">{formatMoney(p.unitPrice, currency, 2)}</td>
                      <td className="num">{formatNumber(p.vat, p.vat % 1 ? 1 : 0)} %</td>
                      <td className="num">{formatMoney(t.ht, currency, 2)}</td>
                      <td className="num strong">{formatMoney(t.ttc, currency, 2)}</td>
                      <td className="num actions"><button type="button" className="icon-btn danger" onClick={() => setToDelete(p)} aria-label="Supprimer l'achat"><Trash2 size={15} /></button></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <ConfirmDialog
        open={!!toDelete}
        title="Supprimer cet achat ?"
        message={toDelete ? `Achat ${toDelete.supplier} du ${formatDateShort(toDelete.date)} (${formatMoney(purchaseTotals(toDelete).ttc, currency, 2)} TTC). Le stock n'est pas modifié.` : ''}
        onClose={() => setToDelete(null)}
        onConfirm={() => { actions.purchases.remove(toDelete.id); toast('Achat supprimé'); }}
      />
    </>
  );
}

export default function StockPage() {
  const { db } = useData();
  const { route } = useNav();
  const [tab, setTab] = useState(route.params.tab === 'purchases' ? 'purchases' : 'stock');
  const alertsCount = db.stock.filter((i) => stockStatus(i, db.settings.stockAlertMargin) !== 'ok').length;

  return (
    <div className="page">
      <PageHero title="Achats & Stocks" subtitle="Inventaire, seuils d'alerte et suivi des achats fournisseurs." />
      <div className="toolbar">
        <Tabs label="Section" value={tab} onChange={setTab} options={[{ value: 'stock', label: 'Stocks', icon: Package, count: alertsCount || undefined }, { value: 'purchases', label: 'Achats', icon: ShoppingCart }]} />
      </div>
      {tab === 'stock'
        ? <StockTab initialQuery={route.params.query} initialStatus={route.params.status} />
        : <PurchasesTab initialSupplier={route.params.supplier} />}
    </div>
  );
}
