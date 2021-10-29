from jinja2 import BaseLoader, Environment
from pathlib import Path
from tests.utils import Ignore
from pystaticpage import parser


def fake_loader(log):
    class FakeLoader(BaseLoader):
        def __init__(self, path):
            self.path = path

        def get_source(self, environment, template):
            log.append(['get_source', environment, template])

            source = 'TITLE: {{ title }}'
            filename = Path(self.path).joinpath(template)
            uptodate = 1634723250.9914954

            return source, filename, uptodate

    return FakeLoader


def test_parse_html():
    log = []
    env = Environment(loader=fake_loader(log)('./jinja_root'))

    parse = parser.HtmlParser(env)
    result = parse('template_name.html', title='The Title')

    assert result == 'TITLE: The Title'
    assert log == [
        ['get_source', Ignore, 'template_name.html'],
    ]
