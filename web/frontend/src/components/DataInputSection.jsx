import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Download, FileText, Calculator } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
import * as XLSX from 'xlsx';

const DataInputSection = ({
  loadProfile,
  setLoadProfile,
  parameters,
  setParameters,
  setError,
}) => {
  const [uploadStatus, setUploadStatus] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadStatus('Загрузка...');
    setError(null);

    try {
      const data = await apiService.uploadExcel(file);
      setLoadProfile(data.load_profile);
      setUploadStatus('Файл успешно загружен!');
      setTimeout(() => setUploadStatus(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке файла');
      setUploadStatus(null);
    }
  }, [setLoadProfile, setError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
  });

  const handleParameterChange = (field, value) => {
    const numValue = parseFloat(value) || 0;
    
    setParameters(prev => {
      const updated = { ...prev, [field]: numValue };
      
      // Пересчет при изменении мощности инвертора
      if (field === 'rated_power_mw' && numValue > 0) {
        updated.runtime_hours = Math.round((prev.rated_capacity_mwh / numValue) * 10) / 10;
      }
      
      // Пересчет при изменении емкости батареи
      if (field === 'rated_capacity_mwh' && prev.rated_power_mw > 0) {
        updated.runtime_hours = Math.round((numValue / prev.rated_power_mw) * 10) / 10;
      }
      
      // Пересчет при изменении времени работы
      if (field === 'runtime_hours' && prev.rated_power_mw > 0) {
        updated.rated_capacity_mwh = numValue * prev.rated_power_mw;
      }
      
      return updated;
    });
  };

  // Автоматический расчет времени работы при загрузке данных
  useEffect(() => {
    if (parameters.rated_power_mw > 0 && parameters.rated_capacity_mwh > 0 && !parameters.runtime_hours) {
      setParameters(prev => ({
        ...prev,
        runtime_hours: Math.round((prev.rated_capacity_mwh / prev.rated_power_mw) * 10) / 10,
      }));
    }
  }, [parameters.rated_power_mw, parameters.rated_capacity_mwh]);

  const loadDefaultProfile = async () => {
    try {
      const data = await apiService.getDefaultProfile();
      setLoadProfile(data.load_profile);
      setUploadStatus('Загружен профиль по умолчанию');
      setTimeout(() => setUploadStatus(null), 3000);
    } catch (err) {
      setError('Ошибка при загрузке профиля по умолчанию');
    }
  };

  const downloadTemplate = () => {
    const hours = Array.from({ length: 24 }, (_, i) => i + 1);
    const template = [
      ['Час', 'Баланс мощности, МВт'],
      ...hours.map(h => [h, '']),
    ];

    const ws = XLSX.utils.aoa_to_sheet(template);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Баланс');
    XLSX.writeFile(wb, 'snee_template.xlsx');
  };

  // Компонент для редактирования значения с локальным состоянием
  const EditableValueInput = ({ value, index, onChange }) => {
    const [localValue, setLocalValue] = useState(String(value));
    
    useEffect(() => {
      setLocalValue(String(value));
    }, [value]);
    
    const normalizeValue = (inputValue) => {
      if (inputValue === '' || inputValue === '-') {
        return 0;
      } else {
        const numValue = parseFloat(inputValue);
        return isNaN(numValue) ? 0 : numValue;
      }
    };
    
    const handleBlur = (e) => {
      const normalized = normalizeValue(e.target.value);
      onChange(index, normalized);
    };
    
    const handleKeyDown = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const normalized = normalizeValue(e.target.value);
        onChange(index, normalized);
        
        // Переводим фокус на следующий input по data-атрибуту
        // Используем setTimeout для надежного перевода фокуса после обновления DOM React
        setTimeout(() => {
          const nextIndex = index + 1;
          // Ищем следующее поле по всему документу
          const nextInput = document.querySelector(`input[data-field-index="${nextIndex}"]`);
          if (nextInput) {
            nextInput.focus();
            // Выделяем содержимое для быстрого ввода нового значения
            nextInput.select();
          }
        }, 50);
      }
    };
    
    return (
      <div className="flex flex-col">
        <label className="text-xs font-semibold text-gray-600 mb-1">
          Час {index + 1}
        </label>
        <input
          type="number"
          data-field-index={index}
          value={localValue}
          onChange={(e) => {
            setLocalValue(e.target.value);
          }}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          className="input-field text-sm py-1 px-1"
          step="100"
        />
      </div>
    );
  };

  return (
    <section id="data-input" className="section-container bg-white/50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Исходные данные</h2>
        <p className="section-subtitle text-center">
          Загрузите баланс мощности и настройте параметры СНЭЭ
        </p>
        <div className="grid md:grid-cols-2 xl:grid-cols-2 gap-6 max-w-full mx-auto">
          {/* Загрузка данных */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="card"
          >
            <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <Upload className="w-6 h-6 mr-2 text-primary-600" />
              Загрузка баланса мощности
            </h3>

            {/* Drag & Drop зона */}
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <FileText className="w-12 h-12 mx-auto mb-4 text-primary-600" />
              {isDragActive ? (
                <p className="text-primary-700 font-semibold">Отпустите файл здесь...</p>
              ) : (
                <>
                  <p className="text-gray-700 font-medium mb-2">
                    Перетащите Excel файл сюда
                  </p>
                  <p className="text-gray-500 text-sm">
                    или кликните для выбора файла (.xlsx, .xls)
                  </p>
                </>
              )}
            </div>

            {uploadStatus && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm"
              >
                {uploadStatus}
              </motion.div>
            )}

            <div className="flex gap-3 mt-4">
              <button
                onClick={loadDefaultProfile}
                className="flex-1 btn-secondary text-sm"
              >
                Профиль по умолчанию
              </button>
              <button
                onClick={downloadTemplate}
                className="flex-1 btn-secondary text-sm flex items-center justify-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Шаблон
              </button>
            </div>

            {loadProfile && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <p className="text-sm text-blue-800 font-medium">
                  ✓ Профиль загружен: {loadProfile.length} значений
                </p>
              </motion.div>
            )}
          </motion.div>

          {/* Параметры СНЭЭ */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
            className="card"
          >
            <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <Calculator className="w-6 h-6 mr-2 text-primary-600" />
              Параметры СНЭЭ
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Мощность инвертора, МВт
                </label>
                <input
                  type="number"
                  value={parameters.rated_power_mw}
                  onChange={(e) => handleParameterChange('rated_power_mw', e.target.value)}
                  className="input-field"
                  min="0"
                  step="10"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Емкость батареи, МВтч
                </label>
                <input
                  type="number"
                  value={parameters.rated_capacity_mwh}
                  onChange={(e) => handleParameterChange('rated_capacity_mwh', e.target.value)}
                  className="input-field"
                  min="0"
                  step="100"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Время работы на номинальной мощности, ч
                </label>
                <input
                  type="number"
                  value={parameters.runtime_hours || ''}
                  onChange={(e) => handleParameterChange('runtime_hours', e.target.value)}
                  className="input-field"
                  min="0"
                  step="0.1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Автоматически рассчитывается как Емкость / Мощность
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  КПД цикла
                </label>
                <input
                  type="number"
                  value={parameters.efficiency}
                  onChange={(e) => handleParameterChange('efficiency', e.target.value)}
                  className="input-field"
                  min="0"
                  max="1"
                  step="0.01"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Значение от 0 до 1 (например, 0.95 = 95%)
                </p>
              </div>
            </div>
          </motion.div>

          {/* Таблица редактирования */}
            {loadProfile && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="card md:col-span-2 xl:col-span-2"
            >
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center" gap-2>
                <FileText className="w-6 h-6 mr-2 text-primary-600" />
                Редактирование значений
              </h3>
              <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-8 lg:grid-cols-12 xl:grid-cols-12 2xl:grid-cols-24 gap-1">
                {loadProfile.map((value, index) => (
                  <EditableValueInput
                    key={index}
                    value={value}
                    index={index}
                    onChange={(idx, newValue) => {
                      const updated = [...loadProfile];
                      updated[idx] = newValue;
                      setLoadProfile(updated);
                    }}
                  />
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-4">
                💡 Положительные значения — избыток энергии, отрицательные — дефицит
              </p>
            </motion.div>
          )}
          </div>

      </motion.div>
    </section>
  );
};

export default DataInputSection;

