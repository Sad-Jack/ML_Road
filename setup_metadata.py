#!/usr/bin/env python3
"""
setup_metadata.py — создаёт _module.json и frontmatter для модулей 01-05 ML.

Читает метаданные прямо из COURSE/PYTHON_COURSE в ml_road.html,
чтобы не вводить данные вручную.

Запускать один раз для инициализации content/ метаданными.
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

# ─── Данные уроков (из COURSE в ml_road.html) ─────────────────────────────────

ML_LESSONS = {
    # Модуль 1
    "l01": {"order": 1,  "num": "01", "title": "01. Что такое машинное обучение простыми словами", "short": "Что такое машинное обучение", "locked": False},
    "l02": {"order": 2,  "num": "02", "title": "02. Типы обучения: supervised, unsupervised, RL",   "short": "Типы обучения",               "locked": False},
    "l03": {"order": 3,  "num": "03", "title": "03. Модель: input → output",                        "short": "Модель: input → output",       "locked": False},
    "l04": {"order": 4,  "num": "04", "title": "04. X, y, признаки и target",                       "short": "X, y, признаки и target",      "locked": False},
    "l05": {"order": 5,  "num": "05", "title": "05. Как выглядят данные в ML",                      "short": "Как выглядят данные в ML",     "locked": False},
    "l06": {"order": 6,  "num": "06", "title": "06. Что модель реально учит из данных",             "short": "Что модель реально учит из данных", "locked": False},
    "l07": {"order": 7,  "num": "07", "title": "07. Статистика для ML: среднее, медиана, дисперсия","short": "Статистика для ML",             "locked": False},
    "l08": {"order": 8,  "num": "08", "title": "08. Числовые и категориальные признаки",            "short": "Числовые и категориальные признаки", "locked": False},
    # Модуль 2
    "l09": {"order": 9,  "num": "09", "title": "09. Регрессия vs классификация",                   "short": "Регрессия vs классификация",   "locked": False},
    "l10": {"order": 10, "num": "10", "title": "10. Вероятности в классификации",                   "short": "Вероятности в классификации",  "locked": False},
    "l11": {"order": 11, "num": "11", "title": "11. Кластеризация как задача",                       "short": "Кластеризация",                "locked": False},
    "l12": {"order": 12, "num": "12", "title": "12. Рекомендательные системы",                      "short": "Рекомендательные системы",     "locked": False},
    "l13": {"order": 13, "num": "13", "title": "13. Детекция аномалий",                              "short": "Детекция аномалий",            "locked": False},
    "l14": {"order": 14, "num": "14", "title": "14. Ранжирование в ML",                              "short": "Ранжирование",                 "locked": False},
    "l15": {"order": 15, "num": "15", "title": "15. Карта задач ML",                                 "short": "Карта задач ML",               "locked": False},
    # Модуль 3
    "l16": {"order": 16, "num": "16", "title": "16. Train / Validation / Test",                     "short": "Train / Validation / Test",    "locked": False},
    "l17": {"order": 17, "num": "17", "title": "17. Cross-validation",                              "short": "Cross-validation",             "locked": False},
    "l18": {"order": 18, "num": "18", "title": "18. Baseline-модель",                               "short": "Baseline-модель",              "locked": False},
    "l19": {"order": 19, "num": "19", "title": "19. Confusion Matrix",                              "short": "Confusion Matrix",             "locked": False},
    "l20": {"order": 20, "num": "20", "title": "20. Метрики классификации",                         "short": "Метрики классификации",        "locked": False},
    "l21": {"order": 21, "num": "21", "title": "21. Метрики регрессии: MAE, MSE, RMSE",             "short": "Метрики регрессии: MAE, MSE, RMSE", "locked": False},
    "l22": {"order": 22, "num": "22", "title": "22. Overfitting и Underfitting",                    "short": "Overfitting и Underfitting",   "locked": False},
    # Модуль 4
    "l23": {"order": 23, "num": "23", "title": "23. Линейная регрессия",                             "short": "Линейная регрессия",           "locked": False},
    "l24": {"order": 24, "num": "24", "title": "24. Логистическая регрессия",                        "short": "Логистическая регрессия",      "locked": False},
    "l25": {"order": 25, "num": "25", "title": "25. Support Vector Machine простыми словами",        "short": "SVM",                          "locked": False},
    "l26": {"order": 26, "num": "26", "title": "26. Decision Tree",                                  "short": "Decision Tree",                "locked": False},
    "l27": {"order": 27, "num": "27", "title": "27. Random Forest",                                  "short": "Random Forest",                "locked": False},
    "l28": {"order": 28, "num": "28", "title": "28. Gradient Boosting",                              "short": "Gradient Boosting",            "locked": False},
    "l29": {"order": 29, "num": "29", "title": "29. XGBoost, LightGBM и CatBoost",                  "short": "XGBoost, LightGBM и CatBoost", "locked": False},
    "l30": {"order": 30, "num": "30", "title": "30. Простой ML-пайплайн",                            "short": "Простой ML-пайплайн",          "locked": False},
    "l31": {"order": 31, "num": "31", "title": "31. Как выбирать модель под задачу",                 "short": "Как выбирать модель под задачу","locked": False},
    # Модуль 5
    "l32": {"order": 32, "num": "32", "title": "32. Что такое Feature Engineering",                 "short": "Что такое Feature Engineering","locked": False},
    "l33": {"order": 33, "num": "33", "title": "33. Масштабирование признаков",                     "short": "Масштабирование признаков",    "locked": False},
    "l34": {"order": 34, "num": "34", "title": "34. Как выбирать признаки для X",                   "short": "Как выбирать признаки для X",  "locked": False},
    "l35": {"order": 35, "num": "35", "title": "35. Пропуски в данных",                             "short": "Пропуски в данных",            "locked": False},
    "l36": {"order": 36, "num": "36", "title": "36. Выбросы в данных",                              "short": "Выбросы в данных",             "locked": False},
    "l37": {"order": 37, "num": "37", "title": "37. Кодирование категориальных признаков",          "short": "Кодирование категориальных признаков", "locked": False},
    "l38": {"order": 38, "num": "38", "title": "38. One-Hot Encoding простыми словами",             "short": "One-Hot Encoding",             "locked": False},
    "l39": {"order": 39, "num": "39", "title": "39. Label Encoding простыми словами",               "short": "Label Encoding",               "locked": False},
    "l40": {"order": 40, "num": "40", "title": "40. Ordinal Encoding простыми словами",             "short": "Ordinal Encoding",             "locked": False},
    "l41": {"order": 41, "num": "41", "title": "41. Создание новых признаков",                      "short": "Создание новых признаков",     "locked": False},
    "l42": {"order": 42, "num": "42", "title": "42. Удаление лишних признаков",                     "short": "Удаление лишних признаков",    "locked": False},
    "l43": {"order": 43, "num": "43", "title": "43. Data Leakage: опасная ошибка в ML",             "short": "Data Leakage",                 "locked": False},
}

PYTHON_LESSONS = {
    "pd01": {"order": 1, "num": "01", "title": "01. DataFrame в Python для ML", "short": "DataFrame в Python для ML", "locked": False},
    "pd02": {"order": 2, "num": "02", "title": "02. Pandas на практике",        "short": "Pandas на практике",        "locked": False},
    "pd03": {"order": 3, "num": "03", "title": "03. Типы данных в Pandas",       "short": "Типы данных в Pandas",       "locked": False},
}


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
