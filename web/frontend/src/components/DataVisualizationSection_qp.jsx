import { motion } from 'framer-motion';
import { useState, useRef, useEffect } from 'react';
import { AreaChart, Area, LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Edit, TrendingUp, TrendingDown, Calculator, AlertCircle, RotateCcw } from 'lucide-react';

// Кастомный компонент для перетаскиваемых точек
const DraggableDot = ({ cx, cy, index, onDrag, isDragging, isActive }) => {
  const handlePointerDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    onDrag(index, 'start', e);
  };

  return (
    <g>
      {/* Внешнее свечение при перетаскивании */}
      {(isDragging || isActive) && (
        <circle
          cx={cx}
          cy={cy}
          r={12}
          fill="#0ea5e9"
          opacity={0.2}
          style={{ pointerEvents: 'none' }}
        />
      )}
      {/* Основная точка */}
      <circle
        cx={cx}
        cy={cy}
        r={isDragging ? 8 : isActive ? 6 : 5}
        fill={isDragging ? "#0284c7" : "#0ea5e9"}
        stroke="#fff"
        strokeWidth={2}
        style={{ 
          cursor: isDragging ? 'grabbing' : 'grab',
          transition: isDragging ? 'none' : 'all 0.2s ease',
          filter: isDragging ? 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3))' : 'none'
        }}
        onPointerDown={handlePointerDown}
        onMouseEnter={() => onDrag(index, 'hover', null)}
        onMouseLeave={() => onDrag(index, 'unhover', null)}
      />
    </g>
  );
};

