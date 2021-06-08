#!/bin/bash
# Compiles the protobuf definition and generates two Python files
# 1. bts_pb2.py: generated request and response classes
# 2. bts_pb2_grpc.py: generated client and server classes
#
# Usage: "./compile.sh <relative path to where proto file exists>"

python -m grpc_tools.protoc --proto_path=$1 \
  --python_out=$1 \
  --grpc_python_out=$1 \
  $1/bts.proto
