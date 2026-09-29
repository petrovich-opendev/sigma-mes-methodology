#!/usr/bin/env python3
"""Извлечение нормативных элементов из Конституции СИГМА.MES+ и Регламента
функциональной приёмки в машиночитаемый YAML.

Вход: .docx (через pandoc/extract-text заранее переведённый в Markdown) или .md.
Выход: YAML с разделами, правилами, ролями, этапами/гейтами, исходами приёмки,
терминами, статусами терминов и кодами проверки терминов.

Использование:
  python3 extract_constitution.py constitution <file.md> > constitution.extract.yaml
  python3 extract_constitution.py acceptance   <file.md> > acceptance-regulation.extract.yaml

Скрипт ничего не придумывает: весь текст переносится дословно. Если ожидаемый
элемент не найден, скрипт завершается с ошибкой, а не выдаёт неполный файл.
"""
import re
import sys

import yaml


class Literal(str):
    pass


def _literal(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(Literal, _literal)

FIELD_RE = re.compile(r'^\*\*(.+?):\s*\*\*\s*(.*)$')


def clean(text):
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_blocks(md):
    """Возвращает список (level, heading, body)."""
    parts = re.split(r'^(#{1,3}) (.+)$', md, flags=re.M)
    blocks = []
    for i in range(1, len(parts), 3):
        blocks.append((len(parts[i]), parts[i + 1].strip(), parts[i + 2]))
    return blocks


def parse_fields(body):
    """Поля вида **Имя: **значение и списочные поля **Имя:** + маркированный список."""
    fields, current, free = {}, None, []
    for raw in body.split('\n'):
        line = raw.strip()
        if not line:
            continue
        m = FIELD_RE.match(line)
        if m:
            name, value = m.group(1).strip(), m.group(2).strip()
            if value:
                fields[name] = value
                current = None
            else:
                fields[name] = []
                current = name
            continue
        if line.startswith('- ') and current is not None:
            item = line[2:].strip().rstrip(';').rstrip('.')
            fields[current].append(item)
            continue
        current = None
        free.append(line)
    return fields, clean('\n\n'.join(free))


def passport(md):
    out = {}
    for key in ['document_id', 'version', 'status', 'document_owner_role_id',
                'approval_authority_role_id', 'publisher_role_id', 'supersedes', 'basis']:
        m = re.search(r'\*\*' + key + r': \*\*(.+)', md)
        if m:
            out[key] = m.group(1).strip()
    return out


def constitution(md):
    blocks = split_blocks(md)
    doc = {'source': passport(md), 'sections': [], 'rules': [], 'roles': [],
           'stages_gates': [], 'acceptance_outcomes': [], 'terms': [],
           'term_statuses': {}, 'term_check_results': {}}
    for level, head, body in blocks:
        fields, free = parse_fields(body)
        rule = re.match(r'(RULE-[A-Z0-9-]+) — (.+)', head)
        role = re.match(r'(ROLE-[A-Z0-9-]+) — (.+)', head)
        gate = re.match(r'(STAGE-\d\d) / (GATE-\d\d) — (.+)', head)
        term = re.match(r'(TERM-[A-Z0-9-]+) — (.+)', head)
        outcome = re.match(r'(ACCEPTED_WITH_REMARKS|ACCEPTED|RETURNED|REJECTED_ARCHITECTURALLY) — (.+)', head)
        if rule:
            doc['rules'].append({'id': rule.group(1), 'title': rule.group(2), 'text': Literal(clean(body))})
        elif role:
            item = {'id': role.group(1), 'name': role.group(2)}
            if fields.get('Статус', '').startswith('deprecated'):
                item['status'] = 'deprecated'
                item['replacement'] = fields.get('Замена', '').rstrip('.')
            else:
                item['status'] = 'active'
                for src, dst in [('Ответственность', 'responsibility'), ('Полномочия', 'authority'),
                                 ('Соответствие OpenUP', 'openup'), ('Требование к носителю', 'carrier_requirement')]:
                    if src in fields:
                        item[dst] = fields[src]
            doc['roles'].append(item)
        elif gate:
            doc['stages_gates'].append({
                'stage': gate.group(1), 'gate': gate.group(2), 'name': gate.group(3),
                'goal': fields.get('Цель'), 'result_state': fields.get('Состояние результата'),
                'responsible_role': fields.get('Ответственная роль', '').rstrip('.'),
                'required_conclusions': fields.get('Заключения', []),
            })
        elif term:
            item = {'id': term.group(1), 'name': term.group(2)}
            if fields.get('Статус', '').startswith('deprecated'):
                item['status'] = 'deprecated'
                item['replacement'] = fields.get('Замена', '').rstrip('.')
                item['reason'] = fields.get('Причина')
            else:
                # Статус термина ведётся только в реестре терминов (приложение A.1),
                # поэтому извлечение статус не присваивает.
                item['definition'] = fields.get('Определение')
                for src, dst in [('Описывает', 'describes'), ('Определяет', 'defines'), ('Включает', 'includes')]:
                    if src in fields:
                        item[dst] = fields[src]
                item['difference'] = fields.get('Отличие')
                item['responsible_role'] = fields.get('Ответственная роль')
            doc['terms'].append(item)
        elif outcome:
            doc['acceptance_outcomes'].append({'code': outcome.group(1), 'name': outcome.group(2),
                                               'text': clean(body)})
        else:
            if head.startswith('A.1'):
                for k in ['candidate', 'approved', 'deprecated']:
                    if k in fields:
                        doc['term_statuses'][k] = fields[k]
                for k, v in fields.items():
                    if k.startswith('TERM_'):
                        doc['term_check_results'][k] = v
            if clean(body):
                doc['sections'].append({'heading': head, 'text': Literal(clean(body))})
    # контроль полноты
    need = {'rules': 30, 'roles': 18, 'stages_gates': 6, 'acceptance_outcomes': 4, 'terms': 30}
    for k, n in need.items():
        if len(doc[k]) < n:
            sys.exit(f'Ошибка извлечения: {k} = {len(doc[k])}, ожидалось не меньше {n}')
    if len(doc['term_check_results']) != 7 or len(doc['term_statuses']) != 3:
        sys.exit('Ошибка извлечения: статусы или коды проверки терминов неполны')
    doc['codes'] = {
        'gate_decisions': ['GO', 'REWORK', 'STOP'],
        'gate_decisions_gate05_extra': ['RETIRE'],
        'independent_reviewer': ['PASS', 'REWORK', 'STOP-RECOMMENDED'],
        'test_result': ['PASS', 'FAIL'],
        'acceptance_outcomes': [o['code'] for o in doc['acceptance_outcomes']],
        'term_status': list(doc['term_statuses'].keys()),
        'term_check': list(doc['term_check_results'].keys()),
    }
    return doc


def acceptance(md):
    blocks = split_blocks(md)
    doc = {'source': passport(md), 'sections': [], 'levels': [], 'principles': [], 'steps': []}
    for level, head, body in blocks:
        fields, free = parse_fields(body)
        m = re.match(r'(ACC-(LEVEL|PRINCIPLE|STEP)-\d+) — (.+)', head)
        if m:
            item = {'id': m.group(1), 'title': m.group(3), 'text': Literal(clean(body))}
            if 'Правило Конституции' in fields:
                item['constitution_rules'] = re.findall(r'RULE-[A-Z0-9-]+\d', fields['Правило Конституции'])
            key = {'LEVEL': 'levels', 'PRINCIPLE': 'principles', 'STEP': 'steps'}[m.group(2)]
            doc[key].append(item)
        elif clean(body):
            doc['sections'].append({'heading': head, 'text': Literal(clean(body))})
    if not (len(doc['levels']) == 6 and len(doc['principles']) == 10 and len(doc['steps']) == 10):
        sys.exit('Ошибка извлечения регламента: ожидалось 6 уровней, 10 принципов, 10 шагов')
    return doc


if __name__ == '__main__':
    kind, path = sys.argv[1], sys.argv[2]
    md = open(path, encoding='utf-8').read()
    data = constitution(md) if kind == 'constitution' else acceptance(md)
    sys.stdout.write('# Сгенерировано tools/extract_constitution.py. Не редактировать вручную.\n')
    yaml.dump(data, sys.stdout, allow_unicode=True, sort_keys=False, width=100)
