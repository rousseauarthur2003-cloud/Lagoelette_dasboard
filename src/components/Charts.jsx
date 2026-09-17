import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, AreaChart, Area, LineChart, Line, ReferenceLine } from 'recharts';
import { useData } from '../context/DataContext';
import { formatMoney, formatNumber } from '../utils/format';

export const CHART_COLORS = {
  gold: '#cfb285',
  blue: '#566e83',
  blueLight: '#7f9cc0',
  lavender: '#a8badb',
  grid: '#1a2833',
  axis: '#2b3945',
  tick: '#c9cdd1',
};

function useChartAnimation() {
  const { db } = useData();
  return db?.settings?.chartAnimations !== false;
}

function MultiLineTick({ x, y, payload }) {
  const lines = String(payload.value).split('\n');
  return (
    <g transform={`translate(${x},${y + 6})`}>
      {lines.map((line, i) => (
        <text key={i} x={0} y={i * 20} dy={10} textAnchor="middle" fill={i === 0 ? CHART_COLORS.tick : '#9aa4ad'} fontSize={12.5}>
          {line}
        </text>
      ))}
    </g>
  );
}

export function ChartTooltip({ active, payload, label, formatter, labelKey = 'label' }) {
  if (!active || !payload?.length) return null;
  const title = payload[0]?.payload?.[labelKey] ?? label;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-title">{title}</div>
      {payload.map((p) => (
        <div key={p.dataKey || p.name} className="chart-tooltip-row">
          <span className="dot" style={{ background: p.color || p.payload?.fill }} />
          <span>{p.name}</span>
          <strong>{formatter ? formatter(p.value, p) : p.value}</strong>
        </div>
      ))}
    </div>
  );
}

