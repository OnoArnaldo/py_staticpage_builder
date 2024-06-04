# Static Page Builder

A very simple static site generator which works with markdown files, jinja templates and Andrew Chilton's minifiers.


# Installation

```commandline
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install git+https://github.com/OnoArnaldo/py_staticpage_builder.git
```

## Install SASS

Download the latest version of SASS (this project was tested with the stand alone version) 
([link](https://github.com/sass/dart-sass/releases)).


# Usage

First you will need to build the project structure, I recommend the structure below.

```text
.
├── _sites/             --> the static site will be built here, this folder will be created if not exists.
├── web
│   ├── data/           --> toml files with data that can be used in the templates.
│   ├── pages/          --> html or markdown files to be transformed into static pages.
│   ├── static/         --> all the assets you want to use in the templates, the files will be copied to _sites.
│   ├── sass/           --> all sass and scss files, this will be compiled and saved in _sites/static/css/.
│   ├── sass_modules/   --> all sass modules to be used with import, this will not be compiled.
│   ├── cdn/            --> all files that will be uploaded to the cdn server.
│   └── templates/      --> templates using jinja syntax.
└── build.py            --> script to execute the builder.
```

## Sample for `build.py`

```python
#!.venv/bin/python
from datetime import datetime, UTC
from pathlib import Path
from staticpage import Build

ROOT = Path(__file__).parent

def current_year() -> str:
    return str(datetime.now(UTC).year)

if __name__ == '__main__':
    Build(
        sites_dir=ROOT / 'web' / 'pages',
        data_dir=ROOT / 'web' / 'data',
        templates_dir=ROOT / 'web' / 'templates',
        static_dir=ROOT / 'web' / 'static',
        sass_dir=ROOT / 'web' / 'sass',
        output_dir=ROOT / '_site',
        sass_bin=ROOT / 'libs' / 'sass'
    ).register_globals(
        current_year=current_year
    ).build()
```

## Pages

### Pages with html

> It uses jinja2 to parse the files

The tag `markdown` was created to allow the use of markdown inside the templates.

File `example.html`

```html
{% extends 'base.html' %}

{% block body %}
  {% markdown %}
    variable: value

    # The title
    ## The subtitle
    
    The variable is ${variable}.
  {% endmarkdown %}
{% endblock %}
```

### Pages with markdown

> The markdown content will be placed in `{{ content }}`.

File `base_md.html`.

```html
{% extends 'base.html' %}

{% block body %}
  {{ content }}
{% endblock %}
```

File `sample.md`.

```markdown
extends: base_md.html
title: The Title

# Subject
## Topic 1: ${title}
```
