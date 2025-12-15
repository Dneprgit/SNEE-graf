import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Battery, Info, RotateCcw, Zap } from 'lucide-react';
import { apiService } from '../services/api';

const BatteryInteractiveSection = ({ loadProfile, parameters, setParameters, maxAbsValue }) => {
  // Расчет максимальных значений
  const maxPower = maxAbsValue || Math.max(...loadProfile.map(v => Math.abs(v))); // Максимум мощности баланса по модулю
  const totalSurplus = loadProfile.filter(v => v > 0).reduce((a, b) => a + b, 0); // Избыток энергии
  const maxDurationHours = loadProfile.filter(v => v < 0).length; // Количество часов в отрицательной зоне
  const minDeficit = Math.abs(Math.min(...loadProfile)) / parameters.efficiency; // Максимальный дефицит с учетом КПД
  
  // Состояние для размеров батареи
  const [batteryPower, setBatteryPower] = useState(parameters.rated_power_mw);
  const [batteryCapacity, setBatteryCapacity] = useState(parameters.rated_capacity_mwh);
  
  // Состояние для оптимальных параметров
  const [optimalPower, setOptimalPower] = useState(null);
  const [optimalCapacity, setOptimalCapacity] = useState(null);
  const [isLoadingOptimal, setIsLoadingOptimal] = useState(false);
  
  // Состояние для drag & resize
  const [isDraggingHeight, setIsDraggingHeight] = useState(false);
  const [isDraggingWidth, setIsDraggingWidth] = useState(false);
  const [dragStartY, setDragStartY] = useState(0);
  const [dragStartX, setDragStartX] = useState(0);
  const [dragStartPower, setDragStartPower] = useState(0);
  const [dragStartCapacity, setDragStartCapacity] = useState(0);
  
  const svgRef = useRef(null);
  
  // Размеры SVG контейнера (фиксированные для адаптивности)
  const viewWidth = 500;
  const viewHeight = 400;
  const padding = 60;
  
  // Масштабирование для отображения
  const scaleX = (viewWidth - padding * 2) / maxDurationHours; // пиксели на час
  const scaleY = (viewHeight - padding * 2) / maxPower; // пиксели на МВт
  
  // Размеры батареи в масштабированных координатах
  const batteryDuration = batteryCapacity / batteryPower;
  const batteryWidth = batteryDuration * scaleX;
  const batteryHeight = batteryPower * scaleY;
  
  // Максимальные размеры
  const maxWidth = maxDurationHours * scaleX;
  const maxHeight = maxPower * scaleY;
  
  // Обновление параметров при изменении
  useEffect(() => {
    if (batteryPower !== parameters.rated_power_mw || batteryCapacity !== parameters.rated_capacity_mwh) {
      const timer = setTimeout(() => {
        setParameters(prev => ({
          ...prev,
          rated_power_mw: batteryPower,
          rated_capacity_mwh: batteryCapacity,
        }));
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [batteryPower, batteryCapacity, parameters.rated_power_mw, parameters.rated_capacity_mwh, setParameters]);
  
  // Синхронизация размеров батареи при изменении параметров извне
  useEffect(() => {
    setBatteryPower(parameters.rated_power_mw);
    setBatteryCapacity(parameters.rated_capacity_mwh);
  }, [parameters.rated_power_mw, parameters.rated_capacity_mwh]);

  // Расчет оптимальных параметров при изменении профиля нагрузки или КПД
  useEffect(() => {
    const calculateOptimal = async () => {
      if (!loadProfile || loadProfile.length !== 24) return;
      
      // Проверяем валидность КПД перед отправкой запроса
      if (!parameters.efficiency || parameters.efficiency <= 0 || parameters.efficiency > 1) {
        return;
      }
      
      setIsLoadingOptimal(true);
      try {
        const result = await apiService.calculateOptimalParameters({
          load_profile: loadProfile,
          efficiency: parameters.efficiency
        });
        
        setOptimalPower(result.optimal_power_mw);
        setOptimalCapacity(result.optimal_capacity_mwh);
      } catch (error) {
        console.error('Ошибка при расчете оптимальных параметров:', error);
        setOptimalPower(null);
        setOptimalCapacity(null);
      } finally {
        setIsLoadingOptimal(false);
      }
    };
    
    calculateOptimal();
  }, [loadProfile, parameters.efficiency]);
  
  // Обработчики для drag высоты
  const handleMouseMove = (e) => {
    if (isDraggingHeight) {
      const deltaY = dragStartY - e.clientY;
      const deltaPower = (deltaY / scaleY);
      let newPower = dragStartPower + deltaPower;
      newPower = Math.round(newPower / 10) * 10; // Округление до 10 МВт
      newPower = Math.max(10, Math.min(maxPower, newPower));
      
      setBatteryPower(newPower);
      
      // Пересчет емкости с сохранением начальной длительности
      const initialDuration = dragStartCapacity / dragStartPower;
      let newCapacity = newPower * initialDuration;
      // newCapacity = Math.round(newCapacity / 100) * 100; // Округление до 100 МВтч
      setBatteryCapacity(newCapacity);
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
    }
  };
  
  const handleMouseUp = () => {
    setIsDraggingHeight(false);
    setIsDraggingWidth(false);
  };
  
  useEffect(() => {
    if (isDraggingHeight || isDraggingWidth) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDraggingHeight, isDraggingWidth, dragStartY, dragStartX, dragStartPower, dragStartCapacity, scaleY, scaleX, maxPower, maxDurationHours, batteryDuration, batteryCapacity, batteryPower]);
  
  // Функция установки оптимальных параметров
  const resetToRecommended = () => {
    if (optimalPower && optimalCapacity) {
      setBatteryPower(Math.round(optimalPower));
      setBatteryCapacity(Math.round(optimalCapacity));
    } else {
      // Если оптимальные параметры не рассчитаны, используем приблизительные
      const recommendedPower = Math.round(maxPower * 0.6 / 10) * 10;
      const recommendedCapacity = Math.round(recommendedPower * 4 / 100) * 100;
      
      setBatteryPower(recommendedPower);
      setBatteryCapacity(recommendedCapacity);
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
      <div className="card max-w-7xl mx-auto">
        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <Battery className="w-6 h-6 mr-2 text-primary-600" />
          Интерактивный выбор параметров СНЭЭ
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
                    <li>Тяните <span className="font-bold text-green-700">зеленый маркер</span> вверх/вниз для изменения мощности инвертора</li>
                    <li>Тяните <span className="font-bold text-blue-700">синий маркер</span> влево/вправо для изменения емкости батареи</li>
                    <li><span className="font-bold text-green-700">Зеленая</span> и <span className="font-bold text-blue-700">синяя</span> пунктирные линии показывают оптимальные параметры мощности и длительности</li>
                    <li><span className="font-bold text-red-700">Красная</span> пунктирная линия показывает минимально необходимую мощность для покрытия максимального дефицита</li>
                  
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
              <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 border-2 border-green-300">
                <div className="text-xs text-gray-600 mb-0.5">Мощность инвертора</div>
                <div className="text-2xl font-bold text-green-700">{batteryPower.toFixed(0)} МВт</div>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border-2 border-blue-300">
                <div className="text-xs text-gray-600 mb-0.5">Емкость батареи</div>
                <div className="text-2xl font-bold text-blue-700">{batteryCapacity.toFixed(0)} МВтч</div>
              </div>

              <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-3 border-2 border-amber-300">
                    <div className="text-xs text-gray-600 mb-0.5">Время работы на номинальной мощности</div>
                    <div className="text-2xl font-bold text-amber-700">{(batteryCapacity / batteryPower).toFixed(1)} ч</div>
              </div>
              
              {/* <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3 border-2 border-purple-300">
                <div className="text-xs text-gray-600 mb-0.5">КПД цикла</div>
                <div className="text-2xl font-bold text-purple-700">{(parameters.efficiency * 100).toFixed(0)}%</div>
              </div> */}
              <button
              onClick={resetToRecommended}
              disabled={isLoadingOptimal}
              className={`w-full btn-secondary text-sm flex items-center justify-center ${isLoadingOptimal ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={optimalPower && optimalCapacity ? `Установить: ${optimalPower.toFixed(0)} МВт, ${optimalCapacity.toFixed(0)} МВтч` : 'Установить оптимальные параметры'}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              {isLoadingOptimal ? 'Расчет...' : 'Установить оценочные параметры'}
              </button>
            </div>


          
          {/* SVG батарея */}
          <div className="flex items-center justify-center">
              <svg
                ref={svgRef}
                viewBox={`0 0 ${viewWidth} ${viewHeight}`}
                className="border-2 border-gray-300 rounded-xl bg-white shadow-lg"
                style={{ 
                  width: '100%', 
                  maxWidth: '500px',
                  height: 'auto',
                  cursor: (isDraggingHeight || isDraggingWidth) ? 'grabbing' : 'default',
                  userSelect: 'none'
                }}
              >
                {/* Фон с сеткой */}
                <defs>
                  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" strokeWidth="0.5"/>
                  </pattern>
                  <linearGradient id="batteryGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
                    <stop offset="50%" stopColor="#2563eb" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#1d4ed8" stopOpacity="1" />
                  </linearGradient>
                  <filter id="shadow">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                
                <rect width={viewWidth} height={viewHeight} fill="url(#grid)" />
                
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
                {optimalPower && optimalCapacity && (
                  <>
                    {/* Оптимальная мощность - горизонтальная линия */}
                    <line
                      x1={padding}
                      y1={viewHeight - padding - optimalPower * scaleY}
                      x2={padding + maxWidth}
                      y2={viewHeight - padding - optimalPower * scaleY}
                      stroke="#10b981"
                      strokeWidth="2"
                      strokeDasharray="6,3"
                      opacity="0.7"
                    />
                    <text
                      x={padding + maxWidth + 5}
                      y={viewHeight - padding - optimalPower * scaleY}
                      fill="#10b981"
                      fontSize="10"
                      fontWeight="bold"
                      //textAnchor="end"
                    >
                      {optimalPower.toFixed(0)} МВт
                    </text>
                    
                    {/* Оптимальная длительность - вертикальная линия */}
                    {(() => {
                      const optimalDuration = optimalCapacity / optimalPower;
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
                
                {/* Линия минимально необходимой мощности */}
                {/* {minDeficit > 0 && (
                  <>
                    <line
                      x1={padding}
                      y1={viewHeight - padding - minDeficit * scaleY}
                      x2={padding + maxWidth}
                      y2={viewHeight - padding - minDeficit * scaleY}
                      stroke="#ef4444"
                      strokeWidth="2"
                      strokeDasharray="6,4"
                      opacity="0.8"
                    />
                    <text
                      x={padding + maxWidth + 5}
                      y={viewHeight - padding - minDeficit * scaleY}
                      fill="#ef4444"
                      fontSize="10"
                      fontWeight="bold"
                      //textAnchor="end"
                    >
                      {minDeficit.toFixed(0)} МВт
                    </text> */}
                    {/* <text
                      x={padding+10}
                      y={viewHeight - padding - minDeficit * scaleY - 10}
                      fill="#ef4444"
                      fontSize="9"
                      fontWeight="600"
                    >
                      Минимально необходимая мощность для покрытия максимального дефицита
                    </text> */}
                  {/* </>
                )} */}
                
                {/* Батарея */}
                <g>
                  {/* Тело батареи */}
                  <rect
                    x={padding}
                    y={viewHeight - padding - batteryHeight}
                    width={batteryWidth}
                    height={batteryHeight}
                    fill="url(#batteryGradient)"
                    stroke="#1e40af"
                    strokeWidth="3"
                    rx="6"
                    filter="url(#shadow)"
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
                    <circle cx="0" cy="0" r="16" fill="#10b981" stroke="#065f46" strokeWidth="2.5" filter="url(#shadow)"/>
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
                    <circle cx="0" cy="0" r="16" fill="#3b82f6" stroke="#1e40af" strokeWidth="2.5" filter="url(#shadow)"/>
                    <line x1="-8" y1="0" x2="8" y2="0" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <polygon points="-8,-5 -12,0 -8,5" fill="white"/>
                    <polygon points="8,-5 12,0 8,5" fill="white"/>
                  </g>
                </g>
                
                {/* Оси */}
                <line x1={padding} y1={viewHeight - padding} x2={padding + maxWidth + 10} y2={viewHeight - padding} 
                      stroke="#475569" strokeWidth="2" markerEnd="url(#arrowX)"/>
                <line x1={padding} y1={viewHeight - padding} x2={padding} y2={viewHeight - padding - maxHeight - 10} 
                      stroke="#475569" strokeWidth="2" markerEnd="url(#arrowY)"/>
                
                <defs>
                  <marker id="arrowX" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                    <polygon points="0,0 10,5 0,10" fill="#475569"/>
                  </marker>
                  <marker id="arrowY" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
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
              ) : optimalPower && optimalCapacity ? (
                <>
                  <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 border-2 border-green-300">
                    <div className="text-xs text-gray-600 mb-0.5">Мощность инвертора (оптимальная)</div>
                    <div className="text-2xl font-bold text-green-700">{optimalPower.toFixed(0)} МВт</div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border-2 border-blue-300">
                    <div className="text-xs text-gray-600 mb-0.5">Емкость батареи (оптимальная)</div>
                    <div className="text-2xl font-bold text-blue-700">{optimalCapacity.toFixed(0)} МВтч</div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-3 border-2 border-amber-300">
                    <div className="text-xs text-gray-600 mb-0.5">Время работы на номинальной мощности</div>
                    <div className="text-2xl font-bold text-amber-700">{(optimalCapacity / optimalPower).toFixed(1)} ч</div>
                  </div>
                </>
              ) : (
                <div className="bg-gray-50 rounded-lg p-4 border-2 border-gray-300 text-center">
                  <div className="text-sm text-gray-600">Оптимальные параметры недоступны</div>
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

export default BatteryInteractiveSection;
