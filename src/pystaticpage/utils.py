import typing as _t
from pathlib import Path as _Path

from .dependency import dependency as _dep


def iter_files(root: _t.Union[str, _Path]) -> _t.Generator:
    if isinstance(root, str):
        root = _dep.path_class(root)

    if root.is_file():
        yield root
    else:
        for path in root.iterdir():
            yield from iter_files(path)


def save_content(dest: _Path, content: str) -> _t.NoReturn:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with _dep.open_file(dest, 'w') as f:
        f.write(content)


def copy_file(orig: _Path, dest: _Path) -> _t.NoReturn:
    dest.parent.mkdir(parents=True, exist_ok=True)
    _dep.shutil_copy(orig, dest)


def gzip_file(orig: _Path) -> _t.NoReturn:
    with _dep.open_file(orig, 'rb') as f_in:
        with _dep.gzip_open(orig.with_suffix(f'{orig.suffix}.gz'), 'wb') as f_out:
            _dep.shutil_copyfileobj(f_in, f_out)


def gzip_data(data: bytes) -> bytes:
    return _dep.gzip_compress(data, compresslevel=9, mtime=_dep.time())


def checksum(text: str) -> str:
    return _dep.md5(text).hexdigest()


def clean_folder(root: _Path) -> _t.NoReturn:
    if root.is_file():
        root.unlink(missing_ok=True)
    elif root.exists():
        for path in root.iterdir():
            clean_folder(path)
        root.rmdir()
