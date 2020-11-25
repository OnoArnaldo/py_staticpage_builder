import os
import shutil
import datetime
import markdown
import jinja2
from .data import Data
from .minifier import minify


def current_year():
    return datetime.datetime.utcnow().year


def create_builder(config):
    return Builder(config)


def create_jinja_env(config, data):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([config.dirs.templates, config.dirs.pages]),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )

    env.globals['current_year'] = current_year
    env.globals['data'] = data.function()
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
        self.initialised = False

    def init(self):
        if self.initialised:
            return

        self.initialised = True

    def clear(self):
        shutil.rmtree(self.config.dirs._sites, ignore_errors=True)
        self.initialised = False

    def save_content(self, template_name, content):
        new_file = os.path.join(self.config.dirs._sites, template_name)
        new_dir, _ = os.path.split(new_file)

        os.makedirs(new_dir, exist_ok=True)

        with open(new_file, 'w') as f:
            f.write(content)

    def build_pages(self):
        self.init()

        data = Data(self.config.dirs.data)
        env = create_jinja_env(self.config, data)
        for root, dirs, files in os.walk(self.config.dirs.pages):
            dir_name = root.replace(self.config.dirs.pages, '')

            for file_name in files:
                _, ext = os.path.splitext(file_name)
                template_name = os.path.join(dir_name, file_name).replace('/', '', 1)

                if ext.lower() == '.html':
                    content = HTMLParser.parser(env, template_name)
                    self.save_content(template_name, content)
                elif ext.lower() == '.md':
                    markdown_name = os.path.join(root, file_name)
                    content, headers = MarkdownParser.parse_from_file(markdown_name)
                    content = HTMLParser.parser(env, headers.get('template', 'base.html'), content=content, **headers)

                    self.save_content(template_name.replace(ext, '.html'), content)

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

    def compress_static(self):
        self.init()

        for root, dirs, files in os.walk(self.config.dirs._sites):
            for file_name in files:
                _, ext = os.path.splitext(file_name)
                if ext.lower() in ['.html', '.css', '.js']:
                    full_name = os.path.join(root, file_name)
                    minify(full_name, save_as=full_name if full_name.endswith('.html') else None)

    def run(self, *, clear=True, build_pages=True, build_static=True, compress_static=True):
        if clear:
            self.clear()

        if build_pages:
            self.build_pages()

        if build_static:
            self.build_static()

        if compress_static:
            self.compress_static()
