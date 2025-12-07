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
import { BarChart3, Activity, Battery, Download } from 'lucide-react';
import * as XLSX from 'xlsx';
import BatteryInteractiveSection from './BatteryInteractiveSection';

const ChartsSection = ({ loadProfile, calculationResult, parameters, setParameters }) => {
  const { eess_schedule, resulting_balance, soc, summary } = calculationResult;

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
    capacity: parameters.rated_capacity_mwh,
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
      ['Параметры СНЭЭ', ''],
      ['Мощность инвертора, МВт', parameters.rated_power_mw],
      ['Емкость батареи, МВтч', parameters.rated_capacity_mwh],
      ['КПД цикла', parameters.efficiency],
    ];

    const wb = XLSX.utils.book_new();
    const wsData = XLSX.utils.aoa_to_sheet(dataSheet);
    const wsSummary = XLSX.utils.aoa_to_sheet(summarySheet);
    
    XLSX.utils.book_append_sheet(wb, wsData, 'Данные');
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Сводка');
    
    XLSX.writeFile(wb, 'snee_results.xlsx');
  };

  return (
    <section id="charts" className="section-container bg-gradient-to-br from-blue-50 to-cyan-50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Результаты расчета</h2>
        <p className="section-subtitle text-center">
          Диспетчерский график работы СНЭЭ и анализ эффективности
        </p>

        {/* Сводная информация */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="card mb-8"
        >
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-bold text-gray-800 flex items-center">
              <Activity className="w-6 h-6 mr-2 text-primary-600" />
              Ключевые показатели
            </h3>
            <button
              onClick={exportResults}
              className="btn-secondary text-sm flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Экспорт в Excel
            </button>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
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
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                viewport={{ once: true }}
                className={`bg-gradient-to-br from-${stat.color}-50 to-${stat.color}-100 border-2 border-${stat.color}-200 rounded-xl p-6 text-center`}
              >
                <div className="text-3xl mb-2">{stat.icon}</div>
                <div className={`text-3xl font-bold text-${stat.color}-700 mb-1`}>
                  {stat.value}
                </div>
                <div className="text-sm font-semibold text-gray-700">{stat.label}</div>
                <div className="text-xs text-gray-600 mt-1">{stat.subValue}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Интерактивный выбор параметров */}
        <BatteryInteractiveSection
          loadProfile={loadProfile}
          parameters={parameters}
          setParameters={setParameters}
        />

        {/* Основной график */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="card mb-8"
        >
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-primary-600" />
            Диспетчерский график работы СНЭЭ
          </h3>
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
                stackId="eess"
              />
              <Bar
                dataKey="charge"
                name="Заряд СНЭЭ (потребление)"
                fill="#ef4444"
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

        {/* График SOC */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="card"
        >
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Battery className="w-6 h-6 mr-2 text-primary-600" />
            Состояние заряда батареи (SOC)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
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
                y={parameters.rated_capacity_mwh}
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: `Макс. емкость: ${parameters.rated_capacity_mwh} МВтч`,
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
        </motion.div>
      </motion.div>
    </section>
  );
};

export default ChartsSection;

