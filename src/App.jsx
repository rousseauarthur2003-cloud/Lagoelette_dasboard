import { useEffect, useState } from 'react';
import { DataProvider, useData } from './context/DataContext';
import { NavProvider, useNav } from './context/NavContext';
import { ToastProvider } from './components/Toast';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { SailboatMark } from './components/Logo';
import DashboardPage from './pages/Dashboard';
import RevenuePage from './pages/Revenue';
import CoversPage from './pages/Covers';
import SalesPage from './pages/Sales';
import StockPage from './pages/Stock';
import ReservationsPage from './pages/Reservations';
import TeamPage from './pages/Team';
import ReportsPage from './pages/Reports';
import SettingsPage from './pages/Settings';

const PAGE_COMPONENTS = {
  dashboard: DashboardPage,
  revenue: RevenuePage,
  covers: CoversPage,
  sales: SalesPage,
  stock: StockPage,
  reservations: ReservationsPage,
  team: TeamPage,
  reports: ReportsPage,
  settings: SettingsPage,
};

function AppShell() {
  const { db, loadError, reload } = useData();
  const { route } = useNav();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const close = () => window.innerWidth > 1100 && setMenuOpen(false);
    window.addEventListener('resize', close);
    return () => window.removeEventListener('resize', close);
  }, []);

  if (loadError) {
    return (
      <div className="app-loading">
        <SailboatMark size={34} />
        <p>Les données n’ont pas pu être chargées : {loadError}</p>
        <button type="button" className="btn btn-gold" onClick={reload}>Réessayer</button>
      </div>
    );
  }
  if (!db) {
    return (
      <div className="app-loading">
        <SailboatMark size={34} />
        <p>Chargement de La Goëlette…</p>
      </div>
    );
  }

  const Page = PAGE_COMPONENTS[route.page] || DashboardPage;

  return (
    <div className={`app ${db.settings.compactMode ? 'compact' : ''}`}>
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="main">
        <Header onMenu={() => setMenuOpen(true)} />
        <main className="content">
          <Page key={`${route.page}-${route.version}`} />
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <DataProvider>
      <NavProvider>
        <ToastProvider>
          <AppShell />
        </ToastProvider>
      </NavProvider>
    </DataProvider>
  );
}
