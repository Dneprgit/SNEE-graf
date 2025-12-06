import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Battery, Info, RotateCcw, Zap } from 'lucide-react';

const BatteryInteractiveSection = ({ loadProfile, parameters, setParameters }) => {
  // Расчет максимальных значений
  const maxPower = Math.max(...loadProfile); // Максимум мощности баланса
  const totalSurplus = loadProfile.filter(v => v > 0).reduce((a, b) => a + b, 0); // Избыток энергии
  const maxDurationHours = totalSurplus / maxPower; // Максимальная длительность в часах
  
  // Состояние для размеров батареи
  const [batteryPower, setBatteryPower] = useState(parameters.rated_power_mw);
  const [batteryCapacity, setBatteryCapacity] = useState(parameters.rated_capacity_mwh);
  
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
  
  // Обработчики для drag высоты
  const handleMouseMove = (e) => {
    if (isDraggingHeight) {
      const deltaY = dragStartY - e.clientY;
      const deltaPower = (deltaY / scaleY);
      let newPower = dragStartPower + deltaPower;
      newPower = Math.round(newPower / 10) * 10; // Округление до 10 МВт
      newPower = Math.max(10, Math.min(maxPower, newPower));
      
      setBatteryPower(newPower);
      
      // Пересчет емкости пропорционально
      const ratio = batteryCapacity / dragStartCapacity;
      let newCapacity = (newPower * batteryDuration);
      newCapacity = Math.round(newCapacity / 100) * 100; // Округление до 100 МВтч
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
  
  // Функция сброса к рекомендуемым параметрам
  const resetToRecommended = () => {
    const recommendedPower = Math.round(maxPower * 0.6 / 10) * 10;
    const recommendedCapacity = Math.round(recommendedPower * 4 / 100) * 100;
    
    setBatteryPower(recommendedPower);
    setBatteryCapacity(recommendedCapacity);
  };
  
  return (
    <section id="battery-interactive" className="section-container bg-gradient-to-br from-blue-50 to-indigo-50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Интерактивный выбор параметров СНЭЭ</h2>
        <p className="section-subtitle text-center">
          Изменяйте размеры батареи, чтобы настроить мощность и емкость
        </p>
        
        <div className="card max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-[1fr,auto] gap-8">
            {/* Инфо панель */}
            <div className="space-y-4">
              <div className="flex items-center text-lg font-semibold text-gray-800 mb-4">
                <Info className="w-6 h-6 mr-2 text-primary-600" />
                Текущие параметры
              </div>
              
              <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4 border-2 border-green-300">
                <div className="text-sm text-gray-600 mb-1">Мощность инвертора</div>
                <div className="text-3xl font-bold text-green-700">{batteryPower.toFixed(0)} МВт</div>
                <div className="text-xs text-gray-500 mt-1">
                  Высота батареи • Макс: {maxPower.toFixed(0)} МВт
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border-2 border-blue-300">
                <div className="text-sm text-gray-600 mb-1">Емкость батареи</div>
                <div className="text-3xl font-bold text-blue-700">{batteryCapacity.toFixed(0)} МВтч</div>
                <div className="text-xs text-gray-500 mt-1">
                  Ширина: {batteryDuration.toFixed(1)} ч • Макс: {maxDurationHours.toFixed(1)} ч
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border-2 border-purple-300">
                <div className="text-sm text-gray-600 mb-1">КПД цикла</div>
                <div className="text-3xl font-bold text-purple-700">{(parameters.efficiency * 100).toFixed(0)}%</div>
              </div>
              
              <div className="bg-amber-50 rounded-lg p-4 border-2 border-amber-200 text-sm text-amber-900">
                <div className="flex items-start">
                  <Zap className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0 text-amber-600" />
                  <div>
                    <strong className="block mb-1">Как использовать:</strong>
                    <ul className="list-disc list-inside space-y-1 text-xs">
                      <li>Тяните <span className="font-bold text-green-700">зеленый маркер</span> вверх/вниз для изменения мощности</li>
                      <li>Тяните <span className="font-bold text-blue-700">синий маркер</span> влево/вправо для изменения емкости</li>
                      <li>Пунктирная рамка показывает максимальные размеры</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <button
                onClick={resetToRecommended}
                className="w-full btn-secondary text-sm flex items-center justify-center"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Рекомендуемые параметры
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
                    transform={`translate(${padding + batteryWidth}, ${viewHeight - padding + 35})`}
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
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default BatteryInteractiveSection;
