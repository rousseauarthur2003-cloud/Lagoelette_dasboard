import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { dataAdapter } from '../data/dataSource';
import { indexDays, stockStatus } from '../data/analytics';
import { TODAY_ISO, formatQuantity, round2, uid } from '../utils/format';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [db, setDb] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(TODAY_ISO);

  const load = useCallback(async () => {
    try {
      setLoadError(null);
      setDb(await dataAdapter.load());
    } catch (error) {
      setLoadError(error.message || 'Chargement des données impossible');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const updateCollection = useCallback((key, updater) => {
    setDb((prev) => {
      const next = updater(prev[key]);
      Promise.resolve(dataAdapter.save(key, next)).catch(() => {});
      return { ...prev, [key]: next };
    });
  }, []);

  const actions = useMemo(() => {
    const crud = (key, prefix) => ({
      add: (item) => {
        const created = { ...item, id: uid(prefix) };
        updateCollection(key, (list) => [created, ...list]);
        return created;
      },
      update: (id, patch) => updateCollection(key, (list) => list.map((x) => (x.id === id ? { ...x, ...patch } : x))),
      remove: (id) => updateCollection(key, (list) => list.filter((x) => x.id !== id)),
    });
    const purchases = crud('purchases', 'pur');
    return {
      reservations: crud('reservations', 'res'),
      stock: crud('stock', 'stk'),
      dishes: crud('dishes', 'dish'),
      team: crud('team', 'emp'),
      notes: crud('notes', 'note'),
      purchases: {
        ...purchases,
        add: (purchase, addToStock = false) => {
          const created = purchases.add(purchase);
          if (addToStock) {
            const target = purchase.product.trim().toLowerCase();
            updateCollection('stock', (list) =>
              list.map((item) => (item.name.toLowerCase() === target ? { ...item, quantity: round2(Number(item.quantity) + Number(purchase.quantity)) } : item))
            );
          }
          return created;
        },
      },
      updateSettings: (patch) =>
        setDb((prev) => {
          const settings = { ...prev.settings, ...patch };
          Promise.resolve(dataAdapter.save('settings', settings)).catch(() => {});
          return { ...prev, settings };
        }),
      resetAll: async () => {
        setDb(await dataAdapter.reset());
        setSelectedDate(TODAY_ISO);
      },
    };
  }, [updateCollection]);

  const dayIndex = useMemo(() => (db ? indexDays(db.dailyStats) : new Map()), [db]);

  const value = useMemo(
    () => ({ db, loadError, reload: load, selectedDate, setSelectedDate, dayIndex, actions, adapter: dataAdapter }),
    [db, loadError, load, selectedDate, dayIndex, actions]
  );

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData() {
  return useContext(DataContext);
}

// Alertes calculées à partir des données (stocks, réservations) + notes libres
export function useAlerts() {
  const { db, selectedDate } = useData();
  return useMemo(() => {
    if (!db) return [];
    const list = [];
    db.stock.forEach((item) => {
      const status = stockStatus(item, db.settings.stockAlertMargin);
      if (status === 'rupture') {
        list.push({ id: `stock-${item.id}-rupture`, tone: 'red', title: `Rupture : ${item.name.toLowerCase()}`, detail: `À commander chez ${item.supplier}`, page: 'stock', params: { status: 'rupture' } });
      } else if (status === 'low') {
        list.push({ id: `stock-${item.id}-low`, tone: 'red', title: `Stock ${item.name.toLowerCase()} faible`, detail: `${formatQuantity(item.quantity)} ${item.unit} restant`, page: 'stock', params: { status: 'low' } });
      }
    });
    const pending = db.reservations.filter((r) => r.status === 'pending' && r.date >= selectedDate);
    if (pending.length) {
      list.push({ id: `pending-${pending.length}`, tone: 'orange', title: `${pending.length} réservation${pending.length > 1 ? 's' : ''} en attente`, detail: 'à confirmer', page: 'reservations', params: { status: 'pending', date: '' } });
    }
    db.notes.forEach((note) => list.push({ id: note.id, tone: note.tone, title: note.title, detail: note.detail, noteId: note.id }));
    return list;
  }, [db, selectedDate]);
}
