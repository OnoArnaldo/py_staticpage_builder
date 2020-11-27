import os
import shutil
import pytest
import pystaticpage
from pystaticpage.builder import create_builder, Builder


def fake_minifier(results):
    def _fake(file_name, save_as=None):
        results.append([file_name, save_as])
    return _fake


def delete_sites():
    if os.path.exists('./dirs/_sites'):
        shutil.rmtree('./dirs/_sites')


def text_from(file_name):
    with open(file_name) as f:
        text = f.read()
    f.close()
    return text


@pytest.fixture
def builder(config):
    bld = create_builder(config)
    assert isinstance(bld, Builder)

    delete_sites()
    yield bld
    delete_sites()


def test_build_defaults(builder):
    minifier_calls = []
    pystaticpage.builder.minify = fake_minifier(minifier_calls)

    builder.run()

    assert text_from('./expected_site/index.html') == text_from('./dirs/_sites/index.html')
    assert text_from('./expected_site/blog/20200126.html') == text_from('./dirs/_sites/blog/20200126.html')
    assert text_from('./expected_site/blog/20200125.html') == text_from('./dirs/_sites/blog/20200125.html')

    assert os.path.exists('./dirs/_sites/static/js/index.js')
    assert os.path.exists('./dirs/_sites/static/css/index.css')

    assert minifier_calls == [
        ['./dirs/_sites/index.html', './dirs/_sites/index.html'],
        ['./dirs/_sites/blog/20200125.html', './dirs/_sites/blog/20200125.html'],
        ['./dirs/_sites/blog/20200126.html', './dirs/_sites/blog/20200126.html'],
        ['./dirs/_sites/static/css/index.css', None],
        ['./dirs/_sites/static/js/index.js', None],
    ]


def test_build(builder):
    minifier_calls = []
    pystaticpage.builder.minify = fake_minifier(minifier_calls)

    builder.run(clear=True, build_pages=True, build_static=True, compress_static=True, only_index_page=False)

    assert text_from('./expected_site/index.html') == text_from('./dirs/_sites/index.html')
    assert text_from('./expected_site/blog/20200126.html') == text_from('./dirs/_sites/blog/20200126.html')
    assert text_from('./expected_site/blog/20200125.html') == text_from('./dirs/_sites/blog/20200125.html')

    assert os.path.exists('./dirs/_sites/static/js/index.js')
    assert os.path.exists('./dirs/_sites/static/css/index.css')

    assert minifier_calls == [
        ['./dirs/_sites/index.html', './dirs/_sites/index.html'],
        ['./dirs/_sites/blog/20200125.html', './dirs/_sites/blog/20200125.html'],
        ['./dirs/_sites/blog/20200126.html', './dirs/_sites/blog/20200126.html'],
        ['./dirs/_sites/static/css/index.css', None],
        ['./dirs/_sites/static/js/index.js', None],
    ]


def test_build_only_index(builder):
    minifier_calls = []
    pystaticpage.builder.minify = fake_minifier(minifier_calls)

    builder.run(clear=True, build_pages=True, build_static=True, compress_static=True, only_index_page=True)

    assert text_from('./expected_site/index.html') == text_from('./dirs/_sites/index.html')
    assert text_from('./expected_site/blog/20200126.html') == text_from('./dirs/_sites/blog/20200126/index.html')
    assert text_from('./expected_site/blog/20200125.html') == text_from('./dirs/_sites/blog/20200125/index.html')

    assert os.path.exists('./dirs/_sites/static/js/index.js')
    assert os.path.exists('./dirs/_sites/static/css/index.css')

    assert minifier_calls == [
        ['./dirs/_sites/index.html', './dirs/_sites/index.html'],
        ['./dirs/_sites/blog/20200125/index.html', './dirs/_sites/blog/20200125/index.html'],
        ['./dirs/_sites/blog/20200126/index.html', './dirs/_sites/blog/20200126/index.html'],
        ['./dirs/_sites/static/css/index.css', None],
        ['./dirs/_sites/static/js/index.js', None],
    ]


def test_build_only_pages(builder):
    minifier_calls = []
    pystaticpage.builder.minify = fake_minifier(minifier_calls)

    builder.run(build_pages=True, build_static=False, compress_static=False, only_index_page=False)

    assert text_from('./expected_site/index.html') == text_from('./dirs/_sites/index.html')
    assert text_from('./expected_site/blog/20200126.html') == text_from('./dirs/_sites/blog/20200126.html')
    assert text_from('./expected_site/blog/20200125.html') == text_from('./dirs/_sites/blog/20200125.html')

    assert not os.path.exists('./dirs/_sites/static/js/index.js')
    assert not os.path.exists('./dirs/_sites/static/css/index.css')

    assert minifier_calls == []


def test_build_only_static(builder):
    minifier_calls = []
    pystaticpage.builder.minify = fake_minifier(minifier_calls)

    builder.run(build_pages=False, build_static=True, compress_static=False, only_index_page=False)

    assert not os.path.exists('./dirs/_sites/index.html')
    assert not os.path.exists('./dirs/_sites/blog/20200126.html')
    assert not os.path.exists('./dirs/_sites/blog/20200125.html')

    assert os.path.exists('./dirs/_sites/static/js/index.js')
    assert os.path.exists('./dirs/_sites/static/css/index.css')

    assert minifier_calls == []
