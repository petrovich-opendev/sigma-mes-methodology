import re, glob, yaml

# Правило Д1: check_result присутствует ТОЛЬКО когда слово совпало с реестром
# (scope «уровень Конституции» либо явный technical_id). Иначе поля быть не должно.
files = sorted(set(glob.glob("plugins/**/*.md", recursive=True) + glob.glob("tests/**/*.md", recursive=True)))
records = 0
bad = []
for f in files:
    txt = open(f, encoding="utf-8").read()
    for m in re.finditer(r"```yaml\n(.*?)```", txt, re.S):
        try:
            doc = yaml.safe_load(m.group(1))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        for key in ("term_candidates", "terms"):
            arr = doc.get(key)
            if not isinstance(arr, list):
                continue
            for rec in arr:
                if not isinstance(rec, dict) or not str(rec.get("id", "")).startswith("TC-"):
                    continue
                records += 1
                matched = ("technical_id" in rec) or (rec.get("scope") == "уровень Конституции")
                has = "check_result" in rec
                if has and not matched:
                    bad.append((f, rec.get("id"), "check_result есть, а совпадения с реестром нет"))
                if matched and not has:
                    bad.append((f, rec.get("id"), "совпадение с реестром есть, а check_result нет"))
                if rec.get("check_result") == "TERM_NOT_DEFINED":
                    bad.append((f, rec.get("id"), "TERM_NOT_DEFINED не ставится никогда"))
print("записей терминов:", records)
print("нарушений правила сверки:", len(bad))
for b in bad:
    print("   ", b)
