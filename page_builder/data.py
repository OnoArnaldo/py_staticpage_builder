import os as _os
import yaml as _yaml


class Data:
    def __init__(self, config):
        self.cfg = config
        self.cache = {}

    def loads(self, fname):
        if fname in self.cache:
            return self.cache[fname]

        with open(fname, 'r') as f:
            ret = _yaml.safe_load(f)
        f.close()

        self.cache[fname] = ret
        return ret

    def full_fname(self, fname):
        return _os.path.join(self.cfg.dirs.data, fname + '.yaml')

    def function(self):
        def _data(fname, key=None):
            ret = self.loads(self.full_fname(fname))
            if isinstance(ret, dict) and key is not None:
                for k in key.split('/'):
                    ret = ret.get(k, {})
            return ret
        return _data

    def clear(self):
        self.cache = {}
