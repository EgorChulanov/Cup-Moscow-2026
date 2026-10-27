"""Synthetic survey about bank support, anchored on public data.

The answers are SYNTHETIC: generated with fixed probabilities taken from open sources
(banki.ru and otzovik review themes, Frank RG/BSS channel survey, SQM FCR benchmarks).
They illustrate the method and the expected shape of the data; replace with real
answers when the team runs the survey (research/04_field_plan.md).

Usage: python3 research/synthetic/generate_survey.py  -> survey.csv + survey_summary.md
"""

import csv
import random
from collections import Counter
from pathlib import Path

SEED = 2026
N = 40
HERE = Path(__file__).parent

# Bank of the last contact: student sample skewed to T-Bank (assumption, our audience)
BANKS = {"Т-Банк": 0.45, "Сбер": 0.25, "Альфа-Банк": 0.12, "ВТБ": 0.08, "Озон Банк": 0.05, "Яндекс Банк": 0.05}
# Channel: Frank RG and BSS 2026, in-app chat is preferred by 64% (itweek.ru, ID=235020)
CHANNELS = {"чат в приложении": 0.64, "звонок": 0.27, "соцсети или почта": 0.09}
# Topic of contact, weights follow review themes in research/01 (blocks and disputes over-represented in complaints)
TOPICS = {
    "оплата или перевод не прошёл": 0.24,
    "блокировка карты или счёта": 0.18,
    "мошенничество": 0.10,
    "списание или комиссия": 0.16,
    "кредит": 0.10,
    "доступ к приложению": 0.12,
    "другое": 0.10,
}
# Situations that are hard by nature (research/01, section 6): lower first-contact resolution
HARD = {"блокировка карты или счёта", "мошенничество", "списание или комиссия"}
# SQM average FCR is 69%; we split it into easy 80% and hard 45% (assumption keeps the mean near 69%)
P_FIRST = {"easy": 0.80, "hard": 0.45}

IRRITANTS = [
    ("долго ждал ответа", 0.30),
    ("пришлось объяснять заново", 0.28),
    ("шаблонный ответ, не про мой вопрос", 0.33),
    ("перекидывали между сотрудниками", 0.18),
    ("отказали без понятного объяснения", 0.20),
    ("бот не понял, трудно дойти до человека", 0.25),
]

OPEN = {
    "good": [
        "Сразу посмотрел мои операции и сам всё сделал, мне не пришлось ничего искать",
        "Написал, что понимает, как неприятно, и сказал, сколько ждать. Этого хватило",
        "Не стал кидать ссылку на инструкцию, а провёл по шагам прямо в чате",
        "Вернулся сам, когда вопрос решился, я даже не успел напомнить",
    ],
    "bad": [
        "Хотелось, чтобы сначала прочитали, что я уже написал, а не задавали те же вопросы",
        "Просто объяснить честно, почему нельзя, а не отвечать «так решила система»",
        "Дать срок и потом его выполнить. Мне три раза переносили",
        "Не отправлять статью из базы знаний, я стою на кассе и мне не до чтения",
        "Перевести на человека сразу, когда видно, что бот не понимает",
        "Сказать, что делать дальше, а не просто «обращение передано»",
    ],
}


