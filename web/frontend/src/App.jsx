import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Hero from './components/Hero';
import DataInputSection from './components/DataInputSection';
import DataVisualizationSection from './components/DataVisualizationSection';
import BatteryInteractiveSection from './components/BatteryInteractiveSection';
import ChartsSection from './components/ChartsSection';
import SchematicSection from './components/SchematicSection';
import Footer from './components/Footer';
import { apiService } from './services/api';

function App() {
  const [loadProfile, setLoadProfile] = useState(null);
  const [parameters, setParameters] = useState({
    rated_power_mw: 500,
    rated_capacity_mwh: 2000,
    efficiency: 0.95,
  });
  const [calculationResult, setCalculationResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);

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

  return (
    <div className="min-h-screen">
      <Hero />
      
      <DataInputSection
        loadProfile={loadProfile}
        setLoadProfile={setLoadProfile}
        parameters={parameters}
        setParameters={setParameters}
        onCalculate={handleCalculate}
        isCalculating={isCalculating}
        error={error}
        setError={setError}
      />

      {loadProfile && (
        <>
          <DataVisualizationSection
            loadProfile={loadProfile}
          />
          
          <BatteryInteractiveSection
            loadProfile={loadProfile}
            parameters={parameters}
            setParameters={setParameters}
          />
        </>
      )}

      {calculationResult && (
        <>
          <ChartsSection
            loadProfile={loadProfile}
            calculationResult={calculationResult}
            parameters={parameters}
          />
          
          <SchematicSection
            calculationResult={calculationResult}
            parameters={parameters}
          />
        </>
      )}

      <Footer />
    </div>
  );
}

export default App;

