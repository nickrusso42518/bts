#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: Test cases for the server.py endpoints.
"""

import httpx

# Define the application HTTP port and base URL
APP_PORT = 8000
BASE_URL = f"http://localhost:{APP_PORT}"


def _announce_route(body, sha256):
    """
    Helper function to announce new routes with
    a given HTTP body (dict) and expected SHA256 hash.
    """

    resp = httpx.post(f"{BASE_URL}/routes", json=body)
    assert resp.status_code == 201

    data = resp.json()
    assert len(data) == 1

    entry = data.get(sha256)
    assert entry
    for key, value in body.items():
        assert entry[key] == value


def _withdraw_route(sha256):
    """
    Helper function to withdraw existing routes with
    a specified SHA256 hash.
    """

    resp = httpx.delete(f"{BASE_URL}/routes/{sha256}")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 4


def _check_routes(sha256_list):
    """
    Helper function to ensure a specified number of routes
    are seen in the outbound adj-RIB within the app. Each
    hash in the list must be present in the response dict.
    """

    resp = httpx.get(f"{BASE_URL}/routes")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == len(sha256_list)

    for sha256 in sha256_list:
        assert data.get(sha256)


def test_version():
    """
    Test the "version" endpoint.
    """

    resp = httpx.get(f"{BASE_URL}/version")
    assert resp.status_code == 200

    data = resp.json()
    assert data.get("fastapi_version")
    assert data.get("exabgp_version")


def test_announce_pfx_nh():
    """
    Test the "announce" endpoint using a prefix and next-hop.
    """

    body = {
        "prefix": "192.0.2.0/24",
        "nexthop": "10.4.7.7",
    }
    sha256 = "939beb6bd53f0f532b202018b499731203df025d5e2e81a1fd7378367288b350"
    _announce_route(body, sha256)


def test_announce_pfx_nh_nbr():
    """
    Test the "announce" endpoint using a prefix, next-hop, and neighbor.
    """

    body = {
        "prefix": "198.51.100.0/24",
        "nexthop": "10.5.8.8",
        "neighbor": "192.168.0.1",
    }
    sha256 = "eae79139364277e7da8d1ebfd4842443fa50626ca45a8d21101f96901e02311e"
    _announce_route(body, sha256)


def test_announce_pfx_nh_nbr_path():
    """
    Test the "announce" endpoint using a prefix, next-hop, neighbor,
    and add-path ID.
    """

    body = {
        "prefix": "203.0.113.0/24",
        "nexthop": "10.6.9.9",
        "neighbor": "192.168.0.2",
        "pathid": 1,
    }
    sha256 = "ff64e67be77d23cc63d57e5cfbf0704c2d8bdcf44ef7bf404f5e83c2d02a26eb"
    _announce_route(body, sha256)


def test_routes_full():
    """
    Test the "routes" endpoint and ensure the adj-RIB reveals
    the correct number of routes after the announcements.
    """

    sha256_list = [
        "939beb6bd53f0f532b202018b499731203df025d5e2e81a1fd7378367288b350",
        "eae79139364277e7da8d1ebfd4842443fa50626ca45a8d21101f96901e02311e",
        "ff64e67be77d23cc63d57e5cfbf0704c2d8bdcf44ef7bf404f5e83c2d02a26eb",
    ]
    _check_routes(sha256_list)


def test_withdraw_pfx():
    """
    Test the "withdraw" endpoint to remove the prefix and nexthop route.
    """

    sha256 = "939beb6bd53f0f532b202018b499731203df025d5e2e81a1fd7378367288b350"
    _withdraw_route(sha256)


def test_withdraw_pfx_nbr():
    """
    Test the "withdraw" endpoint to remove the prefix, nexthop, and
    neighbor route.
    """

    sha256 = "eae79139364277e7da8d1ebfd4842443fa50626ca45a8d21101f96901e02311e"
    _withdraw_route(sha256)


def test_withdraw_pfx_nbr_path():
    """
    Test the "withdraw" endpoint to remove the prefix, nexthop, neighbor,
    and add-path ID route.
    """

    sha256 = "ff64e67be77d23cc63d57e5cfbf0704c2d8bdcf44ef7bf404f5e83c2d02a26eb"
    _withdraw_route(sha256)


def test_routes_empty():
    """
    Test the "routes" endpoint and ensure the adj-RIB reveals
    exactly 0 routes after the withdrawals.
    """

    _check_routes([])
