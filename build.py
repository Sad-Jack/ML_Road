#!/usr/bin/env python3
"""
build.py — сборщик ml_road.html из ml_road_template.html + content/

Читает метаданные из _module.json и YAML-frontmatter в .md файлах,
строит COURSE / PYTHON_COURSE / RIGHT_PANEL_DATA и вставляет cdata-блоки.

Режимы:
  python3 build.py              # полная пересборка из template → ml_road.html
  python3 build.py l05 l20      # обновить только конкретные уроки (патч ml_road.html)
  python3 build.py --check      # проверить расхождения без записи
  python3 build.py --full       # принудительная полная пересборка
"""

import re
import os
import sys
import json
import glob

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, 'ml_road_template.html')
HTML_FILE     = os.path.join(BASE_DIR, 'ml_road.html')
ML_DIR        = os.path.join(BASE_DIR, 'content', 'ml')
PY_DIR        = os.path.join(BASE_DIR, 'content', 'python')
RIGHT_PANEL_DIR = os.path.join(BASE_DIR, 'content', 'right_panel')


# ─────────────────────────────────────────────────────────────────────────────
# Парсинг YAML frontmatter
# ─────────────────────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Вернуть (meta_dict, body_without_frontmatter)."""
    if not (text.startswith('---\n') or text.startswith('---\r\n')):
        return {}, text

    end = text.find('\n---\n', 4)
    if end == -1:
        end = text.find('\n---\r\n', 4)
    if end == -1:
        return {}, text

    fm_text = text[4:end]
    body    = text[end + 5:]  # пропустить \n---\n

    meta = {}
    for line in fm_text.splitlines():
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # Конвертируем типы
        if val == 'true':
            val = True
        elif val == 'false':
            val = False
        elif key == 'tags' and val.startswith('[') and val.endswith(']'):
            raw_items = val[1:-1].strip()
            val = []
            if raw_items:
                val = [item.strip().strip('"').strip("'") for item in raw_items.split(',') if item.strip()]
        elif re.match(r'^\d+$', val):
            val = int(val)
        meta[key] = val

    return meta, body


# ─────────────────────────────────────────────────────────────────────────────
# Сканирование content/
# ─────────────────────────────────────────────────────────────────────────────

