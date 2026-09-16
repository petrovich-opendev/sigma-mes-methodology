#!/usr/bin/env sh
# Проверяет, что копии общих справочников в навыках не разошлись с источником.
# Зависимости — оболочка и базовые утилиты: dirname, sed, diff (echo встроенный).
#
#   sh build/check.sh
#
# Две проверки на каждую пару «источник — копия»:
#   1. копия помечена строкой «СГЕНЕРИРОВАНО» — иначе её правили руками;
#   2. копия без первой строки-комментария совпадает с источником байт в байт.
#
# Код возврата 1 — расхождение найдено, имена файлов перечислены выше.

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PLUGIN="$ROOT/plugins/sigma-mes-skills"
SHARED="$PLUGIN/shared/references"

status=0
checked=0

for src in "$SHARED"/*.md; do
  name=${src##*/}
  for skill in "$PLUGIN"/skills/*/; do
    skill_name=${skill%/}
    skill_name=${skill_name##*/}
    dst="$skill"references/"$name"
    rel="plugins/sigma-mes-skills/skills/$skill_name/references/$name"

    if [ ! -f "$dst" ]; then
      echo "НЕТ КОПИИ: $rel — запустите sh build/sync-shared.sh"
      status=1
      continue
    fi

    case $(sed -n '1p' "$dst") in
      '<!-- СГЕНЕРИРОВАНО'*) ;;
      *)
        echo "КОПИЯ ОТРЕДАКТИРОВАНА ВРУЧНУЮ (нет строки СГЕНЕРИРОВАНО): $rel"
        status=1
        continue
        ;;
    esac

    if sed '1d' "$dst" | diff -q - "$src" > /dev/null; then
      checked=$((checked + 1))
    else
      echo "КОПИЯ РАСХОДИТСЯ С ИСТОЧНИКОМ: $rel"
      status=1
    fi
  done
done

if [ "$status" -eq 0 ]; then
  echo "Готово: $checked копий совпадают с источниками в shared/references/."
fi

exit "$status"
