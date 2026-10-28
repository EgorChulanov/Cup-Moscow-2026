"""Собирает доску Miro из cjm/cjm.json по шаблону доски команды (курс UX-исследований ВШЭ).

Геометрия повторяет фрейм «CJM Алины: 24 шага и Service Blueprint»: колонка шага 448 px с зазором 32 px,
подписи дорожек слева, эмоции и важность точками, Service Blueprint в том же фрейме.
Результат: cjm/out/NN_*.svg, по файлу на загрузку в Miro (Canvas Composer). Большие фреймы режутся на части:
первая создаёт фрейм, следующие добавляют стикеры в него.
Запуск: python3 cjm/miro_svg.py
"""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
OUT = HERE / "out"
CJM = json.loads((HERE / "cjm.json").read_text())
STEPS = {s["n"]: s for s in CJM["steps"]}

# Сдвиг всей раскладки вниз, под старые фреймы доски
OY = 5000


def a(text):
    return escape(str(text), {'"': "&quot;"})


def rich(text):
    """data-content с переносами и жирным: экранируем, затем возвращаем разрешённые теги."""
    return a(text)


def rect(x, y, w, h, content="", fill="#f7f7f7", size=14, bold=False, align="left", valign="top",
         stroke="#e7e7e7", color="#1a1a1a", rx=None, dash=None, rid=None):
    at = [f'x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"']
    if rid:
        at.insert(0, f'id="{rid}"')
    if rx:
        at.append(f'rx="{rx}"')
    if dash:
        at.append(f'stroke-dasharray="{dash}" stroke-width="2"')
    if content:
        tc = "" if color == "#1a1a1a" else f' data-text-color="{color}"'
        al = "" if align == "center" else f' data-text-align="{align}"'
        va = "" if valign == "middle" else f' data-text-align-vertical="{valign}"'
        at.append(f'data-content="{a(content)}"{tc} data-font-size="{size}"{al}{va}')
        if bold:
            at.append('data-font-weight="bold"')
    return f'<rect {" ".join(at)} />'


def text(x, y, w, body, size=24, color="#595959", bold=False):
    b = ' font-weight="bold"' if bold else ""
    return f'<textArea x="{x}" y="{y}" width="{w}" fill="{color}" font-size="{size}"{b}>{body}</textArea>'


def sticky(x, y, w, h, body, color="light_blue"):
    return f'<rect data-type="sticky" x="{x}" y="{y}" width="{w}" height="{h}" data-color="{color}" data-content="{a(body)}" />'


def link_html(s):
    """Превращает «banki.ru/...» в полную ссылку, чтобы в Miro она открывалась."""
    def full(m):
        host = m.group(1)
        url = "https://" + ("www." if host.startswith("banki.ru") else "") + m.group(0)
        return f'<a href="{a(url)}">{escape(m.group(0))}</a>'
    parts = re.split(r"((?:www\.)?(?:banki\.ru|otzovik\.com|brobank\.ru|vc\.ru|sravni\.ru)/\S+)", s)
    out = []
    for p in parts:
        m = re.match(r"((?:www\.)?(?:banki\.ru|otzovik\.com|brobank\.ru|vc\.ru|sravni\.ru))(/\S+)", p)
        out.append(full(m) if m else escape(p))
    return "".join(out)


def frame(fid, x, y, w, h, title, body):
    return (f'<g id="{fid}" transform="translate({x},{y + OY})" data-frame="{a(title)}">\n'
            f'<rect data-type="frame" x="0" y="0" width="{w}" height="{h}" fill="#ffffff" />\n'
            + "\n".join(body) + "\n</g>")


def inside(x, y, w, h, body):
    """Догрузка в уже созданный фрейм: FRAME_ID заменяется на data-miro-id фрейма перед загрузкой."""
    return (f'<g data-miro-id="FRAME_ID" transform="translate({x},{y + OY})">\n'
            f'<rect data-type="frame" x="0" y="0" width="{w}" height="{h}" fill="#ffffff" />\n'
            + "\n".join(body) + "\n</g>")


def svg(*groups):
    return '<svg xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(groups) + "\n</svg>\n"


