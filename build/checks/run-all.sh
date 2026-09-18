#!/usr/bin/env sh
# Прогоняет все проверки согласованности методики. Запускать из корня репозитория:
#
#   sh build/checks/run-all.sh
#
# Проверки дополняют build/check.sh (тот сверяет только копии общих справочников).
# Каждая написана по следу закрытой находки: правило меняли в одном месте, а соседний
# носитель оставался с прежним текстом — и это не ловилось ничем, кроме чтения глазами.
#
# Требуется python3 с PyYAML.

set -e

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

fail=0

run() {
  name=$1
  shift
  printf '\n=== %s ===\n' "$name"
  if "$@"; then
    :
  else
    fail=1
  fi
}

run "Копии общих справочников" sh build/check.sh
run "YAML и обязательные поля разметки" python3 build/checks/validate.py
run "Инварианты модели, обзора и концепта" python3 build/checks/inv_check.py
run "Потолок статуса для формулировки ИИ" python3 build/checks/ceiling_check.py
run "Заявленные числа против факта" python3 build/checks/counts_check.py
run "Состав режимов: SKILL.md против сборки" python3 build/checks/modes_check.py
run "Состав разделов проекции против шаблона" python3 build/checks/parts_check.py
run "Реплики-триггеры: запрет против тела" python3 build/checks/triggers_check.py
run "Распространение правил по носителям" python3 build/checks/propagation_check.py
run "Самодостаточность собранных инструкций" python3 build/checks/selfcontained_check.py
run "Обязательные поля записи термина" python3 build/checks/terms_check.py
run "Правило сверки термина с реестром" python3 build/checks/rule_check.py

printf '\n'
if [ "$fail" = 0 ]; then
  echo "Все проверки пройдены."
else
  echo "Есть непройденные проверки — см. вывод выше."
  exit 1
fi
