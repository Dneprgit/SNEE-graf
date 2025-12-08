"""
Менеджер данных для работы с профилями нагрузки
"""
import pandas as pd
import numpy as np
from typing import List, Optional


class DataManager:
    """
    Класс для управления данными профилей баланса мощности
    """
    
    @staticmethod
    def get_default_profile() -> List[float]:
        """
        Получить профиль баланса мощности по умолчанию
        
        Профиль из примера задания (24 часа)
        Положительные значения = избыток энергии (нужен заряд)
        Отрицательные значения = дефицит энергии (нужен разряд)
        
        Returns:
            Список из 24 значений баланса мощности (МВт)
        """
        return [
            1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
            -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
            -638, -370, 59, 963
        ]
    
    @staticmethod
    def import_from_excel(filepath: str) -> Optional[List[float]]:
        """
        Импорт профиля баланса из Excel файла
        
        Файл может содержать данные в строке или столбце.
        Функция ищет первые 24 числовых значения.
        
        Args:
            filepath: Путь к Excel файлу
            
        Returns:
            Список из 24 значений или None при ошибке
        """
        try:
            # Чтение Excel файла
            df = pd.read_excel(filepath, header=None)
            
            # Попытка найти 24 числовых значения
            values = []
            
            # Поиск по строкам
            for row_idx in range(len(df)):
                row_values = []
                for col_idx in range(len(df.columns)):
                    val = df.iloc[row_idx, col_idx]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        row_values.append(float(val))
                
                if len(row_values) >= 24:
                    return row_values[:24]
                elif len(row_values) > 0:
                    values.extend(row_values)
                    if len(values) >= 24:
                        return values[:24]
            
            # Поиск по столбцам
            for col_idx in range(len(df.columns)):
                col_values = []
                for row_idx in range(len(df)):
                    val = df.iloc[row_idx, col_idx]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        col_values.append(float(val))
                
                if len(col_values) >= 24:
                    return col_values[:24]
            
            # Если не нашли 24 значения
            return None
            
        except Exception as e:
            print(f"Ошибка при чтении Excel файла: {e}")
            return None
    
    @staticmethod
    def export_to_excel(filepath: str, load_profile: List[float], 
                       eess_schedule: List[float], resulting_balance: List[float],
                       soc: List[float]) -> bool:
        """
        Экспорт результатов расчета в Excel файл
        
        Args:
            filepath: Путь для сохранения файла
            load_profile: Исходный профиль баланса
            eess_schedule: График работы СНЭЭ
            resulting_balance: Результирующий баланс
            soc: Состояние заряда батареи
            
        Returns:
            True при успехе, False при ошибке
        """
        try:
            # Создание DataFrame
            hours = list(range(1, 25))
            df = pd.DataFrame({
                'Час': hours,
                'Баланс мощности (МВт)': load_profile,
                'График СНЭЭ (МВт)': eess_schedule,
                'Результирующий баланс (МВт)': resulting_balance,
                'SOC (МВт·ч)': soc
            })
            
            # Сохранение в Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Результаты', index=False)
                
                # Форматирование
                worksheet = writer.sheets['Результаты']
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
    def validate_profile(load_profile: List[float]) -> tuple[bool, Optional[str]]:
        """
        Валидация профиля баланса мощности
        
        Args:
            load_profile: Профиль для проверки
            
        Returns:
            Кортеж (валиден, сообщение об ошибке)
        """
        if not isinstance(load_profile, list):
            return False, "Профиль должен быть списком"
        
        if len(load_profile) != 24:
            return False, f"Профиль должен содержать 24 значения, получено: {len(load_profile)}"
        
        try:
            arr = np.array(load_profile, dtype=float)
            
            if not np.all(np.isfinite(arr)):
                return False, "Профиль содержит некорректные значения (NaN или Infinity)"
            
            return True, None
            
        except (ValueError, TypeError) as e:
            return False, f"Ошибка при валидации: {str(e)}"

