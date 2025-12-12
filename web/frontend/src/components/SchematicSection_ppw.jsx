import { motion } from 'framer-motion';
import { Battery, Zap, ArrowRight, ArrowLeft } from 'lucide-react';

const SchematicSection_ppw = ({ calculationResult, parameters }) => {
  const maxCharge = calculationResult?.summary?.max_charge_power_mw || 0;
  const maxDischarge = calculationResult?.summary?.max_discharge_power_mw || 0;

  return (
    <motion.section
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="section-container py-12"
    >
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-center">Схема потоков энергии (PPW)</h2>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-between">
            {/* Энергосистема */}
            <div className="flex flex-col items-center">
              <Zap className="w-16 h-16 text-blue-500 mb-2" />
              <div className="text-lg font-semibold">Энергосистема</div>
            </div>

            {/* Стрелки */}
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-2">
                <ArrowRight className="w-8 h-8 text-red-500" />
                <span className="text-sm">Заряд: {maxCharge.toFixed(1)} МВт</span>
              </div>
              <div className="flex items-center gap-2">
                <ArrowLeft className="w-8 h-8 text-green-500" />
                <span className="text-sm">Разряд: {maxDischarge.toFixed(1)} МВт</span>
              </div>
            </div>

            {/* СНЭЭ Батарея */}
            <div className="flex flex-col items-center">
              <Battery className="w-16 h-16 text-green-500 mb-2" />
              <div className="text-lg font-semibold">СНЭЭ</div>
              <div className="text-sm text-gray-600">
                {parameters.working_range_energy_mwh.toFixed(0)} МВтч
              </div>
            </div>
          </div>

          {/* Показатели */}
          <div className="mt-8 grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Входная мощность</div>
              <div className="text-lg font-bold">{parameters.rated_power_in_mw} МВт</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Выходная мощность</div>
              <div className="text-lg font-bold">{parameters.rated_power_out_mw} МВт</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">КПД цикла</div>
              <div className="text-lg font-bold">{(parameters.efficiency * 100).toFixed(0)}%</div>
            </div>
          </div>
        </div>
      </div>
    </motion.section>
  );
};

export default SchematicSection_ppw;

