import pytest
from pathlib import Path

from tests.utils import fake_open
from pystaticpage import minifier

LOG = []
FILES_CONTENT = {
    'main.css': (b'.home.title {\n'
                 b'    text-size: 2rem\n'
                 b'}\n')
}


def fake_post(log):
    class FakeResponse:
        @property
        def text(self):
            return '.home.title{text-size:2rem}'

    def _fake(*args, **kwargs):
        log.append(['post', args, kwargs])
        return FakeResponse()

    return _fake


@pytest.fixture
def dependency():
    from pystaticpage.dependency import set_dependencies, Dependency, dependency

    LOG.clear()
    set_dependencies(Dependency(
        requests_post=fake_post(LOG),
        open_file=fake_open(LOG, FILES_CONTENT),
    ))

    return dependency


def test_minifier(dependency):
    minify = minifier.Minifier()
    minify('./dirs/static/css/main.css')

    assert LOG == [
        ['open', (Path('dirs/static/css/main.css'),), {}],
        ['read', 'main.css'],
        ['post', ('https://cssminifier.com/raw',), {'data': {'input': b'.home.title {\n    text-size: 2rem\n}\n'}}],
        ['open', (Path('dirs/static/css/main.min.css'), 'w'), {}],
        ['write', 'main.min.css', ('.home.title{text-size:2rem}',), {}]
    ]


def test_minify_overwrite(dependency):
    minify = minifier.Minifier()
    minify('./dirs/static/css/main.css', overwrite=True)

    assert LOG == [
        ['open', (Path('dirs/static/css/main.css'),), {}],
        ['read', 'main.css'],
        ['post', ('https://cssminifier.com/raw',), {'data': {'input': b'.home.title {\n    text-size: 2rem\n}\n'}}],
        ['open', (Path('dirs/static/css/main.css'), 'w'), {}],
        ['write', 'main.css', ('.home.title{text-size:2rem}',), {}]
    ]


# TODO: test minify_to_text
