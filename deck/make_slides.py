"""Generates deck/slides.html from the project data, so every number on a slide matches
the financial model (model/out/numbers.json) and the CJM (cjm/cjm.json).

Usage: python3 deck/make_slides.py   (then: node deck/build.mjs)
Env:   TEAM  team name shown on the title slide (empty = not shown yet)
"""

import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = json.loads((ROOT / "model/out/numbers.json").read_text(encoding="utf-8"))
CJM = json.loads((ROOT / "cjm/cjm.json").read_text(encoding="utf-8"))
TEAM = os.environ.get("TEAM", "").strip()
OPT = {o["code"]: o for o in NUM["options"]}
REC = OPT["REC"]
MAIN_TOTAL = 8


def mln(x):
    return f"{round(x / 1e6):,}".replace(",", " ")


def rub(x):
    return f"{round(x):,}".replace(",", " ") + " ₽"


def months(x):
    return f"{x:.1f}".replace(".", ",")


E = html.escape

# Key numbers used on several slides
K = dict(
    yn=mln(REC["yn"]), y1=mln(REC["y1"]), once=mln(REC["once"]), payback=months(REC["payback"]),
    clients=f"{REC['clients'] / 1000:.1f}".replace(".", ","), rep=mln(REC["rep_save"]), fix=mln(REC["fix_save"]),
    profit=mln(REC["profit"]), time=mln(REC["time"]), comp=mln(REC["comp"]), yearly=mln(REC["yearly"]),
    thr_low=rub(NUM["threshold"]["low"]), thr_high=rub(NUM["threshold"]["high"]),
    dfcr=round(REC["d_fcr"] * 100),
)

CSS = """
@font-face{font-family:Onest;font-weight:100 900;src:url(fonts/onest-cyrillic-wght-normal.woff2) format('woff2');unicode-range:U+0400-045F,U+2116}
@font-face{font-family:Onest;font-weight:100 900;src:url(fonts/onest-latin-wght-normal.woff2) format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+20BD,U+2122,U+2212}
@font-face{font-family:Onest;font-weight:100 900;src:url(fonts/onest-latin-ext-wght-normal.woff2) format('woff2');unicode-range:U+0100-024F,U+20A0-20AB,U+20AD-20CF}
@page{size:1920px 1080px;margin:0}
:root{--ink:#1a1a1a;--body:#3c4049;--muted:#6b7280;--line:#e3e5e8;--card:#f4f5f7;--y:#ffdd2d;--y2:#fff6c2;--red:#d93f45;--red2:#fde8e8;--green:#1d8f4e;--green2:#e3f5ea;--blue:#2f6fde;--blue2:#e7effd}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Onest,system-ui,sans-serif;color:var(--ink);background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.slide{width:1920px;height:1080px;padding:64px 88px 56px;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column}
.slide:last-child{page-break-after:auto}
.top{display:flex;justify-content:space-between;align-items:center;font-size:18px;color:var(--muted);margin-bottom:22px;font-weight:500}
.top .tag{display:flex;align-items:center;gap:12px}
.top .tag i{width:22px;height:22px;border-radius:6px;background:var(--y);display:inline-block}
.top .pg{font-variant-numeric:tabular-nums}
.top .ap{background:var(--ink);color:#fff;border-radius:999px;padding:4px 14px;font-size:16px;margin-right:12px}
h1{font-size:46px;line-height:1.12;font-weight:700;letter-spacing:-.01em;max-width:1700px}
h1 em{font-style:normal;background:linear-gradient(transparent 58%,var(--y) 58%)}
.lead{font-size:23px;line-height:1.4;color:var(--body);margin-top:14px;max-width:1650px}
.body{flex:1;display:flex;gap:28px;margin-top:30px;min-height:0}
.col{display:flex;flex-direction:column;gap:18px;min-width:0}
.card{background:var(--card);border-radius:22px;padding:24px 26px}
.card.y{background:var(--y)}
.card.yl{background:var(--y2)}
.card.dark{background:var(--ink);color:#fff}
.card h3{font-size:24px;font-weight:700;margin-bottom:10px;line-height:1.2}
.card p,.card li{font-size:20px;line-height:1.38;color:var(--body)}
.card.dark p,.card.dark li{color:#e5e7eb}
.card ul{padding-left:22px}
.card li{margin-bottom:6px}
.k{font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.big{font-size:64px;font-weight:800;letter-spacing:-.02em;line-height:1}
.mid{font-size:40px;font-weight:800;letter-spacing:-.01em;line-height:1.05}
.src{font-size:14.5px;color:var(--muted);line-height:1.35;margin-top:auto;padding-top:14px;border-top:1px solid var(--line)}
.src b{color:var(--body)}
.chip{display:inline-block;border-radius:999px;padding:3px 12px;font-size:16px;font-weight:600;white-space:nowrap}
.c-red{background:var(--red2);color:var(--red)}.c-green{background:var(--green2);color:var(--green)}.c-blue{background:var(--blue2);color:var(--blue)}.c-y{background:var(--y2);color:#7a5b00}.c-ink{background:var(--ink);color:#fff}
table.t{width:100%;border-collapse:separate;border-spacing:0;font-size:18px;line-height:1.3}
table.t th{text-align:left;font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:700;padding:8px 10px;border-bottom:2px solid var(--ink)}
table.t td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:middle;color:var(--body)}
table.t td b{color:var(--ink)}
table.t tr.hl td{background:var(--y2)}
table.t.s{font-size:16px}table.t.s td{padding:6px 8px}table.t.s th{padding:6px 8px;font-size:13px}
table.t.xs{font-size:14px;line-height:1.25}table.t.xs td{padding:5px 7px}table.t.xs th{padding:5px 7px;font-size:12px}
.bar{height:22px;border-radius:6px;display:inline-block;vertical-align:middle}
.row{display:flex;gap:28px}
.letter{width:66px;height:66px;border-radius:18px;background:var(--y);display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:800;flex:none}
.note{font-size:16px;color:var(--muted);line-height:1.35}
.appendix h1{font-size:38px}
.appendix table.t.s{font-size:19px}.appendix table.t.s td{padding:10px 10px}.appendix .card p{font-size:20px}
"""


def page(n, title, body, src="", lead="", appendix=False, label=""):
    if appendix:
        tag = f'<span class="ap">Приложение {n}</span>{E(label)}'
        pg = ""
    else:
        tag = "Changellenge Cup Moscow 2026, секция Т-Банк"
        pg = f"{n} / {MAIN_TOTAL}"
    src_html = f'<div class="src">{src}</div>' if src else ""
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    cls = "slide appendix" if appendix else "slide"
    return (f'<section class="{cls}"><div class="top"><div class="tag"><i></i>{tag}</div><div class="pg">{pg}</div></div>'
            f'<h1>{title}</h1>{lead_html}<div class="body">{body}</div>{src_html}</section>')


# ---------- main slides ----------

def s1():
    team = f'<div style="font-size:30px;font-weight:700;margin-bottom:8px">Команда «{E(TEAM)}»</div>' if TEAM else ""
    letters = "".join(
        f'<div style="display:flex;align-items:center;gap:20px"><div class="letter" style="background:#fff">{l}</div>'
        f'<div style="font-size:24px;font-weight:600">{w}</div></div>'
        for l, w in [("П", "Прочитать контекст"), ("О", "Обозначить, что понял"), ("Н", "Найти настоящую задачу"),
                     ("Я", "Ясный план и действие"), ("Л", "Лично довести и вернуть сигнал")])
    return f"""<section class="slide" style="padding:0;flex-direction:row">
  <div style="flex:1;padding:72px 88px 64px;display:flex;flex-direction:column">
    <div class="top"><div class="tag"><i></i>Changellenge Cup Moscow 2026, секция Т-Банк</div></div>
    <div style="margin-top:110px;font-size:26px;font-weight:600;color:var(--muted)">Подход к работе специалиста клиентской поддержки</div>
    <div style="font-size:92px;font-weight:800;letter-spacing:-.03em;line-height:1;margin-top:18px">ПОНЯЛ</div>
    <div style="font-size:40px;font-weight:700;line-height:1.2;margin-top:26px;max-width:980px">Понять человека, решить с первого обращения и убрать причину в продукте</div>
    <div class="row" style="margin-top:56px;gap:22px">
      <div class="card" style="flex:1"><div class="mid">+{K['dfcr']} п.п.</div><p style="margin-top:8px">решения с первого обращения в сложных ситуациях</p></div>
      <div class="card" style="flex:1"><div class="mid">{K['yn']} млн ₽</div><p style="margin-top:8px">эффект в год со второго года</p></div>
      <div class="card" style="flex:1"><div class="mid">{K['payback']} мес.</div><p style="margin-top:8px">окупаемость внедрения</p></div>
    </div>
    <div style="margin-top:auto">{team}<div style="font-size:22px;color:var(--body)">Егор Чуланов, Екатерина Макаренко (НИУ ВШЭ), Искандер Ханов (МГТУ им. Н. Э. Баумана)</div></div>
  </div>
  <div style="width:620px;background:var(--y);padding:120px 64px;display:flex;flex-direction:column;gap:26px;justify-content:center">{letters}
    <div style="font-size:19px;line-height:1.4;margin-top:20px;color:#3a3000">Пять шагов, после которых клиент чувствует «меня поняли», а банк получает решённый вопрос и сигнал для продукта</div>
  </div></section>"""


