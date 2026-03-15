import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
} from 'recharts';
import { BarChart3, Activity, Battery, Download , Zap } from 'lucide-react';
import * as XLSX from 'xlsx';

const ChartsSection_qp = ({ loadProfile, calculationResult, parameters, scheduleSolver }) => {
  const { eess_schedule, resulting_balance, soc, summary } = calculationResult;
  const resolvedSolver = scheduleSolver || summary?.solver || 'linprog';
  const solverMessage = resolvedSolver === 'highs_qp'
    ? 'Выполнен расчет HiGHS QP'
    : 'Выполнен расчет SciPy linprog';

  const [preset, setPreset] = useState('lineBar');

  const [chartVisibility, setChartVisibility] = useState({
    original: true,
    eess: true,
    resulting: true,
  });

  const [chartType, setChartType] = useState({
    original: 'line',
    eess: 'bar',
    resulting: 'line',
  });

  const applyPreset = (presetName) => {
    if (presetName === 'bar') {
      setChartVisibility({ original: true, eess: false, resulting: true });
      setChartType({ original: 'bar', eess: 'bar', resulting: 'bar' });
    } else if (presetName === 'lineBar') {
      setChartVisibility({ original: true, eess: true, resulting: true });
      setChartType({ original: 'line', eess: 'bar', resulting: 'line' });
    }
    setPreset(presetName);
  };

  const toggleVisibility = (key) => {
    setChartVisibility((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const setChartTypeForKey = (key, type) => {
    setChartType((prev) => ({ ...prev, [key]: type }));
  };

  // Подготовка данных для основного графика
  const mainChartData = loadProfile.map((value, index) => ({
    hour: index + 1,
    original: parseFloat(value.toFixed(2)),
    charge: eess_schedule[index] < 0 ? parseFloat(eess_schedule[index].toFixed(2)) : 0,
    discharge: eess_schedule[index] > 0 ? parseFloat(eess_schedule[index].toFixed(2)) : 0,
    resulting: parseFloat(resulting_balance[index].toFixed(2)),
  }));

  // Данные для SOC графика
  const socChartData = soc.map((value, index) => ({
    hour: index + 1,
    soc: parseFloat(value.toFixed(2)),
    capacity: parameters.dblCapacity_pq,
  }));

  // Вычисление максимального значения для оси Y основного графика
  // Находим максимальное значение по модулю из исходного профиля
  const maxAbsValue = Math.max(...loadProfile.map(v => Math.abs(v)));
  
  // Округляем вверх до ближайшего числа, кратного 100
  const yAxisMax = Math.ceil(maxAbsValue / 100) * 100;
  
  // Используем симметричный диапазон [-yAxisMax, +yAxisMax]
  const yAxisDomain = [-yAxisMax, yAxisMax];

  const exportResults = () => {
    const hours = Array.from({ length: 24 }, (_, i) => i + 1);
    
    const dataSheet = [
      ['Час', 'Исходный баланс, МВт', 'График СНЭЭ, МВт', 'Результирующий баланс, МВт', 'SOC, МВтч'],
      ...hours.map(h => [
        h,
        loadProfile[h - 1],
        eess_schedule[h - 1],
        resulting_balance[h - 1],
        soc[h - 1],
      ]),
    ];

    const summarySheet = [
      ['Показатель', 'Значение'],
      ['Суммарный заряд, МВтч', summary.total_charge_mwh],
      ['Суммарный разряд, МВтч', summary.total_discharge_mwh],
      ['Макс. мощность заряда, МВт', summary.max_charge_power_mw],
      ['Макс. мощность разряда, МВт', summary.max_discharge_power_mw],
      ['Дефицит до СНЭЭ, МВтч', summary.deficit_before_mwh],
      ['Дефицит после СНЭЭ, МВтч', summary.deficit_after_mwh],
      ['Покрытый дефицит, МВтч', summary.deficit_covered_mwh],
      ['Покрытие дефицита, %', summary.deficit_coverage_percent],
      ['Избыток до СНЭЭ, МВтч', summary.surplus_before_mwh],
      ['Избыток после СНЭЭ, МВтч', summary.surplus_after_mwh],
      ['Использованный избыток, МВтч', summary.surplus_utilized_mwh],
      ['Использование избытка, %', summary.surplus_utilization_percent],
      ['', ''],
      ['Результаты QP оптимизации', ''],
      ...(summary.deficit_mw !== undefined ? [['Дефицит мощности (Dmax), МВт', summary.deficit_mw]] : []),
      ...(summary.reserve_mw !== undefined ? [['Резерв мощности (Rmax), МВт', summary.reserve_mw]] : []),
      ['', ''],
      ['Параметры СНЭЭ', ''],
      ['Номинальная активная входная мощность (dblNIn), МВт', parameters.dblNIn_pq],
      ['Номинальная активная выходная мощность (dblNOut), МВт', parameters.dblNOut_pq],
      ['Энергия, фактически отдаваемая в рабочем диапазоне (dblCapacity), МВтч', parameters.dblCapacity_pq],
      ['Энергоэффективность (КПД) (dblEfficiency)', parameters.dblEfficiency_pq],
      ['', ''],
      ['Примечание', ''],
      ['Полярность баланса для QP:', 'положительное = дефицит, отрицательное = избыток'],
    ];

    const wb = XLSX.utils.book_new();
    const wsData = XLSX.utils.aoa_to_sheet(dataSheet);
    const wsSummary = XLSX.utils.aoa_to_sheet(summarySheet);
    
    XLSX.utils.book_append_sheet(wb, wsData, 'Данные');
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Сводка');
    
    XLSX.writeFile(wb, 'snee_results_qp.xlsx');
  };

  return (
    <section id="charts-qp" className="section-container bg-gradient-to-br from-blue-50 to-cyan-50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Результаты расчета (QP)</h2>
        <p className="section-subtitle text-center">
          Диспетчерский график работы СНЭЭ и анализ эффективности
        </p>

        {/* Контейнер для сводной информации и графика */}
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(auto,300px)_1fr] gap-6 mb-8">
          {/* Сводная информация */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="card"
          >
            <div className="flex flex-col gap-2 mb-4">
              <h3 className="text-lg font-bold text-gray-800 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-primary-600" />
                Ключевые показатели
              </h3>
              <div className="text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md px-2 py-1">
                {solverMessage}
              </div>
              <button
                onClick={exportResults}
                className="btn-secondary text-xs flex items-center justify-center"
              >
                <Download className="w-3 h-3 mr-1" />
                Экспорт в Excel
              </button>
            </div>

            <div className="grid grid-cols-1 gap-2">
              {[
                {
                  label: 'Покрытие дефицита',
                  value: `${summary.deficit_coverage_percent}%`,
                  subValue: `${summary.deficit_covered_mwh} МВтч`,
                  color: 'emerald',
                  icon: '✓',
                },
                {
                  label: 'Использование избытка',
                  value: `${summary.surplus_utilization_percent}%`,
                  subValue: `${summary.surplus_utilized_mwh} МВтч`,
                  color: 'blue',
                  icon: '⚡',
                },
                {
                  label: 'Суммарный заряд',
                  value: `${summary.total_charge_mwh} МВтч`,
                  subValue: `max ${summary.max_charge_power_mw} МВт`,
                  color: 'orange',
                  icon: '↓',
                },
                {
                  label: 'Суммарный разряд',
                  value: `${summary.total_discharge_mwh} МВтч`,
                  subValue: `max ${summary.max_discharge_power_mw} МВт`,
                  color: 'green',
                  icon: '↑',
                },
                ...(summary.deficit_mw !== undefined ? [{
                  label: 'Дефицит мощности (Dmax)',
                  value: `${summary.deficit_mw} МВт`,
                  color: Number(summary.deficit_mw) > 0.01 ? 'red' : 'green',
                  ...(Number(summary.deficit_mw) > 0.01 ? { icon: '⚠️' } : {}),
                }] : []),
                // ...(summary.reserve_mw !== undefined ? [{
                //   label: 'Резерв мощности (Rmax)',
                //   value: `${summary.reserve_mw} МВт`,
                //   subValue: 'из QP оптимизации',
                //   color: 'teal',
                //   icon: '✓',
                // }] : []),
              ].map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  viewport={{ once: true }}
                  className={`bg-gradient-to-br from-${stat.color}-50 to-${stat.color}-100 border-2 border-${stat.color}-200 rounded-lg p-3 flex items-center gap-3`}
                >
                  {stat.icon && <div className="text-2xl flex-shrink-0">{stat.icon}</div>}
                  <div className="flex-1">
                    <div className={`text-2xl font-bold text-${stat.color}-700`}>
                      {stat.value}
                    </div>
                    <div className="text-xs font-semibold text-gray-700">{stat.label}</div>
                    <div className="text-xs text-gray-600">{stat.subValue}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Основной график */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="card"
          >
          <div>
            <h3 className="text-xl font-bold text-gray-800 mb-2 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2 text-primary-600" />
              Диспетчерский график работы СНЭЭ (QP)
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Исходный баланс для QP: <span className="text-red-600 font-semibold">положительный</span> = дефицит, <span className="text-green-600 font-semibold">отрицательный</span> = избыток
            </p>
            {/* Пресет отображения */}
            <div className="flex items-center gap-3 mb-4">
              <span className="text-sm font-medium text-gray-700">Пресет:</span>
              <div className="flex rounded overflow-hidden border border-gray-300 text-sm">
                <button
                  type="button"
                  onClick={() => applyPreset('bar')}
                  className={`px-4 py-1.5 ${preset === 'bar' ? 'bg-primary-100 text-primary-700 font-medium' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'}`}
                >
                  Bar
                </button>
                <button
                  type="button"
                  onClick={() => applyPreset('lineBar')}
                  className={`px-4 py-1.5 border-l border-gray-300 ${preset === 'lineBar' ? 'bg-primary-100 text-primary-700 font-medium' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'}`}
                >
                  Line-Bar
                </button>
              </div>
            </div>
            {/* Переключатели видимости и типа графиков */}
            <div className="flex flex-wrap gap-4 mb-4">
              {[
                { key: 'original', label: 'Исходный баланс', color: '#0ea5e9' },
                { key: 'eess', label: 'Заряд и разряд СНЭЭ', color: '#10b981' },
                { key: 'resulting', label: 'Результирующий баланс', color: '#ff6464' },
              ].map(({ key, label, color }) => (
                <div key={key} className="flex items-center gap-2 flex-wrap">
                  <label className="flex items-center gap-1.5 cursor-pointer select-none text-sm">
                    <input
                      type="checkbox"
                      checked={chartVisibility[key]}
                      onChange={() => toggleVisibility(key)}
                      className="w-4 h-4 rounded border-gray-300"
                    />
                    <span
                      className="w-3 h-3 rounded-full shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    <span className={chartVisibility[key] ? 'text-gray-800' : 'text-gray-400 line-through'}>
                      {label}
                    </span>
                  </label>
                  <div className="flex rounded overflow-hidden border border-gray-300 text-xs">
                    <button
                      type="button"
                      onClick={() => setChartTypeForKey(key, 'bar')}
                      disabled={!chartVisibility[key]}
                      className={`px-2 py-0.5 ${chartType[key] === 'bar' ? 'bg-primary-100 text-primary-700 font-medium' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'} disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      Столб
                    </button>
                    <button
                      type="button"
                      onClick={() => setChartTypeForKey(key, 'line')}
                      disabled={!chartVisibility[key]}
                      className={`px-2 py-0.5 border-l border-gray-300 ${chartType[key] === 'line' ? 'bg-primary-100 text-primary-700 font-medium' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'} disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      Линия
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={500}>
            <ComposedChart data={mainChartData} barGap="-80%">
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="hour"
                label={{ value: 'Час', position: 'insideBottom', offset: -5 }}
                stroke="#666"
              />
              <YAxis
                domain={yAxisDomain}
                label={{ value: 'Мощность, МВт', angle: -90, position: 'insideLeft' }}
                stroke="#666"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                  padding: '10px',
                }}
              />
              <Legend />
              <ReferenceLine y={0} stroke="#000" strokeWidth={2} />
              
              {/* Исходный баланс */}
              {chartVisibility.original && (
                chartType.original === 'bar' ? (
                  <Bar
                    dataKey="original"
                    name="Исходный баланс"
                    fill="#0ea5e9"
                    fillOpacity={0.4}
                  />
                ) : (
                  <Line
                    type="linear"
                    dataKey="original"
                    name="Исходный баланс"
                    stroke="#0ea5e9"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    connectNulls
                  />
                )
              )}
              
              {/* Заряд и разряд СНЭЭ */}
              {chartVisibility.eess && (
                chartType.eess === 'bar' ? (
                  <>
                    <Bar
                      dataKey="discharge"
                      name="Разряд СНЭЭ (выдача)"
                      fill="#10b981"
                      fillOpacity={0.4}
                    />
                    <Bar
                      dataKey="charge"
                      name="Заряд СНЭЭ (потребление)"
                      fill="#ef4444"
                      fillOpacity={0.4}
                    />
                  </>
                ) : (
                  <>
                    <Line
                      type="linear"
                      dataKey="discharge"
                      name="Разряд СНЭЭ (выдача)"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={false}
                      connectNulls
                    />
                    <Line
                      type="linear"
                      dataKey="charge"
                      name="Заряд СНЭЭ (потребление)"
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={false}
                      connectNulls
                    />
                  </>
                )
              )}
              
              {/* Результирующий баланс */}
              {chartVisibility.resulting && (
                chartType.resulting === 'bar' ? (
                  <Bar
                    dataKey="resulting"
                    name="Результирующий баланс"
                    fill="rgba(255, 100, 100, 0.5)"
                  />
                ) : (
                  <Line
                    type="linear"
                    dataKey="resulting"
                    name="Результирующий баланс"
                    stroke="rgba(255, 100, 100, 1)"
                    strokeWidth={3}
                    dot={false}
                    connectNulls
                  />
                )
              )}
            </ComposedChart>
          </ResponsiveContainer>
          </motion.div>
        </div>

        {/* <div className="grid grid-cols-1 gap-6 mb-8"> */}


        {/* Контейнер для Оптимальных параметров (QP) и графика SOC */}
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(auto,300px)_1fr] gap-6 mb-8">
        
        {/* Оптимальные параметры (QP) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            viewport={{ once: true }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <Zap className="w-6 h-6 mr-2 text-primary-600" />
              Параметры СНЭЭ
            </h3>
            
            {/* <div className="grid grid-cols-1 gap-4">
            <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-3 border-2 border-red-300">
                <div className="text-xs text-gray-600 mb-0.5">Номинальная активная входная мощность (dblNIn)</div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 border-2 border-green-300">
                <div className="text-xs text-gray-600 mb-0.5">Номинальная активная выходная мощность (dblNOut)</div>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border-2 border-blue-300">
                <div className="text-xs text-gray-600 mb-0.5">Энергия, фактически отдаваемая в рабочем диапазоне (dblCapacity)</div>
              </div>

              <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3 border-2 border-purple-300">
                <div className="text-xs text-gray-600 mb-0.5">Энергоэффективность (КПД) (dblEfficiency)</div>
              </div>
            </div> */}
          </motion.div>




        {/* График SOC */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="card flex flex-col"
        >
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Battery className="w-6 h-6 mr-2 text-primary-600" />
            Состояние заряда батареи (SOC)
          </h3>
          <div className="flex-1 min-h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={socChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="hour"
                label={{ value: 'Час', position: 'insideBottom', offset: -5 }}
                stroke="#666"
              />
              <YAxis
                label={{ value: 'Энергия, МВтч', angle: -90, position: 'insideLeft' }}
                stroke="#666"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <ReferenceLine
                y={parameters.dblCapacity_pq}
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: `Макс. емкость: ${parameters.dblCapacity_pq} МВтч`,
                  position: 'right',
                  fill: '#ef4444',
                }}
              />
              <Area
                type="monotone"
                dataKey="soc"
                name="Заряд батареи"
                fill="rgba(139, 92, 246, 0.3)"
                stroke="#8b5cf6"
                strokeWidth={3}
              />
            </AreaChart>
          </ResponsiveContainer>
          </div>
        </motion.div>


        </div>
      </motion.div>
    </section>
  );
};

export default ChartsSection_qp;

