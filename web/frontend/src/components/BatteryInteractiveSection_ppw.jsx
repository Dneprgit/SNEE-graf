import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Battery, RotateCcw, Zap, Info } from 'lucide-react';
import { apiService } from '../services/api';

const BatteryInteractiveSection_ppw = ({ loadProfile, parameters, setParameters }) => {
  const [optimalParams, setOptimalParams] = useState(null);
  const [isLoadingOptimal, setIsLoadingOptimal] = useState(false);
  const [error, setError] = useState(null);

  // Автоматический расчет оптимальных параметров при изменении профиля или КПД
  useEffect(() => {
    if (loadProfile && loadProfile.length === 24 && parameters.efficiency > 0) {
      calculateOptimalParameters();
    }
  }, [loadProfile, parameters.efficiency]);

  const calculateOptimalParameters = async () => {
    if (!loadProfile || loadProfile.length !== 24) {
      setError('Необходимо загрузить профиль баланса');
      return;
    }

    setIsLoadingOptimal(true);
    setError(null);

    try {
      const result = await apiService.calculatePPWOptimalParameters({
        system_load: loadProfile,
        efficiency: parameters.efficiency,
      });

      setOptimalParams({
        rated_power_in_mw: result.rated_power_in_mw,
        rated_power_out_mw: result.rated_power_out_mw,
        capacity_mwh: result.capacity_mwh,
        actual_discharge_time_h: result.capacity_mwh / result.rated_power_out_mw,
        charge_energy_mwh: result.capacity_mwh / parameters.efficiency,
        actual_charge_time_h: (result.capacity_mwh / parameters.efficiency) / result.rated_power_in_mw,
      });
    } catch (err) {
      console.error('Error calculating optimal parameters:', err);
      setError(err.response?.data?.detail || 'Ошибка при расчете оптимальных параметров');
    } finally {
      setIsLoadingOptimal(false);
    }
  };

  const applyOptimalParameters = () => {
    if (!optimalParams) return;

    setParameters(prev => ({
      ...prev,
      rated_power_in_mw: optimalParams.rated_power_in_mw,
      rated_power_out_mw: optimalParams.rated_power_out_mw,
      rated_capacity_mwh: optimalParams.capacity_mwh,
      capacity_utilization_percent: 90, // Сохраняем текущий
      working_range_energy_mwh: optimalParams.capacity_mwh * 0.9,
      nominal_discharge_time_h: optimalParams.capacity_mwh / optimalParams.rated_power_out_mw,
      actual_discharge_time_h: optimalParams.actual_discharge_time_h,
      charge_energy_mwh: optimalParams.charge_energy_mwh,
      actual_charge_time_h: optimalParams.actual_charge_time_h,
    }));
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-gradient-to-br from-blue-50 to-purple-50 py-12"
    >
      <div className="section-container">
        <h2 className="text-3xl font-bold mb-8 text-center">Интерактивный выбор параметров СНЭЭ</h2>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Левая колонка: Параметры */}
          <div className="space-y-6">
            {/* Текущие параметры */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Battery className="w-6 h-6 text-blue-600" />
                Текущие параметры
              </h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="text-gray-600 mb-1">Вход. мощность</div>
                  <div className="font-bold text-lg">{parameters.rated_power_in_mw} МВт</div>
                </div>
                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-gray-600 mb-1">Вых. мощность</div>
                  <div className="font-bold text-lg">{parameters.rated_power_out_mw} МВт</div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-gray-600 mb-1">Ном. энергоемкость</div>
                  <div className="font-bold">{parameters.rated_capacity_mwh} МВтч</div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-gray-600 mb-1">Коэф. использ. емкости</div>
                  <div className="font-bold">{parameters.capacity_utilization_percent}%</div>
                </div>
                <div className="p-3 bg-green-100 rounded-lg border border-green-300">
                  <div className="text-gray-600 mb-1">Энергия раб. диапазона</div>
                  <div className="font-bold">{parameters.working_range_energy_mwh.toFixed(1)} МВтч</div>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <div className="text-gray-600 mb-1">Факт. время разряда</div>
                  <div className="font-bold">{parameters.actual_discharge_time_h.toFixed(2)} ч</div>
                </div>
                <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="text-gray-600 mb-1">КПД</div>
                  <div className="font-bold">{(parameters.efficiency * 100).toFixed(0)}%</div>
                </div>
                <div className="p-3 bg-red-100 rounded-lg">
                  <div className="text-gray-600 mb-1">Энергия на заряд</div>
                  <div className="font-bold">{parameters.charge_energy_mwh.toFixed(1)} МВтч</div>
                </div>
              </div>
            </div>

            {/* Оценочные параметры */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <Zap className="w-6 h-6 text-purple-600" />
                  Оценочные параметры
                </h3>
                <button
                  onClick={calculateOptimalParameters}
                  disabled={isLoadingOptimal}
                  className="btn-secondary text-sm flex items-center gap-2"
                  title="Пересчитать оценочные параметры"
                >
                  <RotateCcw className={`w-4 h-4 ${isLoadingOptimal ? 'animate-spin' : ''}`} />
                  {isLoadingOptimal ? 'Расчет...' : 'Пересчитать'}
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  {error}
                </div>
              )}

              {optimalParams ? (
                <>
                  <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                    <div className="p-3 bg-red-100 rounded-lg border-2 border-red-300">
                      <div className="text-gray-600 mb-1 flex items-center gap-1">
                        Вход. мощность
                        <Info className="w-3 h-3" title="Оптимальная номинальная активная входная мощность" />
                      </div>
                      <div className="font-bold text-lg text-red-700">{optimalParams.rated_power_in_mw} МВт</div>
                    </div>
                    <div className="p-3 bg-green-100 rounded-lg border-2 border-green-300">
                      <div className="text-gray-600 mb-1 flex items-center gap-1">
                        Вых. мощность
                        <Info className="w-3 h-3" title="Оптимальная номинальная активная выходная мощность" />
                      </div>
                      <div className="font-bold text-lg text-green-700">{optimalParams.rated_power_out_mw} МВт</div>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border-2 border-green-200">
                      <div className="text-gray-600 mb-1">Энергия раб. диапазона</div>
                      <div className="font-bold text-green-600">{optimalParams.capacity_mwh.toFixed(1)} МВтч</div>
                    </div>
                    <div className="p-3 bg-purple-100 rounded-lg border border-purple-200">
                      <div className="text-gray-600 mb-1">Факт. время разряда</div>
                      <div className="font-bold text-purple-700">{optimalParams.actual_discharge_time_h.toFixed(2)} ч</div>
                    </div>
                    <div className="p-3 bg-yellow-100 rounded-lg border border-yellow-200">
                      <div className="text-gray-600 mb-1">КПД</div>
                      <div className="font-bold text-yellow-700">{(parameters.efficiency * 100).toFixed(0)}%</div>
                    </div>
                    <div className="p-3 bg-red-50 rounded-lg">
                      <div className="text-gray-600 mb-1">Энергия на заряд</div>
                      <div className="font-bold">{optimalParams.charge_energy_mwh.toFixed(1)} МВтч</div>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-lg col-span-2">
                      <div className="text-gray-600 mb-1">Факт. время заряда</div>
                      <div className="font-bold">{optimalParams.actual_charge_time_h.toFixed(2)} ч</div>
                    </div>
                  </div>

                  <button
                    onClick={applyOptimalParameters}
                    className="btn-primary w-full"
                  >
                    Установить оценочные параметры
                  </button>
                </>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {isLoadingOptimal ? (
                    <div className="flex items-center justify-center gap-2">
                      <RotateCcw className="w-5 h-5 animate-spin" />
                      <span>Расчет оценочных параметров...</span>
                    </div>
                  ) : (
                    <div>
                      <Info className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                      <p>Загрузите профиль для расчета оценочных параметров</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Правая колонка: Визуализация батареи */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 text-center">Визуализация параметров</h3>
            
            <div className="relative h-96 flex items-center justify-center">
              <svg width="400" height="350" viewBox="0 0 400 350" className="mx-auto">
                {/* Сетка для времени и мощности */}
                <g opacity="0.2">
                  {[0, 1, 2, 3, 4, 5].map(i => (
                    <line key={`h-${i}`} x1="50" y1={50 + i * 40} x2="350" y2={50 + i * 40} stroke="#ccc" strokeDasharray="2,2" />
                  ))}
                  {[0, 1, 2, 3, 4, 5, 6].map(i => (
                    <line key={`v-${i}`} x1={50 + i * 50} y1="50" x2={50 + i * 50} y2="250" stroke="#ccc" strokeDasharray="2,2" />
                  ))}
                </g>

                {/* Оси */}
                <line x1="50" y1="250" x2="350" y2="250" stroke="#333" strokeWidth="2" />
                <line x1="50" y1="50" x2="50" y2="250" stroke="#333" strokeWidth="2" />
                
                {/* Подписи осей */}
                <text x="200" y="285" textAnchor="middle" fontSize="12" fill="#666">Время, ч</text>
                <text x="20" y="150" textAnchor="middle" fontSize="12" fill="#666" transform="rotate(-90, 20, 150)">Мощность, МВт</text>

                {/* Пунктирные линии оценочных параметров (если есть) */}
                {optimalParams && (
                  <>
                    {/* Красная линия - входная мощность */}
                    <line 
                      x1="50" 
                      y1={250 - (optimalParams.rated_power_in_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams.rated_power_in_mw, optimalParams.rated_power_out_mw) * 180)} 
                      x2="350" 
                      y2={250 - (optimalParams.rated_power_in_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams.rated_power_in_mw, optimalParams.rated_power_out_mw) * 180)} 
                      stroke="#EF4444" 
                      strokeWidth="1" 
                      strokeDasharray="5,5" 
                    />
                    
                    {/* Зеленая линия - выходная мощность */}
                    <line 
                      x1="50" 
                      y1={250 - (optimalParams.rated_power_out_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams.rated_power_in_mw, optimalParams.rated_power_out_mw) * 180)} 
                      x2="350" 
                      y2={250 - (optimalParams.rated_power_out_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams.rated_power_in_mw, optimalParams.rated_power_out_mw) * 180)} 
                      stroke="#10B981" 
                      strokeWidth="1" 
                      strokeDasharray="5,5" 
                    />
                    
                    {/* Фиолетовая линия - время разряда */}
                    <line 
                      x1={50 + (optimalParams.actual_discharge_time_h / 6 * 300)} 
                      y1="50" 
                      x2={50 + (optimalParams.actual_discharge_time_h / 6 * 300)} 
                      y2="250" 
                      stroke="#8B5CF6" 
                      strokeWidth="1" 
                      strokeDasharray="5,5" 
                    />
                  </>
                )}

                {/* Прямоугольник разряда (зеленый полупрозрачный) */}
                <rect 
                  x="50" 
                  y={250 - (parameters.rated_power_out_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams?.rated_power_in_mw || 0, optimalParams?.rated_power_out_mw || 0) * 180)} 
                  width={parameters.actual_discharge_time_h / 6 * 300} 
                  height={parameters.rated_power_out_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams?.rated_power_in_mw || 0, optimalParams?.rated_power_out_mw || 0) * 180} 
                  fill="#10B981" 
                  opacity="0.3" 
                  stroke="#10B981" 
                  strokeWidth="2"
                />
                
                {/* Прямоугольник заряда (красный полупрозрачный) */}
                <rect 
                  x="50" 
                  y={250 - (parameters.rated_power_in_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams?.rated_power_in_mw || 0, optimalParams?.rated_power_out_mw || 0) * 180)} 
                  width={parameters.actual_charge_time_h / 6 * 300} 
                  height={parameters.rated_power_in_mw / Math.max(parameters.rated_power_in_mw, parameters.rated_power_out_mw, optimalParams?.rated_power_in_mw || 0, optimalParams?.rated_power_out_mw || 0) * 180} 
                  fill="#EF4444" 
                  opacity="0.3" 
                  stroke="#EF4444" 
                  strokeWidth="2"
                />

                {/* Подписи значений */}
                <text x="200" y="310" textAnchor="middle" fontSize="11" fill="#10B981">
                  Разряд: {parameters.working_range_energy_mwh.toFixed(1)} МВтч
                </text>
                <text x="200" y="325" textAnchor="middle" fontSize="11" fill="#EF4444">
                  Заряд: {parameters.charge_energy_mwh.toFixed(1)} МВтч
                </text>
              </svg>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 opacity-30 border border-green-500"></div>
                <span>Разряд (текущий)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 opacity-30 border border-red-500"></div>
                <span>Заряд (текущий)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-12 h-0.5 border-t-2 border-green-500 border-dashed"></div>
                <span>Вых. мощность (оценка)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-12 h-0.5 border-t-2 border-red-500 border-dashed"></div>
                <span>Вх. мощность (оценка)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.section>
  );
};

export default BatteryInteractiveSection_ppw;