def s2():
    bars = [("П1", "Быстро и решено в чате за один контакт", 8, "g"), ("Ж1", "Шаблонный ответ, нет решения по сути", 7, "r"),
            ("Ж2", "Долго, сдвигаются обещанные сроки", 5, "r"), ("П2", "Оператор сам сделал действие", 4, "g"),
            ("Ж3", "Бот не решает, трудно дойти до человека", 4, "r"), ("Ж4", "Блокировки 115-ФЗ и 161-ФЗ: «замкнутый круг»", 4, "r"),
            ("Ж6", "Мошенничество: отказ без участия", 3, "r"), ("Ж7", "Передачи и повторные обращения", 2, "r")]
    rows = "".join(
        f'<tr><td style="width:60%">{E(t)}</td><td style="white-space:nowrap"><span class="bar" style="width:{n * 16}px;background:{"var(--green)" if c == "g" else "var(--red)"}"></span>'
        f' <b>{n}</b> из 53</td></tr>' for _, t, n, c in bars)
    comp = [("Сбер", "итог звонка присылают в чат", "голосовой бот не понимает, не дозвониться"),
            ("Альфа-Банк", "лучший контакт-центр 2026 (Frank RG)", "«бот не даёт ничего», отписки"),
            ("ВТБ", "лучший чат-бот 2025 (Markswebb)", "8 операторов без ответа"),
            ("Яндекс Банк", "диалог не откатывается к боту", "робот рвёт звонок"),
            ("Озон Банк", "8–10 баллов у 58% (ВЦИОМ)", "отписки при блокировке")]
    crow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in comp)
    best = [("Делать, а не инструктировать", "Т-Банк: блок, перевыпуск и перевод в одном чате"),
            ("Итог и договорённости письменно", "Сбер: итог разговора в чат"),
            ("Не возвращать к боту, если клиент дошёл до человека", "Яндекс Банк"),
            ("Полномочия решать без согласования", "Ritz-Carlton: до $2000 на гостя"),
            ("Отдельный подход к уязвимым", "Т-Банк: команда для детей, поддержка на РЖЯ"),
            ("После решения найти причину", "Disney HEARD: шаг Diagnose")]
    brow = "".join(f'<li><b style="color:var(--ink)">{a}.</b> {b}</li>' for a, b in best)
    body = f"""
<div class="col" style="flex:1.05"><div class="card" style="flex:1"><h3>Т-Банк: что хвалят и что ругают</h3>
  <table class="t s">{rows}</table>
  <p class="note" style="margin-top:12px">53 отзыва 2025–2026 (banki.ru, otzovik, sravni и др.), один отзыв может попасть в несколько тем</p></div></div>
<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Конкуренты: что удобно и что разочаровало</h3>
  <table class="t s"><tr><th>Банк</th><th>Удобно</th><th>Разочаровало</th></tr>{crow}</table>
  <p class="note" style="margin-top:12px">Общее у всех: бот не понимает, трудно дойти до человека, шаблон вместо решения</p></div>
  <div class="card y"><p style="color:var(--ink);font-size:20px"><b>Вывод.</b> Рутину Т-Банк решает лучше рынка: 82% довольны поддержкой, лучший результат в опросе ВЦИОМ. Доверие теряется в нестандартных случаях (шаблон, неизвестный срок, повтор), а именно они достаются специалисту, пока ИИ закрывает до 45% простых обращений.</p></div></div>
<div class="col" style="flex:.95"><div class="card" style="flex:1"><h3>Лучшие практики, которые берём</h3><ul>{brow}</ul></div></div>"""
    src = ("<b>Источники:</b> research/01 (отзывы, ссылки на каждый), ВЦИОМ 05.10.2026 (vedomosti.ru), Frank RG 2026, Markswebb Chatbot Rank 2025, "
           "lenta.ru 20.10.2026 (Сбер), tbank.ru/finance/blog/support-stories, Ritz-Carlton и Disney HEARD (research/03). Подробно: приложения 2–3.")
    return page(2, "Т-Банк силён в простых обращениях, а доверие теряет в сложных: там клиент получает <em>процедуру вместо помощи</em>", body, src)


def s3():
    types = [("Срочно", "действие за минуты", "отказ операции 15 мин назад, «стою на кассе», за рубежом", "статью и инструкцию", "c-red"),
             ("Страшно", "остановить потерю, снять вину", "перевод новому получателю, смена номера, «развели»", "«вы перевели сами»", "c-red"),
             ("Несправедливо", "причина, маршрут, срок", "ограничение 115-ФЗ или 161-ФЗ, спорное списание, «на каком основании»", "«по требованиям законодательства»", "c-blue"),
             ("Тяжело", "бережный темп, человек, близкие", "возраст, путаница в тексте, просрочка, «умер», «болею»", "тон взыскания, полотно текста", "c-blue"),
             ("Снова", "признание и владелец случая", "2+ обращения по теме за 30 дней, «третий раз»", "просить те же данные", "c-y")]
    trows = "".join(
        f'<tr><td><span class="chip {c}">{n}</span></td><td>{need}</td><td>{sig}</td><td>{no}</td></tr>' for n, need, sig, no, c in types)
    acts = [("Прочитал контекст до первого вопроса", 4), ("Назвал ситуацию и эмоцию, снял вину", 4),
            ("Сделал сам, а не отправил инструкцию", 3), ("Дал план и срок, вернулся сам", 5), ("Честно про «нельзя» и альтернатива", 2)]
    arows = "".join(
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px"><div class="letter" style="width:44px;height:44px;font-size:24px;border-radius:12px">{i}</div>'
        f'<div style="flex:1;font-size:20px;line-height:1.25">{t}</div><div style="width:190px;white-space:nowrap"><span class="bar" style="width:{n * 22}px;background:var(--ink)"></span> <b>{n}</b> из 6</div></div>'
        for i, (t, n) in enumerate(acts, 1))
    causes = ["Не понята настоящая проблема", "Ответ верный, но для клиента «ещё одна задача»", "«Нельзя» без объяснения и срока",
              "Вопрос не доведён до конца", "Причина в продукте не устраняется"]
    cz = "".join(f'<div style="flex:1;background:#fff;border-radius:14px;padding:12px 14px;font-size:18px;line-height:1.25"><b>{chr(1040 + i) if i < 4 else "Д"}.</b> {c}</div>'
                 for i, c in enumerate(causes))
    body = f"""
<div class="col" style="flex:1.55">
  <div class="card yl" style="padding:18px 22px"><div class="k" style="color:#7a5b00">Почему клиент уходит без помощи: 5 ветвей дерева причин (5 уровней, приложение 4)</div><div style="display:flex;gap:12px">{cz}</div></div>
  <div class="card" style="flex:1"><h3>5 типов ситуаций, которым нужен особый подход</h3>
  <table class="t s"><tr><th style="width:150px">Тип</th><th>Что нужно человеку</th><th>Сигналы для распознавания</th><th>Чего нельзя</th></tr>{trows}</table>
  <p class="note" style="margin-top:10px">Типы пересекаются: более уязвимый задаёт тон, более срочный задаёт порядок действий</p></div></div>
<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>5 действий, которые решили исход</h3>
  <p class="note" style="margin-bottom:16px">6 ситуаций тренажёрного типа, собранных из реальных отзывов: типичный ответ против ответа по подходу (приложение 6)</p>{arows}
  <div class="card y" style="margin-top:12px;padding:16px 18px"><p style="color:var(--ink);font-size:19px"><b>Главное:</b> исход решает не вежливость, а то, сколько действий остаётся клиенту и знает ли он срок</p></div></div></div>"""
    src = ("<b>Источники:</b> типы из 12 ситуаций research/01 (раздел 6) и FCA FG21/1 (уязвимые клиенты); сигналы: признаки мошеннических операций ЦБ с 01.01.2026; "
           "ситуации тренажёрного типа <b>смоделированы командой</b> по реальным отзывам, реальный тренажёр ЛК заменит их при прохождении (research/synthetic).")
    return page(3, "Сложные обращения делятся на <em>5 типов ситуаций</em>, и исход в них решают 5 действий специалиста", body, src)


def cjm_svg(w=1700, h=330, show_tobe=True, labels=True):
    steps = CJM["steps"]
    n = len(steps)
    left, right, top, bot = 70, 20, 30, 40
    cw = (w - left - right) / n
    y = lambda e: top + (2 - e) / 4 * (h - top - bot)
    x = lambda i: left + cw * (i + 0.5)
    parts = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Onest">']
    for e in (-2, -1, 0, 1, 2):
        parts.append(f'<line x1="{left}" x2="{w - right}" y1="{y(e)}" y2="{y(e)}" stroke="{"#9aa0a6" if e == 0 else "#e3e5e8"}" stroke-width="{2 if e == 0 else 1}"/>')
        parts.append(f'<text x="{left - 14}" y="{y(e) + 6}" font-size="17" text-anchor="end" fill="#6b7280">{e:+d}'.replace("+0", "0") + "</text>")
    if show_tobe:
        idx = [i for i, s in enumerate(steps) if s["tobe"] is not None]
        for a, b in zip(idx, idx[1:]):
            if b == a + 1:
                parts.append(f'<line x1="{x(a):.0f}" y1="{y(steps[a]["tobe"]):.0f}" x2="{x(b):.0f}" y2="{y(steps[b]["tobe"]):.0f}" stroke="#1d8f4e" stroke-width="5" stroke-dasharray="14 10"/>')
            else:
                gx1, gx2 = x(a) + 20, x(b) - 20
                parts.append(f'<rect x="{gx1:.0f}" y="{top}" width="{gx2 - gx1:.0f}" height="{h - top - bot - 6}" rx="12" fill="#e3f5ea"/>')
                parts.append(f'<text x="{(gx1 + gx2) / 2:.0f}" y="{y(1.5):.0f}" font-size="20" font-weight="700" fill="#1d8f4e" text-anchor="middle">С подходом ПОНЯЛ шагов {steps[a + 1]["n"]:02d}–{steps[b - 1]["n"]:02d} нет:</text>')
                parts.append(f'<text x="{(gx1 + gx2) / 2:.0f}" y="{y(1.5) + 26:.0f}" font-size="18" fill="#1d8f4e" text-anchor="middle">вопрос решён в первом обращении</text>')
        for i in idx:
            parts.append(f'<circle cx="{x(i):.0f}" cy="{y(steps[i]["tobe"]):.0f}" r="8" fill="#1d8f4e"/>')
    asis = " ".join(f"{x(i):.0f},{y(s['emotion']):.0f}" for i, s in enumerate(steps))
    parts.append(f'<polyline points="{asis}" fill="none" stroke="#d93f45" stroke-width="5" stroke-linejoin="round"/>')
    colors = {"S": "#d93f45", "R": "#2f6fde", "D": "#1a1a1a"}
    for i, s in enumerate(steps):
        parts.append(f'<circle cx="{x(i):.0f}" cy="{y(s["emotion"]):.0f}" r="10" fill="#d93f45"/>')
        for j, m in enumerate(s["marks"]):
            parts.append(f'<rect x="{x(i) - 17 + j * 36 - (len(s["marks"]) - 1) * 18:.0f}" y="{h - 34}" width="34" height="28" rx="7" fill="{colors[m]}"/>'
                         f'<text x="{x(i) + j * 36 - (len(s["marks"]) - 1) * 18:.0f}" y="{h - 14}" font-size="17" font-weight="700" fill="#fff" text-anchor="middle">{m}</text>')
    parts.append("</svg>")
    return "".join(parts)


