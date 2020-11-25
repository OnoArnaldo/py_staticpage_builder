# Static Page Builder

A very simple static site generator which works with markdown files and jinja templates.

## Installation

```commandline
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install git+https://github.com/OnoArnaldo/py_staticpage_builder.git
```

## Basic usage

First you will need to build the project structure, I recommend the structure below.

```text
.
├── dirs
│   ├── config.yaml
│   ├── _sites/
│   ├── data/
│   ├── pages/
│   ├── static/
│   └── templates/
└── build.py
```

#### The config.yaml file

This file is used to build the static page. Check the sample below with all the options.

```yaml
config:
  dirs:
    _sites: ./dirs/_sites
    pages: ./dirs/pages
    templates: ./dirs/templates
    static: ./dirs/static
    data: ./dirs/data
  urls:
    home: https://home-page.com
    static: /static
```

#### The templates folder

Put all the templates files you will use to build the sites.

The template files uses jinja syntax, so go to their [documents](https://jinja2docs.readthedocs.io/en/stable/) for more details.

#### The static folder

Put all your images, scripts and style files here, these files will be copied to the `_site` folder.

#### The data folder

Put all your data that will be used in the html files. The files has to be a yaml file.

Below is an example.

**Example 1**

`dirs/data/company.yaml`
```yaml
name: Company ABC
address: ABC Street
contacts:
  email: contact@email.com
  phone: +123 456789012
addresses:
  - delivery: address 001
    invoice: address 002
```

`dirs/pages/some_page.html`
```html
{% set company = data('company') %}

<h1>{{ company.name }}</h1>
<h2>{{ company.contacts.email }}</h2>

{% for address in company.addresses %}
    <p>{{ address.invoice }}</p>
{% endfor %}
```

**Example 2**

`dirs/data/home.yaml`
```yaml
data:
  team:
    - name: John
      email: john@email.com
    - name: Anna
      email: anna@email.com
  products:
    - title: Item 1
      price: 100.00
    - title: Item 2
      price: 200.00
otherInfo:
  - other list
```

`dirs/pages/about.html`
```html
...
<section class="team">
  <div class="member">
  {% for member in data('home', 'data/team') %}
    <div>{{ member.name }} - {{ member.email }}</div>  
  {% endfor %}
  </div>
</section>

<section class="products">
  <div class="product">
  {% for product in data('home', 'data/products') %}
    <div>{{ product.title }} - {{ product.price}} </div>
  {% endfor %}
  </div>
</section>
...
```

#### The pages folder

For every file in this folder, a rendered html file will be created in `_site` folder.

Pages can be a html file, using jinja syntax.

`dirs/templates/base.html`
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

`dirs/pages/index.html`
```html
{% extends 'base.html' %}

{%block title%}Index title{% endblock %}

{% block body %}
<h1>The index</h1>
{% endblock %}
```

Or it can be a markdown page.

`dirs/templates/blog_base.html`
```html
{% extends 'base.html' %}

{% block title %}Blog - {{ title }}{% endblock %}

{% block body %}
  <h1>blog - {{ title }}</h1>
  <pre>{{ content|safe }}</pre>
{% endblock %}
```

`dirs/pages/blog/20201201.md`
```markdown
template: blog_base.html
title: First thoughts

# This is the header {: .title #main-title}

* item 1
* item 2
* item 3
```

#### The build.py file

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

Then just execute the script.
```commandline
python build.py
```

## Install for development

```commandline
pip install -e .
```

## Run Test

```commandline
pip install '.[test]'
pytest
```
