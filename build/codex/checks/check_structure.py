#!/usr/bin/env python3
"""Структурные проверки S-01…S-12 по checks/structural-checks.md пакета промпта 0.11.0.

Каждая проверка печатает OK или FAIL с указанием, что именно не так. Код возврата 1,
если есть хотя бы один FAIL. Ослаблять проверки ради прохождения запрещено.

Каталог плагина — plugins/sigma-mes-codex/ (отступление от D-02, см. Q-101 в
OPEN-QUESTIONS.md плагина: по пути из D-02 уже находится плагин 0.10.1 для Claude Code).
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PLUGIN = os.path.join(ROOT, "plugins/sigma-mes-codex")
SHARED = os.path.join(ROOT, "plugin-src/shared")
PROMPT = os.path.join(ROOT, "prompt/0.11.0")
SKILLS = ["sigma-product-owner", "sigma-functional-architect",
          "sigma-technical-architect", "sigma-gates"]

fails = []


def check(name, ok, detail=""):
    if ok:
        print("%s: OK" % name)
    else:
        print("%s: FAIL: %s" % (name, detail))
        fails.append(name)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


# S-01. Манифест
try:
    man = json.loads(read(os.path.join(PLUGIN, "plugin.json")))
    problems = []
    if man.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        problems.append("$schema")
    if man.get("name") != "sigma-mes-skills":
        problems.append("name")
    if man.get("version") != "0.11.0":
        problems.append("version")
    iface = man.get("extensions", {}).get("com.openai", {}).get("interface", {})
    for field in ("displayName", "shortDescription", "longDescription", "developerName",
                  "capabilities", "defaultPrompt"):
        if not iface.get(field):
            problems.append("interface.%s" % field)
    if iface.get("category") != "Productivity":
        problems.append("interface.category")
    check("S-01", not problems, "неверные или пустые поля: " + ", ".join(problems))
except Exception as exc:  # noqa: BLE001
    check("S-01", False, "plugin.json не читается: %s" % exc)

# S-02. Нет лишних манифестов
extra = []
for name in (".codex-plugin", "hooks"):
    if os.path.isdir(os.path.join(PLUGIN, name)):
        extra.append(name + "/")
for name in ("mcp.json", ".mcp.json", ".app.json"):
    if os.path.exists(os.path.join(PLUGIN, name)):
        extra.append(name)
check("S-02", not extra, "в каталоге плагина есть лишнее: " + ", ".join(extra))

# S-03. Навыки
skills_dir = os.path.join(PLUGIN, "skills")
found = sorted(os.listdir(skills_dir)) if os.path.isdir(skills_dir) else []
problems = []
if found != sorted(SKILLS):
    problems.append("состав каталогов: %s" % ", ".join(found))
specs = {
    "sigma-product-owner": "skill-product-owner.md",
    "sigma-functional-architect": "skill-functional-architect.md",
    "sigma-technical-architect": "skill-technical-architect.md",
    "sigma-gates": "skill-gates.md",
}
for skill in SKILLS:
    path = os.path.join(skills_dir, skill, "SKILL.md")
    if not os.path.exists(path):
        problems.append("%s: нет SKILL.md" % skill)
        continue
    fm = frontmatter(read(path))
    m = re.search(r"^name:\s*(\S+)", fm, re.M)
    if not m or m.group(1) != skill:
        problems.append("%s: name в шапке не равен имени каталога" % skill)
    spec = read(os.path.join(PROMPT, "spec", specs[skill]))
    want = re.search(r"^description:\s*(.+)$", frontmatter(
        re.search(r"```yaml\n(---\n.*?\n---\n)```", spec, re.S).group(1)), re.M).group(1).strip()
    got_m = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not got_m or got_m.group(1).strip() != want:
        problems.append("%s: description не совпадает со спецификацией" % skill)
check("S-03", not problems, "; ".join(problems))

# S-04. Разделы SKILL.md — в порядке из спецификации
SECTIONS = {
    "sigma-product-owner": ["Назначение", "Протокол сеанса", "Полномочия роли", "Режимы",
                            "Границы роли", "Передача другим ролям", "Перед выдачей"],
    "sigma-functional-architect": ["Назначение", "Протокол сеанса", "Полномочия роли",
                                   "Модуль работы", "Режимы", "Границы роли",
                                   "Передача другим ролям", "Перед выдачей"],
    "sigma-technical-architect": ["Назначение", "Протокол сеанса", "Полномочия роли", "Режимы",
                                  "Границы роли", "Передача другим ролям", "Перед выдачей"],
    "sigma-gates": ["Назначение", "Протокол сеанса", "Общее правило гейта", "Гейты", "Режимы",
                    "Перед выдачей"],
}
problems = []
for skill, want in SECTIONS.items():
    text = read(os.path.join(skills_dir, skill, "SKILL.md"))
    got = re.findall(r"^## (.+)$", text, re.M)
    if got != want:
        problems.append("%s: %s" % (skill, " | ".join(got)))
check("S-04", not problems, "порядок или состав разделов не совпадает: " + "; ".join(problems))

# S-05. Режимы
MODES = {
    "sigma-product-owner": ["PO-%d" % i for i in range(1, 8)],
    "sigma-functional-architect": ["FA-%d" % i for i in range(1, 13)],
    "sigma-technical-architect": ["TA-%d" % i for i in range(1, 9)],
    "sigma-gates": ["G-%d" % i for i in range(1, 4)],
}
problems = []
for skill, codes in MODES.items():
    text = read(os.path.join(skills_dir, skill, "SKILL.md"))
    heads = re.findall(r"^### (\S+)\.", text, re.M)
    for code in codes:
        if code not in heads:
            problems.append("%s: нет заголовка режима %s" % (skill, code))
check("S-05", not problems, "; ".join(problems))

# S-06. Общие справочники разложены по навыкам с тем же SHA-256
SHARED_TOP = ["session-protocol.md", "constitution.extract.yaml",
              "acceptance-regulation.extract.yaml", "codes.yaml", "deprecated.yaml",
              "config-template.yaml", "artifact-schemas", "templates"]
problems = []
for name in SHARED_TOP:
    if not os.path.exists(os.path.join(SHARED, name)):
        problems.append("в plugin-src/shared нет %s" % name)
src = {}
for base, _, files in os.walk(SHARED):
    for fname in files:
        full = os.path.join(base, fname)
        src[os.path.relpath(full, SHARED)] = sha(full)
for skill in SKILLS:
    refs = os.path.join(skills_dir, skill, "references")
    for rel, digest in src.items():
        target = os.path.join(refs, rel)
        if not os.path.exists(target):
            problems.append("%s: нет %s" % (skill, rel))
        elif sha(target) != digest:
            problems.append("%s: %s отличается от источника" % (skill, rel))
check("S-06", not problems, "; ".join(problems[:6]))

# S-07. Протокол сеанса побайтно равен пакету
check("S-07",
      sha(os.path.join(SHARED, "session-protocol.md")) ==
      sha(os.path.join(PROMPT, "spec/session-protocol.md")),
      "session-protocol.md отличается от spec/session-protocol.md пакета")

# S-08. Извлечения побайтно равны пакету; built_for в codes.yaml
problems = []
pairs = [("constitution.extract.yaml", "context/constitution-v0.9.extract.yaml"),
         ("acceptance-regulation.extract.yaml", "context/acceptance-regulation-v0.1.extract.yaml")]
for shared_name, prompt_rel in pairs:
    if sha(os.path.join(SHARED, shared_name)) != sha(os.path.join(PROMPT, prompt_rel)):
        problems.append("%s отличается от пакета" % shared_name)
codes_text = read(os.path.join(SHARED, "codes.yaml"))
if 'constitution: "0.9"' not in codes_text:
    problems.append('built_for.constitution не равен "0.9"')
if 'acceptance_regulation: "0.1"' not in codes_text:
    problems.append('built_for.acceptance_regulation не равен "0.1"')
check("S-08", not problems, "; ".join(problems))

# S-09. Схемы и шаблоны по числу типов
try:
    import yaml
    types = yaml.safe_load(read(os.path.join(PROMPT, "spec/artifacts.yaml")))["types"]
    problems = []
    for tname in types:
        schema_path = os.path.join(SHARED, "artifact-schemas", "%s.schema.json" % tname)
        tpl_path = os.path.join(SHARED, "templates", "%s.md" % tname)
        if not os.path.exists(schema_path):
            problems.append("нет схемы %s" % tname)
        else:
            schema = json.loads(read(schema_path))
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                problems.append("%s: не draft 2020-12" % tname)
        if not os.path.exists(tpl_path):
            problems.append("нет шаблона %s" % tname)
    # Примеры с заполненными значениями обязаны проходить свою схему (fixtures/).
    try:
        import jsonschema
    except ImportError:
        problems.append("нет модуля jsonschema: python3 -m pip install --user jsonschema")
    else:
        fixtures = os.path.join(ROOT, "build/codex/checks/fixtures")
        for tname in types:
            fx = os.path.join(fixtures, "%s.valid.md" % tname)
            if not os.path.exists(fx):
                problems.append("нет корректного примера %s" % tname)
                continue
            doc = yaml.safe_load(frontmatter(read(fx)))
            schema = json.loads(read(os.path.join(SHARED, "artifact-schemas",
                                                  "%s.schema.json" % tname)))
            try:
                jsonschema.Draft202012Validator(schema).validate(doc)
            except jsonschema.ValidationError as exc:
                problems.append("пример %s не проходит схему: %s" % (tname, exc.message[:60]))
    check("S-09", not problems, "; ".join(problems[:6]))
except Exception as exc:  # noqa: BLE001
    check("S-09", False, "проверка не выполнена: %s" % exc)

# S-10. Маркетплейс
try:
    mp = json.loads(read(os.path.join(ROOT, ".agents/plugins/marketplace.json")))
    entry = mp["plugins"][0]
    path = entry["source"]["path"]
    problems = []
    if not path.startswith("./"):
        problems.append("путь не начинается с ./")
    if ".." in path:
        problems.append("в пути есть ..")
    if not os.path.isdir(os.path.join(ROOT, path)):
        problems.append("каталог %s не существует" % path)
    if entry["source"]["source"] != "local":
        problems.append("source не local")
    if entry["policy"]["installation"] != "AVAILABLE":
        problems.append("installation не AVAILABLE")
    if entry["policy"]["authentication"] != "ON_INSTALL":
        problems.append("authentication не ON_INSTALL")
    if entry.get("category") != "Productivity":
        problems.append("category не Productivity")
    check("S-10", not problems, "; ".join(problems))
except Exception as exc:  # noqa: BLE001
    check("S-10", False, "marketplace.json не читается: %s" % exc)

# S-11. INSTALL.md
install = read(os.path.join(PLUGIN, "INSTALL.md"))
problems = []
for needle in ("[mcp_servers.sigma_terms]", "bearer_token_env_var",
               'default_tools_approval_mode = "writes"', "codex plugin marketplace add",
               "sigma-mes.config.yaml"):
    if needle not in install:
        problems.append("нет фрагмента: %s" % needle)
leak = re.search(r"(?:token|Bearer)[^\n]{0,40}?([A-Za-z0-9_-]{20,})", install, re.I)
if leak:
    problems.append("строка, похожая на токен: %s" % leak.group(1)[:12])
check("S-11", not problems, "; ".join(problems))

# S-12. Версия 0.10.x не тронута
#
# В пакете проверка сравнивала с HEAD, потому что коммит не делался. После решения владельца
# процесса перевести main на 0.11.0 коммит делается, и сравнение с HEAD стало бы вакуумным:
# оно всегда пусто. База сравнения — тег предыдущего выпуска v0.10.1, а при его отсутствии
# сохраняется прежнее поведение.
OLD_PATHS = ["plugins/sigma-mes-skills", ".claude-plugin", "build/product-vision-interview",
             "build/domain-model-interview", "build/check.sh", "build/build.sh",
             "build/sync-shared.sh", "build/checks", "tests", "docs",
             "README.md", "INSTALL.md", "OPEN-QUESTIONS.md", "LICENSE"]
try:
    tag = subprocess.run(
        ["git", "-C", ROOT, "rev-parse", "--verify", "--quiet", "v0.10.1^{commit}"],
        capture_output=True, text=True).stdout.strip()
    base = tag or "HEAD"
    diff = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", base, "--"] + OLD_PATHS,
                          capture_output=True, text=True, check=True).stdout.split()
    check("S-12", not diff,
          "относительно %s изменены файлы прежней версии: %s" % (base[:8], ", ".join(diff)))
except Exception as exc:  # noqa: BLE001
    check("S-12", False, "git diff не выполнен: %s" % exc)

print()
if fails:
    print("Непройденные структурные проверки: %s" % ", ".join(fails))
    sys.exit(1)
print("Все структурные проверки пройдены.")
