# Установка

Три независимых пути. Выбирается один, исходя из того, где ведётся диалог
с владельцем продукта: в Claude Code лично, в Claude Code командой сразу
для всех, либо вне Claude Code — в ChatGPT.

## Путь 1. Claude Code, для одного пользователя

```
/plugin marketplace add petrovich-opendev/sigma-mes-methodology
/plugin install product-vision-interview@sigma-mes-methodology
```

Если репозиторий размещён не на GitHub, а на своём хосте (например, GitLab),
маркетплейс добавляется по прямому URL:

```
/plugin marketplace add https://gitlab.example.com/<group>/sigma-mes-methodology.git
```

Дальше — та же команда `/plugin install product-vision-interview@sigma-mes-methodology`.

Если после установки Claude Code не увидел навык, выполните `/reload-plugins`.

**Как запустить навык.** Специально вызывать не нужно: навык подхватывается
автоматически по описанию — Claude Code включает его, когда пользователь
формулирует продуктовую идею, готовит вход к GATE-01 или меняет границы
существующего описания (см. `description` в `SKILL.md`). Если этого не
произошло, попросите прямо: «проведи продуктовое интервью».

**Проверка разработчиком.** Перед публикацией изменений в маркетплейсе или
плагине проверьте оба манифеста:

```
claude plugin validate .
claude plugin validate ./plugins/product-vision-interview
```

## Путь 2. Claude Code, командой целиком

Чтобы навык подключался у всех участников проекта сразу после того, как они
доверятся папке, добавьте в `.claude/settings.json` проекта:

```json
{
  "extraKnownMarketplaces": {
    "sigma-mes-methodology": {
      "source": {
        "type": "github",
        "repo": "petrovich-opendev/sigma-mes-methodology"
      }
    }
  },
  "enabledPlugins": {
    "product-vision-interview@sigma-mes-methodology": true
  }
}
```

Файл коммитится в репозиторий проекта. Дальнейшая работа — как в пути 1:
запуск по описанию либо прямой просьбой провести продуктовое интервью.

## Путь 3. ChatGPT, без Claude Code

Метод платформонезависим: тот же `references/` собран в единый файл
`build/chatgpt-instructions.md`.

1. Скопируйте содержимое `build/chatgpt-instructions.md` в инструкции проекта
   ChatGPT либо в поле Instructions своего Custom GPT.
2. Приложите пустые шаблоны `description.md` и `description.yaml` из
   `templates/` как knowledge-файлы — по ним ChatGPT воспроизводит форму
   результата (девять разделов и структуру YAML), не изобретая её заново.
3. Если менялись файлы в `references/`, пересоберите инструкцию заново:

   ```
   sh build/build-chatgpt.sh
   ```

   Результат — `build/chatgpt-instructions.md`; он коммитится в репозиторий,
   чтобы владельцы продукта получали его уже готовым, без сборки на своей
   стороне.

## Как обновлять

1. Поднять `version` в обоих манифестах: `.claude-plugin/marketplace.json`
   и `plugins/product-vision-interview/.claude-plugin/plugin.json`.
2. Запушить изменения в репозиторий маркетплейса.
3. Пользователи выполняют `/plugin marketplace update`.

**Предупреждение.** Без повышения `version` в обоих манифестах установленные
у пользователей копии не обновятся, даже если содержимое навыка в
репозитории уже изменилось.
