"""
Модуль управления данными: импорт/экспорт Excel
"""
import pandas as pd
import numpy as np
from typing import List, Optional
from pathlib import Path


class DataManager:
    """Класс для работы с данными СНЭЭ"""
    
    HOURS = 24
    
    @staticmethod
    def import_from_excel(file_path: str) -> Optional[List[float]]:
        """
        Импорт профиля баланса из Excel файла
        
        Args:
            file_path: Путь к Excel файлу
        
        Returns:
            Список из 24 значений или None при ошибке
        """
        try:
            df = pd.read_excel(file_path, header=None)
            
            # Ищем строку или столбец с 24 числовыми значениями
            data = None
            
            # Проверяем строки
            for idx in range(min(10, len(df))):
                row = df.iloc[idx]
                numeric_values = pd.to_numeric(row, errors='coerce').dropna()
                if len(numeric_values) == DataManager.HOURS:
                    data = numeric_values.tolist()
                    break
            
            # Проверяем столбцы, если в строках не нашли
            if data is None:
                for col in df.columns[:10]:
                    column = df[col]
                    numeric_values = pd.to_numeric(column, errors='coerce').dropna()
                    if len(numeric_values) == DataManager.HOURS:
                        data = numeric_values.tolist()
                        break
            
            return data
            
        except Exception as e:
            print(f"Ошибка при импорте из Excel: {e}")
            return None
    
    @staticmethod
    def export_to_excel(file_path: str, load_profile: List[float], 
                       eess_schedule: np.ndarray, summary: dict) -> bool:
        """
        Экспорт результатов в Excel файл
        
        Args:
            file_path: Путь для сохранения
            load_profile: Исходный профиль баланса
            eess_schedule: График работы СНЭЭ
            summary: Сводная информация
        
        Returns:
            True при успехе, False при ошибке
        """
        try:
            hours = list(range(1, DataManager.HOURS + 1))
            resulting_balance = [load_profile[i] + eess_schedule[i] 
                               for i in range(DataManager.HOURS)]
            
            # Создание DataFrame с основными данными
            df_data = pd.DataFrame({
                'Час': hours,
                'Баланс мощности, МВт': load_profile,
                'График СНЭЭ, МВт': eess_schedule,
                'Результирующий баланс, МВт': resulting_balance
            })
            
            # Создание DataFrame со сводкой
            summary_data = {
                'Показатель': [
                    'Суммарный заряд, МВтч',
                    'Суммарный разряд, МВтч',
                    'Макс. мощность заряда, МВт',
                    'Макс. мощность разряда, МВт',
                    'Дефицит до СНЭЭ, МВтч',
                    'Дефицит после СНЭЭ, МВтч',
                    'Покрытый дефицит, МВтч',
                    'Покрытие дефицита, %',
                    'Избыток до СНЭЭ, МВтч',
                    'Избыток после СНЭЭ, МВтч',
                    'Использованный избыток, МВтч',
                    'Использование избытка, %',
                    'Макс. дефицит результирующий, МВт',
                    'Макс. избыток результирующий, МВт',
                ],
                'Значение': [
                    summary['total_charge_mwh'],
                    summary['total_discharge_mwh'],
                    summary['max_charge_power_mw'],
                    summary['max_discharge_power_mw'],
                    summary['deficit_before_mwh'],
                    summary['deficit_after_mwh'],
                    summary['deficit_covered_mwh'],
                    summary['deficit_coverage_percent'],
                    summary['surplus_before_mwh'],
                    summary['surplus_after_mwh'],
                    summary['surplus_utilized_mwh'],
                    summary['surplus_utilization_percent'],
                    summary['resulting_max_deficit_mw'],
                    summary['resulting_max_surplus_mw'],
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            
            # Запись в Excel с двумя листами
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_data.to_excel(writer, sheet_name='Данные', index=False)
                df_summary.to_excel(writer, sheet_name='Сводка', index=False)
                
                # Форматирование столбцов
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return True
            
        except Exception as e:
            print(f"Ошибка при экспорте в Excel: {e}")
            return False
    
    @staticmethod
    def get_default_profile() -> List[float]:
        """Возвращает профиль по умолчанию из задания"""
        return [
            1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
            -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
            -638, -370, 59, 963
        ]

