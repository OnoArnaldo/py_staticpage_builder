import pytest
from pathlib import Path
from tests.utils import fake_func, fake_iter_file

from pystaticpage import tasks, dependency as dep

LOG = []
STATIC_DIR_FILES = [
    Path('./dirs/static/main.css'),
    Path('./dirs/static/app.js'),
    Path('./dirs/static/help.js'),
    Path('./dirs/static/logo.jpeg'),
    Path('./dirs/static/private/team.jpeg'),
]


@pytest.fixture
def dependency():
    LOG.clear()

    dep.set_dependencies(dep.Dependency(
        path_class=Path,
        utils_iter_files=fake_iter_file(LOG, Path('dirs/static'), STATIC_DIR_FILES),
        utils_copy_file=fake_func('copy_file', LOG),
        utils_gzip_file=fake_func('gzip', LOG),
        minify=fake_func('minify', LOG, [
            Path('dirs/sites/static/main.min.css'),
            Path('dirs/sites/static/app.min.js'),
        ]),
    ))

    return dep.dependency


def test_build_task(dependency, dirs, urls):
    builder = tasks.TaskCopyStatic() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .static_config(tasks.StaticConfig(execute=True)) \
        .minify_config(tasks.MinifyConfig(
            execute=True,
            extensions=['.js', '.css'],
            skip_files=['help.js'],
            skip_dirs=['private'],
        )) \
        .gzip_config(tasks.GzipConfig(
            execute=True,
            extensions=['.js', '.css'],
            skip_files=['help.js'],
        ))

    builder.execute()

    assert LOG == [
        ['iter_file', (Path('dirs/static'),), {}],
        ['copy_file', (Path('dirs/static/main.css'), Path('dirs/sites/static/main.css')), {}],
        ['minify', (Path('dirs/sites/static/main.css'), ), {'overwrite': False}],
        ['gzip', (Path('dirs/sites/static/main.min.css'),), {}],
        ['gzip', (Path('dirs/sites/static/main.css'),), {}],
        ['copy_file', (Path('dirs/static/app.js'), Path('dirs/sites/static/app.js')), {}],
        ['minify', (Path('dirs/sites/static/app.js'), ), {'overwrite': False}],
        ['gzip', (Path('dirs/sites/static/app.min.js'),), {}],
        ['gzip', (Path('dirs/sites/static/app.js'),), {}],
        ['copy_file', (Path('dirs/static/help.js'), Path('dirs/sites/static/help.js')), {}],
        ['copy_file', (Path('dirs/static/logo.jpeg'), Path('dirs/sites/static/logo.jpeg')), {}],
        ['copy_file', (Path('dirs/static/private/team.jpeg'), Path('dirs/sites/static/private/team.jpeg')), {}]
    ]
