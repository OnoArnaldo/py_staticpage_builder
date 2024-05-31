import shutil
from pathlib import Path

import pytest

from staticpage.build import Build

ROOT = Path(__file__).parent

WEB = ROOT / 'data' / 'web'
PAGES = WEB / 'pages'
DATA = WEB / 'data'
TEMPLATES = WEB / 'templates'
STATIC = WEB / 'static'
SASS = WEB / 'sass'

OUT = ROOT / 'data' / '_sites'


def clean_dir():
    shutil.rmtree(OUT, ignore_errors=True)


@pytest.fixture
def build() -> Build:
    clean_dir()
    OUT.mkdir(exist_ok=True)
    yield Build(PAGES, DATA, TEMPLATES, STATIC, SASS, OUT)
    clean_dir()


def test_build(build):
    build.build()

    assert (OUT / 'index.html').read_text() == (
        '<START>\n\n\t' 'BODY\n\n  <h1>The name</h1>\n\n' '<END>'
    )
    assert (OUT / 'blog' / 'day-abc' / 'index.html').read_text() == (
        'START The Title\n' '<ul>\n<li>line 1</li>\n' '<li>line 2</li>\n</ul>\n' 'END'
    )
    assert (
        OUT / 'static' / 'css' / 'home.css'
    ).read_text() == 'body{background-color:aqua}\n'
    assert (
        OUT / 'static' / 'js' / 'site.js'
    ).read_text() == "console.info('OK');\n\nconsole.warn('NOK');"
    assert (
        OUT / 'static' / 'js' / 'site.min.js'
    ).read_text() == "console.info('OK'); console.warn('NOK');"
