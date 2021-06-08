#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: Test cases for the server.py RPC methods.
"""

import pytest
import grpc
import bts_pb2
import bts_pb2_grpc


@pytest.fixture(scope="session")
def stub():
    """
    Test fixture to open the gRPC connect before all tests and to close
    it once all tests have completed. It provides the gRPC client stub
    to the individual test functions.
    """

    # Establish gRPC connection and return stub object
    conn = grpc.insecure_channel("localhost:50051")
    stub = bts_pb2_grpc.BTSStub(conn)

    # Close the connection once the tests are finished
    yield stub
    conn.close()


def _check_route_change(data, command):
    """
    Given an AnnounceReply or WithdrawReply object, this ensures
    the status and response are correct, and that the returned
    exabgp command matches the supplied (expected) command.
    """

    assert len(data.response) == 0
    assert data.status == "done"
    assert command == data.command


def _check_routes(stub, count):
    """
    Helper function to ensure a specified number of routes
    are seen in the outbound adj-RIB within the app.
    """

    data = stub.RoutesRPC(bts_pb2.RoutesArgs())

    assert data.count == count
    assert len(data.routes) == count

    for route in data.routes:
        assert route.afi == "ipv4"
        assert route.safi == "unicast"


def test_version(stub):
    """
    Test the "VersionRPC" method.
    """
    data = stub.VersionRPC(bts_pb2.VersionArgs())
    assert data.grpc_version
    assert data.exabgp_version


def test_announce_pfx_nh(stub):
    """
    Test the "AnnounceRPC" method using a prefix and next-hop.
    """

    args = {
        "prefix": "192.0.2.0/24",
        "nexthop": "10.4.7.7",
    }
    command = "announce route 192.0.2.0/24 next-hop 10.4.7.7"
    data = stub.AnnounceRPC(bts_pb2.AnnounceArgs(**args))
    _check_route_change(data, command)


def test_announce_pfx_nh_nbr(stub):
    """
    Test the "AnnounceRPC" method using a prefix, next-hop, and neighbor.
    """

    args = {
        "prefix": "198.51.100.0/24",
        "nexthop": "10.5.8.8",
        "neighbor": "192.168.0.1",
    }
    command = (
        "neighbor 192.168.0.1 announce route 198.51.100.0/24 " "next-hop 10.5.8.8"
    )
    data = stub.AnnounceRPC(bts_pb2.AnnounceArgs(**args))
    _check_route_change(data, command)


def test_announce_pfx_nh_nbr_path(stub):
    """
    Test the "AnnounceRPC" method using a prefix, next-hop, neighbor,
    and add-path ID.
    """

    args = {
        "prefix": "203.0.113.0/24",
        "nexthop": "10.6.9.9",
        "neighbor": "192.168.0.2",
        "pathid": 1,
    }
    command = (
        "neighbor 192.168.0.2 announce route 203.0.113.0/24 "
        "path-information 0.0.0.1 next-hop 10.6.9.9"
    )

    data = stub.AnnounceRPC(bts_pb2.AnnounceArgs(**args))
    _check_route_change(data, command)


def test_routes_full(stub):
    """
    Test the "RoutesRPC" method and ensure the adj-RIB reveals
    the correct number of routes after the announcements.
    """
    _check_routes(stub, 8)


def test_raw(stub):
    """
    Test the "RawRPC" method by examining the adj-RIB out and
    ensuring the correct number of routes exist after the announcements.
    """

    data = stub.RawRPC(bts_pb2.RawArgs(command="show adj-rib out"))

    assert data.status == "done"
    assert data.command == "show adj-rib out"
    assert len(data.response) == 8


def test_withdraw_pfx(stub):
    """
    Test the "WithdrawRPC" method using a prefix.
    """

    args = {"prefix": "192.0.2.0/24"}
    command = "withdraw route 192.0.2.0/24"

    data = stub.WithdrawRPC(bts_pb2.WithdrawArgs(**args))
    _check_route_change(data, command)


def test_withdraw_pfx_nbr(stub):
    """
    Test the "WithdrawRPC" method using a prefix and neighbor.
    """

    args = {
        "prefix": "198.51.100.0/24",
        "neighbor": "192.168.0.1",
    }
    command = "neighbor 192.168.0.1 withdraw route 198.51.100.0/24"

    data = stub.WithdrawRPC(bts_pb2.WithdrawArgs(**args))
    _check_route_change(data, command)


def test_withdraw_pfx_nbr_path(stub):
    """
    Test the "WithdrawRPC" method using a prefix, neighbor, and add-path ID.
    """

    args = {
        "prefix": "203.0.113.0/24",
        "neighbor": "192.168.0.2",
        "pathid": 1,
    }
    command = (
        "neighbor 192.168.0.2 withdraw route 203.0.113.0/24 "
        "path-information 0.0.0.1"
    )

    data = stub.WithdrawRPC(bts_pb2.WithdrawArgs(**args))
    _check_route_change(data, command)


def test_routes_empty(stub):
    """
    Test the "RoutesRPC" method and ensure the adj-RIB reveals
    exactly 0 routes after the withdrawals.
    """

    _check_routes(stub, 0)