def cjm_header(w=1700):
    steps, phases = CJM["steps"], CJM["phases"]
    n = len(steps)
    left, right = 70, 20
    cw = (w - left - right) / n
    ph = "".join(
        f'<div style="position:absolute;left:{left + cw * (p["steps"][0] - 1):.0f}px;width:{cw * len(p["steps"]) - 6:.0f}px;top:0;height:36px;background:{"var(--y)" if k % 2 == 0 else "var(--y2)"};border-radius:10px;font-size:17px;font-weight:700;display:flex;align-items:center;justify-content:center">{E(p["name"])}</div>'
        for k, p in enumerate(phases))
    st = "".join(
        f'<div style="position:absolute;left:{left + cw * i:.0f}px;width:{cw - 6:.0f}px;top:44px;height:64px;font-size:15px;line-height:1.2;text-align:center;color:var(--body)"><b style="color:var(--ink)">{s["n"]:02d}</b><br>{E(s["name"])}</div>'
        for i, s in enumerate(steps))
    return f'<div style="position:relative;height:112px;width:{w}px">{ph}{st}</div>'


def s4():
    body = f"""<div class="col" style="flex:1;gap:10px">
  <div class="card" style="padding:18px 22px 10px">
    <div style="font-size:19px;color:var(--body);margin-bottom:10px"><b style="color:var(--ink)">Ирина, 32 года</b>, зарплатный клиент 4 года. Вечер пятницы, оплата на кассе не проходит: антифрод ограничил карту. Решение на третий день после двух обращений.
</div>
    <div style="display:flex;gap:28px;font-size:17px;color:var(--body);margin-bottom:12px"><span><span style="display:inline-block;width:36px;height:5px;background:#d93f45;vertical-align:middle;margin-right:8px"></span>эмоция сейчас</span><span><span style="display:inline-block;width:36px;height:0;border-top:5px dashed #1d8f4e;vertical-align:middle;margin-right:8px"></span>с подходом ПОНЯЛ</span><span><b>S</b> стресс</span><span><b>R</b> равнодушие</span><span><b>D</b> потеря доверия</span><span>шкала: −2 очень плохо, +2 очень хорошо</span></div>
    {cjm_header()}{cjm_svg()}</div>
  <div class="row" style="gap:18px">
    <div class="card" style="flex:1;padding:18px 22px"><h3><span class="chip c-ink" style="background:#d93f45">S</span> Стресс: шаги 01, 05, 08, 10</h3><p>Деньги нужны сейчас, а причина и срок неизвестны. <b style="color:var(--ink)">Меняем:</b> тип «Срочно» сразу к специалисту, действие вместо статьи</p></div>
    <div class="card" style="flex:1;padding:18px 22px"><h3><span class="chip c-ink" style="background:#2f6fde">R</span> Равнодушие: шаги 04, 06, 07, 11</h3><p>Статья и инструкция вместо действия, те же вопросы второй раз. <b style="color:var(--ink)">Меняем:</b> П и О (контекст и «вижу, что случилось»), карточка случая</p></div>
    <div class="card" style="flex:1;padding:18px 22px"><h3><span class="chip c-ink">D</span> Потеря доверия: шаги 09, 11, 14</h3><p>Второе обращение «как первое», клиентка страхуется картой другого банка. <b style="color:var(--ink)">Меняем:</b> Я и Л (срок, владелец, сам вернулся)</p></div>
  </div></div>"""
    src = ("<b>Основа:</b> реальные отзывы research/01 (Ж1, Ж2, Ж4, Ж7, П1, П2) и типичный путь при блокировке research/03 (4а); эмоции по синтетическим интервью R01, R03, R05. "
           "Оценки эмоций рабочие, не измерения. Полная CJM с 10 дорожками и Service Blueprint: приложения 8–10 и доска Miro.")
    return page(4, "CJM: стресс на кассе, равнодушие в чате и <em>потеря доверия на повторном обращении</em>", body, src)


def s5():
    names = {"O1": "Стандарты и скрипты", "O2": "Тренинг эмпатии для всех", "O3": "ИИ решает сложные случаи сам",
             "O4": "Ситуационный подход ПОНЯЛ", "O5": "Компенсации без согласования", "REC": "ПОНЯЛ + полномочия по формуле + сигнал в продукт"}
    verdict = {"O1": ("отклонён", "c-red"), "O2": ("часть O4", "c-blue"), "O3": ("отклонён", "c-red"), "O4": ("ядро", "c-green"),
               "O5": ("только узко", "c-blue"), "REC": ("выбор", "c-green")}
    fac = NUM["factors"]
    short = ["Решение с первого", "«Меня поняли», CES", "Удержание", "Экономика", "Риски", "Реализуемость", "Причины в продукте"]
    head = "".join(f'<th style="text-align:center;width:112px">{short[i]}<br><span style="font-weight:400;text-transform:none">{round(f["weight"] * 100)}%</span></th>' for i, f in enumerate(fac))
    rows = ""
    for j, code in enumerate(["O1", "O2", "O3", "O4", "O5", "REC"]):
        o = OPT[code]
        dots = "".join(
            f'<td style="text-align:center"><span style="display:inline-block;width:{12 + f["scores"][j] * 4}px;height:{12 + f["scores"][j] * 4}px;border-radius:50%;background:{["#d93f45", "#f08a8e", "#c9ccd1", "#7bc196", "#1d8f4e"][f["scores"][j] - 1]};vertical-align:middle"></span></td>'
            for f in fac)
        yn = o["yn"] / 1e6
        cls = ' class="hl"' if code == "REC" else ""
        v, vc = verdict[code]
        rows += (f'<tr{cls}><td><b>{"" if code == "REC" else code + " "}{names[code]}</b></td>{dots}'
                 f'<td style="text-align:right"><b>{yn:,.0f}</b></td><td style="text-align:center"><b>{o["score"]:.2f}</b></td><td><span class="chip {vc}">{v}</span></td></tr>').replace(",", " ").replace(f'{o["score"]:.2f}', f'{o["score"]:.2f}'.replace(".", ","))
    body = f"""<div class="col" style="flex:1">
  <div class="card" style="flex:1;padding:20px 22px"><table class="t s"><tr><th>Вариант</th>{head}<th style="text-align:right;width:130px">Эффект в год, млн ₽</th><th style="text-align:center;width:90px">Балл из 5</th><th style="width:130px">Вердикт</th></tr>{rows}</table>
  <p class="note" style="margin-top:8px">Точка: оценка фактора 1–5 (крупнее и зеленее = лучше). Эффект в год со 2-го года из финмодели, лист «Варианты»</p></div>
  <div class="row" style="gap:18px">
    <div class="card" style="flex:1.3;padding:18px 22px"><h3>Почему не просто ИИ или компенсации</h3><p>O3: ИИ «обещает» то, чего не решает (удовлетворённость ИИ-сотрудником 78,7% при цели 84,3%). O5: компенсация не доказанно удерживает (de Matos, 2007) и стоит 2,1 млрд ₽ в год.</p></div>
    <div class="card y" style="flex:1;padding:18px 22px"><h3>Выбор: {K['yn']} млн ₽ в год, окупаемость {K['payback']} мес.</h3><p style="color:var(--ink)">Окупается уже при +4 п.п. к решению с первого обращения (приложение 13). Пилот покажет факт до масштабирования.</p></div>
  </div></div>"""
    src = ("<b>Источники:</b> финмодель model/out/*.xlsx (вводные со ссылками на кейс, Т-Технологии МСФО 2025, SQM Group, ContactBabel, Gartner); cnews.ru 07.08.2026 (Афанасий); "
           "de Matos et al., Journal of Service Research, 2007. Допущения: доля сложных обращений 15%, прирост FCR по вариантам, доля намерения уйти, ставшая уходом, 25%.")
    return page(5, "Из 5 вариантов лучше всего работает <em>ситуационный подход</em> с полномочиями по формуле и сигналом в продукт", body, src)


