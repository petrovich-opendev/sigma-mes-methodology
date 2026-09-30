<!-- НЕКОРРЕКТНЫЙ ПРИМЕР: GO при go_excluded = true в связанном пакете (раздел 3.1). Проверки обязаны его отвергнуть. -->
---
artifact_type: gate-decision
artifact_id: GD-GATE-02-blocked
title: 'Некорректное решение: GO при блокирующих пунктах'
product_id: sigma-mes
revision: '0.1'
ai_assistance:
  plugin: sigma-mes-skills
  plugin_version: 0.11.4
  constitution_version: '0.9'
  active_role: ROLE-TECHNICAL-ARCHITECT
  prepared_by_ai: true
  basis:
  - ref: docs/constitution.md@0.9
    element: RULE-AI-002
  gaps: []
  approval:
    required_role: ROLE-TECHNICAL-ARCHITECT
    recorded: true
    statement: 'Решение: GO'
    date: '2026-09-28'
gate: GATE-02
package_ref: gate-package.blocked.md
decision: GO
decided_by_role: ROLE-TECHNICAL-ARCHITECT
---


## Передать

—

## Основания и пробелы

Основание: RULE-AI-002.
