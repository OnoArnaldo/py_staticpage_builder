import typing as _t
import markdown as _markdown
from jinja2 import Environment as _Env
from pathlib import Path as _Path
from .dependency import dependency as _dep


class HtmlParser:
    def __init__(self, env: _Env):
        self.env = env

    def __call__(self, template_name: str, *args, **kwargs) -> str:
        return self.parse(template_name, *args, **kwargs)

    def parse(self, template_name: str, *args, **kwargs) -> str:
        template = self.env.get_template(template_name)
        return template.render(*args, **kwargs)


class MarkdownParser:
    def __init__(self):
        self.extensions = ['meta', 'attr_list', 'tables']

    def __call__(self, file_name: _t.Union[str, _Path]) -> _t.Tuple[str, _t.Dict]:
        return self.parse(file_name)

    def _parse_value(self, value: list) -> _t.Any:
        return value[0] if len(value) == 1 else value

    def _parse(self, text: str) -> _t.Tuple[str, _t.Dict]:
        mk = _markdown.Markdown(extensions=self.extensions)
        content = mk.convert(text)
        headers = {k: self._parse_value(v) for k, v in mk.Meta.items()}

        return content, headers

    def parse(self, file_name: _t.Union[str, _Path]) -> _t.Tuple[str, _t.Dict]:
        with _dep.open_file(file_name) as f:
            return self._parse(f.read())
