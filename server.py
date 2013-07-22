from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

import scrypt

def do_scrypt(request):
    stretched_input = bytes(request.matchdict.get('stretched_input', ''))
    salt = b"identity.mozilla.com/picl/v1/scrypt"
    key = scrypt.hash(stretched_input, salt, N=64*1024, r=8, p=1,
                      buflen=1*32)
    return Response(key)


if __name__ == '__main__':
    config = Configurator()
    config.add_route('do_scrypt', '/{stretched_input}')
    config.add_view(do_scrypt, route_name='do_scrypt')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
