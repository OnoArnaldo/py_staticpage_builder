import typing as _t
import abc as _abc
import re as _re
import dataclasses as _dc
import jinja2 as _jinja
from pathlib import Path as _Path
from datetime import datetime as _dt
from functools import cache as _cache, cached_property as _cached_property

from .dependency import dependency as _dep
from .mimetypes import MIMETYPES


def current_year():
    return _dt.utcnow().year


@_dc.dataclass(frozen=True)
class DirsConfig:
    site: str = ''
    pages: str = ''
    templates: str = ''
    static: str = ''
    cdn: str = ''
    data: str = ''
    sass: str = ''


@_dc.dataclass(frozen=True)
class URLsConfig:
    home: str = ''
    static: str = ''
    cdn: str = ''


@_dc.dataclass(frozen=True)
class PageConfig:
    execute: bool = False
    ony_index: bool = False
    skip_for_index: _t.List[str] = _dc.field(default_factory=list)


@_dc.dataclass(frozen=True)
class GzipConfig:
    execute: bool = False
    extensions: _t.List[str] = _dc.field(default_factory=list)
    skip_files: _t.List[str] = _dc.field(default_factory=list)


@_dc.dataclass(frozen=True)
class StaticConfig:
    execute: bool = False


@_dc.dataclass(frozen=True)
class MinifyConfig:
    execute: bool = False
    extensions: _t.List[str] = _dc.field(default_factory=list)
    skip_files: _t.List[str] = _dc.field(default_factory=list)
    skip_dirs: _t.List[str] = _dc.field(default_factory=list)


@_dc.dataclass(frozen=True)
class SassConfig:
    execute: bool = False
    output_style: str = ''
    destination: str = ''


@_dc.dataclass(frozen=True)
class CdnConfig:
    execute: bool = False
    service_name: str = ''
    region_name: str = ''
    bucket_name: str = ''
    object_key_prefix: str = ''
    endpoint: str = ''
    aws_access_key: str = ''
    aws_secret_access_key: str = ''


@_dc.dataclass(frozen=True)
class CdnObject:
    destination: _Path = _Path()
    text: _t.Union[str, bytes] = ''

    do_generate_key: _t.Callable = None
    do_minify: _t.Callable[[_Path], str] = None
    do_gzip: _t.Callable[[bytes], bytes] = None

    @_cached_property
    def key(self):
        return self.do_generate_key(self.destination)

    @_cached_property
    def minified_key(self):
        return self.do_generate_key(self.minified_destination)

    @_cached_property
    def gzipped_key(self):
        return self.do_generate_key(self.gzipped_destination)

    @_cached_property
    def gzipped_minified_key(self):
        return self.do_generate_key(self.gzipped_minified_destination)

    @_cached_property
    def minified_destination(self):
        return self.destination.with_suffix(f'.min{self.destination.suffix}')

    @_cached_property
    def gzipped_destination(self):
        return self.destination.with_suffix(f'{self.destination.suffix}.gz')

    @_cached_property
    def gzipped_minified_destination(self):
        return self.minified_destination.with_suffix(f'{self.minified_destination.suffix}.gz')

    @_cached_property
    def text_byte(self):
        return self.text.encode() if isinstance(self.text, str) else self.text

    @_cached_property
    def minified_text_byte(self):
        return self.do_minify(self.destination).encode()

    @_cached_property
    def gzipped_text_byte(self):
        return self.do_gzip(self.text_byte)

    @_cached_property
    def gzipped_minified_text_byte(self):
        return self.do_gzip(self.minified_text_byte)

    @_cached_property
    def checksum(self):
        return _dep.utils_checksum(self.text_byte)

    @property
    def content_type(self):
        return MIMETYPES.get(self.destination.suffix, ['application/octet-stream'])[0]

    @property
    def content_encoding(self):
        return ''

    @property
    def gzipped_content_encoding(self):
        return 'gzip'


