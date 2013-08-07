from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

import scrypt

REQUIRED_PARAMETERS = {
    'salt': b'identity.mozilla.com/picl/v1/scrypt',
    'N': 65536,
    'r': 8,
    'p': 1,
    'buflen': 1*32}


def validate_parameters(input_dict):
    '''
    Enforce restrictions on the scrypt parameters.

    Note that we intentionally insist that exactly one set of parameters
    be passed in. This choice allows us a flexible API, with an initially
    inflexible policy that can be loosened in the future.
    '''
    for parameter in REQUIRED_PARAMETERS:
        typecaster = bytes if parameter == 'salt' else int
        if parameter not in input_dict:
            raise ValueError("Missing scrypt parameter '%s'" % parameter)
        value = typecaster(input_dict[parameter])
        if value != REQUIRED_PARAMETERS[parameter]:
            raise ValueError("Parameter %s must be %s, not '%s'" % (
                parameter, REQUIRED_PARAMETERS[parameter],
                input_dict[parameter]))
    return REQUIRED_PARAMETERS


def do_scrypt(request):
    stretched_input = bytes(request.matchdict.get('stretched_input', ''))
    try:
        parameters = validate_parameters(request.params)
    except ValueError, e:
        response = Response(str(e))
        response.status = 400
        return response
    else:
        key = scrypt.hash(stretched_input, **parameters)
        return Response(key)


if __name__ == '__main__':
    config = Configurator()
    config.add_route('do_scrypt', '/{stretched_input}')
    config.add_view(do_scrypt, route_name='do_scrypt')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
