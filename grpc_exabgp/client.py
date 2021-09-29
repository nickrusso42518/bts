#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: The gRPC client side test script for the BGP Traffic-engineering
Server (BTS) project. For more context, read the free technical whitepaper:
http://njrusmc.net/pub/bts_leaf_spine.pdf
"""

import logging

import grpc
import bts_pb2
import bts_pb2_grpc


def main():
    with grpc.insecure_channel('localhost:50051') as conn:
        stub = bts_pb2_grpc.BTSStub(conn)
        resp = stub.VersionRPC(bts_pb2.VersionArgs())
        print(f"flask: {resp.flask_version} / exabgp: {resp.exabgp_version}")

        resp = stub.RoutesRPC(bts_pb2.RoutesArgs())
        print(f"count: {resp.count} / routes: {resp.routes}")

        data = {
            "prefix": "192.0.2.0/24",
            "nexthop": "198.51.100.1",
            # "neighbor": "203.0.113.1",
            # "pathid": 1,
        }
        resp = stub.AnnounceRPC(bts_pb2.AnnounceArgs(**data))
        print(get_scr(resp))

        data = {
            "prefix": "192.0.2.0/24",
            # "neighbor": "203.0.113.1",
            # "pathid": 1,
        }
        resp = stub.WithdrawRPC(bts_pb2.WithdrawArgs(**data))
        print(get_scr(resp))

        resp = stub.RawRPC(bts_pb2.RawArgs(command="show bgp summary"))
        print(get_scr(resp))

def get_scr(resp):
    resp_str = f"status: {resp.status} / command: {resp.command}\nresponse:\n"
    for line in resp.response:
        resp_str += f"  - {line}\n"
    return resp_str.strip()


if __name__ == "__main__":
    logging.basicConfig()
    main()
