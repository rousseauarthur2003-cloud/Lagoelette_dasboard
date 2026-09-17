import { ChevronDown, ArrowUp, ArrowDown, ChevronsUpDown } from 'lucide-react';

export function Panel({ title, icon: Icon, actions, children, className = '', bodyClassName = '' }) {
  return (
    <section className={`panel ${className}`}>
      {(title || actions) && (
        <header className="panel-head">
          <h2 className="panel-title">
            {Icon && <Icon size={19} className="panel-title-icon" />}
            <span className="panel-title-text">{title}</span>
          </h2>
          {actions && <div className="panel-actions">{actions}</div>}
        </header>
      )}
      <div className={`panel-body ${bodyClassName}`}>{children}</div>
    </section>
  );
}

export function SelectBox({ value, onChange, options, label, className = '', small = false }) {
  return (
    <label className={`select-wrap ${small ? 'select-sm' : ''} ${className}`}>
      <span className="sr-only">{label}</span>
      <select className="select" value={value} onChange={(e) => onChange(e.target.value)} aria-label={label}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      <ChevronDown size={15} className="select-chevron" aria-hidden="true" />
    </label>
  );
}

export function Tabs({ value, onChange, options, label }) {
  return (
    <div className="tabs" role="tablist" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="tab"
          aria-selected={value === o.value}
          className={`tab ${value === o.value ? 'active' : ''}`}
          onClick={() => onChange(o.value)}
        >
          {o.icon && <o.icon size={15} />}
          {o.label}
          {o.count !== undefined && <span className="tab-count">{o.count}</span>}
        </button>
      ))}
    </div>
  );
}

export function Field({ label, children, span = 1, hint, group = false }) {
  const Tag = group ? 'div' : 'label';
  return (
    <Tag className={`field ${span === 2 ? 'span-2' : ''}`} role={group ? 'group' : undefined} aria-label={group ? label : undefined}>
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </Tag>
  );
}

export function Badge({ tone = 'grey', children, onClick, title }) {
  if (onClick) {
    return (
      <button type="button" className={`badge badge-${tone} badge-button`} onClick={onClick} title={title}>
        {children}
      </button>
    );
  }
  return <span className={`badge badge-${tone}`} title={title}>{children}</span>;
}

export function Change({ value, suffix = '%', label }) {
  if (value === null || value === undefined) return <span className="change neutral">—</span>;
  const up = value >= 0;
  return (
    <span className={`change ${up ? 'up' : 'down'}`}>
      {up ? <ArrowUp size={13} strokeWidth={2.4} /> : <ArrowDown size={13} strokeWidth={2.4} />}
      {up ? '+' : ''}{value}{suffix}
      {label && <em>{label}</em>}
    </span>
  );
}

export function StatCard({ label, value, change, changeLabel, icon: Icon, onClick, accent, children }) {
  const Tag = onClick ? 'button' : 'div';
  return (
    <Tag type={onClick ? 'button' : undefined} className={`stat-card ${onClick ? 'clickable' : ''} ${accent ? 'accent' : ''}`} onClick={onClick}>
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        {Icon && <Icon size={17} className="stat-icon" />}
      </div>
      <strong className="stat-value">{value}</strong>
      {change !== undefined && <Change value={change} label={changeLabel} />}
      {children}
    </Tag>
  );
}

export function SortableTh({ label, sortKey, sort, onSort, align = 'left' }) {
  const active = sort.key === sortKey;
  return (
    <th className={`th-sort ${align === 'right' ? 'num' : ''}`} aria-sort={active ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}>
      <button type="button" onClick={() => onSort(sortKey)}>
        {label}
        {active ? (sort.dir === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />) : <ChevronsUpDown size={12} className="dim" />}
      </button>
    </th>
  );
}

export function Segmented({ value, onChange, options, label }) {
  return (
    <div className="segmented" role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" role="radio" aria-checked={value === o.value} className={value === o.value ? 'active' : ''} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Toggle({ checked, onChange, label, description }) {
  return (
    <label className="toggle-row">
      <span>
        <span className="toggle-label">{label}</span>
        {description && <span className="toggle-desc">{description}</span>}
      </span>
      <button type="button" role="switch" aria-checked={checked} className={`toggle ${checked ? 'on' : ''}`} onClick={() => onChange(!checked)}>
        <span />
      </button>
    </label>
  );
}

export function EmptyState({ icon: Icon, title, text, action }) {
  return (
    <div className="empty">
      {Icon && <Icon size={26} />}
      <strong>{title}</strong>
      {text && <p>{text}</p>}
      {action}
    </div>
  );
}

export function ProgressBar({ value, max, label }) {
  const pct = max ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div className="progress" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
      <span style={{ width: `${pct}%` }} />
    </div>
  );
}
