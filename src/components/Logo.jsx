export function SailboatMark({ size = 26, className = '' }) {
  return (
    <svg className={className} width={size} height={Math.round(size * 1.1)} viewBox="0 0 40 44" fill="none" aria-hidden="true">
      <path d="M20 1.5V35" stroke="currentColor" strokeWidth="1.6" />
      <path d="M20 1.5L25.5 4L20 6.2Z" fill="currentColor" />
      <path d="M21.6 7.5C27.2 14 30.8 22.5 31.8 31.5H21.6Z" fill="currentColor" />
      <path d="M18.4 12.5C14.2 18.5 11.2 25 10 31.5H18.4Z" fill="currentColor" />
      <path d="M5 34.5H35L30.5 40.5H9.5Z" fill="currentColor" />
    </svg>
  );
}

export function Logo({ tagline = 'Restaurant · Aiguillon-sur-Mer', name = 'La Goëlette' }) {
  return (
    <div className="logo">
      <SailboatMark className="logo-mark" size={24} />
      <span className="logo-name">{name}</span>
      <span className="logo-tagline">{tagline}</span>
    </div>
  );
}