# ---------- CJM: геометрия шаблона ----------
X0, PITCH, CW = 416, 480, 448
N = len(STEPS)
CJM_W = X0 + N * PITCH - 32 + 64           # 11968 при 24 шагах
LANES = {  # y, высота
    "goal": (576, 224), "actions": (832, 320), "thoughts": (1184, 256),
    "reasons": (2432, 256), "touch": (2720, 256), "barriers": (3008, 384),
    "src": (3424, 256), "mat": (3712, 320),
    "vis": (4480, 288), "back": (4864, 288), "sys": (5184, 288), "tobe": (5568, 288),
}
LABELS = [
    ("goal", "Цель шага", "Что нужно получить на этом шаге?"),
    ("actions", "Действия", "Что делает? Куда переходит? Что повторяет?"),
    ("thoughts", "Мысли и вопросы", "Что хочет понять? В чём сомневается?"),
    ("reasons", "Причины оценок", "Что чувствует и почему? Почему шаг важен?"),
    ("touch", "Точки контакта", "Люди, экраны, каналы, сервисы и альтернативы."),
    ("barriers", "Барьеры и эффект", "Что мешает? Потерянное время, деньги, доверие."),
    ("src", "Источник и статус", "Г / Н / С / О. Отзыв, интервью или вопрос для проверки."),
    ("mat", "Фото и материалы", "Цитаты из отзывов со ссылкой, скрины, документы."),
    ("vis", "Видимые действия", "Что видит клиент в работе банка?"),
    ("back", "За кулисами", "Какая работа идёт вне поля зрения Ирины?"),
    ("sys", "Люди и системы", "Кто обеспечивает шаг? На что опирается?"),
    ("tobe", "С подходом ПОНЯЛ", "Что меняется на шаге после внедрения решения."),
]
EMO_Y = {2: 1592, 1: 1656, 0: 1720, -1: 1784, -2: 1848}
IMP_Y = {3: 2136, 2: 2200, 1: 2264}
EMO_FILL = {2: "#8cfbaf", 1: "#c8f7d6", 0: "#e1ecff", -1: "#ffdede", -2: "#ffc6c6"}
IMP_FILL = {1: "#f0f5fd", 2: "#c6dcff", 3: "#8fb8ff"}
MARK = {"S": ("стресс", "#ffc6c6"), "R": ("равнодушие", "#e3e6ec"), "D": ("доверие", "#e6dbff")}
CJM_H = 6260


def sx(n):
    return X0 + (n - 1) * PITCH


def phase_span(steps):
    return sx(steps[0]), sx(steps[-1]) + CW - sx(steps[0])


