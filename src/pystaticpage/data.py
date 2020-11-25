import os
import glob
import yaml


def create_data(config):
    return Data(config.config.dirs.data)


class Data:
    def __init__(self, dir_name):
        self.dir_name = dir_name

    def _file_name(self, data_name):
        find_file = os.path.join(self.dir_name, f'{data_name}.*')
        for fname in glob.glob(find_file):
            return fname
        return None

    def loads(self, data_name):
        file_name = self._file_name(data_name)
        if file_name is None:
            return None

        with open(file_name) as f:
            text = f.read()
        f.close()

        return yaml.safe_load(text)

    def function(self):
        def _data(data_name, key=None):
            ret = self.loads(data_name)
            if isinstance(ret, dict) and key is not None:
                for k in key.split('/'):
                    ret = ret.get(k, {})
            return ret
        return _data
