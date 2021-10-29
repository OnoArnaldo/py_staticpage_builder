import pytest
from pathlib import Path

from tests.utils import fake_open, fake_path
from pystaticpage import data

LOG = []
FILES_CONTENT = {
    'company.yml': (b'title: The Title\n'
                    b'contact:\n'
                    b'  email: contact@email.com\n'
                    b'  phone: 1234.5678\n')
}


@pytest.fixture
def dependency():
    from pystaticpage.dependency import set_dependencies, Dependency, dependency

    LOG.clear()
    set_dependencies(Dependency(
        path_class=fake_path(LOG, [r'data/company\.yml']),
        open_file=fake_open(LOG, FILES_CONTENT),
    ))

    return dependency


def test_data(dependency):
    d = data.Data('./data')
    v = d('company')

    assert v['title'] == 'The Title'
    assert v['contact']['email'] == 'contact@email.com'

    assert LOG == [['open', (Path('data/company.yml'),), {}], ['read', 'company.yml']]
