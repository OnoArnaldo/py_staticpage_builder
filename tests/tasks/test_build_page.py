import pytest
from pathlib import Path
from jinja2 import BaseLoader

from tests.utils import fake_func, fake_iter_file, fake_open, fake_path, Ignore
from pystaticpage import tasks

LOG = []
PAGES_FILES = [
    Path('./dirs/pages/index.md'),
    Path('./dirs/pages/contact.html'),
    Path('./dirs/pages/help.html'),
    Path('./dirs/pages/private/gallery.html'),
]
FILE_CONTENTS = {
    'index.md': ('template: the-base.html\n'
                 'title: The title\n'
                 '\n'
                 '## TITLE: this is the title\n'
                 '#### email: email@email.com'),
    'company.yaml': (b'title: The Title\n'
                     b'contact:\n'
                     b'  email: contact@email.com\n'
                     b'  phone: 1234.5678\n')
}


def fake_cur_year():
    return 2021


def fake_loader(log):
    class FakeLoader(BaseLoader):
        def __init__(self, path):
            self.path = path

        def get_source(self, environment, template):
            log.append(['get_source', environment, template])
            if template == 'contact.html':
                source = ('{% set home = data("company") %}\n'
                          'Contact: {{ home.contact.phone }}\n'
                          'home: {{ url_home }}\n'
                          'static: {{ url_static }}\n'
                          'cdn: {{ url_cdn }}\n'
                          'year: {{ current_year() }}')
            else:
                source = 'TITLE: {{ title }}\n{{ content|safe }}'

            uptodate = 1634723250.9914954
            return source, Path('somename', template), uptodate

    return FakeLoader


@pytest.fixture
def dependency():
    from pystaticpage.dependency import set_dependencies, Dependency, dependency

    LOG.clear()
    path_class = fake_path(LOG)
    set_dependencies(Dependency(
        utils_iter_files=fake_iter_file(LOG, 'dirs/pages', PAGES_FILES),
        path_class=path_class,
        open_file=fake_open(LOG, FILE_CONTENTS),
        jinja_loader_class=fake_loader(LOG),
        utils_save_content=fake_func('utils_save_content', LOG),
        utils_copy_file=fake_func('utils_copy_file', LOG),
        utils_gzip_file=fake_func('utils_gzip_file', LOG),
        minify=fake_func('minify', LOG, [
            path_class('dirs/sites/index.html'),
            path_class('dirs/sites/contact/index.html'),
            path_class('dirs/sites/contact/index.html'),
        ])
    ))

    return dependency


def test_build_page(dependency, dirs, urls):
    builder = tasks.TaskBuildPage() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .page_config(tasks.PageConfig(execute=True,
                                      ony_index=True,
                                      skip_for_index=['help.html'])) \
        .gzip_config(tasks.GzipConfig(execute=True,
                                      extensions=['.html'],
                                      skip_files=['help.html'])) \
        .minify_config(tasks.MinifyConfig(execute=True,
                                          extensions=['.html'],
                                          skip_files=['help.html'],
                                          skip_dirs=['private']))

    builder.current_year = fake_cur_year
    builder.execute()

    assert LOG == [
        ['iter_file', (Path('dirs/pages'),), {}],
        ['open', (Path('dirs/pages/index.md'),), {}],
        ['read', 'index.md'],
        ['get_source', Ignore, 'the-base.html'],
        ['utils_save_content', (),
         {
             'content': ('TITLE: The title\n'
                         '<h2>TITLE: this is the title</h2>\n'
                         '<h4>email: email@email.com</h4>'),
             'dest': Path('dirs/sites/index.html')
         }],
        ['utils_gzip_file', (Path('dirs/sites/index.html'),), {}],
        ['get_source', Ignore, 'contact.html'],
        ['open', (Path('dirs/data/company.yaml'),), {}],
        ['read', 'company.yaml'],
        ['utils_save_content', (),
         {
             'content': ('Contact: 1234.5678\n'
                         'home: https://my-home.com\n'
                         'static: /static\n'
                         'cdn: https://cdn.my-home.com\n'
                         'year: 2021'),
             'dest': Path('dirs/sites/contact/index.html')
         }],
        ['utils_gzip_file', (Path('dirs/sites/contact/index.html'),), {}],
        ['get_source', Ignore, 'help.html'],
        ['utils_save_content', (), {'content': 'TITLE: \n', 'dest': Path('dirs/sites/help.html')}],
        ['get_source', Ignore, 'private/gallery.html'],
        ['utils_save_content', (), {'content': 'TITLE: \n', 'dest': Path('dirs/sites/private/gallery/index.html')}],
        ['utils_gzip_file', (Path('dirs/sites/private/gallery/index.html'),), {}],
    ]