def s6():
    steps = [
        ("П", "Прочитать контекст", "до первого ответа: история, операции за 24 ч, статус ограничения, тип ситуации",
         "не спрашивает то, что уже видно", "история обращений, суммаризация, copilot: подсказка типа", "отказ 15 мин назад, тип блокировки, 2+ обращения по теме, новое устройство"),
        ("О", "Обозначить, что понял", "пересказ ситуации своими словами, назвать состояние, снять вину",
         "«Правильно понимаю, что вы сейчас на кассе?»", "подсказка фразы под тип, текст свой", "«срочно», «развели», «третий раз», капс, нет пунктуации"),
        ("Н", "Найти настоящую задачу", "1–2 уточняющих вопроса, по одному",
         "«Насколько срочно нужны деньги?» «Сейчас кто-то просит назвать код?»", "база знаний по типу ситуации, а не по словам", "слова клиента не совпадают с данными (пишет «списали», а это холд)"),
        ("Я", "Ясный план и действие", "сам делает, что может; план: что сделал, что от клиента, когда результат; «нельзя» с альтернативой",
         "«Я уже снял ограничение. От вас: повторить оплату»", "действия в чате, карточка случая, калькулятор порога уступки", f"порог уступки {K['thr_low']}–{K['thr_high']}, вина банка, сегмент, злоупотребления"),
        ("Л", "Лично довести и вернуть сигнал", "владелец случая до решения, возвращается сам; системная причина в шаблон-обоснование",
         "«Решилось? Ответьте сюда, я увижу»", "напоминание о сроке, закрепление случая, тег причины", "повтор по теме за 7 дней, скор чувствительности к негативу"),
    ]
    cols = ""
    for l, name, do, ask, tools, sig in steps:
        cols += f"""<div class="card" style="flex:1;padding:20px 20px;display:flex;flex-direction:column;gap:12px">
<div style="display:flex;align-items:center;gap:14px"><div class="letter">{l}</div><div style="font-size:23px;font-weight:700;line-height:1.15">{name}</div></div>
<div><div class="k">Что делает</div><p style="font-size:18px">{do}</p></div>
<div><div class="k">Спрашивает</div><p style="font-size:18px">{ask}</p></div>
<div><div class="k">Инструменты</div><p style="font-size:18px">{tools}</p></div>
<div><div class="k">Данные и сигналы</div><p style="font-size:18px">{sig}</p></div></div>"""
    principles = ["Сначала человек, потом процедура", "Минимум действий от клиента", "Срок вместо «ожидайте», не обещать неподтверждённое", "Закрыт не ответ, а проблема"]
    pr = "".join(f'<div style="flex:1;font-size:20px;font-weight:600;padding:4px 0"><span style="color:#7a5b00">{i}.</span> {p}</div>' for i, p in enumerate(principles, 1))
    body = f"""<div class="col" style="flex:1"><div class="row" style="gap:16px;flex:1">{cols}</div>
<div class="card y" style="padding:16px 24px;display:flex;align-items:center;gap:20px"><div style="font-size:20px;font-weight:800;white-space:nowrap">Принципы:</div>{pr}</div></div>"""
    src = ("<b>Основа:</b> 5 действий из ситуаций тренажёрного типа и интервью (research/synthetic), HEARD (Disney), A.P.P.L.E. (Apple), TEXAS и IDEA для уязвимых клиентов, "
           "Customer Effort Score (HBR, 2010), скор негатива Т-Банка (habr.com/post/832580). Плейбук по 5 типам ситуаций: приложение 11.")
    return page(6, "Подход ПОНЯЛ: <em>5 шагов</em> превращают правильный ответ в решённый вопрос", body, src)


def waterfall():
    items = [("Меньше повторов", REC["rep_save"], "+"), ("Устранение причин", REC["fix_save"], "+"), ("Сохранённые клиенты", REC["profit"], "+"),
             ("Время на диалог", REC["time"], "-"), ("Уступки", REC["comp"], "-"), ("Расходы", REC["yearly"], "-")]
    w, h, left, bottom = 530, 340, 4, 44
    total = sum(v for _, v, s in items if s == "+")
    sc = (h - bottom - 40) / total
    bw = 62
    gap = (w - left - bw * 7) / 7
    parts = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Onest">']
    level = 0
    for i, (name, v, sgn) in enumerate(items):
        x = left + i * (bw + gap)
        if sgn == "+":
            y0, y1 = level + v, level
            level += v
            col = "#1d8f4e"
        else:
            y0, y1 = level, level - v
            level -= v
            col = "#d93f45"
        top = h - bottom - y0 * sc
        hh = (y0 - y1) * sc
        parts.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{bw}" height="{max(hh, 2):.0f}" rx="6" fill="{col}"/>')
        parts.append(f'<text x="{x + bw / 2:.0f}" y="{top - 8:.0f}" font-size="17" font-weight="700" text-anchor="middle">{sgn}{round(v / 1e6)}</text>')
        parts.append(f'<foreignObject x="{x - 8:.0f}" y="{h - bottom + 4}" width="{bw + 16}" height="44"><div xmlns="http://www.w3.org/1999/xhtml" style="font:12px/1.15 Onest;text-align:center;color:#3c4049">{name}</div></foreignObject>')
    x = left + 6 * (bw + gap)
    top = h - bottom - level * sc
    parts.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{bw}" height="{level * sc:.0f}" rx="6" fill="#1a1a1a"/>')
    parts.append(f'<text x="{x + bw / 2:.0f}" y="{top - 8:.0f}" font-size="20" font-weight="800" text-anchor="middle">{round(level / 1e6)}</text>')
    parts.append(f'<foreignObject x="{x - 8:.0f}" y="{h - bottom + 4}" width="{bw + 16}" height="44"><div xmlns="http://www.w3.org/1999/xhtml" style="font:700 12px/1.15 Onest;text-align:center">Эффект в год</div></foreignObject>')
    parts.append("</svg>")
    return "".join(parts)


def s7():
    changes = [("Copilot подсказывает тип ситуации и вопросы", "FCR за 7 дней"), ("Карточка случая в чате и один владелец", "повторы, CES"),
               ("Тип ограничения виден специалисту, документы файлом, срок", "жалобы в ЦБ"), (f"Уступка без согласования до порога", "удержание 90 дней"),
               ("Тег причины и ежемесячный топ-10 причин для продуктов", "обращения по тегу")]
    ch = "".join(f'<tr><td><b>{i}.</b> {a}</td><td style="white-space:nowrap"><span class="chip c-blue">{m}</span></td></tr>' for i, (a, m) in enumerate(changes, 1))
    tpl = ["Что произошло (факт)", "Почему важно: последствия и масштаб, похожих за 30 дней", "Что предлагаю: для клиента и для продукта", "На какой результат рассчитываем", "Как проверим и что может ухудшиться"]
    tp = "".join(f'<div style="display:flex;gap:12px;margin-bottom:8px;font-size:18px;line-height:1.25"><span class="chip c-ink">{i}</span><span>{t}</span></div>' for i, t in enumerate(tpl, 1))
    body = f"""
<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Что изменить в продуктах и процессах</h3><table class="t">{ch}</table></div>
  <div class="card" style="padding:18px 22px"><h3 style="font-size:21px">Метрики в паре, чтобы не улучшать одну ценой другой</h3><p style="font-size:18px">FCR ↔ время обработки (+5% максимум); «меня поняли» ↔ оценки после отказа; удержание ↔ расходы на уступки</p></div></div>
<div class="col" style="flex:.95"><div class="card" style="flex:1"><h3>Шаблон-обоснование для специалиста</h3>{tp}
  <div class="card yl" style="padding:14px 18px;margin-top:8px"><div class="k" style="color:#7a5b00">Почему уступка выгодна банку</div>
  <p style="font-size:18px;color:var(--ink)">Порог = 0,20 (снижение риска ухода) x доля, ставшая уходом x прибыль клиента x лет + повторы x 274 ₽ = <b>{K['thr_low']}–{K['thr_high']}</b>. Пример: вернуть 98 ₽ за недоплату 5 копеек, 98 &lt; 809, специалист решает сам</p></div></div></div>
<div class="col" style="flex:1.05"><div class="card" style="flex:1"><h3>На что влияет решение специалиста, млн ₽ в год</h3>{waterfall()}
  <p style="font-size:18px;margin-top:6px">{K['clients']} тыс. сохранённых клиентов в год. Внедрение {K['once']} млн ₽, эффект первого года {K['y1']} млн ₽.</p></div>
  <div class="card dark" style="padding:16px 20px"><p style="font-size:18px"><b style="color:var(--y)">План:</b> 4 недели подготовки, пилот на 1 000 специалистах 8 недель с контрольной группой (35 млн ₽), 3 волны, весь департамент через 6 месяцев</p></div></div>"""
    src = ("<b>Источники:</b> финмодель (лист «Варианты», «Порог компенсации», «Пилот»); прибыль активного клиента 5 220 ₽: 174,4 млрд ₽ / 33,4 млн (Т-Технологии, 2025); "
           "намерение уйти 25% против 5% (SQM Group); стоимость обращения 274 ₽ (оценка research/02); McKinsey: устранение корневых причин минус 25–40% обращений, у нас заложено 2%. Приложения 12–15.")
    return page(7, f"Решение специалиста влияет на деньги банка: <em>{K['yn']} млн ₽ в год</em> за счёт меньших повторов, удержания и устранения причин", body, src)


def s8():
    people = [
        ("Егор Чуланов", "НИУ ВШЭ, Высшая школа бизнеса, «Управление цифровым продуктом», 2 курс", "img/team-egor.webp",
         ["Продукт и исследование: CJM, дерево причин", "Хакатон Альфа-Банка 2026: умный кредитный кабинет, продукт и кредитная логика", "UX-исследования: JTBD, CJM, Service Blueprint"]),
        ("Екатерина Макаренко", "НИУ ВШЭ, Высшая школа бизнеса, «Управление цифровым продуктом», 2 курс", "img/team-kate.webp",
         ["Исследование и качество: опрос, интервью, ситуации", "Хакатон Альфа-Банка 2026: качество, ИИ и инфраструктура", "UX-исследования: интервью, карта сходства"]),
        ("Искандер Ханов", "МГТУ им. Н. Э. Баумана, 2 курс", None,
         ["Финансовая модель и аналитика", "Опыт: уточнить у участника", "Навыки: уточнить у участника"]),
    ]
    cards = ""
    for name, uni, photo, items in people:
        ph = (f'<img src="{photo}" style="width:220px;height:260px;object-fit:cover;object-position:50% 20%;border-radius:20px">' if photo else
              '<div style="width:220px;height:260px;border-radius:20px;background:var(--y);display:flex;align-items:center;justify-content:center;font-size:72px;font-weight:800">ИХ</div>')
        li = "".join(f"<li>{i}</li>" for i in items)
        cards += f"""<div class="card" style="flex:1;display:flex;flex-direction:column;gap:18px">{ph}
<div><div style="font-size:30px;font-weight:800">{name}</div><p style="margin-top:6px;font-size:19px">{uni}</p></div><ul>{li}</ul></div>"""
    team = f"Команда «{E(TEAM)}»" if TEAM else "Команда"
    body = f'<div class="row" style="flex:1;gap:24px">{cards}</div>'
    return page(8, f"{team}: продукт, исследование и цифры в одной связке", body,
                "Мы студенты продуктовых и инженерных программ: делали CJM и Service Blueprint по методике курса «UX-исследование» ВШБ ВШЭ и считали экономику решения в открытой модели (Excel приложен).")


