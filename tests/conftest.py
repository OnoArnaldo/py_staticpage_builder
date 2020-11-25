import pytest


@pytest.fixture
def config_yaml():
    return (
        'config:\n'
        '  dirs:\n'
        '    _sites: ./dirs/_sites\n'
        '    pages: ./dirs/pages\n'
        '    templates: ./dirs/templates\n'
        '    static: ./dirs/static\n'
        '    data: ./dirs/data\n'
        '  urls:\n'
        '    home: https://home-page.com\n'
        '    static: /static\n'
    )


@pytest.fixture
def config_dict():
    return {
        'config': {
            'dirs': {
                '_sites': './dirs/_sites',
                'pages': './dirs/pages',
                'templates': './dirs/templates',
                'static': './dirs/static',
                'data': './dirs/data',
            },
            'urls': {
                'home': 'https://home-page.com',
                'static': '/static',
            }
        }
    }


@pytest.fixture
def config():
    from pystaticpage.config import loads
    return loads('./dirs/config.yaml')


@pytest.fixture
def env(config):
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    e = Environment(
        loader=FileSystemLoader([config.config.dirs.templates, config.config.dirs.pages]),
        autoescape=select_autoescape(['html', 'xml'])
    )
    e.globals['current_year'] = 2020
    e.globals['do_print'] = lambda x: f'DO PRINT({x})'

    return e
