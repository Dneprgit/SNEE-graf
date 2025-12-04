"""
Главное окно приложения на PyQt6
"""
import sys
import os
from typing import List, Optional
import numpy as np
from dotenv import load_dotenv

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QGroupBox, QFileDialog, QMessageBox,
    QSplitter, QTextEdit, QGridLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QDoubleValidator, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

from energy_storage_calculator import EnergyStorageCalculator
from data_manager import DataManager
from visualization import ChartGenerator


class MainWindow(QMainWindow):
    """Главное окно приложения визуализации СНЭЭ"""
    
    def __init__(self):
        super().__init__()
        
        # Загрузка переменных окружения
        load_dotenv()
        
        # Параметры по умолчанию
        self.default_power = float(os.getenv('DEFAULT_INVERTER_POWER', '500'))
        self.default_capacity = float(os.getenv('DEFAULT_BATTERY_CAPACITY', '2000'))
        self.default_efficiency = float(os.getenv('DEFAULT_EFFICIENCY', '0.95'))
        
        # Данные
        self.load_profile = DataManager.get_default_profile()
        self.eess_schedule = None
        self.summary = None
        
        self.init_ui()
        self.calculate_and_update()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('СНЭЭ - Визуализация диспетчерского графика')
        
        # Размеры окна
        width = int(os.getenv('WINDOW_WIDTH', '1400'))
        height = int(os.getenv('WINDOW_HEIGHT', '900'))
        self.resize(width, height)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter для разделения на верхнюю и нижнюю части
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # === ВЕРХНЯЯ ЧАСТЬ: Параметры и таблицы ===
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Параметры СНЭЭ
        params_group = self._create_parameters_group()
        top_layout.addWidget(params_group)
        
        # Таблица исходных данных
        input_group = self._create_input_table_group()
        top_layout.addWidget(input_group)
        
        # Таблица результатов
        results_group = self._create_results_table_group()
        top_layout.addWidget(results_group)
        
        # Сводка
        summary_group = self._create_summary_group()
        top_layout.addWidget(summary_group)
        
        splitter.addWidget(top_widget)
        
        # === НИЖНЯЯ ЧАСТЬ: График ===
        chart_group = self._create_chart_group()
        splitter.addWidget(chart_group)
        
        # Установка пропорций
        splitter.setSizes([500, 400])
        
        main_layout.addWidget(splitter)
        
    def _create_parameters_group(self) -> QGroupBox:
        """Создание группы параметров СНЭЭ"""
        group = QGroupBox("Параметры СНЭЭ")
        layout = QHBoxLayout()
        
        # Валидатор для положительных чисел
        validator = QDoubleValidator(0.0, 999999.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        eff_validator = QDoubleValidator(0.01, 1.0, 3)
        eff_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        # Мощность инвертора
        layout.addWidget(QLabel("Мощность инвертора, МВт:"))
        self.power_input = QLineEdit(str(self.default_power))
        self.power_input.setValidator(validator)
        self.power_input.setMaximumWidth(100)
        self.power_input.textChanged.connect(self.on_parameters_changed)
        layout.addWidget(self.power_input)
        
        layout.addSpacing(20)
        
        # Емкость батареи
        layout.addWidget(QLabel("Емкость батареи, МВтч:"))
        self.capacity_input = QLineEdit(str(self.default_capacity))
        self.capacity_input.setValidator(validator)
        self.capacity_input.setMaximumWidth(100)
        self.capacity_input.textChanged.connect(self.on_parameters_changed)
        layout.addWidget(self.capacity_input)
        
        layout.addSpacing(20)
        
        # КПД
        layout.addWidget(QLabel("КПД трансформации:"))
        self.efficiency_input = QLineEdit(str(self.default_efficiency))
        self.efficiency_input.setValidator(eff_validator)
        self.efficiency_input.setMaximumWidth(100)
        self.efficiency_input.textChanged.connect(self.on_parameters_changed)
        layout.addWidget(self.efficiency_input)
        
        layout.addSpacing(20)
        
        # Кнопка пересчета
        calc_btn = QPushButton("Пересчитать")
        calc_btn.clicked.connect(self.calculate_and_update)
        calc_btn.setMaximumWidth(120)
        layout.addWidget(calc_btn)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _create_input_table_group(self) -> QGroupBox:
        """Создание группы с таблицей исходных данных"""
        group = QGroupBox("Исходные данные: Суточный баланс мощности в контролируемом сечении")
        layout = QVBoxLayout()
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("Импорт из Excel")
        import_btn.clicked.connect(self.import_from_excel)
        btn_layout.addWidget(import_btn)
        
        reset_btn = QPushButton("Сбросить к исходным")
        reset_btn.clicked.connect(self.reset_to_default)
        btn_layout.addWidget(reset_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Таблица
        self.input_table = QTableWidget(2, 24)
        self.input_table.setMaximumHeight(100)
        
        # Заголовки столбцов (часы)
        self.input_table.setHorizontalHeaderLabels([str(i) for i in range(1, 25)])
        self.input_table.setVerticalHeaderLabels(["Час", "Баланс, МВт"])
        
        # Настройка таблицы
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Заполнение первой строки (часы) - только для чтения
        for i in range(24):
            item = QTableWidgetItem(str(i + 1))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.input_table.setItem(0, i, item)
        
        # Заполнение второй строки (значения баланса)
        self._update_input_table()
        
        # Обработчик изменений
        self.input_table.cellChanged.connect(self.on_table_changed)
        
        layout.addWidget(self.input_table)
        
        group.setLayout(layout)
        return group
    
    def _create_results_table_group(self) -> QGroupBox:
        """Создание группы с таблицей результатов"""
        group = QGroupBox("Рассчитанные данные: Диспетчерский график работы СНЭЭ")
        layout = QVBoxLayout()
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        export_btn = QPushButton("Экспорт в Excel")
        export_btn.clicked.connect(self.export_to_excel)
        btn_layout.addWidget(export_btn)
        
        export_html_btn = QPushButton("Сохранить график HTML")
        export_html_btn.clicked.connect(self.export_chart_html)
        btn_layout.addWidget(export_html_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Таблица
        self.results_table = QTableWidget(3, 24)
        self.results_table.setMaximumHeight(120)
        
        # Заголовки
        self.results_table.setHorizontalHeaderLabels([str(i) for i in range(1, 25)])
        self.results_table.setVerticalHeaderLabels([
            "График СНЭЭ, МВт",
            "Результ. баланс, МВт",
            "SOC, МВтч"
        ])
        
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Все ячейки только для чтения
        for i in range(3):
            for j in range(24):
                item = QTableWidgetItem("")
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_table.setItem(i, j, item)
        
        layout.addWidget(self.results_table)
        
        group.setLayout(layout)
        return group
    
    def _create_summary_group(self) -> QGroupBox:
        """Создание группы со сводной информацией"""
        group = QGroupBox("Сводная информация")
        layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(120)
        
        font = QFont("Courier New", 9)
        self.summary_text.setFont(font)
        
        layout.addWidget(self.summary_text)
        
        group.setLayout(layout)
        return group
    
    def _create_chart_group(self) -> QGroupBox:
        """Создание группы с графиком"""
        group = QGroupBox("Интерактивная диаграмма")
        layout = QVBoxLayout()
        
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        group.setLayout(layout)
        return group
    
    def _update_input_table(self):
        """Обновление таблицы исходных данных"""
        self.input_table.blockSignals(True)
        
        for i in range(24):
            value = self.load_profile[i]
            item = QTableWidgetItem(f"{value:.1f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Цвет фона в зависимости от знака
            if value >= 0:
                item.setBackground(Qt.GlobalColor.white)
            else:
                item.setBackground(Qt.GlobalColor.lightGray)
            
            self.input_table.setItem(1, i, item)
        
        self.input_table.blockSignals(False)
    
    def _update_results_table(self):
        """Обновление таблицы результатов"""
        if self.eess_schedule is None:
            return
        
        soc = self._calculate_soc()
        
        for i in range(24):
            # График СНЭЭ
            eess_value = self.eess_schedule[i]
            item1 = QTableWidgetItem(f"{eess_value:.1f}")
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if eess_value > 0:
                item1.setBackground(Qt.GlobalColor.green)
            elif eess_value < 0:
                item1.setBackground(Qt.GlobalColor.cyan)
            
            self.results_table.setItem(0, i, item1)
            
            # Результирующий баланс
            result_balance = self.load_profile[i] + eess_value
            item2 = QTableWidgetItem(f"{result_balance:.1f}")
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if result_balance >= 0:
                item2.setBackground(Qt.GlobalColor.white)
            else:
                item2.setBackground(Qt.GlobalColor.yellow)
            
            self.results_table.setItem(1, i, item2)
            
            # SOC
            item3 = QTableWidgetItem(f"{soc[i]:.1f}")
            item3.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(2, i, item3)
    
    def _update_summary_text(self):
        """Обновление текста сводки"""
        if self.summary is None:
            return
        
        text = f"""
<b>Энергетические показатели:</b>
  Суммарный заряд:     {self.summary['total_charge_mwh']:>8.2f} МВтч
  Суммарный разряд:    {self.summary['total_discharge_mwh']:>8.2f} МВтч
  Макс. мощн. заряда:  {self.summary['max_charge_power_mw']:>8.2f} МВт
  Макс. мощн. разряда: {self.summary['max_discharge_power_mw']:>8.2f} МВт

<b>Покрытие дефицитов:</b>
  Дефицит до СНЭЭ:     {self.summary['deficit_before_mwh']:>8.2f} МВтч
  Дефицит после СНЭЭ:  {self.summary['deficit_after_mwh']:>8.2f} МВтч
  Покрыто:             {self.summary['deficit_covered_mwh']:>8.2f} МВтч ({self.summary['deficit_coverage_percent']:>5.1f}%)

<b>Использование избытков:</b>
  Избыток до СНЭЭ:     {self.summary['surplus_before_mwh']:>8.2f} МВтч
  Избыток после СНЭЭ:  {self.summary['surplus_after_mwh']:>8.2f} МВтч
  Использовано:        {self.summary['surplus_utilized_mwh']:>8.2f} МВтч ({self.summary['surplus_utilization_percent']:>5.1f}%)
"""
        
        self.summary_text.setHtml(f'<pre style="font-family: Courier New; font-size: 10pt;">{text}</pre>')
    
    def _calculate_soc(self) -> List[float]:
        """Расчет состояния заряда батареи"""
        capacity = self.get_capacity()
        soc = [0.0]
        
        for i in range(24):
            energy_change = -self.eess_schedule[i]
            new_soc = soc[-1] + energy_change
            new_soc = max(0, min(new_soc, capacity))
            soc.append(new_soc)
        
        return soc[1:]
    
    def get_power(self) -> float:
        """Получить значение мощности"""
        try:
            return float(self.power_input.text())
        except:
            return self.default_power
    
    def get_capacity(self) -> float:
        """Получить значение емкости"""
        try:
            return float(self.capacity_input.text())
        except:
            return self.default_capacity
    
    def get_efficiency(self) -> float:
        """Получить значение КПД"""
        try:
            return float(self.efficiency_input.text())
        except:
            return self.default_efficiency
    
    def calculate_and_update(self):
        """Выполнить расчет и обновить все элементы"""
        try:
            # Получение параметров
            power = self.get_power()
            capacity = self.get_capacity()
            efficiency = self.get_efficiency()
            
            # Расчет
            calculator = EnergyStorageCalculator(power, capacity, efficiency)
            self.eess_schedule = calculator.calculate_dispatch_schedule(self.load_profile)
            self.summary = calculator.get_summary(self.load_profile, self.eess_schedule)
            
            # Обновление UI
            self._update_results_table()
            self._update_summary_text()
            self._update_chart()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчета", f"Произошла ошибка при расчете:\n{str(e)}")
    
    def _update_chart(self):
        """Обновление графика"""
        try:
            power = self.get_power()
            capacity = self.get_capacity()
            efficiency = self.get_efficiency()
            
            fig = ChartGenerator.create_dispatch_chart(
                self.load_profile,
                self.eess_schedule,
                power,
                capacity,
                efficiency
            )
            
            html = fig.to_html(include_plotlyjs='cdn')
            self.web_view.setHtml(html)
            
        except Exception as e:
            print(f"Ошибка при обновлении графика: {e}")
    
    def on_parameters_changed(self):
        """Обработчик изменения параметров"""
        # Используем таймер для задержки пересчета при вводе
        if hasattr(self, '_calc_timer'):
            self._calc_timer.stop()
        
        self._calc_timer = QTimer()
        self._calc_timer.setSingleShot(True)
        self._calc_timer.timeout.connect(self.calculate_and_update)
        self._calc_timer.start(500)  # 500 мс задержка
    
    def on_table_changed(self, row: int, column: int):
        """Обработчик изменения значений в таблице"""
        if row != 1:  # Редактируем только строку с балансом
            return
        
        try:
            item = self.input_table.item(row, column)
            value = float(item.text())
            self.load_profile[column] = value
            
            # Обновляем цвет ячейки
            if value >= 0:
                item.setBackground(Qt.GlobalColor.white)
            else:
                item.setBackground(Qt.GlobalColor.lightGray)
            
            # Пересчитываем с задержкой
            self.on_parameters_changed()
            
        except ValueError:
            # Возвращаем старое значение при ошибке
            item = self.input_table.item(row, column)
            item.setText(f"{self.load_profile[column]:.1f}")
    
    def import_from_excel(self):
        """Импорт данных из Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Импорт из Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            data = DataManager.import_from_excel(file_path)
            
            if data is not None:
                self.load_profile = data
                self._update_input_table()
                self.calculate_and_update()
                QMessageBox.information(self, "Успех", "Данные успешно импортированы!")
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка импорта",
                    "Не удалось найти 24 числовых значения в файле.\n"
                    "Убедитесь, что данные находятся в одной строке или столбце."
                )
    
    def export_to_excel(self):
        """Экспорт результатов в Excel"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт в Excel",
            "snee_results.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            success = DataManager.export_to_excel(
                file_path,
                self.load_profile,
                self.eess_schedule,
                self.summary
            )
            
            if success:
                QMessageBox.information(self, "Успех", f"Результаты сохранены в:\n{file_path}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл")
    
    def export_chart_html(self):
        """Экспорт графика в HTML"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            "snee_chart.html",
            "HTML Files (*.html)"
        )
        
        if file_path:
            try:
                power = self.get_power()
                capacity = self.get_capacity()
                efficiency = self.get_efficiency()
                
                fig = ChartGenerator.create_dispatch_chart(
                    self.load_profile,
                    self.eess_schedule,
                    power,
                    capacity,
                    efficiency
                )
                
                success = ChartGenerator.save_chart_html(fig, file_path)
                
                if success:
                    QMessageBox.information(self, "Успех", f"График сохранен в:\n{file_path}")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось сохранить график")
                    
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{str(e)}")
    
    def reset_to_default(self):
        """Сброс данных к значениям по умолчанию"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите сбросить данные к исходным значениям?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.load_profile = DataManager.get_default_profile()
            self._update_input_table()
            self.calculate_and_update()

