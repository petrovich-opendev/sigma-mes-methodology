#!/usr/bin/env sh
# Синхронизирует общие справочники плагина в каждый навык.
# Зависимости — оболочка и базовые утилиты: dirname, cat (printf и echo встроенные).
#
#   sh build/sync-shared.sh
#
# Источник один — plugins/sigma-mes-skills/shared/references/. Навык ссылается
# на справочник как на свой (`references/<имя>.md`), поэтому в каждом навыке
# лежит копия, сгенерированная этим скриптом и закоммиченная в репозиторий.
# Копию не редактируют: правка вносится в источник и синхронизируется заново.
# Расхождение копии с источником ловит build/check.sh.

set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PLUGIN="$ROOT/plugins/sigma-mes-skills"
SHARED="$PLUGIN/shared/references"

for src in "$SHARED"/*.md; do
  name=${src##*/}
  for skill in "$PLUGIN"/skills/*/; do
    skill_name=${skill%/}
    skill_name=${skill_name##*/}
    dst="$skill"references/"$name"
    printf '<!-- СГЕНЕРИРОВАНО build/sync-shared.sh из shared/references/%s. Не редактировать: правки вносятся в источник и синхронизируются. -->\n' "$name" > "$dst"
    cat "$src" >> "$dst"
    echo "  $skill_name/references/$name"
  done
done

echo "Готово: общие справочники разложены по навыкам."
