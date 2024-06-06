import typing as _
import tomllib
from pathlib import Path
from collections import UserDict


class DataDict(UserDict):
    def __getitem__(self, item):
        if item in self.data:
            ret = self.data[item]
            return DataDict(ret) if isinstance(ret, dict) else ret
        return ''


class Data:
    def __init__(self, data_dir: str | Path):
        self.root = Path(data_dir)

    def __call__(self, filename: str) -> DataDict:
        return self.from_file(f'{filename}.toml')

    def from_text(self, text: str, loads: _.Callable = None) -> DataDict:
        loads = loads or tomllib.loads
        data = loads(text)
        return DataDict(data)

    def from_file(self, filename: str, load: _.Callable = None) -> DataDict:
        load = load or tomllib.load

        with Path(filename).open('rb') as f:
            data = load(f)
            return DataDict(data)

    def from_object(self, obj: object) -> DataDict:
        data = DataDict()
        for key in dir(obj):
            data[key] = getattr(obj, key)
        return data
