from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='py_staticpage_builder',
    version='10.0.0.3',
    description='Static page generator.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/OnoArnaldo/py_staticpage_builder',
    author='Arnaldo Ono',
    author_email='programmer@onoarnaldo.com',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='~=3.10',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
    ],
    install_requires=['markdown', 'PyYAML', 'Jinja2', 'requests', 'libsass', 'boto3'],
    extras_require={
        'test': ['pytest', 'coverage'],
    },
)
