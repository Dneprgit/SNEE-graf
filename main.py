"""
Главный файл приложения СНЭЭ
Визуализация диспетчерского графика работы системы накопления электрической энергии
"""
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    app.setApplicationName("СНЭЭ - Визуализация")
    app.setOrganizationName("Energy Storage")
    
    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

