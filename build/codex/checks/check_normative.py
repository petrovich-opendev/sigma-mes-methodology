#!/usr/bin/env python3
"""Нормативные проверки по checks/normative-checks.yaml пакета промпта 0.11.0.

Разделы: id_checks, deprecated, required_in_every_skill, forbidden_in_skills,
decision_integrity (на примерах из fixtures/), artifact_validation (правила validation
из spec/artifacts.yaml для всех 21 типа; для acceptance-record — по Q-103),
fa_technical_markers (предупреждение).

Каждая проверка печатает OK, FAIL или WARN. Код возврата 1, если есть хотя бы один FAIL.
Каталог плагина — plugins/sigma-mes-skills/, как в D-02 (Q-101 закрыт).
"""
import fnmatch
import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PLUGIN_REL = "plugins/sigma-mes-skills"
PLUGIN = os.path.join(ROOT, PLUGIN_REL)
SHARED = os.path.join(ROOT, "plugin-src/shared")
FIXTURES = os.path.join(ROOT, "build/codex/checks/fixtures")
SPEC = os.path.join(ROOT, "prompt/0.11.0/checks/normative-checks.yaml")

fails = []
warns = []


def check(name, ok, detail=""):
    if ok:
        print("%s: OK" % name)
    else:
        print("%s: FAIL: %s" % (name, detail))
        fails.append(name)


def warn(name, detail):
    print("%s: WARN: %s" % (name, detail))
    warns.append(name)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    m = re.search(r"^---\n(.*?)\n---\n", text, re.S | re.M)
    return yaml.safe_load(m.group(1)) if m else None


spec = yaml.safe_load(read(SPEC))

# ---------------------------------------------------------------- инвентарь идентификаторов
constitution = yaml.safe_load(read(os.path.join(SHARED, "constitution.extract.yaml")))
acceptance_text = read(os.path.join(SHARED, "acceptance-regulation.extract.yaml"))

known = set()
for rule in constitution["rules"]:
    known.add(rule["id"])
for role in constitution["roles"]:
    known.add(role["id"])
for term in constitution["terms"]:
    known.add(term["id"])
for gate in constitution["stages_gates"]:
    known.add(gate["gate"])
    known.add(gate["stage"])
for pat in spec["id_checks"]["patterns"].values():
    known.update(re.findall(pat, acceptance_text))
    known.update(re.findall(pat, read(os.path.join(SHARED, "constitution.extract.yaml"))))

# ---------------------------------------------------------------- файлы в области проверки
scope_files = []
for base in (PLUGIN, SHARED):
    for root, _, files in os.walk(base):
        for fname in files:
            if fname.endswith((".md", ".yaml", ".json")):
                scope_files.append(os.path.join(root, fname))

# id_checks: каждый найденный идентификатор существует в извлечениях
unknown = {}
for path in scope_files:
    text = read(path)
    for kind, pat in spec["id_checks"]["patterns"].items():
        for ident in re.findall(pat, text):
            if ident not in known:
                unknown.setdefault(ident, set()).add(os.path.relpath(path, ROOT))
check("id_checks", not unknown,
      "неизвестные идентификаторы: " + "; ".join(
          "%s (%s)" % (k, ", ".join(sorted(v))[:80]) for k, v in sorted(unknown.items())[:6]))

# deprecated: выведенные коды только в разрешённых файлах
dep = spec["deprecated"]
allowed_patterns = [p.replace("plugins/sigma-mes-skills", PLUGIN_REL)
                    for p in dep["allowed_only_in"]]
