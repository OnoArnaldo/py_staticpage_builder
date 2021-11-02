import typing as _t
import yaml as _yaml
import dataclasses as _dc
import os as _os


class MissingConfigKey(Exception): pass
class ConfigKeyDoNotExist(Exception): pass


class DictData(dict):
    def get(self, item: str, default: _t.Any = None) -> _t.Any:
        data = dict(self)

        for i in item.split('.'):
            data = data.get(i, {})

        if default is None and not data:
            raise MissingConfigKey(f'Configuration key {item!r} is mandatory.')

        if isinstance(data, str) and data.startswith('$ENV:'):
            key_env = data[5:]
            data = _os.environ.get(key_env)

        return data or default


@_dc.dataclass
class Dirs:
    sites: str
    pages: str
    templates: str
    static: str
    cdn: str
    data: str
    sass: str


@_dc.dataclass
class URLs:
    home: str
    static: str
    cdn: str


@_dc.dataclass
class Pages:
    execute: bool
    only_index:  bool
    skip_for_index: _t.List[str]


@_dc.dataclass
class Static:
    execute: bool


@_dc.dataclass
class Minify:
    execute: bool
    extensions: _t.List[str]
    skip_files: _t.List[str]


@_dc.dataclass
class SASS:
    execute: bool
    output_style: str
    destination: str


@_dc.dataclass
class Gzip:
    execute: bool
    extensions: _t.List[str]
    skip_files: _t.List[str]


@_dc.dataclass
class CDN:
    execute: bool
    service_name: str
    region_name: str
    bucket_name: str
    object_key_prefix: str
    endpoint: str
    aws_access_key: str
    aws_secret_access_key: str


@_dc.dataclass
class Builder:
    clean_before_build: bool
    pages: Pages
    static: Static
    minify: Minify
    sass: SASS
    gzip: Gzip
    cdn: CDN


@_dc.dataclass
class Config:
    environment: str
    dirs: Dirs
    urls: URLs
    builder: Builder

    @classmethod
    def from_yaml(cls, data: str) -> 'Config':
        data = _yaml.safe_load(data)
        return cls.from_dict(data.get('config', {}))

    @classmethod
    def from_dict(cls, data: _t.Dict[str, _t.Any]) -> 'Config':
        data = DictData(data)
        return cls(
            environment=data.get('environment', 'prod'),
            dirs=Dirs(
                sites=data.get('dirs.sites'),
                pages=data.get('dirs.pages'),
                templates=data.get('dirs.templates'),
                static=data.get('dirs.static'),
                cdn=data.get('dirs.cdn'),
                data=data.get('dirs.data'),
                sass=data.get('dirs.sass'),
            ),
            urls=URLs(
                home=data.get('urls.home'),
                static=data.get('urls.static'),
                cdn=data.get('urls.cdn'),
            ),
            builder=Builder(
                clean_before_build=data.get('builder.clean_before_build', False),
                pages=Pages(
                    execute=data.get('builder.pages.execute', False),
                    only_index=data.get('builder.pages.only_index', True),
                    skip_for_index=data.get('builder.pages.skip_for_index', []),
                ),
                static=Static(
                    execute=data.get('builder.static.execute', False),
                ),
                minify=Minify(
                    execute=data.get('builder.minify.execute', False),
                    extensions=data.get('builder.minify.extensions', []),
                    skip_files=data.get('builder.minify.skip_files', []),
                ),
                sass=SASS(
                    execute=data.get('builder.sass.execute', False),
                    output_style=data.get('builder.sass.output_style', 'nested'),
                    destination=data.get('builder.sass.destination', 'static'),
                ),
                gzip=Gzip(
                    execute=data.get('builder.gzip.execute', False),
                    extensions=data.get('builder.gzip.extensions', []),
                    skip_files=data.get('builder.gzip.skip_files', []),
                ),
                cdn=CDN(
                    execute=data.get('builder.cdn.execute', False),
                    service_name=data.get('builder.cdn.service_name', ''),
                    region_name=data.get('builder.cdn.region_name', ''),
                    bucket_name=data.get('builder.cdn.bucket_name', ''),
                    object_key_prefix=data.get('builder.cdn.object_key_prefix', ''),
                    endpoint=data.get('builder.cdn.endpoint', ''),
                    aws_access_key=data.get('builder.cdn.aws_access_key', ''),
                    aws_secret_access_key=data.get('builder.cdn.aws_secret_access_key', ''),
                ),
            )
        )
