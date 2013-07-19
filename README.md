# PiCL Scrypt Helper Service

A hello-world level implementation of a web service that implements the [scrypt key derivation function] [scrypt] .

[scrypt]: http://en.wikipedia.org/wiki/Scrypt

## Installation

You'll need to grab the Python scrypt library version 0.6.1 or better from [PyPI] [pypi] . You'll also need the [Pyramid framework] [pyramid]

[pypi]: https://pypi.python.org/pypi/scrypt/0.6.1
[pyramid]: https://pypi.python.org/pypi/pyramid

## Running

    $ cd picl-spec-crypto
    $ python server.py
    

Then pick an input string and browse to http://localhost:8080/your-input-string . The resulting web page should consist of illegible but correct output from scrypt run with:

    * salt = 'salt'
    * N = 64*1024
    * r=8
    * p=1
    * buflen = 32

## TODO
Everything. Initially, determine whether the input should be moved out of the URL. Parameterize the salt. Write setup.py to handle scrypt and Pyramid installation.