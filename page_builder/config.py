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


def build_config(file_name):
    with open(file_name, 'w') as f:
        f.write(CONFIG_TEMPLATE)
    f.close()


def loads(file_name):
    with open(file_name, 'r') as f:
        cfg = yaml.safe_load(f)
    f.close()
    return Config(cfg.get('config', {}))


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
