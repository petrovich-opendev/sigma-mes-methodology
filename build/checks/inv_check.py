import re, glob, yaml, sys

SK = "plugins/sigma-mes-skills/skills/domain-model-interview/"


def blocks(path):
    s = open(path, encoding="utf-8").read()
    for b in re.findall(r"```yaml\n(.*?)```", s, re.S):
        try:
            d = yaml.safe_load(b)
        except Exception as e:
            print("  !! невалидный YAML в", path, str(e).split("\n")[0])
            continue
        if isinstance(d, dict):
            yield d


# модель портала: объекты и их состояния
model = {}
scenario_steps = 0
for d in blocks(SK + "examples/example-domain-model.md"):
    for o in d.get("objects", []) or []:
        model[o["id"]] = set(o.get("states") or [])
    sc = d.get("scenario")
    if isinstance(sc, dict):
        scenario_steps = len(sc.get("steps") or [])
print("объектов в модели:", len(model), "| шагов сценария:", scenario_steps)

err = []

# --- Р2: исследование ---
for d in blocks(SK + "examples/example-research.md"):
    for p in d.get("patterns", []) or []:
        prov, ver = p.get("provenance"), p.get("verification")
        if prov in ("знание навыка", "гипотеза") and ver == "подтверждено":
            err.append(("research", p["id"], f"{prov} + подтверждено"))
        has_src = "source" in p
        if prov in ("материал пользователя", "публичный источник") and not has_src:
            err.append(("research", p["id"], "нет source при " + prov))
        if prov in ("знание навыка", "гипотеза") and has_src:
            err.append(("research", p["id"], "лишний source при " + prov))
    for q in d.get("questions", []) or []:
        if not q.get("anchored_to"):
            err.append(("research", q["id"], "пустой anchored_to"))
    solved = {q["id"] for q in (d.get("questions") or []) if q.get("status") == "решён"}
    decided = {x["question"] for x in (d.get("decisions") or [])}
    for q in solved - decided:
        err.append(("research", q, "решён, но решения нет"))

# --- ссылки обзора на концепт (по ВСЕМ файлам, не только по эталонному примеру) ---
# ZN-/SC- в anchored_to, applies_to и went_to допустимы только там, где концепт
# существует: файл сам объявляет layout/screens либо это шаблон-заготовка.
import subprocess as _sp
FILES = [f for f in _sp.run(["git", "ls-files", "*.md", "*.yaml"],
                            capture_output=True, text=True).stdout.split()
         if "/build/" not in f]
for f in FILES:
    txt = open(f, encoding="utf-8").read()
    docs = list(blocks(f)) if f.endswith(".md") else []
    if f.endswith(".yaml"):
        try:
            d0 = yaml.safe_load(txt)
            if isinstance(d0, dict):
                docs = [d0]
        except Exception:
            docs = []
    for d in docs:
        has_concept = bool(d.get("layout") or d.get("screens"))
        refs = []
        for q in d.get("questions", []) or []:
            refs += [(q.get("id"), a) for a in (q.get("anchored_to") or [])]
        for x in d.get("decisions", []) or []:
            refs.append((x.get("id"), x.get("went_to")))
        for pt in d.get("patterns", []) or []:
            refs += [(pt.get("id"), a) for a in (pt.get("applies_to") or [])]
        for owner, ref in refs:
            if not isinstance(ref, str):
                continue
            if (ref.startswith("ZN-") or ref.startswith("SC-")) and not has_concept:
                err.append((f, owner, f"ссылка на концепт {ref}, а концепта в документе нет"))

