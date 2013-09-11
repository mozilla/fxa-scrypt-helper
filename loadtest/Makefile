.PHONY: build test bench

# Built virtualenv, to ensure we have all the dependencies.
build:
	virtualenv --no-site-packages .
	./bin/pip install https://github.com/mozilla-services/loads/archive/master.zip

# Run a single test from the local machine, for sanity-checking.
test:
	./bin/loads-runner stress.StressTest.test_scrypt_helper

# Run a full bench, by submitting to broker in AWS.
bench:
	./runbench.sh
