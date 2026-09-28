#!/usr/bin/env sh
# Копирует общие справочники из единого источника plugin-src/shared/ в references/
# каждого навыка (D-05). Правка копий вручную запрещена: копии перезаписываются.
#
#   sh build/codex/sync-shared.sh
#
# Скрипт идемпотентен: повторный запуск даёт то же дерево.

set -e

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC="$ROOT/plugin-src/shared"
PLUGIN="$ROOT/plugins/sigma-mes-codex"

if [ ! -d "$SRC" ]; then
  echo "FAIL: нет каталога $SRC"
  exit 1
fi

for skill in sigma-product-owner sigma-functional-architect sigma-technical-architect sigma-gates; do
  dst="$PLUGIN/skills/$skill/references"
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -R "$SRC"/. "$dst"/
  echo "синхронизирован: $skill"
done

echo "Готово: общие справочники разложены по четырём навыкам."
