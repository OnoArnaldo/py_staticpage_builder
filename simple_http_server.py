import http.server
import socketserver
import os

PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith('/static') and os.path.exists('.' + self.path + '.html'):
            self.path += '.html'
        return super(Handler, self).do_GET()


with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    print("serving at port", PORT)
    os.chdir('web/_sites')
    httpd.serve_forever()
