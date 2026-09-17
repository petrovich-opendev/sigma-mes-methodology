"""Правило, введённое в справочнике, обязано доехать до всех носителей, которые это же
правило пересказывают: руководства для человека (INSTALL.md, README.md), схем и тестов.

Именно этот класс дефекта петля критики ловила чаще всего: правило чинили в одном месте,
а соседний носитель оставался с прежним текстом. Таблица ниже — не полный список правил
методики, а те из них, чьи протечки уже случались: каждая строка стоит закрытой находки.
"""
import re, sys

# маркер правила -> (что обязано присутствовать рядом, в каких файлах)
RULES = [
    (
        "ветка «сам ROLE-PROCESS-OWNER не назначен»",
        r"процессн\w+ вопрос|роль без носителя|не назначена и закрыть находку некому",
        r"ROLE-PRODUCT-OWNER",
        ["INSTALL.md",
         "plugins/sigma-mes-skills/shared/references/incoming-documents.md",
         "plugins/sigma-mes-skills/shared/references/description-schema.md"],
    ),
    (
        "запросы архитектору собираются из всех четырёх документов",
        r"запрос\w* к `?ROLE-ARCHITECT|вопрос\w* к архитектору",
        r"research\.yaml|обзор практик|всех документов|всех четырёх",
        ["plugins/sigma-mes-skills/shared/references/architect-handoff.md"],
    ),
    (
        "ZN-/SC- только при приложенном концепте",
        r"anchored_to",
        r"только если концепт|только при уже собранном",
        ["plugins/sigma-mes-skills/shared/references/research-schema.md",
         "plugins/sigma-mes-skills/skills/domain-model-interview/references/domain-method.md"],
    ),
    (
        "перечень несделанного называет проектные решения (вопрос 17)",
        r"За пределами предметной модели|сознательно не передаётся|not_transferred|что не сделано и кем делается",
        r"вопрос[ау]? 17",
        ["plugins/sigma-mes-skills/skills/domain-model-interview/references/domain-method.md",
         "plugins/sigma-mes-skills/skills/domain-model-interview/SKILL.md",
         "plugins/sigma-mes-skills/skills/domain-model-interview/templates/domain-template.md",
         "plugins/sigma-mes-skills/skills/domain-model-interview/examples/example-domain-model.md",
         "plugins/sigma-mes-skills/shared/references/architect-handoff.md",
         "plugins/sigma-mes-skills/skills/product-vision-interview/references/core-method.md",
         "plugins/sigma-mes-skills/skills/product-vision-interview/examples/example-full-cycle.md"],
    ),
]

err = []
for name, marker, required, files in RULES:
    for f in files:
        try:
            text = open(f, encoding="utf-8").read()
        except FileNotFoundError:
            err.append((f, f"{name}: файла нет"))
            continue
        hits = list(re.finditer(marker, text, re.I))
        if not hits:
            err.append((f, f"{name}: маркер правила не найден — проверка могла устареть"))
            continue
        # Продолжение ищем рядом с маркером, а не где угодно в файле: упоминание той же
        # фразы в другом разделе не должно маскировать пропуск в самом перечне. Правило
        # считается выполненным, если продолжение нашлось хотя бы у одного вхождения.
        ok = any(re.search(required, text[h.start():h.start() + 2500], re.I) for h in hits)
        if not ok:
            err.append((f, f"{name}: правило упомянуто, но его продолжение отсутствует"))
        else:
            print("ok  %-70s %s" % (name, f.split("/")[-1]))

print("носителей, отставших от правила:", len(err))
for e in err:
    print("   ", e)
sys.exit(1 if err else 0)
