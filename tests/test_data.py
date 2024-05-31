from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from staticpage.data import Data


class FakePath(Path):
    def __init__(self, *args, **kwargs):
        super().__init__('not-a-file')
        self.logs: list[str] = []

    def __call__(self, *args, **kwargs):
        self.logs.append(str(args))
        return self

    def open(self, *args, **kwargs):
        self.logs.append('open')
        return self

    def read(self, *args, **kwargs):
        return (
            b'title = "The Title"\n'
            b'[company]\n'
            b'name = "The company"\n'
            b'[company.address]\n'
            b'line1 = "The line 1"\n'
            b'line2 = "The line 2"\n'
        )


@pytest.fixture
def data() -> Data:
    return Data(data_dir=FakePath())


@pytest.fixture
def fake_file(monkeypatch: 'MonkeyPatch'):
    fake = FakePath()
    monkeypatch.setattr('staticpage.data.Path', fake)
    return fake


def test_data_empty(data):
    d = data.from_text('')
    assert d['field01'] == ''


def test_data_from_str(data):
    data_dict = data.from_text(
        'title = "The Title"\n'
        '[company]\n'
        'name = "The company"\n'
        '[company.address]\n'
        'line1 = "The line 1"\n'
        'line2 = "The line 2"\n'
    )

    assert data_dict['title'] == 'The Title'
    assert data_dict['company']['name'] == 'The company'
    assert data_dict['company']['address']['line1'] == 'The line 1'


def test_data_from_file(data, fake_file):
    d = data.from_file('fakefile.toml')

    assert d['title'] == 'The Title'
    assert d['company']['name'] == 'The company'
    assert d['company']['address']['line1'] == 'The line 1'
    assert fake_file.logs == ["('fakefile.toml',)", 'open']


def test_data_from_obj(data):
    class TheData:
        title = 'The Title'
        company = {
            'name': 'The company',
            'address': {'line1': 'The line 1', 'line2': 'The line 2'},
        }

    d = data.from_object(TheData)

    assert d['title'] == 'The Title'
    assert d['company']['name'] == 'The company'
    assert d['company']['address']['line1'] == 'The line 1'


def test_data_caller(data, fake_file):
    d = data('fakefile')

    assert d['title'] == 'The Title'
    assert d['company']['name'] == 'The company'
    assert d['company']['address']['line1'] == 'The line 1'
    assert fake_file.logs == ["('fakefile.toml',)", 'open']
