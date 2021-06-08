#/bin/bash
# Test the API after starting exabgp.

# Enable exit-on-error and command-echo
set -e
set -x

# Start exabgp on the localhost background with dummy port (doesn't need root)
env exabgp.tcp.bind=127.0.0.1 exabgp.tcp.port=5001 exabgp $1/ci.txt &

# Run the API test cases in the proper directory
pytest --verbose $1/test_api.py
