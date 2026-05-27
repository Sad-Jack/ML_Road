#!/usr/bin/env python3
"""
insert_lesson.py — сдвигает уроки >= INSERT_AT на +1, освобождая место для нового урока.

Usage:
  python3 insert_lesson.py --dry   # показать план без изменений
  python3 insert_lesson.py         # применить
"""

import os, re, sys, glob

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ML_DIR     = os.path.join(BASE_DIR, 'content', 'ml')
DRY        = '--dry' in sys.argv
INSERT_AT  = 24   # все уроки с order >= INSERT_AT сдвигаются на +1

TEMP_SUFFIX = '.__inserting__'


def parse_frontmatter(text):
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ':' in line:
            k, _, v = line.partition(':')
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, text[end + 5:]


def shift_frontmatter(text):
    """Увеличить id/order/num/title-префикс на 1."""
    if not text.startswith('---\n'):
        return text
    end = text.find('\n---\n', 4)
    if end == -1:
        return text
    lines = text[4:end].splitlines()
    body  = text[end + 5:]
    out   = []
    for line in lines:
        if line.startswith('id:'):
            m = re.match(r'id:\s*l(\d+)', line)
            out.append(f'id: l{int(m.group(1))+1:02d}' if m else line)
        elif line.startswith('order:'):
            m = re.match(r'order:\s*(\d+)', line)
            out.append(f'order: {int(m.group(1))+1}' if m else line)
        elif line.startswith('num:'):
            m = re.match(r'num:\s*["\']?(\d+)["\']?', line)
            out.append(f'num: "{int(m.group(1))+1}"' if m else line)
        elif line.startswith('title:'):
            # "title: \"24. Линейная регрессия\""  →  "title: \"25. Линейная регрессия\""
            m = re.match(r'(title:\s*["\']?)(\d+)(\..*)', line)
            out.append(f'{m.group(1)}{int(m.group(2))+1}{m.group(3)}' if m else line)
        elif line.startswith('short:'):
            # "short: \"24. Линейная регрессия\"" — иногда содержит номер
            m = re.match(r'(short:\s*["\']?)(\d+)(\..*)', line)
            out.append(f'{m.group(1)}{int(m.group(2))+1}{m.group(3)}' if m else line)
        else:
            out.append(line)
    return '---\n' + '\n'.join(out) + '\n---\n' + body


def shift_refs(text):
    """В теле урока: 'урок(а/е) N' → N+1 для N >= INSERT_AT."""
    def _replace(m):
        prefix, num = m.group(1), int(m.group(2))
        return f'{prefix}{num + 1}' if num >= INSERT_AT else m.group(0)
    return re.sub(r'(урок[аое]?\s+)(\d+)', _replace, text)


# ── Собрать все файлы уроков ──────────────────────────────────────────────────
all_files = sorted(glob.glob(os.path.join(ML_DIR, '**', 'l*.md'), recursive=True))

to_shift  = []   # (path, content, order) — файлы для переименования
to_reref  = []   # (path, content)         — файлы только с обновлением ссылок

for path in all_files:
    with open(path, encoding='utf-8') as f:
        content = f.read()
    meta, _ = parse_frontmatter(content)
    try:
        order = int(float(meta.get('order', 0)))
    except (ValueError, TypeError):
        order = 0

    if order >= INSERT_AT:
        to_shift.append((path, content, order))
    else:
        to_reref.append((path, content))

# Сортировка по убыванию — избегаем конфликтов имён при переименовании
to_shift.sort(key=lambda x: -x[2])

# ── Dry run ───────────────────────────────────────────────────────────────────
if DRY:
    print(f'\n📋 Файлов для сдвига: {len(to_shift)}')
    for path, _, order in to_shift:
        bn     = os.path.basename(path)
        new_bn = re.sub(r'^l(\d+)_', lambda m: f'l{int(m.group(1))+1:02d}_', bn)
        print(f'  l{order:02d} → l{order+1:02d}  {bn}')
    print(f'\n📋 Файлов с cross-reference обновлением: {len(to_reref)}')
    print('\n[dry-run] Файлы не изменены.')
    sys.exit(0)

# ── Фаза 1: создать temp-файлы ────────────────────────────────────────────────
print(f'\n🔄 Сдвигаем l{INSERT_AT}..l97 → l{INSERT_AT+1}..l98 ({len(to_shift)} файлов)...')

temp_pairs = []
try:
    for path, content, order in to_shift:
        new_content = shift_refs(shift_frontmatter(content))
        bn       = os.path.basename(path)
        new_bn   = re.sub(r'^l(\d+)_', lambda m: f'l{int(m.group(1))+1:02d}_', bn)
        new_path = os.path.join(os.path.dirname(path), new_bn)
        temp     = path + TEMP_SUFFIX
        with open(temp, 'w', encoding='utf-8') as f:
            f.write(new_content)
        temp_pairs.append((temp, new_path, path))
except Exception as e:
    print(f'❌ Ошибка фазы 1: {e}')
    for (t, _, _) in temp_pairs:
        if os.path.exists(t): os.remove(t)
    sys.exit(1)

# ── Фаза 2: атомарная замена ──────────────────────────────────────────────────
try:
    for (t, new_path, old_path) in temp_pairs:
        os.remove(old_path)
    for (t, new_path, old_path) in temp_pairs:
        os.rename(t, new_path)
        print(f'  ✓ {os.path.basename(old_path)} → {os.path.basename(new_path)}')
except Exception as e:
    print(f'❌ Ошибка фазы 2: {e}')
    sys.exit(1)

# ── Обновить cross-references в файлах l01–l23 ───────────────────────────────
updated_refs = 0
for path, content in to_reref:
    new_content = shift_refs(content)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'  ✓ refs: {os.path.basename(path)}')
        updated_refs += 1

print(f'\n✅ Готово: переименовано {len(temp_pairs)} файлов, обновлено ссылок в {updated_refs} файлах')
print(f'Создайте урок content/ml/04_Первые_модели/l{INSERT_AT}_*.md, затем: python3 build.py --full')
