import typing as _
from pathlib import Path
from string import Template
from textwrap import dedent

from jinja2 import Environment, FileSystemLoader, select_autoescape, nodes
from jinja2.ext import Extension
from markdown import Markdown
from minify_html import minify

if _.TYPE_CHECKING:  # pragma: no cover
    from jinja2 import Template as JinjaTemplate
    from jinja2.runtime import Macro


class MarkdownExtension(Extension):
    tags = {'markdown'}

    def parse(self, parser):
        stream = next(parser.stream)
        lineno = stream.lineno
        body = parser.parse_statements(['name:endmarkdown'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('call_markdown'), [], [], body
        ).set_lineno(lineno)

    def call_markdown(self, caller: 'Macro') -> str:
        block_text = caller()
        block_text = dedent(block_text).strip()
        return self.parse_markdown(block_text)[0]

    @classmethod
    def parse_markdown(cls, text: str) -> tuple[str, dict]:
        md = Markdown(extensions=['meta', 'fenced_code', 'attr_list'])
        text = md.convert(text)
        meta = {k: ' '.join(v) for k, v in md.Meta.items()}
        result = Template(text).safe_substitute(meta) if meta else text
        return result, meta


class Parser:
    def __init__(self, template_dir: str | Path | _.Sequence[str | Path]):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
        )
        self.env.add_extension('staticpage.parse.MarkdownExtension')

    def render(self, template_name: str, **context: _.Any) -> str:
        template: JinjaTemplate = self.env.get_template(template_name)
        result = template.render(**context)

        if template_name.endswith('.md'):
            result, meta = MarkdownExtension.parse_markdown(result)

            if 'extends' in meta:
                template: JinjaTemplate = self.env.get_template(meta['extends'])
                result = template.render(content=result, **{**context, **meta})

        return minify(result)

    def register_filter(self, name: str, filter: _.Callable) -> None:
        self.env.filters[name] = filter

    def register_globals(self, name: str, value: _.Any) -> None:
        self.env.globals[name] = value
