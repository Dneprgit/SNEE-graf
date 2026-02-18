import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Hero from './components/Hero';
import DataInputSection from './components/DataInputSection';
import DataVisualizationSection from './components/DataVisualizationSection';
import ChartsSection from './components/ChartsSection';
import SchematicSection from './components/SchematicSection';
import DataInputSection_qp from './components/DataInputSection_qp';
import DataVisualizationSection_qp from './components/DataVisualizationSection_qp';
import BatteryInteractiveSection_qp from './components/BatteryInteractiveSection_qp';
import ChartsSection_qp from './components/ChartsSection_qp';
import SchematicSection_qp from './components/SchematicSection_qp';
import Footer from './components/Footer';
import { apiService } from './services/api';

function App() {
  // Выбор алгоритма: 'wf' (water-filling) или 'qp' (quadratic programming)
  const [algorithm, setAlgorithm] = useState('qp');
  
  // Состояния для варианта Water-Filling
  const [loadProfile, setLoadProfile] = useState(null);
  const [parameters, setParameters] = useState({
    rated_power_mw: 500,
    rated_capacity_mwh: 2000,
    efficiency: 0.95,
  });
  const [calculationResult, setCalculationResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  
  // Состояния для варианта Quadratic Programming
  const [loadProfile_qp, setLoadProfile_qp] = useState(null);
  const [parameters_qp, setParameters_qp] = useState({
    dblNIn_pq: 115,
    dblNOut_pq: 145,
    dblCapacity_pq: 535,
    dblEfficiency_pq: 0.84,
  });
  const [calculationResult_qp, setCalculationResult_qp] = useState(null);
  const [showBatterySection_qp, setShowBatterySection_qp] = useState(false);
  const [optimalParams_qp, setOptimalParams_qp] = useState(null);
  const [isCalculating_qp, setIsCalculating_qp] = useState(false);
  const [isCalculatingOptimal_qp, setIsCalculatingOptimal_qp] = useState(false);
  const [error_qp, setError_qp] = useState(null);
  const [optimalError_qp, setOptimalError_qp] = useState(null);

  // Загрузка профиля по умолчанию при запуске
  useEffect(() => {
    loadDefaultProfile();
    loadDefaultProfile_qp();
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

  const loadDefaultProfile_qp = async () => {
    try {
      const data = await apiService.getDefaultProfile();
      setLoadProfile_qp(data.load_profile);
    } catch (err) {
      console.error('Error loading default profile:', err);
      setError_qp('Не удалось загрузить профиль по умолчанию');
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

  // Автоматический пересчет для QP варианта
  useEffect(() => {
    if (calculationResult_qp && loadProfile_qp) {
      const timer = setTimeout(() => {
        handleCalculate_qp();
      }, 500); // Debounce 500ms
      return () => clearTimeout(timer);
    }
  }, [parameters_qp.dblNIn_pq, parameters_qp.dblNOut_pq, parameters_qp.dblCapacity_pq, parameters_qp.dblEfficiency_pq]);

  const handleCalculate = async () => {
    if (!loadProfile || loadProfile.length !== 24) {
      setError('Необходимо загрузить корректный профиль баланса (24 значения)');
      return;
    }

    // Проверяем валидность КПД
    if (!parameters.efficiency || parameters.efficiency <= 0 || parameters.efficiency > 1) {
      setError('КПД должен быть в диапазоне от 0 до 1 (например, 0.95)');
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

  const handleCalculate_qp = async (overrideLoadProfile) => {
    const profile = Array.isArray(overrideLoadProfile) ? overrideLoadProfile : loadProfile_qp;
    if (!profile || profile.length !== 24) {
      setError_qp('Необходимо загрузить корректный профиль баланса (24 значения)');
      return;
    }

    // Проверяем валидность КПД
    if (!parameters_qp.dblEfficiency_pq || parameters_qp.dblEfficiency_pq <= 0 || parameters_qp.dblEfficiency_pq > 1) {
      setError_qp('КПД должен быть в диапазоне от 0 до 1 (например, 0.84)');
      return;
    }

    setIsCalculating_qp(true);
    setError_qp(null);

    try {
      const result = await apiService.calculateSchedule_qp({
        load_profile: profile,
        rated_input_power_mw: parameters_qp.dblNIn_pq,
        rated_output_power_mw: parameters_qp.dblNOut_pq,
        rated_capacity_mwh: parameters_qp.dblCapacity_pq,
        efficiency: parameters_qp.dblEfficiency_pq,
      });
      setCalculationResult_qp(result);
    } catch (err) {
      console.error('Calculation error:', err);
      setError_qp(err.response?.data?.detail || 'Ошибка при расчете графика');
    } finally {
      setIsCalculating_qp(false);
    }
  };

  const handleCalculateOptimal_qp = async () => {
    if (!loadProfile_qp || loadProfile_qp.length !== 24) {
      setOptimalError_qp('Необходимо загрузить корректный профиль баланса (24 значения)');
      return;
    }

    if (!parameters_qp.dblEfficiency_pq || parameters_qp.dblEfficiency_pq <= 0 || parameters_qp.dblEfficiency_pq > 1) {
      setOptimalError_qp('КПД должен быть в диапазоне от 0 до 1 (например, 0.84)');
      return;
    }

    setCalculationResult_qp(null);
    setShowBatterySection_qp(true);
    setIsCalculatingOptimal_qp(true);
    setOptimalError_qp(null);

    try {
      const result = await apiService.calculateOptimalParameters_qp({
        load_profile: loadProfile_qp,
        efficiency: parameters_qp.dblEfficiency_pq,
      });

      const discharge_time = result.optimal_capacity_mwh / result.optimal_power_out_mw;
      const charge_energy = result.optimal_capacity_mwh / parameters_qp.dblEfficiency_pq;
      const charge_time = charge_energy / result.optimal_power_in_mw;

      setOptimalParams_qp({
        power_in: result.optimal_power_in_mw,
        power_out: result.optimal_power_out_mw,
        capacity: result.optimal_capacity_mwh,
        deficit: result.deficit_mw,
        discharge_time,
        charge_energy,
        charge_time,
      });

      // На шаге расчета оценочных параметров сразу переносим их
      // в рабочие параметры СНЭЭ для следующего расчета графика.
      setParameters_qp(prev => ({
        ...prev,
        dblNIn_pq: result.optimal_power_in_mw,
        dblNOut_pq: result.optimal_power_out_mw,
        dblCapacity_pq: result.optimal_capacity_mwh,
        runtime_hours: discharge_time,
      }));
    } catch (err) {
      console.error('Optimal calculation error:', err);
      setOptimalError_qp(err.response?.data?.detail || 'Ошибка при расчете оценочных параметров');
    } finally {
      setIsCalculatingOptimal_qp(false);
    }
  };

  const handleQpProfileChange = (overrideLoadProfile) => {
    if (calculationResult_qp) {
      handleCalculate_qp(overrideLoadProfile);
    }
  };

  return (
    <div className="min-h-screen">
      <Hero algorithm={algorithm} setAlgorithm={setAlgorithm} />
      
      {algorithm === 'wf' ? (
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
              setLoadProfile={setLoadProfile}
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
        <>
          <DataInputSection_qp
            loadProfile={loadProfile_qp}
            setLoadProfile={setLoadProfile_qp}
            parameters={parameters_qp}
            setParameters={setParameters_qp}
            setError={setError_qp}
            onCalculateSchedule={handleQpProfileChange}
          />

          {loadProfile_qp && (
            <DataVisualizationSection_qp
              loadProfile={loadProfile_qp}
              setLoadProfile={setLoadProfile_qp}
              onCalculate={handleCalculateOptimal_qp}
              onCalculateSchedule={handleQpProfileChange}
              isCalculating={isCalculatingOptimal_qp}
              error={optimalError_qp}
            />
          )}

          {showBatterySection_qp && loadProfile_qp && (
            <BatteryInteractiveSection_qp
              loadProfile={loadProfile_qp}
              parameters={parameters_qp}
              setParameters={setParameters_qp}
              maxAbsValue={Math.max(...loadProfile_qp.map(v => Math.abs(v)))}
              setOptimalParams={setOptimalParams_qp}
              initialOptimalParams={optimalParams_qp}
              onCalculateSchedule={handleCalculate_qp}
              isCalculatingSchedule={isCalculating_qp}
              scheduleError={error_qp}
            />
          )}

          {calculationResult_qp && (
            <>
              <ChartsSection_qp
                loadProfile={loadProfile_qp}
                calculationResult={calculationResult_qp}
                parameters={parameters_qp}
              />
              
              <SchematicSection_qp
                calculationResult={calculationResult_qp}
                parameters={parameters_qp}
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

