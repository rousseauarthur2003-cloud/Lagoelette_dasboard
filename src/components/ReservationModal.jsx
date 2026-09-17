import { useEffect, useState } from 'react';
import { Modal } from './Modal';
import { Field } from './UI';
import { useData } from '../context/DataContext';
import { useToast } from './Toast';
import { formatDayMonth } from '../utils/format';

const EMPTY_RESERVATION = { name: '', phone: '', date: '', time: '19:30', people: 2, service: 'dinner', comment: '', status: 'confirmed' };

export function ReservationModal({ open, onClose, reservation, defaultDate }) {
  const { db, actions, selectedDate } = useData();
  const toast = useToast();
  const [form, setForm] = useState(EMPTY_RESERVATION);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) return;
    setError('');
    setForm(reservation ? { ...reservation } : { ...EMPTY_RESERVATION, date: defaultDate || selectedDate });
  }, [open, reservation, defaultDate, selectedDate]);

  const set = (key, value) => setForm((f) => {
    const next = { ...f, [key]: value };
    if (key === 'time' && value) next.service = value < '16:00' ? 'lunch' : 'dinner';
    return next;
  });

  const booked = db
    ? db.reservations
        .filter((r) => r.date === form.date && r.service === form.service && r.status !== 'cancelled' && r.id !== reservation?.id)
        .reduce((s, r) => s + Number(r.people), 0)
    : 0;
  const capacity = db?.settings?.capacity || 0;
  const afterBooking = booked + (Number(form.people) || 0);

  const submit = (e) => {
    e?.preventDefault?.();
    if (!form.name.trim()) return setError('Indiquez le nom de la réservation.');
    if (!form.date || !form.time) return setError('Choisissez une date et une heure.');
    if (!(Number(form.people) >= 1)) return setError('Le nombre de personnes doit être au moins 1.');
    const payload = { ...form, name: form.name.trim(), people: Number(form.people) };
    if (reservation) {
      actions.reservations.update(reservation.id, payload);
      toast(`Réservation ${payload.name} modifiée`);
    } else {
      actions.reservations.add(payload);
      toast(`Réservation ${payload.name} enregistrée pour le ${formatDayMonth(payload.date)} à ${payload.time}`);
    }
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={reservation ? 'Modifier la réservation' : 'Nouvelle réservation'}
      subtitle={form.date ? `${afterBooking} / ${capacity} couverts réservés sur ce service` : undefined}
      footer={
        <>
          <button type="button" className="btn btn-outline" onClick={onClose}>Annuler</button>
          <button type="button" className="btn btn-gold" onClick={submit}>Enregistrer</button>
        </>
      }
    >
      <div className="form-grid" onKeyDown={(e) => { if (e.key === 'Enter' && e.target.tagName === 'INPUT') submit(e); }}>
        <Field label="Nom">
          <input className="input" value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="ex. Famille Durand" />
        </Field>
        <Field label="Téléphone">
          <input className="input" type="tel" value={form.phone} onChange={(e) => set('phone', e.target.value)} placeholder="06 00 00 00 00" />
        </Field>
        <Field label="Date">
          <input className="input" type="date" value={form.date} onChange={(e) => set('date', e.target.value)} />
        </Field>
        <Field label="Heure">
          <input className="input" type="time" step="900" value={form.time} onChange={(e) => set('time', e.target.value)} />
        </Field>
        <Field label="Nombre de personnes">
          <input className="input" type="number" min="1" max="40" value={form.people} onChange={(e) => set('people', e.target.value)} />
        </Field>
        <Field label="Service">
          <select className="input" value={form.service} onChange={(e) => set('service', e.target.value)}>
            <option value="lunch">Midi</option>
            <option value="dinner">Soir</option>
          </select>
        </Field>
        <Field label="Statut" span={2} group>
          <div className="segmented">
            {[['confirmed', 'Confirmée'], ['pending', 'En attente'], ['cancelled', 'Annulée']].map(([value, label]) => (
              <button key={value} type="button" className={form.status === value ? 'active' : ''} onClick={() => set('status', value)}>{label}</button>
            ))}
          </div>
        </Field>
        <Field label="Commentaire" span={2}>
          <textarea className="input" rows={3} value={form.comment} onChange={(e) => set('comment', e.target.value)} placeholder="Allergies, occasion, table souhaitée…" />
        </Field>
      </div>
      {afterBooking > capacity && capacity > 0 && <p className="form-warning">Attention : ce service dépasse la capacité du restaurant ({capacity} couverts).</p>}
      {error && <p className="form-error">{error}</p>}
    </Modal>
  );
}

export const RESERVATION_STATUS = {
  confirmed: { label: 'Confirmée', tone: 'green' },
  pending: { label: 'En attente', tone: 'orange' },
  cancelled: { label: 'Annulée', tone: 'grey' },
};
