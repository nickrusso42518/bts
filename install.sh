#/bin/bash
# Create the input and output OS pipes to communicate with exabgp.
# These are not specific to any API implementation.

# Enable exit-on-error and command-echo
set -e
set -x

# Ensure directory path exists
sudo mkdir -p /var/run/exabgp/

# Build input pipe for sending commands to exabgp
sudo mkfifo /var/run/exabgp/exabgp.in
sudo chmod 666 /var/run/exabgp/exabgp.in

# Build output pipe for reading responses from exabgp
sudo mkfifo /var/run/exabgp/exabgp.out
sudo chmod 666 /var/run/exabgp/exabgp.out

# Install Python packages based on directory name
pip install -r $1/requirements.txt
