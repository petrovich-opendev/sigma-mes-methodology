# Структурные проверки (build/codex/checks/check_structure.py)

Каждая проверка выдаёт `OK` или `FAIL: <что именно>`. `run-all.sh` завершается с кодом 0 только если все проверки `OK`. Ослаблять проверки ради прохождения запрещено.

## S-01. Манифест

`plugins/sigma-mes-skills/plugin.json`:
- валидный JSON;
- `$schema` = `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`;
- `name` = `sigma-mes-skills`;
- `version` = `0.11.0`;
- есть `extensions.com.openai.interface` с полями:
  - `displayName`, `shortDescription`, `longDescription`, `developerName`;
  - `category` = `Productivity`;
  - `capabilities`, `defaultPrompt`.

## S-02. Нет лишних манифестов

В каталоге плагина нет:
- `.codex-plugin/`;
- `mcp.json`, `.mcp.json`, `.app.json`;
- `hooks/`.

## S-03. Навыки

Ровно четыре каталога в `skills/`:
- `sigma-product-owner`;
- `sigma-functional-architect`;
- `sigma-technical-architect`;
- `sigma-gates`.

В каждом есть `SKILL.md` с YAML-шапкой:
- `name` равен имени каталога;
- `description` дословно совпадает со спецификацией навыка.

## S-04. Разделы SKILL.md

Каждый `SKILL.md` содержит заголовки разделов из своей спецификации в указанном порядке.

## S-05. Режимы

Каждый код режима из спецификации навыка присутствует в его `SKILL.md` как заголовок:
- PO-1…PO-7;
- FA-1…FA-12;
- TA-1…TA-8;
- G-1…G-3.

## S-06. Общие справочники

Каждый файл из `plugin-src/shared/` присутствует в `skills/<навык>/references/` каждого навыка с тем же SHA-256.

Состав `plugin-src/shared/`:
- `session-protocol.md`;
- `constitution.extract.yaml`;
- `acceptance-regulation.extract.yaml`;
- `codes.yaml`;
- `deprecated.yaml`;
- `config-template.yaml`;
- `artifact-schemas/`;
- `templates/`.

## S-07. Протокол сеанса

`plugin-src/shared/session-protocol.md` побайтно равен `spec/session-protocol.md` пакета промпта.

## S-08. Извлечения

`plugin-src/shared/constitution.extract.yaml` и `acceptance-regulation.extract.yaml` побайтно равны файлам `context/` пакета.

В `codes.yaml`:
- `built_for.constitution` = `"0.9"`;
- `built_for.acceptance_regulation` = `"0.1"`.

## S-09. Схемы и шаблоны

Для каждого типа из `spec/artifacts.yaml`, раздел `types`, есть:
- `artifact-schemas/<тип>.schema.json` — валидный JSON Schema draft 2020-12;
- `templates/<тип>.md`.

Шаблон с заполненными примерными значениями проходит свою схему. Тестовые примеры — в `build/codex/checks/fixtures/`.

## S-10. Маркетплейс

`.agents/plugins/marketplace.json` — валидный JSON с записью по D-02:
- `source.path` существует;
- в пути нет `..`;
- путь начинается с `./`.

## S-11. INSTALL.md

Содержит:
- фрагмент `[mcp_servers.sigma_terms]` с `bearer_token_env_var` и `default_tools_approval_mode = "writes"`;
- команду `codex plugin marketplace add`;
- указание про `sigma-mes.config.yaml`.

Не содержит строк, похожих на токен: 20 и более символов `[A-Za-z0-9_-]` подряд после `token` или `Bearer`.

## S-12. Нетронутая версия 0.10.0

`git diff --name-only HEAD` (коммит не делается, поэтому сравнение с HEAD показывает все изменения):
- пуст;
- либо содержит только `.agents/plugins/marketplace.json`, если этот файл существовал до начала работы.

Новые неотслеживаемые файлы допустимы только в каталогах из `spec/plugin-layout.md` и в `prompt/`.
