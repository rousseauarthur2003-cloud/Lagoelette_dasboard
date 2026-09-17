# La Goëlette — Tableau de bord de gestion

Application React + Vite pour piloter le restaurant : chiffre d'affaires, couverts, plats, stocks, achats, réservations, équipe, rapports et paramètres.

## Lancer le projet

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # version de production dans dist/
```

Node.js 18 ou plus récent est nécessaire.

## Organisation

```
src/
├── App.jsx                 Coquille : sidebar + barre du haut + page active
├── main.jsx
├── assets/                 Photos (port, terrasse) — remplaçables par vos photos HD
├── components/             Sidebar, Header, KPICard, Charts, Modal, UI, Toast, ReservationModal…
├── pages/                  Dashboard, Revenue, Covers, Sales, Stock, Reservations, Team, Reports, Settings
├── context/                DataContext (données + actions), NavContext (navigation)
├── data/
│   ├── mockData.js         Données de démonstration
│   ├── analytics.js        Calculs métier (CA, marges, stocks, TVA…)
│   ├── dataSource.js       ← choix de la source de données
│   └── adapters/           localAdapter (démo) · googleSheetsAdapter (prêt à brancher)
├── config/navigation.js    Rubriques du menu
├── utils/                  Formats FR, hooks, export CSV / impression PDF
└── styles/global.css       Palette, typographie, responsive, impression
```

Les composants ne lisent jamais les données brutes directement : ils passent par `DataContext`, qui s'appuie sur un adaptateur. Changer de source (Google Sheets, API, base de données) se fait dans `src/data/dataSource.js` sans toucher à l'interface.

## Brancher Google Sheets

1. Créez un onglet par collection : `dailyStats`, `dishes`, `reservations`, `stock`, `purchases`, `team`, `notes`, `settings`.
2. Mettez les noms de colonnes en première ligne (le détail est en tête de `googleSheetsAdapter.js`).
3. Lecture : clé API Google Sheets (feuille partagée en lecture).
4. Écriture : passez par un Google Apps Script publié en application web (`writeEndpoint`) ; ne mettez aucun identifiant secret dans le navigateur.
5. Dans `dataSource.js`, remplacez `localAdapter` par `createGoogleSheetsAdapter({...})`.

## À savoir

- La date de référence des données de démo est fixée dans `src/utils/format.js` (`TODAY_ISO`). Avec de vraies données, remplacez-la par la date du jour.
- Les deux photos ont été extraites de la maquette : elles sont en basse résolution. Remplacez `src/assets/port-aiguillon.jpg` et `terrasse.jpg` par les originaux pour un rendu net.
- Polices : Cormorant Garamond (titres, logo) et Inter (interface), chargées depuis Google Fonts.
- Export PDF : bouton « Exporter PDF » → impression du rapport seul (choisir « Enregistrer au format PDF »).
- En mode démo, les modifications restent en mémoire tant que la page est ouverte.

## Mettre en ligne (GitHub + Hostinger)

```bash
npm install
npm run build          # génère dist/
git init
git add .
git commit -m "Tableau de bord La Goëlette"
git branch -M main
git remote add origin https://github.com/rousseauarthur2003-cloud/NOM-DU-DEPOT.git
git push -u origin main
```

Hostinger copie les fichiers du dépôt sans les construire. Pour un déploiement par Git, retirez la ligne `dist` du `.gitignore`, refaites `npm run build`, commitez le dossier `dist` et indiquez-le comme dossier source dans hPanel → Git. Sinon, envoyez le contenu de `dist/` par le gestionnaire de fichiers.
