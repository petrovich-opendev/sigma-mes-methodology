"""Состав разделов человеческой проекции обязан совпадать в двух носителях:
в справочнике формы (перечень «Части документа») и в шаблоне *-template.md.

Пятая итерация критики нашла ровно это: в screens.md не было раздела открытых
вопросов, хотя схема заводит open_questions и правило каркаса на них опирается;
а нумерация research.md расходилась с шаблоном (шесть пунктов против семи).
"""
import re, sys

FMT = ("plugins/sigma-mes-skills/skills/domain-model-interview/"
       "references/domain-output-format.md")
TPL = "plugins/sigma-mes-skills/skills/domain-model-interview/templates/%s-template.md"

# раздел справочника -> имя шаблона
DOCS = {"Обзор практик (research.md)": "research",
        "Концепт интерфейса (screens.md)": "screens"}

fmt = open(FMT, encoding="utf-8").read()
err = []

for heading, tpl_name in DOCS.items():
    m = re.search(r"## " + re.escape(heading) + r"\n(.*?)(?=\n## )", fmt, re.S)
    if not m:
        err.append((heading, "раздела нет в справочнике формы"))
        continue
    parts = re.findall(r"^(\d+)\.\s+\*\*(.+?)\*\*", m.group(1), re.M)
    tpl = open(TPL % tpl_name, encoding="utf-8").read()
    heads = re.findall(r"^## (\d+)\.\s+(.+)$", tpl, re.M)
    if len(parts) != len(heads):
        err.append((tpl_name, "справочник: %d частей, шаблон: %d разделов"
                    % (len(parts), len(heads))))
    for (n1, t1), (n2, t2) in zip(parts, heads):
        if n1 != n2:
            err.append((tpl_name, "нумерация: справочник %s, шаблон %s" % (n1, n2)))
        # первое слово названия должно совпадать — полные формулировки различаются
        w1 = t1.strip().split()[0].strip("*.,").lower()
        w2 = t2.strip().split()[0].strip("*.,").lower()
        if w1 != w2:
            err.append((tpl_name, "часть %s: справочник «%s», шаблон «%s»" % (n1, t1, t2)))
    print("%s: частей в справочнике %d, разделов в шаблоне %d"
          % (tpl_name, len(parts), len(heads)))

print("расхождений состава разделов:", len(err))
for e in err:
    print("   ", e)
sys.exit(1 if err else 0)
