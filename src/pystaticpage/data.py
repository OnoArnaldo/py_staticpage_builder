import typing as _t
import yaml as _yaml
from pathlib import Path as _Path
from .dependency import dependency as _dep


class DataDoesNotExist(Exception): pass


class Data:
    """
    To be used inside templates.

    Example:
        {% set home = data('home') %}
        <h1>{{ home.title }}</h1>
    """

    def __init__(self, dir_name: _t.Union[str, _Path]):
        self.dir_name = dir_name

    def __call__(self, data_name):
        path = _dep.path_class(self.dir_name, data_name).with_suffix('.yaml')
        if not path.exists():
            path = _dep.path_class(self.dir_name, data_name).with_suffix('.yml')

        if not path.exists():
            raise DataDoesNotExist(f'Data file for {data_name} does not exist.')

        with _dep.open_file(path) as f:
            return _yaml.safe_load(f)
