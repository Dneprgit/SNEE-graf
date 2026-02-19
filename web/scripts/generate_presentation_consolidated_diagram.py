"""
Презентация-диаграмма: сводка исследований из PRESENTATION_FOR_USERS и PRESENTATION_OPTIMIZATION_SIMPLE.
1–3 слайда, схематичная диаграмма, интеграция с лендингом.
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR_TYPE


def add_text_box(slide, left, top, width, height, text, font_size=10, bold=False):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.name = "Calibri"
    return tb


def add_rounded_rect(slide, left, top, width, height, fill_rgb=None):
    sh = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    if fill_rgb:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor(*fill_rgb)
    sh.line.color.rgb = RGBColor(70, 70, 70)
    return sh


def add_connector(slide, x1, y1, x2, y2):
    c = slide.shapes.add_connector(
        MSO_CONNECTOR_TYPE.STRAIGHT,
        Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    c.line.color.rgb = RGBColor(80, 80, 80)
    return c


def main():
    output_path = Path(__file__).resolve().parents[1] / "PRESENTATION_CONSOLIDATED_DIAGRAM.pptx"
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ========== СЛАЙД 1: Полная схема ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Hero / лендинг (верх)
    add_rounded_rect(slide, 0.3, 0.15, 12.7, 1.0, (59, 89, 152))  # primary-800
    add_text_box(slide, 0.5, 0.25, 3, 0.4, "СНЭЭ Graf", 22, True)
    add_text_box(slide, 0.5, 0.55, 12, 0.35, "Визуализация диспетчерского графика • Оптимизация СНЭЭ • Интерактивные графики • SVG", 11)
    add_text_box(slide, 0.5, 0.85, 12, 0.2, "Система накопления электрической энергии | Линейная оптимизация (LP, HiGHS)", 9)

    # Блок ввода
    add_rounded_rect(slide, 0.5, 1.4, 3.5, 1.2, (240, 248, 255))
    add_text_box(slide, 0.6, 1.45, 3.3, 0.4, "Ввод данных", 12, True)
    add_text_box(slide, 0.6, 1.85, 3.3, 0.65, "Профиль 24 ч (Excel / по умолч.)\nNin, Nout, C, КПД η\nРедакт. графика, смещение", 9)

    # Блок шаг 1
    add_rounded_rect(slide, 4.5, 1.4, 4.2, 1.2, (230, 255, 230))
    add_text_box(slide, 4.6, 1.45, 4, 0.4, "Шаг 1: LP-оптимизация параметров", 11, True)
    add_text_box(slide, 4.6, 1.85, 4, 0.65, "linprog → Nin, Nout, C, Dmax\nmin дефицит, учёт η\nКПД в ограничениях CC/η", 9)

    # Блок шаг 2
    add_rounded_rect(slide, 9.2, 1.4, 3.8, 1.2, (255, 248, 220))
    add_text_box(slide, 9.3, 1.45, 3.6, 0.4, "Шаг 2: LP-график", 11, True)
    add_text_box(slide, 9.3, 1.85, 3.6, 0.65, "Заданные Nin,Nout,C →\nзаряд/разряд по часам\nSOC, результ. баланс", 9)

    # Стрелки
    add_connector(slide, 4.0, 2.0, 4.5, 2.0)
    add_connector(slide, 8.7, 2.0, 9.2, 2.0)

    # Блок вывода
    add_rounded_rect(slide, 4.5, 2.9, 4.2, 1.1, (255, 240, 245))
    add_text_box(slide, 4.6, 2.95, 4, 0.4, "Результат", 12, True)
    add_text_box(slide, 4.6, 3.3, 4, 0.6, "Диспетч. график • SOC • KPI\nПокрытие дефицита • Использ. избытка • Excel", 9)

    add_connector(slide, 6.6, 2.6, 6.6, 2.9)
    add_connector(slide, 4.0, 2.55, 4.5, 2.9)
    add_connector(slide, 9.2, 2.55, 9.5, 2.9)
    add_connector(slide, 9.5, 2.9, 6.6, 2.9)

    # Интерактивность (справа)
    add_rounded_rect(slide, 0.5, 2.9, 3.5, 1.1, (245, 245, 255))
    add_text_box(slide, 0.6, 2.95, 3.3, 0.4, "Интерактивность", 11, True)
    add_text_box(slide, 0.6, 3.3, 3.3, 0.6, "Drag-точки графика\nСмещение профиля\nSVG-батарея (маркеры)", 9)
    add_connector(slide, 4.0, 2.55, 4.0, 3.45)
    add_connector(slide, 4.0, 3.45, 4.5, 3.45)

    # Ключевые факты (низ)
    add_text_box(slide, 0.5, 4.2, 12.5, 0.5, "• LP (не QP): scipy.optimize.linprog, HiGHS  • Два шага: параметры → график  • η в ограничениях: CC/η", 10)
    add_text_box(slide, 0.5, 4.7, 12.5, 0.5, "• Допущения: 24ч, шаг 1ч, без деградации, цикл замкнут  • Ровные участки / пики — из оптимума", 10)
    add_text_box(slide, 0.5, 5.2, 12.5, 0.5, "Сценарий: Профиль → Оценоч. парам. → Применить → График → KPI → Excel", 9)
    add_text_box(slide, 0.5, 5.65, 12.5, 0.55, "Сводка: PRESENTATION_FOR_USERS + PRESENTATION_OPTIMIZATION_SIMPLE | 1 слайд, схематичная диаграмма", 8)

    prs.save(str(output_path))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