class MinifierMixin:
    def minify_config(self, config: MinifyConfig) -> 'MinifierMixin':
        self._minify = config
        return self

    def can_generate_minify(self, path: _Path) -> bool:
        return self._minify.execute \
               and self._skip_file_ext_minify(path) \
               and not self._skip_file_minify(path) \
               and not self._skip_folder_minify(path)

    def _skip_file_ext_minify(self, path: _Path) -> bool:
        return path.suffix in self._minify.extensions

    def _skip_file_minify(self, path: _Path) -> bool:
        return any(_re.match(p, path.name) for p in self._minify.skip_files)

    def _skip_folder_minify(self, path: _Path) -> bool:
        return any(_re.match(part, pattern)
                   for pattern in self._minify.skip_dirs
                   for part in self.relative_path_to_dest(path).parent.parts)

    def execute_minify(self, path: _Path, overwrite: bool = False) -> _t.NoReturn:
        if self.can_generate_minify(path):
            return _dep.minify(path, overwrite=overwrite)

    def execute_minify_from_path_to_text(self, path: _Path) -> str:
        if self.can_generate_minify(path):
            return _dep.minify.minify_to_text(path)


class GziperMixin:
    def gzip_config(self, config: GzipConfig) -> 'GziperMixin':
        self._gzip = config
        return self

    def can_generate_gzip(self, path: _Path) -> bool:
        return self._gzip.execute \
               and self._skip_file_ext_gzip(path) \
               and not self._skip_file_gzip(path)

    def _skip_file_ext_gzip(self, path: _Path) -> bool:
        return path.suffix in self._gzip.extensions

    def _skip_file_gzip(self, path: _Path) -> bool:
        return any(_re.match(p, path.name) for p in self._gzip.skip_files)

    def execute_gzip(self, path: _Path):
        if self.can_generate_gzip(path):
            _dep.utils_gzip_file(path)

    def execute_gzip_from_text_to_text(self, text: _t.Union[str, bytes]) -> bytes:
        if isinstance(text, str):
            text = text.encode()

        if self._gzip.execute:
            return _dep.utils_gzip_data(text)


class TaskBase(_abc.ABC):
    def __init__(self):
        self._dirs = DirsConfig()
        self._urls = URLsConfig()

    def dirs_config(self, config: DirsConfig) -> 'TaskBase':
        self._dirs = config
        return self

    def urls_config(self, config: URLsConfig) -> 'TaskBase':
        self._urls = config
        return self

    @_abc.abstractmethod
    def execute(self) -> _t.NoReturn:
        pass

    @property
    @_abc.abstractmethod
    def root_path(self) -> _Path:
        pass

    def relative_path(self, path: _Path) -> _Path:
        return path.relative_to(self.root_path)

    def relative_path_to_dest(self, path: _Path) -> _Path:
        return path.relative_to(self._dirs.site)


class TaskBuildPage(TaskBase, MinifierMixin, GziperMixin):
    def __init__(self):
        super().__init__()

        self._page = PageConfig()
        self._methods = {}

        self.current_year = current_year

    @property
    def root_path(self) -> _Path:
        return _dep.path_class(self._dirs.pages)

    def page_config(self, config: PageConfig) -> 'TaskBuildPage':
        self._page = config
        return self

    def methods(self, methods: _t.Dict[str, _t.Callable]) -> 'TaskBuildPage':
        self._methods = methods
        return self

    @_cache
    def _build_env(self) -> _jinja.Environment:
        env = _jinja.Environment(
            loader=_dep.jinja_loader_class([self._dirs.templates, self._dirs.pages]),
            autoescape=_jinja.select_autoescape(['html', 'xml']),
        )

        env.globals['url_home'] = self._urls.home
        env.globals['url_static'] = self._urls.static
        env.globals['url_cdn'] = self._urls.cdn
        env.globals['data'] = _dep.data_class(self._dirs.data)
        env.globals['current_year'] = self.current_year

        for k, v in self._methods.items():
            env.globals[k] = v

        return env

    def _has_match(self, value: str, patterns: _t.List[str]) -> bool:
        return any([_re.match(p, value) for p in patterns])

    def _file_name(self, fname: _Path) -> _Path:
        if fname.name != 'index.html' \
                and self._page.ony_index \
                and not self._has_match(fname.name, self._page.skip_for_index):
            return fname.with_suffix('').joinpath('index.html')
        return fname

    def _execute_html(self, orig: _Path) -> _Path:
        template_name = self.relative_path(orig)
        parser = _dep.html_parser_class(self._build_env())

        dest = self._file_name(_dep.path_class(self._dirs.site, template_name))
        _dep.utils_save_content(
            dest=dest,
            content=parser(template_name=str(template_name))
        )

        return dest

    def _execute_markdown(self, orig: _Path) -> _Path:
        markdown = _dep.markdown_parser_class()
        html = _dep.html_parser_class(self._build_env())

        content, headers = markdown(orig)
        relative = self.relative_path(orig).with_suffix('.html')

        dest = self._file_name(_dep.path_class(self._dirs.site, relative))
        _dep.utils_save_content(
            dest=dest,
            content=html(template_name=headers.get('template', 'base.html'), content=content, **headers)
        )

        return dest

    def _execute_others(self, orig: _Path) -> _Path:
        relative = self.relative_path(orig)
        dest = _dep.path_class(self._dirs.site, relative)

        _dep._utils_copy_file(orig, dest)

        return dest

    def execute(self) -> _t.NoReturn:
        if self._page.execute:
            for f in _dep.utils_iter_files(self.root_path):
                suffix = f.suffix.lower()

                if suffix == '.html':
                    dest = self._execute_html(f)
                elif suffix == '.md':
                    dest = self._execute_markdown(f)
                else:
                    dest = self._execute_others(f)

                self.execute_minify(dest, True)
                self.execute_gzip(dest)


