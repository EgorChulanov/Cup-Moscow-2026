"""Financial model for the T-Bank support case: builds an .xlsx with live formulas,
recalculates it with LibreOffice and exports the key numbers for the deck.

Usage: python3 model/build_model.py
Out:   model/out/CupMoscow2026-Т-Банк-<TEAM>.xlsx, model/out/numbers.json
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HERE = Path(__file__).parent
OUT = HERE / "out"
TEAM = os.environ.get("TEAM", "Команда")

YELLOW = PatternFill("solid", fgColor="FFDD2D")
INPUT = PatternFill("solid", fgColor="FFF6C2")
GREY = PatternFill("solid", fgColor="F2F3F5")
BOLD = Font(bold=True)
RUB = '#,##0 "₽"'
NUM = "#,##0"
PCT = "0.0%"

# Inputs: (key, label, value, format, source). Yellow cells in the sheet are editable.
INPUTS = [
    ("contacts", "Обращений в поддержку в месяц", 18_000_000, NUM, "Кейс, с. 7"),
    ("ai_share", "Доля обращений, которые закрывает ИИ", 0.45, PCT, "Кейс, с. 7"),
    ("human", "Обращений к специалисту в месяц", "=contacts*(1-ai_share)", NUM, "Расчёт"),
    ("hard_share", "Доля сложных ситуаций среди обращений к специалисту", 0.15, PCT,
     "Допущение. Ориентир: 24,7% жалоб в ЦБ о блокировках и отказах (ЦБ, 2025), но жалоба уже крайний случай"),
    ("hard_year", "Сложных обращений в год", "=human*hard_share*12", NUM, "Расчёт"),
    ("fcr_hard", "Решено с первого обращения в сложных ситуациях сейчас", 0.55, PCT,
     "Допущение. Средний FCR по отраслям 69% (SQM); в сложных ниже. Синтетический опрос: 9 из 20"),
    ("repeats", "Повторных контактов на одно нерешённое обращение", 1.5, "0.0",
     "Допущение. Интервью: от 2 до 6 обращений (синтетические)"),
    ("cost", "Стоимость обращения к специалисту", 274, RUB,
     "research/02, п. 2.3: 205-343 ₽, среднее"),
    ("ai_cost", "Стоимость обращения, закрытого ИИ", 30, RUB,
     "Допущение. Gartner: самообслуживание $0,10 против $8,01 за живой канал"),
    ("profit", "Операционная прибыль на активного клиента в год", 5220, RUB,
     "research/02, п. 2.1: 174,4 млрд ₽ / 33,4 млн активных клиентов, 2025"),
    ("leave_bad", "Намерение уйти, если вопрос не решён", 0.25, PCT, "SQM Group"),
    ("leave_good", "Намерение уйти, если решён с первого обращения", 0.05, PCT, "SQM Group"),
    ("convert", "Доля намерения, которая превращается в уход", 0.25, PCT,
     "Допущение, консервативно; в чувствительности 10-50%"),
    ("cases_per_client", "Сложных обращений на одного клиента в год", 1.3, "0.0", "Допущение"),
    ("hour", "Стоимость часа специалиста с налогами и накладными", 823, RUB,
     "research/02, п. 2.3: (101,6 + 169,9 тыс. ₽) / 2 / 165 ч"),
    ("staff", "Специалистов поддержки", 20_000, NUM, "Кейс, с. 7"),
]

# Options compared on one structure. Costs in rubles, effects as shares.
OPTIONS = [
    ("O1", "Стандарты и скрипты", "Обновить шаблоны ответов и чек-лист контроля качества",
     dict(fix=0.0, once=15e6, yearly=10e6, d_fcr=0.01, aht=0.0, ai=0.0, comp_share=0.0, comp_avg=0)),
    ("O2", "Тренинг эмпатии для всех", "8 часов soft skills для 20 тыс. специалистов, раз в год повтор",
     dict(fix=0.0, once="=staff*8*hour+20000000", yearly=50e6, d_fcr=0.03, aht=0.02, ai=0.0, comp_share=0.0, comp_avg=0)),
    ("O3", "ИИ решает сложные случаи сам", "Афанасий автономно ведёт часть сложных диалогов",
     dict(fix=0.0, once=300e6, yearly=60e6, d_fcr=-0.03, aht=0.0, ai=0.10, comp_share=0.0, comp_avg=0)),
    ("O4", "Пять шагов и подсказки", "5 типов ситуаций, 5 шагов, подсказки в рабочем окне, карточка случая, ответственный",
     dict(fix=0.0, once="=staff*4*hour+105000000", yearly=40e6, d_fcr=0.08, aht=0.05, ai=0.0, comp_share=0.0, comp_avg=0)),
    ("O5", "Компенсации без согласования", "До 3 000 ₽ любому недовольному клиенту",
     dict(fix=0.0, once=10e6, yearly=5e6, d_fcr=0.05, aht=0.0, ai=0.0, comp_share=0.10, comp_avg=1500)),
    ("REC", "Наш выбор: пять шагов, возврат до порога и сигнал в продукт",
     "O4 плюс жест доброй воли по порогу для типов «Несправедливо» и «Снова», шаблон-обоснование",
     dict(fix=0.02, once="=staff*4*hour+115000000", yearly=45e6, d_fcr=0.10, aht=0.05, ai=0.0, comp_share=0.02, comp_avg=600)),
]

# Qualitative comparison: factor, weight, scores per option (1..5), short reason
FACTORS = [
    ("Решение с первого обращения (меньше повторов)", 0.25, [2, 3, 1, 4, 3, 5]),
    ("Ощущение «меня поняли», усилие клиента (CES)", 0.20, [1, 4, 2, 5, 3, 5]),
    ("Удержание клиентов", 0.15, [2, 3, 2, 4, 3, 5]),
    ("Экономика: эффект за вычетом затрат", 0.15, [2, 2, 3, 4, 1, 4]),
    ("Риски: безопасность, комплаенс, злоупотребления", 0.10, [5, 5, 2, 4, 1, 4]),
    ("Реализуемость на 20 тыс. специалистов за 6 месяцев", 0.10, [5, 3, 2, 4, 5, 4]),
    ("Устраняет причины в продуктах (не повторяется)", 0.05, [1, 1, 2, 3, 1, 5]),
]


def build(path):
    wb = Workbook()

    # Sheet 1: inputs with names, so formulas read like the logic of the slide
    ws = wb.active
    ws.title = "Вводные"
    ws.append(["Показатель", "Значение", "Источник или тип"])
    for c in ws[1]:
        c.font, c.fill = BOLD, YELLOW
    names = {}
    for i, (key, label, value, fmt, src) in enumerate(INPUTS, start=2):
        ws.cell(i, 1, label)
        names[key] = f"Вводные!$B${i}"
        ws.cell(i, 3, src)
    for i, (key, label, value, fmt, src) in enumerate(INPUTS, start=2):
        cell = ws.cell(i, 2, sub(value, names))
        cell.number_format = fmt
        if not str(value).startswith("="):
            cell.fill = INPUT
    widths(ws, [62, 18, 110])

    # Sheet 2: options on one structure of factors and money
    wo = wb.create_sheet("Варианты")
    header = ["Показатель"] + [f"{code}: {name}" for code, name, _, _ in OPTIONS]
    wo.append(header)
    wo.append(["Что это"] + [desc for _, _, desc, _ in OPTIONS])
    rows = [
        ("once", "Разовые затраты на внедрение", RUB),
        ("yearly", "Ежегодные затраты", RUB),
        ("d_fcr", "Прирост решения с первого обращения в сложных ситуациях, п.п.", PCT),
        ("aht", "Рост времени на сложное обращение", PCT),
        ("ai", "Доля сложных обращений, которые уходят к ИИ", PCT),
        ("comp_share", "Доля сложных обращений с компенсацией", PCT),
        ("comp_avg", "Средняя компенсация", RUB),
        ("fix", "Доля сложных обращений, которые исчезнут после устранения причин в продуктах", PCT),
    ]
    r = {}
    for key, label, fmt in rows:
        wo.append([label] + [sub(opt[key], names) for *_, opt in OPTIONS])
        r[key] = wo.max_row
        for col in range(2, len(OPTIONS) + 2):
            wo.cell(r[key], col).number_format = fmt
            wo.cell(r[key], col).fill = INPUT
    H, C = names["hard_year"], names["cost"]
    calc = [
        ("cases", "Доп. сложных случаев, решённых с первого обращения в год", NUM, "={H}*{c}{d_fcr}"),
        ("rep_save", "Экономия на повторных обращениях", RUB, "={c}{cases}*{rep}*{C}"),
        ("ai_save", "Экономия от передачи ИИ", RUB, "={H}*{c}{ai}*({C}-{AIC})"),
        ("fix_save", "Экономия от устранения причин в продуктах", RUB, "={H}*{c}{fix}*{C}"),
        ("clients", "Клиентов сохранено в год", NUM, "={c}{cases}/{CPC}*({LB}-{LG})*{CONV}"),
        ("profit", "Сохранённая операционная прибыль в год", RUB, "={c}{clients}*{P}"),
        ("time", "Доп. затраты времени специалистов", RUB, "={H}*(1-{c}{ai})*{c}{aht}*{C}"),
        ("comp", "Компенсации клиентам в год", RUB, "={H}*{c}{comp_share}*{c}{comp_avg}"),
        ("y1", "Эффект первого года", RUB, "={c}{rep_save}+{c}{ai_save}+{c}{fix_save}+{c}{profit}-{c}{once}-{c}{yearly}-{c}{time}-{c}{comp}"),
        ("yn", "Эффект в год со второго года", RUB, "={c}{rep_save}+{c}{ai_save}+{c}{fix_save}+{c}{profit}-{c}{yearly}-{c}{time}-{c}{comp}"),
        ("payback", "Окупаемость, месяцев", "0.0", '=IF({c}{yn}<=0,"не окупается",{c}{once}/({c}{yn}/12))'),
    ]
    refs = dict(H=H, C=C, AIC=names["ai_cost"], CPC=names["cases_per_client"], LB=names["leave_bad"],
                LG=names["leave_good"], CONV=names["convert"], P=names["profit"], rep=names["repeats"])
    for key, label, fmt, formula in calc:
        wo.append([label])
        r[key] = wo.max_row
        for col in range(2, len(OPTIONS) + 2):
            c = get_column_letter(col)
            cell = wo.cell(r[key], col, formula.format(c=c, **refs, **r))
            cell.number_format = fmt
            if key in ("y1", "yn"):
                cell.font, cell.fill = BOLD, GREY
    wo.cell(1, 1).font = BOLD
    for cell in wo[1]:
        cell.font, cell.fill = BOLD, YELLOW
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in wo[2]:
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    widths(wo, [62] + [26] * len(OPTIONS))

    # Sheet 3: weighted comparison on one structure of factors
    wc = wb.create_sheet("Сравнение")
    wc.append(["Фактор", "Вес"] + [code for code, *_ in OPTIONS])
    for name, weight, scores in FACTORS:
        wc.append([name, weight] + scores)
    last = wc.max_row
    wc.append(["Итоговый балл (из 5)", f"=SUM(B2:B{last})"] + [
        f"=SUMPRODUCT($B$2:$B${last},{get_column_letter(col)}2:{get_column_letter(col)}{last})"
        for col in range(3, len(OPTIONS) + 3)])
    for cell in wc[1] + wc[wc.max_row]:
        cell.font = BOLD
    for row in wc.iter_rows(min_row=2, max_row=last, min_col=3, max_col=len(OPTIONS) + 2):
        for cell in row:
            cell.fill = INPUT
    for cell in wc[wc.max_row][2:]:
        cell.number_format = "0.00"
    wc.append([])
    wc.append(["Оценки 1-5 даны командой по данным research/01-03 и расчёту на листе «Варианты»; веса отражают вопрос кейса: опыт клиента и влияние на бизнес."])
    widths(wc, [58, 8] + [10] * len(OPTIONS))

    # Sheet 4: compensation threshold, the core of the justification template
    wk = wb.create_sheet("Порог компенсации")
    wk.append(["Калькулятор для шаблона-обоснования: когда уступка выгоднее отказа", ""])
    wk["A1"].font = BOLD
    rows4 = [
        ("Снижение вероятности ухода, если решить сейчас", f"={names['leave_bad']}-{names['leave_good']}", PCT),
        ("Доля намерения, которая станет уходом", f"={names['convert']}", PCT),
        ("Горизонт ценности клиента, лет", 1, "0"),
        ("Прибыль от активного клиента в год", f"={names['profit']}", RUB),
        ("Ожидаемых повторных обращений, если отказать", 2, "0"),
        ("Стоимость обращения", f"={names['cost']}", RUB),
        ("Максимальная оправданная компенсация", "=B2*B3*B4*B5+B6*B7", RUB),
    ]
    for label, value, fmt in rows4:
        wk.append([label, value])
        wk.cell(wk.max_row, 2).number_format = fmt
    wk["A8"].font = wk["B8"].font = BOLD
    for cell in ("B4", "B6"):
        wk[cell].fill = INPUT
    wk.append([])
    wk.append(["Сценарии порога", "1 год, уход 25%", "3 года, уход 50%"])
    wk.append(["Максимальная компенсация", "=B2*0.25*1*B5+B6*B7", "=B2*0.5*3*B5+B6*B7"])
    for cell in wk[11][1:]:
        cell.number_format = RUB
    wk.append(["Правило: если запрошенная уступка меньше порога и вина или спорность на стороне банка, специалист решает сам; выше порога или при признаках злоупотребления, по шаблону-обоснованию к руководителю."])
    widths(wk, [62, 22, 22])

    # Sheet 5: sensitivity of the recommended option to the two weakest assumptions
    ws5 = wb.create_sheet("Чувствительность")
    ws5.append(["Эффект рекомендации в год со 2-го года, млн ₽", "Доля намерения, ставшая уходом"])
    convs = [0.10, 0.25, 0.50]
    dfcrs = [0.04, 0.06, 0.08, 0.10, 0.12]
    ws5.append(["Прирост FCR, п.п. \\ уход"] + convs)
    rec = get_column_letter(len(OPTIONS) + 1)
    V = "Варианты!"
    for d in dfcrs:
        row = [d]
        for cv in convs:
            cases = f"{H}*{d}"
            row.append(
                f"=({cases}*{refs['rep']}*{C}+{cases}/{refs['CPC']}*({refs['LB']}-{refs['LG']})*{cv}*{refs['P']}"
                f"+{V}{rec}{r['fix_save']}-{V}{rec}{r['yearly']}-{V}{rec}{r['time']}-{V}{rec}{r['comp']})/1000000")
        ws5.append(row)
    for row in ws5.iter_rows(min_row=3, max_row=ws5.max_row):
        row[0].number_format = PCT
        for cell in row[1:]:
            cell.number_format = "#,##0"
    for cell in ws5[2][1:]:
        cell.number_format = PCT
    ws5["A1"].font = BOLD
    widths(ws5, [34, 14, 14, 14])

    # Sheet 6: pilot economics
    wp = wb.create_sheet("Пилот")
    pilot = [
        ("Специалистов в пилоте (5%)", 1000, NUM),
        ("Длительность, недель", 8, "0"),
        ("Обучение: 4 часа на специалиста", f"=B2*4*{names['hour']}", RUB),
        ("Первая версия подсказок (тип ситуации, вопросы, карточка случая)", 30e6, RUB),
        ("Бюджет жестов доброй воли на пилот", f"={H}*B2/{names['staff']}*B3/52*0.02*600", RUB),
        ("Итого стоимость пилота", "=B4+B5+B6", RUB),
        ("Сложных обращений в пилотной группе", f"={H}*B2/{names['staff']}*B3/52", NUM),
    ]
    wp.append(["Пилот: 1 000 специалистов, A/B с контрольной группой", ""])
    wp["A1"].font = BOLD
    for label, value, fmt in pilot:
        wp.append([label, value])
        wp.cell(wp.max_row, 2).number_format = fmt
    wp["A7"].font = wp["B7"].font = BOLD
    widths(wp, [70, 22])

    wb.save(path)


def sub(value, names):
    """Replace input keys inside a formula with absolute references to the inputs sheet."""
    if not isinstance(value, str) or not value.startswith("="):
        return value
    for key in sorted(names, key=len, reverse=True):
        value = value.replace(key, names[key])
    return value


def widths(ws, cols):
    for i, w in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def recalc(path):
    """Open and re-save through LibreOffice so the file carries computed values."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", tmp, str(path)],
                       check=True, capture_output=True, timeout=180)
        shutil.copy(Path(tmp) / path.name, path)


