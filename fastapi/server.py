#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: Simple REST API front-end for exabgp that exposes
endpoints relevant to the BGP Traffic Server (BTS) solution
developed by the author.
"""

from hashlib import sha256
import time
from typing import Optional
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, __version__

# Create the FastAPI app along with host/port
app = FastAPI()
APP_HOST = "0.0.0.0"
APP_PORT = 8000

# Define the Route object dataclass
class Route(BaseModel):
    """
    Identify the optional and mandatory components of a route.
    """

    prefix: str
    nexthop: str
    neighbor: Optional[str] = None
    pathid: Optional[int] = None


# A better API would have a real database; use a dict for now.
# The keys are hashes and the values are Route objects
route_db = {}

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


@app.get("/version")
def version():
    """
    Returns the FastAPI and exabgp versions in a two-key dictionary.
    This is useful for ensuring the API and underlying BGP engine are working.
    """

    response = _send_command("version")
    exabgp_ver = response["response"][0].split(" ")[-1].strip()
    return {"fastapi_version": __version__, "exabgp_version": exabgp_ver}


@app.get("/routes")
def get_routes():
    """
    Returns all routes in the database by simplying returning the
    database itself. An empty dictionary indicates that no routes
    have been announced (advertised).
    """
    return route_db


@app.get("/routes/{route_hash}")
def get_specific_route(route_hash: str):
    """
    Returns an existing route from BGP without any changes. Must include
    the route hash appended to the path URL to target a specific route to
    delete. If the hash is not found, a 404 error is returned.
    """

    # If the hash is in the database, return the specified route
    if route_hash in route_db:
        specific_route = route_db[route_hash]
        return specific_route

    # Hash not present in database; return Not Found error
    raise HTTPException(status_code=404, detail=f"{route_hash} not found")


@app.post("/routes", status_code=201)
def announce_route(route: Route):
    """
    Announces (advertises) a new route into the BGP network. Must include
    "prefix" and "nexthop" fields in the JSON body. Optionally includes
    the "neighbor" field for a targeted announcement. Optionally includes
    the "pathid" field if BGP additional-paths has been negotiated.
    """

    # Collect the individual fields from the body (prefix/nexthop required)
    prefix = route.prefix
    nexthop = route.nexthop
    neighbor = route.neighbor
    pathid = route.pathid

    # Create new hash based on route values
    route_dict = route.dict()
    route_str = ",".join([str(v) for v in route_dict.values()])
    route_hash = sha256(route_str.encode()).hexdigest()

    # If hash already exists, return a Conflict error
    if route_hash in route_db:
        raise HTTPException(status_code=401, detail=f"Duplicate {route_hash}")

    # Hash is new; assemble the path ID, neighbor, and command strings
    path_str = f"path-information 0.0.0.{pathid} " if pathid else ""
    nbr_str = f"neighbor {neighbor} " if neighbor else ""
    cmd_str = f"{nbr_str}announce route {prefix} {path_str}next-hop {nexthop}"

    # Issue the command and raise Bad Request error if it fails
    response = _send_command(cmd_str)
    if response["status"].lower() != "done":
        raise HTTPException(status_code=400, detail=response)

    # Announcement succeeded; add route to database and return it
    route_entry = {route_hash: route_dict}
    route_db.update(route_entry)
    return route_entry


@app.delete("/routes/{route_hash}")
def withdraw_route(route_hash: str):
    """
    Withdraws (un-advertises) an existing route from BGP. Must include
    the route hash appended to the path URL to target a specific route to
    delete. If the hash is not found, a 404 error is returned.
    """

    # If the hash is not in the database, return Not Found error
    if not route_hash in route_db:
        raise HTTPException(status_code=404, detail=f"{route_hash} not found")

    # Hash is present in database, collect route information
    route_entry = route_db[route_hash]

    # Collect the individual fields from the body (prefix required)
    prefix = route_entry["prefix"]
    neighbor = route_entry["neighbor"]
    pathid = route_entry["pathid"]

    # Assemble the neighbor and command strings
    path_str = f"path-information 0.0.0.{pathid}" if pathid else ""
    nbr_str = f"neighbor {neighbor} " if neighbor else ""
    cmd_str = f"{nbr_str}withdraw route {prefix} {path_str}"

    # Issue the command and raise Bad Request error if it fails
    response = _send_command(cmd_str)
    if response["status"].lower() != "done":
        raise HTTPException(status_code=400, detail=response)

    # Withdrawal succeeded; remove route from database and return it
    return route_db.pop(route_hash)


if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
