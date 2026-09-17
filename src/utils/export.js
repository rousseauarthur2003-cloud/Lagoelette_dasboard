// Export CSV (compatible Excel FR : séparateur « ; » et BOM UTF-8) et impression PDF

function escapeCell(value) {
  const text = value === null || value === undefined ? '' : String(value);
  return /[";\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function downloadCSV(filename, columns, rows) {
  const header = columns.map((c) => escapeCell(c.label)).join(';');
  const lines = rows.map((row) =>
    columns
      .map((c) => {
        const raw = row[c.key];
        return escapeCell(typeof raw === 'number' ? String(Math.round(raw * 100) / 100).replace('.', ',') : raw);
      })
      .join(';')
  );
  const blob = new Blob(['\ufeff' + [header, ...lines].join('\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function printReport() {
  document.body.classList.add('printing-report');
  const cleanup = () => {
    document.body.classList.remove('printing-report');
    window.removeEventListener('afterprint', cleanup);
  };
  window.addEventListener('afterprint', cleanup);
  window.print();
  setTimeout(cleanup, 1500);
}
