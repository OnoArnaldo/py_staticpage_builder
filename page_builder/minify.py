import requests as _requests
import os as _os
from glob import glob as _glob
from .config import Config as _Config


class Minifier:
    def __init__(self, config: _Config):
        self.config = config

    @property
    def js_dir(self):
        return self.config.minify.js_dir

    @property
    def level(self):
        return self.config.minify.compilation_level

    def _get_code(self, fname):
        with open(fname) as f:
            ret = f.read()
        f.close()
        return ret

    def _do_minify(self, code):
        resp = _requests.post(
            'https://closure-compiler.appspot.com/compile',
            params={
                'js_code': code,
                'compilation_level': self.level,
                'output_format': 'text',
                'output_info': 'compiled_code'
            },
            headers={'Content-type': 'application/x-www-form-urlencoded'}
        )
        return resp.text

    def _save(self, code, fname):
        with open(fname, 'w') as f:
            f.write(code)
        f.close()

    def run(self):
        for fname in _glob(_os.path.join(self.js_dir, '*.js')):
            if '.min.' in fname:
                continue

            fn, ext = _os.path.splitext(fname)
            self._save(
                self._do_minify(
                    self._get_code(fname)
                ),
                '{}.min{}'.format(fn, ext)
            )
