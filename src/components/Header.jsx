import { useMemo, useRef, useState } from 'react';
import { Search, CalendarDays, ChevronDown, ChevronLeft, ChevronRight, Bell, Menu, X, Settings, Users, FileText, CheckCheck } from 'lucide-react';
import { useData, useAlerts } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { NAV_ITEMS } from '../config/navigation';
import { useDismiss } from '../utils/hooks';
import { TODAY_ISO, formatLongDate, formatDayMonth, normalizeText, toISODate, MONTH_NAMES, capitalize } from '../utils/format';

function CalendarPopover({ value, onSelect, min = '2025-01-01', max = TODAY_ISO }) {
  const [view, setView] = useState(() => ({ year: Number(value.slice(0, 4)), month: Number(value.slice(5, 7)) - 1 }));
  const first = new Date(view.year, view.month, 1);
  const offset = (first.getDay() + 6) % 7;
  const count = new Date(view.year, view.month + 1, 0).getDate();
  const cells = [...Array(offset).fill(null), ...Array.from({ length: count }, (_, i) => toISODate(new Date(view.year, view.month, i + 1)))];
  const shift = (n) => setView((v) => {
    const d = new Date(v.year, v.month + n, 1);
    return { year: d.getFullYear(), month: d.getMonth() };
  });
  const canPrev = toISODate(new Date(view.year, view.month, 0)) >= min;
  const canNext = toISODate(new Date(view.year, view.month + 1, 1)) <= max;

  return (
    <div className="dropdown calendar" role="dialog" aria-label="Choisir une date">
      <div className="calendar-head">
        <button type="button" className="icon-btn" onClick={() => shift(-1)} disabled={!canPrev} aria-label="Mois précédent"><ChevronLeft size={16} /></button>
        <strong>{capitalize(MONTH_NAMES[view.month])} {view.year}</strong>
        <button type="button" className="icon-btn" onClick={() => shift(1)} disabled={!canNext} aria-label="Mois suivant"><ChevronRight size={16} /></button>
      </div>
      <div className="calendar-grid">
        {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((d, i) => <span key={i} className="calendar-dow">{d}</span>)}
        {cells.map((iso, i) =>
          iso ? (
            <button
              key={iso}
              type="button"
              className={`calendar-day ${iso === value ? 'selected' : ''} ${iso === TODAY_ISO ? 'today' : ''}`}
              disabled={iso > max || iso < min}
              onClick={() => onSelect(iso)}
            >
              {Number(iso.slice(8))}
            </button>
          ) : <span key={`e${i}`} />
        )}
      </div>
      <div className="calendar-foot">
        <button type="button" className="btn btn-outline btn-sm" onClick={() => onSelect(TODAY_ISO)}>Aujourd'hui</button>
      </div>
    </div>
  );
}

