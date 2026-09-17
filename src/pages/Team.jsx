import { useEffect, useState } from 'react';
import { Plus, Pencil, Trash2, CalendarRange, List, Search, Users } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { Panel, Tabs, Field, EmptyState } from '../components/UI';
import { Modal, ConfirmDialog } from '../components/Modal';
import { WEEK_DAYS, normalizeText } from '../utils/format';

const SHIFT_TYPES = {
  midi: { label: 'Midi', short: 'M', tone: 'gold' },
  soir: { label: 'Soir', short: 'S', tone: 'blue' },
  journee: { label: 'Journée', short: 'J', tone: 'lavender' },
  repos: { label: 'Repos', short: '—', tone: 'rest' },
};
const SHIFT_ORDER = ['repos', 'midi', 'soir', 'journee'];
const MEMBER_COLORS = ['#cfb285', '#7f9cc0', '#a8badb', '#d98f5a', '#6fb58a', '#b58ad1', '#e0c36a'];

function workedDays(member) {
  return WEEK_DAYS.filter((d) => member.shifts[d.key] !== 'repos');
}

function MemberModal({ open, member, onClose }) {
  const { actions, db } = useData();
  const toast = useToast();
  const blank = { firstName: '', role: '', hours: '10h – 15h / 18h – 23h', color: MEMBER_COLORS[db.team.length % MEMBER_COLORS.length], shifts: Object.fromEntries(WEEK_DAYS.map((d) => [d.key, d.key === 'lun' ? 'repos' : 'journee'])) };
  const [form, setForm] = useState(blank);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) return;
    setError('');
    setForm(member ? { ...member, shifts: { ...member.shifts } } : blank);
  }, [open, member]); // eslint-disable-line react-hooks/exhaustive-deps

  const submit = () => {
    if (!form.firstName.trim()) return setError('Indiquez le prénom.');
    if (!form.role.trim()) return setError('Indiquez le poste.');
    const payload = { firstName: form.firstName.trim(), role: form.role.trim(), hours: form.hours, color: form.color, shifts: form.shifts };
    if (member) { actions.team.update(member.id, payload); toast(`${payload.firstName} mis à jour`); }
    else { actions.team.add(payload); toast(`${payload.firstName} ajouté à l'équipe`); }
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={member ? 'Modifier le membre' : "Ajouter un membre de l'équipe"}
      width={620}
      footer={<><button type="button" className="btn btn-outline" onClick={onClose}>Annuler</button><button type="button" className="btn btn-gold" onClick={submit}>Enregistrer</button></>}
    >
      <div className="form-grid">
        <Field label="Prénom"><input className="input" value={form.firstName} onChange={(e) => setForm({ ...form, firstName: e.target.value })} /></Field>
        <Field label="Poste"><input className="input" list="team-roles" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} placeholder="ex. Serveur" />
          <datalist id="team-roles">{['Gérant', 'Chef de cuisine', 'Second de cuisine', 'Commis', 'Chef de rang', 'Serveur', 'Barman', 'Plongeur'].map((r) => <option key={r} value={r} />)}</datalist>
        </Field>
        <Field label="Horaires" span={2}><input className="input" value={form.hours} onChange={(e) => setForm({ ...form, hours: e.target.value })} placeholder="ex. 11h – 15h / 18h30 – 23h" /></Field>
        <Field label="Semaine type" span={2} group>
          <div className="shift-editor">
            {WEEK_DAYS.map((d) => (
              <label key={d.key} className="shift-editor-day">
                <span>{d.label}</span>
                <select className="input" value={form.shifts[d.key]} onChange={(e) => setForm({ ...form, shifts: { ...form.shifts, [d.key]: e.target.value } })}>
                  {SHIFT_ORDER.map((s) => <option key={s} value={s}>{SHIFT_TYPES[s].label}</option>)}
                </select>
              </label>
            ))}
          </div>
        </Field>
      </div>
      {error && <p className="form-error">{error}</p>}
    </Modal>
  );
}

