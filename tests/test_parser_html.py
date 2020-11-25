import os
import secrets
import pytest
from pystaticpage.builder import HTMLParser

BASE = ('<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '  <meta charset="UTF-8">\n'
        '  <title>{%block title%}TheTile{% endblock %}</title>\n'
        '</head>\n'
        '<body>\n'
        '{% block body %}{% endblock %}\n'
        '</body>\n'
        '</html>\n')

BASIC = ('{% extends \'%BASE%\' %}\n'
         '{%block title%}{{ title }}{% endblock %}\n'
         '{% block body %}\n'
         '<h1>{{ title }}</h1>\n'
         '<h2>Subtitle</h2>\n'
         '{% endblock %}\n')


def template_to_name(template):
    return os.path.join('./temp', template)


@pytest.fixture
def file_name():
    base_name = secrets.token_urlsafe(5)
    with open(template_to_name(base_name), 'w') as f:
        f.write(BASE)
    f.close()

    basic_name = secrets.token_urlsafe(5)
    with open(template_to_name(basic_name), 'w') as f:
        f.write(BASIC.replace('%BASE%', base_name))
    f.close()

    yield basic_name

    os.remove(template_to_name(base_name))
    os.remove(template_to_name(basic_name))


@pytest.fixture
def env():
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    e = Environment(
        loader=FileSystemLoader(['temp']),
        autoescape=select_autoescape(['html', 'xml'])
    )
    e.globals['current_year'] = 2020
    e.globals['do_print'] = lambda x: f'DO PRINT({x})'

    return e


def test_basic(env, file_name):
    content = HTMLParser.parser(env, file_name, title='BASIC PAGE')

    assert content == ('<!DOCTYPE html>\n'
                       '<html lang="en">\n'
                       '<head>\n'
                       '  <meta charset="UTF-8">\n'
                       '  <title>BASIC PAGE</title>\n'
                       '</head>\n'
                       '<body>\n'
                       '\n'
                       '<h1>BASIC PAGE</h1>\n'
                       '<h2>Subtitle</h2>\n'
                       '\n'
                       '</body>\n'
                       '</html>')
