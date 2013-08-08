# Scrypt Helper Service

A hello-world level implementation of a web service that implements the [scrypt key derivation function] [scrypt] .

[scrypt]: http://en.wikipedia.org/wiki/Scrypt

## Installation

You'll need to grab the Python scrypt library version 0.6.1 or better from [PyPI] [pypi] . You'll also need the [Pyramid framework] [pyramid]

[pypi]: https://pypi.python.org/pypi/scrypt/0.6.1
[pyramid]: https://pypi.python.org/pypi/pyramid

## Running

    $ cd scrypt-helper
    $ python server.py


Then make an http POST with a JSON body of the form:

    '{
     "password": <your password to scrypt>,
     "salt": "identity.mozilla.com/picl/v1/scrypt",
     "N": 65536,
     "r": 8,
     "p": 1,
     "buflen": 32
    }'

to:

    - http://localhost:8080

which will return:

    {"output": "return-value-from-scrypt-algorithm"}

(Note that all of the inputs to scrypt except the password are hard-coded; you must modify validate_parameters in server.py if you wish to change any of them.)

## TODO
Write setup.py to handle scrypt and Pyramid installation.