import os
import secrets
import pytest
from pystaticpage.builder import MarkdownParser

SIMPLE = ('# Title 1 {: .title #main-title}\n'
          '\n'
          '* bullet 1\n'
          '* bullet 2\n'
          '\n--\n\n'
          'First Header  | Second Header\n'
          '------------- | -------------\n'
          'Content Cell  | Content Cell\n'
          'Content Cell  | Content Cell\n')

WITH_HEADER = ('template: base.html\n'
               'title: This is the title\n'
               'subtitle: This is the subtitle\n'
               '\n') + SIMPLE

SIMPLE_EXPECTED = ('<h1 class="title" id="main-title">Title 1</h1>\n'
                   '<ul>\n'
                   '<li>bullet 1</li>\n<li>bullet 2</li>\n'
                   '</ul>\n'
                   '<p>--</p>\n'
                   '<table>\n'
                   '<thead>\n'
                   '<tr>\n<th>First Header</th>\n<th>Second Header</th>\n</tr>\n'
                   '</thead>\n'
                   '<tbody>\n'
                   '<tr>\n<td>Content Cell</td>\n<td>Content Cell</td>\n</tr>\n'
                   '<tr>\n<td>Content Cell</td>\n<td>Content Cell</td>\n</tr>\n'
                   '</tbody>\n'
                   '</table>')


@pytest.fixture
def file_name():
    temp_file = os.path.join('./temp', secrets.token_urlsafe(6))
    with open(temp_file, 'w') as f:
        f.write(WITH_HEADER)
    f.close()

    yield temp_file

    os.remove(temp_file)


def test_basic():
    content, headers = MarkdownParser.parse(SIMPLE)

    assert content == SIMPLE_EXPECTED
    assert headers == {}


def test_with_meta():
    content, headers = MarkdownParser.parse(WITH_HEADER)

    assert content == SIMPLE_EXPECTED
    assert headers == {'subtitle': 'This is the subtitle', 'template': 'base.html', 'title': 'This is the title'}


def test_from_file(file_name):
    content, headers = MarkdownParser.parse_from_file(file_name)

    assert content == SIMPLE_EXPECTED
    assert headers == {'subtitle': 'This is the subtitle', 'template': 'base.html', 'title': 'This is the title'}
