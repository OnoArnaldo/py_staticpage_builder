import shutil
import typing as _
from pathlib import Path

import minify_html as minify
import sass

from . import utils
from .data import Data
from .parse import Parser

type DirPath = Path | str


class Build:
    def __init__(
        self,
        sites_dir: DirPath,
        data_dir: DirPath,
        templates_dir: DirPath,
        static_dir: DirPath,
        sass_dir: DirPath,
        output_dir: DirPath,
    ) -> None:
        self.sites_dir = sites_dir
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.static_dir = static_dir
        self.sass_dir = sass_dir
        self.output_dir = output_dir

        self.filters: dict[str, _.Any] = {}
        self.globals: dict[str, _.Any] = {}

    def build(self) -> None:
        self.build_sites()
        self.build_static()
        self.build_sass()

    def build_sites(self) -> None:
        data = Data(self.data_dir)

        parser = Parser([self.sites_dir, self.templates_dir])
        parser.register_globals('data', data)
        parser.register_globals('today', utils.datetime_now)
        parser.register_globals('static', utils.static_url('/static'))

        for k, v in self.filters.items():
            parser.register_filter(k, v)

        for k, v in self.globals.items():
            parser.register_globals(k, v)

        sites_dir = Path(self.sites_dir)
        for fpath in sites_dir.rglob('*.*'):
            site_name = fpath.relative_to(sites_dir)
            html = parser.render(str(site_name))

            if fpath.stem == 'index':
                dest = Path(self.output_dir, site_name.parent)
            else:
                dest = Path(self.output_dir, site_name).with_suffix('')

            dest.mkdir(exist_ok=True, parents=True)
            (dest / 'index.html').write_text(html)

    def build_sass(self) -> None:
        output_dir = Path(self.output_dir) / 'static'
        sass.compile(
            dirname=(self.sass_dir, str(output_dir / 'css')), output_style='compressed'
        )

    def build_static(self) -> None:
        static_dir = Path(self.static_dir)
        output_dir = Path(self.output_dir) / 'static'

        shutil.copytree(static_dir, output_dir)

        self.minify_js()

    def minify_js(self) -> None:
        js_dir = Path(self.output_dir) / 'static'
        for fpath in js_dir.rglob('*.js'):
            dest = Path(fpath).with_stem(f'{fpath.stem}.min')

            minified = minify.minify(fpath.read_text(), minify_js=True)
            dest.write_text(minified)

    def register_filters(self, **filters: _.Any) -> _.Self:
        self.filters.update(filters)
        return self

    def register_globals(self, **globals: _.Any) -> _.Self:
        self.globals.update(globals)
        return self
