import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Download, FileText, Info } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
import * as XLSX from 'xlsx';

const DataInputSection_ppw = ({
  loadProfile,
  setLoadProfile,
  parameters,
  setParameters,
  setError,
}) => {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [lastModifiedField, setLastModifiedField] = useState(null);

  // Обработка загрузки Excel файлов
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

  // Логика пересчета параметров с приоритетами
  const handleParameterChange = (field, value, isUserInput = true) => {
    const numValue = parseFloat(value) || 0;
    
    if (isUserInput) {
      setLastModifiedField(field);
    }
    
    setParameters(prev => {
      const updated = { ...prev, [field]: numValue };
      
      // Приоритеты: Мощность (1) > Энергия (2) > Время и КПД (3)
      
      // Номинальная активная входная мощность (приоритет 1)
      if (field === 'rated_power_in_mw' && numValue > 0) {
        if (updated.charge_energy_mwh > 0) {
          updated.actual_charge_time_h = updated.charge_energy_mwh / numValue;
        }
      }
      
      // Номинальная активная выходная мощность (приоритет 1)
      if (field === 'rated_power_out_mw' && numValue > 0) {
        if (updated.rated_capacity_mwh > 0) {
          updated.nominal_discharge_time_h = updated.rated_capacity_mwh / numValue;
        }
        if (updated.working_range_energy_mwh > 0) {
          updated.actual_discharge_time_h = updated.working_range_energy_mwh / numValue;
        }
      }
      
      // Номинальная энергоемкость (приоритет 2)
      if (field === 'rated_capacity_mwh') {
        if (updated.rated_power_out_mw > 0) {
          updated.nominal_discharge_time_h = numValue / updated.rated_power_out_mw;
        }
        if (updated.capacity_utilization_percent > 0) {
          updated.working_range_energy_mwh = numValue * updated.capacity_utilization_percent / 100;
          if (updated.rated_power_out_mw > 0) {
            updated.actual_discharge_time_h = updated.working_range_energy_mwh / updated.rated_power_out_mw;
          }
          if (updated.efficiency > 0) {
            updated.charge_energy_mwh = updated.working_range_energy_mwh / updated.efficiency * 100;
            if (updated.rated_power_in_mw > 0) {
              updated.actual_charge_time_h = updated.charge_energy_mwh / updated.rated_power_in_mw;
            }
          }
        }
      }
      
      // Коэффициент использования емкости (приоритет 2)
      if (field === 'capacity_utilization_percent') {
        if (updated.rated_capacity_mwh > 0) {
          updated.working_range_energy_mwh = updated.rated_capacity_mwh * numValue / 100;
          if (updated.rated_power_out_mw > 0) {
            updated.actual_discharge_time_h = updated.working_range_energy_mwh / updated.rated_power_out_mw;
          }
          if (updated.efficiency > 0) {
            updated.charge_energy_mwh = updated.working_range_energy_mwh / updated.efficiency * 100;
            if (updated.rated_power_in_mw > 0) {
              updated.actual_charge_time_h = updated.charge_energy_mwh / updated.rated_power_in_mw;
            }
          }
        }
      }
      
      // Энергия в рабочем диапазоне (приоритет 2)
      if (field === 'working_range_energy_mwh') {
        if (updated.rated_capacity_mwh > 0) {
          updated.capacity_utilization_percent = numValue / updated.rated_capacity_mwh * 100;
        }
        if (updated.rated_power_out_mw > 0) {
          updated.actual_discharge_time_h = numValue / updated.rated_power_out_mw;
        }
        if (updated.efficiency > 0) {
          updated.charge_energy_mwh = numValue / updated.efficiency * 100;
          if (updated.rated_power_in_mw > 0) {
            updated.actual_charge_time_h = updated.charge_energy_mwh / updated.rated_power_in_mw;
          }
        }
      }
      
      // Энергоэффективность (КПД) (приоритет 3)
      if (field === 'efficiency') {
        if (updated.working_range_energy_mwh > 0 && numValue > 0) {
          updated.charge_energy_mwh = updated.working_range_energy_mwh / numValue * 100;
          if (updated.rated_power_in_mw > 0) {
            updated.actual_charge_time_h = updated.charge_energy_mwh / updated.rated_power_in_mw;
          }
        }
      }
      
      // Номинальное время разряда (приоритет 3)
      if (field === 'nominal_discharge_time_h' && lastModifiedField === field) {
        if (updated.rated_power_out_mw > 0) {
          updated.rated_capacity_mwh = numValue * updated.rated_power_out_mw;
          if (updated.capacity_utilization_percent > 0) {
            updated.working_range_energy_mwh = updated.rated_capacity_mwh * updated.capacity_utilization_percent / 100;
            updated.actual_discharge_time_h = updated.working_range_energy_mwh / updated.rated_power_out_mw;
          }
        }
      }
      
      // Фактическое время разряда (приоритет 3)
      if (field === 'actual_discharge_time_h' && lastModifiedField === field) {
        if (updated.rated_power_out_mw > 0) {
          updated.working_range_energy_mwh = numValue * updated.rated_power_out_mw;
          if (updated.rated_capacity_mwh > 0) {
            updated.capacity_utilization_percent = updated.working_range_energy_mwh / updated.rated_capacity_mwh * 100;
          }
        }
      }
      
      // Округление
      updated.nominal_discharge_time_h = Math.round(updated.nominal_discharge_time_h * 100) / 100;
      updated.capacity_utilization_percent = Math.round(updated.capacity_utilization_percent * 100) / 100;
      updated.working_range_energy_mwh = Math.round(updated.working_range_energy_mwh * 100) / 100;
      updated.actual_discharge_time_h = Math.round(updated.actual_discharge_time_h * 100) / 100;
      updated.charge_energy_mwh = Math.round(updated.charge_energy_mwh * 100) / 100;
      updated.actual_charge_time_h = Math.round(updated.actual_charge_time_h * 100) / 100;
      
      return updated;
    });
  };

  const loadDefaultProfile = async () => {
    try {
      // Дефолтные данные из таблицы пользователя для PPW варианта
      const defaultData = [
        27, 38, 84, 137.5370102, 21.32816033, -115.1881803, -166.1770748, -185.5883293,
        -130.302316, -48.170602, 37.54855761, 152, 103, 175, 99, 49,
        -47, 7, -130, -176, -117, -222, -205, -166
      ];
      setLoadProfile(defaultData);
      setUploadStatus('Загружен профиль по умолчанию');
      setTimeout(() => setUploadStatus(null), 3000);
    } catch (err) {
      setError('Ошибка при загрузке профиля по умолчанию');
    }
  };

  const downloadTemplate = () => {
    const hours = Array.from({ length: 24 }, (_, i) => i + 1);
    const template = [
      ['Час', 'Баланс мощности энергосистемы, МВт'],
      ...hours.map(h => [h, '']),
    ];

    const ws = XLSX.utils.aoa_to_sheet(template);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Баланс');
    XLSX.writeFile(wb, 'snee_ppw_template.xlsx');
  };

  // Обработка вставки из буфера обмена
  const handlePaste = async (e, hourIndex) => {
    e.preventDefault();
    const paste = e.clipboardData.getData('text');
    const values = paste.split(/[\t\n\r,]+/).map(v => parseFloat(v.trim())).filter(v => !isNaN(v));
    
    if (values.length === 24) {
      // Вставляем все 24 значения
      setLoadProfile(values);
    } else if (values.length > 0 && hourIndex !== null) {
      // Вставляем начиная с текущего часа
      const newProfile = [...loadProfile];
      values.forEach((val, idx) => {
        if (hourIndex + idx < 24) {
          newProfile[hourIndex + idx] = val;
        }
      });
      setLoadProfile(newProfile);
    }
  };

  const handleValueChange = (index, value) => {
    const newProfile = [...loadProfile];
    newProfile[index] = parseFloat(value) || 0;
    setLoadProfile(newProfile);
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="section-container py-12 bg-gray-50"
    >
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-center">Исходные данные (PPW вариант)</h2>

        {/* Параметры СНЭЭ */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-6 h-6 text-primary-600" />
            Параметры СНЭЭ
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Поле 1: Номинальная активная входная мощность */}
            <div className="bg-red-50 p-3 rounded-lg border-2 border-red-200">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Ном. входная мощность, МВт
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Номинальная активная входная мощность (dblNIn)" />
              </label>
              <input
                type="number"
                step="0.1"
                value={parameters.rated_power_in_mw}
                onChange={(e) => handleParameterChange('rated_power_in_mw', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 bg-white"
              />
            </div>

            {/* Поле 2: Номинальная активная выходная мощность */}
            <div className="bg-green-50 p-3 rounded-lg border-2 border-green-200">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Ном. выходная мощность, МВт
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Номинальная активная выходная мощность (dblNOut)" />
              </label>
              <input
                type="number"
                step="0.1"
                value={parameters.rated_power_out_mw}
                onChange={(e) => handleParameterChange('rated_power_out_mw', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 bg-white"
              />
            </div>

            {/* Поле 3: Номинальная энергоемкость */}
            <div className="p-3">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Ном. энергоемкость, МВтч
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Номинальная энергоемкость (выходная)" />
              </label>
              <input
                type="number"
                step="1"
                value={parameters.rated_capacity_mwh}
                onChange={(e) => handleParameterChange('rated_capacity_mwh', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            {/* Поле 4: Номинальное время разряда (рассчитываемое) */}
            <div className="p-3">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Ном. время разряда, ч
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Рассчитывается: Ном. энергоемкость / Ном. выходная мощность" />
              </label>
              <input
                type="number"
                step="0.01"
                value={parameters.nominal_discharge_time_h}
                onChange={(e) => handleParameterChange('nominal_discharge_time_h', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 bg-gray-50"
              />
            </div>

            {/* Поле 5: Коэффициент использования емкости */}
            <div className="p-3">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Коэф. использ. емкости, %
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Коэффициент использования емкости (глубина разряда)" />
              </label>
              <input
                type="number"
                step="1"
                value={parameters.capacity_utilization_percent}
                onChange={(e) => handleParameterChange('capacity_utilization_percent', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            {/* Поле 6: Энергия в рабочем диапазоне */}
            <div className="bg-green-50 p-3 rounded-lg border-2 border-green-200">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Энергия раб. диапазона, МВтч
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Энергия, фактически отдаваемая в рабочем диапазоне (dblCapacity)" />
              </label>
              <input
                type="number"
                step="1"
                value={parameters.working_range_energy_mwh}
                onChange={(e) => handleParameterChange('working_range_energy_mwh', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 bg-white"
              />
            </div>

            {/* Поле 7: Фактическое время разряда */}
            <div className="p-3">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Факт. время разряда, ч
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Рассчитывается: Энергия раб. диапазона / Ном. выходная мощность" />
              </label>
              <input
                type="number"
                step="0.01"
                value={parameters.actual_discharge_time_h}
                onChange={(e) => handleParameterChange('actual_discharge_time_h', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 bg-gray-50"
              />
            </div>

            {/* Поле 8: Энергоэффективность (КПД) */}
            <div className="bg-yellow-50 p-3 rounded-lg border-2 border-yellow-200">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Энергоэффективность (КПД), %
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Энергоэффективность (КПД) цикла (dblEfficiency)" />
              </label>
              <input
                type="number"
                step="1"
                value={parameters.efficiency * 100}
                onChange={(e) => handleParameterChange('efficiency', parseFloat(e.target.value) / 100)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-yellow-500 bg-white"
              />
            </div>

            {/* Поле 9: Энергия затраченная на заряд */}
            <div className="p-3">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Энергия на заряд, МВтч
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Рассчитывается: Энергия раб. диапазона / КПД" />
              </label>
              <input
                type="number"
                step="1"
                value={parameters.charge_energy_mwh}
                readOnly
                className="w-full px-3 py-2 border rounded-lg bg-gray-50 cursor-not-allowed"
              />
            </div>

            {/* Поле 10: Фактическое время заряда */}
            <div className="p-3">
              <label className="block text-sm font-medium mb-1 flex items-center gap-1">
                Факт. время заряда, ч
                <Info className="w-4 h-4 text-gray-400 cursor-help" title="Рассчитывается: Энергия на заряд / Ном. входная мощность" />
              </label>
              <input
                type="number"
                step="0.01"
                value={parameters.actual_charge_time_h}
                readOnly
                className="w-full px-3 py-2 border rounded-lg bg-gray-50 cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Загрузка профиля */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-2xl font-semibold mb-4">Загрузка профиля</h3>
          
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600">
                {isDragActive ? 'Отпустите файл здесь...' : 'Перетащите Excel файл сюда или нажмите для выбора'}
              </p>
              {uploadStatus && (
                <p className="mt-2 text-sm text-primary-600 font-medium">{uploadStatus}</p>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <button
                onClick={loadDefaultProfile}
                className="btn-secondary flex items-center justify-center gap-2"
              >
                <FileText className="w-5 h-5" />
                Загрузить профиль по умолчанию
              </button>
              <button
                onClick={downloadTemplate}
                className="btn-secondary flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Скачать шаблон Excel
              </button>
            </div>
          </div>
        </div>

        {/* Редактирование значений */}
        {loadProfile && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-2xl font-semibold mb-4">
              Исходные данные суточного графика баланса мощности энергосистемы, МВт
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Положительные значения - избыток генерации (-), отрицательные - не покрываемое потребление (+)
            </p>
            
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
              {loadProfile.map((value, index) => (
                <div key={index} className="flex flex-col">
                  <label className="text-xs text-gray-600 mb-1">Час {index + 1}</label>
                  <input
                    type="number"
                    step="0.01"
                    value={value}
                    onChange={(e) => handleValueChange(index, e.target.value)}
                    onPaste={(e) => handlePaste(e, index)}
                    className="px-2 py-1 text-sm border rounded focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.section>
  );
};

export default DataInputSection_ppw;