def pick(rng, weights):
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def respondent(i, rng):
    bank, channel, topic = pick(rng, BANKS), pick(rng, CHANNELS), pick(rng, TOPICS)
    hard = topic in HARD
    first = rng.random() < P_FIRST["hard" if hard else "easy"]
    contacts = 1 if first else rng.choice([2, 2, 3, 3, 4])
    resolved = "да, с первого раза" if first else rng.choice(["да, но не с первого раза"] * 3 + ["частично", "нет"])
    # Each extra contact makes irritants more likely (SQM: every repeat costs about 15% CSAT)
    boost = 0.6 if first else 1.6
    irritants = [name for name, p in IRRITANTS if rng.random() < min(p * boost, 0.9)]
    understood = "да" if first and len(irritants) <= 1 else ("частично" if len(irritants) <= 2 else "нет")
    # Customer Effort Score 1..7 (7 = very easy): falls with contacts and irritants
    ces = max(1, min(7, 7 - (contacts - 1) * 1.5 - len(irritants) * 0.8 + rng.uniform(-0.6, 0.6)))
    if first and understood == "да":
        trust = rng.choice(["стал доверять больше", "не изменилось", "не изменилось"])
    elif understood == "нет" and contacts >= 3:
        trust = rng.choice(["думал уйти к другому банку", "стал доверять меньше", "перестал пользоваться"])
    else:
        trust = rng.choice(["не изменилось", "стал доверять меньше"])
    good = understood == "да"
    return {
        "id": f"A{i:02d}",
        "банк": bank,
        "канал": channel,
        "тема": topic,
        "сложная_ситуация": "да" if hard else "нет",
        "обращений_до_решения": contacts,
        "решено": resolved,
        "CES_1_7": round(ces),
        "поняли": understood,
        "раздражало": "; ".join(irritants) or "ничего",
        "отношение_к_банку": trust,
        "что_могли_лучше": rng.choice(OPEN["good" if good else "bad"]),
    }


def summary(rows):
    n = len(rows)
    lines = [
        "# Синтетический опрос: сводка",
        "",
        f"**Данные синтетические**: {n} ответов сгенерированы скриптом `generate_survey.py` (seed {SEED}) "
        "по распределениям из открытых источников (research/01, research/02). Они иллюстрируют метод и ожидаемую "
        "форму данных и заменяются реальными ответами, когда команда проведёт опрос.",
        "",
        "Счёт ведём в людях: «N из M».",
        "",
    ]

    def block(title, key):
        c = Counter(r[key] for r in rows)
        lines.extend([f"## {title}", "", "| Ответ | N из M |", "|---|---|"])
        lines.extend(f"| {k} | {v} из {n} |" for k, v in c.most_common())
        lines.append("")

    block("Банк последнего обращения", "банк")
    block("Канал", "канал")
    block("Тема", "тема")
    block("Решено ли", "решено")
    block("Было ли ощущение, что поняли", "поняли")
    block("Как изменилось отношение к банку", "отношение_к_банку")

    irr = Counter(x for r in rows for x in r["раздражало"].split("; ") if x != "ничего")
    lines.extend(["## Что раздражало (можно несколько)", "", "| Ответ | N из M |", "|---|---|"])
    lines.extend(f"| {k} | {v} из {n} |" for k, v in irr.most_common())
    lines.append("")

    # The cut that matters for the case: what happens to trust after one vs several contacts
    def lost(group):
        bad = {"стал доверять меньше", "думал уйти к другому банку", "перестал пользоваться"}
        return sum(r["отношение_к_банку"] in bad for r in group), len(group)

    first = [r for r in rows if r["обращений_до_решения"] == 1]
    repeat = [r for r in rows if r["обращений_до_решения"] > 1]
    hard = [r for r in rows if r["сложная_ситуация"] == "да"]
    easy = [r for r in rows if r["сложная_ситуация"] == "нет"]
    ces = lambda g: sum(r["CES_1_7"] for r in g) / max(len(g), 1)
    lines.extend([
        "## Ключевые срезы",
        "",
        "| Группа | Потеряли доверие | Средний CES (7 = легко) |",
        "|---|---|---|",
        f"| решено с первого обращения | {lost(first)[0]} из {lost(first)[1]} | {ces(first):.1f} |",
        f"| понадобилось 2+ обращения | {lost(repeat)[0]} из {lost(repeat)[1]} | {ces(repeat):.1f} |",
        f"| сложная ситуация (блокировка, мошенничество, спор о списании) | {lost(hard)[0]} из {lost(hard)[1]} | {ces(hard):.1f} |",
        f"| обычная ситуация | {lost(easy)[0]} из {lost(easy)[1]} | {ces(easy):.1f} |",
        "",
    ])
    return "\n".join(lines)


def main():
    rng = random.Random(SEED)
    rows = [respondent(i + 1, rng) for i in range(N)]
    with open(HERE / "survey.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (HERE / "survey_summary.md").write_text(summary(rows), encoding="utf-8")
    print(f"{N} synthetic answers -> survey.csv, survey_summary.md")


if __name__ == "__main__":
    main()
