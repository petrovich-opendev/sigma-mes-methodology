"""Ограничение 3 (statuses.md): формулировка ИИ не поднимается выше «принято к формулировке».
Проверяются ВСЕ носители: справочники, схемы, шаблоны (включая закомментированные примеры),
эталонные примеры и тесты."""
import re, subprocess, sys

ABOVE = ("зафиксировано как предложение", "утверждено ответственной ролью")
files = subprocess.run(["git", "ls-files", "*.md", "*.yaml"], capture_output=True, text=True).stdout.split()
err = []
for f in files:
    if "/build/" in f and f.endswith("chatgpt-instructions.md"):
        continue
    lines = open(f, encoding="utf-8").read().split("\n")
    # снимаем комментарий-префикс, чтобы шаблоны проверялись наравне с живым YAML
    norm = [re.sub(r"^\s*#\s?", "", l) for l in lines]
    for i, l in enumerate(norm):
        if 'formulated_by: "ИИ"' not in l:
            continue
        # границы записи: ближайший «- id:»/«- <поле>:» сверху и снизу
        lo = 0
        for j in range(i - 1, -1, -1):
            if re.match(r"\s*-\s+\w+:", norm[j]):
                lo = j
                break
        hi = len(norm)
        for j in range(i + 1, len(norm)):
            if re.match(r"\s*-\s+\w+:", norm[j]) or re.match(r"\s*```", lines[j]):
                hi = j
                break
        for j in range(lo, hi):
            m = re.search(r'confirmation_status:\s*"([^"]+)"', norm[j])
            if m and m.group(1) in ABOVE:
                # у записи должен быть общий отступ — грубая проверка одной записи
                err.append((f, j + 1, m.group(1), i + 1))
print("нарушений потолка ИИ-формулировки:", len(err))
for f, ln, st, fl in err:
    print(f"    {f}:{ln} «{st}» при formulated_by ИИ (строка {fl})")

stale = subprocess.run(["git", "grep", "-n", "-i", "обоих документов",
                        "--", ":!build/checks/"], capture_output=True, text=True).stdout.strip()
stale = [l for l in stale.split("\n") if l and "chatgpt-instructions.md" not in l]
print("упоминаний «обоих документов»:", len(stale))
for l in stale:
    print("   ", l[:160])
sys.exit(1 if err or stale else 0)