export default function TeamPage() {
  const { db, actions } = useData();
  const { route } = useNav();
  const toast = useToast();
  const [tab, setTab] = useState(route.params.tab === 'list' ? 'list' : 'planning');
  const [query, setQuery] = useState(route.params.query || '');
  const [modal, setModal] = useState({ open: false, member: null });
  const [toDelete, setToDelete] = useState(null);

  const members = db.team.filter((m) => !query || normalizeText(`${m.firstName} ${m.role}`).includes(normalizeText(query)));

  const cycleShift = (member, dayKey) => {
    const current = member.shifts[dayKey];
    const next = SHIFT_ORDER[(SHIFT_ORDER.indexOf(current) + 1) % SHIFT_ORDER.length];
    actions.team.update(member.id, { shifts: { ...member.shifts, [dayKey]: next } });
    toast(`${member.firstName} · ${WEEK_DAYS.find((d) => d.key === dayKey).long.toLowerCase()} : ${SHIFT_TYPES[next].label.toLowerCase()}`, 'info');
  };

  const staffing = WEEK_DAYS.map((d) => ({
    ...d,
    lunch: db.team.filter((m) => m.shifts[d.key] === 'midi' || m.shifts[d.key] === 'journee').length,
    dinner: db.team.filter((m) => m.shifts[d.key] === 'soir' || m.shifts[d.key] === 'journee').length,
  }));

  return (
    <div className="page">
      <PageHero title="Équipe" subtitle={`${db.team.length} personnes · planning de la semaine type. Cliquez sur une case pour changer le créneau.`} />

      <div className="toolbar">
        <Tabs label="Vue" value={tab} onChange={setTab} options={[{ value: 'planning', label: 'Planning', icon: CalendarRange }, { value: 'list', label: 'Membres', icon: List }]} />
        <div className="input-icon">
          <Search size={16} />
          <input className="input" placeholder="Prénom ou poste" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Rechercher un membre" />
        </div>
        <button type="button" className="btn btn-gold push-right" onClick={() => setModal({ open: true, member: null })}><Plus size={16} /> Ajouter un membre</button>
      </div>

      {members.length === 0 ? (
        <Panel><EmptyState icon={Users} title="Personne ne correspond à cette recherche" /></Panel>
      ) : tab === 'planning' ? (
        <Panel
          title="Planning hebdomadaire"
          bodyClassName="no-pad-x"
          actions={<div className="shift-legend">{SHIFT_ORDER.map((s) => <span key={s} className={`shift-chip tone-${SHIFT_TYPES[s].tone}`}>{SHIFT_TYPES[s].label}</span>)}</div>}
        >
          <div className="table-wrap">
            <table className="table planning">
              <thead>
                <tr>
                  <th>Membre</th>
                  {WEEK_DAYS.map((d) => <th key={d.key} className="center">{d.label}</th>)}
                  <th className="num">Jours</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <button type="button" className="member-cell" onClick={() => setModal({ open: true, member: m })} title="Modifier">
                        <span className="avatar sm" style={{ background: m.color }}>{m.firstName.slice(0, 1)}</span>
                        <span><strong>{m.firstName}</strong><small>{m.role}</small></span>
                      </button>
                    </td>
                    {WEEK_DAYS.map((d) => {
                      const shift = SHIFT_TYPES[m.shifts[d.key]];
                      return (
                        <td key={d.key} className="center">
                          <button type="button" className={`shift-chip tone-${shift.tone}`} onClick={() => cycleShift(m, d.key)} aria-label={`${m.firstName}, ${d.long} : ${shift.label}. Changer`}>
                            {shift.label}
                          </button>
                        </td>
                      );
                    })}
                    <td className="num strong">{workedDays(m).length}/7</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td className="muted">Effectif midi / soir</td>
                  {staffing.map((d) => <td key={d.key} className={`center staffing ${d.lunch < 3 || d.dinner < 3 ? 'low' : ''}`}>{d.lunch} / {d.dinner}</td>)}
                  <td />
                </tr>
              </tfoot>
            </table>
          </div>
        </Panel>
      ) : (
        <div className="member-grid">
          {members.map((m) => {
            const worked = workedDays(m);
            const rest = WEEK_DAYS.filter((d) => m.shifts[d.key] === 'repos');
            return (
              <article key={m.id} className="panel member-card">
                <header>
                  <span className="avatar" style={{ background: m.color }}>{m.firstName.slice(0, 2).toUpperCase()}</span>
                  <div><h3>{m.firstName}</h3><p>{m.role}</p></div>
                  <div className="member-actions">
                    <button type="button" className="icon-btn" onClick={() => setModal({ open: true, member: m })} aria-label={`Modifier ${m.firstName}`}><Pencil size={15} /></button>
                    <button type="button" className="icon-btn danger" onClick={() => setToDelete(m)} aria-label={`Supprimer ${m.firstName}`}><Trash2 size={15} /></button>
                  </div>
                </header>
                <dl>
                  <div><dt>Horaires</dt><dd>{m.hours}</dd></div>
                  <div><dt>Jours travaillés</dt><dd>{worked.map((d) => d.label).join(', ') || '—'}</dd></div>
                  <div><dt>Jours de repos</dt><dd>{rest.map((d) => d.label).join(', ') || '—'}</dd></div>
                </dl>
                <div className="member-week">
                  {WEEK_DAYS.map((d) => <span key={d.key} className={`shift-dot tone-${SHIFT_TYPES[m.shifts[d.key]].tone}`} title={`${d.long} : ${SHIFT_TYPES[m.shifts[d.key]].label}`}>{d.label.slice(0, 1)}</span>)}
                </div>
              </article>
            );
          })}
        </div>
      )}

      <MemberModal open={modal.open} member={modal.member} onClose={() => setModal({ open: false, member: null })} />
      <ConfirmDialog
        open={!!toDelete}
        title="Retirer ce membre ?"
        message={toDelete ? `${toDelete.firstName} (${toDelete.role}) sera retiré de l'équipe et du planning.` : ''}
        confirmLabel="Retirer"
        onClose={() => setToDelete(null)}
        onConfirm={() => { actions.team.remove(toDelete.id); toast(`${toDelete.firstName} retiré de l'équipe`); }}
      />
    </div>
  );
}
