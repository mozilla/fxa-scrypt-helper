.PHONY: build test bench

# build virtualenv
build:
	virtualenv --no-site-packages .
	./bin/pip install https://github.com/mozilla-services/loads/archive/master.zip

# run a single test, for sanity-checking
test:
	./bin/loads-runner stress.StressTest.test_scrypt_helper

# run actual bench (called from dist.sh over ssh)
bench:
	./bin/loads-runner --users=10 --duration=10 stress.StressTest.test_scrypt_helper
