// Point unique de branchement des données.
// Interface → DataContext → dataAdapter → (données locales | Google Sheets | API)

import { localAdapter } from './adapters/localAdapter';
// import { createGoogleSheetsAdapter } from './adapters/googleSheetsAdapter';

export const dataAdapter = localAdapter;

// Exemple Google Sheets :
// export const dataAdapter = createGoogleSheetsAdapter({
//   spreadsheetId: 'VOTRE_ID_DE_FEUILLE',
//   apiKey: 'VOTRE_CLE_API_LECTURE',
//   writeEndpoint: 'https://script.google.com/macros/s/.../exec',
// });
