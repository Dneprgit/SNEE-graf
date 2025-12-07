import { motion } from 'framer-motion';
import { AreaChart, Area, LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Edit, TrendingUp, TrendingDown, Calculator, AlertCircle } from 'lucide-react';

const DataVisualizationSection = ({ loadProfile, onCalculate, isCalculating, error }) => {
  const chartData = loadProfile.map((value, index) => ({
    hour: index + 1,
    balance: parseFloat(value.toFixed(2)),
  }));

  const stats = {
    max: Math.max(...loadProfile),
    min: Math.min(...loadProfile),
    avg: loadProfile.reduce((a, b) => a + b, 0) / loadProfile.length,
    surplus: loadProfile.filter(v => v > 0).reduce((a, b) => a + b, 0),
    deficit: Math.abs(loadProfile.filter(v => v < 0).reduce((a, b) => a + b, 0)),
  };

  return (
    <section id="data-visualization" className="section-container bg-gradient-to-br from-purple-50 to-pink-50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Визуализация исходных данных</h2>
        <p className="section-subtitle text-center">
          Интерактивный просмотр и редактирование профиля баланса мощности
        </p>

        {/* Статистика */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8 max-w-5xl mx-auto">
          {[
            { label: 'Максимум', value: stats.max.toFixed(1), unit: 'МВт', icon: TrendingUp, color: 'green' },
            { label: 'Минимум', value: stats.min.toFixed(1), unit: 'МВт', icon: TrendingDown, color: 'red' },
            { label: 'Среднее', value: stats.avg.toFixed(1), unit: 'МВт', icon: Edit, color: 'blue' },
            { label: 'Избыток', value: stats.surplus.toFixed(1), unit: 'МВтч', icon: TrendingUp, color: 'emerald' },
            { label: 'Дефицит', value: stats.deficit.toFixed(1), unit: 'МВтч', icon: TrendingDown, color: 'orange' },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              viewport={{ once: true }}
              className={`card bg-gradient-to-br from-${stat.color}-50 to-${stat.color}-100 border border-${stat.color}-200`}
            >
              <stat.icon className={`w-6 h-6 text-${stat.color}-600 mb-2`} />
              <div className={`text-2xl font-bold text-${stat.color}-700`}>
                {stat.value}
              </div>
              <div className="text-xs text-gray-600">{stat.label}</div>
              <div className="text-xs text-gray-500">{stat.unit}</div>
            </motion.div>
          ))}
        </div>

        {/* График */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="card mb-8"
        >
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Суточный профиль баланса мощности
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="hour" 
                label={{ value: 'Час', position: 'insideBottom', offset: -5 }}
                stroke="#666"
              />
              <YAxis 
                label={{ value: 'Мощность, МВт', angle: -90, position: 'insideLeft' }}
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
              <ReferenceLine y={0} stroke="#000" strokeWidth={2} />
              <Area
                type="monotone"
                dataKey="balance"
                name="Баланс мощности"
                stroke="#0ea5e9"
                fill="#0ea5e9"
                fillOpacity={0.3}
                strokeWidth={2}
                dot={{ r: 4, fill: '#0ea5e9' }}
                activeDot={{ r: 6 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Столбчатая диаграмма */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="card mb-8"
        >
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Распределение избытков и дефицитов
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="hour" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <ReferenceLine y={0} stroke="#000" strokeWidth={2} />
              <Bar
                dataKey="balance"
                name="Баланс мощности"
                radius={[4, 4, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.balance > 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Кнопка расчета */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="text-center mt-8"
        >
          <button
            onClick={onCalculate}
            disabled={!loadProfile || isCalculating}
            className={`btn-primary text-lg px-12 py-4 ${
              !loadProfile || isCalculating ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isCalculating ? (
              <>
                <span className="inline-block animate-spin mr-2">⚙️</span>
                Расчет...
              </>
            ) : (
              <>
                <Calculator className="inline-block w-6 h-6 mr-2" />
                Рассчитать график
              </>
            )}
          </button>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 max-w-2xl mx-auto flex items-start"
            >
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </section>
  );
};

export default DataVisualizationSection;