def test_build_page_without_gzip(dependency, dirs, urls):
    builder = tasks.TaskBuildPage() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .page_config(tasks.PageConfig(execute=True,
                                      ony_index=True,
                                      skip_for_index=['help.html'])) \
        .gzip_config(tasks.GzipConfig(execute=False,
                                      extensions=['.html'],
                                      skip_files=['help.html'])) \
        .minify_config(tasks.MinifyConfig(execute=True,
                                          extensions=['.html'],
                                          skip_files=['help.html'],
                                          skip_dirs=['private']))

    builder.current_year = fake_cur_year
    builder.execute()

    assert LOG == [
        ['iter_file', (Path('dirs/pages'),), {}],
        ['open', (Path('dirs/pages/index.md'),), {}],
        ['read', 'index.md'],
        ['get_source', Ignore, 'the-base.html'],
        ['utils_save_content', (),
         {
             'content': ('TITLE: The title\n'
                         '<h2>TITLE: this is the title</h2>\n'
                         '<h4>email: email@email.com</h4>'),
             'dest': Path('dirs/sites/index.html')
         }],
        ['get_source', Ignore, 'contact.html'],
        ['open', (Path('dirs/data/company.yaml'),), {}],
        ['read', 'company.yaml'],
        ['utils_save_content', (),
         {
             'content': ('Contact: 1234.5678\n'
                         'home: https://my-home.com\n'
                         'static: /static\n'
                         'cdn: https://cdn.my-home.com\n'
                         'year: 2021'),
             'dest': Path('dirs/sites/contact/index.html')
         }],
        ['get_source', Ignore, 'help.html'],
        ['utils_save_content', (), {'content': 'TITLE: \n', 'dest': Path('dirs/sites/help.html')}],
        ['get_source', Ignore, 'private/gallery.html'],
        ['utils_save_content', (), {'content': 'TITLE: \n', 'dest': Path('dirs/sites/private/gallery/index.html')}],
    ]


def test_build_page_without_minify(dependency, dirs, urls):
    builder = tasks.TaskBuildPage() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .page_config(tasks.PageConfig(execute=True,
                                      ony_index=True,
                                      skip_for_index=['help.html'])) \
        .gzip_config(tasks.GzipConfig(execute=True,
                                      extensions=['.html'],
                                      skip_files=['help.html'])) \
        .minify_config(tasks.MinifyConfig(execute=False,
                                          extensions=['.html'],
                                          skip_files=['help.html'],
                                          skip_dirs=['private']))

    builder.current_year = fake_cur_year
    builder.execute()

    assert LOG == [
        ['iter_file', (Path('dirs/pages'),), {}],
        ['open', (Path('dirs/pages/index.md'),), {}],
        ['read', 'index.md'],
        ['get_source', Ignore, 'the-base.html'],
        ['utils_save_content', (),
         {
             'content': ('TITLE: The title\n'
                         '<h2>TITLE: this is the title</h2>\n'
                         '<h4>email: email@email.com</h4>'),
             'dest': Path('dirs/sites/index.html')
         }],
        ['utils_gzip_file', (Path('dirs/sites/index.html'),), {}],
        ['get_source', Ignore, 'contact.html'],
        ['open', (Path('dirs/data/company.yaml'),), {}],
        ['read', 'company.yaml'],
        ['utils_save_content', (),
         {
             'content': ('Contact: 1234.5678\n'
                         'home: https://my-home.com\n'
                         'static: /static\n'
                         'cdn: https://cdn.my-home.com\n'
                         'year: 2021'),
             'dest': Path('dirs/sites/contact/index.html')
         }],
        ['utils_gzip_file', (Path('dirs/sites/contact/index.html'),), {}],
        ['get_source', Ignore, 'help.html'],
        ['utils_save_content', (), {'content': 'TITLE: \n', 'dest': Path('dirs/sites/help.html')}],
        ['get_source', Ignore, 'private/gallery.html'],
        ['utils_save_content', (), {'content': 'TITLE: \n', 'dest': Path('dirs/sites/private/gallery/index.html')}],
        ['utils_gzip_file', (Path('dirs/sites/private/gallery/index.html'),), {}],
    ]
