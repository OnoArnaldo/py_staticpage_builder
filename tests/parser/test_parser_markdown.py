import pytest
from tests.utils import fake_open
from pystaticpage import parser

LOG = []
FILES_CONTENT = {
    'index.md': ('template: blog_template.html\n'
                 'title: First thoughts\n'
                 '\n'
                 '# This is the header {: .title #main-title}\n'
                 '\n'
                 '* item 1\n'
                 '* item 2\n'
                 '* item 3')
}


@pytest.fixture
def dependency():
    from pystaticpage.dependency import set_dependencies, Dependency, dependency

    LOG.clear()
    set_dependencies(Dependency(
        open_file=fake_open(LOG, FILES_CONTENT)
    ))

    return dependency


def test_parse_markdown(dependency):
    parse = parser.MarkdownParser()
    result = parse('./dirs/sites/index.md')

    assert result == (
        '<h1 class="title" id="main-title">This is the header</h1>\n'
        '<ul>\n'
        '<li>item 1</li>\n'
        '<li>item 2</li>\n'
        '<li>item 3</li>\n'
        '</ul>',
        {
            'template': 'blog_template.html',
            'title': 'First thoughts'
        }
    )

    assert LOG == [
        ['open', ('./dirs/sites/index.md',), {}], ['read', 'index.md'],
    ]

# TODO: add data reference in the layout
