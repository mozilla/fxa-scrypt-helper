# Scrypt Helper Service

A hello-world level implementation of a web service that implements the [scrypt key derivation function] [scrypt] .

[scrypt]: http://en.wikipedia.org/wiki/Scrypt

## Installation

You'll need to grab the Python scrypt library version 0.6.1 or better from [PyPI] [pypi] . You'll also need the [Pyramid framework] [pyramid].  For simple setups you can likely get away with the usual:

    $> python setup.py install

[pypi]: https://pypi.python.org/pypi/scrypt/0.6.1
[pyramid]: https://pypi.python.org/pypi/pyramid

## Running

Run a simple testing server like so:

    $ python ./script_helper/run.py

Then make an http POST with a JSON body of the form:

    '{
     "input": <your password to scrypt, in hex>,
     "salt": "identity.mozilla.com/picl/v1/scrypt",
     "N": 65536,
     "r": 8,
     "p": 1,
     "buflen": 32
    }'

to:

    - http://localhost:8080

which will return:

    {"output": "return-value-from-scrypt-algorithm, also in hex"}

(Note that all of the inputs to scrypt except the password are hard-coded; you must modify validate_parameters in server.py if you wish to change any of them.)


## Dev Deployment

There is a development instance of this service running in the moz-svc-dev
AWS environment, and available for testing at:

    http://scrypt.dev.lcip.org

This deployment is managed using [awsboxen].  To push a new version of the
code, simply do:

    $> awsboxen deploy scrypt-dev-lcip-org

You can also use awsboxen to spin up a private server stack; just make sure
to set the DNSPrefix deploy parameter so that it doesn't conflict with the
default deployment.  For example:

    $> awsboxen deploy --define=DNSPrefix=loadtest,ClusterSize=5 scrypt-loadtest-lcip-org

When you're finished with it, tear down the stack like so:

    $> awsboxen teardown scrypt-loadtest-lcip-org


[awsboxen]: https://github.com/mozilla/awsboxen/

## TODO

Nothing!  Hmm, maybe not...

