#!/usr/bin/env python3
"""
renumber_lessons.py — переименовывает уроки l95/l96/l97 в l15/l52/l78
и сдвигает l15-l94 на +1/+2/+3 соответственно.

Режимы:
  python3 renumber_lessons.py --dry   # показать что изменится, не трогать файлы
  python3 renumber_lessons.py         # применить изменения
"""

import os, re, sys, glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR   = os.path.join(BASE_DIR, 'content', 'ml')
DRY      = '--dry' in sys.argv


def parse_frontmatter(text):
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    fm_lines = text[4:end].splitlines()
    body     = text[end + 5:]
    meta = {}
    for line in fm_lines:
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def update_frontmatter(text, new_id, new_order, new_num, new_title):
    if not text.startswith('---\n'):
        return text
    end = text.find('\n---\n', 4)
    if end == -1:
        return text
    fm_lines = text[4:end].splitlines()
    body     = text[end + 5:]

    result = []
    for line in fm_lines:
        if line.startswith('id:'):
            result.append(f'id: {new_id}')
        elif line.startswith('order:'):
            result.append(f'order: {new_order}')
        elif line.startswith('num:'):
            result.append(f'num: "{new_num}"')
        elif line.startswith('title:'):
            result.append(f'title: "{new_title}"')
        else:
            result.append(line)
    return '---\n' + '\n'.join(result) + '\n---\n' + body


def compute_new_num(old_num_str):
    """Вычислить новый порядковый номер для урока по старому."""
    try:
        old = float(old_num_str)
    except ValueError:
        return old_num_str  # не меняем если не число

    if old <= 14:
        return int(old)        # l01-l14: без изменений
    elif old == 14.5:
        return 15              # Временные ряды → l15
    elif old < 50.5:
        return int(old) + 1    # l15-l50 → +1
    elif old == 50.5:
        return 52              # SHAP → l52
    elif old < 75.5:
        return int(old) + 2    # l51-l75 → +2
    elif old == 75.5:
        return 78              # p-value → l78
    else:
        return int(old) + 3    # l76-l94 → +3


def new_title(old_title, new_num):
    """Заменить числовой префикс в заголовке урока."""
    # Формат: "14.5. Временные ряды" или "15. Карта задач ML"
    m = re.match(r'^[\d.]+\.\s*(.*)', old_title)
    if m:
        return f'{new_num}. {m.group(1)}'
    return old_title


# ─── Собрать все файлы уроков ─────────────────────────────────────────────────

all_lessons = []
for md_path in glob.glob(os.path.join(ML_DIR, '**', 'l*.md'), recursive=True):
    with open(md_path, encoding='utf-8') as f:
        content = f.read()
    meta, _ = parse_frontmatter(content)
    try:
        order = float(meta.get('order', 0))
    except (ValueError, TypeError):
        order = 0.0
    all_lessons.append({
        'path':    md_path,
        'content': content,
        'id':      meta.get('id', ''),
        'order':   order,
        'num':     meta.get('num', ''),
        'title':   meta.get('title', ''),
    })

all_lessons.sort(key=lambda x: x['order'])

# ─── Guard: скрипт работает только при наличии уроков-вставок ─────────────────
# Этот скрипт предназначен для вставки трёх новых уроков в курс:
#   order=14.5  → «Временные ряды»  → l15
#   order=50.5  → «SHAP»            → l52
#   order=75.5  → «p-value»         → l78
# Без этих уроков запуск сдвинет нумерацию 83 существующих уроков и сломает курс.
float_order_lessons = [l for l in all_lessons if l['order'] != int(l['order'])]
if not float_order_lessons:
    print('❌ Ошибка: не найдено уроков с дробными order (14.5 / 50.5 / 75.5).')
    print()
    print('   Этот скрипт предназначен для вставки новых уроков в курс.')
    print('   Создайте уроки-вставки с дробными order в frontmatter,')
    print('   затем запустите скрипт снова.')
    print()
    print('   Запуск без уроков-вставок перенумерует 83 существующих урока')
    print('   и необратимо сломает структуру курса.')
    sys.exit(1)

# ─── Построить план переименований ────────────────────────────────────────────

plan = []  # список (old_path, new_path, new_content)

for lesson in all_lessons:
    old_num   = lesson['num'] or str(int(lesson['order']))
    n_num     = compute_new_num(old_num)
    n_id      = f'l{n_num:02d}' if n_num <= 99 else f'l{n_num}'
    n_title   = new_title(lesson['title'], n_num)
    n_content = update_frontmatter(lesson['content'], n_id, n_num, str(n_num), n_title)

    # Новое имя файла: заменить lXX_ префикс
    old_file  = os.path.basename(lesson['path'])
    new_file  = re.sub(r'^l[\d.]+_', f'{n_id}_', old_file)
    new_path  = os.path.join(os.path.dirname(lesson['path']), new_file)

    changed = (n_id != lesson['id'])
    plan.append({
        'old_path':  lesson['path'],
        'new_path':  new_path,
        'content':   n_content,
        'changed':   changed,
        'old_id':    lesson['id'],
        'new_id':    n_id,
    })

# ─── Показать план ────────────────────────────────────────────────────────────

changed_count = sum(1 for p in plan if p['changed'])
print(f"\n📋 План переименования: {changed_count} уроков будут изменены\n")

for p in plan:
    if p['changed']:
        old_rel = p['old_path'].replace(ML_DIR + '/', '')
        new_rel = p['new_path'].replace(ML_DIR + '/', '')
        print(f"  {p['old_id']:>4} → {p['new_id']:<5}  {old_rel}")
        if os.path.basename(p['old_path']) != os.path.basename(p['new_path']):
            print(f"               ↳  {new_rel}")

if DRY:
    print('\n[dry-run] Файлы не изменены. Запустите без --dry для применения.')
    sys.exit(0)

# ─── Применить: двухфазное переименование ─────────────────────────────────────
# Фаза 1: все изменённые файлы → _MIGRATING временные имена
# Фаза 2: временные имена → финальные имена
# (избегаем конфликтов: l94→l97, но l97 уже существует как новый урок)

print('\n🔄 Применяем изменения...')

TEMP_SUFFIX = '.__migrating__'

# Фаза 1: переименовать в временные имена, записать новый контент
temp_pairs = []
for p in plan:
    if not p['changed']:
        continue
    temp_path = p['old_path'] + TEMP_SUFFIX
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(p['content'])
    temp_pairs.append((temp_path, p['new_path'], p['old_path']))

# Фаза 2: удалить старые файлы, переименовать temp → финал
for (temp_path, new_path, old_path) in temp_pairs:
    os.remove(old_path)

for (temp_path, new_path, old_path) in temp_pairs:
    os.rename(temp_path, new_path)
    print(f"  ✓ {os.path.basename(old_path)} → {os.path.basename(new_path)}")

print(f'\n✅ Готово: переименовано {len(temp_pairs)} файлов')
print('Запустите: python3 build.py --full')
