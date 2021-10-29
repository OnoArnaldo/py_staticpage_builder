import re
from contextlib import contextmanager
from pathlib import Path, _PosixFlavour


def fake_func(name, log, returns=None):
    def _fake(*args, **kwargs):
        log.append([name, args, kwargs])
        try:
            ret = returns[_fake.idx]
            _fake.idx += 1
            return ret
        except:
            return None

    _fake.idx = 0
    return _fake


def fake_iter_file(log, dir, files):
    def _fake(*args, **kwargs):
        log.append(['iter_file', args, kwargs])

        if args[0] == dir:
            for f in files:
                yield f

    return _fake


def fake_open(log, texts: dict):
    class FakeStream:
        def __init__(self, fname):
            self.end = False
            self.fname = Path(fname)

        def write(self, *args, **kwargs):
            log.append(['write', self.fname.name, args, kwargs])

        def read(self, *args, **kwargs):
            if not self.end:
                log.append(['read', self.fname.name])

                self.end = True
                return texts.get(self.fname.name, self.fname.name)
            return b''

    @contextmanager
    def _fake(*args, **kwargs):
        log.append(['open', args, kwargs])
        yield FakeStream(args[0])

    return _fake


def fake_path(log, exist_files=('.*',)):
    class FakePath(Path):
        _flavour = _PosixFlavour()

        def exists(self) -> bool:
            return any(re.match(pattern, str(self)) for pattern in exist_files)

        def __eq__(self, other):
            return str(self) == str(other)

    return FakePath


class IgnoreValue:
    def __eq__(self, other):
        return True


Ignore = IgnoreValue()
