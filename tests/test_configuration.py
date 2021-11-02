import os
import pytest
from pystaticpage import config


def test_config():
    cfg = config.Config.from_dict({
        'environment': 'prod',
        'dirs': {
            'sites': './dirs/sites',
            'pages': './dirs/pages',
            'templates': './dirs/templates',
            'static': './dirs/static',
            'cdn': './dirs/cdn',
            'data': './dirs/data',
            'sass': './dirs/sass',
        },
        'urls': {
            'home': 'https://my-site.com',
            'static': '/static',
            'cdn': 'https://cdn.my-site.com/assets',
        },
        'builder': {
            'clean_before_build': True,
            'pages': {
                'execute': True,
                'only_index': True,
                'skip_for_index': [
                    'help.html',
                ],
            },
            'static': {
                'execute': True,
            },
            'minify': {
                'execute': True,
                'extensions': ['.css', '.js'],
                'skip_files': [r'.*min\.\w+'],
            },
            'sass': {
                'execute': True,
                'output_style': 'nested',
                'destination': 'static',
            },
            'gzip': {
                'execute': True,
                'extensions': ['.css', '.js'],
                'skip_files': ['main.js'],
            },
            'cdn': {
                'execute': True,
                'service_name': "servname",
                'region_name': "regname",
                'bucket_name': "bucname",
                'object_key_prefix': "keyprefix",
                'endpoint': "https://the-url.com",
                'aws_access_key': "the_key",
                'aws_secret_access_key': "the_secret",
            },
        },
    })

    assert cfg.environment == 'prod'

    assert cfg.dirs.sites == './dirs/sites'
    assert cfg.dirs.pages == './dirs/pages'
    assert cfg.dirs.templates == './dirs/templates'
    assert cfg.dirs.static == './dirs/static'
    assert cfg.dirs.cdn == './dirs/cdn'
    assert cfg.dirs.data == './dirs/data'
    assert cfg.dirs.sass == './dirs/sass'

    assert cfg.urls.home == 'https://my-site.com'
    assert cfg.urls.static == '/static'
    assert cfg.urls.cdn == 'https://cdn.my-site.com/assets'

    assert cfg.builder.clean_before_build
    assert cfg.builder.pages.execute
    assert cfg.builder.pages.only_index
    assert cfg.builder.pages.skip_for_index == ['help.html']

    assert cfg.builder.static.execute

    assert cfg.builder.minify.execute
    assert cfg.builder.minify.extensions == ['.css', '.js']
    assert cfg.builder.minify.skip_files == [r'.*min\.\w+']

    assert cfg.builder.sass.execute
    assert cfg.builder.sass.output_style == 'nested'
    assert cfg.builder.sass.destination == 'static'

    assert cfg.builder.gzip.execute
    assert cfg.builder.gzip.extensions == ['.css', '.js']
    assert cfg.builder.gzip.skip_files == ['main.js']

    assert cfg.builder.cdn.execute
    assert cfg.builder.cdn.service_name == 'servname'
    assert cfg.builder.cdn.region_name == 'regname'
    assert cfg.builder.cdn.bucket_name == 'bucname'
    assert cfg.builder.cdn.object_key_prefix == 'keyprefix'
    assert cfg.builder.cdn.endpoint == 'https://the-url.com'
    assert cfg.builder.cdn.aws_access_key == 'the_key'
    assert cfg.builder.cdn.aws_secret_access_key == 'the_secret'


def assert_config(cfg):
    with pytest.raises(config.MissingConfigKey) as ex:
        cfg = config.Config.from_dict(cfg)


