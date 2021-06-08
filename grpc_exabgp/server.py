#!/usr/bin/env python

"""
Author: Nick Russo (njrusmc@gmail.com)
Purpose: The gRPC server side implementation for the BGP Traffic-engineering
Server (BTS) project. This converts RPC requests into exabgp commands and
returns the exabgp output back to the client in various formats.
For more context, read the free technical whitepaper:
http://njrusmc.net/pub/bts_leaf_spine.pdf
"""

from concurrent import futures
import logging
import re
import time
import grpc
import bts_pb2
import bts_pb2_grpc

# Build these pipes before running exabgp (make_pipes.sh)
TX_PIPE = "/var/run/exabgp/exabgp.in"
RX_PIPE = "/var/run/exabgp/exabgp.out"


class BTS(bts_pb2_grpc.BTSServicer):
    """
    BTS class to implement individual RPCs and interact with exabgp.
    """

    def __init__(self):
        """
        Constructor used to create a simple logger for use in RPC methods.
        Example format: 2020-05-20 07:12:38 INFO Hello world!
        """

        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.INFO,
        )
        self.logger = logging.getLogger()

    @staticmethod
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

    def VersionRPC(self, request, context):
        """
        rpc VersionRPC(VersionArgs) returns(VersionReply) {};
        """

        peer = context.peer()
        self.logger.info("VersionRPC from %s", peer)

        resp = BTS._send_command("version")
        exabgp_ver = resp["response"][0].split(" ")[-1].strip()
        data = {"grpc_version": grpc.__version__, "exabgp_version": exabgp_ver}
        self.logger.info("VersionReply to %s with %s", peer, data)

        return bts_pb2.VersionReply(**data)

    def RoutesRPC(self, request, context):
        """
        rpc RoutesRPC(RoutesArgs) returns(RoutesReply) {};
        """

        peer = context.peer()
        self.logger.info("RoutesRPC from %s", peer)

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

        raw_data = BTS._send_command("show adj-rib out")
        data = bts_pb2.RoutesReply(count=len(raw_data["response"]))
        routes = []

        # For each route returned by exabgp, parse the fields and
        # add them to the "routes" list. If the "pathid" is absent from
        # the output, the "pathid" key is added with a value of "None".
        for route in raw_data["response"]:
            match = route_regex.search(route)
            route_item = bts_pb2.RouteItem(**match.groupdict())
            routes.append(route_item)

        data.routes.extend(routes)
        self.logger.info("RoutesRPC to %s with %s", peer, data)
        return data

    def AnnounceRPC(self, request, context):
        """
        rpc AnnounceRPC(AnnounceArgs) returns(AnnounceReply) {};
        """

        peer = context.peer()
        self.logger.info("AnnounceRPC from %s", peer)

        # Collect the individual fields from the body (prefix/nexthop required)
        prefix = request.prefix
        nexthop = request.nexthop
        neighbor = request.neighbor
        pathid = request.pathid

        # Assemble the path ID, neighbor, and command strings
        path_str = f"path-information 0.0.0.{pathid} " if pathid else ""
        nbr_str = f"neighbor {neighbor} " if neighbor else ""
        cmd_str = f"{nbr_str}announce route {prefix} {path_str}next-hop {nexthop}"

        # Issue the command and return the response
        data = BTS._send_command(cmd_str)
        # data = {"status": "s", "command": "c", "response": ["r"]}

        self.logger.info("AnnounceReply to %s with %s", peer, data)
        return bts_pb2.AnnounceReply(**data)

    def WithdrawRPC(self, request, context):
        """
        rpc WithdrawRPC(WithdrawArgs) returns(WithdrawReply) {};
        """

        peer = context.peer()
        self.logger.info("WithdrawRPC from %s", peer)

        # Collect the individual fields from the body (prefix required)
        prefix = request.prefix
        neighbor = request.neighbor
        pathid = request.pathid

        # Assemble the neighbor and command strings
        path_str = f"path-information 0.0.0.{pathid}" if pathid else ""
        nbr_str = f"neighbor {neighbor} " if neighbor else ""
        cmd_str = f"{nbr_str}withdraw route {prefix} {path_str}"

        # Issue the command and return the response
        data = BTS._send_command(cmd_str)
        # data = {"status": "s", "command": "c", "response": ["r"]}

        self.logger.info("WithdrawRPC to %s with %s", peer, data)
        return bts_pb2.WithdrawReply(**data)

    def RawRPC(self, request, context):
        """
        pc RawRPC(RawArgs) returns(RawReply) {};
        """

        peer = context.peer()
        self.logger.info("RawRPC from %s", peer)

        # Send the raw command and return the response
        data = BTS._send_command(request.command)
        # data = {"status": "s", "command": request.command, "response": ["r"]}

        self.logger.info("RawRPC to %s with %s", peer, data)
        return bts_pb2.RawReply(**data)


def main():
    """
    Following the grpcio example, this function starts the gRPC server and
    binds it to the recommended TCP port of 50051 for up to 10 threads.
    """

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bts_pb2_grpc.add_BTSServicer_to_server(BTS(), server)
    server.add_insecure_port("127.0.0.1:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    main()
