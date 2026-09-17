import { useMemo, useState } from 'react';
import { Sun, Moon, Users, TrendingUp, Armchair, CalendarRange, Settings } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNav } from '../context/NavContext';
import { PageHero } from '../components/PageHero';
import { Panel, SelectBox, StatCard, Segmented, ProgressBar } from '../components/UI';
import { ServiceBarChart, RateLineChart } from '../components/Charts';
import { summarize, periodRange, previousPeriodRange, coversSeries, coversByWeekday } from '../data/analytics';
import { formatNumber, formatDayMonth, percentChange, TODAY_ISO, WEEK_DAYS } from '../utils/format';

const COVERS_PAGE_PERIODS = [
  { value: 'week', label: '7 derniers jours' },
  { value: '30days', label: '30 derniers jours' },
  { value: 'month', label: 'Ce mois' },
  { value: 'year', label: 'Cette année' },
];

export default function CoversPage() {
  const { db, dayIndex, selectedDate } = useData();
  const { navigate } = useNav();
  const capacity = db.settings.capacity;
  const [period, setPeriod] = useState('30days');
  const [chartMode, setChartMode] = useState('grouped');

  const day = summarize(dayIndex, periodRange('today', selectedDate));
  const prevDay = summarize(dayIndex, periodRange('yesterday', selectedDate));
  const current = summarize(dayIndex, periodRange(period, selectedDate));
  const previous = summarize(dayIndex, previousPeriodRange(period, selectedDate));
  const series = useMemo(() => coversSeries(dayIndex, period, selectedDate, capacity), [dayIndex, period, selectedDate, capacity]);
  const weekdays = useMemo(() => coversByWeekday(dayIndex, periodRange(period === 'week' ? '30days' : period, selectedDate)), [dayIndex, period, selectedDate]);

  const dayLabel = selectedDate === TODAY_ISO ? "aujourd'hui" : `le ${formatDayMonth(selectedDate)}`;
  const lunchRate = capacity ? Math.round((day.lunchCovers / capacity) * 100) : 0;
  const dinnerRate = capacity ? Math.round((day.dinnerCovers / capacity) * 100) : 0;
  const best = [...weekdays].sort((a, b) => b.lunch + b.dinner - (a.lunch + a.dinner))[0];

  return (
    <div className="page">
      <PageHero title="Couverts" subtitle={`Fréquentation du restaurant, service par service. Capacité : ${capacity} places par service.`} />

      <div className="toolbar">
        <SelectBox label="Période" value={period} onChange={setPeriod} options={COVERS_PAGE_PERIODS} />
        <button type="button" className="btn btn-outline" onClick={() => navigate('settings')}><Settings size={15} /> Modifier la capacité</button>
      </div>

      <div className="stat-grid six">
        <StatCard icon={Sun} label={`Midi ${dayLabel}`} value={formatNumber(day.lunchCovers)} change={percentChange(day.lunchCovers, prevDay.lunchCovers)} changeLabel="vs. veille" />
        <StatCard icon={Moon} label={`Soir ${dayLabel}`} value={formatNumber(day.dinnerCovers)} change={percentChange(day.dinnerCovers, prevDay.dinnerCovers)} changeLabel="vs. veille" />
        <StatCard icon={Users} label={`Total ${dayLabel}`} value={formatNumber(day.covers)} change={percentChange(day.covers, prevDay.covers)} changeLabel="vs. veille" accent />
        <StatCard icon={CalendarRange} label="Moyenne par jour" value={formatNumber(current.avgCoversPerDay, 1)} change={percentChange(current.avgCoversPerDay, previous.avgCoversPerDay)} changeLabel="vs. période préc." />
        <StatCard icon={TrendingUp} label="Total de la période" value={formatNumber(current.covers)} change={percentChange(current.covers, previous.covers)} changeLabel="vs. période préc." />
        <StatCard icon={Armchair} label="Taux de remplissage" value={`${capacity ? Math.round((day.covers / (capacity * 2)) * 100) : 0} %`}>
          <div className="mini-rates">
            <span>Midi {lunchRate} %</span><ProgressBar value={day.lunchCovers} max={capacity} label="Remplissage midi" />
            <span>Soir {dinnerRate} %</span><ProgressBar value={day.dinnerCovers} max={capacity} label="Remplissage soir" />
          </div>
        </StatCard>
      </div>

      <Panel
        title="Couverts midi et soir"
        actions={<Segmented label="Affichage" value={chartMode} onChange={setChartMode} options={[{ value: 'grouped', label: 'Côte à côte' }, { value: 'stacked', label: 'Empilés' }]} />}
      >
        <div className="chart-legend left">
          <span><i style={{ background: '#cfb285' }} />Midi · {formatNumber(current.lunchCovers)}</span>
          <span><i style={{ background: '#7f9cc0' }} />Soir · {formatNumber(current.dinnerCovers)}</span>
        </div>
        <ServiceBarChart data={series} height={280} stacked={chartMode === 'stacked'} barSize={series.length > 14 ? 8 : 16} />
      </Panel>

      <div className="grid-2">
        <Panel title="Taux de remplissage par service">
          <RateLineChart data={series} height={240} />
        </Panel>
        <Panel title="Moyenne par jour de la semaine">
          {best && best.lunch + best.dinner > 0 && (
            <p className="panel-note">Le {WEEK_DAYS.find((d) => d.label === best.tick)?.long.toLowerCase()} est le jour le plus fréquenté : {best.lunch + best.dinner} couverts en moyenne.</p>
          )}
          <ServiceBarChart data={weekdays} height={212} stacked />
        </Panel>
      </div>
    </div>
  );
}