# Отступление от checks/normative-checks.yaml, записано вопросом Q-102 в OPEN-QUESTIONS.md
# плагина: пакет велит копировать свой OPEN-QUESTIONS.md в плагин (шаг 5.6), а его вопрос
# Q-06 дословно называет выведенные коды ROLE-FUNCTIONAL-OWNER и ROLE-ARCHITECT. Файл
# добавлен в исключения по той же причине, что deprecated.yaml: его предмет — сами эти коды.
# Существо правила не ослаблено: навыкам, схемам и шаблонам эти коды по-прежнему запрещены.
allowed_patterns.append("%s/OPEN-QUESTIONS.md" % PLUGIN_REL)
needles = list(dep["codes"]) + list(dep.get("also_forbidden_words", []))
violations = []
for path in scope_files:
    rel = os.path.relpath(path, ROOT)
    if any(fnmatch.fnmatch(rel, pat) for pat in allowed_patterns):
        continue
    text = read(path)
    for needle in needles:
        if needle in text:
            violations.append("%s: %s" % (rel, needle))
check("deprecated", not violations, "; ".join(sorted(set(violations))[:6]))

# required_in_every_skill
missing = []
for skill_dir in sorted(glob.glob(os.path.join(PLUGIN, "skills", "*"))):
    skill = os.path.basename(skill_dir)
    text = read(os.path.join(skill_dir, "SKILL.md"))
    for needle in spec["required_in_every_skill"]:
        if needle not in text:
            missing.append("%s: нет «%s»" % (skill, needle))
check("required_in_every_skill", not missing, "; ".join(missing))

# forbidden_in_skills
found = []
for skill_dir in sorted(glob.glob(os.path.join(PLUGIN, "skills", "*"))):
    skill = os.path.basename(skill_dir)
    text = read(os.path.join(skill_dir, "SKILL.md"))
    for needle in spec["forbidden_in_skills"]:
        if needle in text:
            found.append("%s: «%s»" % (skill, needle))
check("forbidden_in_skills", not found, "; ".join(found))

# decision_integrity — на примерах из fixtures/
problems = []
docs = {}
for path in sorted(glob.glob(os.path.join(FIXTURES, "*.md"))):
    fm = frontmatter(read(path))
    if fm:
        docs[os.path.basename(path)] = fm

packages = {name: fm for name, fm in docs.items() if fm.get("artifact_type") == "gate-package"}
for name, fm in sorted(docs.items()):
    expect_bad = ".invalid" in name
    local = []

    if fm.get("artifact_type") == "gate-decision":
        ref = str(fm.get("package_ref", ""))
        pkg = None
        for pkg_name, pkg_fm in packages.items():
            if pkg_name in ref or str(pkg_fm.get("artifact_id", "")) in ref:
                pkg = pkg_fm
                break
        if fm.get("decision") == "GO" and pkg is not None and pkg.get("go_excluded") is True:
            local.append("decision = GO при go_excluded = true в пакете (раздел 3.1)")
        if fm.get("decision") == "RETIRE" and fm.get("gate") != "GATE-05":
            local.append("RETIRE допустим только для GATE-05")

    if fm.get("artifact_type") == "deployment-architecture":
        for kind in fm.get("change_kinds") or []:
            if not str(kind.get("rollback") or "").strip():
                local.append("вид изменения «%s» без отката" % kind.get("kind"))

    if fm.get("artifact_type") == "term-proposal":
        for field in fm:
            if field in ("term_status", "status"):
                local.append("в шапке поле статуса термина: %s (раздел 5.2)" % field)

    appr = (fm.get("ai_assistance") or {}).get("approval") or {}
    if appr.get("recorded") is True and not (appr.get("statement") and appr.get("date")):
        local.append("approval.recorded = true без statement или date")

    if fm.get("artifact_type") == "gate-package":
        if bool(fm.get("blocking_items")) != bool(fm.get("go_excluded")):
            local.append("go_excluded не соответствует blocking_items")

    if expect_bad and not local:
        problems.append("%s: некорректный пример НЕ отвергнут" % name)
    if local and not expect_bad:
        problems.append("%s: %s" % (name, "; ".join(local)))
    if local and expect_bad:
        print("    отвергнут ожидаемо — %s: %s" % (name, "; ".join(local)))

