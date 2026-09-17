import { useMemo, useState } from 'react';
import { Plus, Pencil, Trash2, Search, Check, Pause, CalendarDays, Users, Sun, Moon, Clock, Phone } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { useToast } from '../components/Toast';
import { PageHero } from '../components/PageHero';
import { Panel, SelectBox, StatCard, Badge, EmptyState, Segmented, ProgressBar } from '../components/UI';
import { ConfirmDialog } from '../components/Modal';
import { ReservationModal, RESERVATION_STATUS } from '../components/ReservationModal';
import { SERVICE_LABELS } from '../data/analytics';
import { TODAY_ISO, addDaysISO, formatLongDate, formatDateShort, weekdayShort, normalizeText } from '../utils/format';

export default function ReservationsPage() {
  const { db, actions, selectedDate } = useData();
  const { route } = useNav();
  const toast = useToast();
  const capacity = db.settings.capacity;

  const [dateMode, setDateMode] = useState(() => (route.params.date === '' ? 'upcoming' : 'day'));
  const [date, setDate] = useState(route.params.date || selectedDate);
  const [service, setService] = useState('all');
  const [status, setStatus] = useState(route.params.status || 'all');
  const [query, setQuery] = useState(route.params.query || '');
  const [modal, setModal] = useState({ open: false, reservation: null });
  const [toDelete, setToDelete] = useState(null);

  const filtered = useMemo(() => {
    const q = normalizeText(query);
    return db.reservations
      .filter((r) => {
        if (dateMode === 'day' && r.date !== date) return false;
        if (dateMode === 'upcoming' && r.date < selectedDate) return false;
        if (service !== 'all' && r.service !== service) return false;
        if (status !== 'all' && r.status !== status) return false;
        if (q && !normalizeText(`${r.name} ${r.phone} ${r.comment}`).includes(q)) return false;
        return true;
      })
      .sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time));
  }, [db.reservations, dateMode, date, service, status, query, selectedDate]);

  const active = filtered.filter((r) => r.status !== 'cancelled');
  const people = active.reduce((s, r) => s + Number(r.people), 0);
  const lunchPeople = active.filter((r) => r.service === 'lunch').reduce((s, r) => s + Number(r.people), 0);
  const dinnerPeople = active.filter((r) => r.service === 'dinner').reduce((s, r) => s + Number(r.people), 0);
  const pendingCount = filtered.filter((r) => r.status === 'pending').length;

  const setStatusFor = (r, next) => {
    actions.reservations.update(r.id, { status: next });
    toast(`${r.name} · ${formatDateShort(r.date)} ${r.time} : ${RESERVATION_STATUS[next].label.toLowerCase()}`, next === 'confirmed' ? 'success' : 'info');
  };

  const confirmAllPending = () => {
    const list = filtered.filter((r) => r.status === 'pending');
    list.forEach((r) => actions.reservations.update(r.id, { status: 'confirmed' }));
    toast(`${list.length} réservation${list.length > 1 ? 's' : ''} confirmée${list.length > 1 ? 's' : ''}`);
  };

  const quickDate = (iso) => { setDateMode('day'); setDate(iso); };

  return (
    <div className="page">
      <PageHero title="Réservations" subtitle={dateMode === 'day' ? formatLongDate(date) : dateMode === 'upcoming' ? 'Toutes les réservations à venir' : 'Toutes les réservations'} />

      <div className="toolbar">
        <Segmented
          label="Période"
          value={dateMode === 'day' && date === selectedDate ? 'selected' : dateMode === 'day' && date === addDaysISO(selectedDate, 1) ? 'tomorrow' : dateMode}
          onChange={(v) => {
            if (v === 'selected') quickDate(selectedDate);
            else if (v === 'tomorrow') quickDate(addDaysISO(selectedDate, 1));
            else setDateMode(v);
          }}
          options={[{ value: 'selected', label: selectedDate === TODAY_ISO ? "Aujourd'hui" : 'Jour choisi' }, { value: 'tomorrow', label: 'Lendemain' }, { value: 'upcoming', label: 'À venir' }, { value: 'all', label: 'Tout' }]}
        />
        <label className="date-input">
          <span className="sr-only">Date</span>
          <input className="input" type="date" value={dateMode === 'day' ? date : ''} onChange={(e) => e.target.value && quickDate(e.target.value)} />
        </label>
        <SelectBox label="Service" value={service} onChange={setService} options={[{ value: 'all', label: 'Tous services' }, { value: 'lunch', label: 'Midi' }, { value: 'dinner', label: 'Soir' }]} />
        <SelectBox label="Statut" value={status} onChange={setStatus} options={[{ value: 'all', label: 'Tous statuts' }, { value: 'confirmed', label: 'Confirmées' }, { value: 'pending', label: 'En attente' }, { value: 'cancelled', label: 'Annulées' }]} />
        <div className="input-icon">
          <Search size={16} />
          <input className="input" placeholder="Nom, téléphone…" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Rechercher une réservation" />
        </div>
        <button type="button" className="btn btn-gold push-right" onClick={() => setModal({ open: true, reservation: null })}><Plus size={16} /> Ajouter</button>
      </div>

      <div className="stat-grid four">
        <StatCard icon={CalendarDays} label="Réservations" value={active.length}>
          {pendingCount > 0 && <button type="button" className="link-btn stat-foot" onClick={confirmAllPending}><Check size={13} /> Confirmer les {pendingCount} en attente</button>}
        </StatCard>
        <StatCard icon={Users} label="Personnes attendues" value={people} accent />
        <StatCard icon={Sun} label="Midi" value={`${lunchPeople} pers.`}>
          {dateMode === 'day' && <><ProgressBar value={lunchPeople} max={capacity} label="Remplissage midi" /><small className="stat-foot">{capacity ? Math.round((lunchPeople / capacity) * 100) : 0} % de la capacité</small></>}
        </StatCard>
        <StatCard icon={Moon} label="Soir" value={`${dinnerPeople} pers.`}>
          {dateMode === 'day' && <><ProgressBar value={dinnerPeople} max={capacity} label="Remplissage soir" /><small className="stat-foot">{capacity ? Math.round((dinnerPeople / capacity) * 100) : 0} % de la capacité</small></>}
        </StatCard>
      </div>

      <Panel bodyClassName="no-pad-x">
        {filtered.length === 0 ? (
          <EmptyState icon={CalendarDays} title="Aucune réservation sur ces critères" text="Changez la date ou les filtres, ou ajoutez une réservation." action={<button type="button" className="btn btn-gold" onClick={() => setModal({ open: true, reservation: null })}><Plus size={15} /> Ajouter une réservation</button>} />
        ) : (
          <div className="table-wrap">
            <table className="table table-reservations">
              <thead>
                <tr><th>Date</th><th>Heure</th><th>Nom</th><th>Téléphone</th><th className="num">Pers.</th><th>Service</th><th>Commentaire</th><th>Statut</th><th className="num"><span className="sr-only">Actions</span></th></tr>
              </thead>
              <tbody>
                {filtered.map((r) => (
                  <tr key={r.id} className={r.status === 'cancelled' ? 'row-cancelled' : ''}>
                    <td>{weekdayShort(r.date)} {formatDateShort(r.date)}</td>
                    <td><span className="inline-icon"><Clock size={13} />{r.time}</span></td>
                    <td className="strong">{r.name}</td>
                    <td>{r.phone ? <a className="tel" href={`tel:${r.phone.replace(/\s/g, '')}`}><Phone size={13} />{r.phone}</a> : <span className="muted">—</span>}</td>
                    <td className="num strong">{r.people}</td>
                    <td>{SERVICE_LABELS[r.service]}</td>
                    <td className="ellipsis muted comment" title={r.comment}>{r.comment || '—'}</td>
                    <td><Badge tone={RESERVATION_STATUS[r.status].tone}>{RESERVATION_STATUS[r.status].label}</Badge></td>
                    <td className="num actions">
                      {r.status !== 'confirmed' && <button type="button" className="icon-btn success" onClick={() => setStatusFor(r, 'confirmed')} aria-label={`Confirmer ${r.name}`} title="Confirmer"><Check size={15} /></button>}
                      {r.status !== 'pending' && <button type="button" className="icon-btn warn" onClick={() => setStatusFor(r, 'pending')} aria-label={`Mettre ${r.name} en attente`} title="Mettre en attente"><Pause size={15} /></button>}
                      <button type="button" className="icon-btn" onClick={() => setModal({ open: true, reservation: r })} aria-label={`Modifier ${r.name}`} title="Modifier"><Pencil size={15} /></button>
                      <button type="button" className="icon-btn danger" onClick={() => setToDelete(r)} aria-label={`Supprimer ${r.name}`} title="Supprimer"><Trash2 size={15} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <ReservationModal open={modal.open} reservation={modal.reservation} defaultDate={dateMode === 'day' ? date : selectedDate} onClose={() => setModal({ open: false, reservation: null })} />
      <ConfirmDialog
        open={!!toDelete}
        title="Supprimer la réservation ?"
        message={toDelete ? `${toDelete.name}, ${toDelete.people} pers. le ${formatDateShort(toDelete.date)} à ${toDelete.time}.` : ''}
        onClose={() => setToDelete(null)}
        onConfirm={() => { actions.reservations.remove(toDelete.id); toast(`Réservation ${toDelete.name} supprimée`); }}
      />
    </div>
  );
}
