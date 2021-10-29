# Static Page Builder

A very simple static site generator which works with markdown files, jinja templates and Andrew Chilton's minifiers.

# Installation

```commandline
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install git+https://github.com/OnoArnaldo/py_staticpage_builder.git
```

# Usage

First you will need to build the project structure, I recommend the structure below.

```text
.
├── dirs
│   ├── config.yaml     --> configuration file used to build the site.
│   ├── _sites/         --> the static site will be built here, this folder will be created if not exists.
│   ├── data/           --> yaml files with data that can be used in the templates.
│   ├── pages/          --> html or markdow files to be transformed into static pages.
│   ├── static/         --> all the assets you want to use in the templates, the files will be copied to _sites.
│   ├── sass/           --> all sass and scss files, this will be compiled and saved in _sites/static/css/.
│   ├── cdn/            --> all files that will be uploaded to the cdn server.
│   └── templates/      --> templates using jinja syntax.
└── build.py            --> script to execute the builder.
```

You can find an example in the `tests` folder.

## Configuration File

Below is all the values that can be used in the configuration file.

```yaml
config:
  dirs:     # the folder structure used for your project
    sites: ./dirs/_sites
    pages: ./dirs/pages
    templates: ./dirs/templates
    static: ./dirs/static
    cdn: ./dirs/cdn
    data: ./dirs/data
    sass: ./dirs/sass
  urls:     # url used in your templates, more details below
    home: https://home-page.com
    static: /static
    cdn: https://cdn.home-page.com/root
  builder:  # parameters for the builder
    clean_before_build: true  # delete dirs._sites before building
    pages:
      execute: true
      only_index: false     # if set to TRUE, it will generate index.html for all the pages
                                # (this will remove the trailing .html). Default: false
      skip_for_index:           # list of files that will not be turned into index.html
        - file_name_pattern     # the name is a regex pattern
        - ...
    static:
      execute: true
    minify:
      execute: true
      extensions: ['.html', '.js', '.css']
      skip_files:
        - .*min\.\w+
      skip_dirs:
        - cdn
    sass:
      execute: true
      output_style: nested      # check the link for the option https://sass.github.io/libsass-python/sass.html?highlight=sass%20syntax#sass.compile
                                # Default: nested
      destination: static       # choose the destination, it can be either `cdn` or `static`. Default: static
    gzip:
      execute: true
      extensions: [.css, .js]   # choose the extensions that will be compressed. Default: []
      skip_files:
        - main.js
    cdn:                      # configuration to integrate with the CDN
      execute: true
      service_name: servname
      region_name: regname
      bucket_name: bucname
      object_key_prefix: keyprefix      # in case the files will be inside a folder in CDN
      endpoint: "https://the-url.com"
      aws_access_key: the_key
      aws_secret_access_key: the_secret
```

## Templates and pages

The templates work exactly the way is in jinja [documentation](https://jinja2docs.readthedocs.io/en/stable/).

Pages can be a html (using jinja syntax) or a markdown file (see this [document](https://daringfireball.net/projects/markdown/syntax) for the syntax).

#### Example of html page

`templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{%block title%}TheTile{% endblock %}</title>
</head>
<body>
{% block body %}{% endblock %}
</body>
</html>
```

`pages/index.html`
```html
{% extends 'base.html' %}

{% block title %}This is HOME{% endblock %}

{% block body %}
  <h1>This is the home page</h1>
{% endblock %}
```

> Note that we are simply using jinja syntax.


#### Example of markdown page

`templates/blog_template.html`
```html
{% extends 'base.html' %}

{% block title %}Blog - {{ title }}{% endblock %}

{% block body %}
  <h1>blog - {{ title }}</h1>
  <pre>{{ content|safe }}</pre>
{% endblock %}
```

> markdown content will replace the variable `content`.

> `content` needs to use the filter `safe` to parse properly.

`pages/blog/20200101.md`
```markdown
template: blog_template.html
title: First thoughts

# This is the header {: .title #main-title}

* item 1
* item 2
* item 3
```

> note that the header contains key-value pairs will be sent to the template.

> template key is mandatory.

> html attribute can be added using {: .class_attribute #id_attribute}.

## Data files

`data/company.yml`
```yaml
name: Company ABC
contacts:
    - type: email
      value: contact@email.com
    - type: phone
      value: 1234 5678
address:
    delivery:
        street: ABC Street
        number: 1000
        country: ABCD
```

`pages/about.html`
```html
{% extends 'base.html' %}
{{ set company = data('company') }}

{% block title %}About - {{ company.name }}{% endblock %}

{% block body %}
  {% for contact in company.contacts %}
    <p>{{ contact.type }}: {{ contact.value }}</p>
  {% endfor %}
{% endblock %}
```

Or something like:
```html
    ...
    {{ set address = data('company', 'address/delivery') }}

    <p>{{ address.street }}</p>
    <p>{{ address.number }}</p>
    <p>{{ address.country }}</p>
    ...
```

## Functions

There few functions that can be used in the templates.

* url_home(): get the value in the configuration file.
* url_static(): get the value in the configuration file.
* current_year(): get current year (useful for copyright).

Example:

```html
...
<h1>{{ url_home() }}</h1>

<div class="somewhere-in-footer">
  <p class="subtitle">&copy; {{ current_year() }} My company. All right reserved.</p>
</div>

<img src="{{ url_static() }}/image.jpg">
...
```

> The idea is to implement a way to add functions.

## build.py file

You will have to create a script to execute the builder.

The script below should do the trick.

```python
from pystaticpage import load_config, create_builder


def main():
    config = load_config('./dirs/config.yaml')
    builder = create_builder(config)
    builder.run()


if __name__ == '__main__':
    main()
```

You can override the parameters which were set in the config file as below.

```python
builder.run(clean=True, build_pages=True,
            build_static=True, build_sass=True, sass_output_style='nested',
            minify_extensions=['.css', '.js'], only_index_page=True, skip_for_index=[])
```

Then just execute the script to build the static site.

```commandline
venv/bin/python build.py
```

### build.py file with injected functions to be used in templates

You can inject functions to be used in the templates as below.

```python
from pystaticpage import load_config, create_builder
import datetime


def utc_now():
    return datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')


def main():
    config = load_config('./dirs/config.yaml', template_methods={'utc_now': utc_now})
    builder = create_builder(config)
    builder.run()


if __name__ == '__main__':
    main()
```

In the template, you can call the method as below.

```html
<p>{{ utc_now() }}</p>
```

# Development

## Installation

```commandline
pip install -e .
```

## Run Test

```commandline
pip install '.[test]'
pytest
```
