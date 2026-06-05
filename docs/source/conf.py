# -- Path setup --------------------------------------------------------------

import sys
from pathlib import Path
# Добавляем корень проекта в sys.path, чтобы autodoc мог импортировать ваш код
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "api" / "app"))   # путь к src из docs/source

# -- Project information -----------------------------------------------------
project = 'Web Shop'
author = 'Myasnikov Vadim'
release = '0.1.0'        # или импортировать из __version__ пакета

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # автоматическое извлечение docstrings
    'sphinx.ext.napoleon',     # поддержка Google/NumPy стиля docstrings
    'sphinx.ext.viewcode',     # «просмотр исходного кода»
    'sphinx.ext.autosummary',  # автогенерация таблиц
    'myst_parser',             # поддержка Markdown в .md файлах
]

# Автоматически генерировать summary‑таблицы
autosummary_generate = True

# Поддержка markdown‑файлов ( *.md )
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# Выбираем тему (RTD – самая популярная)
html_theme = 'sphinx_rtd_theme'

# Если хотите собственный static‑каталог (логотип, CSS)
html_static_path = ['_static']
# Пример добавления собственного css:
# html_css_files = ['css/custom.css']

# -- Napoleon settings (Google/NumPy style) ----------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_param = True

# -- Параметры автодокументации --------------------------------------------
autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'private-members': False,
    'special-members': '__init__',
    'inherited-members': False,
    'show-inheritance': False,
    'exclude-members':                    
        'query, metadata, registry, objects, __mapper__, '
        'model_dump, model_validate, model_json_schema, dict, json, copy, '
        'from_orm, schema, config, fields',
}

autodoc_member_order = 'bysource'

suppress_warnings = ['docutils', 'ref.ref']

napoleon_google_docstring = True
napoleon_include_init_with_doc = True