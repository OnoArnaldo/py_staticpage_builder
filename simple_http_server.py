import http.server
import socketserver
import os

from page_builder import loads_config

PORT = 8000
CONFIG = './config.yaml'


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith('/static') and os.path.exists('.' + self.path + '.html'):
            self.path += '.html'
        return super(Handler, self).do_GET()


with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    print("serving at port", PORT)
    config = loads_config(CONFIG)
    os.chdir(config.dirs.sites)
    httpd.serve_forever()
