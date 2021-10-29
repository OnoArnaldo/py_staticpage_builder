import pytest
from pathlib import Path
from tests.utils import fake_func, fake_iter_file

from pystaticpage import tasks, dependency as dep

LOG = []


@pytest.fixture
def dependency():
    LOG.clear()
    dep.reset_dependencies()
    dep.set_dependencies(dep.Dependency(
        minify=fake_func('minify', LOG, [
            Path('dirs/sites/static/css/main.min.css'),
            Path('dirs/sites/static/css/table.min.css'),
        ]),
        utils_gzip_file=fake_func('gzip_file', LOG),
        utils_gzip_data=fake_func('gzip_data', LOG),
        sass_compile=fake_func('sass_compile', LOG, ['compiled-main', 'compiled-table']),
        utils_save_content=fake_func('save_content', LOG),
        utils_iter_files=fake_iter_file([], './dirs/sass', [
            Path('./dirs/sass/main.sass'),
            Path('./dirs/sass/table.scss'),
            Path('./dirs/sass/readme.txt'),
        ])
    ))

    return dep.dependency


def test_build_sass_with_static(dependency, dirs, urls):
    builder = tasks.TaskBuildSASS() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .sass_config(tasks.SassConfig(
            execute=True,
            output_style='nested',
            destination='static',
        )).minify_config(tasks.MinifyConfig(
            execute=True,
            extensions=['.css'],
            skip_dirs=[],
            skip_files=[]
        )).gzip_config(tasks.GzipConfig(
            execute=True,
            extensions=['.css'],
            skip_files=[]
        ))

    builder.execute()

    assert LOG == [['sass_compile', (), {'filename': str(Path('dirs/sass/main.sass').absolute()), 'output_style': 'nested'}],
                   ['save_content', (Path('dirs/sites/static/css/main.css'), 'compiled-main'), {}],
                   ['gzip_file', (Path('dirs/sites/static/css/main.css'),), {}],
                   ['minify', (Path('dirs/sites/static/css/main.css'),), {'overwrite': False}],
                   ['gzip_file', (Path('dirs/sites/static/css/main.min.css'),), {}],
                   ['sass_compile', (), {'filename': str(Path('dirs/sass/table.scss').absolute()), 'output_style': 'nested'}],
                   ['save_content', (Path('dirs/sites/static/css/table.css'), 'compiled-table'), {}],
                   ['gzip_file', (Path('dirs/sites/static/css/table.css'),), {}],
                   ['minify', (Path('dirs/sites/static/css/table.css'),), {'overwrite': False}],
                   ['gzip_file', (Path('dirs/sites/static/css/table.min.css'),), {}],
                   ]


def test_build_sass_with_cdn(dependency, dirs, urls):
    builder = tasks.TaskBuildSASS() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .sass_config(tasks.SassConfig(
            execute=True,
            output_style='nested',
            destination='cdn'
        )).minify_config(tasks.MinifyConfig(
            execute=True,
            extensions=['.css'],
            skip_dirs=[],
            skip_files=[]
        )).gzip_config(tasks.GzipConfig(
            execute=True,
            extensions=['.css'],
            skip_files=[]
        ))

    builder.execute()

    assert LOG == [
        ['sass_compile', (), {'filename': str(Path('dirs/sass/main.sass').absolute()), 'output_style': 'nested'}],
        ['save_content', (Path('dirs/cdn/css/main.css'), 'compiled-main'), {}],
        ['sass_compile', (), {'filename': str(Path('dirs/sass/table.scss').absolute()), 'output_style': 'nested'}],
        ['save_content', (Path('dirs/cdn/css/table.css'), 'compiled-table'), {}]
    ]
