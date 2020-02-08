import unittest
from tests import helpers
from page_builder import config, builder


CONFIG = '''\
config:
  dirs:
    sites: ./builder_dirs/sites
    templates: ./builder_dirs/templates
    static: ./builder_dirs/static
    pages: ./builder_dirs/pages
  urls:
    home: https://my-page.com
    static: /static
'''

RESULT_INDEX = '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>This is the test</title>
</head>
<body>

<h1>This is the home page</h1>

</body>
</html>'''


class TestBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.old_config = helpers.CONFIG
        helpers.CONFIG = CONFIG
        config.open = helpers.TestFile

        cfg = config.loads('calling_mock')
        self.builder = builder.Builder(cfg)

    def tearDown(self) -> None:
        self.builder.clear_sites()
        helpers.CONFIG = self.old_config

    def test_render(self):
        html = self.builder.render_html('index.html', the_title='This is the test')
        self.assertEqual(RESULT_INDEX, html)

    def test_build(self):
        self.builder.run()
        self.assertEqual(self.expected_index(), self.get_html('./builder_dirs/sites/index.html'))
        self.assertEqual(self.expected_blog_20200125(), self.get_html('./builder_dirs/sites/blog/20200125.html'))
        self.assertEqual(self.expected_blog_20200126(), self.get_html('./builder_dirs/sites/blog/20200126.html'))

        self.assertEqual(self.expected_style(), self.get_html('./builder_dirs/sites/static/css/index.css'))
        self.assertEqual(self.expected_script(), self.get_html('./builder_dirs/sites/static/js/index.js'))

    def expected_index(self):
        return '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title></title>
</head>
<body>

<h1>This is the home page</h1>

</body>
</html>'''

    def expected_blog_20200125(self):
        return '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Blog - First thoughts</title>
</head>
<body>

  <h1>blog - First thoughts</h1>
  <pre><h1 class="title" id="main-title">This is the header</h1>
<ul>
<li>item 1</li>
<li>item 2</li>
<li>item 3</li>
</ul></pre>

</body>
</html>'''

    def expected_blog_20200126(self):
        return '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Blog - </title>
</head>
<body>

  <h1>blog - </h1>
  <pre>
  <h1>About something</h1>
  <p>this is a paragraph.</p>
  </pre>

</body>
</html>'''

    def expected_style(self):
        return '''\
body {
    background-color: black;
}'''

    def expected_script(self):
        return '''\
(function () {
    console.info("INFO");
})();'''

    def get_html(self, fname):
        with open(fname) as f:
            html = f.read()
        f.close()
        return html
