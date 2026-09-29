<!-- Корректный пакет с блокирующими пунктами. Нужен для проверки запрета GO. -->
---
artifact_type: gate-package
artifact_id: GP-GATE-02-blocked
title: Пакет GATE-02 с блокирующими пунктами (для проверки запрета GO)
product_id: sigma-mes
revision: '0.1'
ai_assistance:
  plugin: sigma-mes-skills
  plugin_version: 0.11.2
  constitution_version: '0.9'
  active_role: ROLE-TECHNICAL-ARCHITECT
  prepared_by_ai: true
  basis:
  - ref: docs/constitution.md@0.9
    element: RULE-AI-002
  gaps: []
  approval:
    required_role: ROLE-TECHNICAL-ARCHITECT
    recorded: false
gate: GATE-02
evaluated_result: образец значения для проверки схемы
responsible_role: ROLE-TECHNICAL-ARCHITECT
required_conclusions:
- role: ROLE-FUNCTIONAL-ARCHITECT
  present: true
  ref: gates/GATE-02/rc-fa.md
- role: ROLE-VERIFICATION-OWNER
  present: false
  ref: —
- role: ROLE-INDEPENDENT-REVIEWER
  present: false
  ref: —
evidence:
- what: образец значения для проверки схемы
  ref: образец значения для проверки схемы
traceability_breaks: []
status_discrepancies: []
acceptance_outcomes:
- образец значения для проверки схемы
blocking_items:
- Нет обязательного заключения ROLE-VERIFICATION-OWNER (раздел 3.2).
- Нет обязательного заключения ROLE-INDEPENDENT-REVIEWER (раздел 3.2).
go_excluded: true
---


## Передать

—

## Основания и пробелы

Основание: RULE-AI-002.
