from pyramid.config import Configurator
from pyramid.response import Response
import binascii, json

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
    try:
        body = json.loads(request.POST)
        hexlified_password = bytes(body.get('input', ''))
        password = binascii.unhexlify(hexlified_password)
        if len(password) < 1 or len(password) > 256:
            msg = 'Password "%s" must be between 1 and 256 bytes'
            raise ValueError(msg % password)
        del body['input']
        parameters = validate_parameters(body)
    except ValueError, e:
        response = Response(str(e))
        response.status = 400
        return response
    else:
        key = scrypt.hash(password, **parameters)
        output = binascii.hexlify(key)
        return Response(json.dumps({'output': output}))


def do_healthcheck(request):
    """A simple healthcheck route.  Just returns 'OK'."""
    return Response("OK")


def make_wsgi_app():
    config = Configurator()
    config.add_route('do_scrypt', '/', request_method='POST')
    config.add_route('do_healthcheck', '/', request_method='GET')
    config.add_view(do_scrypt, route_name='do_scrypt')
    config.add_view(do_healthcheck, route_name='do_healthcheck')
    return config.make_wsgi_app()