def cjm_skeleton():
    b = [text(64, 62, 11840, f"<b>{escape(CJM['heading'])}</b>", 67, "#1a1a1a"),
         text(64, 171, 11840, escape(CJM["persona"]), 30)]
    for st in CJM["stages"]:
        x, w = sx(st["steps"][0]), sx(st["steps"][1]) + CW - sx(st["steps"][0])
        b.append(rect(x, 224, w, 64, st["name"], "#eaf9ef", 36, True, "center", "middle"))
    for ph in CJM["phases"]:
        x, w = phase_span(ph["steps"])
        b.append(rect(x, 320, w, 96, ph["name"], "#adf0c7", 44, True, "center", "middle"))
        for key, (y, h) in LANES.items():
            if key in ("vis", "back", "sys", "tobe"):
                continue
            b.append(rect(x, y, w, h))
    for n, s in STEPS.items():
        b.append(rect(sx(n), 448, CW, 96, f"{n:02d}. {s['name']}", "#eaf9ef", 26, False, "center", "middle"))
    # белые зазоры между шагами внутри этапа, как в шаблоне
    for n in STEPS:
        if n % 3:
            b.append(rect(sx(n) + CW, 576, 32, 3456, fill="#ffffff", stroke="#ffffff"))
    for key, title, sub in LABELS:
        y, h = LANES[key]
        b.append(text(64, y + 28, 336, f"<b>{title}</b>", 30, "#1a1a1a"))
        b.append(text(64, y + 81, 336, sub, 24))
    # эмоции
    b.append(text(64, 1472, 336, "<b>ЭМОЦИИ</b>", 33, "#1a1a1a"))
    b.append(text(64, 1529, 336, "Как переживает этот шаг", 22))
    b.append(text(416, 1468, 11488, "Рабочие оценки команды по отзывам и интервью, не измерения. Розовый: плохо; синий: нормально; зелёный: хорошо. "
                  "Белые точки с жёлтой обводкой: тот же шаг с подходом ПОНЯЛ. Шагов 03, 06, 08, 13-19 с подходом ПОНЯЛ нет: вопрос решён в первом обращении.", 26))
    for v, y in EMO_Y.items():
        lab = {2: "+2 Очень хорошо", 1: "+1 Хорошо", 0: "0 Нормально", -1: "−1 Плохо", -2: "−2 Очень плохо"}[v]
        b.append(text(64, y - 17, 336, lab, 24))
        b.append(f'<line data-type="divider" x1="416" y1="{y}" x2="{CJM_W - 64}" y2="{y}" stroke="#e7e7e7" stroke-width="2" />')
    b.append(text(64, 1903, 336, "<b>Точки боли</b>", 24, "#1a1a1a"))
    b.append(rect(416, 1888, CJM_W - 480, 64, fill="#f7f7f7", stroke="#ffffff"))
    # важность
    b.append(text(64, 2016, 336, "<b>ВАЖНОСТЬ</b>", 33, "#1a1a1a"))
    b.append(text(64, 2073, 336, "Значимость для Ирины", 22))
    b.append(text(416, 2012, 11488, "Значимость шага для Ирины: светло-синий = 1, синий = 2, насыщенный синий = 3. Высокая важность не означает плохую эмоцию.", 26))
    for v, y in IMP_Y.items():
        b.append(text(64, y - 17, 336, {3: "3 Высокая", 2: "2 Средняя", 1: "1 Низкая"}[v], 24))
        b.append(f'<line data-type="divider" x1="416" y1="{y}" x2="{CJM_W - 64}" y2="{y}" stroke="#e7e7e7" stroke-width="2" />')
    # кривые: сначала линии, потом точки
    ns = sorted(STEPS)
    for p, q in zip(ns, ns[1:]):
        b.append(f'<line x1="0" y1="0" x2="1" y2="1" data-start="e{p}" data-end="e{q}" stroke="#595959" stroke-width="2" data-shape="curved" data-start-side="right" data-end-side="left" />')
        b.append(f'<line x1="0" y1="0" x2="1" y2="1" data-start="i{p}" data-end="i{q}" stroke="#595959" stroke-width="2" data-shape="curved" data-start-side="right" data-end-side="left" />')
    tb = [n for n in ns if STEPS[n]["tobe_emo"] is not None]
    for p, q in zip(tb, tb[1:]):
        b.append(f'<line x1="0" y1="0" x2="1" y2="1" data-start="t{p}" data-end="t{q}" stroke="#d6a800" stroke-width="3" stroke-dasharray="5,5" data-shape="curved" data-start-side="right" data-end-side="left" />')
    for n in ns:
        s = STEPS[n]
        c = sx(n) + 150
        b.append(f'<circle id="e{n}" cx="{c}" cy="{EMO_Y[s["emo"]]}" r="24" fill="{EMO_FILL[s["emo"]]}" stroke="#595959" stroke-width="2" data-content="{n:02d}" data-font-size="18" />')
        b.append(f'<circle id="i{n}" cx="{c}" cy="{IMP_Y[s["imp"]]}" r="24" fill="{IMP_FILL[s["imp"]]}" stroke="#595959" stroke-width="2" data-content="{n:02d}" data-font-size="18" />')
        if s["tobe_emo"] is not None:
            b.append(f'<circle id="t{n}" cx="{c + 150}" cy="{EMO_Y[s["tobe_emo"]]}" r="20" fill="#ffffff" stroke="#ffdc4a" stroke-width="4" data-content="{n:02d}" data-font-size="15" />')
        for i, m in enumerate(s["marks"]):
            name, col = MARK[m]
            b.append(rect(sx(n) + 16 + i * 216, 1896, 200, 48, name, col, 22, True, "center", "middle", "#ffffff", rx=24))
    # Service Blueprint
    b.append(text(64, 4191, 11840, "<b>Service Blueprint</b>", 67, "#1a1a1a"))
    b.append(text(64, 4300, 11840, "Тот же путь со стороны банка. Внутренние процессы описываем по открытым источникам и кейсу; неизвестное фиксируем вопросом.", 30))
    for ph in CJM["phases"]:
        x, w = phase_span(ph["steps"])
        lo, hi = ph["steps"][0], ph["steps"][-1]
        b.append(rect(x, 4352, w, 96, f"{lo:02d}-{hi:02d}. {ph['name'].split('. ', 1)[1]}", "#adf0c7", 33, True, "center", "middle"))
        for key in ("vis", "back", "sys", "tobe"):
            y, h = LANES[key]
            b.append(rect(x, y, w, h, fill="#fff6b6" if key == "tobe" else "#f7f7f7", stroke="#ffdc4a" if key == "tobe" else "#e7e7e7"))
    for n in STEPS:
        if n % 3:
            b.append(rect(sx(n) + CW, 4480, 32, 992, fill="#ffffff", stroke="#ffffff"))
            b.append(rect(sx(n) + CW, 5568, 32, 288, fill="#ffffff", stroke="#ffffff"))
    b.append(text(64, 4780, 336, "<b>Линия видимости</b>", 24, "#1a1a1a"))
    b.append(f'<line data-type="divider" x1="416" y1="4816" x2="{CJM_W - 64}" y2="4816" stroke="#595959" stroke-width="3" data-line-style="dashed" />')
    b.append(text(64, 5500, 11840, "<b>Решение команды поверх карты:</b> жёлтая дорожка показывает, что меняет подход ПОНЯЛ и изменения в продукте на каждом шаге.", 26, "#1a1a1a"))
    b.append(text(64, 5900, 11840, escape(CJM["basis"]), 24))
    b.append(text(64, 5990, 11840, "Цитаты в «» из отзывов прочитаны по выдержкам; перед защитой каждую открыть по ссылке. Цитаты с пометкой «синт.» написаны командой по мотивам реальных отзывов, это не слова реальных людей.", 24))
    return frame("cjm", 0, 0, CJM_W, CJM_H, CJM["title"], b)


