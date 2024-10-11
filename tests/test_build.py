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
SASS_BIN = ROOT / 'libs' / 'sass'

OUT = ROOT / 'data' / '_sites'


def add_dirty_to_output():
    OUT.mkdir(exist_ok=True)
    (OUT / 'has_to_be_deleted.txt').touch()


def clean_dir():
    shutil.rmtree(OUT, ignore_errors=True)


@pytest.fixture
def build() -> Build:
    add_dirty_to_output()
    OUT.mkdir(exist_ok=True)
    yield Build(sites_dir=PAGES,
                data_dir=DATA,
                templates_dir=TEMPLATES,
                static_dir=STATIC,
                sass_dir=SASS,
                output_dir=OUT,
                sass_bin=SASS_BIN,
                skip_parsing=['*.xml'],
                parse_keep_extension=['404.html'])
    clean_dir()


def test_build(build):
    build.register_filters(in_hash=lambda x: f'##{x}##').register_globals(
        home='https://the-home'
    ).build(clean=True)

    assert not (OUT / 'has_to_be_deleted.txt').exists()
    assert (OUT / 'index.html').read_text() == (
        '<start> BODY ##abc## https://the-home <h1>The name</h1> <end>'
    )
    assert (OUT / 'blog' / 'day-abc' / 'index.html').read_text() == (
        'START The Title <ul><li>line 1<li>line 2</ul> END'
    )
    assert (OUT / 'sitemap.xml').read_text() == ('Do not change this!')
    assert (OUT / '404.html').read_text() == ('<start> Parse and keep extension <end>')

    assert (OUT / 'static' / 'css' / 'home.css'
            ).read_text() == 'body {\n  background-color: aqua;\n}\n\n/*# sourceMappingURL=home.css.map */\n'
    assert (OUT / 'static' / 'css' / 'home.min.css'
            ).read_text() == 'body{background-color:aqua}/*# sourceMappingURL=home.min.css.map */\n'

    assert (OUT / 'static' / 'js' / 'site.js'
            ).read_text() == "console.info('OK');\n\nconsole.warn('NOK');"
    assert (OUT / 'static' / 'js' / 'site.min.js'
            ).read_text() == "console.info('OK'); console.warn('NOK');"
