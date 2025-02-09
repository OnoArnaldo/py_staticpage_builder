import shutil
import typing as _
import subprocess
from pathlib import Path

import minify_html as minify

from . import utils
from .data import Data
from .parse import Parser

if _.TYPE_CHECKING:
    from jinja2.ext import Extension

type DirPath = Path | str


class Build:
    def __init__(
        self,
        *,
        sites_dir: DirPath,
        data_dir: DirPath,
        templates_dir: DirPath,
        static_dir: DirPath,
        sass_dir: DirPath,
        output_dir: DirPath,
        sass_bin: DirPath,
        skip_parsing: _.Sequence[str] = None,
        parse_keep_extension: _.Sequence[str] = None,
    ) -> None:
        self.sites_dir = sites_dir
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.static_dir = static_dir
        self.sass_dir = sass_dir
        self.output_dir = output_dir
        self.sass_bin = sass_bin
        self.skip_parsing = skip_parsing or []
        self.parse_keep_extension = parse_keep_extension or []

        self.filters: dict[str, _.Any] = {}
        self.globals: dict[str, _.Any] = {}
        self.extensions: list[str] = []

    def _should_skip_parsing(self, path: Path) -> bool:
        return any(path.match(p) for p in self.skip_parsing)

    def _should_keep_extension(self, path: Path) -> bool:
        return any(path.match(p) for p in self.parse_keep_extension)

    def build(
        self,
        *,
        clean: bool = False,
        skip_sites: bool = False,
        skip_static: bool = False,
        skip_sass: bool = False,
    ) -> None:
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
        parser.register_globals("data", data)
        parser.register_globals("today", utils.datetime_now)
        parser.register_globals("static", utils.static_url("/static"))

        for k, v in self.filters.items():
            parser.register_filter(k, v)

        for k, v in self.globals.items():
            parser.register_globals(k, v)

        for v in self.extensions:
            parser.register_extension(v)

        sites_dir = Path(self.sites_dir)
        for fpath in sites_dir.rglob("*.*"):
            site_name = fpath.relative_to(sites_dir)

            if self._should_skip_parsing(fpath):
                dest = Path(self.output_dir, site_name)
                dest.parent.mkdir(exist_ok=True)

                shutil.copy2(str(fpath), str(dest))
            else:
                html = parser.render(str(site_name))

                if self._should_keep_extension(fpath):
                    dest = Path(self.output_dir, site_name)
                    dest.parent.mkdir(exist_ok=True)
                    dest.write_text(html)
                else:
                    if fpath.stem == "index":
                        dest = Path(self.output_dir, site_name.parent)
                    else:
                        dest = Path(self.output_dir, site_name).with_suffix("")

                    dest.mkdir(exist_ok=True, parents=True)
                    (dest / "index.html").write_text(html)

    def build_sass(self) -> None:
        output_dir = Path(self.output_dir) / "static" / "css"
        sass_dir = Path(self.sass_dir)

        for fpath in sass_dir.rglob("*.scss"):
            dest = (output_dir / fpath.relative_to(sass_dir)).with_suffix(".css")
            dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                subprocess.run(
                    [str(self.sass_bin), str(fpath), str(dest)], capture_output=True
                )
                subprocess.run(
                    [
                        str(self.sass_bin),
                        "--style=compressed",
                        str(fpath),
                        str(dest.with_stem(f"{dest.stem}.min")),
                    ],
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                pass

    def build_static(self) -> None:
        static_dir = Path(self.static_dir)
        output_dir = Path(self.output_dir) / "static"

        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)

        self.minify_js()

    def minify_js(self) -> None:
        js_dir = Path(self.output_dir) / "static"
        for fpath in js_dir.rglob("*.js"):
            if fpath.stem.endswith(".min"):
                continue

            dest = Path(fpath).with_stem(f"{fpath.stem}.min")

            minified = minify.minify(fpath.read_text(), minify_js=True)
            dest.write_text(minified)

    def register_filters(self, **filters: _.Any) -> _.Self:
        self.filters.update(filters)
        return self

    def register_globals(self, **globals: _.Any) -> _.Self:
        self.globals.update(globals)
        return self

    def register_extensions(self, *extensions: str | _.Type["Extension"]) -> _.Self:
        self.extensions.extend(extensions)
        return self