export function Header({ onMenu }) {
  const { db, selectedDate, setSelectedDate, actions } = useData();
  const { navigate } = useNav();
  const alerts = useAlerts();

  const [query, setQuery] = useState('');
  const [searchOpen, setSearchOpen] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [bellOpen, setBellOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [readIds, setReadIds] = useState(() => new Set());
  const [activeIndex, setActiveIndex] = useState(0);

  const searchRef = useRef(null);
  const calendarRef = useRef(null);
  const bellRef = useRef(null);
  const profileRef = useRef(null);
  useDismiss(searchRef, searchOpen, () => setSearchOpen(false));
  useDismiss(calendarRef, calendarOpen, () => setCalendarOpen(false));
  useDismiss(bellRef, bellOpen, () => setBellOpen(false));
  useDismiss(profileRef, profileOpen, () => setProfileOpen(false));

  const results = useMemo(() => {
    const q = normalizeText(query.trim());
    if (!q || !db) return [];
    const match = (text) => normalizeText(text).includes(q);
    const list = [];
    NAV_ITEMS.filter((p) => match(p.label)).forEach((p) => list.push({ key: `p-${p.id}`, type: 'Page', label: p.label, page: p.id, params: {} }));
    db.dishes.filter((d) => match(d.name) || match(d.category)).forEach((d) => list.push({ key: d.id, type: 'Plat', label: d.name, detail: d.category, page: 'sales', params: { query: d.name } }));
    db.stock.filter((s) => match(s.name) || match(s.supplier)).forEach((s) => list.push({ key: s.id, type: 'Stock', label: s.name, detail: s.supplier, page: 'stock', params: { query: s.name } }));
    db.reservations.filter((r) => match(r.name) || match(r.phone)).forEach((r) => list.push({ key: r.id, type: 'Réservation', label: r.name, detail: `${formatDayMonth(r.date)} · ${r.time}`, page: 'reservations', params: { query: r.name, date: '' } }));
    db.team.filter((m) => match(m.firstName) || match(m.role)).forEach((m) => list.push({ key: m.id, type: 'Équipe', label: m.firstName, detail: m.role, page: 'team', params: { query: m.firstName, tab: 'list' } }));
    return list.slice(0, 9);
  }, [query, db]);

  const openResult = (r) => {
    navigate(r.page, r.params);
    setQuery('');
    setSearchOpen(false);
  };

  const onSearchKey = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActiveIndex((i) => Math.min(results.length - 1, i + 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActiveIndex((i) => Math.max(0, i - 1)); }
    if (e.key === 'Enter' && results[activeIndex]) openResult(results[activeIndex]);
  };

  const unread = alerts.filter((a) => !readIds.has(a.id)).length;
  const manager = db?.settings?.managerName || 'Arthur';
  const initials = manager.slice(0, 2).toUpperCase();

  return (
    <header className="topbar">
      <button type="button" className="icon-btn hamburger" onClick={onMenu} aria-label="Ouvrir le menu"><Menu size={22} /></button>

      <div className="search" ref={searchRef}>
        <Search size={18} className="search-icon" aria-hidden="true" />
        <input
          type="text"
          placeholder="Rechercher..."
          value={query}
          onChange={(e) => { setQuery(e.target.value); setSearchOpen(true); setActiveIndex(0); }}
          onFocus={() => setSearchOpen(true)}
          onKeyDown={onSearchKey}
          aria-label="Rechercher un plat, un produit, une réservation…"
        />
        {query && <button type="button" className="search-clear" onClick={() => setQuery('')} aria-label="Effacer"><X size={15} /></button>}
        {searchOpen && query.trim() && (
          <div className="dropdown search-results">
            {results.length === 0 ? (
              <p className="dropdown-empty">Aucun résultat pour « {query} ». Essayez un plat, un produit ou un nom de client.</p>
            ) : (
              results.map((r, i) => (
                <button key={r.key} type="button" className={`result ${i === activeIndex ? 'active' : ''}`} onMouseEnter={() => setActiveIndex(i)} onClick={() => openResult(r)}>
                  <span className="result-type">{r.type}</span>
                  <span className="result-label">{r.label}</span>
                  {r.detail && <span className="result-detail">{r.detail}</span>}
                </button>
              ))
            )}
          </div>
        )}
      </div>

      <div className="date-select" ref={calendarRef}>
        <button type="button" className="date-button" onClick={() => setCalendarOpen((o) => !o)} aria-expanded={calendarOpen}>
          <CalendarDays size={17} />
          <span className="date-long">{formatLongDate(selectedDate)}</span>
          <span className="date-short">{formatDayMonth(selectedDate)}</span>
          <ChevronDown size={16} />
        </button>
        {calendarOpen && (
          <CalendarPopover value={selectedDate} onSelect={(iso) => { setSelectedDate(iso); setCalendarOpen(false); }} />
        )}
      </div>

      <div className="topbar-right">
        <div className="menu-anchor" ref={bellRef}>
          <button type="button" className="icon-btn bell" onClick={() => setBellOpen((o) => !o)} aria-label={`Notifications (${unread} non lues)`} aria-expanded={bellOpen}>
            <Bell size={21} />
            {unread > 0 && <span className="bell-dot" />}
          </button>
          {bellOpen && (
            <div className="dropdown notifications">
              <div className="dropdown-head">
                <strong>Notifications</strong>
                <button type="button" className="link-btn" onClick={() => setReadIds(new Set(alerts.map((a) => a.id)))} disabled={!unread}>
                  <CheckCheck size={14} /> Tout marquer comme lu
                </button>
              </div>
              {alerts.length === 0 && <p className="dropdown-empty">Rien à signaler pour le moment.</p>}
              {alerts.map((a) => (
                <button
                  key={a.id}
                  type="button"
                  className={`notif ${readIds.has(a.id) ? 'read' : ''}`}
                  onClick={() => {
                    setReadIds((s) => new Set(s).add(a.id));
                    setBellOpen(false);
                    if (a.page) navigate(a.page, a.params);
                    else navigate('dashboard');
                  }}
                >
                  <span className={`dot dot-${a.tone}`} />
                  <span>
                    <strong>{a.title}</strong>
                    <small>{a.detail}</small>
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <span className="topbar-divider" aria-hidden="true" />

        <div className="menu-anchor" ref={profileRef}>
          <button type="button" className="profile" onClick={() => setProfileOpen((o) => !o)} aria-expanded={profileOpen}>
            <span className="avatar">{initials}</span>
            <span className="profile-text">
              <strong>{manager}</strong>
              <small>Gérant</small>
            </span>
          </button>
          {profileOpen && (
            <div className="dropdown profile-menu">
              <div className="profile-card">
                <span className="avatar">{initials}</span>
                <span><strong>{manager}</strong><small>{db?.settings?.name} · Gérant</small></span>
              </div>
              <button type="button" className="menu-item" onClick={() => { navigate('settings'); setProfileOpen(false); }}><Settings size={16} /> Paramètres du restaurant</button>
              <button type="button" className="menu-item" onClick={() => { navigate('team'); setProfileOpen(false); }}><Users size={16} /> Planning de l'équipe</button>
              <button type="button" className="menu-item" onClick={() => { navigate('reports'); setProfileOpen(false); }}><FileText size={16} /> Rapports et exports</button>
              <button type="button" className="menu-item" onClick={() => { actions.updateSettings({ compactMode: !db.settings.compactMode }); setProfileOpen(false); }}>
                <span className="menu-check">{db?.settings?.compactMode ? '✓' : ''}</span> Affichage compact
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
