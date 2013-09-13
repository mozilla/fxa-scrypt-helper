.PHONY: build test bench

# Build virtualenv, to ensure we have all the dependencies.
build:
	virtualenv --no-site-packages .
	./bin/pip install cython
	CYTHON=`pwd`/bin/cython ./bin/pip install https://github.com/surfly/gevent/archive/1.0rc2.tar.gz
	./bin/pip install https://github.com/mozilla-services/loads/archive/master.zip
	rm -rf ./local  # lol, go home ubuntu, you're drunk

# Clean all the things installed by `make build`.
clean:
	rm -rf ./include ./bin ./lib

# Run a single test from the local machine, for sanity-checking.
test:
	./bin/loads-runner stress.StressTest.test_scrypt_helper

# Run a full bench, by submitting to broker in AWS.
bench:
	./runbench.sh
