#!/usr/bin/env python3
"""
setup_metadata.py — создаёт _module.json и frontmatter при добавлении новых модулей.

СТАТУС: Одноразовый скрипт инициализации. Выполнен в мае 2024.
  - Все _module.json созданы. Источник истины — сами файлы _module.json.
  - Все 97 .md файлов уже имеют frontmatter (id, order, num, title, short, locked).
  - Повторный запуск безопасен (идемпотентен): пропускает файлы с уже существующим
    frontmatter и _module.json.

КАК ДОБАВИТЬ НОВЫЙ УРОК:
  1. Создать .md файл в нужной папке с frontmatter вручную.
  2. Запустить: python3 build.py l<id>   — для патч-обновления HTML.
  Этот скрипт для этого НЕ нужен.

КАК ДОБАВИТЬ НОВЫЙ МОДУЛЬ:
  1. Добавить запись в ML_MODULES ниже.
  2. Создать папку content/ml/XX_Название/.
  3. Добавить _module.json в неё (или запустить этот скрипт).
  4. Создать .md файлы с frontmatter вручную.

ПОЧЕМУ ML_LESSONS УДАЛЁН:
  Словарь покрывал только l01–l43 из 97 уроков, а нумерация l23–l97 в нём
  была сдвинута на 1–3 позиции относительно реального курса (из-за добавления
  уроков Временные ряды / SHAP / p-value). Оставлять неверный словарь в коде
  опаснее, чем его отсутствие — при добавлении нового урока он выдал бы
  неправильные title/num в frontmatter.
  Frontmatter новых уроков писать вручную — это 5 строк.
"""

import os
import re
import json
import glob

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
HTML_FILE  = os.path.join(BASE_DIR, 'ml_road.html')
ML_DIR     = os.path.join(BASE_DIR, 'content', 'ml')
PY_DIR     = os.path.join(BASE_DIR, 'content', 'python')

# ─── Данные модулей (из COURSE в ml_road.html) ───────────────────────────────

ML_MODULES = [
    {"id": "s1",  "num": "01", "title": "База ML и данные",                 "color": "c1",  "locked": False},
    {"id": "s2",  "num": "02", "title": "Типы задач в ML",                  "color": "c2",  "locked": False},
    {"id": "s3",  "num": "03", "title": "Оценка моделей",                   "color": "c3",  "locked": False},
    {"id": "s4",  "num": "04", "title": "Первые модели",                    "color": "c4",  "locked": False},
    {"id": "s5",  "num": "05", "title": "Feature Engineering",              "color": "c5",  "locked": False},
    {"id": "s6",  "num": "06", "title": "Диагностика и улучшение моделей",  "color": "c6",  "locked": False},
    {"id": "s7",  "num": "07", "title": "Обучение без учителя",             "color": "c7",  "locked": False},
    {"id": "s8",  "num": "08", "title": "Рекомендательные системы",         "color": "c8",  "locked": False},
    {"id": "s9",  "num": "09", "title": "ML в производстве",                "color": "c9",  "locked": False},
    {"id": "s10", "num": "10", "title": "Ранжирование",                     "color": "c10", "locked": False},
    {"id": "s11", "num": "11", "title": "Deep Learning, LLM и AI",          "color": "c11", "locked": False},
]

PYTHON_MODULES = [
    {"id": "py1", "num": "01", "title": "NumPy",                        "color": "c1", "locked": True},
    {"id": "py2", "num": "02", "title": "Pandas",                       "color": "c2", "locked": False},
    {"id": "py3", "num": "03", "title": "Matplotlib и Seaborn",         "color": "c3", "locked": True},
    {"id": "py4", "num": "04", "title": "Scikit-learn",                 "color": "c4", "locked": True},
    {"id": "py5", "num": "05", "title": "PyTorch",                      "color": "c5", "locked": True},
    {"id": "py6", "num": "06", "title": "TensorFlow и Keras",           "color": "c6", "locked": True},
    {"id": "py7", "num": "07", "title": "XGBoost, LightGBM, CatBoost",  "color": "c7", "locked": True},
    {"id": "py8", "num": "08", "title": "Hugging Face Transformers",    "color": "c8", "locked": True},
]

# ─── Данные уроков ────────────────────────────────────────────────────────────
# ML_LESSONS и PYTHON_LESSONS удалены: они покрывали только l01–l43 из 97 уроков,
# а нумерация l23+ была сдвинута на 1–3 позиции относительно реального курса.
# Frontmatter новых уроков пишется вручную — это 6 строк (id/order/num/title/short/locked).
# Источник истины по нумерации — frontmatter самих .md файлов.
ML_LESSONS: dict = {}
PYTHON_LESSONS: dict = {}


