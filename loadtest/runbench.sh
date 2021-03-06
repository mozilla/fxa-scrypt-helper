#!/bin/sh
#
# Run loads bench suite, by submitting to worker machines in AWS.

BROKER=loads.loadtest.lcip.org

# We use an ssh tunnel to communicate with the loads-broker in AWS.
# Host key checking is deliberately disabled because the server regularly
# gets torn-down and replaced, and we're not sending any private info anyway.
SSH="ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

if $SSH ec2-user@$BROKER true; then
  true
else
  echo "ERROR: could not ssh into $BROKER"
  exit 1
fi

$SSH -N -L 7776:$BROKER:7776 -L 7780:$BROKER:7780 ec2-user@$BROKER &
SSH_PID=$!

./bin/loads-runner --users=10 --duration=240 --broker=tcp://localhost:7780 --zmq-publisher=tcp://localhost:7776 --agents=4 --include-file=stress.py --python-dep=scrypt stress.StressTest.test_scrypt_helper

kill $SSH_PID

