#!/usr/bin/env python3
"""
test_build.py — integration tests для build.py

Запуск:
  python3 test_build.py
  python3 -m pytest test_build.py -v   (если установлен pytest)
"""

import glob
import os
import re
import subprocess
import sys
import unittest

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'ml_road.html')
ML_DIR    = os.path.join(BASE_DIR, 'content', 'ml')
PY_DIR    = os.path.join(BASE_DIR, 'content', 'python')


def _collect_md_files() -> list[str]:
    result = []
    for track_dir in (ML_DIR, PY_DIR):
        for path in glob.glob(os.path.join(track_dir, '**', '*.md'), recursive=True):
            if not os.path.basename(path).startswith('_'):
                result.append(path)
    return result


class TestBuildIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Полная пересборка — один раз для всех тестов."""
        result = subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, 'build.py'), '--full'],
            capture_output=True, text=True, cwd=BASE_DIR,
        )
        cls.returncode = result.returncode
        cls.stdout     = result.stdout
        cls.stderr     = result.stderr

    # ── 1. Сборка завершается успешно ─────────────────────────────────────────

    def test_build_exits_zero(self):
        self.assertEqual(
            self.returncode, 0,
            f'build.py завершился с кодом {self.returncode}.\n'
            f'STDOUT:\n{self.stdout}\nSTDERR:\n{self.stderr}',
        )

    # ── 2. Файл создан и не пустой ────────────────────────────────────────────

    def test_html_file_exists(self):
        self.assertTrue(os.path.exists(HTML_FILE), f'Файл не найден: {HTML_FILE}')

    def test_html_not_empty(self):
        size = os.path.getsize(HTML_FILE)
        self.assertGreater(size, 100_000, f'Подозрительно маленький HTML: {size} байт')

    # ── 3. Количество cdata-блоков совпадает с количеством .md файлов ─────────

    def test_cdata_count_matches_md_files(self):
        md_count = len(_collect_md_files())

        with open(HTML_FILE, encoding='utf-8') as f:
            html = f.read()

        cdata_count = len(re.findall(r'<script[^>]+type="text/plain"[^>]+id="cdata-', html))

        self.assertEqual(
            md_count, cdata_count,
            f'MD-файлов: {md_count}, cdata-блоков в HTML: {cdata_count}. '
            f'Расхождение — возможно пропущен урок или лишний файл.',
        )

    # ── 4. Каждый id из frontmatter присутствует как cdata-блок ───────────────

    def test_all_lesson_ids_have_cdata(self):
        from build import parse_frontmatter  # импорт чистой функции

        lesson_ids: set[str] = set()
        for md_path in _collect_md_files():
            with open(md_path, encoding='utf-8') as f:
                content = f.read()
            meta, _ = parse_frontmatter(content)
            lid = meta.get('id')
            if lid:
                lesson_ids.add(str(lid))

        with open(HTML_FILE, encoding='utf-8') as f:
            html = f.read()

        missing = [lid for lid in sorted(lesson_ids) if f'id="cdata-{lid}"' not in html]

        self.assertEqual(
            [], missing,
            'Следующие id уроков отсутствуют в HTML как cdata-блоки:\n'
            + '\n'.join(f'  • {lid}' for lid in missing),
        )

    # ── 5. Нет пустых cdata-блоков ────────────────────────────────────────────

    def test_no_empty_cdata_blocks(self):
        with open(HTML_FILE, encoding='utf-8') as f:
            html = f.read()

        empty = re.findall(
            r'<script[^>]+type="text/plain"[^>]+id="(cdata-[^"]+)"[^>]*>\s*</script>',
            html,
        )
        self.assertEqual([], empty, f'Найдены пустые cdata-блоки: {empty}')

    # ── 6. COURSE/PYTHON_COURSE содержат locked для каждой секции ─────────────

    def test_sections_have_locked_field(self):
        with open(HTML_FILE, encoding='utf-8') as f:
            html = f.read()

        # Ищем все секции в JS-объектах COURSE и PYTHON_COURSE
        sections = re.findall(r'\{[^}]*id:\s*\'[^\']+\'[^}]*\}', html)
        bad = [s for s in sections if 'locked:' not in s and "lessons:" in s]

        self.assertEqual(
            [], bad,
            f'Найдены секции без поля locked ({len(bad)} шт.)',
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
