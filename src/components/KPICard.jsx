import { ArrowUp, ArrowDown } from 'lucide-react';
import { Sparkline } from './Charts';

export function KPICard({ id, icon: Icon, title, value, change, changeSuffix = '%', changeLabel = 'vs. hier', series, onClick }) {
  const hasChange = change !== null && change !== undefined;
  const up = hasChange && change >= 0;
  return (
    <button type="button" className="kpi-card" onClick={onClick} aria-label={`${title} : ${value}`}>
      <span className="kpi-icon"><Icon size={30} strokeWidth={1.9} /></span>
      <span className="kpi-main">
        <span className="kpi-title">{title}</span>
        <span className="kpi-value">{value}</span>
      </span>
      <span className="kpi-spark"><Sparkline data={series} id={id} /></span>
      <span className="kpi-change">
        {hasChange ? (
          <span className={`change ${up ? 'up' : 'down'}`}>
            {up ? <ArrowUp size={14} strokeWidth={2.2} /> : <ArrowDown size={14} strokeWidth={2.2} />}
            {up ? '+' : ''}{change}{changeSuffix}
          </span>
        ) : (
          <span className="change neutral">—</span>
        )}
        <span className="kpi-change-label">{changeLabel}</span>
      </span>
    </button>
  );
}
