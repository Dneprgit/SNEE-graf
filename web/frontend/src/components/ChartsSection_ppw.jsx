import { motion } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import BatteryInteractiveSection_ppw from './BatteryInteractiveSection_ppw';

const ChartsSection_ppw = ({ loadProfile, calculationResult, parameters, setParameters }) => {
  // Подготовка данных для графиков
  const chartData = loadProfile?.map((value, index) => ({
    hour: index + 1,
    initial_balance: value,
    eess_load: calculationResult?.eess_load?.[index] || 0,
    resulting_balance: calculationResult?.resulting_balance?.[index] || value,
    soc: calculationResult?.soc?.[index] || 0,
  })) || [];

  return (
    <>
      {/* Интерактивная секция выбора параметров */}
      <BatteryInteractiveSection_ppw
        loadProfile={loadProfile}
        parameters={parameters}
        setParameters={setParameters}
      />

      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="section-container py-12 bg-gray-50"
      >
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-center">Результаты расчета (PPW)</h2>

        {/* Ключевые показатели */}
        {calculationResult?.summary && (
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Заряд</div>
              <div className="text-xl font-bold">{calculationResult.summary.total_charge_mwh} МВтч</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Разряд</div>
              <div className="text-xl font-bold">{calculationResult.summary.total_discharge_mwh} МВтч</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Покрыто дефицита</div>
              <div className="text-xl font-bold">{calculationResult.summary.deficit_covered_mwh} МВтч</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Использовано избытка</div>
              <div className="text-xl font-bold">{calculationResult.summary.surplus_utilized_mwh} МВтч</div>
            </div>
          </div>
        )}

        {/* Основной график - три графика на одном */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-xl font-semibold mb-4">Суточный баланс мощности энергосистемы</h3>
          <ResponsiveContainer width="100%" height={450}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="hour" 
                label={{ value: 'Час суток', position: 'insideBottom', offset: -5 }} 
              />
              <YAxis 
                label={{ value: 'Мощность, МВт', angle: -90, position: 'insideLeft' }} 
              />
              <Tooltip 
                formatter={(value, name) => {
                  const formatted = Number(value).toFixed(2);
                  return [formatted + ' МВт', name];
                }}
              />
              <Legend />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
              
              {/* График 1: Исходный баланс (линия синяя) */}
              <Line 
                type="monotone" 
                dataKey="initial_balance" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Исходный баланс" 
                dot={false}
              />
              
              {/* График 2: Нагрузка СНЭЭ (столбики с цветовой дифференциацией) */}
              <Bar 
                dataKey="eess_load" 
                name="Нагрузка СНЭЭ"
                shape={(props) => {
                  const { x, y, width, height, value } = props;
                  const fill = value > 0 ? '#10B981' : '#EF4444'; // зеленый для разряда, красный для заряда
                  return <rect x={x} y={y} width={width} height={height} fill={fill} opacity={0.7} />;
                }}
              />
              
              {/* График 3: Результирующий баланс (линия фиолетовая) */}
              <Line 
                type="monotone" 
                dataKey="resulting_balance" 
                stroke="#8B5CF6" 
                strokeWidth={2}
                name="Результирующий баланс" 
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* График SOC */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Состояние заряда батареи (SOC)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" label={{ value: 'Час суток', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Заряд, МВтч', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="soc" stroke="#F59E0B" strokeWidth={2} name="SOC" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.section>
    </>
  );
};

export default ChartsSection_ppw;

