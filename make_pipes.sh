#/bin/bash

# Create the input and output OS pipes to communicate with exabgp.
# These are not specific to any API implementation.

# Ensure directory path exists
mkdir -p /var/run/exabgp/

# Build input pipe for sending commands to exabgp
mkfifo /var/run/exabgp/exabgp.in
chmod 666 /var/run/exabgp/exabgp.in

# Build output pipe for reading responses from exabgp
mkfifo /var/run/exabgp/exabgp.out
chmod 666 /var/run/exabgp/exabgp.out
