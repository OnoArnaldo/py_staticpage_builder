import os as _os
import shutil as _shutil
import markdown as _markdown
import datetime as _dt
from jinja2 import (
    Environment as _Env,
    FileSystemLoader as _FileSystemLoader,
    select_autoescape as _select_autoescape)
from .config import Config as _Config
from .data import Data as _Data


def current_year():
    return _dt.datetime.utcnow().year


class Builder:
    def __init__(self, config: _Config):
        self.cfg = config
        self.env = _Env(
            loader=_FileSystemLoader([self.templates, self.pages]),
            autoescape=_select_autoescape(['html', 'xml'])
        )
        self.env.globals['current_year'] = current_year

        self.data = _Data(self.cfg)
        self.env.globals['data'] = self.data.function()

    # region Properties
    @property
    def pages(self):
        return self.cfg.dirs.pages

    @property
    def templates(self):
        return self.cfg.dirs.templates

    @property
    def sites(self):
        return self.cfg.dirs.sites

    @property
    def static(self):
        return self.cfg.dirs.static
    # endregion

    def run(self, clear=True, build_pages=True, build_static=True):
        print('Building: clear: {}, pages: {}, static: {}'.format(
            clear, build_pages, build_static
        ))

        if clear:
            self.clear_sites()
        if build_pages:
            self.data.clear()
            self.process_pages()
        if build_static:
            self.process_static()

    def clear_sites(self):
        for root, dirs, files in _os.walk(self.sites):
            for dname in dirs:
                _shutil.rmtree(_os.path.join(root, dname))

            for fname in files:
                _os.remove(_os.path.join(root, fname))
            break

    def process_pages(self):
        for root, dirs, files in _os.walk(self.pages):
            for fn in files:
                _, fext = _os.path.splitext(fn)
                if fext in ['.md']:
                    md_name = self.template_name(root, fn)
                    self.create_dir_for_template(md_name)
                    self.process_markdown(md_name)
                else:
                    template_name = self.template_name(root, fn)
                    self.create_dir_for_template(template_name)
                    self.process_template(template_name)

    def process_static(self):
        dir_static = _os.path.join(self.sites, 'static')
        for root, dirs, files in _os.walk(self.static):
            for fn in files:
                orig = _os.path.join(root, fn)
                dest = orig.replace(self.static, dir_static)

                self.create_dir_for_file(dest)
                _shutil.copy2(orig, dest)

    def template_name(self, root, file_name):
        return _os.path.join(root, file_name).replace(self.pages+'/', '')

    def create_dir_for_template(self, template_name):
        fname = _os.path.join(self.sites, template_name)
        self.create_dir_for_file(fname)

    def create_dir_for_file(self, file_name):
        dname, _ = _os.path.split(file_name)
        if not _os.path.exists(dname):
            _os.makedirs(dname)

    def process_template(self, template_name):
        html = self.render_html(template_name)
        fname = _os.path.join(self.sites, template_name)
        self.save_html(fname, html)

    def process_markdown(self, md_name):
        html = self.render_markdown(md_name)

        fn, _ = _os.path.splitext(md_name)
        fname = _os.path.join(self.sites, fn + '.html')
        self.save_html(fname, html)

    def render_markdown(self, md_name):
        fname = _os.path.join(self.pages, md_name)
        with open(fname) as f:
            md = f.read()
        f.close()

        markdown = _markdown.Markdown(extensions=['meta', 'attr_list', 'tables'])
        content = markdown.convert(md)
        headers = {k: v[0] if len(v)==1 else v for k, v in markdown.Meta.items()}
        return self.render_html(headers.get('template'), content=content, **headers)

    def render_html(self, template_name, *args, **kwargs):
        template = self.env.get_template(template_name)
        return template.render(*args, **kwargs)

    def save_html(self, file_name, html):
        with open(file_name, 'w') as f:
            f.write(html)
        f.close()