def test_config_mandatory():
    assert_config({})

    assert_config({'dirs': {'sites': './sites'}})
    assert_config({'dirs': {'sites': './sites', 'pages': '/pages'}})
    assert_config({'dirs': {
        'sites': './sites', 'pages': '/pages', 'templates': '/templates'}
    })
    assert_config({'dirs': {
        'sites': './sites', 'pages': '/pages', 'templates': '/templates',
        'static': '/static'
    }})
    assert_config({'dirs': {
        'sites': './sites', 'pages': '/pages', 'templates': '/templates',
        'static': '/static', 'cdn': '/cdn'
    }})
    assert_config({'dirs': {
        'sites': './sites', 'pages': '/pages', 'templates': '/templates',
        'static': '/static', 'cdn': '/cdn', 'data': '/data'
    }})
    assert_config({'dirs': {
        'sites': './sites', 'pages': '/pages', 'templates': '/templates',
        'static': '/static', 'cdn': '/cdn', 'data': '/data', 'sass': '/sass'
    }})

    assert_config({
        'dirs': {
            'sites': './sites', 'pages': '/pages', 'templates': '/templates',
            'static': '/static', 'cdn': '/cdn', 'data': '/data', 'sass': '/sass'
        },
        'urls': {
            'home': '/'
        }
    })
    assert_config({
        'dirs': {
            'sites': './sites', 'pages': '/pages', 'templates': '/templates',
            'static': '/static', 'cdn': '/cdn', 'data': '/data', 'sass': '/sass'
        },
        'urls': {
            'home': '/', 'static': '/static'
        }
    })


def test_default():
    cfg = config.Config.from_dict({
        'dirs': {
            'sites': '/sites', 'pages': '/pages', 'templates': '/templates',
            'static': '/static', 'cdn': '/cdn', 'data': '/data', 'sass': '/sass'
        },
        'urls': {
            'home': '/', 'static': '/static', 'cdn': '/cdn'
        }
    })

    assert cfg.environment == 'prod'

    assert not cfg.builder.pages.execute
    assert not cfg.builder.clean_before_build
    assert cfg.builder.pages.only_index
    assert cfg.builder.pages.skip_for_index == []

    assert not cfg.builder.static.execute

    assert not cfg.builder.minify.execute
    assert cfg.builder.minify.extensions == []
    assert cfg.builder.minify.skip_files == []

    assert not cfg.builder.sass.execute
    assert cfg.builder.sass.output_style == 'nested'
    assert cfg.builder.sass.destination == 'static'

    assert not cfg.builder.gzip.execute
    assert cfg.builder.gzip.extensions == []
    assert cfg.builder.gzip.skip_files == []

    assert not cfg.builder.cdn.execute
    assert cfg.builder.cdn.service_name == ''
    assert cfg.builder.cdn.region_name == ''
    assert cfg.builder.cdn.bucket_name == ''
    assert cfg.builder.cdn.object_key_prefix == ''
    assert cfg.builder.cdn.endpoint == ''
    assert cfg.builder.cdn.aws_access_key == ''
    assert cfg.builder.cdn.aws_secret_access_key == ''


