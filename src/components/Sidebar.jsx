import { NAV_ITEMS } from '../config/navigation';
import { useNav } from '../context/NavContext';
import { useData } from '../context/DataContext';
import { Logo, SailboatMark } from './Logo';
import terracePhoto from '../assets/terrasse.jpg';

export function Sidebar({ open, onClose }) {
  const { route, navigate } = useNav();
  const { db } = useData();
  const manager = db?.settings?.managerName || 'Arthur';

  return (
    <>
      <div className={`sidebar-backdrop ${open ? 'show' : ''}`} onClick={onClose} aria-hidden="true" />
      <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Navigation principale">
        <div className="sidebar-photo" style={{ backgroundImage: `url(${terracePhoto})` }} aria-hidden="true" />
        <button type="button" className="sidebar-brand" onClick={() => { navigate('dashboard'); onClose(); }} aria-label="Retour au tableau de bord">
          <Logo name={db?.settings?.name || 'La Goëlette'} />
        </button>
        <nav className="nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = route.page === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${active ? 'active' : ''}`}
                aria-current={active ? 'page' : undefined}
                onClick={() => { navigate(item.id); onClose(); }}
              >
                <Icon size={22} strokeWidth={2} className="nav-icon" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="sidebar-foot">
          <p className="sidebar-greet">Bonne journée,</p>
          <p className="sidebar-name">{manager} !</p>
          <hr />
          <p className="sidebar-quote">« Bien manger,<br />c’est partager un moment. »</p>
          <SailboatMark size={15} className="sidebar-mark" />
        </div>
      </aside>
    </>
  );
}
