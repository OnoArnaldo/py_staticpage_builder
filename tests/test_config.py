from pystaticpage.config import loads, Config


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


def test_config_with_file():
    cfg = loads('./dirs/config.yaml')

    assert isinstance(cfg, Config)
    assert cfg.config.dirs._sites == './dirs/_sites'
    assert cfg.config.dirs.data == './dirs/data'
    assert cfg.config.urls.home == 'https://home-page.com'
