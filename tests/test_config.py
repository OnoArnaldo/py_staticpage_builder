import unittest
from page_builder import config
from tests.helpers import TestFile

CONFIG = '''\
config:
  dirs:
    sites: ./sites
    templates: ./templates
    static: ./static
  urls:
    home: https://my-page.com
    static: /static
'''


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        config.CONFIG_TEMPLATE = CONFIG
        config.open = TestFile

    def test_create_config(self):
        config.build_config('./the_test.yaml')

        self.assertEqual(CONFIG, TestFile.text)

    def test_load_config(self):
        cfg = config.loads('./the_test.yaml')

        self.assertEqual('./sites', cfg.dirs.sites)
        self.assertEqual('./templates', cfg.dirs.templates)
        self.assertEqual('./static', cfg.dirs.static)
        self.assertEqual('https://my-page.com', cfg.urls.home)
        self.assertEqual('/static', cfg.urls.static)
