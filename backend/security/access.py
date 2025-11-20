import grpc

from grpc import StatusCode, unary_unary_rpc_method_handler
from grpc.aio import ServerInterceptor


class APIKeyInterceptor(ServerInterceptor):
    "Validate the x-api-key metadata in incoming gRPC requests."

    def __init__(self, api_key):
        self.api_key = api_key


    async def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)

        api_key = metadata.get('x-api-key')
        if api_key != self.api_key:
            async def abort_handler(request, context):
                await context.abort(StatusCode.UNAUTHENTICATED, "Invalid or missing API key")
            return unary_unary_rpc_method_handler(abort_handler)

        return await continuation(handler_call_details)
