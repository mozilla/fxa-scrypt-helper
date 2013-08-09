from wsgiref.simple_server import make_server
from scrypt_helper import make_wsgi_app

if __name__ == '__main__':
    app = make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