def mat_cell(n, s):
    x, (y, h) = sx(n), LANES["mat"]
    m = s["mat"]
    if m.startswith("Скрин") or m.startswith("Г:"):
        return [rect(x + 24, y + 24, CW - 48, h - 48, m, "#ffffff", 20, False, "center", "middle", "#b0b0b0", dash="5,5")]
    return [rect(x + 24, y + 24, CW - 48, 150, "", "#ffffff", stroke="#e7e7e7"),
            text(x + 40, y + 40, CW - 80, link_html(m), 18, "#1a1a1a")]


def step_stickies(n):
    s, x = STEPS[n], sx(n)
    b = [sticky(x + 80, 594, 289, 188, s["goal"], "light_green")]
    for i, t in enumerate(s["actions"][:2]):
        b.append(sticky(x + 16 + i * 216, 880, 199, 228, t))
    th = s["thoughts"]
    b.append(sticky(x + 59, 1205, 330, 215, " ".join(th)))
    col = {"pink": "light_pink", "green": "light_green", "blue": "light_blue"}
    for i, (t, c) in enumerate(s["reasons"][:2]):
        b.append(sticky(x + 17 + i * 226, 2441, 188, 215, t, col[c]))
    for i, t in enumerate(s["touch"][:2]):
        b.append(sticky(x + 17 + i * 226, 2740, 188, 215, t))
    for i, t in enumerate(s["barriers"][:2]):
        b.append(sticky(x + 17 + i * 226, 3092, 188, 215, t, "light_pink"))
    src = s["src"]
    b.append(sticky(x + 59, 3445, 330, 215, src, "yellow" if src[:1] in "ОС" else "light_blue"))
    b += mat_cell(n, s)
    return b


def step_blueprint(n):
    s, x = STEPS[n], sx(n)
    b = []
    vis = s["vis"]
    if len(vis) == 1:
        b.append(sticky(x + 128, 4514, 192, 220, vis[0]))
    else:
        for i, t in enumerate(vis[:2]):
            b.append(sticky(x + 17 + i * 222, 4514, 192, 220, t))
    b.append(sticky(x + 38, 4887, 371, 242, s["back"]))
    b.append(sticky(x + 38, 5207, 371, 242, s["sys"]))
    none = s["tobe_emo"] is None and s["tobe"].startswith("Шаг")
    b.append(sticky(x + 38, 5591, 371, 242, s["tobe"], "gray" if none else "yellow"))
    return b


def write_all():
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.svg"):
        f.unlink()
    files = {"10_cjm_skeleton.svg": svg(cjm_skeleton())}
    ns = sorted(STEPS)
    for k in range(0, N, 12):
        body = []
        for n in ns[k:k + 12]:
            body += step_stickies(n)
        files[f"11_cjm_steps_{k + 1:02d}.svg"] = svg(inside(0, 0, CJM_W, CJM_H, body))
    for k in range(0, N, 24):
        body = []
        for n in ns[k:k + 24]:
            body += step_blueprint(n)
        files[f"12_cjm_blueprint_{k + 1:02d}.svg"] = svg(inside(0, 0, CJM_W, CJM_H, body))
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"{name}: {len(content)} символов")


if __name__ == "__main__":
    write_all()