check("decision_integrity", not problems, "; ".join(problems))

# ---------------------------------------------------------------- artifact_validation
# Правила validation из spec/artifacts.yaml, которые не выражаются в JSON Schema. Шаг 3.7
# главного промпта требует реализовать их здесь и перечислить в description схемы.
problems = []
GATE_RESPONSIBLE = {g["gate"]: g["responsible_role"] for g in constitution["stages_gates"]}


def body_of(path):
    text = read(path)
    m = re.search(r"^---\n.*?\n---\n(.*)$", text, re.S)
    return m.group(1) if m else text


def approval_role(fm):
    return ((fm.get("ai_assistance") or {}).get("approval") or {}).get("required_role")


def validate_artifact(name, fm, path):
    t = fm.get("artifact_type")
    out = []

    if t == "po-decision" and approval_role(fm) != "ROLE-PRODUCT-OWNER":
        out.append("решение владельца продукта фиксируется только через approval с "
                   "required_role = ROLE-PRODUCT-OWNER")
    if t == "constitution-change-proposal" and approval_role(fm) != "ROLE-RELEASE-AUTHORITY":
        out.append("approval.required_role должен быть ROLE-RELEASE-AUTHORITY (разделы 5.3, 5.4)")
    if t == "functional-requirement" and approval_role(fm) != "ROLE-FUNCTIONAL-ARCHITECT":
        out.append("включение требования фиксируется через approval с "
                   "required_role = ROLE-FUNCTIONAL-ARCHITECT (RULE-REQ-002)")

    if t == "functional-architecture":
        for obj in fm.get("objects") or []:
            if not str(obj.get("authoritative_state_source") or "").strip():
                out.append("у объекта %s не заполнен authoritative_state_source (RULE-DATA-001)"
                           % obj.get("id"))
        for inter in fm.get("interactions") or []:
            if inter.get("via") not in ("interface", "event", "reference"):
                out.append("interactions.via = %r, допустимы interface, event, reference "
                           "(RULE-SCOPE-001)" % inter.get("via"))

    if t == "practice-review":
        needle = "Обзор практик нормативным основанием не является"
        if needle not in body_of(path):
            out.append("в теле нет фразы «%s»" % needle)

    if t == "technical-constraint" and not str(fm.get("external_source_ref") or "").strip():
        out.append("без external_source_ref артефакт не создаётся (RULE-REQ-003)")

    if t == "quality-requirement":
        for head in re.findall(r"^## (.+)$", body_of(path), re.M):
            if "способ обеспечения" in head.lower():
                out.append("есть раздел о способе обеспечения — это техническая архитектура "
                           "(RULE-QUALITY-002)")

    if t == "test-design":
        for case in fm.get("test_cases") or []:
            if str(case.get("result") or "").strip() and not str(case.get("result_recorded_by") or "").strip():
                out.append("у случая %s заполнен result без result_recorded_by "
                           "(RULE-ACCEPTANCE-005)" % case.get("id"))

    if t == "acceptance-record":
        pre = fm.get("prerequisites") or {}
        outcome = fm.get("outcome")
        # Решение владельца процесса от 2026-09-29 (Q-103): без PASS и описания разработчика
        # запись приёмки готовится как проект, работа не останавливается. Существо
        # RULE-ACCEPTANCE-004 сохранено: исход без обеих предпосылок недопустим.
        if outcome:
            for field in ("tests_pass_ref", "developer_description_ref"):
                if not str(pre.get(field) or "").strip():
                    out.append("исход при отсутствии %s: передача на приёмку не выполнена "
                               "(RULE-ACCEPTANCE-004)" % field)
        recorded = ((fm.get("ai_assistance") or {}).get("approval") or {}).get("recorded")
        if outcome and recorded is not True:
            out.append("outcome заполнен без approval.recorded = true (RULE-AI-001)")
        if outcome == "ACCEPTED_WITH_REMARKS" and not (fm.get("remarks_as_work_items") or []):
            out.append("ACCEPTED_WITH_REMARKS требует remarks_as_work_items (RULE-ACCEPTANCE-006)")
        if outcome == "REJECTED_ARCHITECTURALLY" and not str(fm.get("after_rejection_decision") or "").strip():
            out.append("REJECTED_ARCHITECTURALLY требует after_rejection_decision "
                       "(RULE-FA-CHANGE-002)")

    if t == "adr":
        if fm.get("significance") == "высокая" and len(fm.get("alternatives") or []) < 2:
            out.append("significance = высокая требует не меньше двух alternatives (RULE-ARCH-001)")
        if not (fm.get("evidence") or []) and fm.get("unproven") is not True:
            out.append("нет доказательств, но решение не помечено unproven")

    if t == "c4-model":
        dsl = os.path.join(ROOT, str(fm.get("dsl_file") or ""))
        if os.path.exists(dsl):
            for line in read(dsl).splitlines():
                if re.search(r"\b(person|softwareSystem|container|component)\b", line) and "adr" not in line:
                    out.append("в workspace.dsl есть элемент без свойства adr: %s" % line.strip()[:50])
                    break
        elif fm.get("elements_without_adr") is None:
            out.append("нет ни workspace.dsl, ни перечня elements_without_adr")

    if t == "role-conclusion":
        if fm.get("reviewer_result") and fm.get("role") != "ROLE-INDEPENDENT-REVIEWER":
            out.append("reviewer_result допустим только при role = ROLE-INDEPENDENT-REVIEWER")

    if t == "gate-package":
        if approval_role(fm) != fm.get("responsible_role"):
            out.append("approval.required_role должен равняться responsible_role")
        if ((fm.get("ai_assistance") or {}).get("approval") or {}).get("recorded") is not False:
            out.append("у пакета гейта approval.recorded всегда false")

    if t == "gate-decision":
        want = GATE_RESPONSIBLE.get(fm.get("gate"))
        if want and fm.get("decided_by_role") != want:
            out.append("decided_by_role = %s, а ответственная роль %s — %s (раздел 3.2)"
                       % (fm.get("decided_by_role"), fm.get("gate"), want))

    if t == "enterprise-variant":
        for field in ("variant_owner", "justification", "return_or_termination_condition"):
            if not str(fm.get(field) or "").strip():
                out.append("нет обязательного поля %s (RULE-PRODUCT-UNITY-001)" % field)

    return out


