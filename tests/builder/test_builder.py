import pytest
import gzip
from pathlib import Path
from tests.utils import fake_func
from pystaticpage import create_builder
from pystaticpage import dependency as dep

ROOT = Path('.', 'builder')
LOG = []


class Gzipped:
    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        return gzip.decompress(other) == self._value

    def __repr__(self):
        return f'Gzipped({self._value})'


def delete_folders(path: Path):
    if path.is_file():
        path.unlink(missing_ok=True)
    else:
        for p in path.iterdir():
            delete_folders(p)
        path.rmdir()


def fake_session(log):
    class Fake:
        def client(self, *args, **kwargs):
            log.append(['Session client', args, kwargs])
            return self

        def head_bucket(self, *args, **kwargs):
            log.append(['Session head_bucket', args, kwargs])
            return {}

        def get_object(self, *args, **kwargs):
            log.append(['Session get_object', args, kwargs])
            return {}

        def put_object(self, *args, **kwargs):
            log.append(['Session put_object', args, kwargs])
            return {}

    return Fake


def fake_post(log):
    class FakeResponse:
        def __init__(self, text):
            self.text = text

    def _fake(*args, **kwargs):
        log.append(['request post', args, kwargs])

        txt = kwargs.get('data').get('input')
        return FakeResponse(txt.replace('\n', '').replace(' ', ''))

    return _fake


@pytest.fixture
def dependency():
    LOG.clear()
    dep.reset_dependencies()
    dep.set_dependencies(dep.Dependency(
        boto_session=fake_session(LOG),
        requests_post=fake_post(LOG),
        time=lambda: 1635217453.7966132
    ))

    yield dep.dependency

    delete_folders(ROOT.joinpath('dirs', '_sites'))


