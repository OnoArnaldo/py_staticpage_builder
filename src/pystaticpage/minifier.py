import typing as _t
from pathlib import Path as _Path
from .dependency import dependency as _dep


class NotPossibleToMinify(Exception): pass


class Minifier:
    HTML = 'https://html-minifier.com/raw'
    CSS = 'https://cssminifier.com/raw'
    JS = 'https://javascript-minifier.com/raw'

    EXTENSIONS = ('.html', '.css', '.js')

    def __init__(self):
        self._current_file: _Path = None
        self._current_overwrite: bool = None

    def __call__(self, fname: _Path, *, overwrite: bool = False) -> _Path:
        return self.minify(fname, overwrite)

    @property
    def url_for(self) -> str:
        suffix = self._current_file.suffix.lower()

        if suffix == '.html':
            return self.HTML
        elif suffix == '.css':
            return self.CSS
        elif suffix == '.js':
            return self.JS

        raise NotPossibleToMinify(f'It is not possible to minify the file {self._current_file!s}.')

    @property
    def text(self) -> str:
        with _dep.open_file(self._current_file) as f:
            return f.read()

    @property
    def destination(self) -> _Path:
        if self._current_overwrite:
            return self._current_file
        else:
            return self._current_file.with_suffix(f'.min{self._current_file.suffix}')

    def save(self, fname: _Path, text: str) -> _t.NoReturn:
        with _dep.open_file(fname, 'w') as f:
            f.write(text)

    def minify(self, fname: _t.Union[str, _Path], overwrite: bool = False) -> _Path:
        self._current_file = _dep.path_class(fname)
        self._current_overwrite = overwrite
        dest = self.destination

        self.save(
            fname=dest,
            text=_dep.requests_post(self.url_for, data={'input': self.text}).text
        )

        return dest

    def minify_to_text(self, fname: _t.Union[str, _Path]) -> str:
        self._current_file = _dep.path_class(fname)

        return _dep.requests_post(self.url_for, data={'input': self.text}).text
