# Scrypt Helper Service

A web service that provides the [scrypt key derivation function] [scrypt] for future [Firefox Services] [services].

[scrypt]: http://en.wikipedia.org/wiki/Scrypt
[services]: https://services.mozilla.com/

## Prerequisites

* Python 2.7 or better, but not Python 3.x
* `pip`
* An OpenSSL development package (e.g., `libssl-dev` on Ubuntu/Debian, `openssl-devel` on Red Hat, `brew install openssl` on Mac OS X).

## Installation

    $ virtualenv env
    $ source env/bin/activate
    $ pip install scrypt pyramid

Clone the `scrypt-helper` repo in the `env` directory. In `scrypt-helper`:

    $ python setup.py install

You can deactivate the virtual environment with `deactivate`.

## Testing

With the virtual environment activated, run this:

    $ python setup.py test

## Running

    $ python scrypt_helper/run.py

Then make an HTTP POST with a JSON body of the form:

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

## Testing with curl 

    curl -X POST -H "Content-Type: application/json" \
        -d '{"input": "ABCDEF0123", "salt":"identity.mozilla.com/picl/v1/scrypt", "N": 65536, "r":8, "p":1, "buflen":32}' \
        http://localhost:8080; echo    

Output:

    {"output": "8158f3aae9044369c4c6ba5eda6f679cca8adc1186eb29637a75c9e4b4b940f1"}

(Note that all of the inputs to scrypt except the password are hard-coded; you must modify validate_parameters in server.py if you wish to change any of them.)


## Dev Deployment

There is a development instance of this service running in the moz-svc-dev
AWS environment, and available for testing at:

    https://scrypt-accounts.dev.lcip.org

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
