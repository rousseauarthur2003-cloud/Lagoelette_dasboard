import { useData } from '../context/DataContext';
import harborPhoto from '../assets/port-aiguillon.jpg';

export function PageHero({ title, subtitle, actions, compact = false }) {
  const { db } = useData();
  const showPhoto = db?.settings?.showHeroPhoto !== false;
  return (
    <div className={`hero ${compact ? 'hero-compact' : ''} ${showPhoto ? '' : 'no-photo'}`}>
      {showPhoto && <div className="hero-photo" style={{ backgroundImage: `url(${harborPhoto})` }} aria-hidden="true" />}
      <div className="hero-text">
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {actions && <div className="hero-actions">{actions}</div>}
    </div>
  );
}
