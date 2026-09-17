"""Точная реплика-триггер, названная в «Жёстких запретах», обязана присутствовать и в
том разделе, который это правило детализирует.

Одиннадцатая итерация критики нашла асимметрию: запрет №9 требовал реплики «даю
заключение», а раздел о заключении этой фразы не содержал вовсе — в отличие от решения
по гейту, где форма и список отклоняемых мягких реплик выписаны явно.
"""
import glob, re, sys

# фраза -> в каком разделе собранной инструкции она обязана встретиться
TRIGGERS = {
    "даю заключение": "Заключение роли к гейту",
    "решение: GO": "Решение по гейту",
}

err = []
for built in sorted(glob.glob("build/*/chatgpt-instructions.md")):
    skill = built.split("/")[1]
    text = open(built, encoding="utf-8").read()
    hard = text.split("---", 1)[0]  # преамбула + жёсткие запреты идут до разделителя
    body = text.split("---", 1)[1] if "---" in text else ""
    for phrase, where in TRIGGERS.items():
        in_hard = phrase in hard
        in_body = phrase in body
        if in_hard and not in_body:
            err.append((skill, f"«{phrase}» названа в запретах, но отсутствует в теле ({where})"))
        print("%s: «%s» — запреты: %s, тело: %s"
              % (skill, phrase, "да" if in_hard else "нет", "да" if in_body else "нет"))

print("разрывов между запретом и телом:", len(err))
for e in err:
    print("   ", e)
sys.exit(1 if err else 0)