class TaskCopyStatic(TaskBase, MinifierMixin, GziperMixin):
    def __init__(self):
        super().__init__()

        self._static = StaticConfig()

    @property
    def root_path(self) -> _Path:
        return _dep.path_class(self._dirs.static)

    def static_config(self, static: StaticConfig) -> 'TaskCopyStatic':
        self._static = static
        return self

    def execute(self) -> _t.NoReturn:
        if self._static.execute:
            for path in _dep.utils_iter_files(self.root_path):
                dest = _dep.path_class(self._dirs.site, 'static', self.relative_path(path))

                _dep.utils_copy_file(path, dest)

                if min_path := self.execute_minify(dest, False):
                    self.execute_gzip(min_path)
                self.execute_gzip(dest)


class TaskBuildSASS(TaskBase, MinifierMixin, GziperMixin):
    def __init__(self):
        super().__init__()

        self._sass = SassConfig()

    def sass_config(self, config: SassConfig) -> 'TaskBuildSASS':
        self._sass = config
        return self

    @property
    def root_path(self) -> _Path:
        return _dep.path_class(self._dirs.sass)

    @property
    def static_folder(self) -> _Path:
        return _dep.path_class(self._urls.static.removeprefix('/'))

    @property
    def _is_dest_cdn(self):
        return self._sass.destination == 'cdn'

    @property
    def _is_dest_static(self):
        return self._sass.destination != 'cdn'

    def execute(self) -> _t.NoReturn:
        if self._sass.execute:
            if self._is_dest_cdn:
                dest_root = _dep.path_class(self._dirs.cdn, 'css')
            else:
                dest_root = _dep.path_class(self._dirs.site, self.static_folder, 'css')

            for f in _dep.utils_iter_files(self._dirs.sass):
                if f.suffix in ['.scss', '.sass']:
                    rel = f.relative_to(self._dirs.sass)
                    dest = dest_root.joinpath(rel).with_suffix('.css')

                    res = _dep.sass_compile(filename=str(f.absolute()), output_style=self._sass.output_style)
                    _dep.utils_save_content(dest, res)

                    if self._is_dest_static:
                        self.execute_gzip(dest)

                        if min_path := self.execute_minify(dest):
                            self.execute_gzip(min_path)


