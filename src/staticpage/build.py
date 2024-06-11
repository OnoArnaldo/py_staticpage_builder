import shutil
import typing as _
import subprocess
from pathlib import Path

import minify_html as minify

from . import utils
from .data import Data
from .parse import Parser

type DirPath = Path | str


class Build:
    def __init__(
        self, *,
        sites_dir: DirPath,
        data_dir: DirPath,
        templates_dir: DirPath,
        static_dir: DirPath,
        sass_dir: DirPath,
        output_dir: DirPath,
        sass_bin: DirPath,
    ) -> None:
        self.sites_dir = sites_dir
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.static_dir = static_dir
        self.sass_dir = sass_dir
        self.output_dir = output_dir
        self.sass_bin = sass_bin

        self.filters: dict[str, _.Any] = {}
        self.globals: dict[str, _.Any] = {}

    def build(self, *,
              clean: bool = False,
              skip_sites: bool = False,
              skip_static: bool = False,
              skip_sass: bool = False) -> None:
        if clean:
            self.clean_output_dir()
        if not skip_sites:
            self.build_sites()
        if not skip_static:
            self.build_static()
        if not skip_sass:
            self.build_sass()

    def clean_output_dir(self) -> None:
        shutil.rmtree(self.output_dir, ignore_errors=True)

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
        output_dir = Path(self.output_dir) / 'static' / 'css'
        sass_dir = Path(self.sass_dir)

        for fpath in sass_dir.rglob('*.scss'):
            dest = (output_dir / fpath.relative_to(sass_dir)).with_suffix('.css')
            dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                subprocess.run([str(self.sass_bin), str(fpath), str(dest)], capture_output=True)
                subprocess.run([str(self.sass_bin), '--style=compressed', str(fpath), str(dest.with_stem(f'{dest.stem}.min'))],
                               capture_output=True)
            except subprocess.CalledProcessError:
                pass

    def build_static(self) -> None:
        static_dir = Path(self.static_dir)
        output_dir = Path(self.output_dir) / 'static'

        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)

        self.minify_js()

    def minify_js(self) -> None:
        js_dir = Path(self.output_dir) / 'static'
        for fpath in js_dir.rglob('*.js'):
            if fpath.stem.endswith('.min'):
                continue

            dest = Path(fpath).with_stem(f'{fpath.stem}.min')

            minified = minify.minify(fpath.read_text(), minify_js=True)
            dest.write_text(minified)

    def register_filters(self, **filters: _.Any) -> _.Self:
        self.filters.update(filters)
        return self

    def register_globals(self, **globals: _.Any) -> _.Self:
        self.globals.update(globals)
        return self