const DataVisualizationSection_qp = ({ loadProfile, setLoadProfile, onCalculate, isCalculating, error }) => {
  const chartRef = useRef(null);
  const [draggingIndex, setDraggingIndex] = useState(null);
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [originalProfile, setOriginalProfile] = useState(null);
  const [yAxisDomain, setYAxisDomain] = useState([0, 0]);

  // Сохраняем оригинальный профиль при первой загрузке
  useEffect(() => {
    if (loadProfile && !originalProfile) {
      setOriginalProfile([...loadProfile]);
    }
  }, [loadProfile, originalProfile]);

  // Вычисляем диапазон YAxis
  useEffect(() => {
    if (loadProfile) {
      const min = Math.min(...loadProfile);
      const max = Math.max(...loadProfile);
      const padding = (max - min) * 0.1 || 100;
      setYAxisDomain([Math.floor(min - padding), Math.ceil(max + padding)]);
    }
  }, [loadProfile]);
  const chartData = loadProfile.map((value, index) => ({
    hour: index + 1,
    balance: parseFloat(value.toFixed(2)),
  }));

  // Обработчик перетаскивания точки
  const handleDragPoint = (index, action, event) => {
    if (action === 'start') {
      setDraggingIndex(index);
      
      const handlePointerMove = (e) => {
        if (chartRef.current) {
          const rect = chartRef.current.querySelector('.recharts-wrapper').getBoundingClientRect();
          const chartContainer = chartRef.current.querySelector('.recharts-surface');
          
          if (chartContainer) {
            // Получаем относительную позицию внутри графика
            const relativeY = e.clientY - rect.top;
            
            // Преобразуем Y-координату в значение данных
            const [yMin, yMax] = yAxisDomain;
            const yRange = yMax - yMin;
            
            // Учитываем padding графика (примерно 5% сверху и снизу)
            const padding = 0.05;
            const effectiveHeight = rect.height * (1 - 2 * padding);
            const yOffset = rect.height * padding;
            
            // Вычисляем новое значение
            const normalizedY = (relativeY - yOffset) / effectiveHeight;
            const clampedY = Math.max(0, Math.min(1, normalizedY));
            const newValue = yMax - (clampedY * yRange);
            
            // Обновляем массив loadProfile
            const newLoadProfile = [...loadProfile];
            newLoadProfile[index] = Math.round(newValue * 10) / 10; // Округляем до 1 знака
            setLoadProfile(newLoadProfile);
          }
        }
      };
      
      const handlePointerUp = () => {
        setDraggingIndex(null);
        document.removeEventListener('pointermove', handlePointerMove);
        document.removeEventListener('pointerup', handlePointerUp);
        document.removeEventListener('touchmove', handlePointerMove);
        document.removeEventListener('touchend', handlePointerUp);
      };
      
      // Поддержка как мыши, так и touch-событий
      document.addEventListener('pointermove', handlePointerMove);
      document.addEventListener('pointerup', handlePointerUp);
      document.addEventListener('touchmove', handlePointerMove, { passive: false });
      document.addEventListener('touchend', handlePointerUp);
    } else if (action === 'hover') {
      setHoveredIndex(index);
    } else if (action === 'unhover') {
      setHoveredIndex(null);
    }
  };

  // Кастомный рендер точек
  const renderCustomDot = (props) => {
    const { cx, cy, index } = props;
    return (
      <DraggableDot
        key={`dot-${index}`}
        cx={cx}
        cy={cy}
        index={index}
        onDrag={handleDragPoint}
        isDragging={draggingIndex === index}
        isActive={hoveredIndex === index}
      />
    );
  };

  // Отмена изменений
  const handleReset = () => {
    if (originalProfile) {
      setLoadProfile([...originalProfile]);
    }
  };

  // Проверка, были ли изменения
  const hasChanges = originalProfile && 
    JSON.stringify(loadProfile) !== JSON.stringify(originalProfile);

  const stats = {
    max: Math.max(...loadProfile),
    min: Math.min(...loadProfile),
    avg: loadProfile.reduce((a, b) => a + b, 0) / loadProfile.length,
    surplus: loadProfile.filter(v => v > 0).reduce((a, b) => a + b, 0),
    deficit: Math.abs(loadProfile.filter(v => v < 0).reduce((a, b) => a + b, 0)),
    surplusTime: loadProfile.filter(v => v > 0).length,
    deficitTime: loadProfile.filter(v => v < 0).length,
  };

  return (
    <section id="data-visualization-qp" className="section-container bg-gradient-to-br from-purple-50 to-pink-50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Визуализация исходных данных (QP)</h2>
        <p className="section-subtitle text-center">
          Интерактивный просмотр и редактирование профиля баланса мощности
        </p>
        {/* Контейнер для статистики и графика */}
        <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-6 mb-8 max-w-7xl mx-auto">
        {/* Статистика */}
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: <>Максимальный<br/>избыток<br/>мощности,</>, value: stats.max.toFixed(0), unit: 'МВт', icon: TrendingUp, color: 'green' },
            { label: <>Максимальный<br/>дефицит<br/>мощности,</>, value: stats.min.toFixed(0), unit: 'МВт', icon: TrendingDown, color: 'red' },
            { label: <>Избыток<br/>электрической<br/>энергии,</>, value: stats.surplus.toFixed(0), unit: 'МВтч', icon: TrendingUp, color: 'green' },
            { label: <>Дефицит<br/>электрической<br/>энергии,</>, value: stats.deficit.toFixed(0), unit: 'МВтч', icon: TrendingDown, color: 'red' },
            { label: <>Время<br/>избытка,</>, value: stats.surplusTime, unit: 'ч', icon: TrendingUp, color: 'green' },
            { label: <>Время<br/>дефицита,</>, value: stats.deficitTime, unit: 'ч', icon: TrendingDown, color: 'red' },
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
          className="card relative"
          ref={chartRef}
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-800">
                Суточный профиль баланса мощности
              </h3>
              <p className="text-sm text-gray-500 mt-1 flex items-center gap-2">
                <Edit className="w-4 h-4" />
                Перетаскивайте точки для редактирования данных
              </p>
            </div>
            {hasChanges && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={handleReset}
                className="flex items-center gap-2 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors duration-200 shadow-md"
              >
                <RotateCcw className="w-4 h-4" />
                Отменить изменения
              </motion.button>
            )}
          </div>
          
          {/* Индикатор перетаскивания */}
          {draggingIndex !== null && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute top-4 right-4 px-3 py-1 bg-blue-500 text-white text-sm rounded-full shadow-lg z-10"
            >
              Час {draggingIndex + 1}: {loadProfile[draggingIndex].toFixed(1)} МВт
            </motion.div>
          )}
          
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart 
              data={chartData}
              margin={{ top: 10, right: 30, left: 20, bottom: 20 }}
            >
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
                }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                        <p className="text-gray-600 text-sm">Час: {payload[0].payload.hour}</p>
                        <p className="text-blue-600 font-semibold">
                          Мощность: {payload[0].value.toFixed(1)} МВт
                        </p>
                      </div>
                    );
                  }
                  return null;
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
                dot={renderCustomDot}
                activeDot={false}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
        </div>

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
                Рассчитать график (QP)
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

export default DataVisualizationSection_qp;

