import pytest
from pystaticpage import tasks


@pytest.fixture
def dirs():
    return tasks.DirsConfig(site='./dirs/sites',
                            pages='./dirs/pages',
                            templates='./dirs/templates',
                            static='./dirs/static',
                            cdn='./dirs/cdn',
                            data='./dirs/data',
                            sass='./dirs/sass')


@pytest.fixture
def urls():
    return tasks.URLsConfig(home='https://my-home.com',
                            static='/static',
                            cdn='https://cdn.my-home.com')
