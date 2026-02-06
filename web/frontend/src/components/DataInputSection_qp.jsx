import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Download, FileText, Calculator } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
import * as XLSX from 'xlsx';

const DataInputSection_qp = ({
  loadProfile,
  setLoadProfile,
  parameters,
  setParameters,
  setError,
  onCalculateSchedule,
}) => {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null); // { name, data }
  const [lastExcelData, setLastExcelData] = useState(null);
  const [efficiencyInput, setEfficiencyInput] = useState(String(parameters.dblEfficiency_pq || ''));

  // Синхронизация локального состояния efficiency с внешним параметром
  useEffect(() => {
    setEfficiencyInput(String(parameters.dblEfficiency_pq || ''));
  }, [parameters.dblEfficiency_pq]);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadStatus('Загрузка...');
    setError(null);

    try {
      const data = await apiService.uploadExcel(file);
      setLoadProfile(data.load_profile);
      setLastExcelData(data.load_profile); // Сохраняем данные для восстановления
      setUploadedFile({ name: file.name, data: data.load_profile });
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
      
      // Пересчет при изменении выходной мощности
      if (field === 'dblNOut_pq' && numValue > 0) {
        updated.runtime_hours = Math.round((prev.dblCapacity_pq / numValue) * 10) / 10;
      }
      
      // Пересчет при изменении емкости батареи
      if (field === 'dblCapacity_pq' && prev.dblNOut_pq > 0) {
        updated.runtime_hours = Math.round((numValue / prev.dblNOut_pq) * 10) / 10;
      }
      
      // Пересчет при изменении времени работы
      if (field === 'runtime_hours' && prev.dblNOut_pq > 0) {
        updated.dblCapacity_pq = numValue * prev.dblNOut_pq;
      }
      
      return updated;
    });
  };

  // Обработчики для поля КПД с локальным состоянием
  const handleEfficiencyChange = (e) => {
    setEfficiencyInput(e.target.value);
  };

  const handleEfficiencyBlur = () => {
    const numValue = parseFloat(efficiencyInput);
    if (!isNaN(numValue) && numValue > 0 && numValue <= 1) {
      setParameters(prev => ({ ...prev, dblEfficiency_pq: numValue }));
    } else {
      // Возвращаем предыдущее корректное значение
      setEfficiencyInput(String(parameters.dblEfficiency_pq));
    }
  };

  // Автоматический расчет времени работы при загрузке данных
  useEffect(() => {
    if (parameters.dblNOut_pq > 0 && parameters.dblCapacity_pq > 0 && !parameters.runtime_hours) {
      setParameters(prev => ({
        ...prev,
        runtime_hours: Math.round((prev.dblCapacity_pq / prev.dblNOut_pq) * 10) / 10,
      }));
    }
  }, [parameters.dblNOut_pq, parameters.dblCapacity_pq]);

  const loadDefaultProfile = async () => {
    // Если есть загруженный Excel файл, восстанавливаем данные из него
    if (lastExcelData) {
      setLoadProfile(lastExcelData);
      setUploadStatus(`Восстановлены данные из ${uploadedFile.name}`);
      setTimeout(() => setUploadStatus(null), 3000);
      return;
    }
    
    // Иначе загружаем профиль по умолчанию
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
  const EditableValueInput = ({ value, index, onChange, onBulkPaste, totalFields }) => {
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
          const nextInput = document.querySelector(`input[data-field-index-qp="${nextIndex}"]`);
          if (nextInput) {
            nextInput.focus();
            // Выделяем содержимое для быстрого ввода нового значения
            nextInput.select();
          }
        }, 50);
      }
    };
    
    const handlePaste = (e) => {
      // Получаем данные из буфера обмена
      const pastedData = e.clipboardData.getData('text');
      
      if (!pastedData) return;
      
      // Разбиваем данные по переносам строк и табуляции
      // Excel копирует данные с табуляцией между ячейками и переносами строк между строками
      const rows = pastedData.split(/[\r\n]+/).filter(row => row.trim());
      
      // Собираем все значения из всех строк и столбцов
      const values = [];
      rows.forEach(row => {
        const cells = row.split('\t');
        cells.forEach(cell => {
          const trimmed = cell.trim();
          if (trimmed !== '') {
            const num = parseFloat(trimmed);
            if (!isNaN(num)) {
              values.push(num);
            }
          }
        });
      });
      
      // Если есть данные для вставки
      if (values.length > 0) {
        e.preventDefault();
        onBulkPaste(index, values);
      }
    };
    
    return (
      <div className="flex flex-col">
        <label className="text-xs font-semibold text-gray-600 mb-1">
          Час {index + 1}
        </label>
        <input
          type="number"
          data-field-index-qp={index}
          value={localValue}
          onChange={(e) => {
            setLocalValue(e.target.value);
          }}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          className="input-field text-sm py-1 px-1"
          step="100"
        />
      </div>
    );
  };

  return (
    <section id="data-input-qp" className="section-container bg-white/50">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Исходные данные (QP)</h2>
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
              ) : uploadedFile ? (
                <>
                  <p className="text-green-700 font-semibold mb-2">
                    ✓ Excel файл загружен
                  </p>
                  <p className="text-gray-700 font-medium mb-2">
                    {uploadedFile.name}
                  </p>
                  <p className="text-gray-500 text-sm">
                    Перетащите или кликните для загрузки другого файла
                  </p>
                </>
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
                {uploadedFile ? 'Восстановить данные из Excel' : 'Профиль по умолчанию'}
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

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Номинальная активная входная мощность (dblNIn), МВт
                </label>
                <input
                  type="number"
                  value={parameters.dblNIn_pq}
                  onChange={(e) => handleParameterChange('dblNIn_pq', e.target.value)}
                  className="input-field"
                  min="0"
                  step="10"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Номинальная активная выходная мощность (dblNOut), МВт
                </label>
                <input
                  type="number"
                  value={parameters.dblNOut_pq}
                  onChange={(e) => handleParameterChange('dblNOut_pq', e.target.value)}
                  className="input-field"
                  min="0"
                  step="10"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Энергия, фактически отдаваемая в рабочем диапазоне (dblCapacity), МВтч
                </label>
                <input
                  type="number"
                  value={parameters.dblCapacity_pq}
                  onChange={(e) => handleParameterChange('dblCapacity_pq', e.target.value)}
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
                  Энергоэффективность (КПД) (dblEfficiency)
                </label>
                <input
                  type="number"
                  value={efficiencyInput}
                  onChange={handleEfficiencyChange}
                  onBlur={handleEfficiencyBlur}
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
                Редактирование значений баланса мощности
              </h3>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-3 mb-4">
                <p className="text-sm text-gray-700">
                  <strong>Полярность для алгоритма QP:</strong>
                  <br />
                  • <span className="text-red-600 font-semibold">Положительное значение</span> = потребность в покрытии потребления (дефицит)
                  <br />
                  • <span className="text-green-600 font-semibold">Отрицательное значение</span> = избыток энергии
                </p>
              </div>
              <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-8 lg:grid-cols-12 xl:grid-cols-12 2xl:grid-cols-24 gap-1">
                {loadProfile.map((value, index) => (
                  <EditableValueInput
                    key={index}
                    value={value}
                    index={index}
                    totalFields={loadProfile.length}
                    onChange={(idx, newValue) => {
                      const updated = [...loadProfile];
                      updated[idx] = newValue;
                      setLoadProfile(updated);
                      if (onCalculateSchedule) {
                        onCalculateSchedule(updated);
                      }
                    }}
                    onBulkPaste={(startIndex, values) => {
                      const updated = [...loadProfile];
                      // Вставляем значения начиная с текущего индекса
                      values.forEach((val, i) => {
                        const targetIndex = startIndex + i;
                        if (targetIndex < updated.length) {
                          updated[targetIndex] = val;
                        }
                      });
                      setLoadProfile(updated);
                      if (onCalculateSchedule) {
                        onCalculateSchedule(updated);
                      }
                    }}
                  />
                ))}
              </div>
              <div className="mt-4 space-y-2">
                <p className="text-xs text-gray-500">
                  💡 Положительные значения — избыток энергии, отрицательные — дефицит
                </p>
                <p className="text-xs text-blue-600 font-medium">
                  📋 Совет: Вы можете скопировать данные из Excel и вставить их с помощью Ctrl+V в любое поле — значения автоматически заполнятся по порядку
                </p>
              </div>
            </motion.div>
          )}
          </div>

      </motion.div>
    </section>
  );
};

export default DataInputSection_qp;

