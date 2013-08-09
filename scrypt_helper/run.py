from wsgiref.simple_server import make_server
from scrypt_helper import make_wsgi_app

application = make_wsgi_app()

if __name__ == '__main__':
    server = make_server('0.0.0.0', 8080, application)
    server.serve_forever()
