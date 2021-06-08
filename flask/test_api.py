#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: Test cases for the app.py endpoints.
"""

import httpx

# Define the application HTTP port and base URL
APP_PORT = 5000
BASE_URL = f"http://localhost:{APP_PORT}"


def _change_route(body, command, resource):
    """
    Helper function to announce/withdraw routes with
    a given HTTP body (dict), expected reply command,
    and API resource string.
    """

    resp = httpx.post(f"{BASE_URL}/{resource}", json=body)
    assert resp.status_code == 200

    data = resp.json()
    assert len(data.get("response")) == 0
    assert data.get("status") == "done"

    reply_command = data.get("command")
    assert command == reply_command


def _check_routes(count):
    """
    Helper function to ensure a specified number of routes
    are seen in the outbound adj-RIB within the app.
    """

    resp = httpx.get(f"{BASE_URL}/routes")
    assert resp.status_code == 200

    data = resp.json()

    assert data.get("count") == count
    assert len(data.get("routes")) == count

    for route in data.get("routes"):
        assert len(route) == 6
        assert route.get("afi") == "ipv4"
        assert route.get("safi") == "unicast"


def test_version():
    """
    Test the "version" endpoint.
    """

    resp = httpx.get(f"{BASE_URL}/version")
    assert resp.status_code == 200

    data = resp.json()
    assert data.get("flask_version")
    assert data.get("exabgp_version")


def test_announce_pfx_nh():
    """
    Test the "announce" endpoint using a prefix and next-hop.
    """

    body = {
        "prefix": "192.0.2.0/24",
        "nexthop": "10.4.7.7",
    }
    command = "announce route 192.0.2.0/24 next-hop 10.4.7.7"
    _change_route(body, command, "announce")


def test_announce_pfx_nh_nbr():
    """
    Test the "announce" endpoint using a prefix, next-hop, and neighbor.
    """

    body = {
        "prefix": "198.51.100.0/24",
        "nexthop": "10.5.8.8",
        "neighbor": "192.168.0.1",
    }
    command = (
        "neighbor 192.168.0.1 announce route 198.51.100.0/24 "
        "next-hop 10.5.8.8"
    )
    _change_route(body, command, "announce")


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
    command = (
        "neighbor 192.168.0.2 announce route 203.0.113.0/24 "
        "path-information 0.0.0.1 next-hop 10.6.9.9"
    )
    _change_route(body, command, "announce")


def test_routes_full():
    """
    Test the "routes" endpoint and ensure the adj-RIB reveals
    the correct number of routes after the announcements.
    """
    _check_routes(8)


def test_raw():
    """
    Test the "raw" endpoint by examining the adj-RIB out and
    ensuring the correct number of routes exist after the announcements.
    """

    body = {"command": "show adj-rib out"}
    resp = httpx.post(f"{BASE_URL}/raw", json=body)
    assert resp.status_code == 200

    data = resp.json()
    assert data.get("status") == "done"
    assert data.get("command") == "show adj-rib out"
    assert len(data.get("response")) == 8


def test_withdraw_pfx():
    """
    Test the "withdraw" endpoint using a prefix.
    """
    body = {"prefix": "192.0.2.0/24"}
    command = "withdraw route 192.0.2.0/24"
    _change_route(body, command, "withdraw")


def test_withdraw_pfx_nbr():
    """
    Test the "withdraw" endpoint using a prefix and neighbor.
    """

    body = {
        "prefix": "198.51.100.0/24",
        "neighbor": "192.168.0.1",
    }
    command = "neighbor 192.168.0.1 withdraw route 198.51.100.0/24"
    _change_route(body, command, "withdraw")


def test_withdraw_pfx_nbr_path():
    """
    Test the "withdraw" endpoint using a prefix, neighbor, and add-path ID.
    """

    body = {
        "prefix": "203.0.113.0/24",
        "neighbor": "192.168.0.2",
        "pathid": 1,
    }
    command = (
        "neighbor 192.168.0.2 withdraw route 203.0.113.0/24 "
        "path-information 0.0.0.1"
    )
    _change_route(body, command, "withdraw")


def test_routes_empty():
    """
    Test the "routes" endpoint and ensure the adj-RIB reveals
    exactly 0 routes after the withdrawals.
    """

    _check_routes(0)
