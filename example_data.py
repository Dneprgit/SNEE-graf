"""
Скрипт для создания примера Excel файла с данными
"""
import pandas as pd
from data_manager import DataManager


def create_example_excel():
    """Создание примера Excel файла"""
    
    # Данные по умолчанию
    load_profile = DataManager.get_default_profile()
    hours = list(range(1, 25))
    
    # Создание DataFrame
    df = pd.DataFrame({
        'Час': hours,
        'Баланс мощности, МВт': load_profile
    })
    
    # Сохранение в Excel
    file_path = 'example_balance.xlsx'
    df.to_excel(file_path, index=False, sheet_name='Баланс')
    
    print(f"Пример Excel файла создан: {file_path}")
    print("\nДанные:")
    print(df)


if __name__ == '__main__':
    create_example_excel()

