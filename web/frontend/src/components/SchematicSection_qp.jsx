import { motion } from 'framer-motion';
import { Map, Battery, Zap, ArrowRight, Activity } from 'lucide-react';
import { useState } from 'react';

const SchematicSection_qp = ({ calculationResult, parameters }) => {
  const [selectedHour, setSelectedHour] = useState(12);
  const { eess_schedule, resulting_balance, soc } = calculationResult;

  const currentPower = eess_schedule[selectedHour - 1];
  const currentSOC = soc[selectedHour - 1];
  const currentBalance = resulting_balance[selectedHour - 1];
  const socPercent = (currentSOC / parameters.rated_capacity_mwh) * 100;

  const isCharging = currentPower < 0;
  const isDischarging = currentPower > 0;

  return (
    <section id="schematic-qp" className="section-container bg-gradient-to-br from-green-50 to-emerald-50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Схема системы СНЭЭ (QP)</h2>
        <p className="section-subtitle text-center">
          Интерактивная визуализация потоков энергии в режиме реального времени
        </p>

        {/* Выбор часа */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="card mb-8 max-w-4xl mx-auto"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800">Выберите час для визуализации</h3>
            <div className="text-3xl font-bold text-primary-700">Час {selectedHour}</div>
          </div>
          <input
            type="range"
            min="1"
            max="24"
            value={selectedHour}
            onChange={(e) => setSelectedHour(parseInt(e.target.value))}
            className="w-full h-3 bg-gradient-to-r from-primary-200 to-primary-400 rounded-lg appearance-none cursor-pointer slider"
            style={{
              background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${((selectedHour - 1) / 23) * 100}%, #e0e0e0 ${((selectedHour - 1) / 23) * 100}%, #e0e0e0 100%)`,
            }}
          />
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>24:00</span>
          </div>
        </motion.div>

        {/* SVG Схема */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="card max-w-6xl mx-auto"
        >
          <svg
            viewBox="0 0 1000 600"
            className="w-full h-auto"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              {/* Градиенты */}
              <linearGradient id="batteryGradient-qp-schem" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>
              <linearGradient id="inverterGradient-qp-schem" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#2563eb" />
              </linearGradient>
              <linearGradient id="gridGradient-qp-schem" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#d97706" />
              </linearGradient>

              {/* Анимированный маркер для стрелок */}
              <marker
                id="arrowhead-qp-schem"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 10 3, 0 6" fill="#0ea5e9" />
              </marker>

              {/* Фильтр свечения */}
              <filter id="glow-qp-schem">
                <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Фон */}
            <rect width="1000" height="600" fill="#f8fafc" rx="20" />

            {/* Батарея (слева) */}
            <g id="battery-qp">
              <rect
                x="50"
                y="200"
                width="200"
                height="200"
                rx="15"
                fill="url(#batteryGradient-qp-schem)"
                stroke="#059669"
                strokeWidth="4"
              />
              
              {/* Индикатор заряда */}
              <rect
                x="70"
                y={220 + (180 * (100 - socPercent) / 100)}
                width="160"
                height={180 * socPercent / 100}
                rx="8"
                fill="#dcfce7"
                opacity="0.8"
              />
              
              {/* Контакты батареи */}
              <rect x="130" y="170" width="40" height="30" rx="5" fill="#059669" />
              
              <text x="150" y="320" textAnchor="middle" className="text-2xl font-bold" fill="white">
                Батарея
              </text>
              <text x="150" y="350" textAnchor="middle" className="text-lg" fill="white">
                {currentSOC.toFixed(1)} МВтч
              </text>
              <text x="150" y="375" textAnchor="middle" className="text-base" fill="#dcfce7">
                {socPercent.toFixed(1)}%
              </text>
            </g>

            {/* Инвертор (центр) */}
            <g id="inverter-qp">
              <rect
                x="400"
                y="250"
                width="200"
                height="100"
                rx="10"
                fill="url(#inverterGradient-qp-schem)"
                stroke="#2563eb"
                strokeWidth="3"
              />
              
              {/* Символ инвертора */}
              <path
                d="M 450 270 L 450 330 M 470 270 Q 490 300 470 330 M 510 270 L 510 330 M 530 270 Q 550 300 530 330"
                stroke="white"
                strokeWidth="3"
                fill="none"
              />
              
              <text x="500" y="310" textAnchor="middle" className="text-xl font-bold" fill="white">
                Инвертор
              </text>
              <text x="500" y="335" textAnchor="middle" className="text-sm" fill="#dbeafe">
                {parameters.rated_power_mw} МВт
              </text>
            </g>

            {/* Сеть (справа) */}
            <g id="grid-qp">
              <circle
                cx="850"
                cy="300"
                r="100"
                fill="url(#gridGradient-qp-schem)"
                stroke="#d97706"
                strokeWidth="4"
              />
              
              {/* Символ сети */}
              <path
                d="M 850 230 L 850 370 M 800 280 L 900 280 M 800 320 L 900 320"
                stroke="white"
                strokeWidth="4"
                fill="none"
              />
              
              <text x="850" y="310" textAnchor="middle" className="text-2xl font-bold" fill="white">
                Сеть
              </text>
              <text x="850" y="340" textAnchor="middle" className="text-lg" fill="white">
                {currentBalance >= 0 ? '+' : ''}{currentBalance.toFixed(1)} МВт
              </text>
            </g>

            {/* Стрелки потока энергии */}
            {isCharging && (
              <>
                {/* От сети к инвертору */}
                <motion.path
                  d="M 750 300 L 600 300"
                  stroke="#ef4444"
                  strokeWidth="6"
                  fill="none"
                  markerEnd="url(#arrowhead-qp-schem)"
                  filter="url(#glow-qp-schem)"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
                {/* От инвертора к батарее */}
                <motion.path
                  d="M 400 300 L 250 300"
                  stroke="#ef4444"
                  strokeWidth="6"
                  fill="none"
                  markerEnd="url(#arrowhead-qp-schem)"
                  filter="url(#glow-qp-schem)"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.5 }}
                />
                <text x="500" y="240" textAnchor="middle" className="text-lg font-bold" fill="#ef4444">
                  ⚡ Заряд: {Math.abs(currentPower).toFixed(1)} МВт
                </text>
              </>
            )}

            {isDischarging && (
              <>
                {/* От батареи к инвертору */}
                <motion.path
                  d="M 250 300 L 400 300"
                  stroke="#10b981"
                  strokeWidth="6"
                  fill="none"
                  markerEnd="url(#arrowhead-qp-schem)"
                  filter="url(#glow-qp-schem)"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
                {/* От инвертора к сети */}
                <motion.path
                  d="M 600 300 L 750 300"
                  stroke="#10b981"
                  strokeWidth="6"
                  fill="none"
                  markerEnd="url(#arrowhead-qp-schem)"
                  filter="url(#glow-qp-schem)"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.5 }}
                />
                <text x="500" y="240" textAnchor="middle" className="text-lg font-bold" fill="#10b981">
                  ⚡ Разряд: {currentPower.toFixed(1)} МВт
                </text>
              </>
            )}

            {!isCharging && !isDischarging && (
              <text x="500" y="240" textAnchor="middle" className="text-lg font-bold" fill="#6b7280">
                ⏸ Простой
              </text>
            )}

            {/* Информационная панель */}
            <g id="info-qp">
              <rect x="50" y="450" width="900" height="120" rx="10" fill="white" opacity="0.9" stroke="#cbd5e1" strokeWidth="2" />
              
              <text x="500" y="485" textAnchor="middle" className="text-xl font-bold" fill="#1f2937">
                Состояние системы в час {selectedHour}
              </text>
              
              <text x="100" y="520" className="text-base" fill="#374151">
                Режим: <tspan className="font-bold" fill={isCharging ? '#ef4444' : isDischarging ? '#10b981' : '#6b7280'}>
                  {isCharging ? 'ЗАРЯД' : isDischarging ? 'РАЗРЯД' : 'ПРОСТОЙ'}
                </tspan>
              </text>
              
              <text x="100" y="550" className="text-base" fill="#374151">
                Мощность СНЭЭ: <tspan className="font-bold">{Math.abs(currentPower).toFixed(1)} МВт</tspan>
              </text>
              
              <text x="500" y="520" className="text-base" fill="#374151">
                Заряд батареи: <tspan className="font-bold">{currentSOC.toFixed(1)} МВтч ({socPercent.toFixed(1)}%)</tspan>
              </text>
              
              <text x="500" y="550" className="text-base" fill="#374151">
                Баланс сети: <tspan className="font-bold" fill={currentBalance >= 0 ? '#10b981' : '#ef4444'}>
                  {currentBalance >= 0 ? '+' : ''}{currentBalance.toFixed(1)} МВт
                </tspan>
              </text>
            </g>
          </svg>
        </motion.div>

        {/* Легенда */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="card mt-8 max-w-4xl mx-auto"
        >
          <h3 className="text-lg font-bold text-gray-800 mb-4">Обозначения</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 rounded mr-3"></div>
              <span className="text-sm text-gray-700">Поток энергии при разряде</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-red-500 rounded mr-3"></div>
              <span className="text-sm text-gray-700">Поток энергии при заряде</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-gray-400 rounded mr-3"></div>
              <span className="text-sm text-gray-700">Система в простое</span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
};

export default SchematicSection_qp;

