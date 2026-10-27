"""Builds the Miro board (CJM + Service Blueprint + legend) from cjm/cjm.json.

Output: cjm/out/miro.svg in the Miro Canvas Composer SVG format.
The board copies the lanes of the team's Miro template (HSE UX course):
goal, actions, thoughts, emotions -2..+2, importance 1-3, reasons, touchpoints,
barriers, source and status, materials; below it the Service Blueprint.
Usage: python3 cjm/miro_svg.py, then pass the file to canvas_create_from_svg.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
cjm = json.loads((HERE / "cjm.json").read_text())
steps = {s["n"]: s for s in cjm["steps"]}


def a(text):
    """Attribute-safe text."""
    return escape(str(text), {'"': "&quot;"})


# Grid
X0, COL, CW = 340, 250, 240     # first step x, column pitch, cell width
LX, LW = 40, 240                # lane label column
GAP = 10
FRAME_W = X0 + 13 * COL + CW + 40


def cx(n):
    return X0 + (n - 1) * COL


def span(ns):
    return cx(ns[0]), cx(ns[-1]) + CW - cx(ns[0])


EMO = {-2: "#e5484d", -1: "#f5a524", 0: "#9aa0a6", 1: "#8bc34a", 2: "#2e9e5b"}
MARK = {"S": ("стресс", "#ffd6d6"), "R": ("равнодушие", "#dfe3ea"), "D": ("потеря доверия", "#e7dcff")}
DOTS = {1: "● 1 низкая", 2: "●● 2 средняя", 3: "●●● 3 высокая"}

out = []


def rect(x, y, w, h, content="", fill="#ffffff", color="#1f2329", size=14, bold=False,
         align="left", valign="top", stroke="#d6d6d6", dash=None, rid=None, rx=8):
    attrs = [f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"']
    attrs.append(f'stroke="{stroke}"' + (' stroke-width="2"' if stroke != "none" else ""))
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if rid:
        attrs.insert(0, f'id="{rid}"')
    if content:
        attrs.append(f'data-content="{a(content)}" data-text-color="{color}" data-font-size="{size}"'
                     f' data-text-align="{align}" data-text-align-vertical="{valign}"')
        if bold:
            attrs.append('data-font-weight="bold"')
    out.append(f'  <rect {" ".join(attrs)} />')


def text(x, y, body, size=14, fill="#1f2329", anchor="start", bold=False):
    w = ' font-weight="bold"' if bold else ""
    out.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{w}>{escape(body)}</text>')


def label(y, h, title, sub=""):
    body = f"<b>{escape(title)}</b>" + (f"<br>{escape(sub)}" if sub else "")
    out.append(f'  <rect x="{LX}" y="{y}" width="{LW}" height="{h}" rx="8" fill="#1f2329" stroke="none"'
               f' data-content="{a(body)}" data-text-color="#ffffff" data-font-size="15"'
               f' data-text-align="left" data-text-align-vertical="top" />')


# ---------- Frame 1: CJM ----------
LANES = [  # key, title, subtitle, height, fill
    ("goal", "Цель шага", "что хочет клиент", 90, "#f3f0ff"),
    ("actions", "Действия", "что делает", 120, "#ffffff"),
    ("thoughts", "Мысли и вопросы", "что думает", 120, "#fff6b8"),
    ("emotion", "Эмоции −2…+2", "линия: как есть; пунктир: с ПОНЯЛ", 360, None),
    ("importance", "Важность 1–3", "значимость шага", 60, "#ffffff"),
    ("why", "Причины оценок", "почему такая эмоция", 100, "#ffffff"),
    ("touchpoints", "Точки контакта", "каналы и люди", 100, "#e8f4ff"),
    ("barriers", "Барьеры и эффект", "что мешает", 110, "#ffe3e3"),
    ("status", "Источник и статус", "С, О, Н, Г", 110, "#f2f2f2"),
    ("materials", "Фото и материалы", "скрины, цитаты", 90, None),
    ("tobe", "С подходом ПОНЯЛ", "что меняется на шаге", 130, "#fff4b3"),
]
GRID_Y = 420
FRAME_H = GRID_Y + sum(l[3] + GAP for l in LANES) + 40

out.append(f'<g id="f_cjm" transform="translate(0,0)" data-frame="{a("CJM: " + cjm["title"].split(": ", 1)[1])}">')
out.append(f'  <rect data-type="frame" x="0" y="0" width="{FRAME_W}" height="{FRAME_H}" fill="#ffffff" />')
text(40, 80, "CJM: карта ограничена на кассе, решение на третий день", size=44, bold=True)
out.append(f'  <textArea x="40" y="110" width="2300" font-size="18"><b>Персона.</b> {escape(cjm["persona"])}</textArea>')
out.append(f'  <textArea x="40" y="190" width="2300" font-size="15" fill="#5f6368"><b>Основа.</b> {escape(cjm["basis"])}</textArea>')
# legend, top right
LGX = FRAME_W - 1180
rect(LGX, 100, 1140, 150, "<b>Как читать</b><br>Эмоции: рабочие оценки команды по отзывам и интервью, не измерения.<br>"
     "Статусы: <b>С</b> вторичный источник с URL, <b>О</b> отзыв или опрос, <b>Н</b> наблюдение, <b>Г</b> гипотеза.<br>"
     "«синт.»: синтетические данные (опрос N=40, интервью R01–R08), собраны на основе реальных отзывов.<br>"
     "Метки боли: красная стресс, серая равнодушие, фиолетовая потеря доверия.",
     fill="#f7f7f7", size=15, stroke="none")

# phases and step headers
for ph in cjm["phases"]:
    x, w = span(ph["steps"])
    rect(x, 260, w, 60, ph["name"], fill="#ffdd2d", size=20, bold=True, align="center", valign="middle", stroke="none")
for n, s in steps.items():
    rect(cx(n), 330, CW, 80, f"<b>{n:02d}</b><br>{s['name']}", fill="#333a42", color="#ffffff", size=15, stroke="none")

y = GRID_Y
for key, title, sub, h, fill in LANES:
    label(y, h, title, sub)
    if key == "emotion":
        E_Y = y
        # gap zone first so circles sit above it
        gx, gw = span([8, 12])
        rect(gx, y, gw, h, "С подходом ПОНЯЛ шагов 08–12 нет: вопрос решён в первом обращении",
             fill="#eaf6ee", color="#2e7d4f", size=16, bold=True, align="center", valign="top", stroke="none")
        for v in range(2, -3, -1):
            ly = y + 30 + (2 - v) * 65
            out.append(f'  <line data-type="divider" x1="{X0}" y1="{ly}" x2="{cx(14) + CW}" y2="{ly}"'
                       f' stroke="{"#9aa0a6" if v == 0 else "#e3e3e3"}" stroke-width="{2 if v == 0 else 1}" />')
            text(X0 - 14, ly + 5, f"{v:+d}".replace("-", "−") if v else "0", size=14, fill="#5f6368", anchor="end")
    elif key == "materials":
        for n, s in steps.items():
            first = s["touchpoints"].split(",")[0]
            rect(cx(n), y, CW, h, f"Место для скрина или цитаты: {first.lower()}", fill="#ffffff",
                 color="#9aa0a6", size=13, stroke="#c9c9c9", dash="5,5")
    elif key == "importance":
        for n, s in steps.items():
            rect(cx(n), y, CW, h, DOTS[s["importance"]], fill=fill, size=15, bold=s["importance"] == 3,
                 valign="middle")
    elif key == "tobe":
        for n, s in steps.items():
            gray = s["tobe"] is None
            rect(cx(n), y, CW, h, s["tobe_note"], fill="#f2f2f2" if gray else fill,
                 color="#9aa0a6" if gray else "#1f2329", size=14)
    else:
        for n, s in steps.items():
            rect(cx(n), y, CW, h, s[key], fill=fill, size=14)
    y += h + GAP


def ey(v):
    return E_Y + 30 + (2 - v) * 65


# emotion connectors first (z-order), then points
for n in range(1, 14):
    out.append(f'  <line x1="{cx(n) + 90}" y1="{ey(steps[n]["emotion"])}" x2="{cx(n + 1) + 90}" y2="{ey(steps[n + 1]["emotion"])}"'
               f' stroke="#1f2329" stroke-width="3" data-shape="straight" data-start="e{n}" data-end="e{n + 1}" />')
tobe = [n for n in steps if steps[n]["tobe"] is not None]
for p, q in zip(tobe, tobe[1:]):
    lab = ' data-content="решено в первом обращении"' if q - p > 1 else ""
    out.append(f'  <line x1="{cx(p) + 150}" y1="{ey(steps[p]["tobe"])}" x2="{cx(q) + 150}" y2="{ey(steps[q]["tobe"])}"'
               f' stroke="#2e9e5b" stroke-width="3" stroke-dasharray="5,5" data-shape="straight"'
               f' data-start="t{p}" data-end="t{q}"{lab} />')
for n, s in steps.items():
    v = s["emotion"]
    out.append(f'  <circle id="e{n}" cx="{cx(n) + 90}" cy="{ey(v)}" r="18" fill="{EMO[v]}" stroke="none"'
               f' data-content="{f'{v:+d}'.replace('-', '−')}" data-text-color="#ffffff" data-font-size="13" data-font-weight="bold" />'.replace('"+0"', '"0"'))
    if s["tobe"] is not None:
        t = s["tobe"]
        out.append(f'  <circle id="t{n}" cx="{cx(n) + 150}" cy="{ey(t)}" r="15" fill="#ffffff" stroke="#2e9e5b" stroke-width="3"'
                   f' data-content="{f'{t:+d}'.replace('-', '−')}" data-text-color="#2e7d4f" data-font-size="12" data-font-weight="bold" />'.replace('"+0"', '"0"'))
    for i, m in enumerate(s["marks"]):
        name, col = MARK[m]
        rect(cx(n) + i * 120, E_Y + 318, 115, 30, name, fill=col, size=12, bold=True, align="center",
             valign="middle", stroke="none", rx=14)
out.append("</g>")

# ---------- Frame 2: Service Blueprint ----------
BY = FRAME_H + 200
BP = [  # key, title, subtitle, height, fill
    ("client", "Действия клиента", "шаги CJM", 110, "#fff6b8"),
    ("visible", "Видимые действия", "фронт: что видит клиент", 110, "#e8f4ff"),
    ("line", "Линия видимости", "", 50, None),
    ("backstage", "За кулисами", "что происходит в банке", 120, "#ffffff"),
    ("systems", "Люди и системы", "кто и что поддерживает", 100, "#f2f2f2"),
    ("change", "Что меняем", "ПОНЯЛ и 5 изменений (analysis/04)", 150, "#fff4b3"),
]
CHANGE = [
    "Изм. 3: пуш и экран карты называют тип ограничения и дают кнопку «Подтвердить, что это я». Copilot видит отказ и ставит тип «Срочно»",
    "П-О-Н-Я: прочитать контекст, назвать ситуацию, снять ограничение в диалоге. Изм. 1: copilot подсвечивает тип и сигналы. Изм. 3: специалист видит тип и срок",
    "Изм. 2: карточка случая в чате: что сделано, что нужно от клиента, срок и ответственный. Неизвестности нет",
    "Изм. 2: случай закреплён за специалистом, история видна, те же вопросы не задаём. Изм. 4: уступка по порогу для типа «Снова»",
    "Л: специалист сам сообщает результат и объясняет, как избежать. Изм. 5: тег причины и сигнал в продукт антифрода",
]
BH = 200 + sum(b[3] + GAP for b in BP) + 40
out.append(f'<g id="f_bp" transform="translate(0,{BY})" data-frame="Service Blueprint: тот же путь изнутри банка">')
out.append(f'  <rect data-type="frame" x="0" y="0" width="{FRAME_W}" height="{BH}" fill="#ffffff" />')
text(40, 80, "Service Blueprint: что происходит за линией видимости", size=44, bold=True)
out.append('  <textArea x="40" y="110" width="2600" font-size="18">Колонки совпадают с шагами CJM выше. '
           'Главный разрыв: тип ограничения и срок видит служба безопасности, а не специалист, и второе обращение не связано с первым.</textArea>')
y = 200
for key, title, sub, h, fill in BP:
    if key == "line":
        text(LX, y + 32, "Линия видимости", size=18, fill="#e5484d", bold=True)
        out.append(f'  <line data-type="divider" x1="{X0}" y1="{y + 25}" x2="{cx(14) + CW}" y2="{y + 25}"'
                   f' stroke="#e5484d" stroke-width="3" data-line-style="dashed" />')
    else:
        label(y, h, title, sub)
        for i, row in enumerate(cjm["blueprint"]):
            x, w = span(row["steps"])
            if key == "client":
                body = ", ".join(f"{n:02d} {steps[n]['name']}" for n in row["steps"])
            elif key == "change":
                body = CHANGE[i]
            else:
                body = row[key]
            rect(x, y, w, h, body, fill=fill, size=15)
    y += h + GAP
out.append("</g>")

# ---------- Frame 3: fail points and conclusions ----------
FY = BY + BH + 200
FW = FRAME_W
out.append(f'<g id="f_fp" transform="translate(0,{FY})" data-frame="Точки боли и выводы для решения">')
out.append(f'  <rect data-type="frame" x="0" y="0" width="{FW}" height="560" fill="#ffffff" />')
text(40, 80, "Где клиент теряет доверие и что из этого следует", size=44, bold=True)
cw = (FW - 80 - 3 * 40) // 4
for i, fp in enumerate(cjm["fail_points"]):
    name, col = MARK[fp["mark"]]
    rect(40 + i * (cw + 40), 130, cw, 380, f"<b>{name.capitalize()}</b><br>{fp['where']}<br><br>{(lambda t: t[0].upper() + t[1:])(fp['what'].split(': ', 1)[-1])}",
         fill=col, size=20, stroke="none", rx=12)
rect(40 + 3 * (cw + 40), 130, cw, 380,
     "<b>Вывод для подхода</b><br>Ошибка не в вежливости, а в том, что специалист отвечает на слова, а не на ситуацию, "
     "и не видит тип ограничения. Шаги П и О убирают равнодушие, Я убирает стресс неизвестности, Л возвращает доверие. "
     "Кривая «с ПОНЯЛ» короче на 5 шагов.",
     fill="#ffdd2d", size=20, stroke="none", rx=12)
out.append("</g>")

svg = "<svg xmlns=\"http://www.w3.org/2000/svg\">\n" + "\n".join(out) + "\n</svg>\n"
(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "miro.svg").write_text(svg)
# one file per frame: smaller uploads, a failed one does not block the others
starts = [i for i, line in enumerate(out) if line.startswith("<g ")] + [len(out)]
for k, (b, e) in enumerate(zip(starts, starts[1:]), 1):
    part = "<svg xmlns=\"http://www.w3.org/2000/svg\">\n" + "\n".join(out[b:e]) + "\n</svg>\n"
    (HERE / "out" / f"miro_{k}.svg").write_text(part)
print(f"cjm/out/miro.svg: {len(svg)} chars, frames 3, CJM {FRAME_W}x{FRAME_H}")
