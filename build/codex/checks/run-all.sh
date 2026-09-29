#!/usr/bin/env sh
# Приёмка плагина sigma-mes-skills 0.11.2. Запускать из корня репозитория:
#
#   sh build/codex/checks/run-all.sh
#
# Порядок: синхронизация общих справочников, затем структурные и нормативные проверки.
# Код возврата 0 только при отсутствии FAIL. Предупреждения (WARN) прохождению не мешают.
#
# Зависимости: python3, PyYAML, jsonschema. Установка:
#   python3 -m pip install --user PyYAML jsonschema
# В системах с PEP 668 (externally managed environment) добавьте --break-system-packages.
#
# Нужен git-клон, а не распакованный архив: проверка S-12 берёт перечень файлов из git.
# Без git S-12 честно падает, а не отчитывается OK, ничего не проверив.

set -e

ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$ROOT"

fail=0

printf '=== Синхронизация общих справочников ===\n'
sh build/codex/sync-shared.sh

printf '\n=== Структурные проверки S-01…S-12 ===\n'
if python3 build/codex/checks/check_structure.py; then
  :
else
  fail=1
fi

printf '\n=== Нормативные проверки ===\n'
if python3 build/codex/checks/check_normative.py; then
  :
else
  fail=1
fi

printf '\n'
if [ "$fail" = 0 ]; then
  echo "Все проверки пройдены."
else
  echo "Есть непройденные проверки — см. вывод выше."
  exit 1
fi