for name in sorted(docs):
    path = os.path.join(FIXTURES, name)
    found = validate_artifact(name, docs[name], path)
    expect_bad = ".invalid" in name
    if found and not expect_bad:
        problems.append("%s: %s" % (name, "; ".join(found)))
    if found and expect_bad:
        print("    отвергнут ожидаемо — %s: %s" % (name, "; ".join(found)))
check("artifact_validation", not problems, "; ".join(problems[:6]))

# fa_technical_markers — только предупреждение
fa_skill = os.path.join(PLUGIN, "skills", "sigma-functional-architect", "SKILL.md")
text = read(fa_skill)
before_transfer = text.split("## Передача другим ролям")[0]
hits = []
for marker in spec["fa_technical_markers"]:
    for line in before_transfer.splitlines():
        if marker in line and "Передать" not in line and "Запрещено" not in line:
            hits.append("%s: %s" % (marker, line.strip()[:70]))
            break
if hits:
    warn("fa_technical_markers", "слова способа реализации вне раздела «Передать»: " +
         "; ".join(hits[:4]))
else:
    print("fa_technical_markers: OK")

print()
if warns:
    print("Предупреждения: %s" % ", ".join(warns))
if fails:
    print("Непройденные нормативные проверки: %s" % ", ".join(fails))
    sys.exit(1)
print("Все нормативные проверки пройдены.")
