import pytest
from pystaticpage.data import create_data, Data
from pystaticpage.config import loads


@pytest.fixture
def data():
    cfg = loads('./dirs/config.yaml')
    data = create_data(cfg)
    assert isinstance(data, Data)
    return data


def test_data(data):
    company = data.loads('company')

    assert company['name'] == 'Company ABC'
    assert company['contacts']['email'] == 'contact@email.com'
    assert len(company['books']) == 3
    assert company['books'][0] == 'Thinking, Fast and Slow'


def test_data_not_exists(data):
    not_exists = data.loads('not_exists')

    assert not_exists is None


def test_data_with_key(data):
    func = data.function()
    contacts = func('company', 'contacts')

    assert contacts['email'] == 'contact@email.com'
    assert contacts['phone'] == '+123 456789012'
