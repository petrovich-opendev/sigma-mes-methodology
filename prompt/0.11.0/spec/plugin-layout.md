# Структура плагина sigma-mes-skills 0.11.0

Исполнитель создаёт ровно эти файлы. Файлы, не перечисленные здесь, не создаются.

## Дерево

```
<корень репозитория>/
├── .agents/plugins/marketplace.json            # D-02
├── plugin-src/shared/                          # единый источник общих справочников (D-05)
│   ├── session-protocol.md                     # копия spec/session-protocol.md без изменений
│   ├── constitution.extract.yaml               # копия context/constitution-v0.9.extract.yaml
│   ├── acceptance-regulation.extract.yaml      # копия context/acceptance-regulation-v0.1.extract.yaml
│   ├── codes.yaml                              # см. раздел «codes.yaml»
│   ├── deprecated.yaml                         # см. раздел «deprecated.yaml»
│   ├── config-template.yaml                    # копия spec/config-template.yaml
│   ├── artifact-schemas/<тип>.schema.json      # по одному на тип из spec/artifacts.yaml
│   └── templates/<тип>.md                      # по одному на тип из spec/artifacts.yaml
├── plugins/sigma-mes-skills/
│   ├── plugin.json                             # D-01, см. раздел «plugin.json»
│   ├── README.md                               # назначение, роли, режимы, ссылки на INSTALL.md
│   ├── INSTALL.md                              # см. раздел «INSTALL.md»
│   ├── CHANGELOG.md                            # запись 0.11.0
│   ├── OPEN-QUESTIONS.md                       # копия OPEN-QUESTIONS.md пакета + вопросы исполнителя
│   └── skills/
│       ├── sigma-product-owner/
│       │   ├── SKILL.md                        # по spec/skill-product-owner.md
│       │   └── references/                     # копия plugin-src/shared/ (создаёт sync-shared.sh)
│       ├── sigma-functional-architect/
│       │   ├── SKILL.md                        # по spec/skill-functional-architect.md
│       │   └── references/
│       ├── sigma-technical-architect/
│       │   ├── SKILL.md                        # по spec/skill-technical-architect.md
│       │   └── references/
│       └── sigma-gates/
│           ├── SKILL.md                        # по spec/skill-gates.md
│           └── references/
└── build/codex/
    ├── sync-shared.sh                          # копирует plugin-src/shared/ в references/ каждого навыка
    ├── extract_constitution.py                 # копия tools/extract_constitution.py
    └── checks/
        ├── run-all.sh                          # запускает все проверки, код возврата 0 только при успехе
        ├── check_structure.py                  # checks/structural-checks.md
        └── check_normative.py                  # checks/normative-checks.yaml
```

## plugin.json

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "sigma-mes-skills",
  "version": "0.11.0",
  "description": "Навыки ролей Конституции разработки СИГМА.MES+: владелец продукта, функциональный архитектор, технический архитектор, гейты.",
  "author": { "name": "СИГМА.MES+: владелец Конституции и процесса" },
  "license": "Proprietary",
  "keywords": ["sigma-mes", "openup", "constitution", "gates"],
  "extensions": {
    "com.openai": {
      "interface": {
        "displayName": "СИГМА.MES+ роли и гейты",
        "shortDescription": "Материалы ролей и пакеты гейтов по Конституции разработки",
        "longDescription": "Готовит материалы владельца продукта, функционального и технического архитектора и пакеты гейтов строго по действующей Конституции разработки СИГМА.MES+. Не принимает решений: утверждают профильные роли.",
        "developerName": "СИГМА.MES+",
        "category": "Productivity",
        "capabilities": ["Read", "Write"],
        "defaultPrompt": [
          "Начать работу в роли владельца продукта",
          "Начать работу в роли функционального архитектора",
          "Начать работу в роли технического архитектора",
          "Подготовить пакет гейта"
        ]
      }
    }
  }
}
```

Поле `repository` исполнитель не заполняет: адрес репозитория в GitLab — вопрос Q-04.

## codes.yaml

```yaml
built_for:
  plugin: sigma-mes-skills
  plugin_version: 0.11.0
  constitution: "0.9"
  acceptance_regulation: "0.1"
allowed_codes:            # дословно из checks/normative-checks.yaml, раздел allowed_codes
  ...
roles_in_plugin:
  - {id: ROLE-PRODUCT-OWNER, skill: sigma-product-owner}
  - {id: ROLE-FUNCTIONAL-ARCHITECT, skill: sigma-functional-architect}
  - {id: ROLE-TECHNICAL-ARCHITECT, skill: sigma-technical-architect}
mcp:
  terms_server: sigma_terms
```

## deprecated.yaml

Перечень кодов из раздела 4.3 и приложения A.5 Конституции с заменами — дословно из `constitution.extract.yaml` (роли и термины со `status: deprecated`). Это единственный файл плагина, где эти коды допустимы.

## marketplace.json

```json
{
  "name": "sigma-mes",
  "interface": { "displayName": "СИГМА.MES+" },
  "plugins": [
    {
      "name": "sigma-mes-skills",
      "source": { "source": "local", "path": "./plugins/sigma-mes-skills" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Productivity"
    }
  ]
}
```

## INSTALL.md

Разделы в таком порядке.

1. **Требования.** Персональный ПК, VPN до защищённого сегмента, ChatGPT для десктопа (режимы Codex или Work) либо Codex CLI или IDE. Обычный режим чата для работы с проектом не используется.

2. **Подключение маркетплейса:**
   ```
   codex plugin marketplace add <HTTPS-адрес репозитория плагина в GitLab>
   ```
   Затем установка из Plugins Directory в десктопном приложении или через `/plugins` в Codex. После обновления плагина — перезапуск приложения.

3. **Подключение реестра терминов** в `~/.codex/config.toml`:
   ```toml
   [mcp_servers.sigma_terms]
   url = "<HTTPS-адрес MCP реестра терминов>"        # сообщает ROLE-DOCUMENTATION-OWNER
   bearer_token_env_var = "SIGMA_TERMS_TOKEN"        # токен хранится только в переменной окружения
   default_tools_approval_mode = "writes"            # инструменты не только для чтения требуют подтверждения
   required = false
   ```
   Отдельно: список инструментов посмотреть командой `/mcp` и оставить в `enabled_tools` только инструменты чтения. Запрещено записывать токен в файлы репозитория.

4. **Конфигурация рабочего репозитория.** Скопировать `references/config-template.yaml` любого навыка в корень рабочего репозитория как `sigma-mes.config.yaml` и заполнить все заполнители `<...>`.

5. **Проверка.** `/mcp` показывает `sigma_terms`. Запуск любого навыка выполняет шаги S1–S6 протокола сеанса без ошибок.

6. **Условия применения ИИ.** Работа допускается только при опубликованных условиях (RULE-AI-001); путь — `paths.ai_use_conditions`.

## Имена и описания навыков (frontmatter SKILL.md)

Поле `description` копируется дословно из спецификации навыка. Имя навыка равно имени каталога.
