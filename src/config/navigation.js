import { Home, BarChart3, Utensils, ChefHat, Package, CalendarDays, Users, FileText, Settings } from 'lucide-react';

export const NAV_ITEMS = [
  { id: 'dashboard', label: 'Tableau de bord', icon: Home },
  { id: 'revenue', label: "Chiffre d'affaires", icon: BarChart3 },
  { id: 'covers', label: 'Couverts', icon: Utensils },
  { id: 'sales', label: 'Plats & Ventes', icon: ChefHat },
  { id: 'stock', label: 'Achats & Stocks', icon: Package },
  { id: 'reservations', label: 'Réservations', icon: CalendarDays },
  { id: 'team', label: 'Équipe', icon: Users },
  { id: 'reports', label: 'Rapports', icon: FileText },
  { id: 'settings', label: 'Paramètres', icon: Settings },
];