# ---------- appendix ----------

def a_method():
    rows = [("Отзывы о поддержке", "53 по Т-Банку, около 25 по конкурентам, 2023–2026", "banki.ru, otzovik, sravni, irecommend, brobank, vc.ru", "реальные, по выдержкам поисковой выдачи; ссылка на каждый", "c-green"),
            ("Рынок и регулятор", "ЦБ (жалобы, мошенничество), ВЦИОМ, Frank RG, Markswebb, Naumen", "сайты источников", "реальные", "c-green"),
            ("Экономика", "МСФО Т-Технологий 2025, SQM, ContactBabel, Gartner, McKinsey, NBER", "research/02", "реальные + помеченные допущения", "c-y"),
            ("Практики и методики", "14 компаний, HEARD, A.P.P.L.E., TEXAS, IDEA, FCA FG21/1, NN/g, Shostack", "research/03", "реальные", "c-green"),
            ("Опрос", "40 ответов, вопросы из анкеты в чате участников + CES", "research/synthetic/generate_survey.py", "синтетические: распределения из отзывов и бенчмарков", "c-red"),
            ("Интервью", "8 Interview Snapshot (R01–R08)", "research/synthetic/interviews.md", "синтетические: каждое на реальном отзыве", "c-red"),
            ("Ситуации тренажёрного типа", "6 ситуаций (T1–T6), два ответа и оценка по рубрике", "research/synthetic/trainer_situations.md", "смоделированы по реальным отзывам", "c-red")]
    tr = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td><span class="chip {k}">{d}</span></td></tr>' for a, b, c, d, k in rows)
    body = f"""<div class="col" style="flex:1"><div class="card"><table class="t s"><tr><th>Данные</th><th>Объём</th><th>Где лежат</th><th>Статус</th></tr>{tr}</table></div>
<div class="row"><div class="card" style="flex:1"><h3>Почему синтетические данные и как мы их ограничили</h3><p>За неделю тура команда не успела провести поле и пройти тренажёр. Чтобы не выдумывать, каждый синтетический ответ построен на реальном отзыве со ссылкой, распределения опроса заданы в открытом скрипте. Выводы опираются прежде всего на реальные отзывы, синтетика их иллюстрирует.</p></div>
<div class="card yl" style="flex:1"><h3>Как заменить на реальные</h3><p>Гайд интервью, скрининг и анкета готовы (research/04_field_plan.md), журнал тренажёра research/05_trainer_log.md. Реальные данные заменяют синтетические без изменения структуры решения.</p></div></div></div>"""
    return page(1, "Методология: какие данные реальные, а какие синтетические", body,
                "Все материалы и скрипты лежат в репозитории команды; цифры на слайдах собираются из финмодели автоматически.", appendix=True, label="Методология")


def a_reviews():
    comp = [("Ж1", "Шаблонные ответы, нет решения по сути", "7 из 53", "banki.ru/services/responses/bank/response/12954614"),
            ("Ж2", "Долгое решение, сдвиг сроков", "5 из 53", "otzovik.com/reviews/sluzhba_podderzhki_tinkoff"),
            ("Ж3", "Бот не решает, трудно дойти до человека", "4 из 53", "brobank.ru/banki/tbank/comments"),
            ("Ж4", "Блокировки 115-ФЗ и 161-ФЗ: «замкнутый круг»", "4 из 53", "banki.ru/services/questions-answers/question/845015"),
            ("Ж5", "Телефон: обрывы, занятая линия", "3 из 53", "brobank.ru/banki/tbank/comments"),
            ("Ж6", "Мошенничество: отказ, нет заморозки у получателя", "3 из 53", "banki.ru/services/responses/bank/response/12234755"),
            ("Ж7", "Передачи между операторами, повторы", "2 из 53", "banki.ru/services/responses/bank/response/12942993"),
            ("Ж8", "Ограничение доступа к чату (спор, долг)", "2 из 53", "banki.ru/services/responses/bank/response/12669271"),
            ("Ж9", "Реструктуризация: тон взыскания", "2 из 53", "sravni.ru/bank/t-bank/otzyvy/720279"),
            ("Ж10", "Отказ вернуть мелкую сумму", "2 из 53", "vc.ru/id5515644/2672101"),
            ("П1", "Быстро и решено в чате за один контакт", "8 из 53", "banki.ru/services/responses/bank/response/13179135"),
            ("П2", "Оператор сам делает действие", "4 из 53", "1000bankov.ru/bank/2673/otzyvy/39299"),
            ("П3", "Вежливость, понятное объяснение", "4 из 53", "banki.ru/services/responses/bank/response/12991116"),
            ("П5", "Гибкость, «идут навстречу»", "3 из 53", "banki.ru/services/responses/bank/response/12739708")]
    tr = "".join(f'<tr><td><span class="chip {"c-red" if c[0] == "Ж" else "c-green"}">{c}</span></td><td>{t}</td><td><b>{n}</b></td><td style="font-size:13px">{u}</td></tr>' for c, t, n, u in comp)
    nums = [("Жалобы в ЦБ на банки, 2025", "235,2 тыс. (+14,7%)", "cbr.ru"), ("Доля жалоб о блокировках и отказах", "24,7% (17% в 2024)", "cbr.ru"),
            ("Жалобы на антифрод", "в 2,3 раза: 18 → 40,5 тыс.", "bankstoday.net"), ("Возвращено похищенного, 2025", "1,7 из 29,3 млрд ₽ (5,9%)", "interfax.ru"),
            ("Удовлетворённость поддержкой Т-Банка", "82%, лучший в опросе", "ВЦИОМ, vedomosti.ru 05.10.2026"),
            ("Предпочитают чат в приложении", "64%", "Frank RG и BSS, itweek.ru"), ("Ренкинг ЦБ по жалобам заёмщиков", "Т-Банк 8 из 9", "vbr.ru, 2025"),
            ("Удовлетворённость ИИ-сотрудником", "78,7% при цели 84,3%", "cnews.ru 07.08.2026")]
    nr = "".join(f'<tr><td>{a}</td><td><b>{b}</b></td><td style="font-size:13px">{c}</td></tr>' for a, b, c in nums)
    body = f"""<div class="col" style="flex:1.25"><div class="card" style="flex:1"><h3>Т-Банк: темы отзывов (53 отзыва)</h3><table class="t s" style="font-size:16px"><tr><th>Код</th><th>Тема</th><th>Частота</th><th>Пример источника</th></tr>{tr}</table></div></div>
<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Цифры рынка</h3><table class="t s"><tr><th>Показатель</th><th>Значение</th><th>Источник</th></tr>{nr}</table>
<p class="note" style="margin-top:12px">Выборка отзывов не случайная: частоты показывают, какие темы встречаются, а не долю клиентов. Цитаты сверять по ссылкам.</p></div></div>"""
    return page(2, "Отзывы о поддержке: темы Т-Банка и цифры рынка", body, "Полная таблица со всеми ссылками и цитатами: research/01_reviews_tbank_and_competitors.md.", appendix=True, label="Опыт поддержки")


def a_practices():
    rows = [("Т-Банк", "Оператор делает действие в чате; команда для детей (буллинг); РЖЯ; «Защита близких»", "П2 и уязвимые группы"),
            ("Сбер", "Итог разговора в чат приложения (GigaChat)", "карточка случая"),
            ("Яндекс Банк", "Диалог продолжается с оператором, не откатывается к боту", "тип «Снова»"),
            ("Альфа-Банк", "Лучший контакт-центр 2026, сильная входящая линия", "голос для «Тяжело»"),
            ("Zappos", "Без скриптов и лимита на длину звонка", "своя речь вместо шаблона"),
            ("Amazon", "Andon Cord: поддержка может остановить продажу проблемного товара", "сигнал в продукт"),
            ("Apple", "A.P.P.L.E.: сначала Probe, потом Present", "шаг Н"),
            ("Ritz-Carlton", "До $2000 на гостя без согласования", "уступка по порогу"),
            ("Disney", "HEARD: Hear, Empathize, Apologize, Resolve, Diagnose", "шаги О и Л"),
            ("Monzo", "Инструменты для уязвимых клиентов в чате", "тип «Тяжело»"),
            ("FCA (Великобритания)", "FG21/1: 4 драйвера уязвимости, TEXAS и IDEA", "сигналы уязвимости"),
            ("Revolut", "Как не надо: «робот» с жертвой мошенничества, публичный скандал", "тип «Страшно» только человеку")]
    tr = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td><span class='chip c-y'>{c}</span></td></tr>" for a, b, c in rows)
    body = f'<div class="col" style="flex:1"><div class="card" style="flex:1"><table class="t s"><tr><th style="width:240px">Компания</th><th>Практика</th><th style="width:300px">Что берём в ПОНЯЛ</th></tr>{tr}</table></div></div>'
    return page(3, "Лучшие практики поддержки и что из них берём", body, "Ссылки на каждый пункт: research/03_best_practices_and_cjm_sources.md, раздел 1 и 2.", appendix=True, label="Опыт поддержки")


