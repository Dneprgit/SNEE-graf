import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Calculator, TrendingUp, TrendingDown, Activity, Info } from 'lucide-react';

const DataVisualizationSection_ppw = ({ loadProfile, onCalculate, isCalculating, error }) => {
  const chartData = loadProfile?.map((value, index) => ({
    hour: index + 1,
    balance: value,
  })) || [];

  const stats = loadProfile ? {
    max: Math.max(...loadProfile),
    min: Math.min(...loadProfile),
    avg: loadProfile.reduce((a, b) => a + b, 0) / loadProfile.length,
    surplus: loadProfile.filter(v => v < 0).reduce((a, b) => a + b, 0),
    deficit: loadProfile.filter(v => v > 0).reduce((a, b) => a + b, 0),
  } : null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="section-container py-12"
    >
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-center">
          Суточный профиль баланса мощности энергосистемы
        </h2>
        <p className="text-center text-gray-600 mb-8 flex items-center justify-center gap-2">
          <Info className="w-5 h-5" />
          Положительные значения: не покрываемое потребление (+), Отрицательные: избыток генерации (-)
        </p>

        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-red-500" />
              <span className="text-sm text-gray-600">Макс. дефицит</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats?.max.toFixed(1) || 0} МВт</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-600">Макс. избыток</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats?.min.toFixed(1) || 0} МВт</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-600">Суммарный дефицит</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats?.deficit.toFixed(1) || 0} МВтч</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span className="text-sm text-gray-600">Суммарный избыток</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{Math.abs(stats?.surplus || 0).toFixed(1)} МВтч</div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="hour"
                label={{ value: 'Час суток', position: 'insideBottom', offset: -5 }}
              />
              <YAxis label={{ value: 'Баланс мощности, МВт', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                formatter={(value) => [`${value.toFixed(2)} МВт`, 'Баланс']}
                labelFormatter={(hour) => `Час ${hour}`}
              />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
              <Line
                type="monotone"
                dataKey="balance"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="text-center">
          <button
            onClick={onCalculate}
            disabled={isCalculating || !loadProfile}
            className="btn-primary flex items-center gap-2 mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Calculator className="w-5 h-5" />
            {isCalculating ? 'Расчет...' : 'Рассчитать график'}
          </button>
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>
      </div>
    </motion.section>
  );
};

export default DataVisualizationSection_ppw;

