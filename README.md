# Static page builder

Simple solution to build static pages using Jinja2, Markdown and YAML.

## How to install

Install the requirements, with venv (recommended)
```terminal
python -m venv venv
source venv/bin/active

pip install -r requirements.txt
```

## Directory structure

```text
+ web
  + _sites -> the static pages will be generated in this folder.
  + data -> yaml files with data that can be used in templates.
  + pages -> all .md and .html files in this folder will be transformed in static pages.
  + static -> asset files (.css, .js, .png, ...) for the website (this will be copied to _sites).
  + templates -> jinja templates directory
```

## How to build templates

Templates are build with Jinja (check documentation [here](https://pypi.org/project/Jinja2/)).

Besides, two functions have been added to help in templates.

#### current_year()
This method returns the current year, the idea is to use with copyrights text.
```html
<div class="somewhere-in-footer">
  <p class="subtitle">&copy; {{ current_year() }} My company. All right reserved.</p>
</div>
```

#### data(collection, key)
This method parse the data in folder `data` to be used in templates

example 1:
```yaml
# data/companyinfo.yaml
name: My company
email: contact@mycompany.com
phone: 123.456.789
```
```html
<div class="somewhere">
  {% set company = data('companyinfo') %}
  <div class="name">{{ company.name }}</div>
  <div class="email">{{ company.email }}</div>
  <div class="phone">{{ company.phone }}</div>
</div>
```

> Note that the collection argument is the file name without the extension.


example 2:
```yaml
# data/home.yaml
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
```html
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
```

> Note that the key can be the combination of keys joined with '/'.

# How to build pages

It is possible to build pages with plain HTML, Jinja or markdown files.

Example with HTML
```html
<!-- pages/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My Site</title>
  <link rel="stylesheet" href="/static/css/mysite.css">
</head>
<body>
<div class="container is-fluid">
  The content
</div>

<script src="/static/js/mysite.js"></script>
</body>
</html>
```

Example with Jinja
```html
<!-- pages/index.html -->
{% extends 'base.html' %}
{% import 'macros.html' as macros %}

{% block title %}My company{% endblock %}

{% block body %}
  {% include 'includes/home.html' %}

  <section class="section" id="services">
    <div class="container has-text-centered">
      {% for columns in data('services') %}
        <div class="columns">
          {% for column in columns %}
            {{ macros.service_column(
              column.title,
              column.subtitle,
              column.description,
              column.url,
              column.icon
              )
            }}
          {% endfor %}
        </div>
      {% endfor %}
    </div>
  </section>

  {% include 'includes/contact.html' %}
{% endblock %}
```

Example with markdown
```markdown
# pages/service/service1.md
---
template: service_details.html
title: Service 1
subtitle: The subtitle
---
Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in 
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla 
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
culpa qui officia deserunt mollit anim id est laborum.

<br>
[Book](){: .button }
```

> The header session (between 3 dashes, '---') is parsed as dictionary and sent to the template as argument.

> `template` key is mandatory in the header section.

> The extension enabled are 'meta', 'attr_list', 'tables' (more info [here](https://python-markdown.github.io/extensions/)).
> You can modify the code to add/remove the extensions


```html
<!-- template/service_details.html -->
{% extends 'base.html' %}

{% block body %}
<section class="section">
  <div class="container">
    <div class="columns is-desktop">
      <div class="column is-7-desktop">
        <h2 class="title">{{ title }}</h2>
        <p class="subtitle">{{ subtitle }}</p>
        <hr>
        <div class="md-content">
          <!--the use of filter 'safe' allows to use tags in md files-->
          {{ content|safe }}
        </div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

> All the content in md file is in `content` variable, 
> I recommend to use `safe` filter to give more options while creating the pages 

# How to run

The basic commands are:
```terminal
python main.py -build
python main.py -build-compressed
python mail.py -watch
```

> -watch will keep the builder running and it will regenerate
> '_site' when a file is changed.

Execute the command below to see all the option.
```terminal
python main.py -help
```

# How to check results

Run the command below and open the url `http://localhost:8000` in your browser.
```terminal
python simple_http_server.py
```

> Note that simple_http_server is a lazy development
> and there is a lot of room for improvement
