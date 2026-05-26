#!/usr/bin/env python3
"""
strip_refs.py — удалить все ссылки «Из урока N мы знаем, [контекст]. »
из секций Практика во всех .md файлах.

Паттерн: «Из урока N мы знаем, [что-то]. [Вопрос]»
Результат: «[Вопрос]» — только сам вопрос, без ссылки.

Запуск:
  python3 strip_refs.py          # применить изменения
  python3 strip_refs.py --dry    # показать изменения без записи
"""

import re
import os
import sys
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR   = os.path.join(BASE_DIR, 'content', 'ml')

# Паттерн: "Из урока N мы знаем, [до точки включительно]. "
# Захватываем то, что идёт после первой точки (сам вопрос)
REF_PATTERN = re.compile(
    r'Из урока \d+ мы знаем[^.]+\.\s*',
    re.UNICODE
)


def strip_refs_in_text(text: str) -> tuple[str, int]:
    """Удалить все ссылки из текста. Вернуть (новый текст, кол-во замен)."""
    new_text, count = REF_PATTERN.subn('', text)
    return new_text, count


def process_file(path: str, dry: bool) -> int:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    new_text, count = strip_refs_in_text(original)

    if count == 0:
        return 0

    if not dry:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)

    return count


def main():
    dry = '--dry' in sys.argv

    md_files = sorted(glob.glob(os.path.join(ML_DIR, '**', '*.md'), recursive=True))
    md_files = [p for p in md_files if not os.path.basename(p).startswith('_')]

    mode = 'ПРЕДПРОСМОТР' if dry else 'ПРИМЕНЕНИЕ'
    print(f'🔧 {mode}: удаление ссылок «Из урока N мы знаем...»')
    print(f'   Файлов для обработки: {len(md_files)}')
    print()

    total_files  = 0
    total_refs   = 0

    for path in md_files:
        count = process_file(path, dry)
        if count:
            rel = os.path.relpath(path, BASE_DIR)
            print(f'  • {rel}: {count} ссылок')
            total_files += 1
            total_refs  += count

    print()
    action = 'Будет удалено' if dry else 'Удалено'
    print(f'✅ {action}: {total_refs} ссылок в {total_files} файлах')

    if dry:
        print('\nЗапустите без --dry для применения.')


if __name__ == '__main__':
    main()
