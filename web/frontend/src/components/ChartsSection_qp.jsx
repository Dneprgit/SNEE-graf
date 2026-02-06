import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ComposedChart,
  Line,
  Bar,
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
import { BarChart3, Activity, Battery, Download, Zap } from 'lucide-react';
import * as XLSX from 'xlsx';
import BatteryInteractiveSection_qp from './BatteryInteractiveSection_qp';

const ChartsSection_qp = ({ loadProfile, calculationResult, parameters, setParameters }) => {
  const { eess_schedule, resulting_balance, soc, summary } = calculationResult;
  
  // Состояние для оптимальных параметров QP
  const [optimalParams, setOptimalParams] = useState({
    power_in: null,
    power_out: null,
    capacity: null,
    deficit: null,
    discharge_time: null,
    charge_energy: null,
    charge_time: null
  });

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

        {/* Интерактивный выбор параметров */}
        <BatteryInteractiveSection_qp
          loadProfile={loadProfile}
          parameters={parameters}
          setParameters={setParameters}
          maxAbsValue={maxAbsValue}
          setOptimalParams={setOptimalParams}
        />

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
                  color: 'purple',
                  icon: '↓',
                },
                {
                  label: 'Суммарный разряд',
                  value: `${summary.total_discharge_mwh} МВтч`,
                  subValue: `max ${summary.max_discharge_power_mw} МВт`,
                  color: 'orange',
                  icon: '↑',
                },
                ...(summary.deficit_mw !== undefined ? [{
                  label: 'Дефицит мощности (Dmax)',
                  value: `${summary.deficit_mw} МВт`,
                  subValue: 'из QP оптимизации',
                  color: 'red',
                  icon: '⚠️',
                }] : []),
                ...(summary.reserve_mw !== undefined ? [{
                  label: 'Резерв мощности (Rmax)',
                  value: `${summary.reserve_mw} МВт`,
                  subValue: 'из QP оптимизации',
                  color: 'teal',
                  icon: '✓',
                }] : []),
              ].map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  viewport={{ once: true }}
                  className={`bg-gradient-to-br from-${stat.color}-50 to-${stat.color}-100 border-2 border-${stat.color}-200 rounded-lg p-3 flex items-center gap-3`}
                >
                  <div className="text-2xl flex-shrink-0">{stat.icon}</div>
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
          </div>
          <ResponsiveContainer width="100%" height={500}>
            <ComposedChart data={mainChartData}>
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
              
              {/* Исходный баланс (полупрозрачная область) */}
              <Area
                type="monotone"
                dataKey="original"
                name="Исходный баланс"
                fill="#0ea5e9"
                fillOpacity={0.3}
                stroke="#0ea5e9"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
              
              {/* Заряд и разряд (столбцы) */}
              <Bar
                dataKey="discharge"
                name="Разряд СНЭЭ (выдача)"
                fill="#10b981"
                fillOpacity={0.5}
                stackId="eess"
              />
              <Bar
                dataKey="charge"
                name="Заряд СНЭЭ (потребление)"
                fill="#ef4444"
                fillOpacity={0.5}
                stackId="eess"
              />
              
              {/* Результирующий баланс */}
              <Area
                type="monotone"
                dataKey="resulting"
                name="Результирующий баланс"
                fill="rgba(255, 200, 200, 1)"
                stroke="rgba(255, 100, 100, 1)"
                strokeWidth={3}
              />
            </ComposedChart>
          </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Контейнер для Оптимальных параметров (QP) и графика SOC */}
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(auto,300px)_1fr] gap-6 mb-8">
        
        {/* Оптимальные параметры (QP) */}
        {optimalParams && optimalParams.power_in && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            viewport={{ once: true }}
            className="card"
          >
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <Zap className="w-6 h-6 mr-2 text-primary-600" />
              Оптимальные параметры (алгоритм QP)
            </h3>
            
            <div className="grid grid-cols-1 gap-4">
              {/* dblNIn - Номинальная входная мощность (красный) */}
              <div className="bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Входная мощность</div>
                <div className="text-3xl font-bold text-red-700">{optimalParams.power_in?.toFixed(2)} МВт</div>
              </div>

              {/* Энергия на заряд (светло-красный) */}
              <div className="bg-gradient-to-br from-rose-50 to-rose-100 border-2 border-rose-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Энергия на заряд</div>
                <div className="text-3xl font-bold text-rose-700">{optimalParams.charge_energy?.toFixed(2)} МВтч</div>
              </div>
              
              {/* Фактическое время заряда (фиолетовый) */}
              <div className="bg-gradient-to-br from-violet-50 to-violet-100 border-2 border-violet-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Время заряда</div>
                <div className="text-3xl font-bold text-violet-700">{optimalParams.charge_time?.toFixed(2)} ч</div>
              </div>
              
              {/* dblNOut - Номинальная выходная мощность (зеленый) */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Выходная мощность</div>
                <div className="text-3xl font-bold text-green-700">{optimalParams.power_out?.toFixed(2)} МВт</div>
              </div>
              
              {/* dblCapacity - Емкость (светло-зеленый) */}
              <div className="bg-gradient-to-br from-lime-50 to-lime-100 border-2 border-lime-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Емкость батареи</div>
                <div className="text-3xl font-bold text-lime-700">{optimalParams.capacity?.toFixed(2)} МВтч</div>
              </div>
              
               {/* Фактическое время разряда (фиолетовый) */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Время разряда</div>
                <div className="text-3xl font-bold text-purple-700">{optimalParams.discharge_time?.toFixed(2)} ч</div>
              </div>
              
             {/* Дефицит мощности */}
             <div className="bg-gradient-to-br from-orange-50 to-orange-100 border-2 border-orange-200 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Дефицит мощности</div>
                <div className="text-3xl font-bold text-orange-700">{optimalParams.deficit?.toFixed(2)} МВт</div>
              </div>
              
            </div>
          </motion.div>
        )}        
        
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
          <div className="flex-1 min-h-0">
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

