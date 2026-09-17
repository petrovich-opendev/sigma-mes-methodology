import re, glob, yaml

files = sorted(set(
    glob.glob("plugins/**/*.md", recursive=True)
    + glob.glob("tests/**/*.md", recursive=True)
    + glob.glob("docs/*.md")
    + glob.glob("*.md")
))
n = 0
bad = []
approved = 0
missing = []
stray = []
approved_terms_bad = []
awaiting_no_request = []

for f in files:
    txt = open(f, encoding="utf-8").read()
    for m in re.finditer(r"```yaml\n(.*?)```", txt, re.S):
        n += 1
        try:
            doc = yaml.safe_load(m.group(1))
        except Exception as e:
            bad.append((f, str(e).split("\n")[0]))
            continue
        block = m.group(1)
        for it in re.split(r"\n(?=\s*- id:)", block):
            if 'confirmation_status: "утверждено ответственной ролью"' in it:
                approved += 1
                if "approved_by:" not in it:
                    missing.append((f, it.strip().split("\n")[0]))
            elif re.search(r"^\s+approved_by:", it, re.M) and "утверждено ответственной ролью" not in it:
                stray.append((f, it.strip().split("\n")[0]))
        # термины approved должны иметь definition, scope, owner_role
        for it in re.split(r"\n(?=\s*- id: TC-)", block):
            if "term_status: approved" in it:
                for need in ("definition:", "scope:", "owner_role:"):
                    if need not in it:
                        approved_terms_bad.append((f, it.strip().split("\n")[0], need))

for f in sorted(glob.glob("plugins/**/templates/*.yaml", recursive=True)):
    n += 1
    try:
        yaml.safe_load(open(f, encoding="utf-8"))
    except Exception as e:
        bad.append((f, str(e).split("\n")[0]))

print("YAML-фрагментов и файлов проверено:", n)
print("невалидных:", len(bad), bad)
print("положений «утверждено ответственной ролью»:", approved, "| без approved_by:", len(missing), missing)
print("approved_by при другом статусе:", len(stray), stray)
print("approved-термины без definition/scope/owner_role:", len(approved_terms_bad), approved_terms_bad)

import sys
sys.exit(1 if (bad or missing or stray or approved_terms_bad) else 0)
