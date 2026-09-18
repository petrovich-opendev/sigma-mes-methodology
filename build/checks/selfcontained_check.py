"""Собранная инструкция обещает быть единственным источником правил: «ссылок на внешние
файлы в нём нет, все отсылки ведут к его же разделам». Проверка держит это обещание.

Класс дефекта повторялся четырежды: справочник ссылался на раздел соседнего навыка или на
файл репозитория, которого у исполнителя на ChatGPT нет — INSTALL.md по INSTALL.md же и
не прикладывается, а две сборки в один проект класть запрещено.

Упоминания папок репозитория (templates/, shared/templates/) — не ссылки на правила, а
указание, откуда взять пустые шаблоны перед началом работы; они разрешены явным списком.
"""
import glob, re, sys

# Что искать: имя файла .md, на который сборка ссылается как на источник правила.
REF = re.compile(r"`([A-Za-z0-9\-]+\.md)`|«([А-ЯЁ][^»]{3,60}\.md)»|(INSTALL\.md|OPEN-QUESTIONS\.md|README\.md)")

# Разрешено: имена файлов-результатов и шаблонов, которые исполнитель создаёт или
# прикладывает сам. Это не отсылки к правилам.
ALLOWED = {
    "domain.md", "description.md", "research.md", "screens.md",
    "ROLE-FUNCTIONAL-OWNER.md", "architect-handoff.md",
    "domain-template.md", "description-template.md", "research-template.md",
    "screens-template.md", "architect-handoff-template.md", "role-answer-template.md",
}

err = []
for built in sorted(glob.glob("build/*/chatgpt-instructions.md")):
    skill = built.split("/")[1]
    text = open(built, encoding="utf-8").read()
    # названия разделов самого документа — по маркерам сборки
    sections = set(re.findall(r"<!-- ===== (\S+) ===== -->", text))
    for m in REF.finditer(text):
        name = m.group(1) or m.group(2) or m.group(3)
        if not name or name in ALLOWED:
            continue
        stem = name[:-3]
        if stem in sections:
            continue  # ссылка на собственный раздел этого же документа
        line = text[:m.start()].count("\n") + 1
        err.append((skill, line, name))

print("ссылок на файлы вне собранной инструкции:", len(err))
for skill, line, name in err:
    print("    %s:%d — %s" % (skill, line, name))
sys.exit(1 if err else 0)
