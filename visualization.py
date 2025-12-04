"""
Модуль визуализации графиков с использованием Plotly
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List


class ChartGenerator:
    """Класс для генерации интерактивных графиков"""
    
    @staticmethod
    def create_dispatch_chart(load_profile: List[float], 
                             eess_schedule: np.ndarray,
                             rated_power: float,
                             rated_capacity: float,
                             efficiency: float) -> go.Figure:
        """
        Создание интерактивной диаграммы баланса и графика СНЭЭ
        
        Args:
            load_profile: Исходный профиль баланса мощности
            eess_schedule: График работы СНЭЭ
            rated_power: Номинальная мощность СНЭЭ
            rated_capacity: Емкость батареи
            efficiency: КПД
        
        Returns:
            Plotly Figure объект
        """
        hours = list(range(1, 25))
        resulting_balance = [load_profile[i] + eess_schedule[i] for i in range(24)]
        
        # Расчет состояния заряда батареи
        soc = ChartGenerator._calculate_soc(eess_schedule, rated_capacity)
        
        # Создание фигуры с двумя подграфиками
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=(
                'Суточный баланс мощности и график работы СНЭЭ',
                'Состояние заряда батареи (SOC)'
            ),
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # График 1: Баланс мощности
        # Исходный баланс (области избытка и дефицита)
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=load_profile,
                fill='tozeroy',
                fillcolor='rgba(255, 200, 200, 0.3)',
                line=dict(color='rgba(255, 100, 100, 0.5)', width=1, dash='dot'),
                name='Исходный баланс',
                hovertemplate='Час: %{x}<br>Баланс: %{y:.1f} МВт<extra></extra>',
                showlegend=True
            ),
            row=1, col=1
        )
        
        # График СНЭЭ (заряд и разряд отдельно)
        charge_values = [-v if v < 0 else 0 for v in eess_schedule]
        discharge_values = [v if v > 0 else 0 for v in eess_schedule]
        
        fig.add_trace(
            go.Bar(
                x=hours,
                y=discharge_values,
                name='Разряд СНЭЭ (выдача в сеть)',
                marker_color='rgba(50, 200, 50, 0.7)',
                hovertemplate='Час: %{x}<br>Разряд: %{y:.1f} МВт<extra></extra>',
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=hours,
                y=[-v for v in charge_values],
                name='Заряд СНЭЭ (потребление из сети)',
                marker_color='rgba(50, 100, 200, 0.7)',
                hovertemplate='Час: %{x}<br>Заряд: %{y:.1f} МВт<extra></extra>',
            ),
            row=1, col=1
        )
        
        # Результирующий баланс
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=resulting_balance,
                mode='lines+markers',
                line=dict(color='rgb(50, 50, 50)', width=2.5),
                marker=dict(size=6, symbol='circle'),
                name='Результирующий баланс',
                hovertemplate='Час: %{x}<br>Баланс: %{y:.1f} МВт<extra></extra>',
            ),
            row=1, col=1
        )
        
        # Нулевая линия
        fig.add_hline(y=0, line_dash="solid", line_color="black", 
                     line_width=1, row=1, col=1)
        
        # График 2: Состояние заряда батареи
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=soc,
                mode='lines+markers',
                line=dict(color='rgb(100, 50, 200)', width=2.5),
                marker=dict(size=6, symbol='diamond'),
                name='Заряд батареи',
                fill='tozeroy',
                fillcolor='rgba(100, 50, 200, 0.2)',
                hovertemplate='Час: %{x}<br>SOC: %{y:.1f} МВтч<extra></extra>',
            ),
            row=2, col=1
        )
        
        # Линия максимальной емкости
        fig.add_hline(y=rated_capacity, line_dash="dash", 
                     line_color="red", line_width=1.5,
                     annotation_text=f"Макс. емкость: {rated_capacity} МВтч",
                     annotation_position="right",
                     row=2, col=1)
        
        # Обновление осей
        fig.update_xaxes(
            title_text="Час",
            tickmode='linear',
            tick0=1,
            dtick=2,
            gridcolor='lightgray',
            showgrid=True,
            row=1, col=1
        )
        
        fig.update_yaxes(
            title_text="Мощность, МВт",
            gridcolor='lightgray',
            showgrid=True,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            row=1, col=1
        )
        
        fig.update_xaxes(
            title_text="Час",
            tickmode='linear',
            tick0=1,
            dtick=2,
            gridcolor='lightgray',
            showgrid=True,
            row=2, col=1
        )
        
        fig.update_yaxes(
            title_text="Энергия, МВтч",
            gridcolor='lightgray',
            showgrid=True,
            row=2, col=1
        )
        
        # Обновление макета
        fig.update_layout(
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            ),
            hovermode='x unified',
            plot_bgcolor='white',
            font=dict(size=11),
            margin=dict(l=60, r=30, t=100, b=50)
        )
        
        # Добавление аннотации с параметрами
        annotation_text = (
            f"Параметры СНЭЭ: Мощность = {rated_power} МВт, "
            f"Емкость = {rated_capacity} МВтч, КПД = {efficiency}"
        )
        fig.add_annotation(
            text=annotation_text,
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(size=10, color="gray"),
            xanchor="center"
        )
        
        return fig
    
    @staticmethod
    def _calculate_soc(eess_schedule: np.ndarray, rated_capacity: float) -> List[float]:
        """
        Расчет состояния заряда батареи в течение суток
        
        Args:
            eess_schedule: График работы СНЭЭ (+ разряд, - заряд)
            rated_capacity: Емкость батареи
        
        Returns:
            Список значений SOC для каждого часа
        """
        soc = [0.0]  # Начинаем с разряженной батареи
        
        for i in range(24):
            # Положительное значение = разряд (уменьшает SOC)
            # Отрицательное значение = заряд (увеличивает SOC)
            energy_change = -eess_schedule[i]  # Инвертируем знак
            new_soc = soc[-1] + energy_change
            
            # Ограничиваем в пределах [0, rated_capacity]
            new_soc = max(0, min(new_soc, rated_capacity))
            soc.append(new_soc)
        
        return soc[1:]  # Возвращаем без начального нуля
    
    @staticmethod
    def save_chart_html(fig: go.Figure, file_path: str) -> bool:
        """
        Сохранение графика в HTML файл
        
        Args:
            fig: Plotly Figure объект
            file_path: Путь для сохранения
        
        Returns:
            True при успехе
        """
        try:
            fig.write_html(file_path)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении графика: {e}")
            return False

