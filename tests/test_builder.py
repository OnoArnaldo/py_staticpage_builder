import os
import shutil
import pytest
from pystaticpage.builder import create_builder, Builder


def delete_sites():
    if os.path.exists('./dirs/_sites'):
        shutil.rmtree('./dirs/_sites')


def text_from(file_name):
    with open(file_name) as f:
        text = f.read()
    f.close()
    return text


@pytest.fixture
def builder(config):
    bld = create_builder(config)
    assert isinstance(bld, Builder)

    delete_sites()
    yield bld
    delete_sites()


def test_build(builder):
    builder.run()

    assert text_from('./expected_site/index.html') == text_from('./dirs/_sites/index.html')
    assert text_from('./expected_site/blog/20200126.html') == text_from('./dirs/_sites/blog/20200126.html')
    assert text_from('./expected_site/blog/20200125.html') == text_from('./dirs/_sites/blog/20200125.html')

    assert os.path.exists('./dirs/_sites/static/js/index.js')
    assert os.path.exists('./dirs/_sites/static/css/index.css')

    assert os.path.exists('./dirs/_sites/static/js/index.min.js')
    assert os.path.exists('./dirs/_sites/static/css/index.min.css')
