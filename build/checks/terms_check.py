import re, glob, yaml

REQUIRED = ("scope", "owner_role", "source")
files = sorted(set(
    glob.glob("plugins/**/*.md", recursive=True)
    + glob.glob("tests/**/*.md", recursive=True)
))
records = 0
bad = []
for f in files:
    txt = open(f, encoding="utf-8").read()
    for m in re.finditer(r"```yaml\n(.*?)```", txt, re.S):
        block = m.group(1)
        try:
            doc = yaml.safe_load(block)
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
                miss = [k for k in REQUIRED if k not in rec]
                if miss:
                    bad.append((f, rec.get("id"), miss))
print("записей терминов в примерах и справочниках:", records)
print("без обязательных полей:", len(bad))
for b in bad:
    print("   ", b)
