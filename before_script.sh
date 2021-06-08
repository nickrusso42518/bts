#/bin/bash
# Perform pre-testing checks and processing.

# Enable exit-on-error and command-echo
set -e
set -x

# Perform linting nad formatting checks on server and test files
pylint --verbose $1/server.py $1/test_api.py
black --line-length 82 --check $1/server.py $1/test_api.py

# Replace dummy string in exabgp CI config with proper build directory
sed --in-place "s:BUILD_DIR:$TRAVIS_BUILD_DIR:" $1/ci.txt
head --lines=5 $1/ci.txt

# Validate both exabgp config files
exabgp $1/ci.txt --validate
exabgp $1/conf.txt --validate
