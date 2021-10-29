import pytest
import gzip
from pathlib import Path
from tests.utils import fake_iter_file, fake_open
from pystaticpage import tasks, dependency as dep

LOG = []
CDN_DIR_FILES = [
    Path('./dirs/cdn/css/main.css'),
    Path('./dirs/cdn/css/template.css'),
    Path('./dirs/cdn/js/main.js'),
    Path('./dirs/cdn/js/help.js'),
    Path('./dirs/cdn/private/js/help.js'),
    Path('./dirs/cdn/img/log.jpeg'),
]


class Gzipped:
    def __init__(self, expected):
        if isinstance(expected, str):
            expected = expected.encode()

        self.expected = expected

    def __repr__(self):
        return f'Gzipped({self.expected})'

    def __eq__(self, other):
        return gzip.decompress(other) == self.expected


def fake_session(log):
    class Fake:
        def __init__(self):
            pass

        def client(self, *args, **kwargs):
            log.append(['session_client', args, kwargs])
            return self

        def head_bucket(self, *args, **kwargs):
            log.append(['client_head_bucket', args, kwargs])

        def head_object(self, *args, **kwargs):
            log.append(['client_head_object', args, kwargs])
            raise Exception('object does not exist.')

        def get_object(self, *args, **kwargs):
            log.append(['client_get_object', args, kwargs])
            if kwargs.get('Key') in ['static/css/template.css', 'static/css/template.css.gz',
                                     'static/css/template.min.css', 'static/css/template.min.css.gz']:
                return {'Metadata': {'Checksum': 'ca76a4a7d62e25ad59b25f5833ce9827'}}
            return {'Metadata': {'Checksum': ''}}

        def put_object(self, *args, **kwargs):
            log.append(['client_put_object', args, kwargs])
            return {'result': 'OK'}

    return Fake


def fake_minify(log):
    class Fake:
        def __call__(self, *args, **kwargs):
            log.append(['minify'], args, kwargs)

        def minify_to_text(self, *args, **kwargs):
            log.append(['minify_to_text', args, kwargs])
            return str(args[0]).replace('/', '_').replace('.', '_')

    return Fake()


@pytest.fixture
def dependency():
    dep.reset_dependencies()
    dep.set_dependencies(dep.Dependency(
        utils_iter_files=fake_iter_file(LOG, './dirs/cdn', CDN_DIR_FILES),
        boto_session=fake_session(LOG),
        minify=fake_minify(LOG),
        time=lambda: 1635217453.7966132,
        open_file=fake_open([], {})
    ))

    return dep.dependency


def test_copy_cdn(urls, dirs, dependency):
    builder = tasks.TaskCopyCDN() \
        .dirs_config(dirs) \
        .urls_config(urls) \
        .gzip_config(tasks.GzipConfig(
            execute=True,
            extensions=['.js', '.css'],
            skip_files=[r'help\.(min\.){0,1}js(\.gz){0,1}'],
        )) \
        .cdn_config(tasks.CdnConfig(
            execute=True,
            service_name='s3',
            region_name='regname',
            endpoint='https://endpoint.com',
            bucket_name='my-cdn',
            object_key_prefix='static',
            aws_access_key='acckey',
            aws_secret_access_key='secret',
        )).minify_config(tasks.MinifyConfig(
            execute=True,
            extensions=['.js', '.css'],
            skip_files=[r'help\.(min\.){0,1}js(\.gz){0,1}'],
            skip_dirs=['private']
        ))

    builder.execute()

    assert LOG == [['session_client', (), {'aws_access_key_id': 'acckey',
                                           'aws_secret_access_key': 'secret',
                                           'endpoint_url': 'https://endpoint.com',
                                           'region_name': 'regname',
                                           'service_name': 's3'}],
                   ['client_head_bucket', (), {'Bucket': 'my-cdn'}],
                   ['iter_file', ('./dirs/cdn',), {}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/main.css'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'main.css',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'text/css',
                                              'Key': 'static/css/main.css',
                                              'Metadata': {'Checksum': '4abed1c996f46e1b2ad61757af46ece4'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/main.min.css'}],
                   ['minify_to_text', (Path('dirs/cdn/css/main.css'),), {}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'dirs_cdn_css_main_css',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'text/css',
                                              'Key': 'static/css/main.min.css',
                                              'Metadata': {'Checksum': '4abed1c996f46e1b2ad61757af46ece4'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/main.css.gz'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': Gzipped('main.css'),
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': 'gzip',
                                              'ContentType': 'text/css',
                                              'Key': 'static/css/main.css.gz',
                                              'Metadata': {'Checksum': '4abed1c996f46e1b2ad61757af46ece4'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/main.min.css.gz'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': Gzipped('dirs_cdn_css_main_css'),
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': 'gzip',
                                              'ContentType': 'text/css',
                                              'Key': 'static/css/main.min.css.gz',
                                              'Metadata': {'Checksum': '4abed1c996f46e1b2ad61757af46ece4'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/template.css'}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/template.min.css'}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/template.css.gz'}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/css/template.min.css.gz'}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/js/main.js'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'main.js',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'text/javascript',
                                              'Key': 'static/js/main.js',
                                              'Metadata': {'Checksum': '7a9076d6d94e62c13d641aa71f19ae8e'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/js/main.min.js'}],
                   ['minify_to_text', (Path('dirs/cdn/js/main.js'),), {}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'dirs_cdn_js_main_js',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'text/javascript',
                                              'Key': 'static/js/main.min.js',
                                              'Metadata': {'Checksum': '7a9076d6d94e62c13d641aa71f19ae8e'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/js/main.js.gz'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': Gzipped('main.js'),
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': 'gzip',
                                              'ContentType': 'text/javascript',
                                              'Key': 'static/js/main.js.gz',
                                              'Metadata': {'Checksum': '7a9076d6d94e62c13d641aa71f19ae8e'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/js/main.min.js.gz'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': Gzipped('dirs_cdn_js_main_js'),
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': 'gzip',
                                              'ContentType': 'text/javascript',
                                              'Key': 'static/js/main.min.js.gz',
                                              'Metadata': {'Checksum': '7a9076d6d94e62c13d641aa71f19ae8e'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/js/help.js'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'help.js',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'text/javascript',
                                              'Key': 'static/js/help.js',
                                              'Metadata': {'Checksum': '6c22d2b7e82045f8015c8eb010992d80'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/private/js/help.js'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'help.js',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'text/javascript',
                                              'Key': 'static/private/js/help.js',
                                              'Metadata': {'Checksum': '6c22d2b7e82045f8015c8eb010992d80'}}],
                   ['client_get_object', (), {'Bucket': 'my-cdn', 'Key': 'static/img/log.jpeg'}],
                   ['client_put_object', (), {'ACL': 'public',
                                              'Body': b'log.jpeg',
                                              'Bucket': 'my-cdn',
                                              'ContentEncoding': '',
                                              'ContentType': 'image/jpeg',
                                              'Key': 'static/img/log.jpeg',
                                              'Metadata': {'Checksum': '458e0789e6870d6c774df7ed50fd5147'}}],
                   ]
