// Adaptateur « local » : données de démonstration en mémoire.
// Il expose la même interface que les futurs adaptateurs (Google Sheets, API…) :
//   load()                → renvoie la base complète
//   save(collection, data) → persiste une collection
//   reset()               → recharge les données d'origine

import { createMockDatabase } from '../mockData';

export const localAdapter = {
  id: 'local',
  label: 'Données locales (démo)',
  async load() {
    return createMockDatabase();
  },
  async save() {
    // En mémoire : rien à écrire. Brancher ici un appel API ou Google Sheets.
    return true;
  },
  async reset() {
    return createMockDatabase();
  },
};