def a_tree():
    rows = [("А. Не понята настоящая проблема", "Первое сообщение неполное, слова означают разное", "Ищет статью по ключевым словам", "Copilot подсказывает статью, а не тип ситуации", "кейс с. 3–4; T1; R01"),
            ("", "Не учтён контекст", "Нет времени прочитать историю, ~22 диалога в день", "Метрики скорости поощряют быстрый первый ответ", "research/02; R05"),
            ("Б. Ответ верный, но это «ещё одна задача»", "Инструкция вместо действия", "Шаблон безопаснее", "Качество меряют соответствием процедуре", "Ж1 7 из 53; П2 4 из 53"),
            ("В. «Нельзя» не объяснено", "«По требованиям законодательства», нет срока", "Специалист не видит тип блокировки", "Причина у комплаенса за линией видимости", "Ж4; 115-ФЗ, 161-ФЗ"),
            ("", "Отказ без альтернативы в мелочи", "Нет полномочий или страх уступки", "Нет правила, когда уступка выгодна", "Ж10; R07"),
            ("Г. Не доведено до конца", "«Передано в отдел», сдвиг сроков", "Нет владельца случая", "Обращение закрыто, когда отправлен ответ", "Ж2, Ж7; R03, R05"),
            ("", "Клиент рассказывает заново", "Не видит прошлые диалоги", "Нет карточки случая", "R03, R05, R06"),
            ("Д. Причина в продукте не устраняется", "Тот же сбой у тысяч клиентов", "Решает частный случай", "Нет шаблона и канала «наблюдение → продукт»", "кейс с. 12; T5")]
    tr = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td style='font-size:13px'>{e}</td></tr>" for a, b, c, d, e in rows)
    body = f"""<div class="col" style="flex:1"><div class="card yl" style="padding:16px 22px"><p style="color:var(--ink);font-size:21px"><b>Уровень 1.</b> После обращения в сложной ситуации клиент уходит без ощущения, что ему помогли: пишет снова, жалуется или уходит из банка</p></div>
<div class="card" style="flex:1"><table class="t s"><tr><th>Уровень 2: почему</th><th>Уровень 3: что в диалоге</th><th>Уровень 4: почему так делает специалист</th><th>Уровень 5: причина в системе</th><th>Доказательства</th></tr>{tr}</table>
<p class="note" style="margin-top:10px">Ветки А, Б, Г закрывает поведение специалиста (шаги П, О, Н, Я). Ветки В и Д закрывают рамки: что специалисту видно и разрешено (полномочия, тип ограничения, шаблон-обоснование)</p></div></div>"""
    return page(4, "Дерево причин: 5 уровней от проблемы клиента до причины в системе", body, "analysis/01_problem_and_situations.md", appendix=True, label="Анализ проблемы")


def a_types():
    rows = [("Срочно", "платёж на кассе, за границей, нет доступа к приложению, массовый сбой", "Кейс с. 3; R01, R06; T1"),
            ("Страшно", "мошенничество, социальная инженерия, спорная операция", "возвращено 5,9% похищенного (ЦБ); Ж6; R02; T2"),
            ("Несправедливо", "блокировки 115-ФЗ и 161-ФЗ, спорные списания и комиссии, нежелательный продукт", "Ж4, Ж10; 24,7% жалоб в ЦБ; R03, R07"),
            ("Тяжело", "долг и реструктуризация, болезнь, утрата и наследство, пожилой возраст, дети", "FCA FG21/1, TEXAS; Ж9; R04, R08"),
            ("Снова", "повторное обращение, сдвинутый срок, жалоба после ответа", "SQM: каждый повтор минус 15% CSAT; Ж7; R05")]
    tr = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    body = f"""<div class="col" style="flex:1.2"><div class="card" style="flex:1"><h3>12 ситуаций из отзывов сгруппированы по тому, что нужно человеку</h3><table class="t s"><tr><th style="width:170px">Тип</th><th>Ситуации</th><th>Доказательства</th></tr>{tr}</table></div></div>
<div class="col" style="flex:.8"><div class="card" style="flex:1"><h3>Почему по потребности, а не по продукту</h3><p>Одна и та же блокировка карты бывает «Срочно» (на кассе), «Несправедливо» (115-ФЗ у ИП) и «Тяжело» (пенсионерка после звонка мошенников). Продукт подсказывает процедуру, тип подсказывает, как говорить и что сделать первым.</p>
<p style="margin-top:12px">Тип распознаётся за 1–2 сообщения по сигналам в данных и словах клиента, поэтому его может подсветить copilot, а подтвердить специалист одним кликом.</p></div></div>"""
    return page(5, "5 типов ситуаций: из каких случаев они собраны", body, "analysis/01_problem_and_situations.md, research/01 (раздел 6).", appendix=True, label="Анализ проблемы")


