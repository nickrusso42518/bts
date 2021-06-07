#/bin/bash

# Ensure directory path exists
mkdir -p /var/run/exabgp/

# Build input pipe for sending commands to exabgp
mkfifo /var/run/exabgp/exabgp.in
chmod 666 /var/run/exabgp/exabgp.in

# Build output pipe for reading responses from exabgp
mkfifo /var/run/exabgp/exabgp.out
chmod 666 /var/run/exabgp/exabgp.out