# --- Р3: концепт ---
STEP_RE = re.compile(r"^E2E-\d+#\d+$")
for d in blocks(SK + "examples/example-screens.md"):
    if "screens" not in d:
        continue
    zones = {z["id"] for ly in (d.get("layout") or []) for z in (ly.get("zones") or [])}
    persistent = {z["id"] for ly in (d.get("layout") or []) for z in (ly.get("zones") or []) if z.get("persistent")}
    screen_ids = {s["id"] for s in (d.get("screens") or [])}
    for s in d.get("screens", []) or []:
        for st in s.get("scenario_steps") or []:
            if not STEP_RE.match(st):
                err.append(("screens", s["id"], "шаг не в форме E2E-NNN#N: " + st))
            else:
                n = int(st.split("#")[1])
                if scenario_steps and not (1 <= n <= scenario_steps):
                    err.append(("screens", s["id"], f"шаг {st} вне диапазона 1..{scenario_steps}"))
        for zc in s.get("zone_content") or []:
            if zc["zone"] not in zones:
                err.append(("screens", s["id"], "зона не объявлена: " + zc["zone"]))
            for o in zc.get("objects") or []:
                oid = o.get("object")
                if oid not in model:
                    err.append(("screens", s["id"], "объекта нет в domain.yaml: " + str(oid)))
                    continue
                for st_v in o.get("states_visible") or []:
                    if st_v not in model[oid]:
                        err.append(("screens", s["id"], f"состояние «{st_v}» не из списка {oid}"))
                for a in o.get("actions") or []:
                    ts = a.get("to_state")
                    if ts and ts not in model[oid]:
                        err.append(("screens", s["id"], f"to_state «{ts}» не из списка {oid}"))
                    tsc = a.get("to_screen")
                    if tsc and tsc not in screen_ids:
                        err.append(("screens", s["id"], "to_screen не существует: " + tsc))
    for u in d.get("unbound") or []:
        if not u.get("resolution"):
            err.append(("screens", u["id"], "пустой resolution"))
    rr_targets = {r.get("linked_statement") for r in (d.get("role_requests") or [])}
    rr_text = " ".join((r.get("text") or "") for r in (d.get("role_requests") or []))
    for z in persistent:
        if z not in rr_targets and z not in rr_text:
            err.append(("screens", z, "persistent-зона без запроса архитектору"))


# --- инвариант связи: цель linked_statement стоит в ролевой очереди ---
QUEUE = ("ожидает заключения роли", "ответ роли зафиксирован")
for f in FILES:
    if not f.endswith(".md"):
        continue
    # Документ в примере разнесён по нескольким блокам ```yaml — склеиваем блоки файла
    # в один псевдодокумент, иначе объект и запрос к нему попадут в разные блоки.
    merged = {}
    for d in blocks(f):
        for k, v in d.items():
            if isinstance(v, list):
                merged.setdefault(k, []).extend(v)
            else:
                merged.setdefault(k, v)
    for d in (merged,):
        marked = {}
        for key in ("screens", "objects", "statements", "domain_rules", "terms"):
            for it in (d.get(key) or []):
                if isinstance(it, dict) and it.get("id"):
                    marked[it["id"]] = it
        sc = d.get("scenario")
        if isinstance(sc, dict) and sc.get("id"):
            marked[sc["id"]] = sc
        reqs = d.get("role_requests") or []
        # Обратное направление проверяется везде, где документ вообще показывает массив
        # запросов. Прежнее послабление («справочники — сборники фрагментов, там пары
        # можно не показывать») пропустило настоящий дефект: блок, который исполнитель
        # копирует, обязан показывать пару, иначе он учит форме без запроса.
        check_reverse = "role_requests" in d
        for r in reqs:
            tgt = r.get("linked_statement")
            if not tgt or tgt not in marked:
                continue
            st = marked[tgt].get("confirmation_status")
            if st not in QUEUE:
                err.append((f, r.get("id"), f"цель {tgt} вне ролевой очереди: «{st}»"))
            elif st == "ожидает заключения роли" and not marked[tgt].get("awaiting"):
                err.append((f, r.get("id"), f"у цели {tgt} нет awaiting"))

        # Обратное направление: положение в ролевой очереди обязано иметь РОВНО ОДИН
        # парный запрос, и роль запроса совпадает с awaiting.role. Адресат без запроса
        # означает, что роль ни о чём не попросили.
        for sid, it in (marked.items() if check_reverse else ()):
            if it.get("confirmation_status") not in QUEUE:
                continue
            paired = [r for r in reqs if r.get("linked_statement") == sid]
            if len(paired) != 1:
                err.append((f, sid, f"в ролевой очереди, парных запросов {len(paired)} (нужен ровно один)"))
                continue
            aw = it.get("awaiting") or {}
            if aw.get("role") and paired[0].get("role") and aw["role"] != paired[0]["role"]:
                err.append((f, sid, f"awaiting {aw['role']}, а запрос {paired[0].get('id')} к {paired[0]['role']}"))

        # authoritative_state_source всегда стоит в ролевой очереди к ROLE-ARCHITECT
        # (domain-schema: «объект без такого запроса — незавершённая разметка»).
        for sid, it in (marked.items() if check_reverse else ()):
            if not it.get("authoritative_state_source"):
                continue
            arch = [r for r in reqs
                    if r.get("linked_statement") == sid and r.get("role") == "ROLE-ARCHITECT"]
            if not arch:
                err.append((f, sid, "есть authoritative_state_source, но нет запроса к ROLE-ARCHITECT"))

print("нарушений инвариантов:", len(err))
for e in err:
    print("   ", e)
sys.exit(1 if err else 0)
