"""
Калькулятор для расчета диспетчерского графика работы СНЭЭ
(Система Накопления Электрической Энергии)
"""
import numpy as np
from typing import List


class EnergyStorageCalculator:
    """
    Класс для расчета оптимального графика работы системы накопления энергии
    """
    
    def __init__(self, rated_power_mw: float, rated_capacity_mwh: float, efficiency: float):
        """
        Инициализация калькулятора
        
        Args:
            rated_power_mw: Номинальная мощность инвертора (МВт)
            rated_capacity_mwh: Номинальная емкость батареи (МВт·ч)
            efficiency: КПД цикла заряд-разряд (0-1)
        """
        if rated_power_mw <= 0:
            raise ValueError("Мощность должна быть положительной")
        if rated_capacity_mwh <= 0:
            raise ValueError("Емкость должна быть положительной")
        if not 0 < efficiency <= 1:
            raise ValueError("КПД должен быть в диапазоне (0, 1]")
            
        self.rated_power_mw = rated_power_mw
        self.rated_capacity_mwh = rated_capacity_mwh
        self.efficiency = efficiency
        
    def calculate_dispatch_schedule(self, load_profile: List[float]) -> np.ndarray:
        """
        Расчет диспетчерского графика работы СНЭЭ
        
        Алгоритм:
        - Положительные значения профиля = избыток энергии → заряд батареи (отрицательная мощность СНЭЭ)
        - Отрицательные значения профиля = дефицит энергии → разряд батареи (положительная мощность СНЭЭ)
        - Учет ограничений по мощности и емкости
        - Учет КПД при заряде/разряде
        
        Args:
            load_profile: Суточный профиль баланса мощности (24 значения)
            
        Returns:
            График работы СНЭЭ (+ разряд, - заряд)
        """
        if len(load_profile) != 24:
            raise ValueError(f"Профиль должен содержать 24 значения, получено: {len(load_profile)}")
        
        eess_schedule = np.zeros(24)
        soc = 0.0  # Начальное состояние заряда (МВт·ч)
        
        for hour in range(24):
            balance = load_profile[hour]
            
            if balance > 0:
                # Избыток энергии - нужен заряд (отрицательная мощность СНЭЭ)
                # Максимальная мощность заряда с учетом КПД
                max_charge_power = min(self.rated_power_mw, balance)
                
                # Максимальная энергия, которую можно принять с учетом свободного места
                available_capacity = self.rated_capacity_mwh - soc
                max_charge_energy = min(max_charge_power, available_capacity / self.efficiency)
                
                # Фактическая мощность заряда (отрицательная)
                charge_power = -max_charge_energy
                eess_schedule[hour] = charge_power
                
                # Обновление SOC с учетом КПД заряда
                soc += max_charge_energy * self.efficiency
                
            elif balance < 0:
                # Дефицит энергии - нужен разряд (положительная мощность СНЭЭ)
                deficit = abs(balance)
                
                # Максимальная мощность разряда
                max_discharge_power = min(self.rated_power_mw, deficit)
                
                # Максимальная энергия, которую можно отдать с учетом запаса
                max_discharge_energy = min(max_discharge_power, soc * self.efficiency)
                
                # Фактическая мощность разряда (положительная)
                discharge_power = max_discharge_energy
                eess_schedule[hour] = discharge_power
                
                # Обновление SOC с учетом КПД разряда
                soc -= max_discharge_energy / self.efficiency
            
            # Ограничение SOC в допустимых пределах
            soc = max(0, min(soc, self.rated_capacity_mwh))
        
        return eess_schedule
    
    def get_summary(self, load_profile: List[float], eess_schedule: np.ndarray) -> dict:
        """
        Получение сводной статистики по работе СНЭЭ
        
        Args:
            load_profile: Исходный профиль баланса
            eess_schedule: Рассчитанный график работы СНЭЭ
            
        Returns:
            Словарь с ключевыми показателями
        """
        # Разделение на заряд и разряд
        charge_schedule = eess_schedule[eess_schedule < 0]
        discharge_schedule = eess_schedule[eess_schedule > 0]
        
        # Энергетические показатели
        total_charge_energy = abs(np.sum(charge_schedule))  # МВт·ч
        total_discharge_energy = np.sum(discharge_schedule)  # МВт·ч
        
        # Пиковые значения
        max_charge_power = abs(np.min(eess_schedule)) if len(charge_schedule) > 0 else 0
        max_discharge_power = np.max(eess_schedule) if len(discharge_schedule) > 0 else 0
        
        # Результирующий баланс
        resulting_balance = np.array(load_profile) + eess_schedule
        
        # Анализ балансировки
        initial_peak_surplus = np.max(load_profile)
        initial_peak_deficit = abs(np.min(load_profile))
        final_peak_surplus = np.max(resulting_balance)
        final_peak_deficit = abs(np.min(resulting_balance))
        
        # Эффективность балансировки
        surplus_reduction = ((initial_peak_surplus - final_peak_surplus) / initial_peak_surplus * 100 
                           if initial_peak_surplus > 0 else 0)
        deficit_reduction = ((initial_peak_deficit - final_peak_deficit) / initial_peak_deficit * 100 
                           if initial_peak_deficit > 0 else 0)
        
        # Количество часов работы
        charge_hours = np.sum(eess_schedule < 0)
        discharge_hours = np.sum(eess_schedule > 0)
        idle_hours = 24 - charge_hours - discharge_hours
        
        # Коэффициент использования
        utilization = ((charge_hours + discharge_hours) / 24) * 100
        
        return {
            "energy": {
                "total_charge_mwh": round(total_charge_energy, 2),
                "total_discharge_mwh": round(total_discharge_energy, 2),
                "cycle_efficiency_percent": round((total_discharge_energy / total_charge_energy * 100) 
                                                if total_charge_energy > 0 else 0, 2)
            },
            "power": {
                "max_charge_mw": round(max_charge_power, 2),
                "max_discharge_mw": round(max_discharge_power, 2),
                "rated_power_mw": self.rated_power_mw
            },
            "balancing": {
                "initial_peak_surplus_mw": round(initial_peak_surplus, 2),
                "initial_peak_deficit_mw": round(initial_peak_deficit, 2),
                "final_peak_surplus_mw": round(final_peak_surplus, 2),
                "final_peak_deficit_mw": round(final_peak_deficit, 2),
                "surplus_reduction_percent": round(surplus_reduction, 2),
                "deficit_reduction_percent": round(deficit_reduction, 2)
            },
            "operation": {
                "charge_hours": int(charge_hours),
                "discharge_hours": int(discharge_hours),
                "idle_hours": int(idle_hours),
                "utilization_percent": round(utilization, 2)
            },
            "battery": {
                "rated_capacity_mwh": self.rated_capacity_mwh,
                "efficiency": self.efficiency
            }
        }