def test_builder(dependency):
    config = ROOT.joinpath('dirs/config.yaml')

    builder = create_builder(config)
    builder.run(template_methods={'parse_date': fake_func('parse_date', LOG, ['2021-11-01'])})

    # TODO: check generated files
    # TODO: add methods into templates

    assert LOG == [
        ['request post', ('https://html-minifier.com/raw',), {
            'data': {'input': '<!DOCTYPE html>\n'
                              '<html lang="en">\n'
                              '<head>\n'
                              '    <meta charset="UTF-8">\n'
                              '    <title>How to build static page</title>\n'
                              '</head>\n'
                              '<body>\n'
                              '\n'
                              '    <h1>How to build static page</h1>\n'
                              '    <pre><h1>Title 1</h1>\n'
                              '<h2>Subtitle</h2>\n'
                              '<ul>\n'
                              '<li>item 1</li>\n'
                              '<li>item 2</li>\n'
                              '<li>item 3</li>\n'
                              '</ul></pre>\n'
                              '\n'
                              '</body>\n'
                              '</html>'}}],
        ['parse_date', ('0000',), {}],
        ['request post', ('https://html-minifier.com/raw',), {
            'data': {'input': '<!DOCTYPE html>\n'
                              '<html lang="en">\n'
                              '<head>\n'
                              '    <meta charset="UTF-8">\n'
                              '    <title></title>\n'
                              '</head>\n'
                              '<body>\n'
                              '\n'
                              '    <h1>The main page</h1>\n'
                              '    <h2>The company name</h2>\n'
                              '    <p>11112222</p>\n'
                              '\n'
                              '    <p>https://home-page.com</p>\n'
                              '    <p>/static</p>\n'
                              '    <p>https://cdn.home-page.com/root</p>\n'
                              '\n'
                              '    <p>2021-11-01</p>\n'
                              '\n'
                              '</body>\n'
                              '</html>'}}],
        ['request post', ('https://cssminifier.com/raw',), {
            'data': {'input': '.contact {\n'
                              '  background-color: black;\n'
                              '  font-size: 20rem; }\n'}}],
        ['request post', ('https://cssminifier.com/raw',), {
            'data': {'input': '.hero {\n'
                              '    font-size: 13rem;\n'
                              '}\n'
                              '\n'
                              '.hero .title {\n'
                              '    font-size: 16rem;\n'
                              '}'}}],
        ['request post', ('https://javascript-minifier.com/raw',), {
            'data': {'input': "document.body.getElementsByClassName('title')[0].textContent = 'Sample';"}}],
        ['Session client', (), {'aws_access_key_id': 'the_key',
                                'aws_secret_access_key': 'the_secret',
                                'endpoint_url': 'https://the-url.com',
                                'region_name': 'regname',
                                'service_name': 'servname'}],
        ['Session head_bucket', (), {'Bucket': 'bucname'}],
        ['Session get_object', (), {'Bucket': 'bucname', 'Key': 'keyprefix/timetable.css'}],
        ['Session put_object', (), {'ACL': 'public-read',
                                    'Body': b'.timetable {\n'
                                            b'    font-size: 5rem;\n'
                                            b'}\n\n'
                                            b'.timetable .title {\n'
                                            b'    font-size: 10rem;\n'
                                            b'}\n',
                                    'Bucket': 'bucname',
                                    'ContentEncoding': '',
                                    'ContentType': 'text/css; charset=utf-8',
                                    'Key': 'keyprefix/timetable.css',
                                    'Metadata': {'checksum': '948b1d03e2eef4a3181a3888e7df9647'}}],
        ['Session get_object', (), {'Bucket': 'bucname', 'Key': 'keyprefix/timetable.min.css'}],
        ['request post', ('https://cssminifier.com/raw',),
         {'data': {'input': '.timetable {\n'
                            '    font-size: 5rem;\n'
                            '}\n'
                            '\n'
                            '.timetable .title {\n'
                            '    font-size: 10rem;\n'
                            '}\n'}}],
        ['Session put_object', (), {'ACL': 'public-read',
                                    'Body': b'.timetable{font-size:5rem;}.timetable.title{font-size:10rem;}',
                                    'Bucket': 'bucname',
                                    'ContentEncoding': '',
                                    'ContentType': 'text/css; charset=utf-8',
                                    'Key': 'keyprefix/timetable.min.css',
                                    'Metadata': {'checksum': '948b1d03e2eef4a3181a3888e7df9647'}}],
        ['Session get_object', (), {'Bucket': 'bucname', 'Key': 'keyprefix/timetable.css.gz'}],
        ['Session put_object', (), {'ACL': 'public-read',
                                    'Body': Gzipped(b'.timetable {\n    font-size: 5rem;\n}\n\n.timetable .title {\n    font-size: 10rem;\n}\n'),
                                    'Bucket': 'bucname',
                                    'ContentEncoding': 'gzip',
                                    'ContentType': 'text/css; charset=utf-8',
                                    'Key': 'keyprefix/timetable.css.gz',
                                    'Metadata': {'checksum': '948b1d03e2eef4a3181a3888e7df9647'}}],
        ['Session get_object', (), {'Bucket': 'bucname', 'Key': 'keyprefix/timetable.min.css.gz'}],
        ['Session put_object', (), {'ACL': 'public-read',
                                    'Body': Gzipped(b'.timetable{font-size:5rem;}.timetable.title{font-size:10rem;}'),
                                    'Bucket': 'bucname',
                                    'ContentEncoding': 'gzip',
                                    'ContentType': 'text/css; charset=utf-8',
                                    'Key': 'keyprefix/timetable.min.css.gz',
                                    'Metadata': {'checksum': '948b1d03e2eef4a3181a3888e7df9647'}}],
        ['Session get_object', (), {'Bucket': 'bucname', 'Key': 'keyprefix/readme.txt'}],
        ['Session put_object', (), {'ACL': 'public-read',
                                    'Body': b'Just some text.',
                                    'Bucket': 'bucname',
                                    'ContentEncoding': '',
                                    'ContentType': 'text/plain; charset=utf-8',
                                    'Key': 'keyprefix/readme.txt',
                                    'Metadata': {'checksum': '5b6d8c4a28b23f65a878ed43231045bf'}}]]
