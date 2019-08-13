import re
from request_response import Response, Request


class NotFound(Exception):
    pass


class Router:
    def __init__(self):
        self.routing = []

    def add_route(self, pattern, callback):
        self.routing.append((pattern, callback))

    def match(self, path):
        for (pattern, callback) in self.routing:
            m = re.match(pattern, path)
            if m:
                return (callback, m.groups())
        raise NotFound()

    def __call__(self, patterns):
        def _(func):
            self.routing.append((patterns, func))
        return _

routers = Router()

@routers(r'/hello/(.*)$')
def hello(request, name):
    return Response(f'hello {name}')

#routers.add_route(r'/hello/(.*)/$', hello)


class Application:
    def __init__(self, routers, **kwargs):
        self.routers = routers

    def __call__(self, environ, start_response):
        try:
            request = Request(environ)
            callback, args = routers.match(request.path)
            response = callback(request, *args)
        except NotFound:
            response = Response(f'<h1>Not found</h1>', status=404)
        start_response(response.status, response.headers.items())
        return iter(response)

app = Application(routers)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()