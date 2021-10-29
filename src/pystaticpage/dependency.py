import typing as _t


class Dependency:
    def __init__(self, *,
                 open_file: _t.Callable = None,
                 shutil_copyfileobj: _t.Callable = None,
                 shutil_copy: _t.Callable = None,
                 requests_post: _t.Callable = None,
                 gzip_open: _t.Callable = None,
                 gzip_compress: _t.Callable = None,
                 utils_copy_file: _t.Callable = None,
                 utils_iter_files: _t.Callable = None,
                 utils_save_content: _t.Callable = None,
                 utils_gzip_file: _t.Callable = None,
                 utils_gzip_data: _t.Callable = None,
                 utils_checksum: _t.Callable = None,
                 utils_clean_folder: _t.Callable = None,
                 md5: _t.Callable = None,
                 minify: _t.Callable = None,
                 time: _t.Callable = None,
                 sass_compile: _t.Callable = None,
                 boto_session: _t.Callable = None,
                 path_class: _t.Type = None,
                 html_parser_class: _t.Type = None,
                 markdown_parser_class: _t.Type = None,
                 jinja_loader_class: _t.Type = None,
                 data_class: _t.Type = None):

        self._open_file = open_file
        self._utils_copy_file = utils_copy_file
        self._utils_iter_files = utils_iter_files
        self._utils_save_content = utils_save_content
        self._utils_gzip_file = utils_gzip_file
        self._utils_gzip_data = utils_gzip_data
        self._utils_checksum = utils_checksum
        self._utils_clean_folder = utils_clean_folder
        self._md5 = md5
        self._shutil_copyfileobj = shutil_copyfileobj
        self._shutil_copy = shutil_copy
        self._requests_post = requests_post
        self._gzip_open = gzip_open
        self._gzip_compress = gzip_compress
        self._minify = minify
        self._time = time
        self._sass_compile = sass_compile
        self._boto_session = boto_session

        self._path_class = path_class
        self._html_parser_class = html_parser_class
        self._markdown_parser_class = markdown_parser_class
        self._jinja_loader_class = jinja_loader_class
        self._data_class = data_class

    @property
    def open_file(self) -> _t.Callable:
        return self._open_file or open

    @property
    def utils_copy_file(self) -> _t.Callable:
        from . import utils
        return self._utils_copy_file or utils.copy_file

    @property
    def utils_iter_files(self) -> _t.Callable:
        from . import utils
        return self._utils_iter_files or utils.iter_files

    @property
    def utils_save_content(self) -> _t.Callable:
        from . import utils
        return self._utils_save_content or utils.save_content

    @property
    def utils_clean_folder(self) -> _t.Callable:
        from . import utils
        return self._utils_clean_folder or utils.clean_folder

    @property
    def requests_post(self) -> _t.Callable:
        import requests
        return self._requests_post or requests.post

    @property
    def path_class(self) -> _t.Type:
        import pathlib
        return self._path_class or pathlib.Path

    @property
    def html_parser_class(self) -> _t.Type:
        from . import parser
        return self._html_parser_class or parser.HtmlParser

    @property
    def markdown_parser_class(self) -> _t.Type:
        from . import parser
        return self._markdown_parser_class or parser.MarkdownParser

    @property
    def jinja_loader_class(self) -> _t.Type:
        import jinja2
        return self._jinja_loader_class or jinja2.FileSystemLoader

    @property
    def data_class(self) -> _t.Type:
        from . import data
        return self._data_class or data.Data

    @property
    def utils_gzip_file(self) -> _t.Callable:
        from . import utils
        return self._utils_gzip_file or utils.gzip_file

    @property
    def gzip_open(self):
        import gzip
        return self._gzip_open or gzip.open

    @property
    def gzip_compress(self):
        import gzip
        return self._gzip_compress or gzip.compress

    @property
    def utils_gzip_data(self):
        from . import utils
        return self._utils_gzip_data or utils.gzip_data

    @property
    def utils_checksum(self):
        from . import utils
        return self._utils_checksum or utils.checksum

    @property
    def md5(self):
        from hashlib import md5
        return self._md5 or md5

    @property
    def shutil_copyfileobj(self):
        import shutil
        return self._shutil_copyfileobj or shutil.copyfileobj

    @property
    def shutil_copy(self):
        import shutil
        return self._shutil_copy or shutil.copy2

    @property
    def minify(self):
        from . import minifier
        return self._minify or minifier.Minifier()

    @property
    def time(self):
        from time import time
        return self._time or time

    @property
    def sass_compile(self):
        from sass import compile
        return self._sass_compile or compile

    @property
    def boto_session(self):
        from boto3 import session
        return self._boto_session or session.Session

    def copy(self, other: 'Dependency') -> _t.NoReturn:
        for k, v in vars(other).items():
            cur_v = getattr(self, k, None)
            setattr(self, k, v or cur_v)

    def reset(self) -> _t.NoReturn:
        for k, v in vars(self).items():
            setattr(self, k, None)


dependency = Dependency()


def set_dependencies(dep: Dependency) -> _t.NoReturn:
    dependency.copy(dep)


def reset_dependencies() -> _t.NoReturn:
    dependency.reset()
