from six.moves import urllib
import http.client
from wsgiref.headers import Headers


class Request:
    def __init__(self, environ):
        self.environ = environ

    @property
    def path(self):
        return self.environ['PATH_INFO']

    @property
    def args(self):
        return self.encode_to_dict(self.environ['QUERY_STRING'])

    def encode_to_dict(self, encoded_str):
        pair_list = encoded_str.split('&')
        d = {}
        for pair in pair_list:
            if pair:
                key = pair.split('=')[0]
                val = pair.split('=')[1]
                d[key] = val
        return d


class Response:
    def __init__(self, response=None, status=200, charset='utf-8',
                 content_type='text/html'):
        self.response = [] if response is None else response
        self.charset = charset
        self.headers = Headers()
        content_type = f'{content_type}; charset={charset}'
        self.headers.add_header('content_type', content_type)
        self._status = status

    @property
    def status(self):
        status_string = http.client.responses.get(self._status, 'UNKNOWN')
        return f'{self._status} {status_string}'

    def __iter__(self):
        for val in self.response:
            if isinstance(val, bytes):
                yield val
            else:
                yield val.encode(self.charset)


def request_response_application(func):
    def application(environ, start_response):
        request = Request(environ)
        response = func(request)
        start_response(
            response.status,
            response.headers.items()
        )
        return iter(response)
    return application

@request_response_application
def application(request):
    name = request.args.get('name', 'default')
    return Response([f'hello {name}'])

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('127.0.0.1', 8000, application)
    httpd.serve_forever()