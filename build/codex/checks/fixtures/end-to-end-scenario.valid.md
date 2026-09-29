---
artifact_type: end-to-end-scenario
artifact_id: E2E-001
title: Пример артефакта end-to-end-scenario для проверки схемы
product_id: sigma-mes
revision: '0.1'
ai_assistance:
  plugin: sigma-mes-skills
  plugin_version: 0.11.1
  constitution_version: '0.9'
  active_role: ROLE-FUNCTIONAL-ARCHITECT
  prepared_by_ai: true
  basis:
  - ref: docs/constitution.md@0.9
    element: RULE-AI-002
  gaps: []
  approval:
    required_role: ROLE-FUNCTIONAL-ARCHITECT
    recorded: false
initial_data:
- образец значения для проверки схемы
steps:
- actor: система
  action: образец значения для проверки схемы
- actor: система
  action: образец значения для проверки схемы
expected_production_result: образец значения для проверки схемы
functions_used:
- образец значения для проверки схемы
reverification_needed: true
---

## Передать

—

## Основания и пробелы

Основание: RULE-AI-002.
