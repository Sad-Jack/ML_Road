#!/usr/bin/env python3
"""
build.py — синхронизация content/ → ml_road.html

Читает все .md файлы из папки content/ и вшивает их обратно
в соответствующие <script id="cdata-XXX"> блоки в ml_road.html.

Использование:
    python3 build.py              # синхронизировать все уроки
    python3 build.py l05 l20      # синхронизировать только указанные уроки
    python3 build.py --check      # проверить расхождения без изменений
"""

import re
import os
import sys
import glob

HTML_FILE = os.path.join(os.path.dirname(__file__), 'ml_road.html')
CONTENT_DIR = os.path.join(os.path.dirname(__file__), 'content')

# Поиск ведётся рекурсивно внутри content/ml/ и content/python/


def find_md_file(lesson_id: str) -> str | None:
    """Найти .md файл для урока по его id (например 'l05', 'pd01')."""
    pattern = os.path.join(CONTENT_DIR, '**', f'{lesson_id}_*.md')
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        return None
    if len(matches) > 1:
        print(f'  ⚠️  Найдено несколько файлов для {lesson_id}: {matches}')
    return matches[0]


def get_all_lesson_ids() -> list[str]:
    """Получить список всех id уроков из content/."""
    ids = []
    for path in glob.glob(os.path.join(CONTENT_DIR, '**', '*.md'), recursive=True):
        filename = os.path.basename(path)
        m = re.match(r'^(l\d+|pd\d+)_', filename)
        if m:
            ids.append(m.group(1))
    return sorted(ids)


def inject(html: str, lesson_id: str, new_content: str) -> tuple[str, bool]:
    """Заменить содержимое cdata-блока в HTML. Возвращает (новый html, был_ли_изменён)."""
    pattern = rf'(<script[^>]*id="cdata-{lesson_id}"[^>]*>)(.*?)(</script>)'
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        return html, False

    old_content = m.group(2)
    # Нормализуем: убираем ведущие/хвостовые пробелы, добавляем единый отступ
    normalized_new = '\n' + new_content.strip() + '\n'

    if old_content == normalized_new:
        return html, False  # без изменений

    new_html = html[:m.start()] + m.group(1) + normalized_new + m.group(3) + html[m.end():]
    return new_html, True


def main():
    args = sys.argv[1:]
    check_only = '--check' in args
    if check_only:
        args.remove('--check')

    # Определяем какие уроки обрабатывать
    if args:
        lesson_ids = args
    else:
        lesson_ids = get_all_lesson_ids()

    print(f'📂 content/ → ml_road.html')
    print(f'   Режим: {"проверка" if check_only else "запись"}')
    print(f'   Уроков: {len(lesson_ids)}')
    print()

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    changed = []
    missing = []
    not_found_in_html = []

    for lid in lesson_ids:
        md_path = find_md_file(lid)
        if not md_path:
            missing.append(lid)
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        new_html, was_changed = inject(html, lid, md_content)

        if was_changed:
            changed.append(lid)
            if not check_only:
                html = new_html
        elif md_path and not re.search(rf'id="cdata-{lid}"', html):
            not_found_in_html.append(lid)

    # Итог
    if changed:
        status = '(не записано — режим проверки)' if check_only else '✅ записано'
        print(f'Изменено: {len(changed)} уроков {status}')
        for lid in changed:
            print(f'  • {lid}')
    else:
        print('Изменений нет — content/ совпадает с HTML.')

    if missing:
        print(f'\n⚠️  Не найдены .md файлы для: {", ".join(missing)}')

    if not_found_in_html:
        print(f'\n⚠️  Не найдены cdata-блоки в HTML для: {", ".join(not_found_in_html)}')

    if not check_only and changed:
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'\n✅ ml_road.html обновлён ({len(changed)} уроков)')


if __name__ == '__main__':
    main()
