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
import TopNavigationStrip from './components/TopNavigationStrip';
import OtherTasksPage from './pages/OtherTasksPage';
import InputDataFaqPage from './pages/InputDataFaqPage';
import { apiService } from './services/api';

const getHashRoute = () => {
  if (typeof window === 'undefined') {
    return '/';
  }

  const rawHash = window.location.hash.replace(/^#/, '').trim();
  const route = rawHash.split('?')[0] || '/';

  return route.startsWith('/') ? route : `/${route}`;
};

function HomePage() {
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
    standby_load_mw: 0,
  });
  const [calculationResult_qp, setCalculationResult_qp] = useState(null);
  const [showBatterySection_qp, setShowBatterySection_qp] = useState(false);
  const [optimalParams_qp, setOptimalParams_qp] = useState(null);
  const [isCalculating_qp, setIsCalculating_qp] = useState(false);
  const [isCalculatingOptimal_qp, setIsCalculatingOptimal_qp] = useState(false);
  const [error_qp, setError_qp] = useState(null);
  const [optimalError_qp, setOptimalError_qp] = useState(null);
  const [qpDebugMode, setQpDebugMode] = useState(import.meta.env.VITE_QP_DEBUG_DEFAULT === 'true');
  const [scheduleDebugInfo_qp, setScheduleDebugInfo_qp] = useState(null);
  const [optimalDebugInfo_qp, setOptimalDebugInfo_qp] = useState(null);
  const [scheduleSolver_qp, setScheduleSolver_qp] = useState('linprog');
  const [activeParamsGroup_qp, setActiveParamsGroup_qp] = useState('factory');
  const [activeScheduleSolver_qp, setActiveScheduleSolver_qp] = useState(null);
  const [calculatingScheduleSolver_qp, setCalculatingScheduleSolver_qp] = useState(null);
  const [lastUsedParameters_qp, setLastUsedParameters_qp] = useState({
    dblNIn_pq: 115,
    dblNOut_pq: 145,
    dblCapacity_pq: 535,
    dblEfficiency_pq: 0.84,
    standby_load_mw: 0,
  });
  const [lastUsedParamsGroup_qp, setLastUsedParamsGroup_qp] = useState('factory');

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
  }, [
    parameters_qp.dblNIn_pq,
    parameters_qp.dblNOut_pq,
    parameters_qp.dblCapacity_pq,
    parameters_qp.dblEfficiency_pq,
    parameters_qp.standby_load_mw,
  ]);

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

  const handleCalculate_qp = async (overrideLoadProfile, solverOverride = null, paramsGroupOverride = null) => {
    const profile = Array.isArray(overrideLoadProfile) ? overrideLoadProfile : loadProfile_qp;
    const solverToUse = solverOverride || scheduleSolver_qp;
    const paramsGroupToUse = paramsGroupOverride || activeParamsGroup_qp;
    if (solverOverride) {
      setScheduleSolver_qp(solverOverride);
    }
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
    setCalculatingScheduleSolver_qp(solverToUse);
    setError_qp(null);

    try {
      const hasOptimalParams = Boolean(
        optimalParams_qp?.power_in && optimalParams_qp?.power_out && optimalParams_qp?.capacity
      );
      if (paramsGroupToUse === 'optimal' && !hasOptimalParams) {
        throw new Error('Оценочные параметры СНЭЭ недоступны. Выполните их расчет или переключитесь на заводские параметры.');
      }

      const paramsForCalculation = paramsGroupToUse === 'optimal'
        ? {
            dblNIn_pq: optimalParams_qp.power_in,
            dblNOut_pq: optimalParams_qp.power_out,
            dblCapacity_pq: optimalParams_qp.capacity,
            dblEfficiency_pq: parameters_qp.dblEfficiency_pq,
            standby_load_mw: parameters_qp.standby_load_mw,
          }
        : {
            dblNIn_pq: parameters_qp.dblNIn_pq,
            dblNOut_pq: parameters_qp.dblNOut_pq,
            dblCapacity_pq: parameters_qp.dblCapacity_pq,
            dblEfficiency_pq: parameters_qp.dblEfficiency_pq,
            standby_load_mw: parameters_qp.standby_load_mw,
          };

      const payload = {
        load_profile: profile,
        rated_input_power_mw: paramsForCalculation.dblNIn_pq,
        rated_output_power_mw: paramsForCalculation.dblNOut_pq,
        rated_capacity_mwh: paramsForCalculation.dblCapacity_pq,
        efficiency: paramsForCalculation.dblEfficiency_pq,
        standby_load_mw: paramsForCalculation.standby_load_mw,
        debug: qpDebugMode,
      };
      const result = solverToUse === 'highs_qp'
        ? await apiService.calculateSchedule_qp_highs(payload)
        : solverToUse === 'highs_qp_modified'
          ? await apiService.calculateSchedule_qp_highs_modified(payload)
          : await apiService.calculateSchedule_qp(payload);
      setCalculationResult_qp(result);
      setScheduleDebugInfo_qp(result?.debug_info || null);
      setActiveScheduleSolver_qp(solverToUse);
      setLastUsedParameters_qp(paramsForCalculation);
      setLastUsedParamsGroup_qp(paramsGroupToUse);
    } catch (err) {
      console.error('Calculation error:', err);
      setError_qp(err.response?.data?.detail || err.message || 'Ошибка при расчете графика');
      setScheduleDebugInfo_qp(null);
    } finally {
      setIsCalculating_qp(false);
      setCalculatingScheduleSolver_qp(null);
    }
  };

  const handleActivateParamsGroup_qp = async (group) => {
    setActiveParamsGroup_qp(group);
    if (!loadProfile_qp || loadProfile_qp.length !== 24) {
      return;
    }
    const solverToUse = activeScheduleSolver_qp || scheduleSolver_qp || 'linprog';
    await handleCalculate_qp(undefined, solverToUse, group);
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
        debug: qpDebugMode,
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
      setOptimalDebugInfo_qp(result?.debug_info || null);
    } catch (err) {
      console.error('Optimal calculation error:', err);
      setOptimalError_qp(err.response?.data?.detail || 'Ошибка при расчете оценочных параметров');
      setOptimalDebugInfo_qp(null);
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
      <TopNavigationStrip currentPage="home" />
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
              debugMode={qpDebugMode}
              setDebugMode={setQpDebugMode}
              optimalDebugInfo={optimalDebugInfo_qp}
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
              onCalculateScheduleLinprog={() => handleCalculate_qp(undefined, 'linprog')}
              onCalculateScheduleHighs={() => handleCalculate_qp(undefined, 'highs_qp')}
              onCalculateScheduleHighsModified={() => handleCalculate_qp(undefined, 'highs_qp_modified')}
              isCalculatingSchedule={isCalculating_qp}
              activeParamsGroup={activeParamsGroup_qp}
              onActivateFactoryParams={() => handleActivateParamsGroup_qp('factory')}
              onActivateOptimalParams={() => handleActivateParamsGroup_qp('optimal')}
              hasOptimalParams={Boolean(optimalParams_qp?.power_in && optimalParams_qp?.power_out && optimalParams_qp?.capacity)}
              activeScheduleSolver={activeScheduleSolver_qp}
              calculatingScheduleSolver={calculatingScheduleSolver_qp}
              scheduleError={error_qp}
              debugMode={qpDebugMode}
              scheduleDebugInfo={scheduleDebugInfo_qp}
              optimalDebugInfo={optimalDebugInfo_qp}
            />
          )}

          {calculationResult_qp && (
            <>
              <ChartsSection_qp
                loadProfile={loadProfile_qp}
                calculationResult={calculationResult_qp}
                parameters={lastUsedParameters_qp}
                scheduleSolver={activeScheduleSolver_qp}
                paramsGroup={lastUsedParamsGroup_qp}
              />
              
              <SchematicSection_qp
                calculationResult={calculationResult_qp}
                parameters={lastUsedParameters_qp}
              />
            </>
          )}
        </>
      )}

      <Footer />
    </div>
  );
}

function App() {
  const [route, setRoute] = useState(getHashRoute);

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(getHashRoute());
    };

    if (!window.location.hash) {
      window.location.hash = '/';
    }

    window.addEventListener('hashchange', handleHashChange);

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  if (route === '/other-tasks') {
    return <OtherTasksPage />;
  }

  if (route === '/input-data-faq') {
    return <InputDataFaqPage />;
  }

  return <HomePage />;
}

export default App;