def scan_module(folder_path: str) -> dict | None:
    """Читает _module.json из папки. Возвращает None если нет файла."""
    mod_json = os.path.join(folder_path, '_module.json')
    if not os.path.exists(mod_json):
        return None
    with open(mod_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def scan_lessons(folder_path: str) -> list[dict]:
    """
    Сканирует .md файлы в папке (не _*.md), читает frontmatter.
    Возвращает список уроков, отсортированных по order.
    """
    lessons = []
    for md_path in sorted(glob.glob(os.path.join(folder_path, '*.md'))):
        filename = os.path.basename(md_path)
        if filename.startswith('_'):
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        meta, body = parse_frontmatter(content)

        if not meta.get('id'):
            # Попробовать вывести id из имени файла
            m = re.match(r'^([A-Za-z]+\d+)_', filename)
            if m:
                meta['id'] = m.group(1)
            else:
                print(f'  ⚠️  Пропущен урок без id: {md_path}')
                continue  # непонятный файл — пропустить

        lessons.append({
            'id':     meta.get('id'),
            'order':  meta.get('order', 0),
            'num':    str(meta.get('num', '')),
            'title':  str(meta.get('title', '')),
            'short':  str(meta.get('short', '')),
            '_body':  body,        # содержимое без frontmatter
            '_path':  md_path,
        })

    lessons.sort(key=lambda l: l['order'])
    return lessons


def scan_track(track_dir: str) -> list[dict]:
    """
    Сканирует директорию трека (ml/ или python/).
    Возвращает список секций (с вложенными уроками).
    """
    sections = []
    for folder_name in sorted(os.listdir(track_dir)):
        folder_path = os.path.join(track_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
        if not re.match(r'^\d+_', folder_name):
            continue

        mod_meta = scan_module(folder_path)
        if not mod_meta:
            print(f'  ⚠️  Нет _module.json в {folder_path}')
            continue

        lessons = scan_lessons(folder_path)
        if not lessons:
            continue
        sections.append({**mod_meta, 'lessons': lessons})

    return sections


# ─────────────────────────────────────────────────────────────────────────────
# Генерация JS-объекта COURSE
# ─────────────────────────────────────────────────────────────────────────────

def _js_str(s: str) -> str:
    """Экранировать строку для JS."""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def _js_template_str(s: str) -> str:
    """Экранировать строку для JS template literal."""
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')


def _js_json_str(s: str) -> str:
    """Безопасная JS-строка в двойных кавычках."""
    return json.dumps(s, ensure_ascii=False)


def build_sections_js(sections: list[dict]) -> str:
    """Генерирует JS-массив sections для вставки в COURSE / PYTHON_COURSE."""
    lines = ['[']
    for s in sections:
        lessons_js   = build_lessons_js(s['lessons'])
        lines.append(
            f"        {{\n"
            f"          id: '{s['id']}', num: '{s['num']}', title: '{_js_str(s['title'])}', "
            f"color: '{s['color']}', lessons: {lessons_js}\n"
            f"        }},"
        )
    lines.append('      ]')
    return '\n'.join(lines)


def build_lessons_js(lessons: list[dict]) -> str:
    if not lessons:
        return '[]'
    parts = ['[\n']
    for l in lessons:
        parts.append(
            f"            {{ id: '{l['id']}', order: {l['order']}, num: '{l['num']}', "
            f"title: '{_js_str(l['title'])}', short: '{_js_str(l['short'])}' }},\n"
        )
    parts.append('          ]')
    return ''.join(parts)


def scan_right_panel(panel_dir: str) -> list[dict]:
    """Сканирует статьи правой панели из content/right_panel/*.md."""
    items = []
    if not os.path.isdir(panel_dir):
        return items

    for md_path in sorted(glob.glob(os.path.join(panel_dir, '*.md'))):
        filename = os.path.basename(md_path)
        if filename.startswith('_'):
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        meta, body = parse_frontmatter(content)
        if not meta.get('id'):
            continue

        # Миграционная защита: старые статьи могли приехать из JS-template literal
        # уже с экранированием \` и \${}. В source markdown это не нужно.
        body = body.replace('\\`', '`').replace('\\${', '${')

        items.append({
            'id': str(meta.get('id')),
            'order': int(meta.get('order', 0) or 0),
            'title': str(meta.get('title', '')),
            'category': str(meta.get('category', 'Reference')),
            'type': str(meta.get('type', 'reference')),
            'summary': str(meta.get('summary', '')),
            'priority': int(meta.get('priority', 999) or 999),
            'tags': meta.get('tags', []) if isinstance(meta.get('tags'), list) else [],
            '_body': body.strip(),
        })

    items.sort(key=lambda item: (item['order'], item['priority'], item['title']))
    return items


def build_right_panel_js(items: list[dict]) -> str:
    """Генерирует JS-массив RIGHT_PANEL_DATA."""
    if not items:
        return '[]'

    parts = ['[\n']
    for item in items:
        tags_js = ', '.join(_js_json_str(tag) for tag in item['tags'])
        parts.append(
            "      {\n"
            f'        id: {_js_json_str(item["id"])},\n'
            f'        title: {_js_json_str(item["title"])},\n'
            f'        category: {_js_json_str(item["category"])},\n'
            f'        type: {_js_json_str(item["type"])},\n'
            f'        tags: [{tags_js}],\n'
            f'        summary: {_js_json_str(item["summary"])},\n'
            f'        priority: {item["priority"]},\n'
            f'        content: `{_js_template_str(item["_body"])}`\n'
            "      },\n"
        )
    parts.append('    ]')
    return ''.join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Генерация cdata-блоков
# ─────────────────────────────────────────────────────────────────────────────

def build_cdata_blocks(ml_sections: list[dict], py_sections: list[dict]) -> str:
    """Создаёт строку со всеми <script id="cdata-..."> блоками."""
    parts = ['\n  <!-- ═══ LESSON CONTENT BLOCKS ═══ -->\n']
    for s in ml_sections + py_sections:
        for l in s['lessons']:
            body = l['_body'].strip()
            parts.append(
                f'  <script type="text/plain" id="cdata-{l["id"]}">\n'
                f'{body}\n'
                f'  </script>\n'
            )
    return ''.join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Инъекция в template
# ─────────────────────────────────────────────────────────────────────────────

def replace_sections(html: str, const_name: str, new_sections_js: str) -> str:
    """Заменяет sections: [...] внутри const COURSE / PYTHON_COURSE."""
    # Найти позицию 'sections: ['
    start_marker = f'    const {const_name} = {{\n      sections: '
    start_pos    = html.find(start_marker)
    if start_pos == -1:
        raise ValueError(f'Не найден маркер для {const_name}')

    bracket_start = html.find('[', start_pos)
    if bracket_start == -1:
        raise ValueError(f'Нет [ для {const_name}')

    # Найти конец массива (учитывая вложенность)
    depth = 0
    i = bracket_start
    while i < len(html):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                bracket_end = i
                break
        i += 1
    else:
        raise ValueError(f'Не найден закрывающий ] для {const_name}')

    return html[:bracket_start] + new_sections_js + html[bracket_end + 1:]


def replace_const_array(html: str, const_name: str, new_array_js: str) -> str:
    """Заменяет массив в объявлении const NAME = [...];"""
    pattern = re.compile(rf'(const {re.escape(const_name)} = )\[(.*?)\];', re.DOTALL)
    updated_html, count = pattern.subn(rf'\1{new_array_js};', html, count=1)
    if count != 1:
        raise ValueError(f'Не найден массив для {const_name}')
    return updated_html


def inject_cdata(html: str, cdata_str: str) -> str:
    """Вставляет cdata-блоки перед </body>."""
    pos = html.rfind('</body>')
    if pos == -1:
        raise ValueError('Не найден тег </body>')
    return html[:pos] + cdata_str + html[pos:]


# ─────────────────────────────────────────────────────────────────────────────
# Патч-режим: обновить только конкретные уроки
# ─────────────────────────────────────────────────────────────────────────────

def inject_patch(html: str, lesson_id: str, new_body: str) -> tuple[str, bool]:
    """Заменить содержимое cdata-блока. Возвращает (html, был_ли_изменён)."""
    pattern = rf'(<script[^>]*id="cdata-{lesson_id}"[^>]*>)(.*?)(</script>)'
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        return html, False

    normalized = '\n' + new_body.strip() + '\n  '
    if m.group(2) == normalized:
        return html, False

    new_html = html[:m.start()] + m.group(1) + normalized + m.group(3) + html[m.end():]
    return new_html, True


def find_lesson_by_id(ml_sections: list, py_sections: list, lesson_id: str) -> dict | None:
    for s in ml_sections + py_sections:
        for l in s['lessons']:
            if l['id'] == lesson_id:
                return l
    return None


def build_full_html(template_html: str, ml_sections: list[dict], py_sections: list[dict], right_panel_items: list[dict]) -> str:
    """Собрать итоговый HTML в памяти."""
    html = template_html

    course_js = build_sections_js(ml_sections)
    html = replace_sections(html, 'COURSE', course_js)

    python_js = build_sections_js(py_sections)
    html = replace_sections(html, 'PYTHON_COURSE', python_js)

    right_panel_js = build_right_panel_js(right_panel_items)
    html = replace_const_array(html, 'RIGHT_PANEL_DATA', right_panel_js)

    cdata_str = build_cdata_blocks(ml_sections, py_sections)
    html = inject_cdata(html, cdata_str)

    return html


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args      = sys.argv[1:]
    check_only = '--check' in args
    force_full = '--full' in args
    if check_only: args.remove('--check')
    if force_full: args.remove('--full')

    # Сканируем content/
    print('📂 Сканирование content/...')
    ml_sections = scan_track(ML_DIR)
    py_sections = scan_track(PY_DIR)
    right_panel_items = scan_right_panel(RIGHT_PANEL_DIR)

    ml_lessons_total = sum(len(s['lessons']) for s in ml_sections)
    py_lessons_total = sum(len(s['lessons']) for s in py_sections)
    print(f'   ML:     {len(ml_sections)} модулей, {ml_lessons_total} уроков')
    print(f'   Python: {len(py_sections)} модулей, {py_lessons_total} уроков')
    print(f'   Right panel: {len(right_panel_items)} статей')
    print()

    # ── Патч-режим: только указанные уроки ──────────────────────────────────
    if args and not force_full:
        lesson_ids = args
        print(f'🔧 Патч-режим: {", ".join(lesson_ids)}')
        print(f'   Файл: ml_road.html')
        print(f'   Режим: {"проверка" if check_only else "запись"}')
        print()

        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html = f.read()

        changed    = []
        not_found  = []

        for lid in lesson_ids:
            lesson = find_lesson_by_id(ml_sections, py_sections, lid)
            if not lesson:
                not_found.append(lid)
                continue

            new_html, was_changed = inject_patch(html, lid, lesson['_body'])
            if was_changed:
                changed.append(lid)
                if not check_only:
                    html = new_html

        if changed:
            status = '(не записано — режим проверки)' if check_only else '✅ записано'
            print(f'Изменено: {len(changed)} уроков {status}')
            for lid in changed:
                print(f'  • {lid}')
        else:
            print('Изменений нет — content/ совпадает с HTML.')

        if not_found:
            print(f'\n⚠️  Уроки не найдены в content/: {", ".join(not_found)}')

        if not check_only and changed:
            with open(HTML_FILE, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'\n✅ ml_road.html обновлён ({len(changed)} уроков)')

        return

    # ── Полная пересборка ────────────────────────────────────────────────────
    if check_only:
        print('🔍 Режим проверки: сравниваем content/ с ml_road.html')
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template_html = f.read()
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            current_html = f.read()

        expected_html = build_full_html(template_html, ml_sections, py_sections, right_panel_items)
        if current_html == expected_html:
            print('✅ ml_road.html полностью совпадает с template + content/.')
        else:
            print('⚠️  ml_road.html не совпадает с текущими template/content. Нужна пересборка.')
        return

    print(f'🔨 Полная пересборка: {os.path.basename(TEMPLATE_FILE)} → {os.path.basename(HTML_FILE)}')
    print()

    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_html = f.read()

    html = build_full_html(template_html, ml_sections, py_sections, right_panel_items)
    print(f'  ✓ COURSE.sections: {len(ml_sections)} секций')
    print(f'  ✓ PYTHON_COURSE.sections: {len(py_sections)} секций')
    print(f'  ✓ RIGHT_PANEL_DATA: {len(right_panel_items)} статей')
    print(f'  ✓ cdata-блоки: {ml_lessons_total + py_lessons_total} уроков')

    # 5. Записать результат
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(HTML_FILE) // 1024
    print()
    print(f'✅ ml_road.html собран ({size_kb} KB)')


if __name__ == '__main__':
    main()
