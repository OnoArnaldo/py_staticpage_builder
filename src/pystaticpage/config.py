import yaml

CONFIG_TEMPLATE = '''\
config:
  dirs:
    _sites: ./web/_sites
    templates: ./web/templates
    static: ./web/static
    pages: ./web/pages
    data: ./web/data
  urls:
    home: https://home-page.com
    static: /static
'''


def loads(file_name):
    with open(file_name) as f:
        text = f.read()
    f.close()

    return Config.from_yaml(text)


# Ref: based on https://github.com/alon710/DictToObj
class Config:
    def __init__(self, dict_obj):
        for k, v in dict_obj.items():
            if isinstance(v, (list, tuple)):
                setattr(self, k, [Config(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, Config(v) if isinstance(v, dict) else v)

    def __repr__(self):
        return 'Config({})'.format(', '.join([k for k in self.__dict__]))

    @classmethod
    def from_yaml(cls, yaml_text):
        value = yaml.safe_load(yaml_text)
        return cls(value)

    def get(self, key, default=None):
        if '.' in key:
            keys = key.split('.')
            attr = getattr(self, keys[0], Config({}))
            return attr.get('.'.join(keys[1:]), default)

        return getattr(self, key, default)
