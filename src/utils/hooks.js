import { useEffect, useMemo, useState } from 'react';

// Ferme un menu quand on clique à l'extérieur ou qu'on appuie sur Échap
export function useDismiss(ref, open, onClose) {
  useEffect(() => {
    if (!open) return undefined;
    const handlePointer = (event) => {
      if (ref.current && !ref.current.contains(event.target)) onClose();
    };
    const handleKey = (event) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('mousedown', handlePointer);
    document.addEventListener('touchstart', handlePointer);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handlePointer);
      document.removeEventListener('touchstart', handlePointer);
      document.removeEventListener('keydown', handleKey);
    };
  }, [ref, open, onClose]);
}

// Tri de tableau : clic sur un en-tête → tri croissant / décroissant
export function useSortedRows(rows, initialKey, initialDir = 'desc') {
  const [sort, setSort] = useState({ key: initialKey, dir: initialDir });
  const sorted = useMemo(() => {
    const list = [...rows];
    list.sort((a, b) => {
      const va = a[sort.key];
      const vb = b[sort.key];
      const result = typeof va === 'string' ? va.localeCompare(vb, 'fr') : (va ?? 0) - (vb ?? 0);
      return sort.dir === 'asc' ? result : -result;
    });
    return list;
  }, [rows, sort]);
  const toggleSort = (key) =>
    setSort((s) => (s.key === key ? { key, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: typeof rows[0]?.[key] === 'string' ? 'asc' : 'desc' }));
  return { sorted, sort, toggleSort };
}
