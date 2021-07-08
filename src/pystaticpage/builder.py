import os
import shutil
import datetime
import re
import markdown
import jinja2
import sass

from .data import Data
from .minifier import minify


def current_year():
    return datetime.datetime.utcnow().year


def create_builder(config, template_methods=None):
    builder = Builder(config)
    builder.set_template_methods(template_methods)
    return builder


def create_jinja_env(config, data, methods=None):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([config.dirs.templates, config.dirs.pages]),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )

    env.globals['current_year'] = current_year
    env.globals['url_home'] = lambda: config.urls.home
    env.globals['url_static'] = lambda: config.urls.static
    env.globals['data'] = data.function()

    methods = methods or {}
    for k, v in methods.items():
        env.globals[k] = v

    return env


class MarkdownParser:
    @classmethod
    def _parse_value(cls, value: list):
        return value[0] if len(value) == 1 else value

    @classmethod
    def parse(cls, text):
        mk = markdown.Markdown(extensions=['meta', 'attr_list', 'tables'])
        content = mk.convert(text)
        headers = {k: cls._parse_value(v) for k, v in mk.Meta.items()}

        return content, headers

    @classmethod
    def parse_from_file(cls, file_name):
        with open(file_name) as f:
            text = f.read()
        f.close()

        return cls.parse(text)


class HTMLParser:
    @classmethod
    def parser(cls, env, template_name, *args, **kwargs):
        template = env.get_template(template_name)
        return template.render(*args, **kwargs)


class Builder:
    def __init__(self, config):
        self.config = config.config
        self._template_methods = None
        self.initialised = False

    def init(self):
        if self.initialised:
            return

        self.initialised = True

    def clear(self):
        shutil.rmtree(self.config.dirs._sites, ignore_errors=True)
        self.initialised = False

    def set_template_methods(self, template_methods):
        self._template_methods = template_methods

    def _not_in_skip_list(self, template_name, skip_for_index):
        for pattern in skip_for_index:
            matches = re.findall(pattern, template_name)
            if len(matches) != 0:
                return False
        return True

    def save_content(self, template_name, content, only_index_page, skip_for_index):
        if only_index_page and template_name != 'index.html' and self._not_in_skip_list(template_name, skip_for_index):
            template_name, _ = os.path.splitext(template_name)
            new_file = os.path.join(self.config.dirs._sites, template_name, 'index.html')
            new_dir, _ = os.path.split(new_file)
        else:
            new_file = os.path.join(self.config.dirs._sites, template_name)
            new_dir, _ = os.path.split(new_file)

        os.makedirs(new_dir, exist_ok=True)

        with open(new_file, 'w') as f:
            f.write(content)

    def copy_file(self, file_name):
        orig_file = os.path.join(self.config.dirs.pages, file_name)
        new_file = os.path.join(self.config.dirs._sites, file_name)
        new_dir, _ = os.path.split(new_file)

        os.makedirs(new_dir, exist_ok=True)

        shutil.copy2(orig_file, new_file)

    def build_pages(self, only_index_page, skip_for_index):
        self.init()

        data = Data(self.config.dirs.data)
        env = create_jinja_env(self.config, data, self._template_methods)
        for root, dirs, files in os.walk(self.config.dirs.pages):
            dir_name = root.replace(self.config.dirs.pages, '')

            for file_name in files:
                _, ext = os.path.splitext(file_name)
                template_name = os.path.join(dir_name, file_name).replace('/', '', 1)

                if ext.lower() == '.html':
                    content = HTMLParser.parser(env, template_name)
                    self.save_content(template_name, content, only_index_page, skip_for_index)
                elif ext.lower() == '.md':
                    markdown_name = os.path.join(root, file_name)
                    content, headers = MarkdownParser.parse_from_file(markdown_name)
                    content = HTMLParser.parser(env, headers.get('template', 'base.html'), content=content, **headers)

                    self.save_content(template_name.replace(ext, '.html'), content, only_index_page, skip_for_index)
                else:
                    self.copy_file(template_name)

    def build_static(self):
        self.init()

        for root, dirs, files in os.walk(self.config.dirs.static):
            dir_static = self.config.urls.static
            dir_static = dir_static[1:] if dir_static.startswith('/') else dir_static
            dir_static = os.path.join(self.config.dirs._sites, dir_static)

            dir_name = root.replace(self.config.dirs.static, dir_static)

            for file_name in files:
                os.makedirs(dir_name, exist_ok=True)

                shutil.copy2(
                    os.path.join(root, file_name),
                    os.path.join(dir_name, file_name)
                )

    def build_sass(self, output_style):
        self.init()

        dir_css = os.path.join(self.config.dirs._sites, 'static', 'css')

        os.makedirs(dir_css, exist_ok=True)

        sass.compile(dirname=(self.config.dirs.sass, dir_css), output_style=output_style)

    def compress_static(self):
        self.init()

        for root, dirs, files in os.walk(self.config.dirs._sites):
            for file_name in files:
                is_min_js = file_name.endswith('.min.js')
                is_min_css = file_name.endswith('.min.css')

                _, ext = os.path.splitext(file_name)
                if ext.lower() in ['.html', '.css', '.js'] and not is_min_css and not is_min_js:
                    full_name = os.path.join(root, file_name)
                    minify(full_name, save_as=full_name if full_name.endswith('.html') else None)

    def _value(self, arg, config_key, default=None):
        if arg is None:
            return self.config.get(config_key, default)
        return arg

    def run(self, *,
            clear: bool = None,
            build_pages: bool = None,
            build_static: bool = None,
            build_sass: bool = None,
            sass_output_style: str = None,
            compress_static: bool = None,
            only_index_page: bool = None,
            skip_for_index: list = None):

        if self._value(clear, 'builder.clear_before_build', True):
            self.clear()

        if self._value(build_pages, 'builder.pages', True):
            self.build_pages(
                only_index_page=self._value(only_index_page, 'builder.use_only_index_page', False),
                skip_for_index=self._value(skip_for_index, 'builder.skip_for_index', [])
            )

        if self._value(build_static, 'builder.static', True):
            self.build_static()

        if self._value(build_sass, 'builder.sass.build', True):
            output_style = self._value(sass_output_style, 'builder.sass.output_style', 'nested')
            self.build_sass(output_style)

        if self._value(compress_static, 'builder.compress_static', True):
            self.compress_static()
