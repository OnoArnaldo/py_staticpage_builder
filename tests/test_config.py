import pytest
from pystaticpage.config import loads, Config


@pytest.fixture
def config():
    cfg = loads('./dirs/config.yaml')
    assert isinstance(cfg, Config)
    return cfg


def test_config_with_dict(config_dict):
    cfg = Config(config_dict)

    assert cfg.config.dirs._sites == './dirs/_sites'
    assert cfg.config.dirs.data == './dirs/data'
    assert cfg.config.urls.home == 'https://home-page.com'


def test_config_with_yaml(config_yaml):
    cfg = Config.from_yaml(config_yaml)

    assert cfg.config.dirs._sites == './dirs/_sites'
    assert cfg.config.dirs.data == './dirs/data'
    assert cfg.config.urls.home == 'https://home-page.com'


def test_config_with_file(config):
    assert config.config.dirs._sites == './dirs/_sites'
    assert config.config.dirs.data == './dirs/data'
    assert config.config.urls.home == 'https://home-page.com'


def test_config_attribute_does_not_exists(config):
    with pytest.raises(AttributeError):
        assert config.config.dirs.not_exists


def test_config_key_does_not_exists(config):
    assert config.config.dirs.get('not_exists') is None
    assert config.config.dirs.get('not_exists', 123) == 123


def test_config_key_exists(config):
    assert config.config.dirs.get('data') == './dirs/data'
    assert config.get('config.dirs.data') == './dirs/data'
