import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Battery, Info, RotateCcw, Zap } from 'lucide-react';
import { apiService } from '../services/api';

const BatteryInteractiveSection_qp = ({ loadProfile, parameters, setParameters, maxAbsValue, setOptimalParams }) => {
  // Расчет максимальных значений
  const maxPower = maxAbsValue || Math.max(...loadProfile.map(v => Math.abs(v))); // Максимум мощности баланса по модулю
  const totalSurplus = loadProfile.filter(v => v > 0).reduce((a, b) => a + b, 0); // Избыток энергии
  const maxDurationHours = loadProfile.filter(v => v < 0).length; // Количество часов в отрицательной зоне
  const minDeficit = Math.abs(Math.min(...loadProfile)) / parameters.dblEfficiency_pq; // Максимальный дефицит с учетом КПД
  
  // Состояние для размеров батареи (выходная)
  const [batteryPower, setBatteryPower] = useState(parameters.dblNOut_pq);
  const [batteryCapacity, setBatteryCapacity] = useState(parameters.dblCapacity_pq);
  
  // Состояние для входной батареи
  const [batteryPowerIn, setBatteryPowerIn] = useState(parameters.dblNIn_pq);
  
  // Локальное состояние для оптимальных параметров (расширенный набор)
  const [optimalParams, setOptimalParamsLocal] = useState({
    power_in: null,
    power_out: null,
    capacity: null,
    deficit: null,
    discharge_time: null,      // вычисляемый
    charge_energy: null,        // вычисляемый
    charge_time: null           // вычисляемый
  });
  const [isLoadingOptimal, setIsLoadingOptimal] = useState(false);
  const [optimalError, setOptimalError] = useState(null);
  
  // Состояние для drag & resize выходной батареи
  const [isDraggingHeight, setIsDraggingHeight] = useState(false);
  const [isDraggingWidth, setIsDraggingWidth] = useState(false);
  const [dragStartY, setDragStartY] = useState(0);
  const [dragStartX, setDragStartX] = useState(0);
  const [dragStartPower, setDragStartPower] = useState(0);
  const [dragStartCapacity, setDragStartCapacity] = useState(0);
  const batteryPowerRef = useRef(parameters.dblNOut_pq);
  const batteryCapacityRef = useRef(parameters.dblCapacity_pq);
  const batteryPowerInRef = useRef(parameters.dblNIn_pq);
  
  // Состояние для drag & resize входной батареи
  const [isDraggingHeightIn, setIsDraggingHeightIn] = useState(false);
  const [dragStartYIn, setDragStartYIn] = useState(0);
  const [dragStartPowerIn, setDragStartPowerIn] = useState(0);
  
  const svgRef = useRef(null);
  
  // Размеры SVG контейнера (фиксированные для адаптивности)
  const viewWidth = 500;
  const viewHeight = 400;
  const padding = 60;
  
  // Масштабирование для отображения
  const scaleX = (viewWidth - padding * 2) / maxDurationHours; // пиксели на час
  const scaleY = (viewHeight - padding * 2) / maxPower; // пиксели на МВт
  
  // Размеры выходной батареи в масштабированных координатах
  const batteryDuration = batteryCapacity / batteryPower;
  const batteryWidth = batteryDuration * scaleX;
  const batteryHeight = batteryPower * scaleY;
  
  // Расчеты для входной батареи
  const batteryChargeEnergy = batteryCapacity / parameters.dblEfficiency_pq; // Энергия на заряд
  const batteryChargeDuration = batteryChargeEnergy / batteryPowerIn; // Время заряда
  const batteryWidthIn = batteryChargeDuration * scaleX;
  const batteryHeightIn = batteryPowerIn * scaleY;
  
  // Максимальные размеры
  const maxWidth = maxDurationHours * scaleX;
  const maxHeight = maxPower * scaleY;
  
  // Синхронизация размеров батареи при изменении параметров извне
  useEffect(() => {
    setBatteryPower(parameters.dblNOut_pq);
    setBatteryCapacity(parameters.dblCapacity_pq);
    batteryPowerRef.current = parameters.dblNOut_pq;
    batteryCapacityRef.current = parameters.dblCapacity_pq;
  }, [parameters.dblNOut_pq, parameters.dblCapacity_pq]);

  // Синхронизация входной мощности при изменении параметров извне
  useEffect(() => {
    setBatteryPowerIn(parameters.dblNIn_pq);
    batteryPowerInRef.current = parameters.dblNIn_pq;
  }, [parameters.dblNIn_pq]);

  // Расчет оптимальных параметров при изменении профиля нагрузки или КПД
  useEffect(() => {
    const calculateOptimal = async () => {
      if (!loadProfile || loadProfile.length !== 24) return;
      
      // Проверяем валидность КПД перед отправкой запроса
      if (!parameters.dblEfficiency_pq || parameters.dblEfficiency_pq <= 0 || parameters.dblEfficiency_pq > 1) {
        return;
      }
      
      setIsLoadingOptimal(true);
      try {
        const result = await apiService.calculateOptimalParameters_qp({
          load_profile: loadProfile,
          efficiency: parameters.dblEfficiency_pq
        });
        
        // Рассчитываем дополнительные параметры на фронтенде
        const discharge_time = result.optimal_capacity_mwh / result.optimal_power_out_mw;
        const charge_energy = result.optimal_capacity_mwh / parameters.dblEfficiency_pq;
        const charge_time = charge_energy / result.optimal_power_in_mw;
        
        const newOptimalParams = {
          power_in: result.optimal_power_in_mw,
          power_out: result.optimal_power_out_mw,
          capacity: result.optimal_capacity_mwh,
          deficit: result.deficit_mw,
          discharge_time: discharge_time,
          charge_energy: charge_energy,
          charge_time: charge_time
        };
        
        setOptimalParamsLocal(newOptimalParams);
        if (setOptimalParams) {
          setOptimalParams(newOptimalParams);
        }
        setOptimalError(null); // Сбрасываем ошибку при успешной оптимизации
      } catch (error) {
        console.error('Ошибка при расчете оптимальных параметров:', error);
        
        // Извлекаем детальное сообщение об ошибке
        const errorMessage = error.response?.data?.detail || error.message || 'Неизвестная ошибка оптимизации';
        setOptimalError(errorMessage);
        
        const emptyParams = {
          power_in: null,
          power_out: null,
          capacity: null,
          deficit: null,
          discharge_time: null,
          charge_energy: null,
          charge_time: null
        };
        setOptimalParamsLocal(emptyParams);
        if (setOptimalParams) {
          setOptimalParams(emptyParams);
        }
      } finally {
        setIsLoadingOptimal(false);
      }
    };
    
    calculateOptimal();
  }, [loadProfile, parameters.dblEfficiency_pq]);
  
  // Обработчики для drag выходной батареи
  const handleMouseMove = (e) => {
    if (isDraggingHeight) {
      const deltaY = dragStartY - e.clientY;
      const deltaPower = (deltaY / scaleY);
      let newPower = dragStartPower + deltaPower;
      newPower = Math.round(newPower / 10) * 10; // Округление до 10 МВт
      newPower = Math.max(10, Math.min(maxPower, newPower));
      
      setBatteryPower(newPower);
      batteryPowerRef.current = newPower;
      
      // Пересчет емкости с сохранением начальной длительности
      const initialDuration = dragStartCapacity / dragStartPower;
      let newCapacity = newPower * initialDuration;
      setBatteryCapacity(newCapacity);
      batteryCapacityRef.current = newCapacity;
    }
    
    if (isDraggingWidth) {
      const deltaX = e.clientX - dragStartX;
      const deltaDuration = deltaX / scaleX;
      let newDuration = (dragStartCapacity / dragStartPower) + deltaDuration;
      newDuration = Math.max(0.5, Math.min(maxDurationHours, newDuration));
      
      let newCapacity = batteryPower * newDuration;
      newCapacity = Math.round(newCapacity / 100) * 100; // Округление до 100 МВтч
      newCapacity = Math.max(100, newCapacity);
      
      setBatteryCapacity(newCapacity);
      batteryCapacityRef.current = newCapacity;
    }
    
    // Обработка перетаскивания входной батареи
    if (isDraggingHeightIn) {
      const deltaY = dragStartYIn - e.clientY;
      const deltaPower = (deltaY / scaleY);
      let newPowerIn = dragStartPowerIn + deltaPower;
      newPowerIn = Math.round(newPowerIn / 10) * 10; // Округление до 10 МВт
      newPowerIn = Math.max(10, Math.min(maxPower, newPowerIn));
      
      setBatteryPowerIn(newPowerIn);
      batteryPowerInRef.current = newPowerIn;
    }
  };
  
  const handleMouseUp = () => {
    const wasDragging = isDraggingHeight || isDraggingWidth || isDraggingHeightIn;
    setIsDraggingHeight(false);
    setIsDraggingWidth(false);
    setIsDraggingHeightIn(false);
    
    if (wasDragging) {
      const finalizedPowerOut = batteryPowerRef.current;
      const finalizedCapacity = batteryCapacityRef.current;
      const finalizedPowerIn = batteryPowerInRef.current;
      const runtimeHours = finalizedPowerOut > 0
        ? Math.round((finalizedCapacity / finalizedPowerOut) * 10) / 10
        : 0;
      
      setParameters(prev => ({
        ...prev,
        dblNOut_pq: finalizedPowerOut,
        dblCapacity_pq: finalizedCapacity,
        dblNIn_pq: finalizedPowerIn,
        runtime_hours: runtimeHours,
      }));
    }
  };
  
  useEffect(() => {
    if (isDraggingHeight || isDraggingWidth || isDraggingHeightIn) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDraggingHeight, isDraggingWidth, isDraggingHeightIn, dragStartY, dragStartX, dragStartPower, dragStartCapacity, dragStartYIn, dragStartPowerIn, scaleY, scaleX, maxPower, maxDurationHours, batteryDuration, batteryCapacity, batteryPower]);
  
  // Функция установки оптимальных параметров
  const resetToRecommended = () => {
    const roundToHundredths = (value) => Math.round(value * 100) / 100;
    if (optimalParams.power_out && optimalParams.capacity) {
      // Используем оптимальные значения без округления для дальнейших расчетов
      const exactPowerIn = optimalParams.power_in;
      const exactPowerOut = optimalParams.power_out;
      const exactCapacity = optimalParams.capacity;
      const exactRuntime = exactCapacity / exactPowerOut;
      
      // Обновляем локальные состояния для интерактивного компонента
      setBatteryPower(exactPowerOut);
      setBatteryCapacity(exactCapacity);
      setBatteryPowerIn(exactPowerIn);
      
      // Обновляем глобальные параметры (для DataInputSection)
      setParameters(prev => ({
        ...prev,
        dblNIn_pq: exactPowerIn,
        dblNOut_pq: exactPowerOut,
        dblCapacity_pq: exactCapacity,
        runtime_hours: exactRuntime
      }));
    } else {
      // Если оптимальные параметры не рассчитаны, используем приблизительные
      const recommendedPower = roundToHundredths(Math.round(maxPower * 0.6 / 10) * 10);
      const recommendedCapacity = roundToHundredths(Math.round(recommendedPower * 4 / 100) * 100);
      const recommendedRuntime = roundToHundredths(recommendedCapacity / recommendedPower);
      
      setBatteryPower(recommendedPower);
      setBatteryCapacity(recommendedCapacity);
      setBatteryPowerIn(recommendedPower);
      
      // Обновляем глобальные параметры
      setParameters(prev => ({
        ...prev,
        dblNIn_pq: recommendedPower,
        dblNOut_pq: recommendedPower,
        dblCapacity_pq: recommendedCapacity,
        runtime_hours: recommendedRuntime
      }));
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      viewport={{ once: true }}
      className="mb-8"
    >
      <div className="card mx-auto">
        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <Battery className="w-6 h-6 mr-2 text-primary-600" />
          Интерактивный выбор параметров СНЭЭ (QP)
        </h3>
        
        <div>
          {/* Инфо панель */}
          <div className="mb-6">
            
          <div className="bg-amber-50 rounded-lg p-3 border-2 border-amber-200 text-sm text-amber-900 mb-1">
              <div className="flex items-start">
                <Zap className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0 text-amber-600" />
                <div>
                  <strong className="block mb-1">Как использовать:</strong>
                  <ul className="list-disc list-inside space-y-0.5 text-xs">
                    <li><span className="font-bold text-blue-600">Левая батарея (синяя)</span> - управление выходной мощностью и емкостью:</li>
                    <ul className="list-circle list-inside ml-4 space-y-0.5">
                      <li>Тяните <span className="font-bold text-green-700">зеленый маркер</span> вверх/вниз для изменения выходной мощности</li>
                      <li>Тяните <span className="font-bold text-blue-700">синий маркер</span> влево/вправо для изменения емкости батареи</li>
                    </ul>
                    <li><span className="font-bold text-red-600">Правая батарея (красная)</span> - управление входной мощностью:</li>
                    <ul className="list-circle list-inside ml-4 space-y-0.5">
                      <li>Тяните <span className="font-bold text-red-700">красный маркер</span> вверх/вниз для изменения входной мощности</li>
                      <li>Ширина батареи изменяется автоматически при изменении емкости выходной батареи</li>
                    </ul>
                    <li><span className="font-bold text-green-700">Зеленый</span> и <span className="font-bold text-red-700">красный</span> пунктиры показывают оптимальные выходную и входную мощности</li>
                  </ul>
                </div>
              </div>
            </div>

            {/*Сетка Интерактивных Параметров */}
            
            <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr_auto] gap-3 mb-4">
            {/* Текущие параметры */}
            <div className="grid grid-cols-1 gap-4 max-w-[250px]">
            <div className="flex items-center text-lg font-semibold text-gray-800">
              <Info className="w-6 h-6 mr-2 text-primary-600" />
              Текущие параметры
            </div>
              <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-3 border-2 border-red-300">
                <div className="text-xs text-gray-600 mb-0.5">Номинальная активная входная мощность (dblNIn)</div>
                <div className="text-2xl font-bold text-red-700">{parameters.dblNIn_pq.toFixed(2)} МВт</div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 border-2 border-green-300">
                <div className="text-xs text-gray-600 mb-0.5">Номинальная активная выходная мощность (dblNOut)</div>
                <div className="text-2xl font-bold text-green-700">{batteryPower.toFixed(2)} МВт</div>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border-2 border-blue-300">
                <div className="text-xs text-gray-600 mb-0.5">Энергия, фактически отдаваемая в рабочем диапазоне (dblCapacity)</div>
                <div className="text-2xl font-bold text-blue-700">{batteryCapacity.toFixed(2)} МВтч</div>
              </div>

              <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3 border-2 border-purple-300">
                <div className="text-xs text-gray-600 mb-0.5">Энергоэффективность (КПД) (dblEfficiency)</div>
                <div className="text-2xl font-bold text-purple-700">{(parameters.dblEfficiency_pq * 100).toFixed(2)}%</div>
              </div>

              <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-3 border-2 border-amber-300">
                    <div className="text-xs text-gray-600 mb-0.5">Время работы на номинальной мощности</div>
                    <div className="text-2xl font-bold text-amber-700">{(batteryCapacity / batteryPower).toFixed(1)} ч</div>
              </div>
              
              <button
              onClick={resetToRecommended}
              disabled={isLoadingOptimal}
              className={`w-full btn-secondary text-sm flex items-center justify-center ${isLoadingOptimal ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={optimalParams.power_out && optimalParams.capacity ? `Установить: Вход ${optimalParams.power_in.toFixed(2)} МВт, Выход ${optimalParams.power_out.toFixed(2)} МВт, Емкость ${optimalParams.capacity.toFixed(2)} МВтч` : 'Установить оптимальные параметры'}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              {isLoadingOptimal ? 'Расчет...' : 'Установить оценочные параметры'}
              </button>
            </div>

          
          {/* Контейнер для двух SVG батарей */}
          <div className="w-full flex flex-col lg:flex-row gap-6 items-stretch">
            
            {/* SVG батарея изменения параметров выходной мощности и энергии */}
            <div className="flex-1 flex items-center justify-center">
              <svg
                ref={svgRef}
                viewBox={`0 0 ${viewWidth} ${viewHeight}`}
                className="border-2 border-blue-300 rounded-xl bg-white shadow-lg"
                style={{ 
                  width: '100%', 
                  maxWidth: '100%',
                  height: 'auto',
                  cursor: (isDraggingHeight || isDraggingWidth) ? 'grabbing' : 'default',
                  userSelect: 'none'
                }}
              >
                {/* Фон с сеткой */}
                <defs>
                  <pattern id="grid-qp" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" strokeWidth="0.5"/>
                  </pattern>
                  <linearGradient id="batteryGradient-qp" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
                    <stop offset="50%" stopColor="#2563eb" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#1d4ed8" stopOpacity="1" />
                  </linearGradient>
                  <filter id="shadow-qp">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                
                <rect width={viewWidth} height={viewHeight} fill="url(#grid-qp)" />
                
                {/* Максимальная область (пунктир) */}
                <rect
                  x={padding}
                  y={viewHeight - padding - maxHeight}
                  width={maxWidth}
                  height={maxHeight}
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="2"
                  strokeDasharray="8,4"
                  opacity="0.6"
                />
                
                {/* Оптимальные параметры (пунктирные линии) */}
                {optimalParams.power_out && optimalParams.capacity && (
                  <>
                    {/* Оптимальная мощность - горизонтальная линия (выходная мощность) */}
                    {(() => {
                      const optimalPowerOut = optimalParams.power_out;
                      return (
                        <>
                          <line
                            x1={padding}
                            y1={viewHeight - padding - optimalPowerOut * scaleY}
                            x2={padding + maxWidth}
                            y2={viewHeight - padding - optimalPowerOut * scaleY}
                            stroke="#10b981"
                            strokeWidth="2"
                            strokeDasharray="6,3"
                            opacity="0.7"
                          />
                          <text
                            x={padding + maxWidth + 5}
                            y={viewHeight - padding - optimalPowerOut * scaleY}
                            fill="#10b981"
                            fontSize="10"
                            fontWeight="bold"
                          >
                            {optimalPowerOut.toFixed(0)} МВт
                          </text>
                        </>
                      );
                    })()}
                    
                    {/* Оптимальная длительность - вертикальная линия */}
                    {(() => {
                      const optimalPowerOut = optimalParams.power_out;
                      const optimalDuration = optimalParams.capacity / optimalPowerOut;
                      const optimalDurationX = padding + optimalDuration * scaleX;
                      return optimalDurationX <= padding + maxWidth ? (
                        <>
                          <line
                            x1={optimalDurationX}
                            y1={viewHeight - padding}
                            x2={optimalDurationX}
                            y2={viewHeight - padding - maxHeight}
                            stroke="#3b82f6"
                            strokeWidth="2"
                            strokeDasharray="6,3"
                            opacity="0.7"
                          />
                          <text
                            x={optimalDurationX}
                            y={viewHeight - padding - maxHeight-10}
                            fill="#3b82f6"
                            fontSize="10"
                            fontWeight="bold"
                            textAnchor="middle"
                          >
                            {optimalDuration.toFixed(1)} ч
                          </text>
                        </>
                      ) : null;
                    })()}
                  </>
                )}
                
                {/* Подписи максимумов */}
                <text
                  x={padding + maxWidth + 5}
                  y={viewHeight - padding - maxHeight}
                  fill="#64748b"
                  fontSize="11"
                  fontWeight="bold"
                >
                  {maxPower.toFixed(0)} МВт
                </text>
                <text
                  x={padding + maxWidth}
                  y={viewHeight - padding + 20}
                  fill="#64748b"
                  fontSize="11"
                  fontWeight="bold"
                  textAnchor="end"
                >
                  {maxDurationHours.toFixed(1)} ч
                </text>
                
                {/* Батарея */}
                <g>
                  {/* Тело батареи */}
                  <rect
                    x={padding}
                    y={viewHeight - padding - batteryHeight}
                    width={batteryWidth}
                    height={batteryHeight}
                    fill="url(#batteryGradient-qp)"
                    stroke="#1e40af"
                    strokeWidth="3"
                    rx="6"
                    filter="url(#shadow-qp)"
                  />
                  
                  {/* Иконка батареи */}
                  <g transform={`translate(${padding + batteryWidth / 2 - 15}, ${viewHeight - padding - batteryHeight / 2 - 20})`}>
                    <rect x="5" y="0" width="20" height="30" rx="2" fill="white" opacity="0.95" stroke="#1e40af" strokeWidth="1.5"/>
                    <rect x="10" y="-4" width="10" height="4" rx="1" fill="white" opacity="0.95" stroke="#1e40af" strokeWidth="1.5"/>
                    <rect x="8" y="18" width="14" height="8" fill="#10b981" opacity="0.9" rx="1"/>
                  </g>
                  
                  {/* Емкость в центре батареи */}
                  <text
                    x={padding + batteryWidth / 2}
                    y={viewHeight - padding - batteryHeight / 2 + 25}
                    textAnchor="middle"
                    fill="white"
                    fontSize="16"
                    fontWeight="bold"
                    stroke="#1e40af"
                    strokeWidth="0.5"
                  >
                    {batteryCapacity.toFixed(0)} МВтч
                  </text>
                  
                  {/* Значения на батарее */}
                  <text
                    x={padding + batteryWidth / 2}
                    y={viewHeight - padding - batteryHeight - 10}
                    textAnchor="middle"
                    fill="#1e40af"
                    fontSize="13"
                    fontWeight="bold"
                  >
                    {batteryPower.toFixed(0)} МВт
                  </text>
                  
                  <text
                    x={padding + batteryWidth / 2}
                    y={viewHeight - padding + 20}
                    textAnchor="middle"
                    fill="#1e40af"
                    fontSize="13"
                    fontWeight="bold"
                  >
                    {batteryDuration.toFixed(1)} ч
                  </text>
                  
                  {/* Маркер изменения высоты (зеленый, справа) */}
                  <g
                    transform={`translate(${padding + batteryWidth + 20}, ${viewHeight - padding - batteryHeight / 2})`}
                    onMouseDown={(e) => {
                      setIsDraggingHeight(true);
                      setDragStartY(e.clientY);
                      setDragStartPower(batteryPower);
                      setDragStartCapacity(batteryCapacity);
                    }}
                    style={{ cursor: 'ns-resize' }}
                    opacity={isDraggingHeight ? 1 : 0.85}
                  >
                    <circle cx="0" cy="0" r="16" fill="#10b981" stroke="#065f46" strokeWidth="2.5" filter="url(#shadow-qp)"/>
                    <line x1="0" y1="-8" x2="0" y2="8" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <polygon points="-5,-8 0,-12 5,-8" fill="white"/>
                    <polygon points="-5,8 0,12 5,8" fill="white"/>
                  </g>
                  
                  {/* Маркер изменения ширины (синий, снизу) */}
                  <g
                    transform={`translate(${padding + batteryWidth}, ${viewHeight - padding + 20})`}
                    onMouseDown={(e) => {
                      setIsDraggingWidth(true);
                      setDragStartX(e.clientX);
                      setDragStartCapacity(batteryCapacity);
                      setDragStartPower(batteryPower);
                    }}
                    style={{ cursor: 'ew-resize' }}
                    opacity={isDraggingWidth ? 1 : 0.85}
                  >
                    <circle cx="0" cy="0" r="16" fill="#3b82f6" stroke="#1e40af" strokeWidth="2.5" filter="url(#shadow-qp)"/>
                    <line x1="-8" y1="0" x2="8" y2="0" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <polygon points="-8,-5 -12,0 -8,5" fill="white"/>
                    <polygon points="8,-5 12,0 8,5" fill="white"/>
                  </g>
                </g>
                
                {/* Оси */}
                <line x1={padding} y1={viewHeight - padding} x2={padding + maxWidth + 10} y2={viewHeight - padding} 
                      stroke="#475569" strokeWidth="2" markerEnd="url(#arrowX-qp)"/>
                <line x1={padding} y1={viewHeight - padding} x2={padding} y2={viewHeight - padding - maxHeight - 10} 
                      stroke="#475569" strokeWidth="2" markerEnd="url(#arrowY-qp)"/>
                
                <defs>
                  <marker id="arrowX-qp" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                    <polygon points="0,0 10,5 0,10" fill="#475569"/>
                  </marker>
                  <marker id="arrowY-qp" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                    <polygon points="0,0 10,5 0,10" fill="#475569"/>
                  </marker>
                </defs>
                
                {/* Подписи осей */}
                <text x={padding + maxWidth / 2} y={viewHeight - 10} textAnchor="middle" fill="#475569" fontSize="12" fontWeight="bold">
                  Длительность (часы)
                </text>
                <text 
                  x={15} 
                  y={viewHeight - padding - maxHeight / 2} 
                  textAnchor="middle" 
                  fill="#475569" 
                  fontSize="12"
                  fontWeight="bold"
                  transform={`rotate(-90, 15, ${viewHeight - padding - maxHeight / 2})`}
                >
                  Мощность (МВт)
                </text>
              </svg>
            </div>

            {/* SVG батарея изменения параметров входной мощности и энергии */}
            <div className="flex-1 flex items-center justify-center">
              <svg
                viewBox={`0 0 ${viewWidth} ${viewHeight}`}
                className="border-2 border-red-300 rounded-xl bg-white shadow-lg"
                style={{ 
                  width: '100%', 
                  maxWidth: '100%',
                  height: 'auto',
                  cursor: isDraggingHeightIn ? 'grabbing' : 'default',
                  userSelect: 'none'
                }}
              >
                {/* Фон с сеткой */}
                <defs>
                  <pattern id="grid-in" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" strokeWidth="0.5"/>
                  </pattern>
                  <linearGradient id="batteryGradient-in" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity="0.3" />
                    <stop offset="50%" stopColor="#dc2626" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#b91c1c" stopOpacity="0.3" />
                  </linearGradient>
                  <filter id="shadow-in">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                
                <rect width={viewWidth} height={viewHeight} fill="url(#grid-in)" />
                
                {/* Максимальная область (пунктир) */}
                <rect
                  x={padding}
                  y={viewHeight - padding - maxHeight}
                  width={maxWidth}
                  height={maxHeight}
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="2"
                  strokeDasharray="8,4"
                  opacity="0.6"
                />
                
                {/* Оптимальная входная мощность (красный пунктир) */}
                {optimalParams.power_in && (
                  <>
                    <line
                      x1={padding}
                      y1={viewHeight - padding - optimalParams.power_in * scaleY}
                      x2={padding + maxWidth}
                      y2={viewHeight - padding - optimalParams.power_in * scaleY}
                      stroke="#ef4444"
                      strokeWidth="2"
                      strokeDasharray="6,3"
                      opacity="0.7"
                    />
                    <text
                      x={padding + maxWidth + 5}
                      y={viewHeight - padding - optimalParams.power_in * scaleY}
                      fill="#ef4444"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      {optimalParams.power_in.toFixed(0)} МВт
                    </text>
                  </>
                )}
                
                {/* Подписи максимумов */}
                <text
                  x={padding + maxWidth + 5}
                  y={viewHeight - padding - maxHeight}
                  fill="#64748b"
                  fontSize="11"
                  fontWeight="bold"
                >
                  {maxPower.toFixed(0)} МВт
                </text>
                <text
                  x={padding + maxWidth}
                  y={viewHeight - padding + 20}
                  fill="#64748b"
                  fontSize="11"
                  fontWeight="bold"
                  textAnchor="end"
                >
                  {maxDurationHours.toFixed(1)} ч
                </text>
                
                {/* Батарея входная */}
                <g>
                  {/* Тело батареи */}
                  <rect
                    x={padding}
                    y={viewHeight - padding - batteryHeightIn}
                    width={batteryWidthIn}
                    height={batteryHeightIn}
                    fill="url(#batteryGradient-in)"
                    stroke="#991b1b"
                    strokeWidth="3"
                    rx="6"
                    filter="url(#shadow-in)"
                  />
                  
                  {/* Иконка батареи */}
                  <g transform={`translate(${padding + batteryWidthIn / 2 - 15}, ${viewHeight - padding - batteryHeightIn / 2 - 20})`}>
                    <rect x="5" y="0" width="20" height="30" rx="2" fill="white" opacity="0.95" stroke="#991b1b" strokeWidth="1.5"/>
                    <rect x="10" y="-4" width="10" height="4" rx="1" fill="white" opacity="0.95" stroke="#991b1b" strokeWidth="1.5"/>
                    <rect x="8" y="18" width="14" height="8" fill="#ef4444" opacity="0.9" rx="1"/>
                  </g>
                  
                  {/* Энергия на заряд в центре батареи */}
                  <text
                    x={padding + batteryWidthIn / 2}
                    y={viewHeight - padding - batteryHeightIn / 2 + 25}
                    textAnchor="middle"
                    fill="#991b1b"
                    fontSize="16"
                    fontWeight="bold"
                    stroke="white"
                    strokeWidth="0.5"
                  >
                    {batteryChargeEnergy.toFixed(0)} МВтч
                  </text>
                  
                  {/* Значения на батарее */}
                  <text
                    x={padding + batteryWidthIn / 2}
                    y={viewHeight - padding - batteryHeightIn - 10}
                    textAnchor="middle"
                    fill="#991b1b"
                    fontSize="13"
                    fontWeight="bold"
                  >
                    {batteryPowerIn.toFixed(0)} МВт
                  </text>
                  
                  <text
                    x={padding + batteryWidthIn / 2}
                    y={viewHeight - padding + 20}
                    textAnchor="middle"
                    fill="#991b1b"
                    fontSize="13"
                    fontWeight="bold"
                  >
                    {batteryChargeDuration.toFixed(1)} ч
                  </text>
                  
                  {/* Маркер изменения высоты (красный, справа) - только вертикальное изменение */}
                  <g
                    transform={`translate(${padding + batteryWidthIn + 20}, ${viewHeight - padding - batteryHeightIn / 2})`}
                    onMouseDown={(e) => {
                      setIsDraggingHeightIn(true);
                      setDragStartYIn(e.clientY);
                      setDragStartPowerIn(batteryPowerIn);
                    }}
                    style={{ cursor: 'ns-resize' }}
                    opacity={isDraggingHeightIn ? 1 : 0.85}
                  >
                    <circle cx="0" cy="0" r="16" fill="#ef4444" stroke="#991b1b" strokeWidth="2.5" filter="url(#shadow-in)"/>
                    <line x1="0" y1="-8" x2="0" y2="8" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <polygon points="-5,-8 0,-12 5,-8" fill="white"/>
                    <polygon points="-5,8 0,12 5,8" fill="white"/>
                  </g>
                </g>
                
                {/* Оси */}
                <line x1={padding} y1={viewHeight - padding} x2={padding + maxWidth + 10} y2={viewHeight - padding} 
                      stroke="#475569" strokeWidth="2" markerEnd="url(#arrowX-in)"/>
                <line x1={padding} y1={viewHeight - padding} x2={padding} y2={viewHeight - padding - maxHeight - 10} 
                      stroke="#475569" strokeWidth="2" markerEnd="url(#arrowY-in)"/>
                
                <defs>
                  <marker id="arrowX-in" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                    <polygon points="0,0 10,5 0,10" fill="#475569"/>
                  </marker>
                  <marker id="arrowY-in" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                    <polygon points="0,0 10,5 0,10" fill="#475569"/>
                  </marker>
                </defs>
                
                {/* Подписи осей */}
                <text x={padding + maxWidth / 2} y={viewHeight - 10} textAnchor="middle" fill="#475569" fontSize="12" fontWeight="bold">
                  Время заряда (часы)
                </text>
                <text 
                  x={15} 
                  y={viewHeight - padding - maxHeight / 2} 
                  textAnchor="middle" 
                  fill="#475569" 
                  fontSize="12"
                  fontWeight="bold"
                  transform={`rotate(-90, 15, ${viewHeight - padding - maxHeight / 2})`}
                >
                  Входная мощность (МВт)
                </text>
              </svg>
            </div>
            
          </div>

          {/* Оценочные параметры */}
          <div className="grid grid-cols-1 gap-4 max-w-[240px]">
          <div className="flex items-center text-lg font-semibold text-gray-800">
              <Info className="w-6 h-6 mr-2 text-primary-600" />
              Оценочные параметры
            </div>
              
              {isLoadingOptimal ? (
                <div className="bg-gray-50 rounded-lg p-4 border-2 border-gray-300 text-center">
                  <div className="text-sm text-gray-600">Расчет оптимальных параметров...</div>
                </div>
              ) : optimalParams.power_out && optimalParams.capacity ? (
                <>
                  <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-3 border-2 border-red-300">
                    <div className="text-xs text-gray-600 mb-0.5">Входная мощность2</div>
                  <div className="text-2xl font-bold text-red-700">{optimalParams.power_in.toFixed(5)} МВт</div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 border-2 border-green-300">
                    <div className="text-xs text-gray-600 mb-0.5">Выходная мощность</div>
                  <div className="text-2xl font-bold text-green-700">{optimalParams.power_out.toFixed(2)} МВт</div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border-2 border-blue-300">
                    <div className="text-xs text-gray-600 mb-0.5">Емкость батареи</div>
                  <div className="text-2xl font-bold text-blue-700">{optimalParams.capacity.toFixed(2)} МВтч</div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-3 border-2 border-orange-200">
                    <div className="text-xs text-gray-600 mb-0.5">Дефицит мощности</div>
                  <div className="text-2xl font-bold text-orange-700">{optimalParams.deficit.toFixed(2)} МВтч</div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-3 border-2 border-amber-300">
                    <div className="text-xs text-gray-600 mb-0.5">Время работы</div>
                  <div className="text-2xl font-bold text-amber-700">{(optimalParams.capacity / optimalParams.power_out).toFixed(2)} ч</div>
                  </div>
                </>
              ) : (
                <div className="bg-red-50 rounded-lg p-4 border-2 border-red-300">
                  <div className="text-sm font-semibold text-red-700 mb-2">Оптимальные параметры недоступны</div>
                  {optimalError && (
                    <div className="text-xs text-red-600 bg-white rounded p-2 border border-red-200">
                      <div className="font-medium mb-1">Причина:</div>
                      <div className="whitespace-pre-wrap">{optimalError}</div>
                    </div>
                  )}
                </div>
              )}
            </div>

          </div>
            
          </div>

        </div>
      </div>
    </motion.div>
  );
};

export default BatteryInteractiveSection_qp;

