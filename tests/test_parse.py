import pytest
from jinja2 import DictLoader

from staticpage.parse import Parser


class FakeLoader:
    def __new__(cls, *args, **kwargs):
        return DictLoader(
            {
                'template01': '== {{ title }} ==',
                'template_filter': '!! {{ title | sample }} !!',
                'template_global': '?? {{ title }} {{ sample2(COMPANY) }} ??',
                'with_markdown': (
                    '{% markdown %}\n'
                    '  name: The Name\n'
                    '        Another Name\n'
                    '\n'
                    '  # {{ title }}\n'
                    '\n'
                    '  ## ${name}\n'
                    '{% endmarkdown %}\n'
                ),
                'full_markdown.md': (
                    'extends: template_for_md\n'
                    'name: The Name\n'
                    '\n'
                    '* {{ title }}\n'
                    '* ${name}\n'
                ),
                'template_for_md': ('START\n' '{{ content }}\n' 'END\n'),
            }
        )


@pytest.fixture
def parser(monkeypatch):
    monkeypatch.setattr('staticpage.parse.FileSystemLoader', FakeLoader)
    return Parser('fake-folder')


def test_parse(parser):
    assert parser.render('template01', title='The title') == '== The title =='


def test_parse_add_filter(parser):
    parser.register_filter('sample', lambda x: f'<<{x}>>')
    assert parser.render('template_filter', title='The title') == '!! <<The title>> !!'


def test_parse_add_globals(parser):
    parser.register_globals('COMPANY', 'The Company')
    parser.register_globals('sample2', lambda x: f'--{x}--')
    assert parser.render('template_global', title='The title') == (
        '?? The title --The Company-- ??'
    )


def test_parse_with_markdown_tag(parser):
    assert parser.render('with_markdown', title='The title') == (
        '<h1>The title</h1>\n<h2>The Name Another Name</h2>'
    )


def test_parse_full_markdown(parser):
    assert parser.render('full_markdown.md', title='The title') == (
        'START\n<ul>\n<li>The title</li>\n<li>The Name</li>\n</ul>\nEND'
    )
