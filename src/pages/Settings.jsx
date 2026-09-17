import { useEffect, useRef, useState } from 'react';
import { Save, RotateCcw, Store, Landmark, Target, Package, MonitorSmartphone, Database } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { Panel, Field, Toggle } from '../components/UI';
import { ConfirmDialog } from '../components/Modal';
import { formatMoney } from '../utils/format';

const DISPLAY_KEYS = ['showHeroPhoto', 'compactMode', 'chartAnimations'];
const NUMBER_SETTINGS = ['vatFood', 'vatAlcohol', 'vatPurchases', 'goalDay', 'goalMonth', 'goalYear', 'capacity', 'defaultMinimum', 'stockAlertMargin'];

export default function SettingsPage() {
  const { db, actions, adapter } = useData();
  const toast = useToast();
  const [form, setForm] = useState(db.settings);
  const [confirmReset, setConfirmReset] = useState(false);
  const [error, setError] = useState('');

  const previous = useRef(db.settings);

  // Une préférence d'affichage changée ailleurs ne doit pas effacer une saisie en cours
  useEffect(() => {
    const prev = previous.current;
    previous.current = db.settings;
    setForm((f) => {
      const hasDraft = Object.keys(f).some((k) => !DISPLAY_KEYS.includes(k) && String(f[k]) !== String(prev[k]));
      if (!hasDraft) return db.settings;
      return { ...f, ...Object.fromEntries(DISPLAY_KEYS.map((k) => [k, db.settings[k]])) };
    });
  }, [db.settings]);

  const dirty = JSON.stringify(form) !== JSON.stringify(db.settings);
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));
  const setBool = (key) => (value) => {
    setForm((f) => ({ ...f, [key]: value }));
    actions.updateSettings({ [key]: value });
    toast('Préférence d’affichage enregistrée');
  };

  const save = () => {
    if (!String(form.name).trim()) return setError('Le nom du restaurant est obligatoire.');
    const patch = { ...form, name: String(form.name).trim() };
    for (const key of NUMBER_SETTINGS) {
      const n = Number(String(patch[key]).replace(',', '.'));
      if (Number.isNaN(n) || n < 0) return setError('Les taux, objectifs et seuils doivent être des nombres positifs.');
      patch[key] = n;
    }
    setError('');
    actions.updateSettings(patch);
    toast('Paramètres enregistrés');
  };

  return (
    <div className="page">
      <PageHero title="Paramètres" subtitle="Informations du restaurant, objectifs, seuils et préférences d’affichage." />

      <div className="toolbar sticky-actions">
        <span className={`save-state ${dirty ? 'dirty' : ''}`}>{dirty ? 'Modifications non enregistrées' : 'Tout est enregistré'}</span>
        <div className="push-right toolbar-group">
          <button type="button" className="btn btn-outline" onClick={() => { setForm(db.settings); setError(''); }} disabled={!dirty}>Annuler les modifications</button>
          <button type="button" className="btn btn-gold" onClick={save} disabled={!dirty}><Save size={16} /> Enregistrer</button>
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}

      <div className="settings-grid">
        <Panel title="Restaurant" icon={Store}>
          <div className="form-grid">
            <Field label="Nom du restaurant"><input className="input" value={form.name} onChange={set('name')} /></Field>
            <Field label="Prénom du gérant"><input className="input" value={form.managerName} onChange={set('managerName')} /></Field>
            <Field label="Adresse" span={2}><input className="input" value={form.address} onChange={set('address')} /></Field>
            <Field label="Téléphone"><input className="input" type="tel" value={form.phone} onChange={set('phone')} /></Field>
            <Field label="E-mail"><input className="input" type="email" value={form.email} onChange={set('email')} /></Field>
          </div>
        </Panel>

        <Panel title="Devise et TVA" icon={Landmark}>
          <div className="form-grid">
            <Field label="Devise">
              <select className="input" value={form.currency} onChange={set('currency')}>
                <option value="€">Euro (€)</option>
                <option value="CHF">Franc suisse (CHF)</option>
                <option value="£">Livre sterling (£)</option>
                <option value="$">Dollar ($)</option>
              </select>
            </Field>
            <Field label="TVA restauration (%)"><input className="input" type="number" min="0" step="0.1" value={form.vatFood} onChange={set('vatFood')} /></Field>
            <Field label="TVA boissons alcoolisées (%)"><input className="input" type="number" min="0" step="0.1" value={form.vatAlcohol} onChange={set('vatAlcohol')} /></Field>
            <Field label="TVA achats par défaut (%)"><input className="input" type="number" min="0" step="0.1" value={form.vatPurchases} onChange={set('vatPurchases')} /></Field>
          </div>
        </Panel>

        <Panel title="Objectifs de CA et capacité" icon={Target}>
          <div className="form-grid">
            <Field label={`Objectif journalier (${form.currency})`} hint={formatMoney(Number(form.goalDay) || 0, form.currency)}><input className="input" type="number" min="0" step="50" value={form.goalDay} onChange={set('goalDay')} /></Field>
            <Field label={`Objectif mensuel (${form.currency})`} hint={formatMoney(Number(form.goalMonth) || 0, form.currency)}><input className="input" type="number" min="0" step="500" value={form.goalMonth} onChange={set('goalMonth')} /></Field>
            <Field label={`Objectif annuel (${form.currency})`} hint={formatMoney(Number(form.goalYear) || 0, form.currency)}><input className="input" type="number" min="0" step="1000" value={form.goalYear} onChange={set('goalYear')} /></Field>
            <Field label="Capacité par service (places)"><input className="input" type="number" min="1" value={form.capacity} onChange={set('capacity')} /></Field>
          </div>
        </Panel>

        <Panel title="Seuils de stock" icon={Package}>
          <div className="form-grid">
            <Field label="Seuil minimum par défaut" hint="Proposé à la création d’un produit."><input className="input" type="number" min="0" step="0.1" value={form.defaultMinimum} onChange={set('defaultMinimum')} /></Field>
            <Field label="Marge d’alerte (%)" hint="Ex. 20 % : alerte « Bientôt vide » dès 1,2 × le seuil."><input className="input" type="number" min="0" step="5" value={form.stockAlertMargin} onChange={set('stockAlertMargin')} /></Field>
          </div>
        </Panel>

        <Panel title="Préférences d’affichage" icon={MonitorSmartphone}>
          <Toggle label="Photo en tête de page" description="Le port de L’Aiguillon derrière les titres." checked={form.showHeroPhoto} onChange={setBool('showHeroPhoto')} />
          <Toggle label="Affichage compact" description="Réduit les espacements pour voir plus de lignes." checked={form.compactMode} onChange={setBool('compactMode')} />
          <Toggle label="Animations des graphiques" description="Désactivez-les sur les appareils plus lents." checked={form.chartAnimations} onChange={setBool('chartAnimations')} />
        </Panel>

        <Panel title="Source des données" icon={Database}>
          <p className="panel-note">Source actuelle : <strong>{adapter.label}</strong>. Les modifications sont conservées tant que la page reste ouverte.</p>
          <p className="panel-note">Pour brancher Google Sheets, renseignez l’adaptateur dans <code>src/data/dataSource.js</code> : l’interface ne change pas.</p>
          <button type="button" className="btn btn-outline" onClick={() => setConfirmReset(true)}><RotateCcw size={15} /> Réinitialiser les données de démo</button>
        </Panel>
      </div>

      <ConfirmDialog
        open={confirmReset}
        title="Réinitialiser les données ?"
        message="Réservations, stocks, achats, plats, équipe et paramètres reviennent aux valeurs de démonstration."
        confirmLabel="Réinitialiser"
        onClose={() => setConfirmReset(false)}
        onConfirm={async () => { await actions.resetAll(); toast('Données de démonstration rechargées'); }}
      />
    </div>
  );
}
