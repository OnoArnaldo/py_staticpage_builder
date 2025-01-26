import pytest
from datetime import datetime
from staticpage import utils


class FakeDateTime:
    @classmethod
    def now(cls, *args, **kwargs):
        return datetime(2024, 6, 1, 12, 30)


@pytest.fixture(autouse=True)
def dt(monkeypatch):
    monkeypatch.setattr("staticpage.utils.datetime", FakeDateTime)


def test_datetime_now():
    assert utils.datetime_now() == "01/06/2024"


def test_static_url():
    static = utils.static_url("/static")
    assert static("css/home.css") == "/static/css/home.css"
    assert static("/css/home.css") == "/static/css/home.css"
