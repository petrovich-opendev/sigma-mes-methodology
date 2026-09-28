# История версий

## 0.11.0

- Переход на переносимый формат Agent Plugins для ChatGPT (режимы Codex и Work) и Codex: `plugin.json` в корне плагина, навыки в `skills/<имя>/SKILL.md`, настройки OpenAI — в `extensions.com.openai`.
- Роли по Конституции разработки СИГМА.MES+ редакции 0.9: ROLE-PRODUCT-OWNER, ROLE-FUNCTIONAL-ARCHITECT, ROLE-TECHNICAL-ARCHITECT. Один навык — одна роль.
- Добавлен навык гейтов `sigma-gates`: пакет гейта с блокирующими пунктами, формы заключений ролей без собственного навыка, запись решения ответственной роли.
- Общие справочники ведутся в `plugin-src/shared/` и копируются в `references/` каждого навыка скриптом `build/codex/sync-shared.sh`.
- Артефакты — Markdown с YAML-шапкой; для каждого типа есть JSON Schema и шаблон.
- Версия 0.10.0 для Claude Code не изменялась: её файлы остались на месте и работают как прежде.