export function Sparkline({ data, id, height = 44, color = CHART_COLORS.gold }) {
  const values = data.map((d) => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const floor = min - (max - min || Math.abs(max) || 1) * 0.4;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={`spark-${id}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.55} />
            <stop offset="100%" stopColor={color} stopOpacity={0.08} />
          </linearGradient>
        </defs>
        <YAxis hide domain={[floor, max]} />
        <Area type="monotone" dataKey="value" stroke={color} strokeWidth={1.4} fill={`url(#spark-${id})`} isAnimationActive={false} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function RevenueBarChart({ data, height = 190, currency = '€', barSize = 32, onBarClick }) {
  const animate = useChartAnimation();
  const multiLine = data.some((d) => String(d.tick).includes('\n'));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 6, right: 10, bottom: 0, left: 0 }} barCategoryGap="22%">
        <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} strokeDasharray="0" strokeOpacity={0} />
        <XAxis dataKey="tick" tickLine={false} axisLine={{ stroke: CHART_COLORS.axis }} interval={data.length > 16 ? 'preserveStartEnd' : 0} height={multiLine ? 46 : 26} tick={multiLine ? <MultiLineTick /> : { fill: CHART_COLORS.tick, fontSize: 12 }} />
        <YAxis width={62} tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 12.5 }} tickFormatter={(v) => formatMoney(v, currency)} tickCount={6} />
        <Tooltip cursor={{ fill: 'rgba(207,178,133,0.07)' }} content={<ChartTooltip formatter={(v) => formatMoney(v, currency)} />} />
        <Bar dataKey="value" name="Chiffre d'affaires" fill={CHART_COLORS.gold} radius={[2, 2, 0, 0]} maxBarSize={barSize} isAnimationActive={animate} onClick={onBarClick} cursor={onBarClick ? 'pointer' : undefined} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function RevenueAreaChart({ data, height = 260, currency = '€', goal }) {
  const animate = useChartAnimation();
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 12, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="revenue-area" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={CHART_COLORS.gold} stopOpacity={0.45} />
            <stop offset="100%" stopColor={CHART_COLORS.gold} stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} />
        <XAxis dataKey="tick" tickLine={false} axisLine={{ stroke: CHART_COLORS.axis }} tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} tickFormatter={(v) => String(v).split('\n')[0]} minTickGap={8} />
        <YAxis width={66} tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} tickFormatter={(v) => formatMoney(v, currency)} />
        <Tooltip content={<ChartTooltip formatter={(v) => formatMoney(v, currency)} />} />
        <Area type="monotone" dataKey="value" name="Chiffre d'affaires" stroke={CHART_COLORS.gold} strokeWidth={2} fill="url(#revenue-area)" isAnimationActive={animate} />
        {goal ? <ReferenceLine y={goal} stroke={CHART_COLORS.lavender} strokeDasharray="5 5" label={{ value: `Objectif ${formatMoney(goal, currency)}`, fill: CHART_COLORS.lavender, fontSize: 11.5, position: 'insideTopRight' }} /> : null}
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function DonutChart({ data, centerValue, centerLabel, size = 190, onSliceClick }) {
  const animate = useChartAnimation();
  const outer = size / 2 - 4;
  return (
    <div className="donut" style={{ width: size, height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={outer * 0.72} outerRadius={outer} startAngle={90} endAngle={-270} stroke="none" isAnimationActive={animate} onClick={onSliceClick ? (d) => onSliceClick(d.payload || d) : undefined}>
            {data.map((d) => (
              <Cell key={d.key} fill={d.color} cursor={onSliceClick ? 'pointer' : undefined} />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip labelKey="name" formatter={(v, p) => p?.payload?.display ?? formatNumber(v)} />} />
        </PieChart>
      </ResponsiveContainer>
      <div className="donut-center">
        <strong>{centerValue}</strong>
        <span>{centerLabel}</span>
      </div>
    </div>
  );
}

export function ServiceBarChart({ data, height = 190, stacked = false, barSize = 12 }) {
  const animate = useChartAnimation();
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -14 }} barGap={2} barCategoryGap={data.length > 14 ? '12%' : '26%'}>
        <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} />
        <XAxis dataKey="tick" tickLine={false} axisLine={{ stroke: CHART_COLORS.axis }} tick={{ fill: CHART_COLORS.tick, fontSize: 12.5 }} interval={data.length > 16 ? 'preserveStartEnd' : 0} />
        <YAxis tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 12.5 }} allowDecimals={false} tickCount={6} />
        <Tooltip cursor={{ fill: 'rgba(127,156,192,0.08)' }} content={<ChartTooltip formatter={(v) => `${formatNumber(v)} couverts`} />} />
        <Bar dataKey="lunch" name="Midi" stackId={stacked ? 's' : undefined} fill={CHART_COLORS.gold} maxBarSize={stacked ? 28 : barSize} isAnimationActive={animate} radius={stacked ? [0, 0, 0, 0] : [1, 1, 0, 0]} />
        <Bar dataKey="dinner" name="Soir" stackId={stacked ? 's' : undefined} fill={CHART_COLORS.blueLight} fillOpacity={0.85} maxBarSize={stacked ? 28 : barSize} isAnimationActive={animate} radius={[1, 1, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function RateLineChart({ data, height = 220 }) {
  const animate = useChartAnimation();
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 12, bottom: 0, left: -10 }}>
        <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} />
        <XAxis dataKey="tick" tickLine={false} axisLine={{ stroke: CHART_COLORS.axis }} tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} minTickGap={6} />
        <YAxis tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} tickFormatter={(v) => `${v} %`} domain={[0, 100]} />
        <Tooltip content={<ChartTooltip formatter={(v) => `${v} %`} />} />
        <Line type="monotone" dataKey="lunchRate" name="Remplissage midi" stroke={CHART_COLORS.gold} strokeWidth={2} dot={false} isAnimationActive={animate} />
        <Line type="monotone" dataKey="dinnerRate" name="Remplissage soir" stroke={CHART_COLORS.blueLight} strokeWidth={2} dot={false} isAnimationActive={animate} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function HorizontalBarChart({ data, height = 260, valueFormatter = (v) => v, color = CHART_COLORS.gold, name = 'Valeur' }) {
  const animate = useChartAnimation();
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 16, bottom: 0, left: 0 }} barCategoryGap="28%">
        <CartesianGrid horizontal={false} stroke={CHART_COLORS.grid} />
        <XAxis type="number" tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 11.5 }} tickFormatter={valueFormatter} />
        <YAxis type="category" dataKey="label" width={150} tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 12 }} />
        <Tooltip cursor={{ fill: 'rgba(207,178,133,0.07)' }} content={<ChartTooltip formatter={valueFormatter} />} />
        <Bar dataKey="value" name={name} fill={color} radius={[0, 3, 3, 0]} isAnimationActive={animate} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function SimpleBarChart({ data, height = 200, valueFormatter = (v) => v, name = 'Valeur', color = CHART_COLORS.gold }) {
  const animate = useChartAnimation();
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid vertical={false} stroke={CHART_COLORS.grid} />
        <XAxis dataKey="tick" tickLine={false} axisLine={{ stroke: CHART_COLORS.axis }} tick={{ fill: CHART_COLORS.tick, fontSize: 11.5 }} minTickGap={4} />
        <YAxis width={58} tickLine={false} axisLine={false} tick={{ fill: CHART_COLORS.tick, fontSize: 11.5 }} tickFormatter={valueFormatter} />
        <Tooltip cursor={{ fill: 'rgba(207,178,133,0.07)' }} content={<ChartTooltip formatter={valueFormatter} />} />
        <Bar dataKey="value" name={name} fill={color} radius={[2, 2, 0, 0]} maxBarSize={26} isAnimationActive={animate} />
      </BarChart>
    </ResponsiveContainer>
  );
}
