# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import bts_pb2 as bts__pb2


class BTSStub(object):
    """Define the BTS RPC requests:
    1. VersionRPC returns the exabgp and flask versions (health check).
    2. RoutesRPC returns a list of announced routes (parsed) and an count value.
    3. AnnounceRPC advertises a new route and returns the exabgp response.
    4. WithdrawRPC un-advertises an old route and returns the exabgp response.
    5. RawRPC sends an unmodified raw command and returns the exabgp response.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.VersionRPC = channel.unary_unary(
                '/BTS/VersionRPC',
                request_serializer=bts__pb2.VersionArgs.SerializeToString,
                response_deserializer=bts__pb2.VersionReply.FromString,
                )
        self.RoutesRPC = channel.unary_unary(
                '/BTS/RoutesRPC',
                request_serializer=bts__pb2.RoutesArgs.SerializeToString,
                response_deserializer=bts__pb2.RoutesReply.FromString,
                )
        self.AnnounceRPC = channel.unary_unary(
                '/BTS/AnnounceRPC',
                request_serializer=bts__pb2.AnnounceArgs.SerializeToString,
                response_deserializer=bts__pb2.AnnounceReply.FromString,
                )
        self.WithdrawRPC = channel.unary_unary(
                '/BTS/WithdrawRPC',
                request_serializer=bts__pb2.WithdrawArgs.SerializeToString,
                response_deserializer=bts__pb2.WithdrawReply.FromString,
                )
        self.RawRPC = channel.unary_unary(
                '/BTS/RawRPC',
                request_serializer=bts__pb2.RawArgs.SerializeToString,
                response_deserializer=bts__pb2.RawReply.FromString,
                )


class BTSServicer(object):
    """Define the BTS RPC requests:
    1. VersionRPC returns the exabgp and flask versions (health check).
    2. RoutesRPC returns a list of announced routes (parsed) and an count value.
    3. AnnounceRPC advertises a new route and returns the exabgp response.
    4. WithdrawRPC un-advertises an old route and returns the exabgp response.
    5. RawRPC sends an unmodified raw command and returns the exabgp response.
    """

    def VersionRPC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RoutesRPC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AnnounceRPC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WithdrawRPC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RawRPC(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BTSServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'VersionRPC': grpc.unary_unary_rpc_method_handler(
                    servicer.VersionRPC,
                    request_deserializer=bts__pb2.VersionArgs.FromString,
                    response_serializer=bts__pb2.VersionReply.SerializeToString,
            ),
            'RoutesRPC': grpc.unary_unary_rpc_method_handler(
                    servicer.RoutesRPC,
                    request_deserializer=bts__pb2.RoutesArgs.FromString,
                    response_serializer=bts__pb2.RoutesReply.SerializeToString,
            ),
            'AnnounceRPC': grpc.unary_unary_rpc_method_handler(
                    servicer.AnnounceRPC,
                    request_deserializer=bts__pb2.AnnounceArgs.FromString,
                    response_serializer=bts__pb2.AnnounceReply.SerializeToString,
            ),
            'WithdrawRPC': grpc.unary_unary_rpc_method_handler(
                    servicer.WithdrawRPC,
                    request_deserializer=bts__pb2.WithdrawArgs.FromString,
                    response_serializer=bts__pb2.WithdrawReply.SerializeToString,
            ),
            'RawRPC': grpc.unary_unary_rpc_method_handler(
                    servicer.RawRPC,
                    request_deserializer=bts__pb2.RawArgs.FromString,
                    response_serializer=bts__pb2.RawReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'BTS', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BTS(object):
    """Define the BTS RPC requests:
    1. VersionRPC returns the exabgp and flask versions (health check).
    2. RoutesRPC returns a list of announced routes (parsed) and an count value.
    3. AnnounceRPC advertises a new route and returns the exabgp response.
    4. WithdrawRPC un-advertises an old route and returns the exabgp response.
    5. RawRPC sends an unmodified raw command and returns the exabgp response.
    """

    @staticmethod
    def VersionRPC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BTS/VersionRPC',
            bts__pb2.VersionArgs.SerializeToString,
            bts__pb2.VersionReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RoutesRPC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BTS/RoutesRPC',
            bts__pb2.RoutesArgs.SerializeToString,
            bts__pb2.RoutesReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AnnounceRPC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BTS/AnnounceRPC',
            bts__pb2.AnnounceArgs.SerializeToString,
            bts__pb2.AnnounceReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def WithdrawRPC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BTS/WithdrawRPC',
            bts__pb2.WithdrawArgs.SerializeToString,
            bts__pb2.WithdrawReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RawRPC(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BTS/RawRPC',
            bts__pb2.RawArgs.SerializeToString,
            bts__pb2.RawReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