class TaskCopyCDN(TaskBase, MinifierMixin, GziperMixin):
    def __init__(self):
        super().__init__()

        self._cdn = CdnConfig()

    @property
    def root_path(self) -> _Path:
        return _dep.path_class(self._dirs.cdn)

    def relative_path_to_dest(self, path: _Path) -> _Path:
        return path.relative_to(self._dirs.cdn)

    def cdn_config(self, cdn: CdnConfig) -> 'TaskCopyCDN':
        self._cdn = cdn
        return self

    def object_key(self, path: _Path) -> str:
        return str(_dep.path_class(self._cdn.object_key_prefix, self.relative_path(path)))

    def _read_file(self, path: _Path) -> bytes:
        with _dep.open_file(path, 'rb') as f:
            return f.read()

    def _start_client(self) -> _t.NoReturn:
        session = _dep.boto_session()
        self._current_client = session.client(service_name=self._cdn.service_name,
                                              region_name=self._cdn.region_name,
                                              endpoint_url=self._cdn.endpoint,
                                              aws_access_key_id=self._cdn.aws_access_key,
                                              aws_secret_access_key=self._cdn.aws_secret_access_key)

    def _bucket_exists(self) -> bool:
        try:
            self._current_client.head_bucket(Bucket=self._cdn.bucket_name)
            return True
        except:
            return False

    def _valid_checksum(self, key: str, checksum: str) -> bool:
        try:
            resp = self._current_client.get_object(Bucket=self._cdn.bucket_name, Key=key)
            return resp.get('Metadata', {}).get('Checksum', '') == checksum
        except:
            return False

    def _create_cdn_object(self, f: _Path) -> CdnObject:
        return CdnObject(destination=f,
                         text=self._read_file(f),
                         do_generate_key=self.object_key,
                         do_minify=self.execute_minify_from_path_to_text,
                         do_gzip=self.execute_gzip_from_text_to_text)

    def _put_object(self, obj: CdnObject) -> _t.NoReturn:
        if not self._valid_checksum(obj.key, obj.checksum):
            resp = self._current_client.put_object(
                Bucket=self._cdn.bucket_name,
                Key=obj.key,
                Body=obj.text_byte,
                ACL='public',
                ContentEncoding=obj.content_encoding,
                ContentType=obj.content_type,
                Metadata={'Checksum': obj.checksum}
            )

    def _put_minified_object(self, obj: CdnObject, can_minify: bool) -> _t.NoReturn:
        if can_minify and not self._valid_checksum(obj.minified_key, obj.checksum):
            resp = self._current_client.put_object(
                Bucket=self._cdn.bucket_name,
                Key=obj.minified_key,
                Body=obj.minified_text_byte,
                ACL='public',
                ContentEncoding=obj.content_encoding,
                ContentType=obj.content_type,
                Metadata={'Checksum': obj.checksum}
            )

    def _put_gzipped_object(self, obj: CdnObject, can_gzip: bool) -> _t.NoReturn:
        if can_gzip and not self._valid_checksum(obj.gzipped_key, obj.checksum):
            resp = self._current_client.put_object(
                Bucket=self._cdn.bucket_name,
                Key=obj.gzipped_key,
                Body=obj.gzipped_text_byte,
                ACL='public',
                ContentEncoding=obj.gzipped_content_encoding,
                ContentType=obj.content_type,
                Metadata={'Checksum': obj.checksum}
            )

    def _put_gzipped_minified_object(self, obj: CdnObject, can_minify: bool, can_gzip: bool) -> _t.NoReturn:
        if can_minify and can_gzip and not self._valid_checksum(obj.gzipped_minified_key, obj.checksum):
            resp = self._current_client.put_object(
                Bucket=self._cdn.bucket_name,
                Key=obj.gzipped_minified_key,
                Body=obj.gzipped_minified_text_byte,
                ACL='public',
                ContentEncoding=obj.gzipped_content_encoding,
                ContentType=obj.content_type,
                Metadata={'Checksum': obj.checksum}
            )

    def execute(self) -> _t.NoReturn:
        self._start_client()

        if self._bucket_exists():
            for f in _dep.utils_iter_files(self._dirs.cdn):
                obj = self._create_cdn_object(f)
                can_minify = self.can_generate_minify(f)
                can_gzip = self.can_generate_gzip(f)

                self._put_object(obj)
                self._put_minified_object(obj, can_minify)
                self._put_gzipped_object(obj, can_gzip)
                self._put_gzipped_minified_object(obj, can_minify, can_gzip)
