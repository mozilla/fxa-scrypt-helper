from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

import scrypt

REQUIRED_PARAMETERS = {
    'salt': b'identity.mozilla.com/picl/v1/scrypt',
    'N': 65536, # aka 'n'
    'r': 8,
    'p': 1,
    'buflen': 32}


def validate_parameters(input_dict):
    '''
    Enforce restrictions on the scrypt parameters.
    '''
    for parameter in REQUIRED_PARAMETERS:
        typecaster = bytes if parameter == 'salt' else int
        input = input_dict.get(parameter)
        if input is None:
            if parameter == 'N':
                input = input_dict.get('n')
            if input is None:
                return (False, 'Missing Scrypt parameter "%s"' % parameter)
        try:
            assert typecaster(input) == REQUIRED_PARAMETERS[parameter]
        except Exception:
            msg = 'Bad value "%s" for Scrypt parameter "%s"'
            return (False, msg % (input, parameter))
    return (True, REQUIRED_PARAMETERS)
    

def do_scrypt(request):
    stretched_input = bytes(request.matchdict.get('stretched_input', ''))
    valid, parameters = validate_parameters(request.params)
    if not valid:
        response = Response(parameters) # an error message
        response.status = 400
        return response
    key = scrypt.hash(stretched_input, **parameters)
    return Response(key)


if __name__ == '__main__':
    config = Configurator()
    config.add_route('do_scrypt', '/{stretched_input}')
    config.add_view(do_scrypt, route_name='do_scrypt')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