def a_trainer():
    rows = [("T1 «Вы можете просто помочь?»", "Срочно", "статья «причины отклонения»", "«Покупку остановила защита. Уже снял ограничение, прикладывайте карту»", "D1, D4, D6"),
            ("T2 Перевёл мошенникам 46 000 ₽", "Страшно", "«подайте заявление, до 30 дней»", "снял вину, заблокировал, запрос в банк получателя, честно о шансах, вопрос о продолжающейся атаке", "D2, D3, D4, D5"),
            ("T3 Ограничение СБП у ИП, 3-е обращение", "Несправедливо", "«по требованиям законодательства»", "тип 161-ФЗ, документы файлом, срок до 31.10, «напишу сам»", "D4, D5, D7"),
            ("T4 Пожилая клиентка и кредит «под диктовку»", "Тяжело", "длинный текст про период охлаждения", "короткие сообщения, вопрос о звонке, голос, «Защита близких»", "D2, D3, D6"),
            ("T5 Третий раз про кешбэк 1 240 ₽", "Снова", "«начисляется автоматически»", "признал повтор, начислил сейчас, передал причину разработчикам", "D1, D2, D8"),
            ("T6 98 ₽ за недоплату 5 копеек", "Несправедливо", "«согласно тарифу»", "вернул 98 ₽ (порог 809 ₽), включил автоплатёж", "D4, D8")]
    tr = "".join(f"<tr><td><b>{a}</b></td><td><span class='chip c-y'>{b}</span></td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in rows)
    body = f"""<div class="col" style="flex:1"><div class="card" style="flex:1"><table class="t s"><tr><th>Ситуация</th><th>Тип</th><th>Типичный ответ</th><th>Ответ по подходу</th><th>Решило</th></tr>{tr}</table>
<p class="note" style="margin-top:12px">D1 контекст до вопроса, D2 назвал эмоцию, D3 вопрос до инструкции, D4 план и срок, D5 честно о «нельзя», D6 без шаблона, D7 вернулся сам, D8 решил на месте. Сводка «N из 6» на слайде 3.</p></div>
<div class="card yl" style="padding:16px 22px"><p style="color:var(--ink);font-size:19px"><b>Смоделировано:</b> ситуации собраны из реальных отзывов (ссылки в research/synthetic/trainer_situations.md), оценка по нашей рубрике, а не ботом тренажёра. Реальные ситуации из тренажёра ЛК заносятся в research/05_trainer_log.md и заменяют эту таблицу.</p></div></div>"""
    return page(6, "Ситуации тренажёрного типа: что изменило исход", body, "", appendix=True, label="Тренажёр")


def a_survey():
    import csv
    rows = list(csv.DictReader(open(ROOT / "research/synthetic/survey.csv", encoding="utf-8")))
    n = len(rows)
    bad = {"стал доверять меньше", "думал уйти к другому банку", "перестал пользоваться"}
    def grp(f):
        g = [r for r in rows if f(r)]
        return sum(r["отношение_к_банку"] in bad for r in g), len(g), sum(int(r["CES_1_7"]) for r in g) / max(len(g), 1)
    cuts = [("Решено с первого обращения", grp(lambda r: r["обращений_до_решения"] == "1")),
            ("Понадобилось 2+ обращения", grp(lambda r: r["обращений_до_решения"] != "1")),
            ("Сложная ситуация", grp(lambda r: r["сложная_ситуация"] == "да")),
            ("Обычная ситуация", grp(lambda r: r["сложная_ситуация"] == "нет"))]
    cr = "".join(f"<tr><td>{a}</td><td><b>{b[0]} из {b[1]}</b></td><td><b>{b[2]:.1f}</b></td></tr>".replace(".", ",") for a, b in cuts)
    from collections import Counter
    irr = Counter(x for r in rows for x in r["раздражало"].split("; ") if x != "ничего").most_common()
    ir = "".join(f'<tr><td>{k}</td><td><span class="bar" style="width:{v * 14}px;background:var(--red)"></span> <b>{v}</b> из {n}</td></tr>' for k, v in irr)
    snaps = [("R01 Марина, Срочно", "«Я стою с пакетами, а мне присылают инструкцию»"), ("R02 Олег, Страшно", "«Мне было стыдно, а мне отвечают как будто я сам виноват»"),
             ("R03 Алексей, Несправедливо", "«Я против того, что никто не говорит, что нужно и сколько ждать»"), ("R05 Дарья, Снова", "«Каждый раз как будто первый»")]
    sn = "".join(f'<p style="margin-bottom:8px;font-size:17px"><b style="color:var(--ink)">{a}:</b> {b}</p>' for a, b in snaps)
    body = f"""<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Опрос: что раздражало ({n} ответов)</h3><table class="t s">{ir}</table></div>
<div class="card"><h3>Ключевой срез</h3><table class="t s"><tr><th>Группа</th><th>Потеряли доверие</th><th>CES, 7 = легко</th></tr>{cr}</table></div></div>
<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Интервью: 8 снимков, повторяющиеся наблюдения</h3>
<table class="t s"><tr><td>Ждали действия, а получили инструкцию</td><td><b>4 из 8</b></td></tr><tr><td>Момент «поняли» = назвал ситуацию и эмоцию</td><td><b>5 из 8</b></td></tr>
<tr><td>Неизвестность тяжелее отказа</td><td><b>4 из 8</b></td></tr><tr><td>Признаки особой ситуации видны в данных заранее</td><td><b>5 из 8</b></td></tr><tr><td>Потеря доверия после обращения</td><td><b>5 из 8</b></td></tr></table>
<div style="margin-top:14px">{sn}</div></div>
<div class="card yl" style="padding:14px 20px"><p style="color:var(--ink);font-size:17px"><b>Синтетические данные:</b> опрос сгенерирован скриптом (seed 2026) по распределениям из отзывов и бенчмарков; интервью собраны на реальных отзывах, цитаты написаны командой. Не измерения.</p></div></div>"""
    return page(7, "Синтетический опрос и интервью: повторное обращение в 2+ раза чаще ведёт к потере доверия", body,
                "research/synthetic/survey_summary.md, research/synthetic/interviews.md; вопросы анкеты по форме из чата участников секции.", appendix=True, label="Исследование")


def cjm_table(steps):
    lanes = [("Цель шага", "goal"), ("Действия", "actions"), ("Мысли и вопросы", "thoughts"), ("Эмоция −2…+2", "emotion"), ("Важность 1–3", "importance"),
             ("Причины оценок", "why"), ("Точки контакта", "touchpoints"), ("Барьеры и эффект", "barriers"), ("Источник и статус", "status"), ("С подходом ПОНЯЛ", "tobe_note")]
    head = "".join(f'<th>{s["n"]:02d}. {E(s["name"])}</th>' for s in steps)
    body = ""
    for name, key in lanes:
        cells = ""
        for s in steps:
            v = s[key]
            if key == "emotion":
                c = "c-red" if v < 0 else ("c-green" if v > 0 else "c-blue")
                marks = " ".join(f'<span class="chip c-ink">{m}</span>' for m in s["marks"])
                cells += f'<td><span class="chip {c}">{v:+d}</span> {marks}</td>'
            elif key == "importance":
                cells += f"<td><b>{v}</b></td>"
            elif key == "tobe_note":
                cells += f'<td style="background:var(--green2)">{E(v)}</td>'
            else:
                cells += f"<td>{E(v)}</td>"
        body += f'<tr><td style="background:var(--card)"><b>{name}</b></td>{cells}</tr>'
    return f'<table class="t xs" style="table-layout:fixed;font-size:16px"><tr><th style="width:150px">Дорожка</th>{head}</tr>{body}</table>'


def a_cjm():
    st = CJM["steps"]
    p1 = page(8, "CJM полностью: шаги 01–07 (проблема и первое обращение)", f'<div class="col" style="flex:1"><div class="card" style="flex:1;padding:16px">{cjm_table(st[:7])}</div></div>',
              E(CJM["basis"]), appendix=True, label="CJM")
    bp = "".join(f'<tr><td><b>{", ".join(f"{x:02d}" for x in b["steps"])}</b></td><td>{E(b["visible"])}</td><td>{E(b["backstage"])}</td><td>{E(b["systems"])}</td></tr>' for b in CJM["blueprint"])
    p2 = page(9, "CJM полностью: шаги 08–14 (ожидание, повтор, решение)", f'<div class="col" style="flex:1"><div class="card" style="flex:1;padding:16px">{cjm_table(st[7:])}</div></div>',
              "Статусы: С вторичный источник с URL, О опрос или интервью (синтетические), Г гипотеза. Метки: S стресс, R равнодушие, D потеря доверия. Шаги 08–12 при подходе ПОНЯЛ исчезают.", appendix=True, label="CJM")
    fails = "".join(f'<tr><td><span class="chip c-ink">{f["mark"]}</span></td><td><b>{E(f["where"])}</b></td><td>{E(f["what"])}</td></tr>' for f in CJM["fail_points"])
    p3 = page(10, "Service Blueprint: что видит клиент и что происходит за линией видимости", f"""<div class="col" style="flex:1"><div class="card" style="flex:1"><table class="t s"><tr><th style="width:150px">Шаги</th><th>Видимые действия банка</th><th>За кулисами (за линией видимости)</th><th>Люди и системы</th></tr>{bp}</table></div>
<div class="row"><div class="card" style="flex:1.3"><h3>Точки сбоя (fail points по Шостак)</h3><table class="t s">{fails}</table></div>
<div class="card yl" style="flex:1"><h3>Главный разрыв</h3><p style="color:var(--ink)">Тип ограничения и срок проверки живут у антифрода за линией видимости, а специалист и клиент их не видят. Поэтому подход ПОНЯЛ требует изменения 3 (тип ограничения виден специалисту), а не только новых слов.</p></div></div></div>""",
              "Шаблон Service Blueprint: NN/g, G. L. Shostack (HBR, 1984); дорожки как на доске Miro курса «UX-исследование». Внутренние процессы банка восстановлены по открытым источникам и помечены как гипотезы.", appendix=True, label="CJM")
    return p1 + p2 + p3


def a_playbook():
    rows = [("Первая фраза", "«Вижу, оплата не прошла. Уже смотрю»", "«Понимаю, как это страшно. Вы правильно сделали, что сразу написали»", "«Вижу ограничение и понимаю, что это мешает работать»", "«Я с вами, разберёмся вместе, без спешки»", "«Вижу, вы пишете третий раз. Разберусь до конца сам»"),
            ("Главный вопрос", "«Вы сейчас на кассе?»", "«Сейчас кто-то просит перевести деньги или назвать код?»", "«Какие операции нужны в первую очередь?»", "«Удобнее здесь или голосом?»", "«Что из обещанного раньше не сделано?»"),
            ("Сделать", "снять ограничение или обходной путь за минуты", "заблокировать, запрос в банк получателя, заявление за клиента, «Защита близких»", "тип ограничения, документы файлом, срок, один ответственный", "короткие сообщения, голос или РЖЯ, близкий, тон партнёра", "взять на себя, решить или дать дату и вернуться"),
            ("Не делать", "статья из базы знаний", "«вы перевели сами», обещать возврат", "«по требованиям законодательства» без шагов", "полотно текста, перекидывание", "просить те же данные"),
            ("Уступка", "обычно не нужна", "по правилам «Защитим или вернём деньги»", "по порогу, если спорно или вина банка", "реструктуризация по процедуре", "по порогу за ошибку банка")]
    tr = "".join(f"<tr><td style='background:var(--card)'><b>{r[0]}</b></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    body = f'<div class="col" style="flex:1"><div class="card" style="flex:1"><table class="t s"><tr><th style="width:160px"></th><th>Срочно</th><th>Страшно</th><th>Несправедливо</th><th>Тяжело</th><th>Снова</th></tr>{tr}</table></div></div>'
    return page(11, "Плейбук ПОНЯЛ по 5 типам ситуаций", body, "analysis/03_approach_ponyal.md", appendix=True, label="Рекомендации")


def a_options():
    rows = [("O1 Стандарты", "дёшево, эффект мал", "шаблонность растёт", "200 частых шаблонов за месяц"),
            ("O2 Тренинг", "152 млн ₽, окупаемость 10 мес.", "без инструмента эффект затухает", "8 ч, повтор раз в год"),
            ("O3 ИИ сам", "300 млн ₽, эффект около нуля", "обещания без решения, рост повторов", "только второй пилот"),
            ("O4 ПОНЯЛ", "171 млн ₽, окупаемость 3,5 мес.", "+5% времени на обращение", "пилот 1 000 специалистов"),
            ("O5 Компенсации", "минус 2,1 млрд ₽ в год", "злоупотребления, рост ожиданий", "не внедрять широко"),
            ("Рекомендация", f"{K['once']} млн ₽, окупаемость {K['payback']} мес.", "время, злоупотребления ограничены порогом", "пилот, 3 волны, 6 месяцев")]
    tr = "".join(f"<tr{' class=hl' if a == 'Рекомендация' else ''}><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)
    fac = NUM["factors"]
    fr = "".join(f"<tr><td>{f['name']}</td><td><b>{round(f['weight'] * 100)}%</b></td>" + "".join(f"<td style='text-align:center'>{s}</td>" for s in f["scores"]) + "</tr>" for f in fac)
    body = f"""<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Оценки по факторам (1–5) и веса</h3><table class="t s"><tr><th>Фактор</th><th>Вес</th><th>O1</th><th>O2</th><th>O3</th><th>O4</th><th>O5</th><th>Рек.</th></tr>{fr}</table></div></div>
<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Финансы, риски и план по каждому варианту</h3><table class="t s"><tr><th>Вариант</th><th>Финансы</th><th>Риски</th><th>План</th></tr>{tr}</table></div></div>"""
    return page(12, "Сравнение вариантов по единой структуре факторов", body, "analysis/02_options.md; финмодель, листы «Сравнение» и «Варианты».", appendix=True, label="Варианты")


def a_model():
    inp = NUM["inputs"]
    rows = [("Обращений в месяц", f"{inp['contacts'] / 1e6:.0f} млн", "кейс"), ("Закрывает ИИ", "45%", "кейс"), ("Доля сложных ситуаций у специалиста", "15%", "допущение"),
            ("Сложных обращений в год", f"{inp['hard_year'] / 1e6:.1f} млн".replace(".", ","), "расчёт"), ("Решено с первого сейчас", "55%", "допущение, SQM 69% в среднем"),
            ("Повторов на нерешённое", "1,5", "допущение"), ("Стоимость обращения", "274 ₽", "оценка: зарплата, взносы, накладные"),
            ("Прибыль активного клиента", "5 220 ₽ в год", "Т-Технологии 2025"), ("Намерение уйти: не решено / решено", "25% / 5%", "SQM Group"),
            ("Намерение, ставшее уходом", "25%", "допущение, консервативно")]
    tr = "".join(f"<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>" for a, b, c in rows)
    sens = NUM["sensitivity"]
    sh = "".join(f"<th style='text-align:center'>уход {round(c * 100)}%</th>" for c in sens[0][1:])
    sr = "".join("<tr><td><b>+" + f"{round(r[0] * 100)}" + " п.п.</b></td>" + "".join(
        f"<td style='text-align:center;{'background:var(--y2);font-weight:700' if (round(r[0] * 100) == 10 and abs(c - .25) < 1e-9) else ''}{'color:var(--red)' if v < 0 else ''}'>{round(v)}</td>"
        for c, v in zip(sens[0][1:], r[1:])) + "</tr>" for r in sens[1:])
    body = f"""<div class="col" style="flex:1"><div class="card" style="flex:1"><h3>Вводные</h3><table class="t s"><tr><th>Показатель</th><th>Значение</th><th>Источник</th></tr>{tr}</table></div></div>
<div class="col" style="flex:.9"><div class="card"><h3>Чувствительность: эффект рекомендации, млн ₽ в год</h3><table class="t s"><tr><th>Прирост FCR</th>{sh}</tr>{sr}</table>
<p class="note" style="margin-top:10px">Окупается уже при +4 п.п. и консервативной конверсии 25%. Жёлтая ячейка: базовый сценарий</p></div>
<div class="card yl"><h3>Расчёт эффекта в год</h3><p style="color:var(--ink)">повторы {K['rep']} + причины {K['fix']} + прибыль {K['profit']} − время {K['time']} − уступки {K['comp']} − сопровождение {K['yearly']} = <b>{K['yn']} млн ₽</b></p></div></div>"""
    return page(13, "Финмодель: вводные, допущения и чувствительность", body, "Excel с формулами приложен (тот же файл, что и PDF); model/build_model.py пересобирает его из вводных.", appendix=True, label="Влияние на бизнес")


def a_template():
    ex = ("1. Клиентка 6 лет, кредитная карта, просрочек не было. Тип: Несправедливо. Списано 98 ₽ за недоплату 0,05 ₽.<br>"
          "2. Без уступки ожидаем 2 повтора (548 ₽) и риск ухода. Похожих за 30 дней: проверить по тегу.<br>"
          f"3. (а) Вернуть 98 ₽: порог 0,20 x 0,25 x 5 220 ₽ + 548 ₽ = {K['thr_low']}, 98 ₽ меньше, решаю сам. (б) Не начислять штраф при недоплате меньше 1 ₽ или предлагать автоплатёж. Кому: продукт «Кредитные карты», риски.<br>"
          "4. Повторы по теме вниз, удержание клиентов с такой ситуацией вверх.<br>5. Проверить через 2 месяца: обращений в 2 раза меньше. Контроль: доля просрочек не растёт.")
    ex2 = ("1. Третье обращение (Снова): 4 покупки в «Аптеках» не попали в кешбэк, магазин передаёт другой MCC. Начислил 1 240 ₽ вручную.<br>"
           "2. 3 обращения x 274 ₽ = 822 ₽ на случай; похожих по тегу за 30 дней: взять из системы.<br>3. (б) Добавить MCC сети в правило категории. Кому: продукт «Кешбэк», ИТ.<br>"
           "4. Повторы по теме к нулю. 5. Признак: 2 недели без обращений по тегу. Контроль: расходы на кешбэк в категории.")
    body = f"""<div class="col" style="flex:.8"><div class="card y" style="flex:1"><h3>Шаблон (3–5 минут)</h3>
<p style="color:var(--ink)"><b>1. Что произошло:</b> клиент, тип ситуации, факт, ссылка на диалог<br><br><b>2. Почему важно:</b> для клиента; для банка (повторы x 274 ₽, риск ухода, жалоба); масштаб: похожих за 30 дней<br><br>
<b>3. Что предлагаю:</b> (а) для клиента, с расчётом порога; (б) для продукта или процесса и кому<br><br><b>4. Результат:</b> метрика и ожидаемое изменение, стоимость изменения<br><br><b>5. Как проверим:</b> признак, срок, что может ухудшиться</p></div></div>
<div class="col" style="flex:1.2"><div class="card" style="flex:1"><h3>Пример 1. Уступка: 98 ₽ за недоплату 5 копеек</h3><p style="font-size:18px">{ex}</p></div>
<div class="card" style="flex:1"><h3>Пример 2. Сигнал в продукт: кешбэк в категории</h3><p style="font-size:18px">{ex2}</p></div></div>"""
    return page(14, "Шаблон-обоснование для специалиста и два примера", body,
                f"docs/JUSTIFICATION_TEMPLATE.md; порог {K['thr_low']} (1 год, уход 25%) и {K['thr_high']} (3 года, 50%), лист «Порог компенсации». Выше порога и в случаях мошенничества: через руководителя.",
                appendix=True, label="Влияние на бизнес")


def a_plan():
    metrics = [("Решение с первого обращения в сложных ситуациях", "нет повтора по теме 7 дней", "время обработки, рост не больше 5%"),
               ("«Меня поняли»", "1 вопрос после диалога", "оценки после отказа"), ("CES", "«Насколько легко было решить?» 1–7", "число сообщений клиента"),
               ("Удержание", "активен через 90 дней после сложного обращения", "расходы на уступки на клиента"), ("Жалобы", "в ЦБ и финомбудсмену на 100 тыс. клиентов", "доля обоснованных"),
               ("Сигналы в продукт", "шаблонов, принятых командами", "обращения по тегу через 2 месяца")]
    mr = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in metrics)
    plan = [("0. Подготовка", "4 недели", "правила по 5 типам, формулировки с комплаенсом, порог с финансами, MVP copilot"),
            ("1. Пилот", "8 недель", "1 000 специалистов, A/B, 137 тыс. сложных обращений, 35 млн ₽; переход при +4 п.п. FCR"),
            ("2. Волны", "3 месяца", "чаты, затем звонки и вторая линия, обучение 4 часа"), ("3. Весь департамент", "6 месяцев", "20 тыс. специалистов, топ причин для продуктов")]
    pr = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in plan)
    risks = [("Время растёт больше 5%", "copilot готовит контекст заранее"), ("Злоупотребления уступками", "порог, сегмент, лимит в год, контроль"),
             ("Copilot ошибается в типе", "подсказка, специалист подтверждает"), ("Лишнее раскрытие по 115-ФЗ", "формулировки согласует комплаенс"),
             ("Допущения не подтвердятся", "пилот с контрольной группой, окупаемость уже при +4 п.п.")]
    rr = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in risks)
    body = f"""<div class="col" style="flex:1.1"><div class="card" style="flex:1"><h3>Метрики в паре с контрольными</h3><table class="t s"><tr><th>Целевая</th><th>Как считать</th><th>Контрольная</th></tr>{mr}</table></div></div>
<div class="col" style="flex:1"><div class="card"><h3>План внедрения</h3><table class="t s">{pr}</table></div><div class="card" style="flex:1"><h3>Риски и как снижаем</h3><table class="t s">{rr}</table></div></div>"""
    return page(15, "Метрики, план внедрения и риски", body, "analysis/04_business_impact.md; финмодель, лист «Пилот».", appendix=True, label="Влияние на бизнес")


