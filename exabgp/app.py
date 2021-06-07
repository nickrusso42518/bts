#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: Simple HTTP API front-end for exabgp that exposes
endpoints relevant to the BGP Traffic Server (BTS) solution
developed by the author.
"""

import re
import time
from flask import Flask, request, __version__

# Create the flask app along with host/port
app = Flask(__name__)
APP_HOST = "0.0.0.0"
APP_PORT = 5000

# Build these pipes before running exabgp (make_pipes.sh)
TX_PIPE = "/var/run/exabgp/exabgp.in"
RX_PIPE = "/var/run/exabgp/exabgp.out"


def _send_command(cmd_str):
    """
    Helper function to send a command to exabgp and return the response.
    The dictionary returned includes the status code, response lines,
    and the original command issued.
    """

    # Strip extra whitespace and send the command to exabgp
    cmd_str = cmd_str.strip()
    with open(TX_PIPE, "w", encoding="utf-8") as pipe:
        pipe.write(f"{cmd_str}\n")
        pipe.flush()

    # Read the response from the command
    with open(RX_PIPE, "r", encoding="utf-8") as pipe:
        response = pipe.read()

        # Some commands generate many lines of output; introduce a short wait
        # Keep looping until we see "done" or "error" in the response text
        while not ("done" in response or "error" in response):
            time.sleep(0.3)
            response += pipe.read()

    # The last line of the response has a status code; all other lines are data
    lines = response.strip().split("\n")
    return {"status": lines[-1], "command": cmd_str, "response": lines[:-1]}


@app.route("/version", methods=["GET"])
def version():
    """
    Returns the flask and exabgp versions in a two-key dictionary.
    This is useful for ensuring the API and underlying BGP engine are working.
    """

    response = _send_command("version")
    exabgp_ver = response["response"][0].split(" ")[-1].strip()
    return {"flask_version": __version__, "exabgp_version": exabgp_ver}


@app.route("/announce", methods=["POST"])
def announce():
    """
    Announces (advertises) a new route into the BGP network. Must include
    "prefix" and "nexthop" fields in the JSON body. Optionally includes
    the "neighbor" field for a targeted announcement. Optionally includes
    the "pathid" field if BGP additional-paths has been negotiated.
    """

    # Collect the individual fields from the body
    prefix = request.json.get("prefix")
    nexthop = request.json.get("nexthop")
    neighbor = request.json.get("neighbor")
    pathid = request.json.get("pathid")

    # Ensure that "prefix" and "nexthop" are specified, at a minimum
    if not prefix or not nexthop:
        return ({"reason": "body needs 'prefix' and 'nexthop' fields"}, 400)

    # Assemble the path ID, neighbor, and command strings
    path_str = f"path-information 0.0.0.{pathid} " if pathid else ""
    nbr_str = f"neighbor {neighbor} " if neighbor else ""
    cmd_str = f"{nbr_str}announce route {prefix} {path_str}next-hop {nexthop}"

    # Issue the command and return the response
    response = _send_command(cmd_str)
    return response


@app.route("/withdraw", methods=["POST"])
def withdraw():
    """
    Withdraws (un-advertises) an existing route from BGP. Must include
    the "prefix" field in the JSON body. Optionally includes
    the "neighbor" field for a targeted withdrawal. Optionally includes
    the "pathid" field if BGP additional-paths has been negotiated.
    """

    # Collect the individual fields from the body
    prefix = request.json.get("prefix")
    neighbor = request.json.get("neighbor")
    pathid = request.json.get("pathid")

    # Ensure that "prefix" is specified, at a minimum
    if not prefix:
        return ({"reason": "body needs 'prefix' field"}, 400)

    # Assemble the neighbor and command strings
    path_str = f"path-information 0.0.0.{pathid}" if pathid else ""
    nbr_str = f"neighbor {neighbor} " if neighbor else ""
    cmd_str = f"{nbr_str}withdraw route {prefix} {path_str}"

    # Issue the command and return the response
    response = _send_command(cmd_str)
    return response


@app.route("/routes", methods=["GET"])
def routes():
    """
    Collect the BGP outbound adj-rib from exabgp, which reveals
    the announced routes for each peer. The response is a dictionary
    that contains the number of routes and a list of sub-dictionaries
    containing the key attributes of a route: neighbor, afi, safi,
    prefix, pathid (optional), and nexthop.
    """

    # Define pattern to match text response from exabgp. Example:
    # neighbor 192.168.0.1 ipv4 unicast 203.0.113.0/24 next-hop 10.5.8.8
    # (add-path): 203.0.113.0/24 path-information 0.0.0.1 next-hop 10.5.8.8
    pattern = (
        r"neighbor\s+(?P<neighbor>\S+)\s+(?P<afi>\S+)\s+(?P<safi>\S+)\s+"
        r"(?P<prefix>\S+)(?:\s+path-information\s+(?P<pathid>\S+))?"
        r"\s+next-hop\s+(?P<nexthop>\S+)"
    )

    # Compile the regex, collect the outbound BGP routes, and assemble
    # the response dictionary super-structure
    route_regex = re.compile(pattern)
    raw_data = _send_command("show adj-rib out")
    response = {"count": len(raw_data["response"]), "routes": []}

    # For each route returned by exabgp, parse the fields and
    # add them to the "routes" list. If the "pathid" is absent from
    # the output, the "pathid" key is added with a value of "None".
    for route in raw_data["response"]:
        match = route_regex.search(route)
        response["routes"].append(match.groupdict())

    # Return the response dictionary
    return response


@app.route("/raw", methods=["POST"])
def raw():
    """
    Issue a plaintext command to exabgp. Requires the "command"
    field in the JSON body, which does not need to include the
    trailing "\n" character.
    """

    # Collect the individual fields from the body
    cmd_str = request.json.get("command")

    # Ensure that "cmd_str" is specified, at a minimum
    if not cmd_str:
        return ({"reason": "body needs 'command' field"}, 400)

    # Send the raw command and return the response
    response = _send_command(cmd_str)
    return response


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT)
