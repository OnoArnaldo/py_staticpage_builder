from contextlib import ContextDecorator

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


class TestFile(ContextDecorator):
    text = ''

    def __init__(self, *args, **kwargs):
        if args[1] == 'r':
            self.__class__.text = CONFIG
        else:
            self.__class__.text = ''
        self.pos = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def write(self, text):
        self.__class__.text += text

    def close(self):
        pass

    def read(self, size):
        res = self.__class__.text[self.pos:self.pos+size]
        self.pos += size
        return res