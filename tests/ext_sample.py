from jinja2 import nodes
from jinja2.ext import Extension
from textwrap import dedent


class HelloExtension(Extension):
    # https://jinja.palletsprojects.com/en/stable/extensions/
    tags = {"sayhello"}

    def __init__(self, environment):
        super().__init__(environment)
        environment.extend(fragment_cache_prefix="", fragment_cache=None)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression()]

        if parser.stream.skip_if("comma"):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        body = parser.parse_statements(["name:endsayhello"], drop_needle=True)

        return nodes.CallBlock(
            self.call_method("_say_hello", args), [], [], body
        ).set_lineno(lineno)

    def _say_hello(self, name, mark, caller):
        rv = caller()
        rv = dedent(rv).strip()
        return f'<hello name="{name}" mark="{mark}">{rv}</hello>'
