#!/usr/bin/env sh
# Собирает платформонезависимую инструкцию по ОДНОМУ навыку.
# Зависимости — оболочка и базовые утилиты: dirname, sed, cat, head, mkdir, mv, rm.
#
#   sh build/build.sh product-vision-interview
#
# Результат: build/<навык>/chatgpt-instructions.md — коммитится в репозиторий,
# чтобы владельцы ролей получали его готовым, без сборки на своей стороне.
#
# Одна сборка на роль. Общей сборки на несколько ролей нет: плоская инструкция
# не имеет прогрессивного раскрытия, и модель, видящая две роли в одном тексте,
# дрейфует между ними.
#
# Порядок вывода: преамбула навыка -> жёсткие запреты -> разделитель ->
# справочники в порядке build/manifest.txt навыка.
#
# Справочники ссылаются друг на друга по именам файлов. В собранном документе
# этих файлов нет — он один, — поэтому имена файлов заменяются на названия
# разделов. Название берётся из первой строки-заголовка `# ` самого справочника;
# хардкода названий в скрипте нет.

set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PLUGIN="$ROOT/plugins/sigma-mes-skills"
SKILLS="$PLUGIN/skills"

SKILL_NAME=$1

list_skills() {
  for d in "$SKILLS"/*/; do
    d=${d%/}
    echo "  ${d##*/}"
  done
}

if [ -z "$SKILL_NAME" ]; then
  echo "Укажите навык: sh build/build.sh <имя-навыка>"
  echo "Навыки в плагине:"
  list_skills
  exit 1
fi

SKILL_DIR="$SKILLS/$SKILL_NAME"

if [ ! -d "$SKILL_DIR" ]; then
  echo "Навыка «$SKILL_NAME» в плагине нет."
  echo "Навыки в плагине:"
  list_skills
  exit 1
fi

REF="$SKILL_DIR/references"
MANIFEST="$SKILL_DIR/build/manifest.txt"
PREAMBLE="$SKILL_DIR/build/preamble.md"
HARD_RULES="$SKILL_DIR/build/hard-rules.md"

OUT_DIR="$ROOT/build/$SKILL_NAME"
OUT="$OUT_DIR/chatgpt-instructions.md"
TMP="$OUT.tmp"
SED_SCRIPT="$OUT.sed"

VERSION=$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$PLUGIN/.claude-plugin/plugin.json" | head -1)

mkdir -p "$OUT_DIR"

# (1) Преамбула навыка с подстановкой версии плагина.
sed "s/{{VERSION}}/$VERSION/g" "$PREAMBLE" > "$OUT"

# (2) Жёсткие запреты — до любого справочника.
printf '\n' >> "$OUT"
cat "$HARD_RULES" >> "$OUT"

# (3) Разделитель.
printf '\n---\n' >> "$OUT"

# (4) Справочники в порядке манифеста.
while IFS= read -r name; do
  [ -n "$name" ] || continue
  src="$REF/$name.md"
  printf '\n\n<!-- ===== %s ===== -->\n\n' "$name" >> "$OUT"
  case $(sed -n '1p' "$src") in
    '<!-- СГЕНЕРИРОВАНО'*) sed '1d' "$src" >> "$OUT" ;;
    *) cat "$src" >> "$OUT" ;;
  esac
  printf '\n\n---\n' >> "$OUT"
done < "$MANIFEST"

# Имена файлов -> названия разделов этого же документа.
# Название раздела — первая строка справочника, начинающаяся с «# ».
: > "$SED_SCRIPT"

while IFS= read -r name; do
  [ -n "$name" ] || continue
  title=$(sed -n '/^# /{s/^# //p;q;}' "$REF/$name.md")
  printf 's#`references/%s\\.md`#«%s»#g\n' "$name" "$title" >> "$SED_SCRIPT"
  printf 's#references/%s\\.md#«%s»#g\n' "$name" "$title" >> "$SED_SCRIPT"
  printf 's#`%s\\.md`#«%s»#g\n' "$name" "$title" >> "$SED_SCRIPT"
done < "$MANIFEST"

cat >> "$SED_SCRIPT" <<'EXTRA'
s#в других файлах навыка#в остальных разделах этой инструкции#g
s#зафиксировано как открытый вопрос в OPEN-QUESTIONS\.md#зафиксировано как открытый вопрос к владельцу процесса#g
s#OPEN-QUESTIONS\.md#перечне открытых вопросов проекта#g
EXTRA

sed -f "$SED_SCRIPT" "$OUT" > "$TMP" && mv "$TMP" "$OUT"
rm -f "$SED_SCRIPT"

echo "Готово: $OUT (версия $VERSION)"
