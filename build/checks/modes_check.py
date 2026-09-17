"""Состав режимов в SKILL.md обязан присутствовать в преамбуле сборки и в собранной
инструкции: исполнитель на ChatGPT получает только её, и режим, которого там нет,
для него не существует."""
import re, sys, glob

err = []
for skill_dir in sorted(glob.glob("plugins/sigma-mes-skills/skills/*/")):
    name = skill_dir.rstrip("/").split("/")[-1]
    skill = open(skill_dir + "SKILL.md", encoding="utf-8").read()
    m = re.search(r"##\s*1\.\s*Режим и вход\n(.*?)(?=\n## )", skill, re.S)
    if not m:
        print(f"{name}: раздел «Режим и вход» не найден — режимы не перечислены явно, пропуск")
        continue
    modes = re.findall(r"^-\s+\*\*(.+?)\*\*", m.group(1), re.M)
    if not modes:
        print(f"{name}: режимы списком не заданы, пропуск")
        continue
    targets = [skill_dir + "build/preamble.md", f"build/{name}/chatgpt-instructions.md"]
    for t in targets:
        try:
            txt = re.sub(r"\s+", " ", open(t, encoding="utf-8").read())
        except FileNotFoundError:
            err.append((t, "файла нет"))
            continue
        for mode in modes:
            if re.sub(r"\s+", " ", mode) not in txt:
                err.append((t, f"режим «{mode}» отсутствует"))
    print(f"{name}: режимов в SKILL.md — {len(modes)}")

print("расхождений состава режимов:", len(err))
for t, e in err:
    print("   ", t, "—", e)
sys.exit(1 if err else 0)
