import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Hero from './components/Hero';
import DataInputSection from './components/DataInputSection';
import DataVisualizationSection from './components/DataVisualizationSection';
import ChartsSection from './components/ChartsSection';
import SchematicSection from './components/SchematicSection';
import DataInputSection_ppw from './components/DataInputSection_ppw';
import DataVisualizationSection_ppw from './components/DataVisualizationSection_ppw';
import ChartsSection_ppw from './components/ChartsSection_ppw';
import SchematicSection_ppw from './components/SchematicSection_ppw';
import Footer from './components/Footer';
import { apiService } from './services/api';

function App() {
  // Состояние активного варианта ('v1' - первый вариант, 'ppw' - второй вариант)
  const [activeVariant, setActiveVariant] = useState('v1');
  
  // Состояния для первого варианта (water-filling)
  const [loadProfile, setLoadProfile] = useState(null);
  const [parameters, setParameters] = useState({
    rated_power_mw: 500,
    rated_capacity_mwh: 2000,
    efficiency: 0.95,
  });
  const [calculationResult, setCalculationResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  
  // Состояния для второго варианта (PPW - квадратичная оптимизация)
  const [loadProfile_ppw, setLoadProfile_ppw] = useState(null);
  const [parameters_ppw, setParameters_ppw] = useState({
    rated_power_in_mw: 95,
    rated_power_out_mw: 140,
    rated_capacity_mwh: 400,
    nominal_discharge_time_h: 2.86,
    capacity_utilization_percent: 90,
    working_range_energy_mwh: 360,
    actual_discharge_time_h: 2.57,
    efficiency: 0.95,
    charge_energy_mwh: 378.95,
    actual_charge_time_h: 3.99,
  });
  const [calculationResult_ppw, setCalculationResult_ppw] = useState(null);
  const [isCalculating_ppw, setIsCalculating_ppw] = useState(false);
  const [error_ppw, setError_ppw] = useState(null);

  // Загрузка профиля по умолчанию при запуске
  useEffect(() => {
    loadDefaultProfile();
  }, []);

  const loadDefaultProfile = async () => {
    try {
      const data = await apiService.getDefaultProfile();
      setLoadProfile(data.load_profile);
    } catch (err) {
      console.error('Error loading default profile:', err);
      setError('Не удалось загрузить профиль по умолчанию');
    }
  };

  // Автоматический пересчет при изменении параметров (если уже был выполнен расчет)
  useEffect(() => {
    if (calculationResult && loadProfile) {
      const timer = setTimeout(() => {
        handleCalculate();
      }, 500); // Debounce 500ms
      return () => clearTimeout(timer);
    }
  }, [parameters.rated_power_mw, parameters.rated_capacity_mwh, parameters.efficiency]);

  // Автоматический пересчет для PPW варианта
  useEffect(() => {
    if (calculationResult_ppw && loadProfile_ppw) {
      const timer = setTimeout(() => {
        handleCalculate_ppw();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [parameters_ppw.rated_power_in_mw, parameters_ppw.rated_power_out_mw, parameters_ppw.working_range_energy_mwh, parameters_ppw.efficiency]);

  const handleCalculate = async () => {
    if (!loadProfile || loadProfile.length !== 24) {
      setError('Необходимо загрузить корректный профиль баланса (24 значения)');
      return;
    }

    setIsCalculating(true);
    setError(null);

    try {
      const result = await apiService.calculateSchedule({
        load_profile: loadProfile,
        ...parameters,
      });
      setCalculationResult(result);
    } catch (err) {
      console.error('Calculation error:', err);
      setError(err.response?.data?.detail || 'Ошибка при расчете графика');
    } finally {
      setIsCalculating(false);
    }
  };

  const handleCalculate_ppw = async () => {
    if (!loadProfile_ppw || loadProfile_ppw.length !== 24) {
      setError_ppw('Необходимо загрузить корректный профиль баланса (24 значения)');
      return;
    }

    setIsCalculating_ppw(true);
    setError_ppw(null);

    try {
      const result = await apiService.calculatePPWSchedule({
        system_load: loadProfile_ppw,
        rated_power_in_mw: parameters_ppw.rated_power_in_mw,
        rated_power_out_mw: parameters_ppw.rated_power_out_mw,
        capacity_mwh: parameters_ppw.working_range_energy_mwh,
        efficiency: parameters_ppw.efficiency,
      });
      setCalculationResult_ppw(result);
    } catch (err) {
      console.error('Calculation error (PPW):', err);
      setError_ppw(err.response?.data?.detail || 'Ошибка при расчете графика PPW');
    } finally {
      setIsCalculating_ppw(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Hero activeVariant={activeVariant} setActiveVariant={setActiveVariant} />
      
      {activeVariant === 'v1' ? (
        // Первый вариант (water-filling)
        <>
          <DataInputSection
            loadProfile={loadProfile}
            setLoadProfile={setLoadProfile}
            parameters={parameters}
            setParameters={setParameters}
            setError={setError}
          />

          {loadProfile && (
            <DataVisualizationSection
              loadProfile={loadProfile}
              onCalculate={handleCalculate}
              isCalculating={isCalculating}
              error={error}
            />
          )}

          {calculationResult && (
            <>
              <ChartsSection
                loadProfile={loadProfile}
                calculationResult={calculationResult}
                parameters={parameters}
                setParameters={setParameters}
              />
              
              <SchematicSection
                calculationResult={calculationResult}
                parameters={parameters}
              />
            </>
          )}
        </>
      ) : (
        // Второй вариант (PPW - квадратичная оптимизация)
        <>
          <DataInputSection_ppw
            loadProfile={loadProfile_ppw}
            setLoadProfile={setLoadProfile_ppw}
            parameters={parameters_ppw}
            setParameters={setParameters_ppw}
            setError={setError_ppw}
          />

          {loadProfile_ppw && (
            <DataVisualizationSection_ppw
              loadProfile={loadProfile_ppw}
              onCalculate={handleCalculate_ppw}
              isCalculating={isCalculating_ppw}
              error={error_ppw}
            />
          )}

          {calculationResult_ppw && (
            <>
              <ChartsSection_ppw
                loadProfile={loadProfile_ppw}
                calculationResult={calculationResult_ppw}
                parameters={parameters_ppw}
                setParameters={setParameters_ppw}
              />
              
              <SchematicSection_ppw
                calculationResult={calculationResult_ppw}
                parameters={parameters_ppw}
              />
            </>
          )}
        </>
      )}

      <Footer />
    </div>
  );
}

export default App;

