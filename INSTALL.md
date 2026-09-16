# Установка

Три независимых пути. Выбирается один, исходя из того, где ведётся диалог
с владельцем продукта: в Claude Code лично, в Claude Code командой сразу
для всех, либо вне Claude Code — в ChatGPT.

## Путь 1. Claude Code, для одного пользователя

```
/plugin marketplace add petrovich-opendev/sigma-mes-methodology
/plugin install sigma-mes-skills@sigma-mes-methodology
```

Плагин `sigma-mes-skills` ставится целиком; навыки ролей, которые в нём есть,
подключаются вместе с ним. Сейчас в плагине два навыка:
`product-vision-interview` (владелец продукта) и `domain-model-interview`
(функциональный владелец).

Если репозиторий размещён не на GitHub, а на своём хосте (например, GitLab),
маркетплейс добавляется по прямому URL:

```
/plugin marketplace add https://gitlab.example.com/<group>/sigma-mes-methodology.git
```

Дальше — та же команда `/plugin install sigma-mes-skills@sigma-mes-methodology`.

Если после установки Claude Code не увидел навык, выполните `/reload-plugins`.

**Как запустить навык.** Специально вызывать не нужно: навык подхватывается
автоматически по описанию — Claude Code включает его, когда пользователь
формулирует продуктовую идею, готовит вход к GATE-01 или меняет границы
существующего описания (см. `description` в `SKILL.md`). Если этого не
произошло, попросите прямо: «проведи продуктовое интервью» либо вызовите
команду `/product-vision-interview`.

Навык функционального владельца вызывается так же — `/domain-model-interview`
либо просьбой разобрать предметную сторону. **Он начинает работу только от
приложенного `description.yaml`**: предметная модель разворачивает продуктовые
решения, а заключение к гейту проверяет их же, и по пересказу ни того ни другого
делать нельзя. Приложите файл в первой же реплике.

**Проверка разработчиком.** Перед публикацией изменений в маркетплейсе или
плагине проверьте оба манифеста:

```
claude plugin validate .
claude plugin validate ./plugins/sigma-mes-skills
```

## Путь 2. Claude Code, командой целиком

Чтобы навыки подключались у всех участников проекта сразу после того, как они
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
    "sigma-mes-skills@sigma-mes-methodology": true
  }
}
```

Файл коммитится в репозиторий проекта. Дальнейшая работа — как в пути 1:
запуск по описанию либо прямой просьбой провести продуктовое интервью.

## Путь 3. ChatGPT, без Claude Code

Метод платформонезависим: справочники каждого навыка собраны в свой единый файл —
`build/product-vision-interview/chatgpt-instructions.md` для владельца продукта и
`build/domain-model-interview/chatgpt-instructions.md` для функционального
владельца.

1. Скопируйте содержимое сборки **одной роли** в инструкции проекта ChatGPT либо
   в поле Instructions своего Custom GPT. Две сборки в один проект не кладутся —
   см. ниже.
2. Приложите пустые шаблоны из `templates/` соответствующего навыка как
   knowledge-файлы — по ним ChatGPT воспроизводит форму результата, не изобретая
   её заново. Для продуктового навыка это `description.md` и `description.yaml`,
   для навыка функционального владельца — `domain.md`, `domain.yaml` и два шаблона
   заключения к гейту.
3. Если менялись файлы в `references/` навыка, пересоберите инструкцию заново:

   ```
   sh build/build.sh product-vision-interview
   sh build/build.sh domain-model-interview
   ```

   Результат — `build/product-vision-interview/chatgpt-instructions.md`; он
   коммитится в репозиторий, чтобы владельцы ролей получали его уже готовым,
   без сборки на своей стороне.

**Один файл сборки на роль.** У каждого навыка своя сборка в
`build/<навык>/chatgpt-instructions.md`. Объединять роли в один файл нельзя:
плоская инструкция не имеет прогрессивного раскрытия, и модель, видящая две
роли в одном тексте, дрейфует между ними. В проект ChatGPT кладётся сборка
ровно одной роли.

Если менялись общие справочники в `plugins/sigma-mes-skills/shared/references/`,
сначала разложите их по навыкам и проверьте копии:

```
sh build/sync-shared.sh
sh build/check.sh
```

## Переход с product-vision-interview 0.4.0

В версии 0.5.0 плагин переименован: был `product-vision-interview`, стал
`sigma-mes-skills`. Причина — плагин рассчитан на несколько навыков ролей, а
не на один; имя плагина перестало совпадать с именем навыка.

1. Удалите старый плагин: `/plugin uninstall product-vision-interview@sigma-mes-methodology`.
2. Обновите маркетплейс: `/plugin marketplace update sigma-mes-methodology`.
3. Установите новый: `/plugin install sigma-mes-skills@sigma-mes-methodology`.

**Имя навыка и команда не изменились.** Навык по-прежнему называется
`product-vision-interview`, команда `/product-vision-interview` работает как
раньше, девять разделов описания и форма результата те же. Изменилась
упаковка, а не методика.

Если плагин подключался командным `.claude/settings.json` (путь 2), замените
в нём ключ `"product-vision-interview@sigma-mes-methodology"` на
`"sigma-mes-skills@sigma-mes-methodology"`.

Сборка для ChatGPT переехала из `build/` в `build/product-vision-interview/`:
старый файл `build/chatgpt-instructions.md` удалён, актуальный —
`build/product-vision-interview/chatgpt-instructions.md`.

## Как обновлять

1. Поднять `version` в обоих манифестах: `.claude-plugin/marketplace.json`
   и `plugins/sigma-mes-skills/.claude-plugin/plugin.json`.
2. Пересобрать инструкцию для ChatGPT: `sh build/build.sh product-vision-interview` —
   версия попадает в шапку сборки из `plugin.json`.
3. Запушить изменения в репозиторий маркетплейса.
4. Пользователи выполняют `/plugin marketplace update`.

**Предупреждение.** Без повышения `version` в обоих манифестах установленные
у пользователей копии не обновятся, даже если содержимое навыка в
репозитории уже изменилось.
