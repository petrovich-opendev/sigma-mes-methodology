<!-- НЕКОРРЕКТНЫЙ ПРИМЕР: у вида изменения нет поля rollback (D-14, GATE-04). Проверки обязаны его отвергнуть. -->
---
artifact_type: deployment-architecture
artifact_id: DEP-no-rollback
title: 'Некорректная архитектура развёртывания: нет отката'
product_id: sigma-mes
revision: '0.1'
ai_assistance:
  plugin: sigma-mes-skills
  plugin_version: 0.11.5
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
placement:
- образец значения для проверки схемы
change_kinds:
- kind: обновление схемы данных
  update: последовательное обновление узлов
  data_migration: миграция с проверкой контрольных сумм
backup_restore: образец значения для проверки схемы
monitoring_logging: образец значения для проверки схемы
---


## Передать

—

## Основания и пробелы

Основание: RULE-AI-002.
