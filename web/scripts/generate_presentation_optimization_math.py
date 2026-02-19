"""
Генерация третьей презентации: чистая математика оптимизации СНЭЭ.
Итерации решения, формулировка LP, используемые библиотеки.
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Pt


def set_run_font(run, size=24, bold=False):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold


def add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle

    title_run = slide.shapes.title.text_frame.paragraphs[0].runs[0]
    set_run_font(title_run, size=36, bold=True)

    subtitle_run = slide.placeholders[1].text_frame.paragraphs[0].runs[0]
    set_run_font(subtitle_run, size=20)


def add_bullet_slide(prs, title, bullets):
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title

    title_run = slide.shapes.title.text_frame.paragraphs[0].runs[0]
    set_run_font(title_run, size=28, bold=True)

    tf = slide.shapes.placeholders[1].text_frame
    tf.clear()

    for idx, item in enumerate(bullets):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        if isinstance(item, tuple):
            text, level = item
            p.text = text
            p.level = level
        else:
            p.text = item
            p.level = 0

        if p.runs:
            set_run_font(p.runs[0], size=18)


def main():
    output_path = (
        Path(__file__).resolve().parents[1]
        / "PRESENTATION_OPTIMIZATION_MATH.pptx"
    )

    prs = Presentation()

    add_title_slide(
        prs,
        "Математика оптимизации СНЭЭ",
        "Линейная оптимизация: переменные, ограничения, итерации решения",
    )

    add_bullet_slide(
        prs,
        "Стандартная форма задачи LP",
        [
            "Минимизировать: c₁x₁ + c₂x₂ + ... + cₙxₙ",
            "При ограничениях:",
            ("A_eq · x = b_eq (равенства)", 1),
            ("A_ub · x ≤ b_ub (неравенства)", 1),
            ("lb ≤ x ≤ ub (границы переменных)", 1),
            "Переменные x неотрицательны",
        ],
    )

    add_bullet_slide(
        prs,
        "Две LP-задачи в коде",
        [
            "Задача A (100 переменных): подбор Nin, Nout, C, Dmax",
            "Задача B (98 переменных): график при заданных Nin, Nout, C",
            "В обеих — 24 уравнения баланса и десятки неравенств",
        ],
    )

    add_bullet_slide(
        prs,
        "Переменные (Задача A)",
        [
            "L[i] — энергия в батарее в конце часа i (SOC)",
            "CC[i] — мощность заряда в час i (приведённая к выходу)",
            "CD[i] — мощность разряда в час i",
            "D[i] — остаточный дефицит мощности",
            "Dmax, Nin, Nout, C — скалярные параметры",
        ],
    )

    add_bullet_slide(
        prs,
        "Целевая функция (минимизация)",
        [
            "F = Σ(D[i])·w_d + Dmax·w_dmax + Nin·w_n + Nout·w_n + C·w_c",
            "Самый большой вес — у Dmax (главная цель)",
            "Остальные веса уменьшают «раздувание» системы",
        ],
    )

    add_bullet_slide(
        prs,
        "Ограничение-равенство: баланс энергии",
        [
            "L[i] − L[i−1] − CC[i] + CD[i] = 0",
            "Для i=0: L[0] − L[23] − CC[0] + CD[0] = 0 (цикл суток)",
            "Изменение запаса = разряд минус заряд",
        ],
    )

    add_bullet_slide(
        prs,
        "Ограничения-неравенства (смысл)",
        [
            "rD: CC[i]/η − CD[i] − D[i] ≤ −Load[i] — баланс мощности, учёт КПД",
            "rC: L[i] ≤ C — запас не выше ёмкости",
            "rNi: CC[i]/η ≤ Nin — лимит мощности заряда",
            "rNo: CD[i] ≤ Nout — лимит мощности разряда",
            "rDmax: D[i] ≤ Dmax — пик дефицита",
        ],
    )

    add_bullet_slide(
        prs,
        "КПД η в формулах",
        [
            "η входит в коэффициенты при CC[i]: член CC[i]/η",
            "Чем ниже КПД — тем больше нужна CC при той же полезной энергии",
            "Ограничения автоматически ужесточаются при малом η",
        ],
    )

    add_bullet_slide(
        prs,
        "Как работает симплекс-метод (итерации)",
        [
            "Ограничения задают многогранник, оптимум — в вершине",
            "Базис: часть переменных «активна», остальные — нули",
            "Шаг: переход в соседнюю вершину (смена базиса)",
            "Цель шага — уменьшить целевую функцию",
            "Остановка, когда улучшение невозможно",
        ],
    )

    add_bullet_slide(
        prs,
        "Метод внутренней точки (альтернатива)",
        [
            "Решение движется внутри допустимой области",
            "На каждой итерации — линеаризация (Ньютон)",
            "Часто быстрее на больших задачах",
            "HiGHS поддерживает оба подхода",
        ],
    )

    add_bullet_slide(
        prs,
        "Библиотеки: NumPy",
        [
            "Хранение векторов c, b и матриц A_eq, A_ub",
            "Формирование bounds для каждой переменной",
            "Обработка результата (вектор x)",
        ],
    )

    add_bullet_slide(
        prs,
        "Библиотеки: SciPy и HiGHS",
        [
            "SciPy: linprog(c, A_ub, b_ub, A_eq, b_eq, bounds, method='highs')",
            "HiGHS: встроенный LP-солвер в SciPy (C++)",
            "Лицензия MIT, без внешних зависимостей",
        ],
    )

    add_bullet_slide(
        prs,
        "Извлечение результата из x",
        [
            "x[0..23] = L[i], x[24..47] = CC[i], x[48..71] = CD[i]",
            "График СНЭЭ: EESSLoad[i] = CD[i] − CC[i]/η",
            "Проверка: Σ(CC[i] − CD[i]) ≈ 0 (баланс заряда и разряда)",
        ],
    )

    prs.save(str(output_path))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
