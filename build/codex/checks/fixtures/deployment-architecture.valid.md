---
artifact_type: deployment-architecture
artifact_id: DEP-sigma-mes
title: Пример артефакта deployment-architecture для проверки схемы
product_id: sigma-mes
revision: '0.1'
ai_assistance:
  plugin: sigma-mes-skills
  plugin_version: 0.11.3
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
  rollback: возврат к предыдущей версии из резервной копии схемы
backup_restore: образец значения для проверки схемы
monitoring_logging: образец значения для проверки схемы
---

## Передать

—

## Основания и пробелы

Основание: RULE-AI-002.