def test_config_from_yaml():
    cfg = config.Config.from_yaml(
        'config:\n'
        '  environment: prod\n'
        '  dirs:\n'
        '    sites: ./dirs/sites\n'
        '    pages: ./dirs/pages\n'
        '    templates: ./dirs/templates\n'
        '    static: ./dirs/static\n'
        '    cdn: ./dirs/cdn\n'
        '    data: ./dirs/data\n'
        '    sass: ./dirs/sass\n'
        '  urls:\n'
        '    home: https://my-site.com\n'
        '    static: /static\n'
        '    cdn: https://cdn.my-site.com/assets\n'
        '  builder:\n'
        '    clean_before_build: True\n'
        '    pages:\n'
        '      execute: True\n'
        '      only_index: True\n'
        '      skip_for_index:\n'
        '        - help.html\n'
        '    static:\n'
        '      execute: True\n'
        '    minify:\n'
        '      execute: True\n'
        '      extensions: [.css, .js]\n'
        '      skip_files:\n'
        r'        - .*min\.\w+' '\n'
        '    sass:\n'
        '      execute: True\n'
        '      output_style: nested\n'
        '      destination: static\n'
        '    gzip:\n'
        '      execute: True\n'
        '      extensions: [.css, .js]\n'
        '      skip_files:\n'
        '        - main.js\n'
        '    cdn:\n'
        '      execute: True\n'
        '      service_name: servname\n'
        '      region_name: regname\n'
        '      bucket_name: bucname\n'
        '      object_key_prefix: keyprefix\n'
        '      endpoint: https://the-url.com\n'
        '      aws_access_key: the_key\n'
        '      aws_secret_access_key: the_secret'
    )

    assert cfg.environment == 'prod'

    assert cfg.dirs.sites == './dirs/sites'
    assert cfg.dirs.pages == './dirs/pages'
    assert cfg.dirs.templates == './dirs/templates'
    assert cfg.dirs.static == './dirs/static'
    assert cfg.dirs.cdn == './dirs/cdn'
    assert cfg.dirs.data == './dirs/data'
    assert cfg.dirs.sass == './dirs/sass'

    assert cfg.urls.home == 'https://my-site.com'
    assert cfg.urls.static == '/static'
    assert cfg.urls.cdn == 'https://cdn.my-site.com/assets'

    assert cfg.builder.clean_before_build
    assert cfg.builder.pages.execute
    assert cfg.builder.pages.only_index
    assert cfg.builder.pages.skip_for_index == ['help.html']

    assert cfg.builder.static.execute

    assert cfg.builder.minify.execute
    assert cfg.builder.minify.extensions == ['.css', '.js']
    assert cfg.builder.minify.skip_files == [r'.*min\.\w+']

    assert cfg.builder.sass.execute
    assert cfg.builder.sass.output_style == 'nested'
    assert cfg.builder.sass.destination == 'static'

    assert cfg.builder.gzip.execute
    assert cfg.builder.gzip.extensions == ['.css', '.js']
    assert cfg.builder.gzip.skip_files == ['main.js']

    assert cfg.builder.cdn.execute
    assert cfg.builder.cdn.service_name == 'servname'
    assert cfg.builder.cdn.region_name == 'regname'
    assert cfg.builder.cdn.bucket_name == 'bucname'
    assert cfg.builder.cdn.object_key_prefix == 'keyprefix'
    assert cfg.builder.cdn.endpoint == 'https://the-url.com'
    assert cfg.builder.cdn.aws_access_key == 'the_key'
    assert cfg.builder.cdn.aws_secret_access_key == 'the_secret'


def test_config_from_env():
    os.environ['STATIC_ACCESS_KEY'] = 'access_key'
    os.environ['STATIC_SECRET_KEY'] = 'secret_key'

    cfg = config.Config.from_yaml(
        'config:\n'
        '  environment: prod\n'
        '  dirs:\n'
        '    sites: ./dirs/sites\n'
        '    pages: ./dirs/pages\n'
        '    templates: ./dirs/templates\n'
        '    static: ./dirs/static\n'
        '    cdn: ./dirs/cdn\n'
        '    data: ./dirs/data\n'
        '    sass: ./dirs/sass\n'
        '  urls:\n'
        '    home: https://my-site.com\n'
        '    static: /static\n'
        '    cdn: https://cdn.my-site.com/assets\n'
        '  builder:\n'
        '    clean_before_build: True\n'
        '    cdn:\n'
        '      execute: True\n'
        '      service_name: servname\n'
        '      region_name: regname\n'
        '      bucket_name: bucname\n'
        '      object_key_prefix: keyprefix\n'
        '      endpoint: https://the-url.com\n'
        '      aws_access_key: "$ENV:STATIC_ACCESS_KEY"\n'
        '      aws_secret_access_key: "$ENV:STATIC_SECRET_KEY"'
    )

    assert cfg.builder.cdn.execute
    assert cfg.builder.cdn.service_name == 'servname'
    assert cfg.builder.cdn.region_name == 'regname'
    assert cfg.builder.cdn.bucket_name == 'bucname'
    assert cfg.builder.cdn.object_key_prefix == 'keyprefix'
    assert cfg.builder.cdn.endpoint == 'https://the-url.com'
    assert cfg.builder.cdn.aws_access_key == 'access_key'
    assert cfg.builder.cdn.aws_secret_access_key == 'secret_key'
