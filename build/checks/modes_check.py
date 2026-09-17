"""Состав режимов в SKILL.md обязан присутствовать в преамбуле сборки и в собранной
инструкции: исполнитель на ChatGPT получает только её, и режим, которого там нет,
для него не существует."""
import re, sys, glob

err = []
for skill_dir in sorted(glob.glob("plugins/sigma-mes-skills/skills/*/")):
    name = skill_dir.rstrip("/").split("/")[-1]
    skill = open(skill_dir + "SKILL.md", encoding="utf-8").read()
    m = (re.search(r"##\s*1\.\s*Режим и вход\n(.*?)(?=\n## )", skill, re.S)
         or re.search(r"##\s*1\.?[а-я]*\.?\s*Определение режима\n(.*?)(?=\n## )", skill, re.S))
    if not m:
        # Раздела о режимах нет вовсе — это само по себе находка: навык обязан
        # объявлять свои режимы, иначе сверять сборку не с чем.
        err.append((skill_dir + "SKILL.md", "раздел о режимах не найден"))
        continue
    # только пункты списка: жирные врезки-пояснения режимами не являются
    bullets = [ln for ln in m.group(1).split("\n") if re.match(r"\s*-\s", ln)]
    modes = []
    for ln in bullets:
        modes += [x.strip(" —:") for x in re.findall(r"\*\*([^*]+?)\*\*", ln)]
    modes = [x for x in modes if len(x) > 3]
    if not modes:
        err.append((skill_dir + "SKILL.md", "режимы в разделе не выделены — сверять нечего"))
        continue
    targets = [skill_dir + "build/preamble.md", f"build/{name}/chatgpt-instructions.md"]
    for t in targets:
        try:
            # регистр не значим: в начале предложения режим пишется с прописной
            txt = re.sub(r"\s+", " ", open(t, encoding="utf-8").read()).lower()
        except FileNotFoundError:
            err.append((t, "файла нет"))
            continue
        for mode in modes:
            if re.sub(r"\s+", " ", mode).lower() not in txt:
                err.append((t, f"режим «{mode}» отсутствует"))
    print(f"{name}: режимов в SKILL.md — {len(modes)}")

print("расхождений состава режимов:", len(err))
for t, e in err:
    print("   ", t, "—", e)
sys.exit(1 if err else 0)
