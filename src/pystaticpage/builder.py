import typing as _t
from pathlib import Path as _Path
from .config import Config as _Config
from .dependency import dependency as _dep
from . import tasks as _tasks


class Builder:
    def __init__(self):
        self._config: _Config

    def config(self, config: _Config) -> 'Builder':
        self._config = config
        return self

    @property
    def dirs_config(self):
        return _tasks.DirsConfig(
            templates=self._config.dirs.templates,
            static=self._config.dirs.static,
            pages=self._config.dirs.pages,
            cdn=self._config.dirs.cdn,
            data=self._config.dirs.data,
            site=self._config.dirs.sites,
            sass=self._config.dirs.sass,
        )

    @property
    def urls_config(self):
        return _tasks.URLsConfig(
            static=self._config.urls.static,
            cdn=self._config.urls.cdn,
            home=self._config.urls.home
        )

    @property
    def page_config(self):
        return _tasks.PageConfig(
            execute=self._config.builder.pages.execute,
            ony_index=self._config.builder.pages.only_index,
            skip_for_index=self._config.builder.pages.skip_for_index
        )

    @property
    def minify_config(self):
        return _tasks.MinifyConfig(
            execute=self._config.builder.minify.execute,
            extensions=self._config.builder.minify.extensions,
            # skip_dirs=, #TODO: implement this option in config
            skip_files=self._config.builder.minify.skip_files
        )

    @property
    def gzip_config(self):
        return _tasks.GzipConfig(
            execute=self._config.builder.gzip.execute,
            extensions=self._config.builder.gzip.extensions,
            skip_files=self._config.builder.gzip.skip_files,
        )

    @property
    def sass_config(self):
        return _tasks.SassConfig(
            execute=self._config.builder.sass.execute,
            destination=self._config.builder.sass.destination,
            output_style=self._config.builder.sass.output_style
        )

    @property
    def static_config(self):
        return _tasks.StaticConfig(
            execute=self._config.builder.static.execute
        )

    @property
    def cdn_config(self):
        return _tasks.CdnConfig(
            execute=self._config.builder.cdn.execute,
            bucket_name=self._config.builder.cdn.bucket_name,
            region_name=self._config.builder.cdn.region_name,
            service_name=self._config.builder.cdn.service_name,
            endpoint=self._config.builder.cdn.endpoint,
            object_key_prefix=self._config.builder.cdn.object_key_prefix,
            aws_access_key=self._config.builder.cdn.aws_access_key,
            aws_secret_access_key=self._config.builder.cdn.aws_secret_access_key
        )

    def run(self):
        _dep.utils_clean_folder(_dep.path_class(self.dirs_config.site))

        _tasks.TaskBuildPage()\
            .dirs_config(self.dirs_config)\
            .urls_config(self.urls_config)\
            .page_config(self.page_config)\
            .minify_config(self.minify_config)\
            .gzip_config(self.gzip_config)\
            .execute()

        _tasks.TaskBuildSASS()\
            .dirs_config(self.dirs_config)\
            .urls_config(self.urls_config)\
            .sass_config(self.sass_config)\
            .minify_config(self.minify_config)\
            .gzip_config(self.gzip_config)\
            .execute()

        _tasks.TaskCopyStatic()\
            .dirs_config(self.dirs_config)\
            .urls_config(self.urls_config)\
            .minify_config(self.minify_config)\
            .gzip_config(self.gzip_config)\
            .static_config(self.static_config)\
            .execute()

        _tasks.TaskCopyCDN()\
            .dirs_config(self.dirs_config)\
            .urls_config(self.urls_config)\
            .minify_config(self.minify_config)\
            .gzip_config(self.gzip_config)\
            .cdn_config(self.cdn_config)\
            .execute()


def create_builder(config: _t.Union[_Config, _Path, str, _t.Dict]) -> Builder:
    """
    Create the an instance of static page builder.
    :param config: it can be one of the following.
                    * Config: the config object.
                    * Path: path for the configuration file.
                    * str: text with the yaml structure.
                    * Dict: dictionary with the values.
    :return: Builder
    """
    if isinstance(config, _Config):
        cfg = config
    elif isinstance(config, _Path):
        with _dep.open_file(config) as f:
            cfg = _Config.from_yaml(f.read())
    elif isinstance(config, str):
        cfg = _Config.from_yaml(config)
    elif isinstance(config, dict):
        cfg = _Config.from_dict(config)
    else:
        raise Exception('Invalid config type.')

    return Builder().config(cfg)