def export(path):
    wb = load_workbook(path, data_only=True)
    wo, wc, wk = wb["Варианты"], wb["Сравнение"], wb["Порог компенсации"]
    labels = {wo.cell(i, 1).value: i for i in range(1, wo.max_row + 1)}
    out = {"options": [], "inputs": {}}
    wi = wb["Вводные"]
    for i, (key, *_rest) in enumerate(INPUTS, start=2):
        out["inputs"][key] = wi.cell(i, 2).value
    total = wc.max_row - 2
    for j, (code, name, desc, _) in enumerate(OPTIONS, start=2):
        get = lambda label: wo.cell(labels[label], j).value
        out["options"].append({
            "code": code, "name": name, "desc": desc,
            "once": get("Разовые затраты на внедрение"),
            "yearly": get("Ежегодные затраты"),
            "d_fcr": get("Прирост решения с первого обращения в сложных ситуациях, п.п."),
            "rep_save": get("Экономия на повторных обращениях"),
            "ai_save": get("Экономия от передачи ИИ"),
            "fix_save": get("Экономия от устранения причин в продуктах"),
            "clients": get("Клиентов сохранено в год"),
            "profit": get("Сохранённая операционная прибыль в год"),
            "time": get("Доп. затраты времени специалистов"),
            "comp": get("Компенсации клиентам в год"),
            "y1": get("Эффект первого года"),
            "yn": get("Эффект в год со второго года"),
            "payback": get("Окупаемость, месяцев"),
            "score": wc.cell(total, j + 1).value,
        })
    out["factors"] = [{"name": n, "weight": w, "scores": s} for n, w, s in FACTORS]
    out["threshold"] = {"base": wk["B8"].value, "low": wk["B11"].value, "high": wk["C11"].value}
    ws5 = wb["Чувствительность"]
    out["sensitivity"] = [[ws5.cell(r, c).value for c in range(1, 5)] for r in range(2, ws5.max_row + 1)]
    wp = wb["Пилот"]
    out["pilot"] = {wp.cell(r, 1).value: wp.cell(r, 2).value for r in range(2, wp.max_row + 1)}
    return out


def main():
    OUT.mkdir(exist_ok=True)
    path = OUT / f"CupMoscow2026-Т-Банк-{TEAM}.xlsx"
    build(path)
    recalc(path)
    numbers = export(path)
    (OUT / "numbers.json").write_text(json.dumps(numbers, ensure_ascii=False, indent=2), encoding="utf-8")
    for o in numbers["options"]:
        print(f"{o['code']:4} score {o['score']:.2f}  y1 {o['y1']/1e6:8.0f} млн  yn {o['yn']/1e6:8.0f} млн  "
              f"clients {o['clients']:8.0f}  payback {o['payback']}")
    print("threshold", numbers["threshold"])
    print(path)


if __name__ == "__main__":
    main()