def a_sources():
    src = [
        "Кейс Changellenge >> для Т-Банка «За сообщением клиента», 2026 (факты о поддержке Т-Банка)",
        "Т-Технологии, результаты по МСФО за 2025 год: tinkoff-group.com (прибыль, клиенты, MAU)",
        "Банк России: обзор жалоб и защита прав потребителей 2025, cbr.ru; операции без согласия 2025, interfax.ru, kommersant.ru",
        "ВЦИОМ, удовлетворённость клиентов банков, vedomosti.ru, 05.10.2026; Frank RG, «Банковские контакт-центры 2026», frankrg.com",
        "Frank RG и BSS, предпочитаемые каналы, itweek.ru (ID 235020); Markswebb Chatbot Rank 2025, markswebb.com",
        "Т-Банк: ИИ-сотрудник «Афанасий», cnews.ru 07.08.2026; истории поддержки tbank.ru/finance/blog/support-stories; habr.com/post/832580 (скор негатива)",
        "Сбер присылает итог звонка в чат, lenta.ru, 20.10.2026",
        "SQM Group, First Call Resolution benchmarks, sqmgroup.com; ContactBabel; Gartner (стоимость каналов, CES)",
        "Dixon, Freeman, Toman, «Stop Trying to Delight Your Customers», HBR, 2010; de Matos et al., Journal of Service Research, 2007",
        "Brynjolfsson et al., Generative AI at Work, NBER, 2023; McKinsey о корневых причинах обращений",
        "FCA FG21/1 Fair treatment of vulnerable customers, 2021; TEXAS и IDEA (Money Advice Trust); Which? о жертвах мошенничества",
        "NN/g, Journey Mapping 101 и Service Blueprints; G. L. Shostack, «Designing Services That Deliver», HBR, 1984",
        "Отзывы: banki.ru, otzovik.com, sravni.ru, irecommend.ru, brobank.ru, 1000bankov.ru, vc.ru (полный список со ссылками: research/01)",
        "Методические указания «UX-исследование», ВШБ НИУ ВШЭ, 2026 (шаблон CJM, формула инсайта, «N из M»)",
    ]
    li = "".join(f"<li style='margin-bottom:8px'>{s}</li>" for s in src)
    body = f'<div class="col" style="flex:1"><div class="card" style="flex:1"><ol style="padding-left:28px;font-size:18px;line-height:1.35;color:var(--body)">{li}</ol></div></div>'
    return page(16, "Источники", body, "Все источники со ссылками и датами: research/01, research/02, research/03.", appendix=True, label="Источники")


def main():
    slides = [s1(), s2(), s3(), s4(), s5(), s6(), s7(), s8(),
              a_method(), a_reviews(), a_practices(), a_tree(), a_types(), a_trainer(), a_survey(), a_cjm(),
              a_playbook(), a_options(), a_model(), a_template(), a_plan(), a_sources()]
    doc = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>CupMoscow2026, Т-Банк: подход ПОНЯЛ</title>'
           f"<style>{CSS}</style></head><body>{''.join(slides)}</body></html>")
    (ROOT / "deck/slides.html").write_text(doc, encoding="utf-8")
    print("deck/slides.html written")


if __name__ == "__main__":
    main()