def has_frontmatter(content: str) -> bool:
    return content.startswith('---\n') or content.startswith('---\r\n')


def make_frontmatter(lesson_id: str, meta: dict) -> str:
    locked_str = 'true' if meta['locked'] else 'false'
    return (
        f"---\n"
        f"id: {lesson_id}\n"
        f"order: {meta['order']}\n"
        f"num: \"{meta['num']}\"\n"
        f"title: \"{meta['title']}\"\n"
        f"short: \"{meta['short']}\"\n"
        f"locked: {locked_str}\n"
        f"---\n"
    )


def process_md_file(path: str, lesson_id: str, meta: dict):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if has_frontmatter(content):
        return False  # уже есть

    frontmatter = make_frontmatter(lesson_id, meta)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    return True


def process_module_folder(folder_path: str, module_meta: dict, lessons_meta: dict):
    """Создать _module.json если нет. Добавить frontmatter в .md файлы если нет."""
    mod_json_path = os.path.join(folder_path, '_module.json')

    # 1. Создать _module.json если нет
    created_json = False
    if not os.path.exists(mod_json_path):
        with open(mod_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "id": module_meta["id"],
                "num": module_meta["num"],
                "title": module_meta["title"],
                "color": module_meta["color"],
                "locked": module_meta["locked"]
            }, f, ensure_ascii=False, indent=2)
        created_json = True

    # 2. Добавить frontmatter в .md файлы
    md_files = sorted(glob.glob(os.path.join(folder_path, '*.md')))
    added_frontmatter = []
    for md_path in md_files:
        filename = os.path.basename(md_path)
        if filename.startswith('_'):
            continue

        # Извлечь ID урока из имени файла
        m = re.match(r'^(l\d+|pd\d+)_', filename)
        if not m:
            continue
        lesson_id = m.group(1)

        if lesson_id not in lessons_meta:
            continue

        if process_md_file(md_path, lesson_id, lessons_meta[lesson_id]):
            added_frontmatter.append(lesson_id)

    return created_json, added_frontmatter


def main():
    # ─── ML модули ──────────────────────────────────────────────────────────
    ml_folders = sorted([
        d for d in os.listdir(ML_DIR)
        if os.path.isdir(os.path.join(ML_DIR, d))
    ])

    print('📁 Обработка ML модулей...')
    for folder_name in ml_folders:
        folder_path = os.path.join(ML_DIR, folder_name)
        num_match = re.match(r'^(\d+)_', folder_name)
        if not num_match:
            continue
        num = num_match.group(1).zfill(2)

        # Найти метаданные модуля
        module_meta = next((m for m in ML_MODULES if m['num'] == num), None)
        if not module_meta:
            print(f'  ⚠️  Нет метаданных для модуля {num}: {folder_name}')
            continue

        created_json, added_frontmatter = process_module_folder(
            folder_path, module_meta, ML_LESSONS
        )

        status_parts = []
        if created_json:
            status_parts.append('_module.json создан')
        if added_frontmatter:
            status_parts.append(f'frontmatter добавлен: {", ".join(added_frontmatter)}')
        if not status_parts:
            status_parts.append('уже актуально')

        print(f'  • {folder_name}: {"; ".join(status_parts)}')

    # ─── Python модули ───────────────────────────────────────────────────────
    py_folders = sorted([
        d for d in os.listdir(PY_DIR)
        if os.path.isdir(os.path.join(PY_DIR, d))
    ])

    print('\n📁 Обработка Python модулей...')
    for folder_name in py_folders:
        folder_path = os.path.join(PY_DIR, folder_name)
        num_match = re.match(r'^(\d+)_', folder_name)
        if not num_match:
            continue
        num = num_match.group(1).zfill(2)

        module_meta = next((m for m in PYTHON_MODULES if m['num'] == num), None)
        if not module_meta:
            print(f'  ⚠️  Нет метаданных для Python модуля {num}: {folder_name}')
            continue

        created_json, added_frontmatter = process_module_folder(
            folder_path, module_meta, PYTHON_LESSONS
        )

        status_parts = []
        if created_json:
            status_parts.append('_module.json создан')
        if added_frontmatter:
            status_parts.append(f'frontmatter добавлен: {", ".join(added_frontmatter)}')
        if not status_parts:
            status_parts.append('уже актуально')

        print(f'  • {folder_name}: {"; ".join(status_parts)}')

    print('\n✅ Готово!')


if __name__ == '__main__':
    main()
