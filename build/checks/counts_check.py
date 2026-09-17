"""Заявленные числа (сценарии, справочники) обязаны совпадать с фактом.

Написанное словами число отстаёт молча: «собран из десяти справочников» пережило
четыре пополнения манифеста, а «тридцать один сценарий» — три итерации критики.
"""
import re, glob, sys

WORDS = {6: "шесть", 10: "десять", 12: "двенадцать", 14: "четырнадцать",
         16: "шестнадцать", 31: "тридцать один", 34: "тридцать четыре",
         35: "тридцать пять", 36: "тридцать шесть", 37: "тридцать семь",
         38: "тридцать восемь"}
err = []

for d in sorted(glob.glob("tests/*/")):
    name = d.rstrip("/").split("/")[-1]
    import os
    if not os.path.exists(d + "scenarios.md"):
        continue
    sc = open(d + "scenarios.md", encoding="utf-8").read()
    eb = open(d + "expected-behaviour.md", encoding="utf-8").read()
    n_sc = len(re.findall(r"^## \d+\.", sc, re.M))
    n_eb = len(re.findall(r"^## \d+\.", eb, re.M))
    if n_sc != n_eb:
        err.append((name, "scenarios %d != expected-behaviour %d" % (n_sc, n_eb)))
    word = WORDS.get(n_sc)
    if word is None:
        err.append((name, "числительного для %d нет в словаре проверки — молча пропустить нельзя" % n_sc))
    if word and word not in eb:
        m = re.search(r"те же (.+?) (?:номер|заголов)", eb)
        err.append((d + "expected-behaviour.md",
                    "заявлено «%s», фактически %d (%s)" % (m.group(1) if m else "?", n_sc, word)))
    # README: берём строку scenarios.md под ближайшим ВЫШЕ заголовком навыка,
    # иначе нежадный поиск цепляется к соседней секции
    lines = open("README.md", encoding="utf-8").read().split("\n")
    cur = None
    for ln in lines:
        m_dir = re.match(r"\s{2}(\S+)/\s*$", ln)
        if m_dir:
            cur = m_dir.group(1)
        m_sc = re.search(r"scenarios\.md\s+—\s+(.+?)\s+сценари", ln)
        if m_sc and cur == name and word and word not in m_sc.group(1):
            err.append(("README.md", "для %s заявлено «%s», фактически %s"
                        % (name, m_sc.group(1), word)))
    print("%s: сценариев %d" % (name, n_sc))

for man in sorted(glob.glob("plugins/sigma-mes-skills/skills/*/build/manifest.txt")):
    skill = man.split("/")[-3]
    n = len([l for l in open(man, encoding="utf-8") if l.strip()])
    built = open("build/%s/chatgpt-instructions.md" % skill, encoding="utf-8").read()
    marks = len(re.findall(r"<!-- =====", built))
    if marks != n:
        err.append((skill, "манифест %d != разделов в сборке %d" % (n, marks)))
    m = re.search(r"собран из (\S+) справочник", built)
    stated = m.group(1) if m else "?"
    if m and stated != str(n):
        err.append((skill, "в сборке сказано «из %s», а справочников %d" % (stated, n)))
    print("%s: справочников %d, разделов в сборке %d, в тексте «%s»" % (skill, n, marks, stated))

print("расхождений чисел:", len(err))
for e in err:
    print("   ", e)
sys.exit(1 if err else 0)
